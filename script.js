// script.js

// Example: initialize tooltips for all elements with title
document.addEventListener("DOMContentLoaded", function() {
    const tooltips = document.querySelectorAll('[title]');
    tooltips.forEach(el => {
        el.addEventListener("mouseenter", () => {
            // Could show custom tooltip here
        });
    });
});