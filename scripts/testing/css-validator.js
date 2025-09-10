#!/usr/bin/env node

/**
 * CSS Validation Script
 * Phase 5: Comprehensive CSS quality checks
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// ANSI color codes for terminal output
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    gray: '\x1b[90m'
};

// Validation rules
const validators = {
    // Check for !important usage
    checkImportant: (content, file) => {
        const matches = content.match(/!important/g);
        if (matches) {
            return {
                level: 'error',
                count: matches.length,
                message: `Found ${matches.length} !important declaration(s)`
            };
        }
        return null;
    },

    // Check for hardcoded colors (not using variables)
    checkHardcodedColors: (content, file) => {
        // Skip variables.css file
        if (file.includes('variables.css')) return null;
        
        const hexColors = content.match(/#[0-9a-fA-F]{3,6}(?![0-9a-fA-F])/g);
        const rgbColors = content.match(/rgb\([^)]+\)/g);
        const namedColors = content.match(/(?:^|\s)(red|blue|green|yellow|black|white|gray|grey)(?:\s|;)/gi);
        
        const total = (hexColors?.length || 0) + (rgbColors?.length || 0) + (namedColors?.length || 0);
        
        if (total > 0) {
            return {
                level: 'warning',
                count: total,
                message: `Found ${total} hardcoded color(s) - use CSS variables instead`
            };
        }
        return null;
    },

    // Check for hardcoded spacing values
    checkHardcodedSpacing: (content, file) => {
        // Skip variables.css file
        if (file.includes('variables.css')) return null;
        
        const pixelValues = content.match(/\d+px/g);
        const remValues = content.match(/\d+(\.\d+)?rem/g);
        
        // Filter out common acceptable values (0, 1px for borders)
        const filtered = (pixelValues || []).filter(v => !['0px', '1px', '0.5px'].includes(v));
        
        if (filtered.length > 0) {
            return {
                level: 'warning',
                count: filtered.length,
                message: `Found ${filtered.length} hardcoded spacing value(s) - consider using variables`
            };
        }
        return null;
    },

    // Check for CSS variable usage
    checkVariableUsage: (content, file) => {
        // Skip variables.css file
        if (file.includes('variables.css')) return null;
        
        const variables = content.match(/var\(--[^)]+\)/g);
        
        if (!variables || variables.length < 5) {
            return {
                level: 'info',
                count: variables?.length || 0,
                message: `Low CSS variable usage (${variables?.length || 0}) - consider using more variables`
            };
        }
        return null;
    },

    // Check for overly specific selectors
    checkSelectorSpecificity: (content, file) => {
        // Look for selectors with more than 3 levels
        const overlySpecific = content.match(/([.#][\w-]+\s+){3,}[.#][\w-]+/g);
        
        if (overlySpecific) {
            return {
                level: 'warning',
                count: overlySpecific.length,
                message: `Found ${overlySpecific.length} overly specific selector(s)`
            };
        }
        return null;
    },

    // Check for duplicate properties within rules
    checkDuplicateProperties: (content, file) => {
        const rules = content.match(/\{[^}]+\}/g) || [];
        let duplicates = 0;
        
        rules.forEach(rule => {
            const properties = rule.match(/[\w-]+(?=:)/g) || [];
            const seen = new Set();
            
            properties.forEach(prop => {
                if (seen.has(prop)) {
                    duplicates++;
                }
                seen.add(prop);
            });
        });
        
        if (duplicates > 0) {
            return {
                level: 'error',
                count: duplicates,
                message: `Found ${duplicates} duplicate propert${duplicates === 1 ? 'y' : 'ies'}`
            };
        }
        return null;
    },

    // Check file size
    checkFileSize: (content, file) => {
        const lines = content.split('\n').length;
        const size = Buffer.byteLength(content, 'utf8');
        
        if (lines > 500) {
            return {
                level: 'info',
                count: lines,
                message: `Large file: ${lines} lines (${(size / 1024).toFixed(1)}KB) - consider splitting`
            };
        }
        return null;
    },

    // Check for vendor prefixes (should use autoprefixer instead)
    checkVendorPrefixes: (content, file) => {
        const prefixes = content.match(/-(?:webkit|moz|ms|o)-/g);
        
        if (prefixes) {
            return {
                level: 'info',
                count: prefixes.length,
                message: `Found ${prefixes.length} vendor prefix${prefixes.length === 1 ? '' : 'es'} - consider using autoprefixer`
            };
        }
        return null;
    },

    // Check for z-index values
    checkZIndex: (content, file) => {
        const zIndexes = content.match(/z-index:\s*(\d+)/g);
        
        if (zIndexes) {
            const values = zIndexes.map(z => parseInt(z.match(/\d+/)[0]));
            const highValues = values.filter(v => v > 100);
            
            if (highValues.length > 0) {
                return {
                    level: 'warning',
                    count: highValues.length,
                    message: `Found ${highValues.length} high z-index value(s) (>100): ${highValues.join(', ')}`
                };
            }
        }
        return null;
    }
};

// Main validation function
function validateCSS(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const results = [];
    
    // Run all validators
    Object.entries(validators).forEach(([name, validator]) => {
        const result = validator(content, filePath);
        if (result) {
            results.push({ name, ...result });
        }
    });
    
    return results;
}

// Get all CSS files
function getCSSFiles() {
    const patterns = [
        'theme/css/**/*.css',
        'custom.css'
    ];
    
    let files = [];
    patterns.forEach(pattern => {
        files = files.concat(glob.sync(pattern));
    });
    
    return files;
}

