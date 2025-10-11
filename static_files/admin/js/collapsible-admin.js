/**
 * Collapsible Admin Interface JavaScript
 * Provides functionality for collapsible apps and navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeCollapsibleAdmin();
});

function initializeCollapsibleAdmin() {
    // Initialize app states from localStorage
    initializeAppStates();
    
    // Set up event listeners
    setupEventListeners();
    
    // Highlight current page
    highlightCurrentPage();
    
    // Restore collapsed states
    restoreCollapsedStates();
}

function setupEventListeners() {
    // Handle model link clicks
    document.querySelectorAll('.model-link, .nav-model-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const modelName = this.dataset.model;
            const appLabel = this.closest('[data-app-label]').dataset.appLabel;
            
            // Store current model for highlighting
            localStorage.setItem('currentModel', modelName);
            localStorage.setItem('currentApp', appLabel);
            
            // Expand the app if collapsed
            expandApp(appLabel);
        });
    });
    
    // Handle window resize for mobile
    window.addEventListener('resize', handleResize);
}

function toggleApp(appLabel) {
    const content = document.getElementById('content-' + appLabel);
    const icon = document.getElementById('icon-' + appLabel);
    const appModule = document.querySelector(`[data-app-label="${appLabel}"]`);
    
    if (!content || !icon) return;
    
    const isCollapsed = content.style.display === 'none';
    
    if (isCollapsed) {
        expandApp(appLabel);
    } else {
        collapseApp(appLabel);
    }
    
    // Save state to localStorage
    saveAppState(appLabel, !isCollapsed);
}

function toggleNavApp(appLabel) {
    const content = document.getElementById('nav-content-' + appLabel);
    const icon = document.getElementById('nav-icon-' + appLabel);
    
    if (!content || !icon) return;
    
    const isCollapsed = content.style.display === 'none';
    
    if (isCollapsed) {
        expandNavApp(appLabel);
    } else {
        collapseNavApp(appLabel);
    }
    
    // Save state to localStorage
    saveNavAppState(appLabel, !isCollapsed);
}

function expandApp(appLabel) {
    const content = document.getElementById('content-' + appLabel);
    const icon = document.getElementById('icon-' + appLabel);
    const appModule = document.querySelector(`[data-app-label="${appLabel}"]`);
    
    if (content) {
        content.style.display = 'block';
        content.classList.remove('collapsed');
    }
    
    if (icon) {
        icon.classList.remove('collapsed');
    }
    
    if (appModule) {
        appModule.classList.add('active');
    }
    
    // Also expand in navigation
    expandNavApp(appLabel);
}

function collapseApp(appLabel) {
    const content = document.getElementById('content-' + appLabel);
    const icon = document.getElementById('icon-' + appLabel);
    const appModule = document.querySelector(`[data-app-label="${appLabel}"]`);
    
    if (content) {
        content.style.display = 'none';
        content.classList.add('collapsed');
    }
    
    if (icon) {
        icon.classList.add('collapsed');
    }
    
    if (appModule) {
        appModule.classList.remove('active');
    }
}

function expandNavApp(appLabel) {
    const content = document.getElementById('nav-content-' + appLabel);
    const icon = document.getElementById('nav-icon-' + appLabel);
    const navApp = document.querySelector(`.nav-app[data-app-label="${appLabel}"]`);
    
    if (content) {
        content.style.display = 'block';
        content.classList.remove('collapsed');
    }
    
    if (icon) {
        icon.classList.remove('collapsed');
    }
    
    if (navApp) {
        navApp.classList.add('active');
    }
}

function collapseNavApp(appLabel) {
    const content = document.getElementById('nav-content-' + appLabel);
    const icon = document.getElementById('nav-icon-' + appLabel);
    const navApp = document.querySelector(`.nav-app[data-app-label="${appLabel}"]`);
    
    if (content) {
        content.style.display = 'none';
        content.classList.add('collapsed');
    }
    
    if (icon) {
        icon.classList.add('collapsed');
    }
    
    if (navApp) {
        navApp.classList.remove('active');
    }
}

function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const currentModel = localStorage.getItem('currentModel');
    const currentApp = localStorage.getItem('currentApp');
    
    // Remove existing active classes
    document.querySelectorAll('.model-link.active, .nav-model-link.active').forEach(link => {
        link.classList.remove('active');
    });
    
    // Highlight current model
    if (currentModel) {
        const modelLinks = document.querySelectorAll(`[data-model="${currentModel}"]`);
        modelLinks.forEach(link => {
            link.classList.add('active');
        });
    }
    
    // Expand current app
    if (currentApp) {
        expandApp(currentApp);
    }
    
    // Auto-detect current model from URL
    autoDetectCurrentModel(currentPath);
}

function autoDetectCurrentModel(path) {
    // Extract model name from URL patterns like /admin/app/model/
    const pathParts = path.split('/').filter(part => part);
    
    if (pathParts.length >= 3 && pathParts[0] === 'admin') {
        const appLabel = pathParts[1];
        const modelName = pathParts[2];
        
        // Find and highlight the model
        const modelLinks = document.querySelectorAll(`[data-model="${modelName}"]`);
        modelLinks.forEach(link => {
            link.classList.add('active');
        });
        
        // Expand the app
        expandApp(appLabel);
        
        // Save to localStorage
        localStorage.setItem('currentModel', modelName);
        localStorage.setItem('currentApp', appLabel);
    }
}

function saveAppState(appLabel, isExpanded) {
    const states = JSON.parse(localStorage.getItem('appStates') || '{}');
    states[appLabel] = isExpanded;
    localStorage.setItem('appStates', JSON.stringify(states));
}

function saveNavAppState(appLabel, isExpanded) {
    const states = JSON.parse(localStorage.getItem('navAppStates') || '{}');
    states[appLabel] = isExpanded;
    localStorage.setItem('navAppStates', JSON.stringify(states));
}

function restoreCollapsedStates() {
    const appStates = JSON.parse(localStorage.getItem('appStates') || '{}');
    const navAppStates = JSON.parse(localStorage.getItem('navAppStates') || '{}');
    
    // Restore main app states
    Object.keys(appStates).forEach(appLabel => {
        if (!appStates[appLabel]) {
            collapseApp(appLabel);
        }
    });
    
    // Restore navigation app states
    Object.keys(navAppStates).forEach(appLabel => {
        if (!navAppStates[appLabel]) {
            collapseNavApp(appLabel);
        }
    });
}

function initializeAppStates() {
    // Initialize all apps as collapsed by default (except current app)
    const currentApp = localStorage.getItem('currentApp');
    const allApps = document.querySelectorAll('[data-app-label]');
    
    allApps.forEach(app => {
        const appLabel = app.dataset.appLabel;
        if (appLabel !== currentApp) {
            const states = JSON.parse(localStorage.getItem('appStates') || '{}');
            if (!(appLabel in states)) {
                collapseApp(appLabel);
            }
        }
    });
}

function handleResize() {
    const sidebar = document.getElementById('nav-sidebar');
    if (window.innerWidth <= 480) {
        // Mobile view - hide sidebar by default
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    } else {
        // Desktop view - show sidebar
        if (sidebar) {
            sidebar.classList.add('open');
        }
    }
}

// Global functions for template use
window.toggleApp = toggleApp;
window.toggleNavApp = toggleNavApp;
window.expandApp = expandApp;
window.collapseApp = collapseApp;

// Utility function to clear all states (for debugging)
window.clearAdminStates = function() {
    localStorage.removeItem('appStates');
    localStorage.removeItem('navAppStates');
    localStorage.removeItem('currentModel');
    localStorage.removeItem('currentApp');
    location.reload();
};
