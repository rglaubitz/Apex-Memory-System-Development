# Archive Issue

You are being asked to move a resolved issue to the archive with complete history.

## Your Task

1. **Parse the issue ID** from the command (e.g., `/archive-issue ISSUE-009`)

2. **Find all testing files**:
   - Look in `issues/needs-tested/` for:
     - `ISSUE-{NNN}-CONTEXT.md` (original issue)
     - `ISSUE-{NNN}-DIAGNOSIS.md` (root cause)
     - `ISSUE-{NNN}-SOLUTION.md` (implementation plan)
     - `ISSUE-{NNN}-TESTING.md` (validation results)
   - Read ALL four files completely

3. **Verify resolution is complete**:
   - Check TESTING.md for completion status
   - Verify commit was created (commit hash present)
   - Verify all tests passed
   - Verify code quality checks passed
   - Verify documentation was updated
   - **If ANY item incomplete**: Stop and inform user what's missing

4. **Get current date** in YYYY-MM format (e.g., "2025-10")

5. **Create archive folder structure**:
   - Create folder: `issues/archived/{YYYY-MM}/` if not exists
   - Get slug from original filename (ISSUE-{NNN}-{slug}.md)
   - Create folder: `issues/archived/{YYYY-MM}/ISSUE-{NNN}-{slug}/`

6. **Create SUMMARY.md** (quick reference file):
   ```markdown
   # ISSUE-{NNN}: {Title} - SUMMARY

   **Issue ID:** ISSUE-{NNN}
   **Archived Date:** {YYYY-MM-DD}
   **Status:** ✅ Resolved

   ---

   ## Quick Reference

   **Problem:**
   {1-2 sentence summary from DIAGNOSIS.md}

   **Root Cause:**
   {Primary cause from DIAGNOSIS.md}

   **Solution:**
   {Chosen approach from SOLUTION.md}

   **Files Modified:**
   {List from SOLUTION.md or TESTING.md}

   **Tests Added:**
   {Count from TESTING.md}

   **Commit:**
   {Hash from TESTING.md}

   ---

   ## Resolution Details

   **Severity:** {from CONTEXT.md}
   **Time to Resolve:** {calculate from dates}
   **Impact:** {from DIAGNOSIS.md}

   **All documentation:**
   - CONTEXT.md - Original issue report
   - DIAGNOSIS.md - Root cause analysis
   - SOLUTION.md - Implementation plan
   - TESTING.md - Validation results

   ---

   **Archived:** {YYYY-MM-DD}
   ```

7. **Move all files to archive**:
   - Move from `needs-tested/` to `archived/{YYYY-MM}/ISSUE-{NNN}-{slug}/`:
     - `ISSUE-{NNN}-CONTEXT.md`
     - `ISSUE-{NNN}-DIAGNOSIS.md`
     - `ISSUE-{NNN}-SOLUTION.md`
     - `ISSUE-{NNN}-TESTING.md`
   - Save new `SUMMARY.md` to same folder
   - Delete originals from `needs-tested/`

8. **Output summary**:
   ```
   ✅ Issue archived!

   📁 Location: issues/archived/{YYYY-MM}/ISSUE-{NNN}-{slug}/

   📄 Files:
      - SUMMARY.md (quick reference)
      - CONTEXT.md (original issue)
      - DIAGNOSIS.md (root cause analysis)
      - SOLUTION.md (fix proposal)
      - TESTING.md (validation results)

   🎯 Resolution:
      - Problem: {brief summary}
      - Root cause: {brief summary}
      - Fix: {brief summary}
      - Tests: {count} added, all passed
      - Commit: {hash}

   Issue ISSUE-{NNN} is now complete and archived.
   ```

## Archive Structure

The final archive structure will be:

```
issues/archived/
└── {YYYY-MM}/                    # Month folder (e.g., 2025-10)
    └── ISSUE-{NNN}-{slug}/       # Issue folder (e.g., ISSUE-009-cache-crashes)
        ├── SUMMARY.md            # Quick reference
        ├── CONTEXT.md            # Original issue
        ├── DIAGNOSIS.md          # Problem analysis
        ├── SOLUTION.md           # Fix proposal
        └── TESTING.md            # Validation results
```

## Validation Checks (MANDATORY)

**Before archiving, verify:**
- ✅ Issue exists in `needs-tested/`
- ✅ All 4 files present (CONTEXT, DIAGNOSIS, SOLUTION, TESTING)
- ✅ TESTING.md shows resolution complete
- ✅ Commit hash present in TESTING.md
- ✅ All tests passed
- ✅ Documentation updated

**If ANY check fails:**
- Show which checks failed
- Inform user what needs completion
- Do NOT archive until all checks pass

## Error Handling

- If issue not found in `needs-tested/`: Show error, list available issues
- If testing incomplete: Show what's missing, cannot archive yet
- If no commit hash: Tests not complete, cannot archive yet
- If tests failed: Issues not resolved, cannot archive yet
- If archive folder already exists: Warn user, ask if should overwrite

## Time Calculation

Calculate "Time to Resolve" by:
- Get "Reported Date" from CONTEXT.md
- Get "Testing Date" from TESTING.md
- Calculate business days difference
- Format as: "{X} days" or "{X} weeks"
