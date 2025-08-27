/**
 * Enhanced Navigation Controls for City of Rivergrove mdBook
 * Adds search, filtering, and view controls to the sidebar
 * Also implements the right panel for document relationships
 */

class NavigationController {
    constructor() {
        this.documents = [];
        this.relationships = {};
        this.currentView = 'chronological';  // Default to chronological like mockup
        this.searchTerm = '';
        this.currentDocument = null;
        this.sortOrder = 'asc';  // 'asc' for oldest first (default), 'desc' for newest first
        
        // Wait for DOM to be fully ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    async init() {
        // Detect which section we're in
        this.detectSection();
        
        // Load relationships data
        try {
            const response = await fetch('/relationships.json');
            if (response.ok) {
                const data = await response.json();
                this.documents = Object.values(data.documents);
                this.relationships = data.relationships || {};
                this.topics = data.topics || {};
                console.log('Loaded', this.documents.length, 'documents');
            } else {
                console.warn('Failed to load relationships.json:', response.status);
            }
        } catch (error) {
            console.warn('Could not load relationships.json:', error);
        }
        
        // Only enhance navigation if we're in a document section
        if (this.currentSection && this.currentSection !== 'home') {
            this.enhanceSidebar();
            this.filterSidebarToCurrentSection();
            this.addRightPanel();
            this.bindEvents();
            // Remove number prefixes again after enhancement
            this.removeNumberPrefixes();
            // Apply initial view - CRITICAL: Force the default active view to actually apply
            setTimeout(() => {
                this.applyInitialView();
                this.detectCurrentDocument();
                // One more time after delay to catch any late-rendered items
                this.removeNumberPrefixes();
            }, 100);
        }
    }
    
    filterSidebarToCurrentSection() {
        // Hide all items that aren't in the current section
        const sidebar = document.querySelector('.chapter');
        if (!sidebar) return;
        
        // Get all sidebar items
        const allItems = sidebar.querySelectorAll('li');
        let inCurrentSection = false;
        let currentSectionHeader = null;
        
        allItems.forEach(item => {
            // Check if this is a section header (part-title)
            if (item.classList.contains('part-title')) {
                const headerText = item.textContent.toLowerCase().trim();
                
                // Check if this header matches our current section
                if (
                    (this.currentSection === 'ordinances' && headerText.includes('ordinance')) ||
                    (this.currentSection === 'resolutions' && headerText.includes('resolution')) ||
                    (this.currentSection === 'interpretations' && headerText.includes('interpretation')) ||
                    (this.currentSection === 'transcripts' && (headerText.includes('transcript') || headerText.includes('meeting')))
                ) {
                    inCurrentSection = true;
                    currentSectionHeader = item;
                    item.style.display = 'none'; // Hide the section header itself
                } else {
                    inCurrentSection = false;
                    item.style.display = 'none'; // Hide other section headers
                }
            } 
            // Check if this is a spacer or separator
            else if (item.classList.contains('spacer') || item.classList.contains('affix')) {
                item.style.display = 'none'; // Always hide spacers
            }
            // Handle regular items
            else {
                const link = item.querySelector('a[href]');
                if (link) {
                    const href = link.getAttribute('href');
                    // Check if this item belongs to the current section
                    if (href && href.includes('/' + this.currentSection + '/')) {
                        item.style.display = ''; // Show items in current section
                    } else {
                        item.style.display = 'none'; // Hide items from other sections
                    }
                } else if (!inCurrentSection) {
                    // Hide items without links that aren't in our section
                    item.style.display = 'none';
                }
            }
        });
        
        console.log(`Filtered sidebar to show only ${this.currentSection}`);
        
        // Remove numbered list prefixes from sidebar items
        this.removeNumberPrefixes();
        
        // Update the document count
        const visibleDocs = sidebar.querySelectorAll('li.chapter-item:not([style*="display: none"])').length;
        const docCount = document.getElementById('docCount');
        if (docCount) {
            docCount.textContent = visibleDocs;
        }
    }
    
    removeNumberPrefixes() {
        // Find all links in the sidebar
        const sidebarLinks = document.querySelectorAll('.sidebar .chapter a');
        
        sidebarLinks.forEach(link => {
            let text = link.textContent;
            // Remove patterns like "1. ", "10. ", "1.1. " etc from the beginning
            const cleanedText = text.replace(/^\d+(\.\d+)*\.\s*/, '');
            
            if (cleanedText !== text) {
                // Only update if we actually removed something
                link.textContent = cleanedText;
                console.log(`Removed number prefix from: "${text}" -> "${cleanedText}"`);
            }
        });
    }
    
