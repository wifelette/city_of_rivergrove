const { test, expect } = require('@playwright/test');

test.describe('Enhanced Document Elements Visual Tests', () => {
  test('definition items styling', async ({ page }) => {
    await page.goto('/resolutions/2019-Res-41425-Public-Records.html');
    await page.waitForLoadState('networkidle');
    
    // Wait for definition items
    const definitionItem = page.locator('.definition-item').first();
    await expect(definitionItem).toBeVisible();
    
    // Take screenshot of first definition item
    await expect(definitionItem).toHaveScreenshot('definition-item.png');
    
    // Test multiple definition items in context
    const section = page.locator('.content').filter({ hasText: 'Section 2' });
    await expect(section).toHaveScreenshot('definition-items-context.png');
    
    // Verify CSS properties
    await expect(definitionItem).toHaveCSS('padding', '16px');
    await expect(definitionItem).toHaveCSS('border-left', '3px solid rgb(9, 105, 218)');
    
    // Check definition marker styling
    const marker = page.locator('.definition-marker').first();
    // Font weight removed for cleaner appearance
    await expect(marker).toHaveCSS('color', 'rgb(9, 105, 218)');
  });

  test('formatted tables', async ({ page }) => {
    // Navigate to a page with formatted tables
    await page.goto('/resolutions/2024-Res-300-Fee-Schedule-Modification.html');
    await page.waitForLoadState('networkidle');
    
    const formattedTable = page.locator('.formatted-table').first();
    const tableCount = await formattedTable.count();
    
    if (tableCount > 0) {
      // Table wrapper screenshot
      const wrapper = page.locator('.table-wrapper').first();
      await expect(wrapper).toHaveScreenshot('table-wrapper.png');
      
      // Check table hover states
      const firstRow = formattedTable.locator('tbody tr').first();
      await firstRow.hover();
      await expect(firstRow).toHaveScreenshot('table-row-hover.png');
      
      // Verify table styling
      await expect(formattedTable).toHaveCSS('border-collapse', 'separate');
      await expect(formattedTable).toHaveCSS('border-spacing', '0px');
    }
  });

  test('WHEREAS clauses in resolutions', async ({ page }) => {
    await page.goto('/resolutions/1984-Res-72-Municipal-Services.html');
    await page.waitForLoadState('networkidle');
    
    const whereasClause = page.locator('.whereas-clause').first();
    const whereasCount = await whereasClause.count();
    
    if (whereasCount > 0) {
      await expect(whereasClause).toHaveScreenshot('whereas-clause.png');
      
      // Check marker styling
      const marker = whereasClause.locator('.whereas-marker').first();
      if (await marker.count() > 0) {
        // Font weight removed for cleaner appearance - marker still exists but not bold
        await expect(marker).toBeVisible();
      }
    }
  });

  test('responsive behavior', async ({ page }) => {
    await page.goto('/resolutions/2019-Res-41425-Public-Records.html');
    await page.waitForLoadState('networkidle');
    
    const definitionItem = page.locator('.definition-item').first();
    
    // Mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(definitionItem).toHaveScreenshot('enhanced-mobile.png');
    
    // Tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(definitionItem).toHaveScreenshot('enhanced-tablet.png');
    
    // Desktop viewport
    await page.setViewportSize({ width: 1440, height: 900 });
    await expect(definitionItem).toHaveScreenshot('enhanced-desktop.png');
  });

  test('print styles', async ({ page }) => {
    await page.goto('/resolutions/2019-Res-41425-Public-Records.html');
    await page.waitForLoadState('networkidle');
    
    // Emulate print media
    await page.emulateMedia({ media: 'print' });
    
    const definitionItem = page.locator('.definition-item').first();
    await expect(definitionItem).toHaveScreenshot('enhanced-print.png');
    
    // Reset to screen media
    await page.emulateMedia({ media: 'screen' });
  });
});