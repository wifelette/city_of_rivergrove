/**
 * Working Navigation Enhancement for mdBook
 * Reorganizes existing elements without breaking mdBook
 */

class NavigationEnhancer {
    constructor() {
        this.currentView = 'chronological';
        this.currentOrder = 'asc';
        this.allOrdinanceItems = [];
        this.originalOrder = [];
        this.init();
    }
    
    init() {
        console.log('NavigationEnhancer: Initializing...');
        
        // Store all ordinance items
        this.collectOrdinanceItems();
        
        // Add controls
        this.addControls();
        
        // Hide other sections initially
        this.hideOtherSections();
    }
    
    createCleanTitle(id, title, year) {
        // Truncate long titles while preserving key information
        let cleanTitle = title;
        
        // Common abbreviations for space saving
        cleanTitle = cleanTitle.replace(/Amendment/g, 'Amend')
                              .replace(/Development/g, 'Dev')
                              .replace(/Management/g, 'Mgmt')
                              .replace(/Standards?/g, 'Std')
                              .replace(/Requirements?/g, 'Req')
                              .replace(/Provisions?/g, 'Prov')
                              .replace(/Ordinance/g, 'Ord')
                              .replace(/Water Quality Resource Area/g, 'WQRA')
                              .replace(/Municipal/g, 'Muni')
                              .replace(/Services?/g, 'Svc');
        
        // If still too long, truncate intelligently
        if (cleanTitle.length > 35) {
            // Try to cut at word boundaries
            if (cleanTitle.length > 45) {
                cleanTitle = cleanTitle.substring(0, 32) + '...';
            } else {
                // Find last space before 35 chars and cut there
                const cutPoint = cleanTitle.substring(0, 35).lastIndexOf(' ');
                if (cutPoint > 20) {
                    cleanTitle = cleanTitle.substring(0, cutPoint) + '...';
                }
            }
        }
        
        return `#${id} - ${cleanTitle} (${year})`;
    }
    
