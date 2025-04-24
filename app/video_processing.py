# app/video_processing.py
#
# This module contains functions for video processing tasks
# using libraries like MoviePy within the Clipia Flask application.

import os
import logging
from flask import current_app # Import current_app to access app config
# from moviepy.editor import VideoFileClip # Import VideoFileClip for video processing
from moviepy import VideoFileClip # Attempting alternative import based on documentation examples

# Import necessary functions from file_utils
from .file_utils import get_video_file

# Import the WorkspaceManager (needed for split_video_into_clips)
from .workspace import WorkspaceManager



def get_video_duration(video_path: str) -> float | None:
    """
    Gets the duration of a video file in seconds.

    Args:
        video_path (str): The full path to the video file.

    Returns:
        float | None: The duration of the video in seconds, or None if an error occurs.
    """
    logging.info(f"Attempting to get duration for video: {video_path}")
    try:
        with VideoFileClip(video_path) as video:
            duration = video.duration
            logging.info(f"Successfully retrieved duration: {duration} seconds.")
            return duration
    except Exception as e:
        logging.error(f"Error getting duration for video {video_path}: {e}")
        return None

# Configure logging (ensure this is not duplicated if already in __init__.py)
# logging.basicConfig(level=logging.INFO)

def trim_video(input_filename, start_time, end_time):
    """
    Trims a video file using MoviePy based on start and end times.

    Args:
        input_filename (str): The name of the input video file in the upload folder.
        start_time (float): The start time for trimming in seconds.
        end_time (float): The end time for trimming in seconds.

    Returns:
        tuple: A tuple containing a dictionary result and an HTTP status code.
               Result dictionary includes 'success' (bool), 'message' (str),
               and optionally 'trimmed_filename' (str) on success.
    """
    # Get the full path of the input video file using file_utils
    input_filepath_result, status_code = get_video_file(input_filename)

    # Check if the input file was found
    if not input_filepath_result.get("success"):
        # If not found, return the error from get_video_file
        return input_filepath_result, status_code

    input_filepath = input_filepath_result.get("filepath")

    # Define the output filename for the trimmed video
    # Appends '_trimmed' and keeps the original extension
    name, ext = os.path.splitext(input_filename)
    trimmed_filename = f"{name}_trimmed{ext}"
    trimmed_filepath = os.path.join(current_app.config['VIDEO_UPLOAD_FOLDER'], trimmed_filename)

    try:
        # Load the video clip using MoviePy
        with VideoFileClip(input_filepath) as clip:
            # Validate trimming times against video duration
            if start_time is None or end_time is None:
                 logging.error("Start or end time not provided for trimming.")
                 return {"success": False, "message": "Start and end times must be provided."}, 400

            if start_time < 0 or end_time < 0:
                 logging.error(f"Invalid negative time provided: start={start_time}, end={end_time}")
                 return {"success": False, "message": "Start and end times cannot be negative."}, 400

            if start_time >= clip.duration or end_time > clip.duration:
                 logging.error(f"Trimming times out of bounds: start={start_time}, end={end_time}, duration={clip.duration}")
                 return {"success": False, "message": "Trimming times are out of the video's duration."}, 400

            if start_time >= end_time:
                 logging.error(f"Invalid time range: start={start_time}, end={end_time}")
                 return {"success": False, "message": "Start time must be before end time."}, 400

            # Perform the trimming using the correct method
            trimmed_clip = clip.subclipped(start_time, end_time)

            # Write the trimmed video to a new file
            # Use a common codec like 'libx264' for MP4
            trimmed_clip.write_videofile(trimmed_filepath, codec='libx264', audio_codec='aac')

        logging.info(f"Successfully trimmed video and saved to: {trimmed_filepath}")
        # Return success message and the filename of the trimmed video
        return {"success": True, "message": "Video trimmed successfully.", "trimmed_filename": trimmed_filename}, 200

    except Exception as e:
        # Handle potential errors during video processing (e.g., unsupported format, MoviePy errors)
        logging.error(f"Error trimming video {input_filename}: {e}")
        # Return an error message with the exception details
        return {"success": False, "message": f"Error trimming video: {e}"}, 500

