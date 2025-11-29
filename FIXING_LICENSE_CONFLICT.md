# Fixing GitHub License Detection Conflict

## Problem

GitHub repository shows **GPL-3.0** in the header, but:
- LICENSE file contains **MIT License**
- README.md claims **MIT License**
- setup.py specifies **MIT License**

This creates confusion for contributors and users.

## Root Cause

GitHub's automatic license detection is showing cached/incorrect information.

## Solution Steps

### Step 1: Verify LICENSE File (Done ✓)

The LICENSE file is correct and contains the standard MIT License text.

### Step 2: Update GitHub Repository Settings

1. Go to your repository on GitHub: https://github.com/flytohub/flyto2
2. Click **Settings** (top right)
3. Scroll down to the **About** section (right sidebar on main repo page)
4. Click the ⚙️ gear icon next to "About"
5. Under **License**, select **MIT License** from the dropdown
6. Click **Save changes**

### Step 3: Force GitHub to Re-scan

Option A - Add a commit (Recommended):
```bash
# Make a trivial change to LICENSE to trigger re-scan
echo "" >> LICENSE
git add LICENSE
git commit -m "Trigger GitHub license re-scan"
git push
```

Option B - Wait for automatic re-scan:
- GitHub will eventually re-scan the license (may take hours/days)

### Step 4: Verify the Fix

After 5-10 minutes:
1. Visit https://github.com/flytohub/flyto2
2. Check the license badge in the top right
3. It should now show "MIT License"

## Additional Files to Check

These files also reference the license and should be consistent:

- ✅ `LICENSE` - MIT License (correct)
- ✅ `README.md` - Claims MIT (correct)
- ✅ `setup.py` - Claims MIT (correct)
- ⚠️ GitHub repo settings - Shows GPL-3.0 (needs manual update)

## Prevention

To avoid this in the future:
1. Always check GitHub's detected license after pushing changes
2. Keep LICENSE file in repository root with standard format
3. Manually verify repository settings match LICENSE file

## Current Status

- [x] LICENSE file verified as MIT
- [x] README.md references MIT
- [x] setup.py specifies MIT
- [ ] **Need to update GitHub repository settings manually**
- [ ] **Verify fix after settings update**

---

**Action Required**: Update the license in GitHub repository settings as described in Step 2.
