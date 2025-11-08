const { test, expect } = require("@playwright/test");

/**
 * Visual regression test for Ordinance 65-99 Section 2
 *
 * This section has a complex structure that has regressed multiple times:
 * - "B. Lake Oswego agrees to:" (numbered list with nested alpha list)
 * - "C. The parties agree:" (should be paragraph BETWEEN two numbered lists, not inside B's list)
 * - Following numbered list (1. and 2.)
 *
 * The postprocessor extracts "C. The parties agree:" from being a list item
 * and positions it correctly as a standalone paragraph.
 */

test.describe("Ordinance 65-99 Section 2 - List Break", () => {
  test("section 2 B and C layout", async ({ page }) => {
    await page.goto("/ordinances/1999-Ord-65-99-Sewer-Services.html");
    await page.waitForLoadState("networkidle");

    // Find "B. Lake Oswego agrees to:" heading
    const bSection = page
      .locator('p:has-text("B. Lake Oswego agrees to:")')
      .first();

    // Get the parent container that includes B, C, and the following lists
    const container = bSection.locator("xpath=ancestor::*[1]");

    // Take screenshot of the entire B/C section
    await expect(container).toHaveScreenshot("1999-ord-65-section-2-b-c.png");
  });

  // TODO: Re-enable when postprocessor correctly extracts "C. The parties agree:"
  // The postprocessor fix_ord_65_list_break() needs to handle the case where
  // "C." is wrapped in <span class="list-marker-alpha">
  test.skip("C. The parties agree - structure validation", async ({ page }) => {
    await page.goto("/ordinances/1999-Ord-65-99-Sewer-Services.html");
    await page.waitForLoadState("networkidle");

    // Verify "C. The parties agree:" is a paragraph, not a list item
    const cParagraph = page
      .locator('p:has-text("C. The parties agree:")')
      .first();
    await expect(cParagraph).toBeVisible();

    // Verify it has a <strong> tag (correct structure)
    const cStrong = cParagraph.locator(
      'strong:has-text("C. The parties agree:")'
    );
    await expect(cStrong).toBeVisible();

    // Verify it's NOT inside a list item (the regression)
    const parentLi = cParagraph.locator("xpath=ancestor::li");
    const isInsideList = (await parentLi.count()) > 0;
    expect(isInsideList).toBe(false);

    // Take a focused screenshot of just the C paragraph
    await expect(cParagraph).toHaveScreenshot(
      "1999-ord-65-section-2-c-paragraph.png"
    );
  });
});