def split_video_into_clips(video_identifier: str, output_directory: str):
    """
    Splits a video into 25-minute clips with a 3-minute overlap using MoviePy.

    Args:
        video_identifier (str): The identifier or path of the video in the upload folder.
                                This is assumed to be the filename for now, retrieved
                                from the WorkspaceManager.
        output_directory (str): The directory where the trimmed clips will be saved.

    Returns:
        dict: A dictionary where keys are the paths of the saved clips and values
              are dictionaries with 'start_time' and 'end_time' in the original video.
              Returns an empty dictionary and logs errors if the process fails.
    """
    logging.info(f"Attempting to split video: {video_identifier} into clips.")

    # Assume video_identifier is the filename stored in the workspace
    workspace = WorkspaceManager.get_instance()
    current_video_filename = workspace.video_in

    if not current_video_filename:
        logging.error("No current video found in workspace to split.")
        return {}

    # Get the full path of the input video file using file_utils
    input_filepath_result, status_code = get_video_file(current_video_filename)

    if not input_filepath_result.get("success"):
        logging.error(f"Input video file not found for splitting: {current_video_filename}")
        return {}

    input_filepath = input_filepath_result.get("filepath")

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
    logging.info(f"Ensured output directory exists: {output_directory}")

    clip_duration = 1500  # 25 minutes in seconds
    overlap = 180         # 3 minutes in seconds
    step = clip_duration - overlap # 22 minutes step

    clips_info = {}
    clip_index = 1

    try:
        # Load the video clip
        with VideoFileClip(input_filepath) as video:
            video_duration = video.duration
            logging.info(f"Video duration: {video_duration} seconds.")

            # Handle case where video is shorter than the clip duration
            if video_duration < clip_duration:
                logging.warning(f"Video duration ({video_duration}s) is less than clip duration ({clip_duration}s). Saving as a single clip.")
                start_time = 0
                end_time = video_duration
                output_filename = f"clip_{clip_index}.mp4"
                output_filepath = os.path.join(output_directory, output_filename)

                try:
                    single_clip = video.subclipped(start_time, end_time)
                    single_clip.write_videofile(output_filepath, codec='libx264', audio_codec='aac')
                    logging.info(f"Saved single clip: {output_filepath}")
                    clips_info[output_filepath] = {"start_time": start_time, "end_time": end_time}
                except Exception as e:
                    logging.error(f"Error saving single clip {output_filepath}: {e}")
                return clips_info # Return after saving the single clip

            # Split the video into clips
            start_time = 0
            while start_time < video_duration:
                end_time = min(start_time + clip_duration, video_duration)
                output_filename = f"clip_{clip_index}.mp4"
                output_filepath = os.path.join(output_directory, output_filename)

                try:
                    # Create the subclip
                    subclip = video.subclipped(start_time, end_time)
                    # Write the subclip to a file
                    subclip.write_videofile(output_filepath, codec='libx264', audio_codec='aac')
                    logging.info(f"Saved clip {clip_index}: {output_filepath} (Original time: {start_time}-{end_time}s)")
                    # Store clip info
                    clips_info[output_filepath] = {"start_time": start_time, "end_time": end_time}
                except Exception as e:
                    logging.error(f"Error saving clip {clip_index} ({output_filepath}): {e}")
                    # Continue to the next clip even if one fails to save

                # Move to the next start time
                start_time += step
                clip_index += 1

        logging.info("Video splitting complete.")
        return clips_info

    except Exception as e:
        # Handle errors during video loading or processing
        logging.error(f"Error splitting video {input_filepath}: {e}")
        return {} # Return empty dictionary on failure

# TODO: Add other video processing functions here as needed (e.g., for effects)