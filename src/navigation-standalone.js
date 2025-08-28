/**
 * Standalone Navigation System for City of Rivergrove
 * 
 * This replaces mdBook's sidebar entirely to avoid DOM conflicts.
 * Architecture:
 * - Hides mdBook's sidebar completely via CSS
 * - Creates our own sidebar container
 * - Builds from relationships.json as single source of truth
 * - Handles navigation with History API
 * - No mutation observers, no DOM manipulation of mdBook elements
 */

class StandaloneNavigation {
    constructor() {
        this.documents = {};
        this.relationships = {};
        this.currentView = 'chronological';
        this.currentOrder = 'asc';
        this.currentDocType = 'ordinances';
        this.currentDocId = null;
        
        this.init();
    }
    
    async init() {
        console.log('StandaloneNavigation: Initializing clean navigation system...');
        
        // Hide mdBook's sidebar immediately
        this.hideMdBookSidebar();
        
        // Load data
        await this.loadRelationships();
        
        // Create our navigation UI
        this.createNavigationUI();
        
        // Handle browser navigation
        this.setupNavigationHandlers();
        
        // Set initial state
        this.detectCurrentDocument();
        
        console.log('StandaloneNavigation: Initialization complete');
    }
    
    hideMdBookSidebar() {
        // Hide mdBook's sidebar without removing it (mdBook needs it internally)
        const style = document.createElement('style');
        style.id = 'standalone-nav-override';
        style.textContent = `
            /* Hide mdBook's sidebar completely */
            #sidebar, .sidebar {
                display: none !important;
                visibility: hidden !important;
                width: 0 !important;
                opacity: 0 !important;
            }
            
            /* AGGRESSIVELY override page wrapper positioning */
            .page-wrapper {
                margin-left: 300px !important;
                margin-right: 280px !important;
                transform: none !important;
                transition: none !important;
                animation: none !important;
                animation-duration: 0s !important;
                transition-duration: 0s !important;
            }
            
            /* Override all possible animation sources - but preserve content visibility */
            .page-wrapper,
            #sidebar,
            .sidebar {
                animation: none !important;
                animation-duration: 0s !important;
                animation-delay: 0s !important;
                animation-fill-mode: none !important;
                transition: none !important;
                transition-duration: 0s !important;
                transition-delay: 0s !important;
                transform: none !important;
            }
            
            /* Prevent horizontal scrolling */
            body, html {
                overflow-x: hidden !important;
            }
            
            /* Target specific mdBook classes - ensure they're visible */
            #content,
            .content,
            .chapter,
            main {
                margin-left: 0 !important;
                margin-right: 0 !important;
                transform: translateX(0) !important;
                transition: none !important;
                animation: none !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            /* Make sure page content is visible */
            .page {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            /* Override any slide effects */
            @keyframes slide-in {
                from, to { transform: translateX(0) !important; }
            }
            
            /* Disable print styles that might interfere */
            @media screen {
                .page-wrapper {
                    margin-left: 300px !important;
                    margin-right: 280px !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    async loadRelationships() {
        try {
            const response = await fetch('/relationships.json');
            const data = await response.json();
            this.documents = data.documents || {};
            this.relationships = data.relationships || {};
            console.log(`StandaloneNavigation: Loaded ${Object.keys(this.documents).length} documents`);
        } catch (error) {
            console.error('StandaloneNavigation: Failed to load relationships.json:', error);
            // Fallback: parse from current page structure if needed
            this.parseDocumentsFromDOM();
        }
    }
    
    parseDocumentsFromDOM() {
        // Fallback method to extract document info from page if relationships.json fails
        console.log('StandaloneNavigation: Parsing documents from DOM as fallback...');
        
        // This would parse the SUMMARY.md structure if needed
        // For now, we'll rely on relationships.json being present
    }
    
    createNavigationUI() {
        // Create LEFT sidebar container
        const leftContainer = document.createElement('div');
        leftContainer.id = 'standalone-navigation';
        leftContainer.className = 'standalone-nav-container';
        leftContainer.innerHTML = `
            <div class="nav-sidebar">
                <div class="nav-header">
                    <!-- Context Switcher Dropdown -->
                    <div class="context-switcher">
                        <button class="context-dropdown" aria-label="Switch document type">
                            <span class="context-icon">📋</span>
                            <span class="context-label">Ordinances</span>
                            <span class="dropdown-arrow">▼</span>
                        </button>
                        <div class="context-menu" style="display: none;">
                            <div class="context-item active" data-type="ordinances" data-icon="📋">
                                <span class="context-icon">📋</span>
                                Ordinances
                                <span class="context-count">19</span>
                            </div>
                            <div class="context-item" data-type="resolutions" data-icon="📄">
                                <span class="context-icon">📄</span>
                                Resolutions
                                <span class="context-count">3</span>
                            </div>
                            <div class="context-item" data-type="interpretations" data-icon="📝">
                                <span class="context-icon">📝</span>
                                Interpretations
                                <span class="context-count">12</span>
                            </div>
                            <div class="context-item" data-type="transcripts" data-icon="🎙️">
                                <span class="context-icon">🎙️</span>
                                Meeting Records
                                <span class="context-count">2</span>
                            </div>
                            <hr class="context-divider">
                            <div class="context-item" data-type="home" data-icon="🏠">
                                <span class="context-icon">🏠</span>
                                Home / Overview
                            </div>
                        </div>
                    </div>
                    
                    <div class="nav-title-row">
                        <div class="order-controls">
                            <button class="order-btn active" data-order="asc" title="Oldest First">↑</button>
                            <button class="order-btn" data-order="desc" title="Newest First">↓</button>
                        </div>
                    </div>
                    
                    <input type="text" class="nav-search" placeholder="Search ordinances..." />
                    
                    <div class="view-controls">
                        <div class="control-label">View</div>
                        <div class="view-buttons">
                            <button class="view-btn" data-view="numerical">Numerical</button>
                            <button class="view-btn active" data-view="chronological">Chronological</button>
                            <button class="view-btn" data-view="topical">Topical</button>
                        </div>
                    </div>
                </div>
                
                <div class="nav-content">
                    <!-- Document list will be populated here -->
                </div>
                
                <div class="nav-stats">
                    <span class="visible-count">0</span> of <span class="total-count">0</span> documents
                </div>
            </div>
        `;
        
        // Create RIGHT sidebar container separately
        const rightContainer = document.createElement('div');
        rightContainer.className = 'nav-relationships';
        rightContainer.innerHTML = `
            <div class="relationships-header">
                <h3>Document Relationships</h3>
            </div>
            <div class="relationships-content">
                <!-- Relationships will be shown here -->
            </div>
        `;
        
        // Insert both containers
        document.body.insertBefore(leftContainer, document.body.firstChild);
        document.body.appendChild(rightContainer);
        
        // Add styles
        this.addStyles();
        
        // Bind events
        this.bindEvents();
        
        // Initial render
        this.renderDocuments();
    }
    
    bindEvents() {
        // Context switcher dropdown
        const contextDropdown = document.querySelector('.context-dropdown');
        const contextMenu = document.querySelector('.context-menu');
        
        if (contextDropdown && contextMenu) {
            contextDropdown.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = contextMenu.style.display !== 'none';
                contextMenu.style.display = isOpen ? 'none' : 'block';
                contextDropdown.classList.toggle('open', !isOpen);
            });
            
            // Context menu items
            document.querySelectorAll('.context-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const type = item.dataset.type;
                    
                    if (type === 'home') {
                        // Navigate to home/landing page
                        window.location.pathname = '/';
                        return;
                    }
                    
                    // Update active state
                    document.querySelectorAll('.context-item').forEach(i => {
                        i.classList.remove('active');
                    });
                    item.classList.add('active');
                    
                    // Update dropdown label
                    const icon = item.dataset.icon || '📋';
                    const label = item.textContent.trim().split('\n')[1].trim();
                    contextDropdown.querySelector('.context-icon').textContent = icon;
                    contextDropdown.querySelector('.context-label').textContent = label;
                    
                    // Hide menu
                    contextMenu.style.display = 'none';
                    contextDropdown.classList.remove('open');
                    
                    // Switch document type
                    this.switchDocumentType(type);
                });
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                contextMenu.style.display = 'none';
                contextDropdown.classList.remove('open');
            });
        }
        
        // View buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.dataset.view);
            });
        });
        
        // Order buttons
        document.querySelectorAll('.order-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchOrder(e.target.dataset.order);
            });
        });
        
        // Search
        const searchInput = document.querySelector('.nav-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterDocuments(e.target.value);
            });
        }
    }
    
    switchDocumentType(type) {
        this.currentDocType = type;
        
        // Update search placeholder
        const search = document.querySelector('.nav-search');
        const typeLabels = {
            'ordinances': 'ordinances',
            'resolutions': 'resolutions',
            'interpretations': 'interpretations',
            'transcripts': 'meeting records'
        };
        
        search.placeholder = `Search ${typeLabels[type] || type}...`;
        
        // Update view controls visibility
        const viewButtons = document.querySelector('.view-buttons');
        if (type === 'interpretations') {
            viewButtons.innerHTML = `
                <button class="view-btn active" data-view="bydate">By Date</button>
                <button class="view-btn" data-view="bysection">By Code Section</button>
            `;
        } else if (type === 'transcripts') {
            viewButtons.innerHTML = `
                <button class="view-btn active" data-view="bydate">By Date</button>
                <button class="view-btn" data-view="bymeeting">By Meeting</button>
            `;
        } else {
            viewButtons.innerHTML = `
                <button class="view-btn" data-view="numerical">Numerical</button>
                <button class="view-btn active" data-view="chronological">Chronological</button>
                <button class="view-btn" data-view="topical">Topical</button>
            `;
        }
        
        // Re-bind view button events
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.dataset.view);
            });
        });
        
        // Re-render
        this.renderDocuments();
    }
    
    switchView(view) {
        this.currentView = view;
        
        // Update active state
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
        
        this.renderDocuments();
    }
    
    switchOrder(order) {
        this.currentOrder = order;
        
        // Update active state
        document.querySelectorAll('.order-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.order === order);
        });
        
        this.renderDocuments();
    }
    
    filterDocuments(searchTerm) {
        const term = searchTerm.toLowerCase();
        const items = document.querySelectorAll('.doc-item');
        let visibleCount = 0;
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = !term || text.includes(term);
            item.style.display = matches ? '' : 'none';
            if (matches) visibleCount++;
        });
        
        // Update count
        document.querySelector('.visible-count').textContent = visibleCount;
    }
    
    renderDocuments() {
        const container = document.querySelector('.nav-content');
        if (!container) return;
        
        // Filter documents by type
        const docs = Object.values(this.documents).filter(doc => {
            if (this.currentDocType === 'ordinances') return doc.type === 'ordinance';
            if (this.currentDocType === 'resolutions') return doc.type === 'resolution';
            if (this.currentDocType === 'interpretations') return doc.type === 'interpretation';
            return false;
        });
        
        // Sort documents
        docs.sort((a, b) => {
            const yearA = parseInt(a.year) || 0;
            const yearB = parseInt(b.year) || 0;
            return this.currentOrder === 'asc' ? yearA - yearB : yearB - yearA;
        });
        
        // Group documents based on view
        const grouped = this.groupDocuments(docs);
        
        // Render grouped documents
        container.innerHTML = '';
        
        if (this.currentView === 'chronological' || this.currentView === 'bydate') {
            this.renderChronologicalView(container, grouped);
        } else if (this.currentView === 'numerical') {
            this.renderNumericalView(container, grouped);
        } else if (this.currentView === 'bysection') {
            this.renderBySectionView(container, grouped);
        } else {
            // Default flat list
            this.renderFlatList(container, docs);
        }
        
        // Update counts
        document.querySelector('.total-count').textContent = docs.length;
        document.querySelector('.visible-count').textContent = docs.length;
    }
    
    groupDocuments(docs) {
        const groups = {};
        
        if (this.currentView === 'chronological' || this.currentView === 'bydate') {
            // Group by decade
            docs.forEach(doc => {
                const year = parseInt(doc.year) || 2000;
                const decade = Math.floor(year / 10) * 10;
                const key = `${decade}s`;
                if (!groups[key]) groups[key] = [];
                groups[key].push(doc);
            });
        } else if (this.currentView === 'numerical') {
            // Group by number range
            docs.forEach(doc => {
                const match = doc.id.match(/^(\d+)/);
                const num = match ? parseInt(match[1]) : 0;
                let key = '#1-50';
                if (num > 100) key = '#101+';
                else if (num > 50) key = '#51-100';
                
                if (!groups[key]) groups[key] = [];
                groups[key].push(doc);
            });
        } else if (this.currentView === 'bysection') {
            // Group by code section
            docs.forEach(doc => {
                const section = doc.section || 'Other';
                if (!groups[section]) groups[section] = [];
                groups[section].push(doc);
            });
        }
        
        return groups;
    }
    
    renderChronologicalView(container, groups) {
        const decades = Object.keys(groups).sort((a, b) => {
            return this.currentOrder === 'asc' ? a.localeCompare(b) : b.localeCompare(a);
        });
        
        decades.forEach(decade => {
            const group = this.createGroup(decade, groups[decade]);
            container.appendChild(group);
        });
    }
    
    renderNumericalView(container, groups) {
        const ranges = ['#1-50', '#51-100', '#101+'];
        ranges.forEach(range => {
            if (groups[range] && groups[range].length > 0) {
                const group = this.createGroup(range, groups[range]);
                container.appendChild(group);
            }
        });
    }
    
    renderBySectionView(container, groups) {
        const sections = Object.keys(groups).sort();
        sections.forEach(section => {
            const group = this.createGroup(section, groups[section]);
            container.appendChild(group);
        });
    }
    
    renderFlatList(container, docs) {
        docs.forEach(doc => {
            const item = this.createDocumentItem(doc);
            container.appendChild(item);
        });
    }
    
    createGroup(label, docs) {
        const group = document.createElement('div');
        group.className = 'doc-group';
        
        const header = document.createElement('div');
        header.className = 'group-header';
        header.innerHTML = `
            <span class="group-arrow">▼</span>
            <span class="group-label">${label}</span>
            <span class="group-count">${docs.length}</span>
        `;
        
        const list = document.createElement('div');
        list.className = 'group-list';
        
        docs.forEach(doc => {
            const item = this.createDocumentItem(doc);
            list.appendChild(item);
        });
        
        group.appendChild(header);
        group.appendChild(list);
        
        // Toggle functionality
        header.addEventListener('click', () => {
            const isCollapsed = group.classList.contains('collapsed');
            group.classList.toggle('collapsed');
            header.querySelector('.group-arrow').textContent = isCollapsed ? '▼' : '▶';
        });
        
        return group;
    }
    
    createDocumentItem(doc) {
        const item = document.createElement('div');
        item.className = 'doc-item';
        item.dataset.docId = doc.id;
        
        // Check if this document has relationships
        const hasInterpretations = this.relationships[doc.id]?.interpretations?.length > 0;
        if (hasInterpretations) {
            item.classList.add('has-interpretations');
        }
        
        // Format display based on document type
        let display = '';
        if (doc.type === 'ordinance') {
            const match = doc.id.match(/^(\d+[\w-]*)-(.+)/);
            if (match) {
                const [, num, topic] = match;
                display = `<span class="doc-number">#${num}</span> - ${this.truncateTitle(topic)} <span class="doc-year">[${doc.year}]</span>`;
            } else {
                display = `${doc.id} <span class="doc-year">[${doc.year}]</span>`;
            }
        } else if (doc.type === 'resolution') {
            const match = doc.id.match(/^(\d+)-(.+)/);
            if (match) {
                const [, num, topic] = match;
                display = `<span class="doc-number">#${num}</span> - ${this.truncateTitle(topic)} <span class="doc-year">[${doc.year}]</span>`;
            } else {
                display = `${doc.id} <span class="doc-year">[${doc.year}]</span>`;
            }
        } else {
            // Interpretation
            display = `${doc.date || doc.year} - ${doc.section || doc.title}`;
        }
        
        item.innerHTML = display;
        
        // Click handler
        item.addEventListener('click', () => {
            this.navigateToDocument(doc);
        });
        
        return item;
    }
    
    truncateTitle(title) {
        // Clean up and truncate long titles
        let clean = title.replace(/-/g, ' ')
                        .replace(/\b(\w)/g, (match) => match.toUpperCase());
        
        if (clean.length > 30) {
            clean = clean.substring(0, 27) + '...';
        }
        
        return clean;
    }
    
    navigateToDocument(doc) {
        // Construct the URL path based on document type and file
        let path = '';
        if (doc.type === 'ordinance') {
            path = `/ordinances/${doc.file.replace('.md', '.html').replace('#', '')}`;
        } else if (doc.type === 'resolution') {
            path = `/resolutions/${doc.file.replace('.md', '.html').replace('#', '')}`;
        } else if (doc.type === 'interpretation') {
            path = `/interpretations/${doc.file.replace('.md', '.html')}`;
        }
        
        // Navigate directly without animations
        if (window.location.pathname !== path) {
            window.location.pathname = path;
        }
        
        // Update active state
        this.setActiveDocument(doc.id);
        
        // Show relationships
        this.showRelationships(doc.id);
    }
    
    setActiveDocument(docId) {
        this.currentDocId = docId;
        
        // Update active state in UI
        document.querySelectorAll('.doc-item').forEach(item => {
            item.classList.toggle('active', item.dataset.docId === docId);
        });
    }
    
    showRelationships(docId) {
        const container = document.querySelector('.relationships-content');
        if (!container) return;
        
        const rels = this.relationships[docId];
        if (!rels || Object.keys(rels).length === 0) {
            container.innerHTML = '<p class="no-relationships">No related documents</p>';
            return;
        }
        
        let html = '';
        
        // Interpretations
        if (rels.interpretations && rels.interpretations.length > 0) {
            html += `
                <div class="rel-section">
                    <h4 class="rel-title">📝 Interpretations</h4>
                    <div class="rel-list">
            `;
            rels.interpretations.forEach(id => {
                const doc = this.documents[id];
                if (doc) {
                    html += `<div class="rel-item" data-doc-id="${id}">${doc.date || doc.year} - ${doc.section || doc.title}</div>`;
                }
            });
            html += '</div></div>';
        }
        
        // Related Ordinances
        if (rels.references && rels.references.length > 0) {
            html += `
                <div class="rel-section">
                    <h4 class="rel-title">📋 Related Ordinances</h4>
                    <div class="rel-list">
            `;
            rels.references.forEach(id => {
                const doc = this.documents[id];
                if (doc) {
                    html += `<div class="rel-item" data-doc-id="${id}">${doc.id}</div>`;
                }
            });
            html += '</div></div>';
        }
        
        // Amendments
        if (rels.amendments && rels.amendments.length > 0) {
            html += `
                <div class="rel-section">
                    <h4 class="rel-title">🔄 Amendments</h4>
                    <div class="rel-list">
            `;
            rels.amendments.forEach(id => {
                const doc = this.documents[id];
                if (doc) {
                    html += `<div class="rel-item" data-doc-id="${id}">${doc.year} - ${doc.id}</div>`;
                }
            });
            html += '</div></div>';
        }
        
        container.innerHTML = html;
        
        // Add click handlers to relationship items
        container.querySelectorAll('.rel-item').forEach(item => {
            item.addEventListener('click', () => {
                const targetId = item.dataset.docId;
                const targetDoc = this.documents[targetId];
                if (targetDoc) {
                    this.navigateToDocument(targetDoc);
                }
            });
        });
    }
    
    detectCurrentDocument() {
        // Detect which document we're currently viewing based on URL
        const path = window.location.pathname;
        
        // Find matching document
        for (const [id, doc] of Object.entries(this.documents)) {
            const docPath = doc.file.replace('.md', '.html').replace('#', '');
            if (path.includes(docPath)) {
                this.setActiveDocument(id);
                this.showRelationships(id);
                break;
            }
        }
    }
    
    setupNavigationHandlers() {
        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.detectCurrentDocument();
            // Reapply our styles after navigation
            setTimeout(() => this.reapplyStyles(), 50);
        });
        
        // Monitor for DOM changes that might restore animations
        const observer = new MutationObserver((mutations) => {
            let needsReapply = false;
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    // Check if page-wrapper got reset
                    const pageWrapper = document.querySelector('.page-wrapper');
                    if (pageWrapper) {
                        const styles = window.getComputedStyle(pageWrapper);
                        if (styles.marginLeft !== '300px') {
                            needsReapply = true;
                        }
                    }
                }
            });
            
            if (needsReapply) {
                this.reapplyStyles();
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class']
        });
    }
    
    reapplyStyles() {
        // Remove and re-add our override styles
        const existingStyle = document.getElementById('standalone-nav-override');
        if (existingStyle) {
            existingStyle.remove();
        }
        this.hideMdBookSidebar();
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Container layout */
            .standalone-nav-container {
                position: fixed;
                top: 0;
                left: 0;
                bottom: 0;
                width: 300px;
                z-index: 100;
                display: flex;
                flex-direction: column;
            }
            
            /* Right relationships panel */
            .nav-relationships {
                position: fixed;
                top: 0;
                right: 0;
                bottom: 0;
                width: 280px;
                background: white;
                border-left: 1px solid #dee2e6;
                display: flex;
                flex-direction: column;
                z-index: 100;
            }
            
            /* Page wrapper already styled in hideMdBookSidebar */
            
            /* Make sure main content is visible and stable */
            .page {
                position: relative;
                z-index: 1;
            }
            
            main {
                position: relative;
                z-index: 1;
            }
            
            /* Override mdBook's default transitions */
            #content {
                transition: none !important;
            }
            
            /* Prevent the sliding effect on navigation */
            .chapter {
                animation: none !important;
                transition: none !important;
            }
            
            /* Navigation sidebar */
            .nav-sidebar {
                background: white;
                border-right: 1px solid #dee2e6;
                display: flex;
                flex-direction: column;
                height: 100vh;
                overflow: hidden;
                pointer-events: auto;
                position: relative;
            }
            
            /* Header section */
            .nav-header {
                padding: 14px;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-bottom: 2px solid #dee2e6;
            }
            
            /* Context Switcher Dropdown */
            .context-switcher {
                margin-bottom: 12px;
                position: relative;
            }
            
            .context-dropdown {
                width: 100%;
                padding: 10px 12px;
                background: white;
                border: 1.5px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                color: #1a1a1a;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: space-between;
                transition: all 0.2s;
                box-shadow: 0 1px 2px rgba(0,0,0,0.04);
            }
            
            .context-dropdown:hover {
                background: #f8f9fa;
                border-color: #adb5bd;
            }
            
            .context-dropdown.open {
                border-color: #0969da;
                box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.1);
            }
            
            .context-icon {
                margin-right: 8px;
                font-size: 16px;
            }
            
            .context-label {
                flex: 1;
                text-align: left;
            }
            
            .dropdown-arrow {
                font-size: 10px;
                color: #6b7280;
                transition: transform 0.2s;
            }
            
            .context-dropdown.open .dropdown-arrow {
                transform: rotate(180deg);
            }
            
            .context-menu {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                margin-top: 4px;
                max-height: 400px;
                overflow-y: auto;
            }
            
            .context-item {
                padding: 10px 12px;
                display: flex;
                align-items: center;
                cursor: pointer;
                transition: background 0.2s;
                font-size: 13px;
            }
            
            .context-item:hover {
                background: #f8f9fa;
            }
            
            .context-item.active {
                background: #e7f3ff;
                color: #0969da;
                font-weight: 600;
            }
            
            .context-item .context-icon {
                margin-right: 10px;
                font-size: 16px;
            }
            
            .context-count {
                margin-left: auto;
                background: #e5e7eb;
                color: #6b7280;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: normal;
            }
            
            .context-item.active .context-count {
                background: #dbeafe;
                color: #0969da;
            }
            
            .context-divider {
                margin: 4px 0;
                border: none;
                border-top: 1px solid #e5e7eb;
            }
            
            /* Title row */
            .nav-title-row {
                display: flex;
                justify-content: flex-end;
                align-items: center;
                margin-bottom: 12px;
            }
            
            .order-controls {
                display: flex;
                gap: 2px;
            }
            
            .order-btn {
                width: 22px;
                height: 22px;
                padding: 0;
                border: 1.5px solid #dee2e6;
                background: white;
                border-radius: 3px;
                cursor: pointer;
                font-size: 12px;
                line-height: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
                color: #495057;
                font-weight: 600;
            }
            
            .order-btn:hover {
                background: #f8f9fa;
                border-color: #adb5bd;
            }
            
            .order-btn.active {
                background: #0969da;
                color: white;
                border-color: #0969da;
            }
            
            /* Search */
            .nav-search {
                width: 100%;
                padding: 8px 12px;
                border: 1.5px solid #e9ecef;
                border-radius: 6px;
                font-size: 13px;
                margin-bottom: 12px;
                box-sizing: border-box;
                transition: all 0.2s;
                background: white;
                box-shadow: 0 1px 2px rgba(0,0,0,0.04);
            }
            
            .nav-search:focus {
                outline: none;
                border-color: #0969da;
                box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.1);
            }
            
            /* View controls */
            .view-controls {
                margin-bottom: 10px;
            }
            
            .control-label {
                font-size: 10px;
                color: #6b7280;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 6px;
            }
            
            .view-buttons {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 4px;
            }
            
            .view-btn {
                padding: 6px 8px;
                font-size: 11px;
                font-weight: 500;
                border: 1px solid #dee2e6;
                background: white;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s ease;
                text-align: center;
            }
            
            .view-btn:hover {
                background: #f8f9fa;
                border-color: #adb5bd;
            }
            
            .view-btn.active {
                background: #0969da;
                color: white;
                border-color: #0969da;
            }
            
            .view-btn.active:hover {
                background: #0550ae;
            }
            
            /* Stats - floating at bottom */
            .nav-stats {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                font-size: 10px;
                color: #6b7280;
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(8px);
                border-top: 1px solid #e5e7eb;
                text-align: center;
                z-index: 5;
            }
            
            .nav-stats .visible-count,
            .nav-stats .total-count {
                font-weight: 600;
                color: #1f2937;
            }
            
            /* Content area */
            .nav-content {
                flex: 1;
                overflow-y: auto;
                padding: 12px;
                padding-bottom: 40px; /* Space for floating stats */
                background: #fefefe;
            }
            
            /* Document groups */
            .doc-group {
                margin-bottom: 10px;
            }
            
            .group-header {
                display: flex;
                align-items: center;
                padding: 6px 8px;
                background: #f8f9fa;
                border-radius: 4px;
                cursor: pointer;
                user-select: none;
                margin-bottom: 5px;
            }
            
            .group-header:hover {
                background: #e9ecef;
            }
            
            .doc-group.collapsed .group-list {
                display: none;
            }
            
            .group-arrow {
                margin-right: 8px;
                font-size: 10px;
                color: #666;
            }
            
            .group-label {
                flex: 1;
                font-size: 12px;
                font-weight: 600;
                color: #333;
            }
            
            .group-count {
                background: #dee2e6;
                color: #495057;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 10px;
            }
            
            .group-list {
                padding-left: 15px;
            }
            
            /* Document items */
            .doc-item {
                padding: 6px 8px;
                margin: 2px 0;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 12px;
                color: #333;
            }
            
            .doc-item:hover {
                background: #f0f7ff;
            }
            
            .doc-item.active {
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                font-weight: 500;
            }
            
            .doc-item.has-interpretations {
                border-left: 3px solid #fbbf24;
                padding-left: 5px;
            }
            
            .doc-number {
                font-weight: 600;
                color: #0969da;
            }
            
            .doc-year {
                color: #666;
                font-size: 11px;
            }
            
            
            .relationships-header {
                padding: 15px;
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            
            .relationships-header h3 {
                margin: 0;
                font-size: 14px;
                color: #333;
            }
            
            .relationships-content {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
            }
            
            .no-relationships {
                color: #666;
                font-style: italic;
                font-size: 12px;
            }
            
            .rel-section {
                margin-bottom: 20px;
            }
            
            .rel-title {
                font-size: 12px;
                font-weight: 600;
                color: #333;
                margin: 0 0 8px 0;
                padding-bottom: 4px;
                border-bottom: 1px solid #e1e4e8;
            }
            
            .rel-list {
                font-size: 12px;
            }
            
            .rel-item {
                padding: 5px 8px;
                margin: 2px 0;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .rel-item:hover {
                background: #f0f7ff;
            }
            
            /* Mobile responsiveness */
            @media (max-width: 1200px) {
                .standalone-nav-container {
                    grid-template-columns: 280px 1fr;
                }
                
                .nav-relationships {
                    display: none;
                }
                
                .page-wrapper {
                    margin-right: 0 !important;
                }
            }
            
            @media (max-width: 768px) {
                .standalone-nav-container {
                    grid-template-columns: 1fr;
                }
                
                .nav-sidebar {
                    position: fixed;
                    left: -280px;
                    width: 280px;
                    transition: left 0.3s;
                    z-index: 200;
                }
                
                .nav-sidebar.open {
                    left: 0;
                }
                
                .page-wrapper {
                    margin-left: 0 !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize after everything loads
function initNavigation() {
    // Wait for mdBook to fully initialize
    setTimeout(() => {
        new StandaloneNavigation();
    }, 100);
}

// Try multiple initialization points
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
} else if (document.readyState === 'interactive') {
    // DOM ready but resources still loading
    setTimeout(initNavigation, 50);
} else {
    // Everything loaded
    initNavigation();
}

// Also listen for page navigation events
window.addEventListener('load', () => {
    // Re-apply our styles after any page navigation
    setTimeout(() => {
        const existingStyle = document.getElementById('standalone-nav-override');
        if (!existingStyle) {
            // Styles got removed, need to reinitialize
            initNavigation();
        }
    }, 50);
});