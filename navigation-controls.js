/**
 * Enhanced Navigation Controls for City of Rivergrove mdBook
 * Adds search, filtering, and view controls to the sidebar
 * Also implements the right panel for document relationships
 */

class NavigationController {
    constructor() {
        this.documents = [];
        this.relationships = {};
        this.currentView = 'chronological';
        this.currentOrder = 'asc';
        this.searchTerm = '';
        this.currentDocument = null;
        this.leftPanelWidth = localStorage.getItem('leftPanelWidth') || '350';
        this.rightPanelWidth = localStorage.getItem('rightPanelWidth') || '300';
        
        this.init();
    }
    
    async init() {
        // Load relationships data
        try {
            // Try different paths for relationships.json
            let response = await fetch('/relationships.json');
            if (!response.ok) {
                response = await fetch('./relationships.json');
            }
            if (!response.ok) {
                response = await fetch('../relationships.json');
            }
            
            const data = await response.json();
            this.documents = Object.values(data.documents);
            this.relationships = data.relationships;
            this.topics = data.topics;
            console.log('NavigationController: Loaded', this.documents.length, 'documents');
        } catch (error) {
            console.warn('NavigationController: Could not load relationships.json:', error);
            // Fallback - try to parse from existing sidebar
            this.parseExistingSidebar();
        }
        
        // Initialize navigation enhancement
        this.enhanceSidebar();
        this.addRightPanel();
        this.bindEvents();
        this.detectCurrentDocument();
    }
    
    parseExistingSidebar() {
        // Parse documents from existing sidebar if relationships.json fails
        this.documents = [];
        
        // Wait a moment for mdBook to populate
        setTimeout(() => {
            const links = document.querySelectorAll('ol.chapter a[href*="ordinances/"]');
            links.forEach(link => {
                const text = link.textContent;
                const match = text.match(/#(\d+[\w-]*)\s*-\s*(.+?)\s*\((\d{4})\)/);
                if (match) {
                    this.documents.push({
                        id: match[1],
                        title: match[2],
                        year: match[3],
                        file: link.getAttribute('href'),
                        type: 'ordinance'
                    });
                }
            });
            console.log('NavigationController: Parsed', this.documents.length, 'documents from sidebar');
            
            // Update sidebar with parsed documents
            if (this.documents.length > 0) {
                this.updateSidebar();
            }
        }, 1000);
    }
    
    enhanceSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const sidebarScrollbox = document.querySelector('mdbook-sidebar-scrollbox');
        if (!sidebar || !sidebarScrollbox) {
            console.warn('NavigationController: Sidebar elements not found');
            return;
        }
        
        // Create enhanced header
        const header = document.createElement('div');
        header.className = 'nav-header-enhanced';
        header.innerHTML = `
            <div class="header-top">
                <div class="sidebar-title">Ordinances</div>
                <div class="order-icons">
                    <button class="order-icon active" data-order="asc" title="Oldest First">▲</button>
                    <button class="order-icon" data-order="desc" title="Newest First">▼</button>
                </div>
            </div>
            <div class="nav-search-container">
                <input type="text" 
                       class="nav-search" 
                       placeholder="Search ordinances..." 
                       id="navSearch">
            </div>
            <div class="nav-controls">
                <div class="control-label">View</div>
                <div class="view-buttons">
                    <button class="nav-btn" data-view="numerical" title="Organized by ordinance number ranges">Numerical</button>
                    <button class="nav-btn active" data-view="chronological" title="Grouped by decade with historical ordering">Chronological</button>
                    <button class="nav-btn" data-view="topical" title="Grouped by subject matter">Topical</button>
                </div>
            </div>
            <div class="nav-stats" id="navStats">
                Showing <span id="docCount">${this.documents.length}</span> of <span id="totalCount">${this.documents.length}</span> ordinances
            </div>
        `;
        
        // Insert header before the sidebar scrollbox
        sidebarScrollbox.parentNode.insertBefore(header, sidebarScrollbox);
    }
    
