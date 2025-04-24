// static/js/video_trimming.js
//
// This module handles the video trimming functionality on the Upload tab.

// Import necessary functions from other modules
// import { updateVideoPreview } from './video_preview.js'; // Assuming a video_preview module for updating the preview

export function initializeVideoTrimming(uploadedFilename = null) {
    // --- Video Trimming Functionality ---
    const startSecondInput = document.getElementById('start-second');
    const endSecondInput = document.getElementById('end-second');
    const trimVideoButton = document.getElementById('trim-video-button');
    const videoPreviewArea = document.getElementById('video-preview-area'); // Needed to show/hide preview area
    const videoElement = document.getElementById('video-preview'); // Needed to set video src


    // Keep track of the currently uploaded video filename
    // Initialize with uploadedFilename if provided (e.g., on page load if workspace state is loaded)
    let currentVideoFilename = uploadedFilename;

    if (startSecondInput && endSecondInput && trimVideoButton && videoPreviewArea && videoElement) {

        // Enable trim inputs/button if a filename is already available (e.g., from loaded workspace)
        if (currentVideoFilename) {
             startSecondInput.disabled = false;
             endSecondInput.disabled = false;
             trimVideoButton.disabled = false;
             console.log(`Trimming functionality enabled for video: ${currentVideoFilename}`);
        } else {
             // Initially disable trim inputs/button if no video is uploaded yet
             startSecondInput.disabled = true;
             endSecondInput.disabled = true;
             trimVideoButton.disabled = true;
             console.log("Trimming functionality initialized, waiting for video upload.");
        }


        trimVideoButton.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent default form submission

            // Ensure a video has been uploaded
            if (!currentVideoFilename) {
                alert("Please upload a video first.");
                return;
            }

            // Get start and end times from input fields
            const startTime = parseFloat(startSecondInput.value);
            const endTime = parseFloat(endSecondInput.value);

            // Basic validation for numeric values and range
            if (isNaN(startTime) || isNaN(endTime) || startTime < 0 || endTime < 0) {
                alert("Please enter valid positive numbers for start and end times.");
                return;
            }

            if (startTime >= endTime) {
                 alert("Start time must be less than end time.");
                 return;
            }

            // Prepare data for the trim endpoint
            const trimData = {
                filename: currentVideoFilename,
                start_time: startTime,
                end_time: endTime
            };

            // Set loading state and disable button
            trimVideoButton.classList.add('loading');
            trimVideoButton.disabled = true;
            trimVideoButton.textContent = 'Trimming...'; // Update button text
            // TODO: Add visual feedback for trimming process

            // Call the trim video endpoint
            fetch('/trim_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json' // Specify JSON content type
                },
                body: JSON.stringify(trimData) // Send data as JSON string
            })
            .then(response => {
                // Check if the response is OK
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.message || 'Trimming failed'); });
                }
                return response.json();
            })
            .then(data => {
                // Handle successful trimming response
                console.log('Trimming successful:', data);
                alert(data.message || 'Video trimmed successfully!'); // Show success message

                // If trimming was successful and trimmed filename is returned, update preview
                if (data.success && data.trimmed_filename) {
                    currentVideoFilename = data.trimmed_filename; // Update current filename to the trimmed one
                    // updateVideoPreview(currentVideoFilename); // Use a dedicated function to update the preview
                    videoElement.src = `/get_video/${currentVideoFilename}`; // Set preview to the trimmed video
                    videoPreviewArea.classList.add('active'); // Ensure preview area is visible
                    console.log(`Setting video preview source to trimmed video: /get_video/${currentVideoFilename}`);
                    // TODO: Update UI to indicate trimmed video is now previewed
                } else {
                    console.warn("Trimming successful, but no trimmed_filename returned for preview update.");
                    // TODO: Handle cases where trimmed filename is not returned
                }
            })
            .catch(error => {
                // Handle trimming errors
                console.error('Trimming error:', error);
                alert(`Trimming failed: ${error.message || 'An unknown error occurred.'}`); // Show error message
                // TODO: Display error message on the UI
            })
            .finally(() => {
                // Remove loading state and re-enable button
                trimVideoButton.classList.remove('loading');
                trimVideoButton.disabled = false;
                trimVideoButton.textContent = 'Trim Video'; // Reset button text
            });
        });
    } else {
        console.error("One or more required elements for trimming functionality not found.");
    }

    console.log("Video trimming functionality initialized.");
}

// Dependencies:
// - Requires elements with IDs: 'start-second', 'end-second', 'trim-video-button', 'video-preview-area', 'video-preview' in the HTML.
// - Depends on the backend '/trim_video' endpoint (POST).
// - Depends on the backend '/get_video/<name>' endpoint (GET) for preview after trimming.
// - Can optionally receive the uploaded filename to enable trimming immediately if a video is already in the workspace.
// - Assumes a video_preview.js module with updateVideoPreview function (commented out for now).