const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './specs',
  outputDir: './test-results',
  
  // Maximum time for each test
  timeout: 30000,
  
  // Test reporter
  reporter: [
    ['html', { outputFolder: './test-report', open: 'never' }],
    ['list']
  ],
  
  // Shared settings for all tests
  use: {
    // Base URL for tests
    baseURL: 'http://localhost:3000',
    
    // Screenshot options
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true
    },
    
    // Visual regression settings
    ignoreHTTPSErrors: true,
    
    // Viewport size
    viewport: { width: 1280, height: 720 }
  },
  
  // Configure projects for different browsers/viewports
  projects: [
    {
      name: 'Desktop Chrome',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      }
    },
    {
      name: 'Desktop Firefox',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 }
      }
    },
    {
      name: 'Desktop Safari',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1920, height: 1080 }
      }
    },
    {
      name: 'Tablet',
      use: { 
        ...devices['iPad Pro'],
        viewport: { width: 1024, height: 1366 }
      }
    },
    {
      name: 'Mobile',
      use: { 
        ...devices['iPhone 12'],
        viewport: { width: 390, height: 844 }
      }
    }
  ],
  
  // Dev server configuration
  webServer: {
    command: 'npm run serve',
    port: 3000,
    timeout: 120000,
    reuseExistingServer: true
  }
});