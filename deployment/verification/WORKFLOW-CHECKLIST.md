# Verification Workflow Checklist

**Purpose:** Ensure the verification process is followed correctly for every theory.

**Goal:** Complete, traceable, evidence-based verification with zero shortcuts.

---

## Table of Contents

1. [Pre-Verification Requirements](#pre-verification-requirements)
2. [Step-by-Step Research Process](#step-by-step-research-process)
3. [Verification Decision Criteria](#verification-decision-criteria)
4. [Auto-Trigger Procedures](#auto-trigger-procedures)
5. [Quality Gates](#quality-gates)
6. [Sign-Off Process](#sign-off-process)

---

## Pre-Verification Requirements

**Before starting research on ANY theory, confirm:**

- [ ] Theory file exists in `unverified/` folder
- [ ] Theory follows the template (Hypothesis, Expected Behavior, Why Important, Research Plan)
- [ ] Research plan is detailed and specific
- [ ] Success criteria are defined
- [ ] Priority is assigned (Blocker/Critical/Important/Nice-to-have)

**If any checkbox is unchecked, DO NOT proceed. Update the theory file first.**

---

## Step-by-Step Research Process

### Phase 1: Code Search (30-60 minutes)

**Objective:** Find evidence of the feature in the codebase

**Checklist:**

- [ ] **Search API endpoints**
  ```bash
  grep -r "[feature-keyword]" apex-memory-system/src/apex_memory/api/
  ```

- [ ] **Search workflows**
  ```bash
  grep -r "[FeatureName]Workflow" apex-memory-system/src/apex_memory/temporal/workflows/
  ```

- [ ] **Search activities**
  ```bash
  grep -r "[feature-keyword]_activity" apex-memory-system/src/apex_memory/temporal/activities/
  ```

- [ ] **Search services**
  ```bash
  grep -r "[FeatureName]Service" apex-memory-system/src/apex_memory/services/
  ```

- [ ] **Search database writers**
  ```bash
  grep -r "write_[feature-keyword]" apex-memory-system/src/apex_memory/database/
  ```

- [ ] **Check database schemas**
  ```bash
  PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "\dt" | grep [feature-keyword]
  ```

- [ ] **Document findings** in `research-logs/[theory-name]-research.md`
  - List all files found
  - Copy relevant code snippets
  - Note partial implementations

**Output:** Research log with all code search results

---

### Phase 2: Test Execution (15-30 minutes)

**Objective:** Verify feature works via tests

**Checklist:**

- [ ] **Find test files**
  ```bash
  find apex-memory-system/tests/ -name "*[feature-keyword]*"
  ```

- [ ] **Run unit tests**
  ```bash
  cd apex-memory-system
  pytest tests/unit/test_[feature-keyword].py -v
  ```

- [ ] **Run integration tests**
  ```bash
  pytest tests/integration/test_[feature-keyword].py -v -m integration
  ```

- [ ] **Run API smoke tests** (if applicable)
  ```bash
  curl http://localhost:8000/api/v1/[feature-endpoint] | jq
  ```

- [ ] **Document test results** in research log
  - Pass/fail counts
  - Error messages
  - Test coverage

**Output:** Test execution results appended to research log

---

### Phase 3: Manual Verification (15-30 minutes)

**Objective:** Manually test the feature if automated tests don't exist

**Checklist (only if no automated tests found):**

- [ ] **Start all services**
  ```bash
  cd apex-memory-system/docker && docker-compose up -d
  temporal server start-dev &
  python src/apex_memory/temporal/workers/dev_worker.py &
  uvicorn apex_memory.main:app --reload --port 8000 &
  ```

- [ ] **Test API endpoint** (if applicable)
  ```bash
  curl -X POST http://localhost:8000/api/v1/[feature-endpoint] \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}'
  ```

- [ ] **Check Temporal UI** (if workflow-based)
  - Open http://localhost:8088
  - Search for workflow executions
  - Verify workflow completed successfully

- [ ] **Check database** (if data is written)
  ```bash
  PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory \
    -c "SELECT * FROM [table_name] LIMIT 5;"
  ```

- [ ] **Document manual test results** in research log

**Output:** Manual verification results appended to research log

---

### Phase 4: Evidence Compilation (15 minutes)

**Objective:** Organize all findings for decision-making

**Checklist:**

- [ ] **Create evidence summary** in research log
  - Code found: YES/NO
  - Tests found: YES/NO
  - Tests passing: YES/NO/N/A
  - Manual verification: PASS/FAIL/N/A

- [ ] **Capture proof**
  - Code snippets (minimum 10 lines showing feature)
  - Test output (pass/fail results)
  - API response (if applicable)
  - Database query results (if applicable)

- [ ] **Determine feature completeness**
  - Fully implemented (all components working)
  - Partially implemented (some components missing/broken)
  - Not implemented (no evidence found)

**Output:** Evidence summary with proof

---

## Verification Decision Criteria

### Decision Matrix

Use this matrix to make the verification decision:

| Evidence Found | Tests Exist | Tests Pass | Manual Verification | **DECISION** |
|----------------|-------------|------------|---------------------|--------------|
| ✅ Yes | ✅ Yes | ✅ Yes | ✅ Pass | **IMPLEMENTED** |
| ✅ Yes | ✅ Yes | ✅ Yes | N/A | **IMPLEMENTED** |
| ✅ Yes | ✅ Yes | ❌ No | ❌ Fail | **MISSING** (broken) |
| ✅ Yes | ❌ No | N/A | ✅ Pass | **IMPLEMENTED** (needs tests) |
| ✅ Yes | ❌ No | N/A | ❌ Fail | **MISSING** (incomplete) |
| ❌ No | ❌ No | N/A | N/A | **MISSING** |

### Detailed Criteria

**Feature is IMPLEMENTED if:**
1. ✅ Code exists for all components (API, workflow, activities, database)
2. ✅ Tests exist (unit + integration)
3. ✅ Tests pass (100% pass rate)
4. ✅ Manual verification successful (if applicable)
5. ✅ Documentation exists

**Feature is MISSING if:**
1. ❌ No code found, OR
2. ❌ Partial implementation (missing critical components), OR
3. ❌ Tests failing, OR
4. ❌ Manual verification fails, OR
5. ❌ No documentation

**Special Case: Partial Implementation**

If feature is partially implemented:
- Treat as **MISSING**
- Document what exists vs. what's missing
- Create completion plan in upgrade folder

---

## Auto-Trigger Procedures

### Trigger 1: Feature is MISSING

**When:** Verification decision is MISSING

**Automatic Actions:**

1. **Move theory file**
   ```bash
   mv unverified/[theory].md verified/missing/[theory].md
   ```

2. **Update theory file**
   - Change status to "MISSING ❌"
   - Add research findings
   - Add evidence summary
   - Add next steps

3. **Create upgrade folder**
   ```bash
   mkdir -p upgrades/active/[feature-name]/{research,tests}
   ```

4. **Create upgrade documents**
   - `IMPROVEMENT-PLAN.md` - What needs to be built
   - `IMPLEMENTATION-GUIDE.md` - How to build it
   - `research/RESEARCH-FOUNDATION.md` - Research findings
   - `tests/TEST-SPECIFICATIONS.md` - Test requirements

5. **Notify**
   - Log creation in research log
   - Update deployment readiness checklist

**Checklist:**

- [ ] Theory file moved to `verified/missing/`
- [ ] Theory file updated with findings
- [ ] Upgrade folder created in `upgrades/active/`
- [ ] All 4 upgrade documents created
- [ ] Deployment readiness updated

---

### Trigger 2: Feature is IMPLEMENTED

**When:** Verification decision is IMPLEMENTED

**Automatic Actions:**

1. **Move theory file**
   ```bash
   mv unverified/[theory].md verified/implemented/[theory].md
   ```

2. **Update theory file**
   - Change status to "IMPLEMENTED ✅"
   - Add architecture documentation
   - Add code locations
   - Add usage examples

3. **Mark as deployment-ready**
   - Update deployment checklist
   - Log completion

**Checklist:**

- [ ] Theory file moved to `verified/implemented/`
- [ ] Theory file updated with architecture
- [ ] Code locations documented
- [ ] Usage examples provided
- [ ] Deployment readiness updated

---

### Trigger 3: Missing Feature Implemented

**When:** A missing feature has been implemented and tested

**Automatic Actions:**

1. **Move theory file**
   ```bash
   mv verified/missing/[feature].md verified/implemented/[feature].md
   ```

2. **Update theory file**
   - Change status to "IMPLEMENTED ✅"
   - Add final architecture documentation
   - Add implementation date

3. **Archive upgrade folder**
   ```bash
   mv upgrades/active/[feature]/ upgrades/completed/[feature]/
   ```

4. **Update deployment readiness**
   - Remove from missing list
   - Add to implemented list

**Checklist:**

- [ ] Theory file moved to `verified/implemented/`
- [ ] Upgrade folder archived to `upgrades/completed/`
- [ ] Final architecture documented
- [ ] Deployment readiness updated

---

## Quality Gates

### Gate 1: Research Completeness

**Before making verification decision, confirm:**

- [ ] All code search commands executed
- [ ] All test commands executed
- [ ] Manual verification performed (if no tests)
- [ ] Evidence compiled in research log
- [ ] Code snippets captured
- [ ] Test results captured

**If any checkbox unchecked, research is INCOMPLETE. Do not proceed to decision.**

---

### Gate 2: Evidence Quality

**Before making verification decision, confirm:**

- [ ] Evidence is specific (exact file paths, line numbers)
- [ ] Evidence is verifiable (others can reproduce)
- [ ] Evidence is recent (code still exists, tests still run)
- [ ] Evidence is complete (covers all components of feature)

**If any checkbox unchecked, gather more evidence.**

---

### Gate 3: Decision Justification

**Before finalizing decision, confirm:**

- [ ] Decision matches decision matrix
- [ ] Decision is based on evidence (not assumptions)
- [ ] Decision considers all components (API, workflow, database, tests)
- [ ] Decision is traceable (research log supports conclusion)

**If any checkbox unchecked, re-evaluate decision.**

---

### Gate 4: Documentation Completeness

**Before moving theory file, confirm:**

- [ ] Theory file has all required sections
- [ ] Research log is complete
- [ ] Evidence is documented
- [ ] Next steps are clear
- [ ] Deployment impact is assessed

**If any checkbox unchecked, complete documentation first.**

---

### Gate 5: Known Issues Check

**During testing and verification, check for critical bugs:**

- [ ] Feature tested manually (if applicable)
- [ ] Feature works as expected (no critical failures)
- [ ] All test failures documented in `KNOWN-ISSUES.md` (if found)
- [ ] Bug severity assessed (CRITICAL/HIGH/LOW)
- [ ] Investigation plan created for CRITICAL issues

**If CRITICAL bugs found:**
- Create issue in `KNOWN-ISSUES.md` immediately
- Document evidence, user impact, and investigation plan
- Mark feature as "IMPLEMENTED but BLOCKED" until resolved
- CRITICAL issues block deployment

**If HIGH/LOW bugs found:**
- Document in `KNOWN-ISSUES.md`
- Feature can still be marked IMPLEMENTED
- Bugs tracked for resolution before/after deployment

**Special Case: Feature Implemented but Critically Broken**

If feature code exists but has CRITICAL bugs:
- Verification decision: IMPLEMENTED ✅ (code exists)
- Known issues: CRITICAL 🔴 (blocks deployment)
- Both can be true simultaneously
- Deployment blocked until bug resolved OR feature disabled

---

## Sign-Off Process

### Researcher Sign-Off

**Required for:** Every verification decision

**Checklist:**

- [ ] I completed all research steps
- [ ] I executed all commands in the research plan
- [ ] I documented all findings in the research log
- [ ] I compiled evidence supporting the decision
- [ ] I followed the decision matrix
- [ ] I tested the feature (if IMPLEMENTED)
- [ ] I checked for critical bugs and documented in `KNOWN-ISSUES.md` (if found)
- [ ] I updated the theory file with findings
- [ ] I triggered appropriate auto-actions

**Signature:** [Name] | [Date]

---

### Reviewer Sign-Off (for MISSING decisions)

**Required for:** All MISSING decisions before creating upgrade plan

**Checklist:**

- [ ] I reviewed the research log
- [ ] I verified the evidence supports the decision
- [ ] I confirmed all components were checked
- [ ] I agree with the MISSING decision
- [ ] I approve creation of upgrade plan

**Signature:** [Name] | [Date]

---

## Workflow Summary

```
┌─────────────────────────┐
│ 1. PRE-VERIFICATION     │
│ ✓ Theory file complete  │
│ ✓ Research plan ready   │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 2. CODE SEARCH          │
│ ✓ Search all locations  │
│ ✓ Document findings     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 3. TEST EXECUTION       │
│ ✓ Run all tests         │
│ ✓ Document results      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 4. MANUAL VERIFICATION  │
│ ✓ Test manually         │
│ ✓ Verify functionality  │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 5. EVIDENCE COMPILATION │
│ ✓ Organize findings     │
│ ✓ Capture proof         │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 6. QUALITY GATES        │
│ ✓ Check completeness    │
│ ✓ Verify evidence       │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 7. DECISION             │
│ Implemented or Missing? │
└──────────┬──────────────┘
           │
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│IMPLEMEN│   │MISSING │
│TED     │   │        │
└────┬───┘   └───┬────┘
     │           │
     ▼           ▼
┌────────┐   ┌────────┐
│verified│   │verified│
│/implem│   │/missing│
│ented/  │   │        │
└────────┘   └───┬────┘
                 │
                 ▼
            ┌────────┐
            │upgrades│
            │/active/│
            └────────┘
```

---

## Common Mistakes to Avoid

1. **Skipping code search** - Always search all locations
2. **Assuming without testing** - Run the tests
3. **Partial evidence** - Gather complete proof
4. **Unclear decisions** - Use the decision matrix
5. **Incomplete documentation** - Fill all sections
6. **Manual steps without docs** - Document everything
7. **No reviewer for MISSING** - Get sign-off

---

## Quick Reference

**Starting research?**
→ Check Pre-Verification Requirements

**Found partial implementation?**
→ Treat as MISSING, document what's incomplete

**Tests failing?**
→ Feature is MISSING (broken)

**No tests found?**
→ Do manual verification

**Manual verification fails?**
→ Feature is MISSING (incomplete)

**Ready to decide?**
→ Use Decision Matrix

**Decided MISSING?**
→ Get reviewer sign-off before auto-trigger

---

**Last Updated:** 2025-10-20
**Version:** 1.0
