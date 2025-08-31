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
        this.airtableMetadata = {};
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
        // Check if we're on the home page
        const isHomePage = window.location.pathname === '/' || 
                          window.location.pathname.endsWith('/index.html') ||
                          window.location.pathname.endsWith('/introduction.html');
        
        // CSS in custom.css now handles the immediate hiding
        // This just adds any additional runtime overrides if needed
        const style = document.createElement('style');
        style.id = 'standalone-nav-override';
        
        // Different styles for home page vs other pages
        if (isHomePage) {
            style.textContent = `
                /* Hide all sidebars and menu controls on home page */
                #sidebar, .sidebar,
                #standalone-navigation, .standalone-nav-container,
                #relationships-panel, .relationships-panel,
                #menu-bar .left-buttons,
                #sidebar-toggle,
                .menu-bar .left-buttons,
                .sidebar-toggle {
                    display: none !important;
                    visibility: hidden !important;
                }
                
                /* Center content on home page */
                .page-wrapper {
                    margin-left: auto !important;
                    margin-right: auto !important;
                    max-width: 900px !important;
                    padding: 0 20px !important;
                }
                
                /* Ensure content is visible */
                #content, .content, .chapter, main, .page {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                }
            `;
        } else {
            style.textContent = `
            /* Runtime reinforcement of CSS rules */
            #sidebar, .sidebar {
                display: none !important;
                visibility: hidden !important;
            }
            
            /* Ensure content is visible */
            #content,
            .content,
            .chapter,
            main,
            .page {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            /* Prevent horizontal scrolling */
            body, html {
                overflow-x: hidden !important;
            }
        `;
        }
        
        document.head.appendChild(style);
    }
    
    async loadRelationships() {
        try {
            // Load the main relationships data
            const response = await fetch('/relationships.json');
            const data = await response.json();
            this.documents = data.documents || {};
            this.relationships = data.relationships || {};
            
            // Load Airtable metadata for badges and special states
            try {
                const airtableResponse = await fetch('/airtable-metadata.json');
                const airtableData = await airtableResponse.json();
                // Index by filename without extension - the documents are stored under a 'documents' key
                this.airtableMetadata = {};
                const documents = airtableData.documents || airtableData;
                Object.entries(documents).forEach(([key, doc]) => {
                    // The key itself is already the filename without extension
                    this.airtableMetadata[key] = doc;
                });
                console.log(`StandaloneNavigation: Loaded Airtable metadata for ${Object.keys(this.airtableMetadata).length} documents`);
            } catch (error) {
                console.log('StandaloneNavigation: No airtable metadata found');
                this.airtableMetadata = {};
            }
            
            // Load Airtable metadata for meetings to filter what should be shown
            try {
                const meetingsResponse = await fetch('/meetings-metadata.json');
                const meetingsData = await meetingsResponse.json();
                this.meetingsMetadata = meetingsData.meetings || {};
                
                // Filter out meeting documents that aren't in Airtable
                this.filterMeetingDocuments();
            } catch (error) {
                console.log('StandaloneNavigation: No meetings metadata found, showing all meeting documents');
                this.meetingsMetadata = {};
            }
            
            console.log(`StandaloneNavigation: Loaded ${Object.keys(this.documents).length} documents`);
        } catch (error) {
            console.error('StandaloneNavigation: Failed to load relationships.json:', error);
            // Fallback: parse from current page structure if needed
            this.parseDocumentsFromDOM();
        }
    }
    
    filterMeetingDocuments() {
        // Only show meeting documents that are in Airtable metadata
        const filteredDocs = {};
        
        for (const [key, doc] of Object.entries(this.documents)) {
            // Keep non-meeting documents
            if (!['transcript', 'agenda', 'minutes', 'meeting'].includes(doc.type)) {
                filteredDocs[key] = doc;
                continue;
            }
            
            // For meeting documents, check if they're in Airtable
            // The Airtable key format is like "2018-05-14-agenda"
            const dateMatch = doc.file?.match(/(\d{4}-\d{2}-\d{2})/);
            if (dateMatch) {
                const date = dateMatch[1];
                const airtableKey = `${date}-${doc.type}`;
                
                // Check if this document exists in Airtable metadata
                if (this.meetingsMetadata[airtableKey]) {
                    filteredDocs[key] = doc;
                    console.log(`StandaloneNavigation: Including ${doc.type} from ${date} (found in Airtable)`);
                } else {
                    console.log(`StandaloneNavigation: Excluding ${doc.type} from ${date} (not in Airtable)`);
                }
            }
        }
        
        this.documents = filteredDocs;
    }
    
    parseDocumentsFromDOM() {
        // Fallback method to extract document info from page if relationships.json fails
        console.log('StandaloneNavigation: Parsing documents from DOM as fallback...');
        
        // This would parse the SUMMARY.md structure if needed
        // For now, we'll rely on relationships.json being present
    }
    
    createNavigationUI() {
        // Check if we're on the home page
        const isHomePage = window.location.pathname === '/' || 
                          window.location.pathname.endsWith('/index.html') ||
                          window.location.pathname.endsWith('/introduction.html');
        
        // Don't create sidebars on home page
        if (isHomePage) {
            console.log('StandaloneNavigation: On home page, skipping sidebar creation');
            return;
        }
        
        // Calculate counts for each document type
        const counts = {
            ordinances: 0,
            resolutions: 0,
            interpretations: 0,
            transcripts: 0,
            other: 0
        };
        
        Object.values(this.documents).forEach(doc => {
            if (doc.type === 'ordinance') counts.ordinances++;
            else if (doc.type === 'resolution') counts.resolutions++;
            else if (doc.type === 'interpretation') counts.interpretations++;
            else if (doc.type === 'transcript' || doc.type === 'meeting' || doc.type === 'agenda' || doc.type === 'minutes') counts.transcripts++;
            else if (doc.type === 'other' || doc.type === 'charter') counts.other++;
        });
        
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
                                <span class="context-count">${counts.ordinances}</span>
                            </div>
                            <div class="context-item" data-type="resolutions" data-icon="📄">
                                <span class="context-icon">📄</span>
                                Resolutions
                                <span class="context-count">${counts.resolutions}</span>
                            </div>
                            <div class="context-item" data-type="interpretations" data-icon="📝">
                                <span class="context-icon">📝</span>
                                Interpretations
                                <span class="context-count">${counts.interpretations}</span>
                            </div>
                            <div class="context-item" data-type="transcripts" data-icon="🎙️">
                                <span class="context-icon">🎙️</span>
                                Meeting Records
                                <span class="context-count">${counts.transcripts}</span>
                            </div>
                            <div class="context-item" data-type="other" data-icon="📚">
                                <span class="context-icon">📚</span>
                                Other Documents
                                <span class="context-count">${counts.other}</span>
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
            const contextItems = document.querySelectorAll('.context-item');
            
            contextItems.forEach(item => {
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
                    // Get the text based on type
                    let label = '';
                    switch(type) {
                        case 'ordinances': label = 'Ordinances'; break;
                        case 'resolutions': label = 'Resolutions'; break;
                        case 'interpretations': label = 'Interpretations'; break;
                        case 'transcripts': label = 'Meeting Records'; break;
                        case 'other': label = 'Other Documents'; break;
                        default: label = type;
                    }
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
        console.log('StandaloneNavigation: Switching to document type:', type);
        
        // Update search placeholder
        const search = document.querySelector('.nav-search');
        if (!search) {
            console.error('StandaloneNavigation: Search input not found');
            return;
        }
        
        const typeLabels = {
            'ordinances': 'ordinances',
            'resolutions': 'resolutions',
            'interpretations': 'interpretations',
            'transcripts': 'meeting records',
            'other': 'other documents'
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
        } else if (type === 'other') {
            viewButtons.innerHTML = `
                <button class="view-btn active" data-view="chronological">Chronological</button>
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
        
        // Navigate to the first document in this category
        const docs = Object.entries(this.documents)
            .filter(([key, doc]) => {
                if (type === 'ordinances') return doc.type === 'ordinance';
                if (type === 'resolutions') return doc.type === 'resolution';
                if (type === 'interpretations') return doc.type === 'interpretation';
                if (type === 'transcripts') return doc.type === 'transcript' || doc.type === 'meeting' || doc.type === 'agenda' || doc.type === 'minutes';
                if (type === 'other') return doc.type === 'other' || doc.type === 'charter';
                return false;
            })
            .map(([key, doc]) => ({ ...doc, docKey: key }));
        
        // If we have documents in this category, navigate to the first one
        if (docs.length > 0) {
            // Sort by date (newest first) for meeting documents, or by year for others
            if (type === 'transcripts') {
                docs.sort((a, b) => {
                    const dateA = new Date(a.date || '1900-01-01');
                    const dateB = new Date(b.date || '1900-01-01');
                    return dateB - dateA;
                });
            } else {
                docs.sort((a, b) => {
                    const yearA = parseInt(a.year) || 0;
                    const yearB = parseInt(b.year) || 0;
                    return yearB - yearA;
                });
            }
            
            // Navigate to the first document
            this.navigateToDocument(docs[0]);
        } else {
            console.log(`StandaloneNavigation: No documents found for type ${type}`);
        }
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
        if (!container) {
            console.error('StandaloneNavigation: nav-content container not found');
            return;
        }
        
        
        // Filter documents by type - preserve the full key as docKey
        const docs = Object.entries(this.documents)
            .filter(([key, doc]) => {
                if (this.currentDocType === 'ordinances') return doc.type === 'ordinance';
                if (this.currentDocType === 'resolutions') return doc.type === 'resolution';
                if (this.currentDocType === 'interpretations') return doc.type === 'interpretation';
                if (this.currentDocType === 'transcripts') return doc.type === 'transcript' || doc.type === 'meeting' || doc.type === 'agenda' || doc.type === 'minutes';
                if (this.currentDocType === 'other') return doc.type === 'other' || doc.type === 'charter';
                return false;
            })
            .map(([key, doc]) => ({ ...doc, docKey: key }));
        
        console.log(`StandaloneNavigation: Rendering ${docs.length} ${this.currentDocType}`);
        
        // Minimum threshold for grouping
        const MIN_DOCS_FOR_GROUPING = 10;
        
        container.innerHTML = '';
        // If too few documents, just render a sorted flat list
        if (docs.length < MIN_DOCS_FOR_GROUPING) {
            // Sort documents based on current view
            this.sortDocumentsForView(docs);
            this.renderFlatList(container, docs);
        } else {
            // Sort documents
            docs.sort((a, b) => {
                const yearA = parseInt(a.year) || 0;
                const yearB = parseInt(b.year) || 0;
                return this.currentOrder === 'asc' ? yearA - yearB : yearB - yearA;
            });
            
            // Group documents based on view
            const grouped = this.groupDocuments(docs);
            
            if (this.currentView === 'chronological' || this.currentView === 'bydate') {
                this.renderChronologicalView(container, grouped);
            } else if (this.currentView === 'numerical') {
                this.renderNumericalView(container, grouped);
            } else if (this.currentView === 'bysection') {
                this.renderBySectionView(container, grouped);
            } else {
                // Default flat list
                console.log('StandaloneNavigation: Using flat list view');
                this.renderFlatList(container, docs);
            }
        }
        
        // Update counts
        const totalCountEl = document.querySelector('.total-count');
        const visibleCountEl = document.querySelector('.visible-count');
        if (totalCountEl) totalCountEl.textContent = docs.length;
        if (visibleCountEl) visibleCountEl.textContent = docs.length;
    }
    
    sortDocumentsForView(docs) {
        if (this.currentView === 'chronological' || this.currentView === 'bydate') {
            // Sort by year
            docs.sort((a, b) => {
                const yearA = parseInt(a.year) || 0;
                const yearB = parseInt(b.year) || 0;
                return this.currentOrder === 'asc' ? yearA - yearB : yearB - yearA;
            });
        } else if (this.currentView === 'numerical') {
            // Sort by number
            docs.sort((a, b) => {
                const matchA = a.id ? a.id.match(/^(\d+)/) : null;
                const matchB = b.id ? b.id.match(/^(\d+)/) : null;
                const numA = matchA ? parseInt(matchA[1]) : 0;
                const numB = matchB ? parseInt(matchB[1]) : 0;
                return this.currentOrder === 'asc' ? numA - numB : numB - numA;
            });
        } else if (this.currentView === 'bysection') {
            // Sort by section then by ID
            docs.sort((a, b) => {
                const sectionCompare = (a.section || 'Other').localeCompare(b.section || 'Other');
                if (sectionCompare !== 0) return sectionCompare;
                return (a.id || '').localeCompare(b.id || '');
            });
        }
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
                const match = doc.id ? doc.id.match(/^(\d+)/) : null;
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
        // Use docKey if available (full key like 'ordinance-52-Flood'), otherwise fall back to doc.id
        const fullId = doc.docKey || doc.id;
        item.dataset.docId = fullId;
        
        // Check if this is the current document
        if (fullId === this.currentDocId) {
            item.classList.add('active');
        }
        
        // Check if this document has relationships  
        const hasInterpretations = this.relationships[fullId]?.interpretations?.length > 0;
        if (hasInterpretations) {
            item.classList.add('has-interpretations');
        }
        
        // Get Airtable metadata for badges and display formatting
        const fileKey = doc.file ? doc.file.replace('.md', '') : null;
        const airtableData = fileKey ? this.airtableMetadata[fileKey] : null;
        
        // Add special state badge if available
        let specialStateBadge = '';
        if (airtableData?.special_state) {
            // Handle special_state being either a string or array
            let stateValue = airtableData.special_state;
            if (Array.isArray(stateValue)) {
                stateValue = stateValue[0]; // Take first value if array
            }
            if (stateValue) {
                const stateClass = stateValue.toLowerCase().replace(/\s+/g, '-');
                specialStateBadge = `<span class="special-state state-${stateClass}">${stateValue}</span>`;
            }
        }
        
        // Format display - use Airtable data if available for better formatting
        let display = '';
        if (airtableData && airtableData.doc_number) {
            // Use Airtable metadata for clean display
            const docNumber = airtableData.doc_number;
            const shortTitle = airtableData.short_title || '';
            const year = airtableData.year || doc.year;
            
            if (doc.type === 'ordinance' || doc.type === 'resolution') {
                // Format with floating year on the right
                display = `<div class="doc-item-main">
                    <span class="doc-number">#${docNumber}</span>
                    ${shortTitle ? ` - <span class="doc-title">${shortTitle}</span>` : ''}
                    ${specialStateBadge}
                    <span class="doc-year-tag">${year}</span>
                </div>`;
            } else {
                // Other document types
                display = `${airtableData.display_name || doc.id} ${specialStateBadge}`;
            }
        } else {
            // Fallback to auto-generated display when no Airtable data
            if (doc.type === 'ordinance') {
                const match = doc.id.match(/^(\d+[\w-]*)-(.+)/);
                if (match) {
                    const [, num, topic] = match;
                    display = `<div class="doc-item-main">
                        <span class="doc-number">#${num}</span> - 
                        <span class="doc-title">${this.truncateTitle(topic)}</span>
                        ${specialStateBadge}
                        <span class="doc-year-tag">${doc.year}</span>
                    </div>`;
                } else {
                    display = `${doc.id} ${specialStateBadge} <span class="doc-year">[${doc.year}]</span>`;
                }
            } else if (doc.type === 'resolution') {
                const match = doc.id.match(/^(\d+)-(.+)/);
                if (match) {
                    const [, num, topic] = match;
                    display = `<div class="doc-item-main">
                        <span class="doc-number">#${num}</span> - 
                        <span class="doc-title">${this.truncateTitle(topic)}</span>
                        ${specialStateBadge}
                        <span class="doc-year-tag">${doc.year}</span>
                    </div>`;
                } else {
                    display = `${doc.id} ${specialStateBadge} <span class="doc-year">[${doc.year}]</span>`;
                }
            } else if (doc.type === 'transcript' || doc.type === 'agenda' || doc.type === 'minutes') {
                // Meeting documents - format as date and type
                const typeLabel = doc.type.charAt(0).toUpperCase() + doc.type.slice(1);
                if (doc.date) {
                    // Try to format the date nicely
                    const dateObj = new Date(doc.date + 'T00:00:00');
                    const formatted = dateObj.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
                    display = `${formatted} - ${typeLabel}`;
                } else {
                    display = `${doc.title || doc.file} - ${typeLabel}`;
                }
            } else {
                // Interpretation and other documents
                display = `${doc.date || doc.year} - ${doc.section || doc.title}`;
            }
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
        } else if (doc.type === 'transcript') {
            path = `/transcripts/${doc.file.replace('.md', '.html')}`;
        } else if (doc.type === 'agenda') {
            path = `/agendas/${doc.file.replace('.md', '.html')}`;
        } else if (doc.type === 'minutes') {
            path = `/minutes/${doc.file.replace('.md', '.html')}`;
        } else if (doc.type === 'other' || doc.type === 'charter') {
            path = `/other/${doc.file.replace('.md', '.html')}`;
        }
        
        // Navigate directly without animations
        if (window.location.pathname !== path) {
            window.location.pathname = path;
        }
        
        // Update active state - use full key if available
        const fullId = doc.docKey || doc.id;
        this.setActiveDocument(fullId);
        
        // Show relationships
        this.showRelationships(fullId);
    }
    
    setActiveDocument(docId) {
        this.currentDocId = docId;
        
        // Update active state in UI
        const items = document.querySelectorAll('.doc-item');
        
        items.forEach(item => {
            const itemId = item.dataset.docId;
            const isActive = itemId === docId;
            item.classList.toggle('active', isActive);
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
                // Determine document type and update context switcher
                let docType = 'ordinances';
                if (doc.type === 'resolution') docType = 'resolutions';
                else if (doc.type === 'interpretation') docType = 'interpretations';
                else if (doc.type === 'transcript' || doc.type === 'meeting' || doc.type === 'agenda' || doc.type === 'minutes') docType = 'transcripts';
                else if (doc.type === 'other' || doc.type === 'charter') docType = 'other';
                
                // Update current doc type if different
                if (this.currentDocType !== docType) {
                    this.currentDocType = docType;
                    
                    // Update dropdown to show correct type
                    const contextDropdown = document.querySelector('.context-dropdown');
                    if (contextDropdown) {
                        const contextIcon = contextDropdown.querySelector('.context-icon');
                        const contextLabel = contextDropdown.querySelector('.context-label');
                        
                        // Update icon and label
                        const icons = {
                            'ordinances': '📋',
                            'resolutions': '📜',
                            'interpretations': '💭',
                            'transcripts': '🎙️',
                            'other': '📚'
                        };
                        const labels = {
                            'ordinances': 'Ordinances',
                            'resolutions': 'Resolutions', 
                            'interpretations': 'Interpretations',
                            'transcripts': 'Meeting Records',
                            'other': 'Other Documents'
                        };
                        
                        if (contextIcon) contextIcon.textContent = icons[docType] || '📋';
                        if (contextLabel) contextLabel.textContent = labels[docType] || docType;
                    }
                    
                    // Update search placeholder to match document type
                    const search = document.querySelector('.nav-search');
                    if (search) {
                        const searchLabels = {
                            'ordinances': 'ordinances',
                            'resolutions': 'resolutions',
                            'interpretations': 'interpretations',
                            'transcripts': 'meeting records',
                            'other': 'other documents'
                        };
                        search.placeholder = `Search ${searchLabels[docType] || docType}...`;
                    }
                    
                    // Re-render the documents list for the correct type
                    this.renderDocuments();
                    
                    // Must set active AFTER re-rendering
                    setTimeout(() => {
                        this.setActiveDocument(id);
                    }, 10);
                } else {
                    // No re-render needed, just set active
                    this.setActiveDocument(id);
                }
                
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
            
            /* Special state badges */
            .special-state {
                display: inline-block;
                padding: 2px 6px;
                margin-left: 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
                vertical-align: middle;
            }
            
            .state-never-passed {
                background: #fee2e2;
                color: #991b1b;
                border: 1px solid #fca5a5;
            }
            
            .state-repealed {
                background: #fef3c7;
                color: #92400e;
                border: 1px solid #fcd34d;
            }
            
            .state-amended {
                background: #dbeafe;
                color: #1e40af;
                border: 1px solid #93c5fd;
            }
            
            .state-superseded {
                background: #f3e8ff;
                color: #6b21a8;
                border: 1px solid #d8b4fe;
            }
            
            .state-draft {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
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

// Global instance to prevent multiple initializations
let navigationInstance = null;

// Initialize after everything loads
function initNavigation() {
    if (navigationInstance) {
        return;
    }
    
    // Wait for mdBook to fully initialize
    setTimeout(() => {
        navigationInstance = new StandaloneNavigation();
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