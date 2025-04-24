# app/app.py
#
# This is the main entry point for the Clipia Flask application.
# It imports the application factory function and runs the app.

from . import create_app

# Create the Flask application instance using the factory function
app = create_app()

# Note: The application is typically run using a command like 'flask run'
# with the FLASK_APP environment variable set to 'app'.
# The debug mode and other configurations are handled within the create_app() function.