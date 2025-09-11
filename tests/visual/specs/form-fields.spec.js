const { test, expect } = require('@playwright/test');

test.describe('Form Field Visual Tests', () => {
  test('filled form fields styling', async ({ page }) => {
    // Navigate to a page with filled form fields
    await page.goto('/ordinances/2001-Ord-70-2001-WQRA.html');
    await page.waitForLoadState('networkidle');
    
    // Wait for form fields to be styled
    await page.waitForSelector('.form-field-filled');
    
    // Take screenshot of first filled field
    const filledField = page.locator('.form-field-filled').first();
    await expect(filledField).toHaveScreenshot('filled-field.png');
    
    // Test hover state
    await filledField.hover();
    await expect(filledField).toHaveScreenshot('filled-field-hover.png');
    
    // Take screenshot of multiple fields in context
    const contentArea = page.locator('.content').first();
    await expect(contentArea).toHaveScreenshot('form-fields-context.png', {
      clip: { x: 0, y: 0, width: 800, height: 400 }
    });
  });

  test('empty form fields styling', async ({ page }) => {
    // Find a page with empty form fields if available
    await page.goto('/ordinances/1999-Ord-65-99-Sewer-Services.html');
    await page.waitForLoadState('networkidle');
    
    const emptyField = page.locator('.form-field-empty').first();
    const count = await emptyField.count();
    
    if (count > 0) {
      await expect(emptyField).toHaveScreenshot('empty-field.png');
      
      // Test hover tooltip
      await emptyField.hover();
      await page.waitForTimeout(600); // Wait for tooltip delay
      await expect(emptyField).toHaveScreenshot('empty-field-tooltip.png');
    }
  });

  test('form fields in different contexts', async ({ page }) => {
    await page.goto('/ordinances/2001-Ord-70-2001-WQRA.html');
    await page.waitForLoadState('networkidle');
    
    // Test form field in heading if exists
    const headingField = page.locator('h1 .form-field-filled, h2 .form-field-filled, h3 .form-field-filled').first();
    const headingCount = await headingField.count();
    
    if (headingCount > 0) {
      await expect(headingField).toHaveScreenshot('field-in-heading.png');
    }
    
    // Test form field in table if exists
    const tableField = page.locator('table .form-field-filled').first();
    const tableCount = await tableField.count();
    
    if (tableCount > 0) {
      await expect(tableField).toHaveScreenshot('field-in-table.png');
    }
  });

  test('form field colors and borders', async ({ page }) => {
    await page.goto('/ordinances/2001-Ord-70-2001-WQRA.html');
    await page.waitForLoadState('networkidle');
    
    const filledField = page.locator('.form-field-filled').first();
    
    // Verify CSS properties are applied
    await expect(filledField).toHaveCSS('background-color', 'rgb(227, 242, 253)'); // #e3f2fd
    await expect(filledField).toHaveCSS('border-bottom', '2px solid rgb(25, 118, 210)'); // #1976d2
    // Font weight removed for cleaner appearance
  });
});