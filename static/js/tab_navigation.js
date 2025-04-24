// static/js/tab_navigation.js
//
// This module handles the tab-based navigation on the index page.

export function initializeTabNavigation() {
    // --- Tab Navigation ---
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and content
            navTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to the clicked tab
            tab.classList.add('active');

            // Show the corresponding tab content
            const targetId = tab.getAttribute('data-target');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });

    // Activate the default tab (e.g., 'upload') on page load
    const defaultTab = document.querySelector('.nav-tab.active');
    if (defaultTab) {
        const defaultTargetId = defaultTab.getAttribute('data-target');
        const defaultTargetContent = document.getElementById(defaultTargetId);
        if (defaultTargetContent) {
            defaultTargetContent.classList.add('active');
        }
    } else {
        // If no default active tab is set, activate the first one
        if (navTabs.length > 0) {
            navTabs[0].classList.add('active');
            const firstTargetId = navTabs[0].getAttribute('data-target');
            const firstTargetContent = document.getElementById(firstTargetId);
            if (firstTargetContent) {
                firstTargetContent.classList.add('active');
            }
        }
    }

    console.log("Tab navigation initialized.");
}

// Note: This module does not have external dependencies beyond standard browser APIs.