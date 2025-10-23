/**
 * Equipment list admin functionality
 * Handles archived row styling and other equipment-specific features
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add archived row styling
    const rows = document.querySelectorAll('#result_list tbody tr');
    rows.forEach(function(row) {
        const archiveIcon = row.querySelector('.field-archive_icon');
        if (archiveIcon && archiveIcon.textContent.includes('🗃️')) {
            row.classList.add('archived-row');
        }
    });
});
