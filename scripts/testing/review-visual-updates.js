#!/usr/bin/env node

/**
 * Interactive Visual Test Update Tool
 *
 * Helps review and selectively update visual regression test baselines.
 *
 * Usage:
 *   npm run test:visual:review
 *
 * Workflow:
 *   1. Runs visual tests to identify failures
 *   2. Presents list of failed tests
 *   3. Allows selection of tests to update
 *   4. Updates only selected baselines
 */

const { spawn } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m',
};

class VisualTestReviewer {
  constructor() {
    this.failedTests = [];
    this.totalTestsRun = 0;
    this.testAliases = {}; // Maps short aliases to test indices
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  generateAlias(test, index) {
    // Generate short alias from filename and key part of test name
    const fileName = path.basename(test.file, '.spec.js');
    const filePrefix = fileName.split('-').map(word => word[0]).join('').substring(0, 3);

    // Use testName if available (from parseListOutput), otherwise fallback to fullTitle
    const nameToUse = test.testName || test.fullTitle;

    // Extract key identifier from test name (look for document/ordinance numbers)
    let keyPart = '';

    // Try to find 4-digit year followed by number (like 1999-Ord-65-99)
    const ordMatch = nameToUse.match(/(\d{4}).*?(\d{2,3})/);
    if (ordMatch) {
      keyPart = `${ordMatch[1].substring(2)}-${ordMatch[2]}`; // "99-65" from "1999-Ord-65"
    } else {
      // Fallback to any numbers
      const numMatch = nameToUse.match(/\d{2,4}/);
      if (numMatch) {
        keyPart = numMatch[0];
      } else {
        // Last resort: first few chars of test name
        keyPart = nameToUse.split(' ')[0].substring(0, 4).toLowerCase();
      }
    }

    const alias = `${filePrefix}-${keyPart}`.toLowerCase();
    this.testAliases[alias] = index;
    return alias;
  }

  log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
  }

  async checkServer() {
    // Check if dev server is running
    const http = require('http');

    return new Promise((resolve) => {
      const req = http.get('http://localhost:3000', (res) => {
        resolve(true);
      });

      req.on('error', () => {
        resolve(false);
      });

      req.setTimeout(1000, () => {
        req.destroy();
        resolve(false);
      });
    });
  }

  async runTests() {
    // Check if server is running
    const serverRunning = await this.checkServer();
    if (!serverRunning) {
      this.log('\n⚠️  Dev server is not running at localhost:3000', 'yellow');
      this.log('   Starting dev server... (this may take a moment)\n', 'cyan');
    } else {
      this.log('\n✓ Dev server detected at localhost:3000\n', 'green');
    }

    this.log('🎭 Running visual regression tests...', 'cyan');
    this.log('   This may take a minute - testing across multiple browsers\n', 'cyan');

    // Show a spinner
    const spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
    let spinnerIndex = 0;
    const spinnerInterval = setInterval(() => {
      process.stdout.write(`\r   ${spinner[spinnerIndex]} Running tests...`);
      spinnerIndex = (spinnerIndex + 1) % spinner.length;
    }, 80);

    return new Promise((resolve, reject) => {
      // Use default reporter to ensure webServer config is respected
      const testProcess = spawn('npx', ['playwright', 'test', '--reporter=list'], {
        cwd: process.cwd(),
        stdio: ['ignore', 'pipe', 'pipe']
      });

      let output = '';
      let testsStarted = false;
      let testCount = 0;
      let totalTests = 0;
      let lastReportedCount = 0;

      testProcess.stdout.on('data', (data) => {
        const dataStr = data.toString();
        output += dataStr;

        // Detect total test count at start
        if (!testsStarted) {
          const totalMatch = dataStr.match(/Running (\d+) tests? using/);
          if (totalMatch) {
            totalTests = parseInt(totalMatch[1]);
            this.totalTestsRun = totalTests; // Store for later
            testsStarted = true;
            clearInterval(spinnerInterval);
            process.stdout.write(`\r   ⚡ Running ${totalTests} tests across all browsers...\n\n`);
          }
        }

        // Count test completions (passed or failed)
        const passMatches = dataStr.match(/✓/g);
        const failMatches = dataStr.match(/✘/g);
        if (passMatches) testCount += passMatches.length;
        if (failMatches) testCount += failMatches.length;

        // Update progress bar (only when count changes and every 5 tests to reduce flicker)
        if (testsStarted && testCount > lastReportedCount && testCount % 5 === 0) {
          lastReportedCount = testCount;
          const percent = Math.floor((testCount / totalTests) * 100);
          const barLength = 30;
          const filled = Math.floor((testCount / totalTests) * barLength);
          const bar = '█'.repeat(filled) + '░'.repeat(barLength - filled);
          process.stdout.write(`\r   ${bar} ${testCount}/${totalTests} (${percent}%)`);
        }
      });

      testProcess.stderr.on('data', (data) => {
        // stderr might have error messages, but not test results
        if (process.env.DEBUG) {
          console.log('STDERR:', data.toString());
        }
      });

      testProcess.on('close', (code) => {
        clearInterval(spinnerInterval);
        if (testsStarted) {
          // Show final progress bar at 100%
          const barLength = 30;
          const bar = '█'.repeat(barLength);
          process.stdout.write(`\r   ${bar} ${totalTests}/${totalTests} (100%)\n`);
        }
        process.stdout.write('   ✓ Tests complete!\n');

        // Debug: show sample of output
        if (process.env.DEBUG) {
          console.log('\n--- DEBUG: Sample stdout output ---');
          console.log(output.split('\n').slice(0, 20).join('\n'));
          console.log('--- END DEBUG ---\n');
        }

        // Parse test output from stdout (list reporter writes there)
        this.parseListOutput(output);

        // Debug: show what was found
        if (process.env.DEBUG) {
          console.log(`\nDEBUG: Found ${this.failedTests.length} failed tests`);
          if (this.failedTests.length > 0) {
            console.log('First few:', this.failedTests.slice(0, 3));
          }
        }

        resolve();
      });

      testProcess.on('error', (error) => {
        clearInterval(spinnerInterval);
        this.log(`\n❌ Error running tests: ${error.message}`, 'red');
        reject(error);
      });
    });
  }

