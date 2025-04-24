# app/routes.py
#
# This module defines the Flask routes (endpoints) for the Clipia application.
# It handles incoming HTTP requests and calls appropriate functions or utilities.

from flask import render_template, request, jsonify, send_from_directory, Blueprint
import logging
import os # Import os for path manipulation if needed in routes, though utilities handle most

# Import utility functions from the new modules
from .file_utils import save_video_file, get_video_file # Import file handling utilities
from .video_processing import trim_video, split_video_into_clips # Import video processing utilities
from .workspace_utils import update_workspace_video # Import workspace utility

# Create a Blueprint for the application routes
# Blueprints help organize routes and other app components into reusable parts
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Root route: Renders the main index page of the application.
    This serves as the single page application entry point.
    """
    logging.info("Rendering index page.")
    return render_template('index.html')

@main.route('/upload_video', methods=['POST'])
def upload_video():
    """
    API endpoint to handle video uploads.
    Expects a video file in the 'video' part of a multipart/form-data request.
    Uses the save_video_file utility function to process and save the file.
    Updates the WorkspaceManager with the uploaded video filename on success.
    Returns a JSON response indicating success or failure.
    """
    logging.info("Received request to /upload_video.")
    # Check if the 'video' file is in the request
    if 'video' not in request.files:
        logging.error("No 'video' file part in upload request.")
        # Return a JSON error response with a 400 status code
        return jsonify({"success": False, "message": "No 'video' file part in the request."}), 400

    file = request.files['video']

    # Use the helper function from file_utils.py to save the file
    result, status_code = save_video_file(file)

    # If the file was saved successfully, update the WorkspaceManager using the utility function
    if result.get("success") and result.get("filename"):
        update_workspace_video(result.get("filename"))

    # Return the result (success/error message and filename if successful)
    # as a JSON response with the appropriate status code returned by the utility
    return jsonify(result), status_code

@main.route('/upload_image', methods=['POST'])
def upload_image():
    """
    Stub API endpoint for image uploads.
    Currently not implemented, returns a 501 Not Implemented status.
    """
    logging.info("Image upload endpoint called (stub).")
    # Return a JSON response indicating that the feature is not implemented
    return jsonify({"success": False, "message": "Image upload not yet implemented."}), 501 # Not Implemented

@main.route('/get_video/<name>', methods=['GET'])
def get_video(name):
    """
    API endpoint to retrieve a video file by name.
    Looks for the video file in the configured upload directory.
    Uses the get_video_file utility function to locate the file.
    Returns the video file if found, or a JSON error response if not found.
    """
    logging.info(f"Received request to /get_video/{name}.")
    # Use the helper function from file_utils.py to get the video file path
    result, status_code = get_video_file(name)

    # If the utility function successfully found the file
    if result.get("success"):
        # Extract the directory and filename from the result
        directory = os.path.dirname(result.get("filepath"))
        filename = os.path.basename(result.get("filepath"))
        logging.info(f"Serving video file: {filename} from {directory}")
        # Use Flask's send_from_directory to securely serve the file
        return send_from_directory(directory, filename)
    else:
        # If the utility function returned an error (e.g., file not found),
        # return the JSON error response with the appropriate status code
        return jsonify(result), status_code

@main.route('/trim_video', methods=['POST'])
def trim_video_route():
    """
    API endpoint to trim a video.
    Expects 'filename', 'start_time', and 'end_time' in the JSON request body.
    Uses the trim_video utility function to perform the trimming.
    Updates the WorkspaceManager with the trimmed video filename on success.
    Returns a JSON response indicating success or failure, with the trimmed filename on success.
    """
    logging.info("Received request to /trim_video.")
    # Get data from the JSON request body
    data = request.get_json()

    # Extract parameters, providing default values or handling missing ones
    filename = data.get('filename')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    # Validate required parameters
    if not filename or start_time is None or end_time is None:
        logging.error("Missing required parameters for trimming.")
        return jsonify({"success": False, "message": "Missing filename, start_time, or end_time."}), 400

    # Attempt to convert start and end times to float, handle potential errors
    try:
        start_time = float(start_time)
        end_time = float(end_time)
    except (ValueError, TypeError):
        logging.error("Invalid start_time or end_time format.")
        return jsonify({"success": False, "message": "Invalid format for start_time or end_time. Must be numbers."}), 400

    # Use the utility function from video_processing.py to trim the video
    result, status_code = trim_video(filename, start_time, end_time)

    # If trimming was successful and a trimmed filename is returned, update the WorkspaceManager using the utility function
    if result.get("success") and result.get("trimmed_filename"):
        update_workspace_video(result.get("trimmed_filename"))

    # Return the result (success/error message and trimmed filename if successful)
    # as a JSON response with the appropriate status code returned by the utility
    return jsonify(result), status_code

# TODO: Add other routes here as needed (e.g., for other video processing effects, results)