    collectOrdinanceItems() {
        // Find all ordinance list items
        const items = document.querySelectorAll('ol.chapter > li.chapter-item');
        
        items.forEach(item => {
            const link = item.querySelector('a');
            if (link && link.href.includes('ordinances/')) {
                // Parse the ordinance info from the link text
                const text = link.textContent.trim();
                console.log('Processing:', text); // Debug log
                
                // Try different patterns - the text might not have # prefix
                let match = text.match(/#(\d+[\w-]*)\s*-\s*(.+?)\s*\((\d{4})\)/);
                if (!match) {
                    // Try without # prefix
                    match = text.match(/(\d+[\w-]*)\s*-\s*(.+?)\s*\((\d{4})\)/);
                }
                if (!match) {
                    // Try to extract from href if text doesn't match
                    const hrefMatch = link.href.match(/(\d{4})-Ord-(\d+[\w-]*)-(.+)\.html/);
                    if (hrefMatch) {
                        const [, year, id, titleSlug] = hrefMatch;
                        const title = titleSlug.replace(/-/g, ' ');
                        match = ['', id, title, year];
                    }
                }
                
                if (match) {
                    const [, id, title, year] = match;
                    const cleanTitle = this.createCleanTitle(id, title, year);
                    
                    this.allOrdinanceItems.push({
                        element: item,
                        id: id,
                        title: title,
                        year: year,
                        number: parseInt(id) || 0,
                        link: link,
                        cleanTitle: cleanTitle
                    });
                    
                    // Update the display immediately
                    link.textContent = cleanTitle;
                    console.log('Updated to:', cleanTitle); // Debug log
                }
            }
        });
        
        // Store original order
        this.originalOrder = [...this.allOrdinanceItems];
        
        console.log(`NavigationEnhancer: Found ${this.allOrdinanceItems.length} ordinances`);
    }
    
    addControls() {
        const scrollbox = document.querySelector('mdbook-sidebar-scrollbox');
        if (!scrollbox) {
            console.error('NavigationEnhancer: Could not find scrollbox');
            return;
        }
        
        // Create control panel
        const controls = document.createElement('div');
        controls.className = 'nav-controls-panel';
        controls.innerHTML = `
            <div class="nav-header">
                <div class="header-row">
                    <div class="nav-title">Ordinances</div>
                    <div class="order-icons">
                        <button class="order-icon active" data-order="asc" title="Oldest First">▲</button>
                        <button class="order-icon" data-order="desc" title="Newest First">▼</button>
                    </div>
                </div>
            </div>
            <div class="nav-search-box">
                <input type="text" id="ordSearch" placeholder="Search ordinances..." />
            </div>
            <div class="nav-controls-section">
                <div class="control-label">View</div>
                <div class="nav-view-buttons">
                    <button class="view-btn" data-view="numerical" title="Organized by ordinance number ranges">Numerical</button>
                    <button class="view-btn active" data-view="chronological" title="Grouped by decade with historical ordering">Chronological</button>
                    <button class="view-btn" data-view="topical" title="Grouped by subject matter">Topical</button>
                </div>
            </div>
            <div class="nav-stats">
                Showing <span id="visibleCount">${this.allOrdinanceItems.length}</span> of <span id="totalCount">${this.allOrdinanceItems.length}</span> ordinances
            </div>
        `;
        
        // Insert before scrollbox content
        const firstChild = scrollbox.querySelector('ol.chapter');
        if (firstChild) {
            scrollbox.insertBefore(controls, firstChild);
        } else {
            scrollbox.appendChild(controls);
        }
        
        // Add event listeners
        this.bindEvents();
        
        // Add styles
        this.addStyles();
    }
    
    bindEvents() {
        // View buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.switchView(e.target.dataset.view);
            });
        });
        
        // Order buttons
        document.querySelectorAll('.order-icon').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.order-icon').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentOrder = e.target.dataset.order;
                this.switchView(this.currentView); // Re-render with new order
            });
        });
        
        // Search
        const searchInput = document.getElementById('ordSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterOrdinances(e.target.value);
            });
        }
    }
    
    switchView(view) {
        console.log(`NavigationEnhancer: Switching to ${view} view`);
        this.currentView = view;
        
        const chapterList = document.querySelector('ol.chapter');
        if (!chapterList) return;
        
        // Remove any existing groups
        document.querySelectorAll('.view-group').forEach(g => g.remove());
        
        switch (view) {
            case 'numerical':
                this.showNumberView();
                break;
            case 'chronological':
                this.showChronologicalView();
                break;
            case 'topical':
                this.showTopicalView();
                break;
            default:
                this.showChronologicalView();
                break;
        }
    }
    
    showChronologicalView() {
        // Group by decade
        const decades = {};
        
        this.allOrdinanceItems.forEach(item => {
            const decade = Math.floor(parseInt(item.year) / 10) * 10;
            const key = decade + 's';
            
            if (!decades[key]) {
                decades[key] = [];
            }
            decades[key].push(item);
            
            // Hide original item
            item.element.style.display = 'none';
        });
        
        // Create decade groups
        const chapterList = document.querySelector('ol.chapter');
        
        // Sort decades based on current order
        const sortedKeys = Object.keys(decades).sort((a, b) => {
            return this.currentOrder === 'asc' ? a.localeCompare(b) : b.localeCompare(a);
        });
        
        sortedKeys.forEach(decade => {
            const group = document.createElement('li');
            group.className = 'chapter-item expanded view-group';
            group.classList.add('no-list-style');
            group.style.cssText = '';
            
            const header = document.createElement('div');
            header.className = 'group-header';
            header.innerHTML = `
                <span class="group-arrow">▼</span>
                <span class="group-name">${decade}</span>
                <span class="group-count">${decades[decade].length}</span>
            `;
            
            const list = document.createElement('ul');
            list.className = 'group-list';
            list.style.cssText = 'margin: 0; padding-left: 15px;';
            
            decades[decade].forEach(item => {
                const li = document.createElement('li');
                li.className = 'chapter-item';
                li.style.cssText = 'margin: 2px 0;';
                const clonedLink = item.link.cloneNode(true);
                clonedLink.style.cssText = 'display: block; padding: 3px 5px; text-decoration: none; color: inherit;';
                li.appendChild(clonedLink);
                list.appendChild(li);
            });
            
            group.appendChild(header);
            group.appendChild(list);
            
            // Add toggle functionality
            header.addEventListener('click', () => {
                const arrow = header.querySelector('.group-arrow');
                const isHidden = list.style.display === 'none';
                list.style.display = isHidden ? '' : 'none';
                arrow.textContent = isHidden ? '▼' : '▶';
                header.classList.toggle('collapsed');
            });
            
            // Insert at the end of ordinances section
            const firstNonOrd = Array.from(chapterList.children).find(child => {
                const link = child.querySelector('a');
                return link && !link.href.includes('ordinances/');
            });
            
            if (firstNonOrd) {
                chapterList.insertBefore(group, firstNonOrd);
            } else {
                chapterList.appendChild(group);
            }
        });
    }
    
    showNumberView() {
        // Group by number ranges
        const ranges = [
            {label: '#1-50', min: 1, max: 50},
            {label: '#51-100', min: 51, max: 100},
            {label: '#101+', min: 101, max: 9999}
        ];
        
        const chapterList = document.querySelector('ol.chapter');
        
        ranges.forEach(range => {
            const items = this.allOrdinanceItems.filter(item => 
                item.number >= range.min && item.number <= range.max
            );
            
            if (items.length === 0) return;
            
            // Hide original items
            items.forEach(item => {
                item.element.style.display = 'none';
            });
            
            // Create range group
            const group = document.createElement('li');
            group.className = 'chapter-item view-group';
            group.classList.add('no-list-style');
            group.style.cssText = '';
            
            const header = document.createElement('div');
            header.className = 'group-header';
            header.innerHTML = `
                <span class="group-arrow">▼</span>
                <span class="group-name">${range.label}</span>
                <span class="group-count">${items.length}</span>
            `;
            
            const list = document.createElement('ul');
            list.className = 'group-list';
            list.style.cssText = 'margin: 0; padding-left: 15px;';
            
            items.sort((a, b) => a.number - b.number).forEach(item => {
                const li = document.createElement('li');
                li.className = 'chapter-item';
                li.style.cssText = 'margin: 2px 0;';
                const clonedLink = item.link.cloneNode(true);
                clonedLink.style.cssText = 'display: block; padding: 3px 5px; text-decoration: none; color: inherit;';
                li.appendChild(clonedLink);
                list.appendChild(li);
            });
            
            group.appendChild(header);
            group.appendChild(list);
            
            // Add toggle functionality
            header.addEventListener('click', () => {
                const arrow = header.querySelector('.group-arrow');
                const isHidden = list.style.display === 'none';
                list.style.display = isHidden ? '' : 'none';
                arrow.textContent = isHidden ? '▼' : '▶';
                header.classList.toggle('collapsed');
            });
            
            // Insert at the end of ordinances section
            const firstNonOrd = Array.from(chapterList.children).find(child => {
                const link = child.querySelector('a');
                return link && !link.href.includes('ordinances/');
            });
            
            if (firstNonOrd) {
                chapterList.insertBefore(group, firstNonOrd);
            } else {
                chapterList.appendChild(group);
            }
        });
    }
    
    showTopicalView() {
        // For now, just show chronological view
        // TODO: Implement topic grouping when we have topic data
        this.showChronologicalView();
    }
    
    filterOrdinances(searchTerm) {
        const term = searchTerm.toLowerCase();
        
        this.allOrdinanceItems.forEach(item => {
            const matches = !term || 
                item.title.toLowerCase().includes(term) ||
                item.id.toLowerCase().includes(term) ||
                item.year.includes(term);
            
            item.element.style.display = matches ? '' : 'none';
            
            // Also handle cloned items in groups
            if (this.currentView !== 'default') {
                document.querySelectorAll('.view-group a').forEach(link => {
                    if (link.href === item.link.href) {
                        link.parentElement.style.display = matches ? '' : 'none';
                    }
                });
            }
        });
        
        // Update stats
        const visible = this.allOrdinanceItems.filter(item => 
            item.element.style.display !== 'none'
        ).length;
        
        const visibleCount = document.getElementById('visibleCount');
        const totalCount = document.getElementById('totalCount');
        
        if (visibleCount) visibleCount.textContent = visible;
        if (totalCount) totalCount.textContent = this.allOrdinanceItems.length;
    }
    
    hideOtherSections() {
        // Add a style to hide non-ordinance sections - only in sidebar
        const style = document.createElement('style');
        style.textContent = `
            /* Hide section headers and non-ordinance items - ONLY in sidebar navigation */
            mdbook-sidebar-scrollbox ol.chapter > .spacer,
            mdbook-sidebar-scrollbox ol.chapter > .part-title:not(:first-of-type),
            mdbook-sidebar-scrollbox ol.chapter > li.chapter-item:has(a[href*="resolutions/"]),
            mdbook-sidebar-scrollbox ol.chapter > li.chapter-item:has(a[href*="interpretations/"]),
            mdbook-sidebar-scrollbox ol.chapter > li.chapter-item:has(a[href*="transcripts/"]) {
                display: none !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .nav-controls-panel {
                padding: 15px;
                background: #f8f9fa;
                border-bottom: 2px solid #dee2e6;
                margin-bottom: 10px;
            }
            
            .nav-header {
                margin-bottom: 12px;
            }
            
            .header-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .nav-title {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            
            .order-icons {
                display: flex;
                gap: 4px;
            }
            
            .order-icon {
                background: transparent;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 10px;
                cursor: pointer;
                color: #666;
                transition: all 0.2s;
            }
            
            .order-icon:hover {
                background: #e9ecef;
            }
            
            .order-icon.active {
                background: #0969da;
                color: white;
                border-color: #0969da;
            }
            
            .nav-controls-section {
                margin-bottom: 10px;
            }
            
            .control-label {
                font-size: 11px;
                color: #666;
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .nav-stats {
                font-size: 11px;
                color: #666;
                padding: 8px 15px;
                background: #f0f0f0;
                border-top: 1px solid #dee2e6;
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                margin: 0;
            }
            
            .nav-controls-panel {
                position: relative;
                padding-bottom: 40px; /* Make room for stats bar */
            }
            
            .nav-search-box {
                margin-bottom: 10px;
            }
            
            #ordSearch {
                width: 100%;
                padding: 6px 10px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-size: 13px;
            }
            
            .nav-view-buttons {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 4px;
            }
            
            .view-btn {
                padding: 6px 8px;
                border: 1px solid #dee2e6;
                background: white;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s;
                text-align: center;
            }
            
            .view-btn:hover {
                background: #f0f0f0;
            }
            
            .view-btn.active {
                background: #0969da;
                color: white;
                border-color: #0969da;
            }
            
            /* Group header styles */
            .group-header {
                display: flex;
                align-items: center;
                padding: 8px 10px;
                background: #f8f9fa;
                border-radius: 4px;
                cursor: pointer;
                user-select: none;
                margin: 5px 0;
                font-size: 13px;
                font-weight: 600;
                color: #333;
            }
            
            .group-header:hover {
                background: #e9ecef;
            }
            
            .group-header.collapsed {
                background: #fff;
                border: 1px solid #dee2e6;
            }
            
            .group-arrow {
                margin-right: 8px;
                font-size: 10px;
                transition: transform 0.2s;
            }
            
            .group-name {
                flex: 1;
            }
            
            .group-count {
                background: #dee2e6;
                color: #495057;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: normal;
            }
            
            /* Hide mdBook's automatic numbering for our custom groups */
            mdbook-sidebar-scrollbox .view-group {
                counter-reset: none !important;
                list-style: none !important;
            }
            
            mdbook-sidebar-scrollbox .view-group::before {
                display: none !important;
            }
            
            mdbook-sidebar-scrollbox .view-group .chapter-item::before {
                display: none !important;
            }
            
            mdbook-sidebar-scrollbox .group-list {
                list-style: none !important;
            }
            
            mdbook-sidebar-scrollbox .group-list li {
                list-style: none !important;
            }
            
            /* Ensure our grouped items don't show numbers - be specific to navigation only */
            mdbook-sidebar-scrollbox ol.chapter .view-group {
                list-style: none !important;
            }
            
            mdbook-sidebar-scrollbox ol.chapter .view-group li.chapter-item {
                list-style: none !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize when ready
window.addEventListener('load', () => {
    console.log('Window loaded, initializing navigation enhancer...');
    
    setTimeout(() => {
        const chapterList = document.querySelector('ol.chapter');
        if (chapterList && chapterList.children.length > 0) {
            new NavigationEnhancer();
        } else {
            console.error('Chapter list not ready');
        }
    }, 1000);
});