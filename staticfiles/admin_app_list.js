/**
 * Admin app list functionality
 * Enhances collapsible application groups in admin sidebar
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers to app group summaries
    const appGroups = document.querySelectorAll('.app-group > summary');
    
    appGroups.forEach(function(summary) {
        // Add visual feedback on click
        summary.addEventListener('click', function(e) {
            // Add a small delay to show the click effect
            this.style.opacity = '0.7';
            setTimeout(() => {
                this.style.opacity = '1';
            }, 150);
        });
        
        // Add keyboard support (Enter and Space)
        summary.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
        
        // Ensure summary is focusable for keyboard navigation
        summary.setAttribute('tabindex', '0');
        summary.setAttribute('role', 'button');
        summary.setAttribute('aria-expanded', summary.parentElement.hasAttribute('open'));
    });
    
    // Update aria-expanded when details open/close
    const detailsElements = document.querySelectorAll('.app-group');
    detailsElements.forEach(function(details) {
        details.addEventListener('toggle', function() {
            const summary = this.querySelector('summary');
            summary.setAttribute('aria-expanded', this.hasAttribute('open'));
        });
    });
});
