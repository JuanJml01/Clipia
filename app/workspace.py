# app/workspace.py
#
# This module defines the WorkspaceManager class for managing the application's state.
# It handles saving and loading the workspace state to/from a JSON file.

import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class WorkspaceManager:
    """
    Manages the state of the Clipia application workspace.

    Properties:
        video_in (str): The name/path of the current input video file.
        context (str): A description of the video content or project context.

    Methods:
        get_instance(): Class method to get the singleton instance.
        save(): Saves the current workspace state to a JSON file.
        load(): Loads the workspace state from a JSON file.
    """

    _instance = None # Class variable to hold the singleton instance
    _save_file_path = 'workspace/save/save.json' # Path to the save file

    def __init__(self, video_in: str = None, context: str = "Live gameplay stream footage"):
        """
        Initializes the WorkspaceManager instance.

        Args:
            video_in (str, optional): Initial input video filename. Defaults to None.
            context (str, optional): Initial video context description. Defaults to "Live gameplay stream footage".
        """
        if WorkspaceManager._instance is not None:
            # Prevent direct instantiation if an instance already exists
            raise Exception("Singleton instance already exists. Use get_instance() instead.")
        else:
            self.video_in = video_in
            self.context = context
            WorkspaceManager._instance = self # Set the instance

    @classmethod
    def get_instance(cls):
        """
        Gets the singleton instance of WorkspaceManager.
        Creates a new instance with default values if one does not exist.

        Returns:
            WorkspaceManager: The singleton instance.
        """
        if cls._instance is None:
            # Create the instance if it doesn't exist
            cls._instance = cls()
            logging.info("WorkspaceManager instance created with default values.")
        return cls._instance

    def save(self):
        """
        Saves the current object state (video_in, context) to a JSON file.
        Overwrites the file if it exists, creates it otherwise.
        """
        # Ensure the save directory exists
        save_dir = os.path.dirname(self._save_file_path)
        os.makedirs(save_dir, exist_ok=True)
        logging.info(f"Ensured save directory exists: {save_dir}")

        # Prepare data to be saved
        data_to_save = {
            "video_in": self.video_in,
            "context": self.context
        }
        logging.info(f"Saving workspace state to {self._save_file_path}: {data_to_save}")

        try:
            # Write the data to the JSON file
            with open(self._save_file_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            logging.info("Workspace state saved successfully.")
        except IOError as e:
            # Handle file writing errors
            logging.error(f"Error saving workspace state to {self._save_file_path}: {e}")
            # In a real application, you might want to return an error status or raise the exception

    @classmethod
    def load(cls):
        """
        Loads object state from the JSON save file.
        If the file exists, reads its content and returns a new instance
        populated with the loaded data. If the file does not exist or
        loading fails, returns None.

        Returns:
            WorkspaceManager or None: A new WorkspaceManager instance with loaded data,
                                      or None if loading failed.
        """
        if not os.path.exists(cls._save_file_path):
            logging.warning(f"Workspace save file not found at {cls._save_file_path}.")
            return None # File does not exist

        logging.info(f"Attempting to load workspace state from {cls._save_file_path}.")
        try:
            # Read data from the JSON file
            with open(cls._save_file_path, 'r') as f:
                loaded_data = json.load(f)

            # Create a new instance with loaded data
            # Note: This bypasses the singleton check in __init__ for loading purposes
            # A more robust singleton might handle loading within get_instance
            instance = cls(video_in=loaded_data.get("video_in"), context=loaded_data.get("context"))
            logging.info("Workspace state loaded successfully.")
            return instance

        except (IOError, json.JSONDecodeError) as e:
            # Handle file reading or JSON parsing errors
            logging.error(f"Error loading workspace state from {cls._save_file_path}: {e}")
            return None # Loading failed

# Example usage (for testing the class in isolation if needed)
# if __name__ == '__main__':
#     # Test saving
#     manager = WorkspaceManager.get_instance()
#     manager.video_in = "my_video.mp4"
#     manager.context = "Testing save functionality"
#     manager.save()

#     # Test loading (simulate a new application run)
#     WorkspaceManager._instance = None # Reset the instance for testing load
#     loaded_manager = WorkspaceManager.load()
#     if loaded_manager:
#         print(f"Loaded video_in: {loaded_manager.video_in}")
#         print(f"Loaded context: {loaded_manager.context}")
#     else:
#         print("Failed to load workspace state, initializing with defaults.")
#         default_manager = WorkspaceManager.get_instance()
#         print(f"Default video_in: {default_manager.video_in}")
#         print(f"Default context: {default_manager.context}")