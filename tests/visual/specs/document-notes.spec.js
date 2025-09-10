const { test, expect } = require('@playwright/test');

test.describe('Document Notes Visual Tests', () => {
  const documentsWithNotes = [
    '/ordinances/1999-Ord-65-99-Sewer-Services.html',
    '/ordinances/1978-Ord-28-Parks.html',
    '/ordinances/1993-Ord-57-93-Manufactured-Homes.html'
  ];

  documentsWithNotes.forEach(path => {
    const docName = path.split('/').pop().replace('.html', '');
    
    test(`document notes styling - ${docName}`, async ({ page }) => {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      
      // Wait for Document Notes section
      const docNotes = page.locator('.document-note').first();
      const count = await docNotes.count();
      
      if (count > 0) {
        // Full Document Notes section
        await expect(docNotes).toHaveScreenshot(`${docName}-notes-full.png`);
        
        // Check for icon positioning
        const iconVisible = await page.evaluate(() => {
          const noteEl = document.querySelector('.document-note');
          if (!noteEl) return false;
          const styles = window.getComputedStyle(noteEl, '::after');
          return styles.content.includes('📝');
        });
        
        expect(iconVisible).toBeTruthy();
      }
    });
  });

  test('document notes components', async ({ page }) => {
    await page.goto('/ordinances/1999-Ord-65-99-Sewer-Services.html');
    await page.waitForLoadState('networkidle');
    
    const docNotes = page.locator('.document-note').first();
    const exists = await docNotes.count() > 0;
    
    if (exists) {
      // Test individual components
      
      // Note type labels (badges)
      const noteLabel = page.locator('.note-type-label').first();
      if (await noteLabel.count() > 0) {
        await expect(noteLabel).toHaveScreenshot('note-type-label.png');
      }
      
      // Page reference
      const pageRef = page.locator('.label-page-ref').first();
      if (await pageRef.count() > 0) {
        await expect(pageRef).toHaveScreenshot('page-reference.png');
      }
      
      // Note content area
      const noteContent = page.locator('.note-content').first();
      if (await noteContent.count() > 0) {
        await expect(noteContent).toHaveScreenshot('note-content.png');
      }
    }
  });

  test('document notes styling properties', async ({ page }) => {
    await page.goto('/ordinances/1999-Ord-65-99-Sewer-Services.html');
    await page.waitForLoadState('networkidle');
    
    const docNotes = page.locator('.document-note').first();
    const exists = await docNotes.count() > 0;
    
    if (exists) {
      // Verify CSS properties
      await expect(docNotes).toHaveCSS('position', 'relative');
      await expect(docNotes).toHaveCSS('background-color', 'rgb(255, 255, 255)'); // white
      
      // Check for border
      const border = await docNotes.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return styles.border;
      });
      expect(border).toContain('1px');
      
      // Check padding is applied
      const padding = await docNotes.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return styles.padding;
      });
      expect(padding).not.toBe('0px');
    }
  });

  test('document notes with form fields', async ({ page }) => {
    await page.goto('/ordinances/1999-Ord-65-99-Sewer-Services.html');
    await page.waitForLoadState('networkidle');
    
    // Test Document Notes containing form fields
    const notesWithFields = page.locator('.document-note:has(.form-field-filled)').first();
    const hasFields = await notesWithFields.count() > 0;
    
    if (hasFields) {
      await expect(notesWithFields).toHaveScreenshot('notes-with-form-fields.png');
    }
  });

  test('document notes responsive behavior', async ({ page }) => {
    await page.goto('/ordinances/1999-Ord-65-99-Sewer-Services.html');
    await page.waitForLoadState('networkidle');
    
    const docNotes = page.locator('.document-note').first();
    const exists = await docNotes.count() > 0;
    
    if (exists) {
      // Test at different viewport sizes
      
      // Mobile
      await page.setViewportSize({ width: 375, height: 667 });
      await expect(docNotes).toHaveScreenshot('notes-mobile.png');
      
      // Tablet
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(docNotes).toHaveScreenshot('notes-tablet.png');
      
      // Desktop
      await page.setViewportSize({ width: 1440, height: 900 });
      await expect(docNotes).toHaveScreenshot('notes-desktop.png');
    }
  });
});