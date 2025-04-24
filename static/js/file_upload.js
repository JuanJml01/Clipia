// static/js/file_upload.js
//
// This module handles the file upload functionality on the Upload tab.

// Import necessary functions from other modules
// import { updateVideoPreview } from './video_preview.js'; // Assuming a video_preview module for updating the preview
import { initializeVideoTrimming } from './video_trimming.js'; // Import trimming initialization

export function initializeFileUpload() {
    // --- File Input and Upload Button ---
    const videoFileInput = document.getElementById('video-file-input');
    const uploadButton = document.getElementById('upload-video-button');
    const videoPreviewArea = document.getElementById('video-preview-area'); // Needed to show/hide preview area
    const videoElement = document.getElementById('video-preview'); // Needed to set video src
    const videoMetadata = document.getElementById('video-metadata'); // Needed to display metadata

    // Keep track of the currently uploaded video filename
    let currentVideoFilename = null;

    if (videoFileInput && uploadButton && videoPreviewArea && videoElement && videoMetadata) {
        // --- File Input Change Handler ---
        // Handles file selection and displays basic info, but not video preview
        videoFileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];

            if (file) {
                // TODO: Add file type validation (check if it's a video)
                // You can check file.type or file.name extension

                // Display basic metadata (more can be added)
                videoMetadata.innerHTML = `
                    <p><strong>Filename:</strong> ${file.name}</p>
                    <p><strong>Type:</strong> ${file.type}</p>
                    <p><strong>Size:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <!-- TODO: Add video dimensions/duration after loading -->
                `;

                // Show the preview area structure, but video src is set after upload
                videoPreviewArea.classList.add('active');
                videoElement.src = ''; // Clear previous preview

                // Enable the upload button
                uploadButton.disabled = false;

            } else {
                // Hide preview and disable upload if no file is selected
                videoPreviewArea.classList.remove('active');
                videoElement.src = '';
                videoMetadata.innerHTML = '';
                uploadButton.disabled = true;
            }
        });

        // --- Upload Button Click Handler ---
        // Handles sending the file to the backend and setting preview from server
        uploadButton.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent default form submission

            const file = videoFileInput.files[0];
            if (!file) {
                alert("Please select a video file to upload.");
                return;
            }

            // Implement actual file upload using Fetch API
            const formData = new FormData();
            formData.append('video', file); // 'video' must match the key expected by Flask (request.files['video'])

            // Set loading state and disable button
            uploadButton.classList.add('loading');
            uploadButton.disabled = true;
            uploadButton.textContent = 'Uploading...'; // Update button text

            fetch('/upload_video', {
                method: 'POST',
                body: formData // Send the FormData object
            })
            .then(response => {
                // Check if the response is OK (status in the range 200-299)
                if (!response.ok) {
                    // If not OK, parse the JSON error response and throw an error
                    return response.json().then(err => { throw new Error(err.message || 'Upload failed'); });
                }
                // If OK, parse the JSON success response
                return response.json();
            })
            .then(data => {
                // Handle successful upload response
                console.log('Upload successful:', data);
                alert(data.message || 'File uploaded successfully!'); // Show success message

                // If upload was successful and filename is returned, set video preview src from server
                if (data.success && data.filename) {
                    currentVideoFilename = data.filename; // Store the filename
                    // updateVideoPreview(currentVideoFilename); // Use a dedicated function to update the preview
                     videoElement.src = `/get_video/${currentVideoFilename}`; // Set preview from server
                     videoPreviewArea.classList.add('active'); // Ensure preview area is visible
                     console.log(`Setting video preview source to: /get_video/${currentVideoFilename}`);

                    // Initialize trimming functionality with the uploaded filename
                    initializeVideoTrimming(currentVideoFilename);

                } else {
                    console.warn("Upload successful, but no filename returned for preview.");
                    // TODO: Handle cases where filename is not returned
                }
            })
            .catch(error => {
                // Handle upload errors (network issues, server errors, invalid file type, etc.)
                console.error('Upload error:', error);
                alert(`Upload failed: ${error.message || 'An unknown error occurred.'}`); // Show error message
                // TODO: Display error message on the UI
            })
            .finally(() => {
                // Remove loading state and re-enable button
                uploadButton.classList.remove('loading');
                uploadButton.disabled = false;
                uploadButton.textContent = 'Upload Video'; // Reset button text
                // Optional: Clear the file input or reset the preview
                // videoFileInput.value = '';
                // videoPreviewArea.classList.remove('active'); // Decide if you want to clear preview on error/completion
            });
        });

        // Initially disable the upload button
        uploadButton.disabled = true;

    } else {
        console.error("One or more required elements for file input/upload not found.");
    }

    console.log("File upload functionality initialized.");
}

// Dependencies:
// - Requires elements with IDs: 'video-file-input', 'upload-video-button', 'video-preview-area', 'video-preview', 'video-metadata' in the HTML.
// - Depends on the backend '/upload_video' endpoint (POST).
// - Depends on the backend '/get_video/<name>' endpoint (GET) for preview after upload.
// - Calls initializeVideoTrimming from video_trimming.js after successful upload.
// - Assumes a video_preview.js module with updateVideoPreview function (commented out for now).