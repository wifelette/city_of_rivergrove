/**
 * Enhanced Navigation Controls for City of Rivergrove mdBook
 * Adds search, filtering, and view controls to the sidebar
 * Also implements the right panel for document relationships
 */

class NavigationController {
    constructor() {
        this.documents = [];
        this.relationships = {};
        this.currentView = 'list';
        this.searchTerm = '';
        this.currentDocument = null;
        
        this.init();
    }
    
    async init() {
        // Load relationships data
        try {
            const response = await fetch('relationships.json');
            const data = await response.json();
            this.documents = Object.values(data.documents);
            this.relationships = data.relationships;
            this.topics = data.topics;
        } catch (error) {
            console.warn('Could not load relationships.json:', error);
        }
        
        // Initialize navigation enhancement
        this.enhanceSidebar();
        this.addRightPanel();
        this.bindEvents();
        this.detectCurrentDocument();
    }
    
    enhanceSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;
        
        // Create enhanced header
        const header = document.createElement('div');
        header.className = 'nav-header-enhanced';
        header.innerHTML = `
            <div class="nav-search-container">
                <input type="text" 
                       class="nav-search" 
                       placeholder="Search documents..." 
                       id="navSearch">
            </div>
            <div class="nav-controls">
                <button class="nav-btn active" data-view="list">List</button>
                <button class="nav-btn" data-view="decade">By Decade</button>
                <button class="nav-btn" data-view="topic">By Topic</button>
            </div>
            <div class="nav-stats" id="navStats">
                <span id="docCount">${this.documents.length}</span> documents
            </div>
        `;
        
        // Insert header at the top of sidebar
        const sidebarHeader = sidebar.querySelector('.sidebar-header') || sidebar.firstChild;
        if (sidebarHeader) {
            sidebarHeader.after(header);
        } else {
            sidebar.prepend(header);
        }
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
        const sidebar = document.querySelector('.sidebar-content ul') || document.querySelector('.chapter');
        if (!sidebar) return;
        
        const filtered = this.filterDocuments();
        
        switch (this.currentView) {
            case 'list':
                this.renderListView(sidebar, filtered);
                break;
            case 'decade':
                this.renderDecadeView(sidebar, filtered);
                break;
            case 'topic':
                this.renderTopicView(sidebar, filtered);
                break;
        }
        
        // Update stats
        const docCount = document.getElementById('docCount');
        if (docCount) {
            docCount.textContent = filtered.length;
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
    
    renderListView(container, documents) {
        // Sort documents by type and then chronologically
        const sorted = documents.sort((a, b) => {
            // First by type (ordinances, resolutions, interpretations)
            const typeOrder = { 'ordinance': 0, 'resolution': 1, 'interpretation': 2, 'transcript': 3 };
            if (typeOrder[a.type] !== typeOrder[b.type]) {
                return typeOrder[a.type] - typeOrder[b.type];
            }
            
            // Then by year/date
            const aDate = a.year || a.date || '0000';
            const bDate = b.year || b.date || '0000';
            return aDate.localeCompare(bDate);
        });
        
        const html = sorted.map(doc => {
            const href = doc.file.replace('.md', '.html');
            const displayId = doc.id || (doc.date ? doc.date : 'N/A');
            const year = doc.year || (doc.date ? doc.date.substring(0, 4) : '');
            
            return `
                <li class="chapter-item">
                    <a href="${href}" class="doc-link">
                        <span class="doc-number">#${displayId}</span>
                        <span class="doc-title">${doc.title || doc.file}</span>
                        <span class="doc-year">(${year})</span>
                    </a>
                </li>
            `;
        }).join('');
        
        container.innerHTML = html;
    }
    
    renderDecadeView(container, documents) {
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
    
    renderTopicView(container, documents) {
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

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new NavigationController());
} else {
    new NavigationController();
}