  parseListOutput(output) {
    // Parse the list reporter output to find failed tests
    // Format: "  ✘  123 [project] › tests/visual/specs/file.spec.js:line:col › Suite › test name (1.5s)"
    const lines = output.split('\n');
    const failedPattern = /^\s*✘\s+\d+\s+\[(.*?)\]\s+›\s+(.*?\.spec\.js):(\d+):\d+\s+›\s+(.+)/;

    const seenTests = new Set();

    for (const line of lines) {
      const match = line.match(failedPattern);
      if (match) {
        const [, project, fullFilePath, lineNum, fullTestPath] = match;
        const fileName = path.basename(fullFilePath);

        // Remove timing info like "(1.5s)" from the end
        const cleanedPath = fullTestPath.replace(/\s*\(\d+\.?\d*[ms]s?\)\s*$/, '').trim();

        // Extract just the test name (last part after final ›)
        const pathParts = cleanedPath.split('›').map(p => p.trim());
        const testName = pathParts[pathParts.length - 1];

        // Use cleaned full path for deduplication (includes suite name, no timing)
        const testKey = `${fileName}:${cleanedPath}`;

        // Avoid duplicates (same test might fail in multiple browsers)
        if (!seenTests.has(testKey)) {
          seenTests.add(testKey);
          this.failedTests.push({
            title: `[${project}] › ${cleanedPath}`,
            file: path.join(process.cwd(), 'tests/visual/specs', fileName),
            line: parseInt(lineNum),
            fullTitle: cleanedPath, // Full path including suite, no timing
            testName: testName // Just the test name for alias generation
          });
        }
      }
    }
  }

  async promptSelection() {
    if (this.failedTests.length === 0) {
      this.log('\n✅ No failed tests found! All visual tests are passing.', 'green');
      return [];
    }

    // Count total unique tests (not counting browser variations)
    const totalTests = this.failedTests.length;
    const passedTests = this.totalTestsRun - totalTests;

    this.log(`\n📋 Found ${this.failedTests.length} failed visual test(s) (${passedTests} passed):\n`, 'yellow');

    // Group tests by file and create display order mapping
    const testsByFile = {};
    const displayOrderMap = {}; // Maps display number to actual test
    this.failedTests.forEach((test, index) => {
      const fileName = path.basename(test.file);
      if (!testsByFile[fileName]) {
        testsByFile[fileName] = [];
      }
      testsByFile[fileName].push({ ...test, index });
    });

    // Display grouped tests with aliases and build display order map
    let displayNumber = 1;
    for (const [fileName, tests] of Object.entries(testsByFile)) {
      this.log(`  ${fileName}`, 'cyan');
      for (const test of tests) {
        const alias = this.generateAlias(test, test.index);
        this.log(`    ${displayNumber}. ${test.fullTitle} [${alias}]`, 'reset');
        displayOrderMap[displayNumber] = test; // Map display number to actual test
        displayNumber++;
      }
      console.log('');
    }

    // Store the display order map for use in selection
    this.displayOrderMap = displayOrderMap;

    this.log('Options:', 'bold');
    this.log('  • Enter a test number (e.g., "5") or alias (e.g., "dn-1999")');
    this.log('  • Enter partial text to fuzzy match (e.g., "65-99" or "headers")');
    this.log('  • Enter "all" to update all failed tests at once');
    this.log('  • Enter "report" to open the HTML test report');
    this.log('  • Enter "ui" to open the Playwright UI mode');
    this.log('  • Enter "done" to finish\n');

    return await this.interactiveSelection(testsByFile);
  }

