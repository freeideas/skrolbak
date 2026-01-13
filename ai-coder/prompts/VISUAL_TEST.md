You are performing visual verification of screenshot(s).

---

## Your Task

**Screenshot(s):**
{IMAGE_FILES}

**Assertion:** {ASSERTION}

**Code location:** {CODE_PATH}

**Test script:** {TEST_SCRIPT}

---

## Project-Specific Testing Rules

Check if `./specs/TESTING.md` exists. If it does, read it first and follow any project-specific instructions it contains.

---

## Instructions

1. **Examine the screenshot(s)** listed above

2. **Evaluate the assertion:**
   - Is the assertion TRUE about the screenshot(s)?
   - Look carefully at what the assertion claims

3. **Make your decision:**

   **If the assertion is TRUE:**
   - Do NOT modify any code files
   - Report what you observed that confirms the assertion

   **If the assertion is FALSE:**
   - Modify the code in `{CODE_PATH}` to make the assertion true
   - Make minimal changes necessary
   - If you need to take new screenshots to verify your fix, see `{TEST_SCRIPT}` for how screenshots are captured

---

## Examples

### Example 1: Single image, assertion true

**Assertion:** "A login form with centered blue submit button"

**Screenshot shows:** Form with email/password fields, blue "Login" button centered below

**Action:** Do NOT modify any files. Report:
```
ASSERTION: A login form with centered blue submit button
STATUS: TRUE

The screenshot shows a login form with email and password input fields.
A blue "Login" button is centered below the form fields.
Assertion is true -- no changes needed.
```

### Example 2: Two images, assertion true

**Assertion:** "The two screenshots show different background positions"

**Screenshots show:** First image has background shifted left, second has background shifted right

**Action:** Do NOT modify any files. Report:
```
ASSERTION: The two screenshots show different background positions
STATUS: TRUE

Screenshot 1 shows background positioned to the left.
Screenshot 2 shows background positioned to the right.
The backgrounds are clearly in different positions.
Assertion is true -- no changes needed.
```

### Example 3: Single image, assertion false

**Assertion:** "A login form with centered blue submit button"

**Screenshot shows:** Form with a green button aligned to the left

**Action:** Modify the code to change button color and alignment, then report:
```
ASSERTION: A login form with centered blue submit button
STATUS: FALSE

Screenshot shows green button aligned left, not blue and centered.
Fixed by modifying CSS: changed button color to blue and added centering.
```

### Example 4: Two images, assertion false

**Assertion:** "The two screenshots show different background positions"

**Screenshots show:** Both images have background in the same position

**Action:** Modify the code to ensure background moves, then report:
```
ASSERTION: The two screenshots show different background positions
STATUS: FALSE

Both screenshots show background in the same position.
Fixed by modifying animation code to ensure position changes between frames.
```

---

## What to Report

**Format:**

```
ASSERTION: {ASSERTION}
STATUS: [TRUE|FALSE]

OBSERVATIONS:
[What you observed in the screenshot(s)]

CHANGES:
[If FALSE: what you modified and why]
[If TRUE: "No changes -- assertion is true"]
```

---

## Important Notes

- **Minimal changes:** Only modify what's necessary to make the assertion true
- **Preserve functionality:** Don't break existing behavior while fixing visuals
- **Be reasonable:** Minor variations are acceptable (exact pixel matching not required)
- **Document changes:** Clearly explain what you changed and why

---

Begin your visual inspection now.
