const { test, expect } = require('@playwright/test');

test.describe('Homepage Visual Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for navigation to load
    await page.waitForLoadState('networkidle');
  });

  test('homepage layout', async ({ page }) => {
    // Take full page screenshot
    await expect(page).toHaveScreenshot('homepage-full.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('homepage cards', async ({ page }) => {
    // Wait for cards to be visible
    const cardsContainer = page.locator('.simple-cards');
    await expect(cardsContainer).toBeVisible();
    
    // Screenshot just the cards section
    await expect(cardsContainer).toHaveScreenshot('homepage-cards.png');
  });

  test('navigation menu', async ({ page }) => {
    // Screenshot the top navigation
    const nav = page.locator('.menu-bar');
    await expect(nav).toBeVisible();
    await expect(nav).toHaveScreenshot('homepage-navigation.png');
  });

  test('homepage hover states', async ({ page }) => {
    // Test card hover state
    const firstCard = page.locator('.simple-card').first();
    await firstCard.hover();
    await expect(firstCard).toHaveScreenshot('card-hover.png');
  });

  test('theme switcher', async ({ page }) => {
    // Test theme switcher if visible
    const themeToggle = page.locator('#theme-toggle');
    if (await themeToggle.isVisible()) {
      await expect(themeToggle).toHaveScreenshot('theme-toggle.png');
      
      // Click and test dark mode
      await themeToggle.click();
      await page.waitForTimeout(500); // Wait for transition
      await expect(page).toHaveScreenshot('homepage-dark.png', {
        fullPage: true,
        animations: 'disabled'
      });
    }
  });
});