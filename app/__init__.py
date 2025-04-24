# app/__init__.py
#
# This file initializes the Flask application and registers blueprints.
# It sets up the application factory pattern for better organization.

from flask import Flask
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import the WorkspaceManager
from .workspace import WorkspaceManager

def create_app():
    """
    Factory function to create the Flask application instance.
    Configures the application and registers blueprints.
    Initializes the WorkspaceManager.

    Returns:
        Flask: The configured Flask application instance.
    """
    # Create the Flask application instance
    # Specify template and static folders relative to the instance
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Define base directories for uploads using app.instance_path or a relative path from the project root
    # Using a path relative to the project root as defined in the original app.py
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app.config['VIDEO_UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'videos', 'samples')
    app.config['IMAGE_UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'images', 'memes')

    # Configure a secret key for security (e.g., for sessions)
    # In a real application, this should be loaded from environment variables or a config file
    app.config['SECRET_KEY'] = 'a_very_secret_key_replace_me' # TODO: Replace with a real secret key

    # Configure max content length for uploads (example limit)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Ensure upload folders exist
    os.makedirs(app.config['VIDEO_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['IMAGE_UPLOAD_FOLDER'], exist_ok=True)

    # Initialize the WorkspaceManager
    # Attempt to load existing state, otherwise initialize with defaults
    workspace_manager = WorkspaceManager.load()
    if workspace_manager is None:
        workspace_manager = WorkspaceManager() # Initialize with defaults if load fails

    # Make the workspace_manager available to the application context
    # This can be done by adding it to the app config or using Flask's AppContext
    # For simplicity here, we'll just ensure the singleton instance is created/loaded
    # and can be accessed via WorkspaceManager.get_instance() in routes/utils.
    # A more advanced approach might use Flask extensions or context processors.
    logging.info("WorkspaceManager initialized.")


    # Import and register blueprints
    # Blueprints help modularize the application
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # TODO: Register other blueprints (e.g., for processing, results)

    return app

# Note: The 'if __name__ == '__main__': app.run()' block is removed
# when using the application factory pattern. The application is typically
# run using a command like 'flask run' which automatically discovers the app
# via the FLASK_APP environment variable (e.g., export FLASK_APP=app).