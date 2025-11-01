# Test Ready - Implement and Validate

You are being asked to implement the solution and validate through comprehensive testing.

## Your Task

1. **Parse the issue ID** from the command (e.g., `/test-ready ISSUE-009`)

2. **Find all solution files**:
   - Look in `issues/solution-identified/` for:
     - `ISSUE-{NNN}-CONTEXT.md` (original issue)
     - `ISSUE-{NNN}-DIAGNOSIS.md` (root cause)
     - `ISSUE-{NNN}-SOLUTION.md` (implementation plan)
   - Read ALL three files completely

3. **Read the testing template**:
   - Read `workflow/issues/templates/4-TESTING-TEMPLATE.md`

4. **Execute the 9-phase mandatory checklist** (DO NOT SKIP ANY PHASES):

   ### ✅ Phase 1: Pre-Implementation Review
   - Read solution proposal completely
   - Verify all files identified
   - Confirm test plan complete
   - Check for breaking changes
   - Review rollback plan
   - **Document review in template**

   ### ✅ Phase 2: Implementation
   - **Follow exact execution order** from solution proposal
   - For each file change:
     - Make the change
     - Verify syntax is correct
     - Document what changed
   - **Document all changes in template**

   ### ✅ Phase 3: Unit Testing
   - Create unit tests as specified in solution
   - Run each test
   - Verify each test passes
   - **Document test results in template**
   - **If any test fails**: Fix code, re-test, document fix

   ### ✅ Phase 4: Integration Testing
   - **Reproduce original issue WITHOUT fix** (verify still broken)
   - **Apply fix and test again** (verify now fixed)
   - Run end-to-end workflow test
   - **Document integration test results in template**
   - **If original issue not fixed**: Re-diagnose, update solution

   ### ✅ Phase 5: Regression Testing
   - Run full test suite: `pytest tests/ -v`
   - Document results (tests run, passed, failed, skipped)
   - **If any failures**:
     - Determine if related to fix
     - Fix if needed
     - Document resolution
   - **Document regression results in template**

   ### ✅ Phase 6: Performance Testing
   - If performance-related issue:
     - Measure baseline performance
     - Measure performance after fix
     - Document change (+/-X%)
   - If not applicable: Mark as N/A
   - **Document performance results in template**

   ### ✅ Phase 7: Code Quality
   - Run formatters:
     ```bash
     black src/ tests/
     isort src/ tests/
     ```
   - Run linter:
     ```bash
     flake8 src/ tests/ --max-line-length=100
     ```
   - Run type checker:
     ```bash
     mypy src/
     ```
   - **All must pass before proceeding**
   - **Document code quality results in template**

   ### ✅ Phase 8: Documentation
   - Add code comments (explain WHY, not just WHAT)
   - Update API docs (if API changed)
   - Update architecture docs (if design changed)
   - Update CHANGELOG
   - **Document what was updated in template**

   ### ✅ Phase 9: Commit
   - Stage changes: `git add {files}`
   - Create commit with detailed message:
     ```
     fix: ISSUE-{NNN} - {Title}

     PROBLEM: {1-line problem}
     ROOT CAUSE: {1-line cause}
     FIX: {1-line fix}
     IMPACT: {breaking changes/none}

     Files changed: {list}
     Tests added: {count}
     ```
   - Record commit hash
   - **Document commit in template**

5. **Fill in the testing template**:
   - Replace all `{NNN}` with issue number
   - Replace all `{Title}` with issue title
   - Replace `{YYYY-MM-DD}` with today's date
   - Fill in ALL checklist items
   - Include test output evidence
   - Include before/after comparisons

6. **Create testing file**:
   - Filename: `ISSUE-{NNN}-TESTING.md`
   - Save to: `issues/needs-tested/`

7. **Move existing files**:
   - Copy all 3 files from `solution-identified/` to `needs-tested/`:
     - `ISSUE-{NNN}-CONTEXT.md`
     - `ISSUE-{NNN}-DIAGNOSIS.md`
     - `ISSUE-{NNN}-SOLUTION.md`
   - Delete originals from `solution-identified/`

8. **Output summary**:
   ```
   ✅ Implementation and testing complete!

   🧪 Test results:
      - Unit tests: {X}/{Y} passed
      - Integration tests: {X}/{Y} passed
      - Regression tests: {X}/{Y} passed
      - Performance: {impact/no impact/N/A}

   📝 Commit: {hash}
      Files changed: {count}
      Lines added: {count}
      Lines removed: {count}

   Created:
      - issues/needs-tested/ISSUE-{NNN}-CONTEXT.md
      - issues/needs-tested/ISSUE-{NNN}-DIAGNOSIS.md
      - issues/needs-tested/ISSUE-{NNN}-SOLUTION.md
      - issues/needs-tested/ISSUE-{NNN}-TESTING.md

   Next step: /archive-issue ISSUE-{NNN}
   ```

## Validation Gates (MANDATORY)

**You MUST NOT mark phase complete until:**
- ✅ Original issue is verified fixed (reproduce test shows it working)
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Regression tests pass (no breakage introduced)
- ✅ Code quality checks pass (black, isort, flake8, mypy)
- ✅ Documentation updated
- ✅ Commit created

**If ANY validation gate fails:**
- Document the failure
- Fix the issue
- Re-run validation
- Only proceed when ALL gates pass

## Error Handling

- If issue not found in `solution-identified/`: Show error, list available issues
- If solution incomplete: Cannot proceed, ask user to complete solution
- If tests fail: Do NOT commit, fix issues first
- If regression tests fail: Determine if related to fix, resolve before proceeding
- If code quality fails: Fix formatting/linting/type errors before proceeding
