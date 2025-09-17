/**
 * Copy Code Button Functionality for Style Guide
 * Adds copy buttons to all code blocks for easy code copying
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCopyCode);
    } else {
        initCopyCode();
    }

    function initCopyCode() {
        // Add copy buttons to all code blocks
        addCopyButtons();

        // Re-add buttons if content changes (for dynamic content)
        observeContentChanges();
    }

    function addCopyButtons() {
        // Find all code blocks - both traditional pre>code and div-based code snippets
        const codeBlocks = document.querySelectorAll('pre > code, .code-snippet, .markdown-example');

        codeBlocks.forEach((codeBlock) => {
            // Handle both pre>code structure and div-based snippets
            const isDiv = codeBlock.classList.contains('code-snippet') || codeBlock.classList.contains('markdown-example');
            const targetElement = isDiv ? codeBlock : codeBlock.parentElement;

            // Skip if button already exists
            if (targetElement.querySelector('.copy-code-button')) {
                return;
            }

            // Create wrapper div for positioning
            const wrapper = document.createElement('div');
            wrapper.className = 'code-block-wrapper';
            wrapper.style.position = 'relative';

            // Wrap the target element
            targetElement.parentNode.insertBefore(wrapper, targetElement);
            wrapper.appendChild(targetElement);

            // Create copy button
            const button = document.createElement('button');
            button.className = 'copy-code-button';
            button.textContent = 'Copy';
            button.setAttribute('aria-label', 'Copy code to clipboard');

            // Style the button
            Object.assign(button.style, {
                position: 'absolute',
                top: '8px',
                right: '8px',
                padding: '4px 12px',
                fontSize: '12px',
                fontWeight: '600',
                color: '#4A5568',
                backgroundColor: '#EDF2F7',
                border: '1px solid #CBD5E0',
                borderRadius: '4px',
                cursor: 'pointer',
                fontFamily: 'inherit',
                lineHeight: '1.5',
                transition: 'all 0.2s',
                zIndex: '10'
            });

            // Add hover effect
            button.addEventListener('mouseenter', () => {
                button.style.backgroundColor = '#E2E8F0';
                button.style.borderColor = '#A0AEC0';
                button.style.color = '#2D3748';
            });

            button.addEventListener('mouseleave', () => {
                if (button.textContent === 'Copy') {
                    button.style.backgroundColor = '#EDF2F7';
                    button.style.borderColor = '#CBD5E0';
                    button.style.color = '#4A5568';
                }
            });

            // Add click handler
            button.addEventListener('click', async () => {
                const code = codeBlock.textContent;

                try {
                    if (navigator.clipboard && window.isSecureContext) {
                        // Modern async clipboard API
                        await navigator.clipboard.writeText(code);
                    } else {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = code;
                        textArea.style.position = 'fixed';
                        textArea.style.opacity = '0';
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                    }

                    // Show success feedback
                    button.textContent = 'Copied!';
                    button.style.backgroundColor = '#C6F6D5';
                    button.style.borderColor = '#9AE6B4';
                    button.style.color = '#22543D';

                    // Reset after 2 seconds
                    setTimeout(() => {
                        button.textContent = 'Copy';
                        button.style.backgroundColor = '#EDF2F7';
                        button.style.borderColor = '#CBD5E0';
                        button.style.color = '#4A5568';
                    }, 2000);

                } catch (err) {
                    console.error('Failed to copy code:', err);
                    button.textContent = 'Error';
                    button.style.backgroundColor = '#FED7D7';
                    button.style.borderColor = '#FC8181';
                    button.style.color = '#742A2A';

                    setTimeout(() => {
                        button.textContent = 'Copy';
                        button.style.backgroundColor = '#EDF2F7';
                        button.style.borderColor = '#CBD5E0';
                        button.style.color = '#4A5568';
                    }, 2000);
                }
            });

            // Add button to wrapper
            wrapper.appendChild(button);
        });
    }

    function observeContentChanges() {
        // Watch for dynamic content changes
        if (typeof MutationObserver !== 'undefined') {
            const observer = new MutationObserver((mutations) => {
                // Check if any new code blocks were added
                let hasNewCode = false;
                mutations.forEach((mutation) => {
                    if (mutation.addedNodes.length > 0) {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === 1) { // Element node
                                if (node.matches && (node.matches('pre') || node.querySelector('pre'))) {
                                    hasNewCode = true;
                                }
                            }
                        });
                    }
                });

                if (hasNewCode) {
                    // Debounce to avoid multiple calls
                    clearTimeout(window.copyCodeDebounce);
                    window.copyCodeDebounce = setTimeout(addCopyButtons, 100);
                }
            });

            // Observe the main content area
            const content = document.querySelector('.content, #content, main');
            if (content) {
                observer.observe(content, {
                    childList: true,
                    subtree: true
                });
            }
        }
    }
})();

// Add global styles for copy button
if (!document.getElementById('copy-code-styles')) {
    const style = document.createElement('style');
    style.id = 'copy-code-styles';
    style.textContent = `
        .code-block-wrapper {
            position: relative;
        }

        .code-block-wrapper pre,
        .code-block-wrapper .code-snippet,
        .code-block-wrapper .markdown-example {
            padding-right: 60px !important; /* Make room for button */
        }

        .copy-code-button {
            opacity: 0.7;
        }

        .code-block-wrapper:hover .copy-code-button {
            opacity: 1;
        }

        @media print {
            .copy-code-button {
                display: none !important;
            }
        }

        /* For mdBook's hljs theme compatibility */
        .hljs {
            position: relative;
        }
    `;
    document.head.appendChild(style);
}