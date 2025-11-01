# Propose Solution

You are being asked to design a solution with implementation plan and rollback strategy.

## Your Task

1. **Parse the issue ID** from the command (e.g., `/propose-solution ISSUE-009`)

2. **Find the diagnosis files**:
   - Look in `issues/problem-identified/` for:
     - `ISSUE-{NNN}-CONTEXT.md` (original issue)
     - `ISSUE-{NNN}-DIAGNOSIS.md` (root cause analysis)
   - Read BOTH files completely

3. **Read the solution template**:
   - Read `workflow/issues/templates/3-SOLUTION-TEMPLATE.md`

4. **Execute the 5-step mandatory checklist** (DO NOT SKIP ANY STEPS):

   ### ✅ Step 1: Solution Design (REQUIRED)
   - **Evaluate 2-3 different approaches** (minimum 2 options)
   - For each option:
     - Describe approach
     - List pros (benefits)
     - List cons (drawbacks)
     - Assess complexity (Low/Medium/High)
     - Assess risk (Low/Medium/High)
   - **Select the best option** and justify why
   - **Review for breaking changes** (migration needed? deprecation period?)
   - **Document all options in template**

   ### ✅ Step 2: Implementation Plan (REQUIRED)
   - List ALL files to modify (with line numbers)
   - Show exact code changes (BEFORE/AFTER snippets)
   - Define execution order (what depends on what)
   - Identify risks and mitigation strategies
   - **Document complete implementation plan in template**

   ### ✅ Step 3: Testing Strategy (REQUIRED)
   - Define unit tests (what to test, expected results)
   - Define integration tests (end-to-end workflows)
   - Define regression tests (run full suite)
   - Define performance tests (if applicable)
   - **Document testing strategy in template**

   ### ✅ Step 4: Rollback Plan (REQUIRED)
   - **Can we rollback?** (Yes/No and why)
   - Define rollback steps (exact commands)
   - Identify data migration needs (reversible?)
   - Identify rollback risks
   - **Document complete rollback plan in template**

   ### ✅ Step 5: Documentation (REQUIRED)
   - Identify what code comments needed
   - Identify what API docs need updating
   - Identify what architecture docs need updating
   - Identify what user docs need updating (if user-facing)
   - **Document documentation plan in template**

5. **Fill in the solution template**:
   - Replace all `{NNN}` with issue number
   - Replace all `{Title}` with issue title
   - Replace `{YYYY-MM-DD}` with today's date
   - Fill in ALL checklist items
   - Include code snippets for all changes
   - Include exact file paths with line numbers

6. **Create solution file**:
   - Filename: `ISSUE-{NNN}-SOLUTION.md`
   - Save to: `issues/solution-identified/`

7. **Move existing files**:
   - Copy `ISSUE-{NNN}-CONTEXT.md` from `problem-identified/` to `solution-identified/`
   - Copy `ISSUE-{NNN}-DIAGNOSIS.md` from `problem-identified/` to `solution-identified/`
   - Delete originals from `problem-identified/`

8. **Output summary**:
   ```
   ✅ Solution proposal complete!
   💡 Recommended approach: {option name}

   📋 Implementation plan:
      - Modify {file}:{lines} ({description})
      - Modify {file}:{lines} ({description})
      - Add {count} tests
      - Breaking changes: {Yes/No}

   🔄 Rollback: {method} ({notes})

   Created:
      - issues/solution-identified/ISSUE-{NNN}-CONTEXT.md
      - issues/solution-identified/ISSUE-{NNN}-DIAGNOSIS.md
      - issues/solution-identified/ISSUE-{NNN}-SOLUTION.md

   Next step: /test-ready ISSUE-{NNN}
   ```

## Options Evaluation (MANDATORY)

**You MUST evaluate at least 2 different approaches:**

Example format:
- **Option 1**: Add try-catch to cache operations
  - Pros: ✅ Simple, ✅ No breaking changes
  - Cons: ❌ Doesn't fix root cause
  - Complexity: Low
  - Risk: Low

- **Option 2**: Redesign cache system with circuit breaker
  - Pros: ✅ Fixes root cause, ✅ Better reliability
  - Cons: ❌ High complexity, ❌ Breaking changes
  - Complexity: High
  - Risk: Medium

- **Chosen**: Option 1 (then explain WHY Option 1 is better)

## Error Handling

- If issue not found in `problem-identified/`: Show error, list available issues
- If diagnosis incomplete: Cannot proceed, ask user to complete diagnosis
- If only 1 option evaluated: Request at least 2 options for comparison