  async interactiveSelection(testsByFile) {
    const selectedTests = [];
    let uiProcess = null;

    while (true) {
      const answer = await this.question('> ');
      const input = answer.trim().toLowerCase();

      if (input === 'done' || input === '') {
        // Clean up UI process if running
        if (uiProcess) {
          this.log('\n🛑 Closing Playwright UI...', 'yellow');
          uiProcess.kill();
        }
        break;
      }

      if (input === 'ui') {
        if (uiProcess) {
          this.log('\n⚠️  Playwright UI is already running', 'yellow');
        } else {
          this.log('\n🎭 Opening Playwright UI mode...', 'cyan');
          this.log('   Opening all tests - failed tests will show with red X', 'cyan');
          this.log('   (Click a failed test to see the diff)\n', 'cyan');

          const { spawn } = require('child_process');
          uiProcess = spawn('npx', ['playwright', 'test', '--ui'], {
            cwd: process.cwd(),
            stdio: 'ignore',
            detached: true
          });

          // Don't wait for the UI process
          uiProcess.unref();

          this.log('   ✓ Playwright UI will open shortly\n', 'green');
          this.log('   💡 Review diffs in the UI, then come back here to mark tests for update\n', 'blue');
        }
        continue;
      }

      if (input === 'report') {
        this.log('\n📊 Opening HTML test report...', 'cyan');
        const reportPath = path.join(process.cwd(), 'tests/visual/test-report/index.html');
        const { spawn } = require('child_process');
        spawn('open', [reportPath], { stdio: 'ignore' });
        this.log('   Report opened in your browser\n', 'green');
        continue;
      }

      if (input === 'all') {
        const confirm = await this.question('\n⚠️  Update ALL failed tests? (y/N): ');
        if (confirm.toLowerCase() === 'y') {
          return this.failedTests;
        }
        continue;
      }

      // Check if it's an alias
      if (this.testAliases[input]) {
        const testIndex = this.testAliases[input];
        const test = this.failedTests[testIndex];
        await this.handleTestSelection(test, selectedTests);
        continue;
      }

      // Check if it's a number
      const testNum = parseInt(input);
      if (!isNaN(testNum) && testNum >= 1 && testNum <= Object.keys(this.displayOrderMap).length) {
        const test = this.displayOrderMap[testNum];
        if (process.env.DEBUG) {
          console.log(`DEBUG: User entered ${testNum}, accessing displayOrderMap[${testNum}]`);
          console.log(`DEBUG: Test is: ${test.fullTitle}`);
        }
        await this.handleTestSelection(test, selectedTests);
        continue;
      }

      // Try fuzzy matching
      const matches = this.fuzzyMatchTests(input);
      if (matches.length === 1) {
        // Single match - use it
        await this.handleTestSelection(matches[0], selectedTests);
        continue;
      } else if (matches.length > 1) {
        // Multiple matches - show them and ask which one
        this.log(`\n🔍 Found ${matches.length} matches for "${input}":\n`, 'yellow');
        matches.forEach((test, idx) => {
          const testIndex = this.failedTests.indexOf(test);
          const alias = Object.keys(this.testAliases).find(key => this.testAliases[key] === testIndex);
          this.log(`  ${idx + 1}. ${test.fullTitle} [${alias}]`, 'reset');
        });

        const choice = await this.question('\nEnter number or alias to select (or Enter to cancel): ');
        if (choice.trim()) {
          // Try to select from the matches
          const choiceNum = parseInt(choice);
          if (!isNaN(choiceNum) && choiceNum >= 1 && choiceNum <= matches.length) {
            await this.handleTestSelection(matches[choiceNum - 1], selectedTests);
          } else if (this.testAliases[choice.trim().toLowerCase()]) {
            const testIndex = this.testAliases[choice.trim().toLowerCase()];
            await this.handleTestSelection(this.failedTests[testIndex], selectedTests);
          } else {
            this.log('Invalid selection\n', 'red');
          }
        }
        continue;
      }

      this.log('❌ No matches found. Try a test number, alias, or partial name', 'red');
    }

    return selectedTests;
  }