// Format output
function formatResults(file, results) {
    if (results.length === 0) {
        return `${colors.green}✓${colors.reset} ${colors.gray}${file}${colors.reset}`;
    }
    
    let output = `${colors.cyan}${file}${colors.reset}\n`;
    
    results.forEach(result => {
        const icon = result.level === 'error' ? '✗' : 
                    result.level === 'warning' ? '⚠' : 
                    'ℹ';
        const color = result.level === 'error' ? colors.red : 
                      result.level === 'warning' ? colors.yellow : 
                      colors.blue;
        
        output += `  ${color}${icon} ${result.message}${colors.reset}\n`;
    });
    
    return output;
}

// Summary statistics
function generateSummary(allResults) {
    const stats = {
        files: 0,
        clean: 0,
        errors: 0,
        warnings: 0,
        info: 0
    };
    
    Object.entries(allResults).forEach(([file, results]) => {
        stats.files++;
        if (results.length === 0) {
            stats.clean++;
        }
        results.forEach(r => {
            stats[r.level + 's']++;
        });
    });
    
    return stats;
}

// Main execution
function main() {
    console.log(`${colors.cyan}🔍 CSS Validation Report${colors.reset}`);
    console.log(`${colors.gray}${'='.repeat(50)}${colors.reset}\n`);
    
    const files = getCSSFiles();
    const allResults = {};
    
    // Validate each file
    files.forEach(file => {
        const results = validateCSS(file);
        allResults[file] = results;
        console.log(formatResults(file, results));
    });
    
    // Generate summary
    const stats = generateSummary(allResults);
    
    console.log(`\n${colors.cyan}📊 Summary${colors.reset}`);
    console.log(`${colors.gray}${'='.repeat(50)}${colors.reset}`);
    console.log(`Total files: ${stats.files}`);
    console.log(`${colors.green}✓ Clean files: ${stats.clean}${colors.reset}`);
    
    if (stats.errors > 0) {
        console.log(`${colors.red}✗ Errors: ${stats.errors}${colors.reset}`);
    }
    if (stats.warnings > 0) {
        console.log(`${colors.yellow}⚠ Warnings: ${stats.warnings}${colors.reset}`);
    }
    if (stats.info > 0) {
        console.log(`${colors.blue}ℹ Info: ${stats.info}${colors.reset}`);
    }
    
    // Quality score
    const score = Math.max(0, 100 - (stats.errors * 10) - (stats.warnings * 2));
    const scoreColor = score >= 90 ? colors.green : 
                      score >= 70 ? colors.yellow : 
                      colors.red;
    
    console.log(`\n${scoreColor}Quality Score: ${score}/100${colors.reset}`);
    
    // Architecture metrics
    console.log(`\n${colors.cyan}📐 Architecture Metrics${colors.reset}`);
    console.log(`${colors.gray}${'='.repeat(50)}${colors.reset}`);
    
    // Count total lines
    let totalLines = 0;
    let totalSize = 0;
    files.forEach(file => {
        const content = fs.readFileSync(file, 'utf8');
        totalLines += content.split('\n').length;
        totalSize += Buffer.byteLength(content, 'utf8');
    });
    
    console.log(`Total CSS lines: ${totalLines.toLocaleString()}`);
    console.log(`Total CSS size: ${(totalSize / 1024).toFixed(1)}KB`);
    console.log(`Average file size: ${(totalSize / files.length / 1024).toFixed(1)}KB`);
    console.log(`Modular files: ${files.filter(f => f.includes('theme/css/')).length}`);
    
    // Exit code based on errors
    process.exit(stats.errors > 0 ? 1 : 0);
}

// Run the validator
if (require.main === module) {
    main();
}

module.exports = { validateCSS, getCSSFiles };