    detectSection() {
        const path = window.location.pathname;
        if (path.includes('/ordinances/')) {
            this.currentSection = 'ordinances';
        } else if (path.includes('/resolutions/')) {
            this.currentSection = 'resolutions';
        } else if (path.includes('/interpretations/')) {
            this.currentSection = 'interpretations';
        } else if (path.includes('/transcripts/')) {
            this.currentSection = 'transcripts';
        } else if (path === '/' || path.endsWith('/index.html') || path.endsWith('/')) {
            this.currentSection = 'home';
        } else {
            this.currentSection = null;
        }
    }
    
    enhanceSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;
        
        // Find the scrollbox where the chapter content is
        const scrollbox = sidebar.querySelector('.sidebar-scrollbox');
        if (!scrollbox) return;
        
        // Create enhanced header with section-specific controls
        const header = document.createElement('div');
        header.className = 'nav-header-enhanced';
        
        let controls = '';
        let placeholder = 'Search documents...';
        let docType = 'documents';
        
        switch(this.currentSection) {
            case 'ordinances':
                controls = `
                    <button class="nav-btn" data-view="numerical">Numerical</button>
                    <button class="nav-btn active" data-view="chronological">Chronological</button>
                    <button class="nav-btn" data-view="topical">Topical</button>
                `;
                placeholder = 'Search ordinances...';
                docType = 'ordinances';
                break;
            case 'resolutions':
                controls = `
                    <button class="nav-btn active" data-view="chronological">Chronological</button>
                    <button class="nav-btn" data-view="numerical">By Number</button>
                `;
                placeholder = 'Search resolutions...';
                docType = 'resolutions';
                break;
            case 'interpretations':
                controls = `
                    <button class="nav-btn active" data-view="chronological">By Date</button>
                    <button class="nav-btn" data-view="section">By Code Section</button>
                `;
                placeholder = 'Search interpretations...';
                docType = 'interpretations';
                break;
            case 'transcripts':
                controls = `
                    <button class="nav-btn active" data-view="chronological">By Date</button>
                `;
                placeholder = 'Search transcripts...';
                docType = 'transcripts';
                break;
        }
        
        // Get a cleaner section name for display
        const sectionNames = {
            'ordinances': 'Ordinances',
            'resolutions': 'Resolutions', 
            'interpretations': 'Interpretations',
            'transcripts': 'Meeting Records'
        };
        const currentSectionName = sectionNames[this.currentSection] || 'Documents';
        
        header.innerHTML = `
            <div class="nav-header-top">
                <div class="nav-section-selector">
                    <button class="section-dropdown-btn" id="sectionDropdown">
                        <span class="section-name">${currentSectionName}</span>
                        <span class="dropdown-arrow">▾</span>
                    </button>
                    <div class="section-dropdown-menu" id="sectionMenu" style="display: none;">
                        <a href="/" class="dropdown-item">
                            <span class="dropdown-icon">🏠</span> Home
                        </a>
                        <div class="dropdown-divider"></div>
                        <a href="/ordinances/1974-Ord-16-Parks.html" class="dropdown-item ${this.currentSection === 'ordinances' ? 'active' : ''}">
                            Ordinances
                        </a>
                        <a href="/resolutions/1976-Res-22-PC.html" class="dropdown-item ${this.currentSection === 'resolutions' ? 'active' : ''}">
                            Resolutions
                        </a>
                        <a href="/interpretations/1997-07-07-RE-2.040h-permitting-adus.html" class="dropdown-item ${this.currentSection === 'interpretations' ? 'active' : ''}">
                            Interpretations
                        </a>
                        <a href="/transcripts/02-2024-Transcript.html" class="dropdown-item ${this.currentSection === 'transcripts' ? 'active' : ''}">
                            Meeting Records
                        </a>
                    </div>
                </div>
                <div class="sort-toggle" title="Sort order">
                    <button class="sort-toggle-btn ${this.sortOrder === 'asc' ? 'active' : ''}" 
                            data-sort="asc" 
                            title="Sort oldest first">
                        <span>⬆</span>
                    </button>
                    <button class="sort-toggle-btn ${this.sortOrder === 'desc' ? 'active' : ''}" 
                            data-sort="desc" 
                            title="Sort newest first">
                        <span>⬇</span>
                    </button>
                </div>
            </div>
            <div class="nav-search-container">
                <input type="text" 
                       class="nav-search" 
                       placeholder="${placeholder}" 
                       id="navSearch">
            </div>
            <div class="nav-controls">
                ${controls}
            </div>
            <div class="nav-stats" id="navStats">
                <span id="docCount">0</span> ${docType}
            </div>
        `;
        
