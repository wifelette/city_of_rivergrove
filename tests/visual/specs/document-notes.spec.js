const { test, expect } = require('@playwright/test');

/**
 * Generate standardized snapshot name following our naming conventions
 * Format: {year}-{type}-{number}-{test-focus}.png
 *
 * Examples:
 * - 1999-ord-65-document-notes.png
 * - 1978-ord-28-signatures.png
 * - 2024-res-300-full-page.png
 */
function getSnapshotName(htmlPath, testFocus) {
  const filename = htmlPath.split('/').pop().replace('.html', '');

  // Parse the filename (e.g., "1999-Ord-65-99-Sewer-Services")
  const parts = filename.split('-');
  const year = parts[0]; // 1999

  // Determine document type from path
  let docType = 'other';
  if (htmlPath.includes('/ordinances/')) docType = 'ord';
  else if (htmlPath.includes('/resolutions/')) docType = 'res';
  else if (htmlPath.includes('/interpretations/')) docType = 'int';
  else if (htmlPath.includes('/agendas/')) docType = 'agenda';
  else if (htmlPath.includes('/minutes/')) docType = 'minutes';
  else if (htmlPath.includes('/transcripts/')) docType = 'transcript';

  // Extract document number (after Ord/Res/etc, before topic)
  // Handle formats like: Ord-65-99, Ord-28, Res-300
  let docNumber = parts[2]; // Start with first number
  if (parts[3] && /^\d+/.test(parts[3])) {
    docNumber += `-${parts[3]}`; // Add second number if exists (e.g., 65-99)
  }

  return `${year}-${docType}-${docNumber}-${testFocus}.png`;
}

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
        await expect(docNotes).toHaveScreenshot(getSnapshotName(path, 'document-notes'));
        
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
    const path = '/ordinances/1999-Ord-65-99-Sewer-Services.html';
    await page.goto(path);
    await page.waitForLoadState('networkidle');

    const docNotes = page.locator('.document-note').first();
    const exists = await docNotes.count() > 0;

    if (exists) {
      // Test individual components

      // Note type labels (badges)
      const noteLabel = page.locator('.note-type-label').first();
      if (await noteLabel.count() > 0) {
        await expect(noteLabel).toHaveScreenshot(getSnapshotName(path, 'note-type-label'));
      }

      // Page reference
      const pageRef = page.locator('.label-page-ref').first();
      if (await pageRef.count() > 0) {
        await expect(pageRef).toHaveScreenshot(getSnapshotName(path, 'page-reference'));
      }

      // Note content area
      const noteContent = page.locator('.note-content').first();
      if (await noteContent.count() > 0) {
        await expect(noteContent).toHaveScreenshot(getSnapshotName(path, 'note-content'));
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
    const path = '/ordinances/1999-Ord-65-99-Sewer-Services.html';
    await page.goto(path);
    await page.waitForLoadState('networkidle');

    // Test Document Notes containing form fields
    const notesWithFields = page.locator('.document-note:has(.form-field-filled)').first();
    const hasFields = await notesWithFields.count() > 0;

    if (hasFields) {
      await expect(notesWithFields).toHaveScreenshot(getSnapshotName(path, 'notes-with-form-fields'));
    }
  });

  test('document notes responsive behavior', async ({ page }) => {
    const path = '/ordinances/1999-Ord-65-99-Sewer-Services.html';
    await page.goto(path);
    await page.waitForLoadState('networkidle');

    const docNotes = page.locator('.document-note').first();
    const exists = await docNotes.count() > 0;

    if (exists) {
      // Test at different viewport sizes

      // Mobile
      await page.setViewportSize({ width: 375, height: 667 });
      await expect(docNotes).toHaveScreenshot(getSnapshotName(path, 'notes-mobile'));

      // Tablet
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(docNotes).toHaveScreenshot(getSnapshotName(path, 'notes-tablet'));

      // Desktop
      await page.setViewportSize({ width: 1440, height: 900 });
      await expect(docNotes).toHaveScreenshot(getSnapshotName(path, 'notes-desktop'));
    }
  });
});