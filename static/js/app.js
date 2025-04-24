// static/js/app.js
//
// This is the main entry point for the frontend JavaScript application.
// It initializes the different modules and sets up the overall behavior.

// Import initialization functions from other modules
import { initializeTabNavigation } from './tab_navigation.js';
import { initializeFileUpload } from './file_upload.js';
import { initializeVideoTrimming } from './video_trimming.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize tab navigation
    initializeTabNavigation();

    // Initialize file upload functionality
    initializeFileUpload();

    // Initialize video trimming functionality
    // The file upload module will call initializeVideoTrimming with the filename after upload
    // We can potentially load the last used filename from the backend on page load here if needed
    initializeVideoTrimming();


    console.log("Frontend application initialized.");
});

// Note: This module orchestrates the initialization of other frontend modules.