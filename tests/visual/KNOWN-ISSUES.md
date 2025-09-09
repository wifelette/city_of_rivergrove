# Known Visual Issues

## Meeting Pages UI Regression
**Date Identified**: January 2025  
**Status**: Not yet fixed  
**Pages Affected**: 
- `/minutes/*.html`
- `/agendas/*.html`
- `/transcripts/*.html`

**Description**: 
The Meeting pages are not showing the most recent version of the UI. There appears to be a regression that occurred during recent development work.

**Impact on Testing**:
- These pages should NOT be used as baseline references
- Visual tests for meeting pages should be skipped until fixed
- Once fixed, new baselines should be created

**Temporary Workaround**:
The test specs have been updated to skip Meeting pages until the regression is fixed.

## Action Items:
1. ✅ Document the issue
2. ⬜ Identify when/how the regression occurred
3. ⬜ Fix the regression
4. ⬜ Create new baseline screenshots for Meeting pages
5. ⬜ Re-enable Meeting page tests