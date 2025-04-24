# app/video_analysis.py
#
# This module contains the main function for video analysis using the Gemini API.

import os
import logging
import json
import datetime
import base64
import hashlib
from flask import current_app
from google import genai
from google.genai import types
from moviepy.editor import VideoFileClip # Import VideoFileClip for duration check

# Import necessary functions and classes from other modules
from .workspace import WorkspaceManager
from .file_utils import get_video_file
from .video_processing import split_video_into_clips, get_video_duration # Import the new duration function

# Configure logging (ensure this is not duplicated if already in __init__.py)
# logging.basicConfig(level=logging.INFO)

# Define the minimum duration for splitting in seconds (25 minutes)
MIN_DURATION_FOR_SPLIT = 1500

# Define the output directory for temporary clips
TEMP_CLIPS_DIR = "workspace/temp_clips"

# Define the output directory for analysis results
ANALYSIS_OUTPUT_DIR = "workspace"

# Gemini API configuration
GEMINI_MODEL = "gemini-2.5-flash-preview-04-17"
GEMINI_FLASH_MODEL = "gemini-2.0-flash" # Model for video upload

# Gemini API prompt
GEMINI_PROMPT = """Analyze this video segment and identify the most noteworthy moments. For each moment provide:
  - The reason why it's significant
  - Start time (in seconds)
  - End time (in seconds)"""

# Gemini API response schema
GEMINI_RESPONSE_SCHEMA = genai.types.Schema(
    type=genai.types.Type.OBJECT,
    properties={
        "Momentos": genai.types.Schema(
            type=genai.types.Type.ARRAY,
            items=genai.types.Schema(
                type=genai.types.Type.OBJECT,
                properties={
                    "Razon": genai.types.Schema(
                        type=genai.types.Type.STRING,
                    ),
                    "Segundo_inicio": genai.types.Schema(
                        type=genai.types.Type.STRING,
                    ),
                    "Segundo_termina": genai.types.Schema(
                        type=genai.types.Type.STRING,
                    ),
                },
            ),
        ),
    },
)

# Helper function for calculating file hash for caching
def calculate_file_hash(filepath: str) -> str | None:
    """
    Calculates the SHA256 hash of a file.

    Args:
        filepath (str): The path to the file.

    Returns:
        str | None: The SHA256 hash of the file, or None if an error occurs.
    """
    logging.info(f"Calculating hash for file: {filepath}")
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            # Read and update hash string value in chunks
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        logging.info(f"Calculated hash: {file_hash}")
        return file_hash
    except Exception as e:
        logging.error(f"Error calculating hash for {filepath}: {e}")
        return None

