/**
 * Minimal Navigation Enhancement for mdBook
 * Only adds a search box and stats, doesn't modify the existing navigation
 */

console.log('Navigation enhancement script loaded');

// Wait for mdBook to finish loading
window.addEventListener('load', () => {
    console.log('Window loaded, attempting to enhance navigation...');
    
    setTimeout(() => {
        const sidebar = document.querySelector('#sidebar');
        const scrollbox = document.querySelector('mdbook-sidebar-scrollbox');
        
        if (!sidebar || !scrollbox) {
            console.error('Could not find sidebar elements');
            return;
        }
        
        console.log('Found sidebar, adding minimal enhancements...');
        
        // Count ordinances
        const ordinanceLinks = document.querySelectorAll('a[href*="ordinances/"]');
        const count = ordinanceLinks.length;
        
        // Add a simple info box
        const info = document.createElement('div');
        info.style.cssText = `
            padding: 10px;
            background: #f0f0f0;
            font-size: 12px;
            color: #666;
            text-align: center;
            border-bottom: 1px solid #ddd;
        `;
        info.textContent = `${count} Ordinances`;
        
        // Insert at the top of the scrollbox
        if (scrollbox.firstChild) {
            scrollbox.insertBefore(info, scrollbox.firstChild);
            console.log('Added info box');
        } else {
            console.error('Could not insert info box');
        }
        
    }, 1000); // Give mdBook time to populate
});