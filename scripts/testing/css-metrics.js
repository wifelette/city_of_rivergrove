#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const csstree = require('css-tree');
const specificity = require('specificity');
const chalk = require('chalk');

class CSSMetricsAnalyzer {
  constructor() {
    this.metrics = {
      files: [],
      totals: {
        files: 0,
        rules: 0,
        selectors: 0,
        declarations: 0,
        importantCount: 0,
        mediaQueries: 0,
        uniqueProperties: new Set(),
        fileSize: 0,
        duplicateSelectors: 0,
        highSpecificitySelectors: 0,
        deeplyNestedSelectors: 0
      },
      issues: {
        important: [],
        highSpecificity: [],
        deepNesting: [],
        duplicates: [],
        vendorPrefixes: []
      }
    };
  }

  analyzeFile(filePath) {
    const css = fs.readFileSync(filePath, 'utf8');
    const ast = csstree.parse(css);
    
    const fileMetrics = {
      path: filePath,
      size: Buffer.byteLength(css, 'utf8'),
      rules: 0,
      selectors: 0,
      declarations: 0,
      important: 0,
      mediaQueries: 0,
      maxSpecificity: [0, 0, 0],
      maxNesting: 0
    };

    const selectors = new Set();

    csstree.walk(ast, (node, item, list) => {
      switch (node.type) {
        case 'Rule':
          fileMetrics.rules++;
          this.analyzeRule(node, fileMetrics, filePath);
          break;
          
        case 'Declaration':
          fileMetrics.declarations++;
          this.metrics.totals.uniqueProperties.add(node.property);
          
          if (node.important) {
            fileMetrics.important++;
            this.metrics.totals.importantCount++;
            this.metrics.issues.important.push({
              file: path.basename(filePath),
              property: node.property,
              line: this.getLineNumber(css, node.loc.start.offset)
            });
          }
          
          // Check for vendor prefixes
          if (node.property.startsWith('-webkit-') || 
              node.property.startsWith('-moz-') || 
              node.property.startsWith('-ms-') || 
              node.property.startsWith('-o-')) {
            this.metrics.issues.vendorPrefixes.push({
              file: path.basename(filePath),
              property: node.property
            });
          }
          break;
          
        case 'MediaQuery':
          fileMetrics.mediaQueries++;
          this.metrics.totals.mediaQueries++;
          break;
      }
    });

    this.metrics.totals.files++;
    this.metrics.totals.fileSize += fileMetrics.size;
    this.metrics.files.push(fileMetrics);
    
    return fileMetrics;
  }

  analyzeRule(rule, fileMetrics, filePath) {
    if (rule.prelude && rule.prelude.type === 'SelectorList') {
      rule.prelude.children.forEach(selector => {
        fileMetrics.selectors++;
        this.metrics.totals.selectors++;
        
        const selectorText = csstree.generate(selector);
        
        try {
          // Check specificity
          const specResult = specificity.calculate(selectorText);
          if (specResult && specResult.length > 0 && specResult[0].specificityArray) {
            const spec = specResult[0];
            const specArray = spec.specificityArray.slice(0, 3);
            
            // Track high specificity (anything with ID or too many classes)
            if (specArray[0] > 0 || specArray[1] > 3) {
              this.metrics.totals.highSpecificitySelectors++;
              this.metrics.issues.highSpecificity.push({
                file: path.basename(filePath),
                selector: selectorText,
                specificity: specArray.join(',')
              });
            }
            
            // Track max specificity
            for (let i = 0; i < 3; i++) {
              if (specArray[i] > fileMetrics.maxSpecificity[i]) {
                fileMetrics.maxSpecificity[i] = specArray[i];
              }
            }
          }
        } catch (e) {
          // Some selectors might not be parseable by specificity lib
          console.error(chalk.gray(`    Skipping specificity for: ${selectorText.substring(0, 50)}`));
        }
        
        // Check nesting depth
        const nestingDepth = this.getNestingDepth(selectorText);
        if (nestingDepth > fileMetrics.maxNesting) {
          fileMetrics.maxNesting = nestingDepth;
        }
        if (nestingDepth > 3) {
          this.metrics.totals.deeplyNestedSelectors++;
          this.metrics.issues.deepNesting.push({
            file: path.basename(filePath),
            selector: selectorText,
            depth: nestingDepth
          });
        }
      });
    }
  }

  getNestingDepth(selector) {
    const parts = selector.split(/[\s>+~]/);
    return parts.filter(p => p.length > 0).length;
  }

  getLineNumber(css, offset) {
    const lines = css.substring(0, offset).split('\n');
    return lines.length;
  }

  analyzeDirectory(dir) {
    const cssFiles = this.findCSSFiles(dir);
    
    cssFiles.forEach(file => {
      // Skip node_modules and build directories
      if (file.includes('node_modules') || 
          file.includes('book/') || 
          file.includes('FontAwesome/')) {
        return;
      }
      
      try {
        this.analyzeFile(file);
      } catch (error) {
        console.error(chalk.red(`Error analyzing ${file}: ${error.message}`));
      }
    });
  }