# Main video analysis function
def analyze_video(video_identifier: str):
    """
    Analyzes a video using the Gemini API to identify noteworthy moments.

    Args:
        video_identifier (str): The identifier or filename of the video
                                in the upload folder.

    Returns:
        dict: A dictionary containing the analysis results and metadata,
              or an error message.
    """
    logging.info(f"Starting video analysis for: {video_identifier}")

    # Get the full path of the input video file
    input_filepath_result, status_code = get_video_file(video_identifier)

    if not input_filepath_result.get("success"):
        logging.error(f"Input video file not found: {video_identifier}")
        return {"success": False, "message": "Input video file not found."}, status_code

    input_filepath = input_filepath_result.get("filepath")

    # --- Implement Requirement 6 (Caching) ---
    video_hash = calculate_file_hash(input_filepath)
    if video_hash:
        cache_file_path = os.path.join(ANALYSIS_OUTPUT_DIR, f"{video_hash}.json")
        if os.path.exists(cache_file_path):
            logging.info(f"Cache hit for video {video_identifier}. Loading analysis from {cache_file_path}")
            try:
                with open(cache_file_path, 'r') as f:
                    cached_analysis = json.load(f)
                # Add a note that this was loaded from cache
                cached_analysis['metadata']['cached'] = True
                return cached_analysis, 200
            except Exception as e:
                logging.error(f"Error loading cached analysis from {cache_file_path}: {e}")
                # If loading from cache fails, proceed with analysis

    # --- Implement Requirement 0 (Duration Check) ---
    video_duration = get_video_duration(input_filepath)

    if video_duration is None:
        logging.error(f"Could not get duration for video: {video_identifier}")
        return {"success": False, "message": "Could not get video duration."}, 500

    logging.info(f"Video duration: {video_duration} seconds.")

    clips_info = {}
    if video_duration < MIN_DURATION_FOR_SPLIT:
        logging.warning(f"Video duration ({video_duration}s) is less than {MIN_DURATION_FOR_SPLIT}s. Skipping splitting.")
        # Treat the entire video as a single clip
        clips_info[input_filepath] = {"start_time": 0, "end_time": video_duration}
        # Ensure the temp clips directory exists even if not splitting, as the API might save temp files
        os.makedirs(TEMP_CLIPS_DIR, exist_ok=True)
    else:
        logging.info(f"Video duration ({video_duration}s) is {MIN_DURATION_FOR_SPLIT}s or more. Splitting video.")
        # --- Implement Requirement 1 (Video Splitting) ---
        clips_info = split_video_into_clips(video_identifier, TEMP_CLIPS_DIR)

        if not clips_info:
            logging.error(f"Failed to split video: {video_identifier}")
            return {"success": False, "message": "Failed to split video."}, 500

    all_moments = []
    total_clips = len(clips_info)
    processed_clips = 0

    # --- Implement Requirement 2 & 3 (API Calls) ---
    # Process clips sequentially to avoid rate limiting (Requirement 4)
    for clip_path, time_info in clips_info.items():
        processed_clips += 1
        logging.info(f"Processing clip {processed_clips}/{total_clips}: {clip_path}")

        try:
            # Initialize Gemini client
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

            # Upload video clip to Gemini API
            logging.info(f"Uploading clip to Gemini API: {clip_path}")
            # Use the flash model for file upload as per documentation
            myfile = client.files.upload(file=clip_path)
            logging.info(f"Clip uploaded. File URI: {myfile.uri}")

            # Prepare content for the API call
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=GEMINI_PROMPT),
                    ],
                ),
                types.Content(
                    role="user",
                    parts=[
                         types.Part.from_uri(uri=myfile.uri, mime_type=myfile.mime_type)
                    ]
                )
            ]

            # Make the API call
            logging.info(f"Calling Gemini API for analysis...")
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                response_mime_type="application/json",
                response_schema=GEMINI_RESPONSE_SCHEMA,
            )

            # Use generate_content instead of stream for simplicity in collecting full JSON
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=generate_content_config,
            )
            logging.info("Received response from Gemini API.")

            # Parse the JSON response
            try:
                analysis_result = json.loads(response.text)
                if "Momentos" in analysis_result:
                    # Adjust timestamps based on the clip's start time in the original video
                    clip_start_time = time_info["start_time"]
                    for moment in analysis_result["Momentos"]:
                        try:
                            # Convert string times to float, add clip start time, and convert back to string
                            moment_start = float(moment.get("Segundo_inicio", 0)) + clip_start_time
                            moment_end = float(moment.get("Segundo_termina", 0)) + clip_start_time
                            moment["Segundo_inicio"] = str(moment_start)
                            moment["Segundo_termina"] = str(moment_end)
                            all_moments.append(moment)
                        except ValueError as ve:
                            logging.error(f"Error converting moment timestamps to float for clip {clip_path}: {ve}")
                            # Append moment with original timestamps if conversion fails
                            all_moments.append(moment)

            except json.JSONDecodeError as jde:
                logging.error(f"Error decoding JSON response for clip {clip_path}: {jde}")
                # Continue to the next clip if JSON decoding fails

            # Delete the uploaded file from Gemini Files API to free up space
            try:
                client.files.delete(name=myfile.name)
                logging.info(f"Deleted uploaded file from Gemini Files API: {myfile.name}")
            except Exception as delete_error:
                logging.warning(f"Could not delete uploaded file {myfile.name} from Gemini Files API: {delete_error}")


        except Exception as e:
            # Handle API errors gracefully (Requirement 4)
            logging.error(f"Error processing clip {clip_path} with Gemini API: {e}")
            # Continue to the next clip even if one fails

    # --- Implement Requirement 6 (Timestamp Validation) ---
    valid_moments = []
    for moment in all_moments:
        try:
            start_time = float(moment.get("Segundo_inicio", 0))
            end_time = float(moment.get("Segundo_termina", 0))
            if 0 <= start_time <= video_duration and 0 <= end_time <= video_duration and start_time <= end_time:
                valid_moments.append(moment)
            else:
                logging.warning(f"Invalid timestamp found in analysis: {moment}. Start: {start_time}, End: {end_time}, Video Duration: {video_duration}")
        except ValueError as ve:
             logging.error(f"Error validating moment timestamps (could not convert to float): {moment}. Error: {ve}")
             # If conversion fails during validation, skip this moment

    # --- Implement Requirement 5 (Final Output) ---
    final_analysis = {
        "Momentos": valid_moments,
        "metadata": {
            "total_moments_identified": len(valid_moments),
            "processing_timestamp": datetime.datetime.now().isoformat(),
            "clip_segmentation_info": clips_info,
            "original_video_duration": video_duration,
            "video_identifier": video_identifier,
        }
    }

    # Ensure the analysis output directory exists
    os.makedirs(ANALYSIS_OUTPUT_DIR, exist_ok=True)

    # Determine the output filename (using video hash for caching)
    output_filename = f"analizys-{video_hash if video_hash else 'no-hash'}.json"
    output_filepath = os.path.join(ANALYSIS_OUTPUT_DIR, output_filename)

    # Save the final analysis to a JSON file
    try:
        with open(output_filepath, 'w') as f:
            json.dump(final_analysis, f, indent=4)
        logging.info(f"Final analysis saved to: {output_filepath}")

        # --- Implement Requirement 6 (Caching) - Save to cache if hash was calculated ---
        if video_hash:
             logging.info(f"Saving analysis to cache: {cache_file_path}")
             try:
                 with open(cache_file_path, 'w') as f:
                     json.dump(final_analysis, f, indent=4)
             except Exception as e:
                 logging.error(f"Error saving analysis to cache {cache_file_path}: {e}")


        return {"success": True, "message": "Video analysis complete.", "output_filepath": output_filepath}, 200

    except Exception as e:
        logging.error(f"Error saving final analysis to {output_filepath}: {e}")
        return {"success": False, "message": f"Error saving final analysis: {e}"}, 500

# Helper function to clean up temporary clip files
def cleanup_temp_clips():
    """
    Removes all files from the temporary clips directory.
    """
    logging.info(f"Cleaning up temporary clips directory: {TEMP_CLIPS_DIR}")
    try:
        if os.path.exists(TEMP_CLIPS_DIR):
            for filename in os.listdir(TEMP_CLIPS_DIR):
                file_path = os.path.join(TEMP_CLIPS_DIR, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logging.error(f"Error deleting temporary file {file_path}: {e}")
        logging.info("Temporary clip cleanup complete.")
    except Exception as e:
        logging.error(f"Error during temporary clip cleanup: {e}")

# TODO: Consider adding a mechanism to trigger cleanup_temp_clips after analysis is complete.
# This could be done in the route handler that calls analyze_video.