const { test, expect } = require('@playwright/test');

test.describe('List Formatting Visual Tests', () => {
  // Full page test for Ord #54 - catches regressions anywhere
  test('Ord 54 full page with complex lists', async ({ page }) => {
    await page.goto('/ordinances/1989-Ord-54-89C-Land-Development.html');
    await page.waitForLoadState('networkidle');

    // Full page screenshot captures all list formatting
    await expect(page).toHaveScreenshot('ord-54-full-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  // Critical Section 5.080 - setback specifications with special formatting
  test('Section 5.080 setback specifications', async ({ page }) => {
    await page.goto('/ordinances/1989-Ord-54-89C-Land-Development.html');
    await page.waitForLoadState('networkidle');

    // Find Section 5.080
    const section = page.locator('h3:has-text("Section 5.080")');
    await expect(section).toBeVisible();

    // Capture the entire section including all setback specs
    const sectionContent = page.locator('#section-5080-general-building-setbacks-in-all-zones-and-districts').locator('..');
    await expect(sectionContent).toHaveScreenshot('section-5080-setbacks.png');
  });

  // Critical Section 5.120 - nested numeric lists under alpha items
  test('Section 5.120 nested lists', async ({ page }) => {
    await page.goto('/ordinances/1989-Ord-54-89C-Land-Development.html');
    await page.waitForLoadState('networkidle');

    // Find Section 5.120
    const section = page.locator('h3:has-text("Section 5.120")');
    await expect(section).toBeVisible();

    // Capture the entire section with nested lists
    const sectionContent = page.locator('#section-5120-home-occupations-in-all-zones-and-districts').locator('..');
    await expect(sectionContent).toHaveScreenshot('section-5120-nested-lists.png');
  });

  // Critical Section 2.060 - the original hanging indent issue
  test('Section 2.060 hanging indent for wrapped text', async ({ page }) => {
    await page.goto('/ordinances/1989-Ord-54-89C-Land-Development.html');
    await page.waitForLoadState('networkidle');

    // Find Section 2.060
    const section = page.locator('h3:has-text("Section 2.060")');
    await expect(section).toBeVisible();

    // Capture the section showing hanging indent behavior
    const sectionContent = page.locator('#section-2060-continuation-of-a-nonconforming-development').locator('..');
    await expect(sectionContent).toHaveScreenshot('section-2060-hanging-indent.png');
  });

  // These tests are now covered by the section-specific tests above
  // Commenting out to avoid selector issues with generic .first() locators

  // Test responsive behavior of lists on mobile
  test('list formatting on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/ordinances/1989-Ord-54-89C-Land-Development.html');
    await page.waitForLoadState('networkidle');

    // Capture Section 2.060 on mobile to ensure hanging indent works
    const section = page.locator('#section-2060-continuation-of-a-nonconforming-development').locator('..');
    await expect(section).toBeVisible();
    await expect(section).toHaveScreenshot('section-2060-mobile.png');
  });

  // Test roman numeral lists if they exist
  test('roman list markers', async ({ page }) => {
    await page.goto('/ordinances/1989-Ord-54-89C-Land-Development.html');
    await page.waitForLoadState('networkidle');

    const romanList = page.locator('ul.roman-list').first();
    const romanCount = await romanList.count();

    if (romanCount > 0) {
      await expect(romanList).toHaveScreenshot('roman-list.png');
    } else {
      // Skip if no roman lists found
      test.skip();
    }
  });

  // Test print styles for lists
  test('list formatting in print mode', async ({ page }) => {
    await page.goto('/ordinances/1989-Ord-54-89C-Land-Development.html');
    await page.waitForLoadState('networkidle');

    // Emulate print media
    await page.emulateMedia({ media: 'print' });

    // Capture Section 2.060 in print mode
    const section = page.locator('#section-2060-continuation-of-a-nonconforming-development').locator('..');
    await expect(section).toBeVisible();
    await expect(section).toHaveScreenshot('section-2060-print.png');

    // Reset to screen media
    await page.emulateMedia({ media: 'screen' });
  });
});