  findCSSFiles(dir) {
    let results = [];
    
    try {
      const files = fs.readdirSync(dir);
      
      for (const file of files) {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory() && !file.startsWith('.')) {
          results = results.concat(this.findCSSFiles(fullPath));
        } else if (file.endsWith('.css')) {
          results.push(fullPath);
        }
      }
    } catch (error) {
      // Ignore permission errors
    }
    
    return results;
  }

  printReport() {
    console.log(chalk.bold.blue('\n📊 CSS Metrics Report\n'));
    console.log(chalk.gray('═'.repeat(60)));
    
    // Summary
    console.log(chalk.bold('\n📈 Summary:'));
    console.log(`  Files analyzed: ${chalk.green(this.metrics.totals.files)}`);
    console.log(`  Total size: ${chalk.green(this.formatBytes(this.metrics.totals.fileSize))}`);
    console.log(`  Rules: ${chalk.green(this.metrics.totals.rules)}`);
    console.log(`  Selectors: ${chalk.green(this.metrics.totals.selectors)}`);
    console.log(`  Declarations: ${chalk.green(this.metrics.totals.declarations)}`);
    console.log(`  Unique properties: ${chalk.green(this.metrics.totals.uniqueProperties.size)}`);
    console.log(`  Media queries: ${chalk.green(this.metrics.totals.mediaQueries)}`);
    
    // Issues
    console.log(chalk.bold('\n⚠️  Issues Found:'));
    console.log(`  !important declarations: ${chalk.yellow(this.metrics.totals.importantCount)}`);
    console.log(`  High specificity selectors: ${chalk.yellow(this.metrics.totals.highSpecificitySelectors)}`);
    console.log(`  Deeply nested selectors: ${chalk.yellow(this.metrics.totals.deeplyNestedSelectors)}`);
    console.log(`  Vendor prefixes: ${chalk.yellow(this.metrics.issues.vendorPrefixes.length)}`);
    
    // Top issues
    if (this.metrics.issues.important.length > 0) {
      console.log(chalk.bold('\n🚨 Top !important usage:'));
      this.metrics.issues.important.slice(0, 10).forEach(issue => {
        console.log(`  ${chalk.red('!')} ${issue.file}:${issue.line} - ${issue.property}`);
      });
      if (this.metrics.issues.important.length > 10) {
        console.log(chalk.gray(`  ... and ${this.metrics.issues.important.length - 10} more`));
      }
    }
    
    if (this.metrics.issues.highSpecificity.length > 0) {
      console.log(chalk.bold('\n📍 High specificity selectors:'));
      this.metrics.issues.highSpecificity.slice(0, 5).forEach(issue => {
        console.log(`  ${chalk.yellow('⚠')} ${issue.file} - [${issue.specificity}] ${issue.selector.substring(0, 50)}${issue.selector.length > 50 ? '...' : ''}`);
      });
      if (this.metrics.issues.highSpecificity.length > 5) {
        console.log(chalk.gray(`  ... and ${this.metrics.issues.highSpecificity.length - 5} more`));
      }
    }
    
    // File details
    console.log(chalk.bold('\n📁 File Analysis:'));
    this.metrics.files
      .sort((a, b) => b.important - a.important)
      .slice(0, 10)
      .forEach(file => {
        const name = path.basename(file.path);
        console.log(`  ${name}:`);
        console.log(`    Size: ${this.formatBytes(file.size)} | Rules: ${file.rules} | !important: ${file.important}`);
      });
    
    // Recommendations
    console.log(chalk.bold('\n💡 Recommendations:'));
    if (this.metrics.totals.importantCount > 20) {
      console.log(chalk.yellow('  • High !important usage detected. Consider refactoring for better specificity management.'));
    }
    if (this.metrics.totals.highSpecificitySelectors > 10) {
      console.log(chalk.yellow('  • Many high specificity selectors. Consider using BEM or similar methodology.'));
    }
    if (this.metrics.totals.fileSize > 100000) {
      console.log(chalk.yellow('  • Large CSS size. Consider splitting into modules and lazy loading.'));
    }
    if (this.metrics.issues.vendorPrefixes.length > 0) {
      console.log(chalk.yellow('  • Vendor prefixes detected. Use autoprefixer for better browser support.'));
    }
    
    console.log(chalk.gray('\n' + '═'.repeat(60)));
    console.log(chalk.green('✅ Analysis complete!\n'));
    
    // Save JSON report
    const reportPath = path.join(process.cwd(), 'css-metrics-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(this.metrics, null, 2));
    console.log(chalk.gray(`Full report saved to: ${reportPath}\n`));
  }

  formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  }
}

// Run the analyzer
const analyzer = new CSSMetricsAnalyzer();
analyzer.analyzeDirectory(process.cwd());
analyzer.printReport();