        // Insert header before scrollbox content
        scrollbox.prepend(header);
    }
    
    addRightPanel() {
        // Check if panel already exists
        if (document.getElementById('rightPanel')) return;
        
        // Create right panel
        const rightPanel = document.createElement('div');
        rightPanel.className = 'right-panel';
        rightPanel.id = 'rightPanel';
        rightPanel.innerHTML = `
            <div class="right-panel-header">
                <h3>Document Relationships</h3>
                <button class="panel-toggle" id="panelToggle" title="Close panel">×</button>
            </div>
            <div class="right-panel-content" id="rightPanelContent">
                <div class="panel-placeholder">
                    Loading document relationships...
                </div>
            </div>
        `;
        
        // Add panel to page
        document.body.appendChild(rightPanel);
        
        // Adjust main content width to make room for the panel
        const mainContent = document.querySelector('.content');
        if (mainContent) {
            mainContent.style.marginRight = '300px';
        }
    }
    
    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('navSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.updateSidebar();
            });
            
            // Clear search on Escape key
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    searchInput.value = '';
                    this.searchTerm = '';
                    this.updateSidebar();
                    searchInput.blur(); // Remove focus from search box
                }
            });
        }
        
        // View controls
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentView = e.target.dataset.view;
                // For now, just reorder based on the view - don't replace content
                this.updateSidebar();
            });
        });
        
        // Section dropdown
        const dropdownBtn = document.getElementById('sectionDropdown');
        const dropdownMenu = document.getElementById('sectionMenu');
        if (dropdownBtn && dropdownMenu) {
            dropdownBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = dropdownMenu.style.display !== 'none';
                dropdownMenu.style.display = isVisible ? 'none' : 'block';
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                dropdownMenu.style.display = 'none';
            });
        }
        
        // Sort toggle controls (pill-style buttons)
        document.querySelectorAll('.sort-toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sortButton = e.target.closest('.sort-toggle-btn');
                if (!sortButton) return;
                
                const newSortOrder = sortButton.dataset.sort;
                console.log('Sort button clicked:', newSortOrder, 'Current:', this.sortOrder);
                
                // Update active state
                document.querySelectorAll('.sort-toggle-btn').forEach(b => b.classList.remove('active'));
                sortButton.classList.add('active');
                
                // Update sort order
                this.sortOrder = newSortOrder;
                
                // Re-apply current view with new sort order
                this.updateSidebar();
            });
        });
        
        // Panel toggle
        const panelToggle = document.getElementById('panelToggle');
        if (panelToggle) {
            panelToggle.addEventListener('click', () => {
                this.toggleRightPanel();
            });
        }
        
        // Document link clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href*=".html"]');
            if (link) {
                setTimeout(() => {
                    this.detectCurrentDocument();
                }, 100);
            }
        });
    }
    
    detectCurrentDocument() {
        const currentPath = window.location.pathname;
        const filename = currentPath.split('/').pop().replace('.html', '.md');
        
        console.log('Detecting document for:', filename);
        
        // Find matching document
        const doc = this.documents.find(d => {
            // Match by file name
            if (d.file === filename) return true;
            
            // Also try matching with variations in the filename format
            const simplifiedFile = d.file.replace('#', '');
            const simplifiedCurrent = filename.replace('#', '');
            
            return simplifiedFile === simplifiedCurrent;
        });
        
        if (doc) {
            console.log('Found document:', doc);
            this.currentDocument = doc;
            this.updateRightPanel();
            this.highlightCurrentDocument();
        } else {
            console.log('Document not found for:', filename);
            this.highlightCurrentDocument();
        }
    }
    
    highlightCurrentDocument() {
        // Remove any existing active states
        document.querySelectorAll('.sidebar .chapter-item').forEach(item => {
            item.classList.remove('active', 'selected');
        });
        document.querySelectorAll('.sidebar a').forEach(link => {
            link.classList.remove('active', 'selected');
        });
        
        // Get current path
        const currentPath = window.location.pathname;
        
        // Find and highlight the matching link
        const sidebarLinks = document.querySelectorAll('.sidebar a[href]');
        sidebarLinks.forEach(link => {
            const href = link.getAttribute('href');
            // Check if this link matches the current path
            if (href && (currentPath.endsWith(href) || href.endsWith(currentPath.split('/').pop()))) {
                link.classList.add('active', 'selected');
                const parentLi = link.closest('li');
                if (parentLi) {
                    parentLi.classList.add('active', 'selected');
                }
            }
        });
    }
    
    applyInitialView() {
        // Find the active button and ensure the view is properly applied on page load
        const activeBtn = document.querySelector('.nav-btn.active');
        if (activeBtn) {
            const activeView = activeBtn.dataset.view;
            console.log('Applying initial view:', activeView);
            this.currentView = activeView;
            this.updateSidebar();
        }
    }
    
    updateSidebar() {
        const sidebar = document.querySelector('.chapter');
        if (!sidebar) return;
        
        // Get existing items and reorder them instead of replacing
        const items = Array.from(sidebar.querySelectorAll('li.chapter-item:not(.grouped-item):not(.group-header)')).filter(li => {
            // Only get visible items with links
            if (li.style.display === 'none') return false;
            const link = li.querySelector('a[href*=".html"]');
            return link !== null;
        });
        
        if (items.length > 0) {
            // Apply the current view (grouping or reordering)
            this.applyCurrentView(sidebar, items);
        } else {
            // Fallback to custom rendering only if no items found
            const filtered = this.filterDocuments();
            this.renderChronologicalView(sidebar, filtered);
        }
        
        // Update stats
        const visibleItems = sidebar.querySelectorAll('li.chapter-item:not([style*="display: none"])').length;
        const docCount = document.getElementById('docCount');
        if (docCount) {
            docCount.textContent = visibleItems;
        }
        
        // Highlight the current document after sidebar update
        this.highlightCurrentDocument();
    }
    
    reorderExistingItemsByView(container, items) {
        // For proper grouping, we need to use custom rendering
        // Clear existing items and render with groups
        const sidebar = document.querySelector('.chapter');
        if (!sidebar) return;
        
        // Store current scroll position
        const scrollbox = document.querySelector('.sidebar-scrollbox');
        const scrollPos = scrollbox?.scrollTop || 0;
        
        // Get the data from existing items to recreate with grouping
        const itemData = items.map(item => {
            const link = item.querySelector('a[href*=".html"]');
            if (!link) return null;
            
            const text = link.textContent?.trim() || '';
            const href = link.getAttribute('href') || '';
            const numberMatch = text.match(/#?(\d+)/);
            const number = numberMatch ? parseInt(numberMatch[1]) : 0;
            const year = this.extractYear(href) || this.extractYear(text) || '0000';
            
            return {
                text,
                href,
                number,
                year,
                element: item
            };
        }).filter(item => item !== null);
        
        // Clear the sidebar items
        items.forEach(item => {
            if (item.parentElement) {
                item.remove();
            }
        });
        
        // Render groups based on view
        this.renderGroupedView(sidebar, itemData);
        
        // Restore scroll position
        if (scrollbox) {
            scrollbox.scrollTop = scrollPos;
        }
    }
    
    renderGroupedView(container, itemData) {
        let html = '';
        
        if (this.currentView === 'numerical') {
            // Group by number ranges (e.g., 1-20, 21-40, etc.)
            const groups = {};
            itemData.forEach(item => {
                const rangeStart = Math.floor((item.number - 1) / 20) * 20 + 1;
                const rangeEnd = rangeStart + 19;
                const key = `${rangeStart}-${rangeEnd}`;
                if (!groups[key]) groups[key] = [];
                groups[key].push(item);
            });
            
            Object.keys(groups).sort((a, b) => {
                const aStart = parseInt(a.split('-')[0]);
                const bStart = parseInt(b.split('-')[0]);
                return aStart - bStart;
            }).forEach(range => {
                const items = groups[range].sort((a, b) => a.number - b.number);
                html += `
                    <li class="group-header">
                        <div class="group-title">Numbers ${range}</div>
                    </li>
                `;
                items.forEach(item => {
                    html += `
                        <li class="chapter-item grouped-item">
                            <a href="${item.href}" class="doc-link">${item.text}</a>
                        </li>
                    `;
                });
            });
            
        } else if (this.currentView === 'chronological') {
            // Group by decades
            const groups = {};
            itemData.forEach(item => {
                const year = parseInt(item.year);
                const decade = Math.floor(year / 10) * 10;
                const key = `${decade}s`;
                if (!groups[key]) groups[key] = [];
                groups[key].push(item);
            });
            
            // Sort decades by the sort order as well
            const sortedDecades = Object.keys(groups).sort((a, b) => {
                if (this.sortOrder === 'asc') {
                    return a.localeCompare(b); // 1970s, 1980s, 1990s...
                } else {
                    return b.localeCompare(a); // 2020s, 2010s, 2000s...
                }
            });
            
            sortedDecades.forEach(decade => {
                const items = groups[decade].sort((a, b) => {
                    if (this.sortOrder === 'asc') {
                        return a.year.localeCompare(b.year);
                    } else {
                        return b.year.localeCompare(a.year);
                    }
                });
                html += `
                    <li class="group-header">
                        <div class="group-title">${decade}</div>
                    </li>
                `;
                items.forEach(item => {
                    html += `
                        <li class="chapter-item grouped-item">
                            <a href="${item.href}" class="doc-link">${item.text}</a>
                        </li>
                    `;
                });
            });
            
        } else if (this.currentView === 'topical') {
            // Group by topics based on keywords
            const groups = {};
            itemData.forEach(item => {
                let topic = 'General';
                const text = item.text.toLowerCase();
                
                if (text.includes('park') || text.includes('recreation')) {
                    topic = 'Parks & Recreation';
                } else if (text.includes('water') || text.includes('sewer') || text.includes('utility')) {
                    topic = 'Utilities';
                } else if (text.includes('development') || text.includes('planning') || text.includes('zoning')) {
                    topic = 'Development & Planning';
                } else if (text.includes('flood') || text.includes('drainage')) {
                    topic = 'Flood Management';
                } else if (text.includes('fee') || text.includes('tax') || text.includes('budget')) {
                    topic = 'Finance';
                } else if (text.includes('building') || text.includes('construction')) {
                    topic = 'Building & Construction';
                }
                
                if (!groups[topic]) groups[topic] = [];
                groups[topic].push(item);
            });
            
            Object.keys(groups).sort().forEach(topic => {
                const items = groups[topic].sort((a, b) => a.text.localeCompare(b.text));
                html += `
                    <li class="group-header">
                        <div class="group-title">${topic} (${items.length})</div>
                    </li>
                `;
                items.forEach(item => {
                    html += `
                        <li class="chapter-item grouped-item">
                            <a href="${item.href}" class="doc-link">${item.text}</a>
                        </li>
                    `;
                });
            });
        }
        
        container.innerHTML = html;
        
        // Run number prefix removal and update document count
        setTimeout(() => {
            this.removeNumberPrefixes();
            // Update document count
            const visibleItems = container.querySelectorAll('li.chapter-item:not([style*="display: none"])').length;
            const docCount = document.getElementById('docCount');
            if (docCount) {
                docCount.textContent = visibleItems;
            }
            // Highlight current document
            this.highlightCurrentDocument();
        }, 50);
    }
    
    refreshSidebar() {
        // Force a page reload to restore the original sidebar state
        console.log('Refreshing sidebar due to DOM corruption');
        window.location.reload();
    }
    
    reorderExistingItems(container, items) {
        // Clone the items array to avoid modifying the original
        const itemsToSort = [...items];
        
        // Sort items based on current view and sort order
        itemsToSort.sort((a, b) => {
            const linkA = a.querySelector('a[href*=".html"]');
            const linkB = b.querySelector('a[href*=".html"]');
            
            if (!linkA || !linkB) return 0;
            
            // Extract info from the link text and href
            const textA = linkA.textContent.trim();
            const textB = linkB.textContent.trim();
            const hrefA = linkA.getAttribute('href') || '';
            const hrefB = linkB.getAttribute('href') || '';
            
            if (this.currentView === 'numerical') {
                // Extract numbers from text (e.g., "#16" or "Ord #16")
                const numA = parseInt(textA.match(/#?(\d+)/)?.[1] || '0');
                const numB = parseInt(textB.match(/#?(\d+)/)?.[1] || '0');
                
                // Always sort numerically ascending
                return numA - numB;
            } else if (this.currentView === 'chronological') {
                // Extract years from href first (more reliable), then text
                const yearA = this.extractYear(hrefA) || this.extractYear(textA) || '0000';
                const yearB = this.extractYear(hrefB) || this.extractYear(textB) || '0000';
                
                // Apply sort order
                if (this.sortOrder === 'asc') {
                    return yearA.localeCompare(yearB); // Oldest first
                } else {
                    return yearB.localeCompare(yearA); // Newest first
                }
            }
            
            return 0;
        });
        
        // Find the parent that contains these items
        const parent = items[0]?.parentElement;
        if (!parent) return;
        
        // Store current scroll position
        const scrollbox = document.querySelector('.sidebar-scrollbox');
        const scrollPos = scrollbox?.scrollTop || 0;
        
        // Remove all items first
        items.forEach(item => {
            if (item.parentElement === parent) {
                parent.removeChild(item);
            }
        });
        
        // Re-append in sorted order
        itemsToSort.forEach(item => {
            parent.appendChild(item);
        });
        
        // Restore scroll position
        if (scrollbox) {
            scrollbox.scrollTop = scrollPos;
        }
        
        console.log(`Reordered ${itemsToSort.length} items in ${this.currentView} view, sort: ${this.sortOrder}`);
    }
    
    applyCurrentView(sidebar, items) {
        // Clear any existing grouping first
        const existingGroups = sidebar.querySelectorAll('.group-header, .decade-header');
        existingGroups.forEach(group => group.remove());
        const groupedItems = sidebar.querySelectorAll('.grouped-item');
        groupedItems.forEach(item => item.classList.remove('grouped-item'));
        
        // Apply view-specific logic
        if (this.currentView === 'numerical' || this.currentView === 'topical') {
            // For grouping views, extract data and render groups
            this.reorderExistingItemsByView(sidebar, items);
        } else if (this.currentView === 'chronological') {
            // For chronological view, check if we need to group by decades
            const activeBtn = document.querySelector('.nav-btn.active');
            if (activeBtn && activeBtn.dataset.view === 'chronological' && this.currentSection === 'ordinances') {
                // Apply decade grouping for ordinances chronological view
                this.reorderExistingItemsByView(sidebar, items);
            } else {
                // Just reorder existing items
                this.reorderExistingItems(sidebar, items);
            }
        }
    }
    
    extractYear(text) {
        if (!text) return null;
        // Try to find a 4-digit year
        const yearMatch = text.match(/\b(19\d{2}|20\d{2})\b/);
        return yearMatch ? yearMatch[1] : null;
    }
    
    filterDocuments() {
        // Start with documents from the current section
        let sectionDocuments = this.documents.filter(doc => {
            switch(this.currentSection) {
                case 'ordinances': return doc.type === 'ordinance';
                case 'resolutions': return doc.type === 'resolution';
                case 'interpretations': return doc.type === 'interpretation';
                case 'transcripts': return doc.type === 'transcript';
                default: return true;
            }
        });
        
        // Apply search filter if there's a search term
        if (!this.searchTerm) return sectionDocuments;
        
        return sectionDocuments.filter(doc => {
            return (
                (doc.id && doc.id.toLowerCase().includes(this.searchTerm)) ||
                (doc.title && doc.title.toLowerCase().includes(this.searchTerm)) ||
                (doc.year && doc.year.toString().includes(this.searchTerm)) ||
                (doc.date && doc.date.includes(this.searchTerm)) ||
                (doc.section && doc.section.toLowerCase().includes(this.searchTerm))
            );
        });
    }
    
    renderNumericalView(container, documents) {
        // Sort by document number
        const sorted = documents.sort((a, b) => {
            const numA = parseInt(a.id?.replace(/\D/g, '') || '0');
            const numB = parseInt(b.id?.replace(/\D/g, '') || '0');
            return numA - numB;
        });
        
        this.renderDocumentList(container, sorted);
    }
    
    renderDocumentList(container, documents) {
        // Generate HTML for document list
        const html = documents.map(doc => {
            // Build the correct path based on section
            let href = '/' + this.currentSection + '/' + doc.file.replace('.md', '.html').replace('#', '');
            
            const displayId = doc.id || (doc.date ? doc.date : 'N/A');
            const year = doc.year || (doc.date ? doc.date.substring(0, 4) : '');
            
            // Clean up the ID display
            let cleanId = displayId;
            if (displayId.includes('-')) {
                // Extract just the number from IDs like "71-2002-Gates"
                cleanId = displayId.split('-')[0];
            }
            
            // Clean up title - remove redundant info
            let displayTitle = doc.title || doc.file;
            if (displayTitle.startsWith('AN ORDINANCE')) {
                displayTitle = displayTitle.replace(/^AN ORDINANCE\s*/i, '').trim();
            }
            if (displayTitle.startsWith('BEFORE THE CITY')) {
                displayTitle = displayTitle.replace(/^BEFORE THE CITY.*?OREGON\s*/i, '').trim();
            }
            // Truncate very long titles
            if (displayTitle.length > 60) {
                displayTitle = displayTitle.substring(0, 57) + '...';
            }
            
            return `
                <li class="chapter-item">
                    <a href="${href}" class="doc-link">
                        <span class="doc-number">#${cleanId}</span>
                        <span class="doc-title">${displayTitle}</span>
                        ${year ? `<span class="doc-year">(${year})</span>` : ''}
                    </a>
                </li>
            `;
        }).join('');
        
        container.innerHTML = html;
    }
    
    renderChronologicalView(container, documents) {
        // Sort chronologically based on sortOrder
        const sorted = documents.sort((a, b) => {
            const aDate = a.year || a.date || '0000';
            const bDate = b.year || b.date || '0000';
            
            // Apply sort order
            if (this.sortOrder === 'asc') {
                return aDate.localeCompare(bDate); // Oldest first
            } else {
                return bDate.localeCompare(aDate); // Newest first
            }
        });
        
        this.renderDocumentList(container, sorted);
    }
    
    renderTopicalView(container, documents) {
        // Filter documents by current section
        const sectionDocuments = documents.filter(doc => {
            switch(this.currentSection) {
                case 'ordinances': return doc.type === 'ordinance';
                case 'resolutions': return doc.type === 'resolution';
                case 'interpretations': return doc.type === 'interpretation';
                case 'transcripts': return doc.type === 'transcript';
                default: return true;
            }
        });
        
        // Group by topic - use simple keyword-based classification
        const topics = {};
        sectionDocuments.forEach(doc => {
            let topic = 'General';
            const title = (doc.title || '').toLowerCase();
            
            // Simple topic classification
            if (title.includes('park') || title.includes('recreation')) {
                topic = 'Parks & Recreation';
            } else if (title.includes('water') || title.includes('sewer') || title.includes('utility')) {
                topic = 'Utilities';
            } else if (title.includes('development') || title.includes('planning') || title.includes('zoning')) {
                topic = 'Development & Planning';
            } else if (title.includes('flood') || title.includes('drainage')) {
                topic = 'Flood Management';
            } else if (title.includes('fee') || title.includes('tax') || title.includes('budget')) {
                topic = 'Finance';
            } else if (title.includes('building') || title.includes('construction')) {
                topic = 'Building & Construction';
            }
            
            if (!topics[topic]) topics[topic] = [];
            topics[topic].push(doc);
        });
        
        // Sort topics alphabetically
        const sortedTopics = Object.keys(topics).sort();
        
        let html = '';
        sortedTopics.forEach(topic => {
            html += `
                <li class="topic-group">
                    <div class="topic-header">${topic}</div>
                    <ul class="topic-list">
                        ${topics[topic].map(doc => {
                            const href = '/' + this.currentSection + '/' + doc.file.replace('.md', '.html');
                            const cleanId = doc.id?.includes('-') ? doc.id.split('-')[0] : doc.id;
                            const year = doc.year || doc.date?.split('-')[0] || '';
                            return `
                                <li>
                                    <a href="${href}" class="doc-link">
                                        <span class="doc-number">#${cleanId}</span>
                                        <span class="doc-title">${doc.title}</span>
                                        ${year ? `<span class="doc-year">(${year})</span>` : ''}
                                    </a>
                                </li>
                            `;
                        }).join('')}
                    </ul>
                </li>
            `;
        });
        
        container.innerHTML = html;
    }
    
    renderDecadeViewOld(container, documents) {
        const grouped = {};
        
        documents.forEach(doc => {
            const year = parseInt(doc.year || (doc.date ? doc.date.substring(0, 4) : '0000'));
            const decade = Math.floor(year / 10) * 10;
            const key = decade === 0 ? 'Unknown' : `${decade}s`;
            
            if (!grouped[key]) grouped[key] = [];
            grouped[key].push(doc);
        });
        
        const html = Object.keys(grouped)
            .sort((a, b) => a === 'Unknown' ? 1 : b === 'Unknown' ? -1 : a.localeCompare(b))
            .map(decade => {
                const docs = grouped[decade].sort((a, b) => {
                    const aDate = a.year || a.date || '0000';
                    const bDate = b.year || b.date || '0000';
                    return aDate.localeCompare(bDate);
                });
                
                return `
                    <li class="chapter-item expanded">
                        <div class="decade-header">${decade}</div>
                        <ul class="decade-list">
                            ${docs.map(doc => {
                                const href = doc.file.replace('.md', '.html');
                                const displayId = doc.id || doc.date;
                                return `
                                    <li class="chapter-item">
                                        <a href="${href}" class="doc-link">
                                            <span class="doc-number">#${displayId}</span>
                                            <span class="doc-title">${doc.title}</span>
                                        </a>
                                    </li>
                                `;
                            }).join('')}
                        </ul>
                    </li>
                `;
            }).join('');
        
        container.innerHTML = html;
    }
    
    renderTopicViewOld(container, documents) {
        if (!this.topics) {
            this.renderListView(container, documents);
            return;
        }
        
        const html = Object.keys(this.topics)
            .map(topic => {
                const topicDocs = this.topics[topic]
                    .map(docKey => this.documents.find(d => this.getDocumentKey(d) === docKey))
                    .filter(d => d && documents.includes(d));
                
                if (topicDocs.length === 0) return '';
                
                return `
                    <li class="chapter-item expanded">
                        <div class="topic-header">${topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                        <ul class="topic-list">
                            ${topicDocs.map(doc => {
                                const href = doc.file.replace('.md', '.html');
                                const displayId = doc.id || doc.date;
                                const year = doc.year || (doc.date ? doc.date.substring(0, 4) : '');
                                return `
                                    <li class="chapter-item">
                                        <a href="${href}" class="doc-link">
                                            <span class="doc-number">#${displayId}</span>
                                            <span class="doc-title">${doc.title}</span>
                                            <span class="doc-year">(${year})</span>
                                        </a>
                                    </li>
                                `;
                            }).join('')}
                        </ul>
                    </li>
                `;
            }).join('');
        
        container.innerHTML = html;
    }
    
    updateRightPanel() {
        const content = document.getElementById('rightPanelContent');
        if (!content) {
            console.log('Right panel content element not found');
            return;
        }
        
        if (!this.currentDocument) {
            content.innerHTML = '<div class="panel-placeholder">Select a document to view its relationships</div>';
            return;
        }
        
        const docKey = this.getDocumentKey(this.currentDocument);
        console.log('Looking for relationships for:', docKey);
        const rels = this.relationships[docKey];
        
        if (!rels) {
            // Try a simplified version of the key
            const simplifiedKey = `${this.currentDocument.type}-${this.currentDocument.id?.split('-')[0] || this.currentDocument.date}`;
            const alternateRels = this.relationships[simplifiedKey];
            
            if (!alternateRels) {
                content.innerHTML = `
                    <div class="current-document">
                        <h4>${this.currentDocument.title}</h4>
                        <p class="doc-meta">
                            ${this.currentDocument.type.charAt(0).toUpperCase() + this.currentDocument.type.slice(1)} 
                            #${this.currentDocument.id?.split('-')[0] || this.currentDocument.date || ''}
                        </p>
                    </div>
                    <div class="panel-placeholder">No relationships found for this document</div>
                `;
                return;
            }
            // Use the alternate relationships if found
            rels = alternateRels;
        }
        
        let html = `
            <div class="current-document">
                <h4>${this.currentDocument.title}</h4>
                <p class="doc-meta">
                    ${this.currentDocument.type.charAt(0).toUpperCase() + this.currentDocument.type.slice(1)} 
                    #${this.currentDocument.id?.split('-')[0] || this.currentDocument.date || ''}
                </p>
            </div>
        `;
        
        let hasRelationships = false;
        
        // Amendments
        if (rels.amended_by && rels.amended_by.length > 0) {
            html += this.renderRelationshipSection('Amended By', rels.amended_by, 'amendment');
            hasRelationships = true;
        }
        
        if (rels.amends && rels.amends.length > 0) {
            html += this.renderRelationshipSection('Amends', rels.amends, 'amendment');
            hasRelationships = true;
        }
        
        // References
        if (rels.referenced_by && rels.referenced_by.length > 0) {
            html += this.renderRelationshipSection('Referenced By', rels.referenced_by, 'reference');
            hasRelationships = true;
        }
        
        if (rels.references && rels.references.length > 0) {
            html += this.renderRelationshipSection('References', rels.references, 'reference');
            hasRelationships = true;
        }
        
        // Interpretations
        if (rels.interpretations && rels.interpretations.length > 0) {
            html += this.renderRelationshipSection('Code Sections', rels.interpretations, 'interpretation');
            hasRelationships = true;
        }
        
        // Resolutions
        if (rels.resolutions && rels.resolutions.length > 0) {
            html += this.renderRelationshipSection('Related Resolutions', rels.resolutions, 'resolution');
            hasRelationships = true;
        }
        
        // Related documents
        if (rels.related && rels.related.length > 0) {
            html += this.renderRelationshipSection('Related Documents', rels.related.slice(0, 5), 'related');
            hasRelationships = true;
        }
        
        if (!hasRelationships) {
            html += '<div class="panel-placeholder">No relationships found for this document</div>';
        }
        
        content.innerHTML = html;
    }
    
    renderRelationshipSection(title, items, type) {
        const docs = items.map(item => {
            if (typeof item === 'string' && item.includes('-')) {
                // It's a document key
                return this.documents.find(d => this.getDocumentKey(d) === item);
            } else {
                // It's a reference ID, try to find matching document
                return this.documents.find(d => d.id === item);
            }
        }).filter(d => d);
        
        if (docs.length === 0 && type !== 'interpretation') return '';
        
        let html = `
            <div class="relationship-section">
                <h5>${title}</h5>
                <ul class="relationship-list">
        `;
        
        if (type === 'interpretation') {
            // Show section references
            items.forEach(section => {
                html += `<li class="relationship-item section-ref">Section ${section}</li>`;
            });
        } else {
            // Show document links
            docs.forEach(doc => {
                const href = doc.file.replace('.md', '.html');
                const displayId = doc.id || doc.date;
                const year = doc.year || (doc.date ? doc.date.substring(0, 4) : '');
                
                html += `
                    <li class="relationship-item">
                        <a href="${href}" class="rel-link">
                            <span class="rel-number">#${displayId}</span>
                            <span class="rel-title">${doc.title}</span>
                            <span class="rel-year">(${year})</span>
                        </a>
                    </li>
                `;
            });
        }
        
        html += '</ul></div>';
        return html;
    }
    
    getDocumentKey(doc) {
        const id = doc.id || doc.date || doc.section || 'unknown';
        return `${doc.type}-${id}`;
    }
    
    toggleRightPanel() {
        const panel = document.getElementById('rightPanel');
        const mainContent = document.querySelector('.content');
        
        if (panel.classList.contains('collapsed')) {
            panel.classList.remove('collapsed');
            if (mainContent) mainContent.style.marginRight = '300px';
        } else {
            panel.classList.add('collapsed');
            if (mainContent) mainContent.style.marginRight = '0';
        }
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new NavigationController());
} else {
    new NavigationController();
}