  fuzzyMatchTests(input) {
    // Match tests by partial name, file name, or any part of the test title
    const searchLower = input.toLowerCase();
    return this.failedTests.filter(test => {
      const fileName = path.basename(test.file, '.spec.js').toLowerCase();
      const fullTitle = test.fullTitle.toLowerCase();
      return fileName.includes(searchLower) || fullTitle.includes(searchLower);
    });
  }

  async handleTestSelection(test, selectedTests) {
    this.log(`\n📝 Selected: ${test.fullTitle}`, 'cyan');
    this.log('   File: ' + path.basename(test.file), 'cyan');

    const action = await this.question('   [v]iew, [u]pdate, or [s]kip? ');

    if (action.toLowerCase() === 'v') {
      this.log('   Opening test report...', 'blue');
      const reportPath = path.join(process.cwd(), 'tests/visual/test-report/index.html');
      const { spawn } = require('child_process');
      spawn('open', [reportPath], { stdio: 'ignore' });
      this.log('   💡 Check the report, then come back here\n', 'yellow');
      await this.question('   Press Enter when ready...');

      // Ask again after viewing
      const updateNow = await this.question('   Update this test? (y/N): ');
      if (updateNow.toLowerCase() === 'y') {
        selectedTests.push(test);
        this.log('   ✓ Marked for update\n', 'green');
      } else {
        this.log('   Skipped\n', 'yellow');
      }
    } else if (action.toLowerCase() === 'u') {
      selectedTests.push(test);
      this.log('   ✓ Marked for update\n', 'green');
    } else {
      this.log('   Skipped\n', 'yellow');
    }
  }

  async uiModeWorkflow() {
    const selectedTests = [];
    let uiProcess = null;

    this.log('UI Mode Instructions:', 'bold');
    this.log('  1. Type "ui" to open Playwright UI and review all tests');
    this.log('  2. In the UI, identify which tests you want to update');
    this.log('  3. Come back here and enter commands to update baselines\n');
    this.log('Commands:', 'bold');
    this.log('  • "ui" - Open Playwright UI mode (shows all tests)');
    this.log('  • "update:file:<filename>" - Update all tests in a file');
    this.log('     Example: update:file:font-sizes');
    this.log('  • "update:grep:<pattern>" - Update tests matching pattern');
    this.log('     Example: update:grep:headers should scale');
    this.log('  • "update:all" - Update ALL failed tests');
    this.log('  • "done" - Finish and apply updates\n');

    while (true) {
      const answer = await this.question('> ');
      const input = answer.trim().toLowerCase();

      if (input === 'done' || input === '') {
        if (uiProcess) {
          this.log('\n🛑 Closing Playwright UI...', 'yellow');
          uiProcess.kill();
        }
        break;
      }

      if (input === 'ui') {
        if (uiProcess) {
          this.log('\n⚠️  Playwright UI is already running', 'yellow');
        } else {
          this.log('\n🎭 Opening Playwright UI mode...', 'cyan');
          const { spawn } = require('child_process');
          uiProcess = spawn('npx', ['playwright', 'test', '--ui'], {
            cwd: process.cwd(),
            stdio: 'ignore',
            detached: true
          });
          uiProcess.unref();
          this.log('   ✓ UI opened - review tests there, then use commands here to update\n', 'green');
        }
        continue;
      }

      if (input.startsWith('update:file:')) {
        const fileName = input.substring(12).trim();
        this.log(`\n📝 Will update all tests in files matching: ${fileName}`, 'cyan');
        selectedTests.push({ type: 'file', pattern: fileName });
        this.log('   ✓ Queued for update\n', 'green');
        continue;
      }

      if (input.startsWith('update:grep:')) {
        const pattern = input.substring(12).trim();
        this.log(`\n📝 Will update tests matching: ${pattern}`, 'cyan');
        selectedTests.push({ type: 'grep', pattern: pattern });
        this.log('   ✓ Queued for update\n', 'green');
        continue;
      }

      if (input === 'update:all') {
        const confirm = await this.question('\n⚠️  Update ALL failed tests? (y/N): ');
        if (confirm.toLowerCase() === 'y') {
          selectedTests.push({ type: 'all' });
          this.log('   ✓ All tests queued for update\n', 'green');
        }
        continue;
      }

      this.log('❌ Invalid command. Try "ui", "update:file:name", "update:grep:pattern", or "done"', 'red');
    }

    return selectedTests;
  }