    addRightPanel() {
        const contentWrapper = document.querySelector('#content');
        if (!contentWrapper) return;
        
        // Create right panel
        const rightPanel = document.createElement('div');
        rightPanel.className = 'right-panel';
        rightPanel.id = 'rightPanel';
        rightPanel.innerHTML = `
            <div class="right-panel-header">
                <h3>Document Relationships</h3>
                <button class="panel-toggle" id="panelToggle">×</button>
            </div>
            <div class="right-panel-content" id="rightPanelContent">
                <div class="panel-placeholder">
                    Select a document to view its relationships
                </div>
            </div>
        `;
        
        // Add panel to page
        document.body.appendChild(rightPanel);
        
        // Adjust main content width
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
        }
        
        // View controls
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentView = e.target.dataset.view;
                this.updateSidebar();
            });
        });
        
        // Order controls
        document.querySelectorAll('.order-icon').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.order-icon').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentOrder = e.target.dataset.order;
                
                // Update tooltips based on view
                if (this.currentView === 'numerical') {
                    document.querySelector('[data-order="asc"]').title = 'Low to High';
                    document.querySelector('[data-order="desc"]').title = 'High to Low';
                } else {
                    document.querySelector('[data-order="asc"]').title = 'Oldest First';
                    document.querySelector('[data-order="desc"]').title = 'Newest First';
                }
                
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
        const filename = currentPath.split('/').pop();
        
        // Find matching document
        const doc = this.documents.find(d => d.file.replace('.md', '.html') === filename);
        if (doc) {
            this.currentDocument = doc;
            this.updateRightPanel();
        }
    }
    
    updateSidebar() {
        // Store original sidebar content if not already stored
        if (!this.originalSidebar) {
            const sidebar = document.querySelector('ol.chapter');
            if (sidebar) {
                this.originalSidebar = sidebar.cloneNode(true);
            }
        }
        
        // Find the container for the chapter list
        let sidebar = document.querySelector('ol.chapter');
        if (!sidebar) {
            // Try to find it within the scrollbox
            const scrollbox = document.querySelector('mdbook-sidebar-scrollbox');
            if (scrollbox) {
                sidebar = scrollbox.querySelector('ol.chapter');
            }
        }
        
        if (!sidebar) {
            console.warn('NavigationController: Cannot find sidebar content container');
            // Try again in a moment
            setTimeout(() => this.updateSidebar(), 500);
            return;
        }
        
        const filtered = this.filterDocuments();
        console.log('NavigationController: Updating sidebar with', filtered.length, 'documents');
        
        // Clear current content but preserve the structure
        const ordinanceItems = Array.from(sidebar.querySelectorAll('li.chapter-item')).filter(li => {
            const link = li.querySelector('a');
            return link && link.href.includes('ordinances/');
        });
        
        // Store references to preserve mdBook functionality
        this.mdBookItems = ordinanceItems;
        
        switch (this.currentView) {
            case 'numerical':
                this.renderNumericalView(sidebar, filtered);
                break;
            case 'chronological':
                this.renderChronologicalView(sidebar, filtered);
                break;
            case 'topical':
                this.renderTopicalView(sidebar, filtered);
                break;
        }
        
        // Update stats
        const docCount = document.getElementById('docCount');
        const totalCount = document.getElementById('totalCount');
        if (docCount) {
            docCount.textContent = filtered.length;
        }
        if (totalCount) {
            totalCount.textContent = this.documents.length;
        }
    }
    
    filterDocuments() {
        if (!this.searchTerm) return this.documents;
        
        return this.documents.filter(doc => {
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
        // Group by number ranges
        const ranges = [
            {title: '#1-50', min: 1, max: 50},
            {title: '#51-100', min: 51, max: 100},
            {title: '#101+', min: 101, max: 999999}
        ];
        
        const html = ranges.map(range => {
            const rangeDocs = documents.filter(doc => {
                const num = parseInt(doc.id) || 0;
                return num >= range.min && num <= range.max;
            });
            
            if (rangeDocs.length === 0) return '';
            
            // Sort by number within each range
            rangeDocs.sort((a, b) => {
                const numA = parseInt(a.id) || 0;
                const numB = parseInt(b.id) || 0;
                return this.currentOrder === 'asc' ? numA - numB : numB - numA;
            });
            
            return `
                <li class="chapter-item expanded">
                    <div class="group-header" onclick="this.classList.toggle('collapsed'); this.nextElementSibling.classList.toggle('collapsed')">
                        <span class="arrow">▼</span>
                        <span>${range.title}</span>
                        <span class="count">${rangeDocs.length}</span>
                    </div>
                    <ul class="group-content">
                        ${rangeDocs.map(doc => {
                            const href = doc.file.replace('.md', '.html');
                            const displayId = doc.id || 'N/A';
                            const year = doc.year || (doc.date ? doc.date.substring(0, 4) : '');
                            const topics = doc.topics || [];
                            
                            return `
                                <li class="chapter-item">
                                    <a href="${href}" class="doc-link">
                                        <div class="doc-main">
                                            <span class="doc-number">#${displayId}</span>
                                            <span class="doc-title">${doc.title || doc.file}</span>
                                            <span class="doc-year">(${year})</span>
                                        </div>
                                        ${topics.length > 0 ? `<div class="doc-topics">${topics.map(t => `<span class="topic-tag">${t}</span>`).join(' ')}</div>` : ''}
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
    
    renderChronologicalView(container, documents) {
        const grouped = {};
        
        documents.forEach(doc => {
            const year = parseInt(doc.year || (doc.date ? doc.date.substring(0, 4) : '0000'));
            const decade = Math.floor(year / 10) * 10;
            const key = decade === 0 ? 'Unknown' : `${decade}s`;
            
            if (!grouped[key]) grouped[key] = [];
            grouped[key].push(doc);
        });
        
        // Sort decades based on order
        const decadeKeys = Object.keys(grouped).sort((a, b) => {
            if (a === 'Unknown') return 1;
            if (b === 'Unknown') return -1;
            return this.currentOrder === 'asc' ? a.localeCompare(b) : b.localeCompare(a);
        });
        
        const html = decadeKeys.map(decade => {
            const docs = grouped[decade].sort((a, b) => {
                const aDate = a.year || a.date || '0000';
                const bDate = b.year || b.date || '0000';
                return this.currentOrder === 'asc' ? aDate.localeCompare(bDate) : bDate.localeCompare(aDate);
            });
            
            return `
                <li class="chapter-item expanded">
                    <div class="group-header" onclick="this.classList.toggle('collapsed'); this.nextElementSibling.classList.toggle('collapsed')">
                        <span class="arrow">▼</span>
                        <span>${decade}</span>
                        <span class="count">${docs.length}</span>
                    </div>
                    <ul class="group-content">
                        ${docs.map(doc => {
                            const href = doc.file.replace('.md', '.html');
                            const displayId = doc.id || doc.date;
                            const year = doc.year || (doc.date ? doc.date.substring(0, 4) : '');
                            const topics = doc.topics || [];
                            
                            return `
                                <li class="chapter-item">
                                    <a href="${href}" class="doc-link">
                                        <div class="doc-main">
                                            <span class="doc-number">#${displayId}</span>
                                            <span class="doc-title">${doc.title}</span>
                                            <span class="doc-year">(${year})</span>
                                        </div>
                                        ${topics.length > 0 ? `<div class="doc-topics">${topics.map(t => `<span class="topic-tag">${t}</span>`).join(' ')}</div>` : ''}
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
    
    renderTopicalView(container, documents) {
        if (!this.topics) {
            this.renderChronologicalView(container, documents);
            return;
        }
        
        const html = Object.keys(this.topics)
            .map(topic => {
                const topicDocs = this.topics[topic]
                    .map(docKey => this.documents.find(d => this.getDocumentKey(d) === docKey))
                    .filter(d => d && documents.includes(d));
                
                if (topicDocs.length === 0) return '';
                
                // Sort docs within topic based on current order
                topicDocs.sort((a, b) => {
                    const aDate = a.year || a.date || '0000';
                    const bDate = b.year || b.date || '0000';
                    return this.currentOrder === 'asc' ? aDate.localeCompare(bDate) : bDate.localeCompare(aDate);
                });
                
                return `
                    <li class="chapter-item expanded">
                        <div class="group-header" onclick="this.classList.toggle('collapsed'); this.nextElementSibling.classList.toggle('collapsed')">
                            <span class="arrow">▼</span>
                            <span>${topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                            <span class="count">${topicDocs.length}</span>
                        </div>
                        <ul class="group-content">
                            ${topicDocs.map(doc => {
                                const href = doc.file.replace('.md', '.html');
                                const displayId = doc.id || doc.date;
                                const year = doc.year || (doc.date ? doc.date.substring(0, 4) : '');
                                return `
                                    <li class="chapter-item">
                                        <a href="${href}" class="doc-link">
                                            <div class="doc-main">
                                                <span class="doc-number">#${displayId}</span>
                                                <span class="doc-title">${doc.title}</span>
                                                <span class="doc-year">(${year})</span>
                                            </div>
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
        if (!content || !this.currentDocument) return;
        
        const docKey = this.getDocumentKey(this.currentDocument);
        const rels = this.relationships[docKey];
        
        if (!rels) {
            content.innerHTML = '<div class="panel-placeholder">No relationships found</div>';
            return;
        }
        
        let html = `
            <div class="current-document">
                <h4>${this.currentDocument.title}</h4>
                <p class="doc-meta">
                    ${this.currentDocument.type.charAt(0).toUpperCase() + this.currentDocument.type.slice(1)} 
                    ${this.currentDocument.id || this.currentDocument.date || ''}
                </p>
            </div>
        `;
        
        // Amendments
        if (rels.amended_by && rels.amended_by.length > 0) {
            html += this.renderRelationshipSection('Amended By', rels.amended_by, 'amendment');
        }
        
        if (rels.amends && rels.amends.length > 0) {
            html += this.renderRelationshipSection('Amends', rels.amends, 'amendment');
        }
        
        // References
        if (rels.referenced_by && rels.referenced_by.length > 0) {
            html += this.renderRelationshipSection('Referenced By', rels.referenced_by, 'reference');
        }
        
        if (rels.references && rels.references.length > 0) {
            html += this.renderRelationshipSection('References', rels.references, 'reference');
        }
        
        // Interpretations
        if (rels.interpretations && rels.interpretations.length > 0) {
            html += this.renderRelationshipSection('Section References', rels.interpretations, 'interpretation');
        }
        
        // Related documents
        if (rels.related && rels.related.length > 0) {
            html += this.renderRelationshipSection('Related Documents', rels.related.slice(0, 5), 'related');
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

// Initialize when DOM is loaded and mdBook is ready
function initWhenReady() {
    console.log('NavigationController: Starting initialization...');
    
    // For mdBook, we need a different approach - wait for the actual content
    let attempts = 0;
    const maxAttempts = 100; // 10 seconds
    
    const checkSidebar = setInterval(() => {
        attempts++;
        
        // Look for signs that mdBook has loaded
        const sidebarScrollbox = document.querySelector('mdbook-sidebar-scrollbox');
        const sidebar = document.querySelector('#sidebar');
        
        // Debug logging
        if (attempts === 1 || attempts % 10 === 0) {
            console.log('NavigationController: Checking for sidebar...', {
                sidebarScrollbox: !!sidebarScrollbox,
                sidebar: !!sidebar,
                attempts: attempts
            });
        }
        
        // Check if we have the basic structure
        if (sidebarScrollbox && sidebar) {
            clearInterval(checkSidebar);
            console.log('NavigationController: Found sidebar elements, initializing...');
            
            // Initialize immediately - we'll handle dynamic content separately
            new NavigationController();
        } else if (attempts >= maxAttempts) {
            clearInterval(checkSidebar);
            console.warn('NavigationController: Timeout - forcing initialization');
            new NavigationController();
        }
    }, 100);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWhenReady);
} else {
    initWhenReady();
}