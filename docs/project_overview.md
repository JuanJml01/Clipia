# Clipia Project Overview

This document provides an overview of the Clipia project structure and components, intended as context for AI models.

## Project Structure

The project follows a standard Flask application structure:

```
Clipia/
├── app/
│   └── app.py          # Main Flask application file
├── docs/
│   └── project_overview.md # This documentation file
├── images/
│   └── memes/          # Directory for uploaded image memes
├── videos/
│   └── samples/        # Directory for uploaded video samples
├── static/             # Directory for static files (CSS, JS, images)
├── templates/          # Directory for HTML templates
│   └── index.html      # Main page template
└── requirements.txt    # Project dependencies
```

## Key Components

*   **`app/app.py`**:
    *   Initializes the Flask application.
    *   Configures upload folders (`videos/samples`, `images/memes`).
    *   Includes a root route (`/`) that renders `index.html`.
    *   Contains stub routes (`/upload_video`, `/upload_image`) for handling file uploads. These stubs currently do not save files but demonstrate the route structure.
    *   Placeholder comments (`TODO`) indicate where future logic for video processing, Gemini AI integration, and download functionality will be added.
*   **`templates/index.html`**:
    *   A basic HTML template serving as the project's landing page.
    *   Includes "Hello World" text.
    *   Contains simple forms for uploading videos and images, pointing to the respective stub routes.
    *   Placeholder comments (`TODO`) indicate where future UI elements will be added.
*   **`requirements.txt`**:
    *   Lists the Python dependencies required for the project: `Flask==2.3.3` and `MoviePy==2.1.2`.
*   **`videos/samples/`**:
    *   Designated directory for saving uploaded video files.
*   **`images/memes/`**:
    *   Designated directory for saving uploaded image files (intended for memes).
*   **`static/`**:
    *   Intended for serving static assets like CSS, JavaScript, and images used by the web interface. Currently empty.
*   **`docs/`**:
    *   Intended for project documentation.

## Python Virtual Environment Setup

It is highly recommended to use a Python virtual environment to manage project dependencies.

1.  **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    ```
    (Replace `python3` with your Python executable if necessary)
2.  **Activate the virtual environment**:
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    3.  **Install dependencies**:
        ```bash
        pip install -r requirements.txt
        ```
    4.  **Run the Flask application**:
        ```bash
        export FLASK_APP=app/app.py
        flask run
        ```
        The application should be accessible at `http://127.0.0.1:5000/`.

## Future Development

The current structure provides a foundation. Future development will involve:

*   Implementing secure file saving in upload routes.
*   Integrating the MoviePy library for video processing tasks (trimming, effects).
*   Integrating with the Gemini AI API to receive processing instructions.
*   Developing logic to dynamically apply edits based on AI instructions.
*   Creating a download endpoint for processed videos.
*   Adding proper error handling and user feedback.
*   Developing the frontend (`index.html` and static files) further.