# app/workspace_utils.py
#
# This module contains utility functions for interacting with the WorkspaceManager.

import logging

# Import the WorkspaceManager
from .workspace import WorkspaceManager

# Configure logging (ensure this is not duplicated if already in __init__.py)
# logging.basicConfig(level=logging.INFO)

def update_workspace_video(filename: str):
    """
    Updates the WorkspaceManager with the given filename as the current video_in
    and saves the workspace state.

    Args:
        filename (str): The filename to set as the current video_in.
    """
    workspace = WorkspaceManager.get_instance()
    workspace.video_in = filename
    workspace.save()
    logging.info(f"Workspace updated with video_in: {workspace.video_in}")

# TODO: Add other workspace utility functions here as needed