  async updateTests(selectedTests) {
    if (selectedTests.length === 0) {
      this.log('\n❌ No tests selected. Exiting.', 'yellow');
      return;
    }

    this.log(`\n🔄 Updating baselines...\n`, 'cyan');

    // Handle different update types
    for (const update of selectedTests) {
      if (update.type === 'all') {
        this.log('  📝 Updating ALL tests...', 'blue');
        await this.runUpdate('--update-snapshots');
      } else if (update.type === 'file') {
        this.log(`  📝 Updating tests in files matching: ${update.pattern}...`, 'blue');
        await this.runUpdate(`tests/visual/specs/*${update.pattern}*.spec.js`);
      } else if (update.type === 'grep') {
        this.log(`  📝 Updating tests matching: ${update.pattern}...`, 'blue');
        await this.runUpdateGrep(update.pattern);
      } else {
        // Original behavior - update specific test file
        const fileGroups = {};
        selectedTests.forEach(test => {
          if (test.file) {
            if (!fileGroups[test.file]) {
              fileGroups[test.file] = [];
            }
            fileGroups[test.file].push(test);
          }
        });

        for (const [file, tests] of Object.entries(fileGroups)) {
          const relativeFile = path.relative(process.cwd(), file);
          this.log(`  📝 Updating ${tests.length} test(s) in ${path.basename(file)}...`, 'blue');
          await this.runUpdate(relativeFile);
        }
      }
    }

    this.log('\n✅ Baseline updates complete!', 'green');
    this.log('\n💡 Next steps:', 'cyan');
    this.log('  1. Review the updated snapshots in git');
    this.log('  2. Run tests again: npm run test:visual');
    this.log('  3. Commit if everything looks good\n');
  }

  async runUpdate(file) {
    return new Promise((resolve, reject) => {
      const updateProcess = spawn('npx', ['playwright', 'test', file, '--update-snapshots'], {
        cwd: process.cwd(),
        stdio: 'inherit'
      });

      updateProcess.on('close', (code) => {
        resolve();
      });

      updateProcess.on('error', (error) => {
        this.log(`❌ Error updating ${file}: ${error.message}`, 'red');
        reject(error);
      });
    });
  }

  async runUpdateGrep(pattern) {
    return new Promise((resolve, reject) => {
      const updateProcess = spawn('npx', ['playwright', 'test', '--update-snapshots', '--grep', pattern], {
        cwd: process.cwd(),
        stdio: 'inherit'
      });

      updateProcess.on('close', (code) => {
        resolve();
      });

      updateProcess.on('error', (error) => {
        this.log(`❌ Error updating tests: ${error.message}`, 'red');
        reject(error);
      });
    });
  }

  question(prompt) {
    return new Promise((resolve) => {
      this.rl.question(`${colors.bold}${prompt}${colors.reset}`, (answer) => {
        resolve(answer);
      });
    });
  }

  async run() {
    try {
      this.log('\n' + '='.repeat(60), 'cyan');
      this.log('  Visual Test Baseline Update Tool', 'bold');
      this.log('='.repeat(60) + '\n', 'cyan');

      // Check if --ui flag was passed
      const useUIMode = process.argv.includes('--ui');

      if (useUIMode) {
        this.log('🎭 UI Mode: Skipping initial test run', 'cyan');
        this.log('   You can open the UI to review tests interactively\n', 'cyan');

        // Skip test run, go straight to interactive mode
        // User will open UI manually and use commands to update
        const selectedTests = await this.uiModeWorkflow();

        if (selectedTests.length > 0) {
          await this.updateTests(selectedTests);
        } else {
          this.log('\n👋 No tests updated.', 'cyan');
        }
        return;
      }

      await this.runTests();
      const selectedTests = await this.promptSelection();

      if (selectedTests.length > 0) {
        await this.updateTests(selectedTests);
      } else {
        this.log('\n👋 No tests updated.', 'cyan');
      }
    } catch (error) {
      this.log(`\n❌ Error: ${error.message}`, 'red');
      process.exit(1);
    } finally {
      this.rl.close();
    }
  }
}

// Run the tool
const reviewer = new VisualTestReviewer();
reviewer.run();
