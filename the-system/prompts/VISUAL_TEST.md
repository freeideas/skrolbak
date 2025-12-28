You are performing visual verification of a screenshot.

---

## Your Task

**Screenshot:** {IMAGE_FILE}

**Expected appearance:** {DESCRIPTION}

**Code location:** {CODE_PATH}

**Test script:** {TEST_SCRIPT}

---

## Project-Specific Testing Rules

Check if `./specs/TESTING.md` exists. If it does, read it first and follow any project-specific instructions it contains. Those instructions take precedence over the defaults below.

If `./specs/TESTING.md` does not exist, proceed with the instructions below.

---

## Instructions

1. **Examine the screenshot** at `{IMAGE_FILE}`

2. **Compare against the expected appearance:**
   - Does the screenshot visually match what is described?
   - Look for key visual elements mentioned in the description
   - Consider overall appearance, UI elements, colors, text, layout

3. **Make your decision:**

   **If the screenshot MATCHES the description:**
   - Do NOT modify any code files
   - Report what you found that confirms the match

   **If the screenshot does NOT MATCH the description:**
   - Modify the code in `{CODE_PATH}` to fix the visual appearance
   - Make minimal changes necessary to achieve the expected look
   - If you need to take a new screenshot to verify your fix, see example `{TEST_SCRIPT}` for how screenshots are captured in this project

---

## Taking New Screenshots

If you need to verify your changes by taking a new screenshot:

1. Read `{TEST_SCRIPT}` to understand how screenshots are captured
2. The test script shows the exact mechanism used (Selenium, Playwright, Flutter, etc.)
3. Use the same approach to capture a verification screenshot
4. Check if your changes achieved the expected appearance

---

## Examples

### Example 1: Match (No Changes)

**Expected:** "A login form with centered blue submit button"

**Screenshot shows:** Form with email/password fields, blue "Login" button centered below

**Action:** Do NOT modify any files. Report:
```
The screenshot shows a login form with email and password input fields.
A blue "Login" button is centered below the form fields.
This matches the expected appearance -- no changes needed.
```

### Example 2: Mismatch (Fix Required)

**Expected:** "A login form with centered blue submit button"

**Screenshot shows:** Form with a green button aligned to the left

**Action:** Modify the code to change button color and alignment:
```css
/* Changed from green to blue, added centering */
.submit-button {
    background-color: #0066cc;  /* was #00cc66 */
    margin: 0 auto;  /* added for centering */
    display: block;  /* added for centering */
}
```

Report what was wrong and what you fixed.

### Example 3: Iterative Fix

**Expected:** "Navigation bar with logo on left and menu on right"

**Screenshot shows:** Logo and menu both on the left

**Action:**
1. Modify CSS to move menu to the right
2. Read `{TEST_SCRIPT}` to learn how to take screenshots
3. Take a new screenshot to verify the fix
4. If still wrong, continue fixing until correct

---

## What to Report

**Format:**

```
VISUAL CHECK: {DESCRIPTION}
STATUS: [PASS|FAIL]

FINDINGS:
[What you observed in the screenshot]

CHANGES:
[If FAIL: what you modified and why]
[If PASS: "No changes -- appearance already matches"]

VERIFICATION:
[If you took additional screenshots, describe what you saw]
```

---

## Important Notes

- **Minimal changes:** Only modify what's necessary to achieve the expected appearance
- **Preserve functionality:** Don't break existing behavior while fixing visuals
- **Be reasonable:** Minor variations are acceptable (exact pixel matching not required)
- **Focus on intent:** Match the spirit of the description, not necessarily literal interpretation
- **Document changes:** Clearly explain what you changed and why

---

Begin your visual inspection now.
