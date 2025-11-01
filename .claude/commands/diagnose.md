# Diagnose Issue

You are being asked to systematically diagnose an issue using the mandatory diagnostic checklist.

## Your Task

1. **Parse the issue ID** from the command (e.g., `/diagnose ISSUE-009`)

2. **Find the issue context file**:
   - Look in `issues/new-issue-context/` for `ISSUE-{NNN}-*.md`
   - Read the entire file to understand the issue

3. **Read the diagnosis template**:
   - Read `workflow/issues/templates/2-DIAGNOSIS-TEMPLATE.md`

4. **Execute the 5-step mandatory checklist** (DO NOT SKIP ANY STEPS):

   ### ✅ Step 1: Code Review (REQUIRED)
   - Search codebase for keywords from error message/symptoms using Grep
   - List ALL affected files
   - **READ EVERY AFFECTED FILE** using Read tool (no assumptions!)
   - Map upstream dependencies (what calls this code)
   - Map downstream dependencies (what this code calls)
   - Check for similar patterns elsewhere (grep for similar code)
   - **Document all findings in template**

   ### ✅ Step 2: Error Analysis (REQUIRED)
   - Analyze full error message
   - Identify error type (exception, HTTP error, database error, etc.)
   - Trace stack trace to origin
   - Review error handling (is error caught? logged? graceful degradation?)
   - **Document all findings in template**

   ### ✅ Step 3: Reproduction (REQUIRED)
   - Follow exact steps from ISSUE-{NNN}-CONTEXT.md
   - Reproduce the issue (verify it actually happens)
   - Isolate minimal reproduction case
   - Test edge cases (what makes it worse/better)
   - **Document reproduction evidence in template**

   ### ✅ Step 4: Impact Analysis (REQUIRED)
   - Identify direct impact (what breaks immediately)
   - Identify cascading effects (secondary breakage)
   - Assess user impact (how many users affected)
   - Check database impact (schema/data changes needed)
   - Check API changes (breaking changes)
   - **Document impact scope in template**

   ### ✅ Step 5: Root Cause Analysis (REQUIRED)
   - Identify THE ACTUAL BUG (not just symptoms)
   - Identify contributing factors (what made this possible)
   - Identify why not caught earlier (testing gaps, review gaps)
   - Check for similar past issues
   - Check if this is systematic (pattern across codebase)
   - **Document root cause in template**

5. **Fill in the diagnosis template**:
   - Replace all `{NNN}` with issue number
   - Replace all `{Title}` with issue title
   - Replace `{YYYY-MM-DD}` with today's date
   - Fill in ALL checklist items with actual findings
   - Include code snippets, file paths with line numbers
   - Include evidence (error messages, test results)

6. **Create diagnosis file**:
   - Filename: `ISSUE-{NNN}-DIAGNOSIS.md`
   - Save to: `issues/problem-identified/`

7. **Move context file**:
   - Copy `ISSUE-{NNN}-*.md` from `new-issue-context/` to `problem-identified/`
   - Rename to `ISSUE-{NNN}-CONTEXT.md`
   - Delete original from `new-issue-context/`

8. **Output summary**:
   ```
   ✅ Diagnosis complete!
   📊 Results:
      - Root cause: {brief summary}
      - Files affected: {list with line numbers}
      - Impact: {summary}
      - Severity: {P0/P1/P2/P3 confirmed}

   Created:
      - issues/problem-identified/ISSUE-{NNN}-CONTEXT.md
      - issues/problem-identified/ISSUE-{NNN}-DIAGNOSIS.md

   Next step: /propose-solution ISSUE-{NNN}
   ```

## Checklist Enforcement

**You MUST complete ALL checklist items before proceeding. This is non-negotiable.**

❌ **Will not proceed without:**
- Reading all affected files (use Read tool)
- Mapping dependencies (upstream + downstream)
- Reproducing the issue (verify it's real)
- Identifying root cause (not just symptoms)

## Error Handling

- If issue not found in `new-issue-context/`: Show error, list available issues
- If cannot reproduce issue: Document this in diagnosis, investigate why
- If multiple root causes: Document all, rank by priority
