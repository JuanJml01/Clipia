# app/file_utils.py
#
# This module contains utility functions for file handling and validation
# within the Clipia Flask application.

import os
import logging
from werkzeug.utils import secure_filename
from flask import current_app # Import current_app to access app config

# Configure logging (ensure this is not duplicated if already in __init__.py)
# logging.basicConfig(level=logging.INFO)

# Allowed video extensions for validation
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename, allowed_extensions):
    """
    Checks if a file's extension is in the allowed set.

    Args:
        filename (str): The name of the file.
        allowed_extensions (set): A set of allowed file extensions (e.g., {'txt', 'pdf'}).

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_video_file(file):
    """
    Helper function to save an uploaded video file to the configured upload folder.

    Args:
        file (FileStorage): The uploaded file object from Flask's request.files.

    Returns:
        tuple: A tuple containing a dictionary result and an HTTP status code.
               Result dictionary includes 'success' (bool), 'message' (str),
               and optionally 'filename' (str) on success.
    """
    # Check if the file is provided
    if not file:
        logging.error("No file provided for upload.")
        return {"success": False, "message": "No file part in the request."}, 400

    # Check if the filename is empty
    if file.filename == '':
        logging.error("No selected file for upload.")
        return {"success": False, "message": "No selected file."}, 400

    # Validate file extension using the helper function
    if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        logging.error(f"Invalid file type uploaded: {file.filename}")
        return {"success": False, "message": f"Invalid file type. Allowed types are: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"}, 400

    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(file.filename)
    # Construct the full file path using the configured upload folder
    filepath = os.path.join(current_app.config['VIDEO_UPLOAD_FOLDER'], filename)

    try:
        # Save the file to the specified upload folder
        file.save(filepath)
        logging.info(f"Successfully saved file: {filepath}")
        # Return success message and the saved filename
        return {"success": True, "message": "File uploaded successfully.", "filename": filename}, 201
    except Exception as e:
        # Handle potential errors during file saving (e.g., permissions, disk space)
        logging.error(f"Error saving file {filename}: {e}")
        # Return an error message with the exception details
        return {"success": False, "message": f"Error saving file: {e}"}, 500

def get_video_file(filename):
    """
    Helper function to retrieve the full path of a video file from the configured upload folder.

    Args:
        filename (str): The name of the video file to retrieve.

    Returns:
        tuple: A tuple containing a dictionary result and an HTTP status code.
               Result dictionary includes 'success' (bool), 'message' (str) on error,
               and 'filepath' (str) on success.
    """
    # Construct the full file path using the configured upload folder
    filepath = os.path.join(current_app.config['VIDEO_UPLOAD_FOLDER'], filename)

    # Check if the file exists at the constructed path
    if not os.path.exists(filepath):
        logging.warning(f"Video file not found: {filepath}")
        # Return a 404 Not Found error if the file does not exist
        return {"success": False, "message": "Video not found."}, 404

    # Return success and the full file path if the file exists
    logging.info(f"Found video file: {filepath}")
    return {"success": True, "filepath": filepath}, 200

# TODO: Add other file utility functions here as needed (e.g., for image handling)