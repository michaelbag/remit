/**
 * Simple Collapsible Admin JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all apps as collapsed by default
    initializeCollapsedApps();
});

function initializeCollapsedApps() {
    // Get all app modules in main content and sidebar
    const appModules = document.querySelectorAll('.module');
    
    appModules.forEach(app => {
        const caption = app.querySelector('caption');
        if (caption) {
            const icon = caption.querySelector('.collapse-icon');
            const tbody = app.querySelector('tbody');
            
            if (icon && tbody) {
                // Collapse by default
                tbody.style.display = 'none';
                icon.textContent = '▶';
            }
        }
    });
}

function toggleApp(appLabel) {
    // Handle both main content and sidebar
    const tbody = document.getElementById('content-' + appLabel) || document.getElementById('sidebar-content-' + appLabel);
    const icon = document.getElementById('icon-' + appLabel) || document.getElementById('sidebar-icon-' + appLabel);
    
    if (!tbody || !icon) return;
    
    const isCollapsed = tbody.style.display === 'none';
    
    if (isCollapsed) {
        // Expand
        tbody.style.display = '';
        icon.textContent = '▼';
    } else {
        // Collapse
        tbody.style.display = 'none';
        icon.textContent = '▶';
    }
}

// Make function globally available
window.toggleApp = toggleApp;