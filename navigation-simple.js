/**
 * Simple Navigation Enhancement for mdBook
 * Adds view controls without breaking mdBook's navigation
 */

class SimpleNavController {
    constructor() {
        this.currentView = 'default';
        this.init();
    }
    
    init() {
        console.log('SimpleNav: Initializing...');
        this.addControls();
        this.hideNonOrdinances();
    }
    
    addControls() {
        const sidebar = document.querySelector('.sidebar');
        const scrollbox = document.querySelector('mdbook-sidebar-scrollbox');
        
        if (!sidebar || !scrollbox) {
            console.log('SimpleNav: Waiting for sidebar...');
            setTimeout(() => this.addControls(), 500);
            return;
        }
        
        // Create simple view toggle
        const controls = document.createElement('div');
        controls.className = 'simple-nav-controls';
        controls.innerHTML = `
            <style>
                .simple-nav-controls {
                    padding: 10px;
                    background: #f8f9fa;
                    border-bottom: 1px solid #dee2e6;
                    margin-bottom: 10px;
                }
                
                .nav-message {
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                    padding: 5px;
                }
                
                .nav-info {
                    font-size: 11px;
                    color: #999;
                    text-align: center;
                    margin-top: 5px;
                }
                
                /* Hide non-ordinance sections */
                .hide-non-ordinances .part-title:not(:first-of-type),
                .hide-non-ordinances .chapter-item:has(a[href*="resolutions/"]),
                .hide-non-ordinances .chapter-item:has(a[href*="interpretations/"]),
                .hide-non-ordinances .chapter-item:has(a[href*="transcripts/"]) {
                    display: none !important;
                }
            </style>
            <div class="nav-message">Navigation View Controls</div>
            <div class="nav-info">Enhanced views coming soon!</div>
        `;
        
        scrollbox.parentNode.insertBefore(controls, scrollbox);
        console.log('SimpleNav: Controls added');
    }
    
    hideNonOrdinances() {
        // Add class to hide non-ordinance items
        const scrollbox = document.querySelector('mdbook-sidebar-scrollbox');
        if (scrollbox) {
            scrollbox.classList.add('hide-non-ordinances');
        }
    }
}

// Initialize when ready
function initSimpleNav() {
    const checkReady = setInterval(() => {
        if (document.querySelector('mdbook-sidebar-scrollbox')) {
            clearInterval(checkReady);
            new SimpleNavController();
        }
    }, 100);
    
    setTimeout(() => clearInterval(checkReady), 10000);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSimpleNav);
} else {
    initSimpleNav();
}