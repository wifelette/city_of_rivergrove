const { test, expect } = require('@playwright/test');

test.describe('Font Size Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
  });

  test('body font size should be 16px', async ({ page }) => {
    // Check computed style of body
    const fontSize = await page.evaluate(() => {
      const body = document.body;
      return window.getComputedStyle(body).fontSize;
    });
    
    expect(fontSize).toBe('16px');
  });

  test('content paragraphs should be readable size', async ({ page }) => {
    // Navigate to a content page
    await page.goto('http://localhost:3000/ordinances/1974-Ord-16-Parks.html');
    
    // Check paragraph font size
    const paragraphSize = await page.evaluate(() => {
      const p = document.querySelector('.content p');
      if (!p) return null;
      return window.getComputedStyle(p).fontSize;
    });
    
    // Should inherit from body (16px) or be explicitly set
    expect(paragraphSize).toBeTruthy();
    const size = parseInt(paragraphSize);
    expect(size).toBeGreaterThanOrEqual(14);
    expect(size).toBeLessThanOrEqual(18);
  });

  test('headers should scale appropriately', async ({ page }) => {
    await page.goto('http://localhost:3000/ordinances/1974-Ord-16-Parks.html');
    
    const h1Size = await page.evaluate(() => {
      const h1 = document.querySelector('h1');
      if (!h1) return null;
      return parseInt(window.getComputedStyle(h1).fontSize);
    });
    
    const h2Size = await page.evaluate(() => {
      const h2 = document.querySelector('h2');
      if (!h2) return null;
      return parseInt(window.getComputedStyle(h2).fontSize);
    });
    
    // H1 should be larger than body text
    if (h1Size) {
      expect(h1Size).toBeGreaterThan(16);
    }
    
    // H2 should be between H1 and body
    if (h2Size && h1Size) {
      expect(h2Size).toBeLessThan(h1Size);
      expect(h2Size).toBeGreaterThan(16);
    }
  });

  test('mdBook root font-size handling', async ({ page }) => {
    // Check that we're properly handling mdBook's 62.5% root font-size
    const rootSize = await page.evaluate(() => {
      const html = document.documentElement;
      return window.getComputedStyle(html).fontSize;
    });
    
    // mdBook sets this to 62.5% of browser default (16px), so should be 10px
    expect(rootSize).toBe('10px');
    
    // But body should compensate with 1.6rem to get back to 16px
    const bodySize = await page.evaluate(() => {
      const body = document.body;
      const computed = window.getComputedStyle(body);
      return {
        fontSize: computed.fontSize,
        // Also check the rem value if possible
        fontSizeRem: computed.fontSize
      };
    });
    
    expect(bodySize.fontSize).toBe('16px');
  });

  test('tooltip font sizes should be consistent', async ({ page }) => {
    // Check that tooltips don't inherit unwanted font properties
    await page.goto('http://localhost:3000/resolutions/1984-Res-72-Municipal-Services.html');
    
    // Find an element with a tooltip
    const hasTooltip = await page.evaluate(() => {
      const elements = document.querySelectorAll('[data-tooltip]');
      return elements.length > 0;
    });
    
    if (hasTooltip) {
      // Hover to show tooltip
      await page.hover('[data-tooltip]');
      
      // Check pseudo-element styles (harder to test, but we can verify the element exists)
      const tooltipElement = await page.evaluate(() => {
        const el = document.querySelector('[data-tooltip]');
        if (!el) return null;
        const styles = window.getComputedStyle(el, ':after');
        return {
          fontSize: styles.fontSize,
          fontFamily: styles.fontFamily
        };
      });
      
      // Tooltips should have explicit font-size
      if (tooltipElement && tooltipElement.fontSize) {
        expect(tooltipElement.fontSize).toBe('12px');
      }
    }
  });
});