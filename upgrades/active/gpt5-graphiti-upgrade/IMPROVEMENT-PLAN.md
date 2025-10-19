# OpenAI GPT-5 + graphiti-core 0.22.0 Upgrade - Comprehensive Plan

**Created:** 2025-10-19
**Status:** Active - Not Yet Started
**Priority:** **CRITICAL** - Blocking Issue
**Complexity:** High (20+ files affected)
**Timeline:** 3-4 days

---

## Executive Summary

This upgrade addresses **two critical dependencies** that were discovered during Week 2 Day 4 (JSON Temporal Activities) implementation:

1. **Invalid OpenAI Model Names:** Current codebase uses `gpt-4.1-mini` and `gpt-4.1-nano` which **DO NOT EXIST** in OpenAI's API
2. **graphiti-core Version:** Upgrade from 0.20.4 (installed) → 0.22.0 (latest stable)

**Current Impact:**
- ❌ `test_orphaned_episode_cleanup` failing with: `Unsupported parameter: 'reasoning.effort' is not supported with this model`
- ❌ Documentation states "GPT-4.1-mini/nano are correct, latest 2025 models" (INCORRECT)
- ❌ Version mismatch: requirements.txt specifies 0.21.0, but 0.20.4 installed

**Risk Level:** **HIGH** - Affects LLM-powered entity extraction across entire ingestion pipeline

---

## Current State Analysis

### Problem 1: Non-Existent Model Names

**Evidence from Official OpenAI Platform Documentation (Screenshot Verified 2025-10-19):**

✅ **Models that EXIST:**
- `gpt-5` (main model)
- `gpt-5-mini` (mid-tier)
- `gpt-5-nano` (fastest)
- `gpt-5-pro` (premium)

❌ **Models in our codebase (DO NOT EXIST):**
- `gpt-4.1-mini` (used in 3+ files)
- `gpt-4.1-nano` (used in 3+ files)

**Files Affected (Direct Model Names):**

1. **`src/apex_memory/services/graphiti_service.py`** (lines 64-65)
   ```python
   llm_model: str = "gpt-4.1-mini",
   small_model: str = "gpt-4.1-nano",
   ```

2. **`src/apex_memory/services/graphiti_config.py`** (lines 24, 29)
   ```python
   llm_model: str = Field(
       default="gpt-4.1-mini",
       description="Main LLM model for entity extraction"
   )

   small_model: str = Field(
       default="gpt-4.1-nano",
       description="Smaller/faster model for simple tasks"
   )
   ```

3. **`docs/GRAPHITI-OPTIMIZATION.md`** (lines 31, 233, 261, 291)
   - Documents these as "latest 2025 models" (INCORRECT)

**Files Affected (Configuration References):** 16+ files found with `llm_model` references

---

### Problem 2: graphiti-core Version Mismatch

**Current State:**
- **Installed:** 0.20.4
- **requirements.txt:** 0.21.0
- **Latest Stable:** 0.22.0 (Released Oct 13, 2025)

**0.22.0 Breaking Changes (from Release Notes):**

1. **Refactored Node Extraction**
   - Removed summary from attribute extraction
   - Shorter summaries (8-sentence limit enforced)

2. **Prompt Structure Changes**
   - Moved MESSAGES after instructions
   - Removed JSON indentation (token reduction)

3. **New Features**
   - OpenTelemetry distributed tracing support

4. **Bug Fixes and Improvements**
   - Character limit enforcement
   - Prevent meta-commentary in summaries

**Compatibility Risk:** Medium - Prompt changes may affect entity extraction quality

---

## Research Summary

### Official Sources (Tier 1)

1. **OpenAI Platform Documentation**
   - Source: https://platform.openai.com/docs/models
   - Verified: 2025-10-19 via screenshot
   - Models: gpt-5, gpt-5-mini, gpt-5-nano, gpt-5-pro

2. **graphiti-core 0.22.0 Release**
   - Source: https://github.com/getzep/graphiti/releases
   - Published: 2025-10-13
   - Title: "OpenTelemetry Support; Bug fixes and improvements"

3. **PyPI graphiti-core Package**
   - Source: https://pypi.org/project/graphiti-core/
   - Latest: 0.22.0
   - Previous: 0.21.0, 0.20.4

### Test Failure Root Cause

**Error:**
```
Unsupported parameter: 'reasoning.effort' is not supported with this model.
```

**Analysis:**
- The `reasoning.effort` parameter is ONLY supported by o-series reasoning models (o1-preview, o1-mini, o3, o4-mini)
- NOT supported by GPT-4.1 or GPT-5 series
- Test `test_orphaned_episode_cleanup` is likely using this parameter incorrectly

---

## Proposed Solution

### Phase 1: Model Name Updates (Day 1)

**Objective:** Replace all non-existent model references with correct OpenAI models

**Tasks:**

1. **Update Core Service Files** (1-2 hours)
   - `graphiti_service.py:64-65` → `gpt-5-mini`, `gpt-5-nano`
   - `graphiti_config.py:24,29` → `gpt-5-mini`, `gpt-5-nano`

2. **Update Documentation** (30 minutes)
   - `GRAPHITI-OPTIMIZATION.md` - Correct model names throughout
   - Remove claims about "GPT-4.1 being latest 2025 models"

3. **Search and Replace Across Codebase** (1-2 hours)
   - Find all 16+ files with `llm_model` references
   - Verify each usage
   - Update defaults, examples, comments

4. **Update Environment Files** (15 minutes)
   - `.env.example` - Correct model names
   - Configuration documentation

**Expected Changes:**
```diff
- llm_model: str = "gpt-4.1-mini",
- small_model: str = "gpt-4.1-nano",
+ llm_model: str = "gpt-5-mini",
+ small_model: str = "gpt-5-nano",
```

---

### Phase 2: graphiti-core Upgrade (Day 1-2)

**Objective:** Upgrade to 0.22.0 and validate compatibility

**Tasks:**

1. **Upgrade Package** (15 minutes)
   ```bash
   pip install graphiti-core==0.22.0
   pip freeze | grep graphiti-core >> requirements.txt
   ```

2. **Review Breaking Changes** (1 hour)
   - Read full 0.22.0 changelog
   - Identify affected code paths
   - Plan mitigation strategies

3. **Test Entity Extraction** (2-3 hours)
   - Run `test_graphiti_extraction_activity.py` (5 tests)
   - Run `test_graphiti_rollback.py` (6 tests)
   - Verify extraction quality hasn't degraded
   - Check for new warnings/errors

4. **Validate Prompt Changes** (1-2 hours)
   - Test with sample documents
   - Compare entity extraction before/after
   - Adjust if needed (8-sentence summary limit)

---

### Phase 3: Comprehensive Testing (Day 2-3)

**Objective:** Ensure zero breaking changes to existing functionality

**Test Suite Execution:**

1. **Graphiti Baseline Tests** (Expected: 11/11 passing)
   ```bash
   pytest tests/unit/test_graphiti_extraction_activity.py -v --no-cov
   pytest tests/unit/test_graphiti_rollback.py -v --no-cov
   ```

2. **JSON Temporal Activities** (Expected: 5/5 passing)
   ```bash
   pytest tests/unit/test_json_temporal_activities.py -v --no-cov
   ```

3. **Integration Tests** (Expected: 5/5 passing)
   ```bash
   pytest tests/integration/test_structured_data_saga.py -v --no-cov
   ```

4. **Database Writers** (Expected: 14/14 passing)
   ```bash
   pytest tests/unit/test_json_writer_*.py -v --no-cov
   ```

5. **Enhanced Saga Baseline** (Expected: 121/121 passing)
   ```bash
   pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v
   ```

**Total Expected:** 161 tests passing (11 + 5 + 5 + 14 + 126)

---

### Phase 4: Integration Validation (Day 3)

**Objective:** Test end-to-end document ingestion with real data

**Tasks:**

1. **Real Document Tests** (2-3 hours)
   - Upload PDF document (invoices, contracts)
   - Verify Graphiti episode creation
   - Check entity extraction quality
   - Validate Neo4j graph structure

2. **Performance Benchmarking** (1 hour)
   - Measure episode creation time
   - Compare before/after upgrade
   - Document any performance changes

3. **Error Monitoring** (1 hour)
   - Check logs for new warnings
   - Verify fallback behavior still works
   - Test failure scenarios

---

### Phase 5: Documentation Update (Day 3-4)

**Objective:** Update all documentation to reflect correct models

**Files to Update:**

1. **`GRAPHITI-OPTIMIZATION.md`**
   - Correct model names throughout
   - Update "Current Status" section
   - Remove false claims about GPT-4.1

2. **`IMPLEMENTATION.md`** (Week 2 JSON Integration)
   - Update model references
   - Correct any examples

3. **`README.md`** files
   - Search all READMEs for model references
   - Update examples

4. **Code Comments**
   - Update inline comments referencing models
   - Fix docstrings with outdated model names

---

## Implementation Phases

### Week 1: Model Name Fix + Upgrade

| Day | Phase | Tasks | Deliverable |
|-----|-------|-------|-------------|
| **Day 1** | Phase 1 | Model name updates (3 core files) | ✅ Correct model names |
| | Phase 2 | graphiti-core upgrade to 0.22.0 | ✅ Package upgraded |
| **Day 2** | Phase 3 | Run all test suites (161 tests) | ✅ 161/161 passing |
| | Phase 4 | Integration testing with real docs | ✅ E2E validated |
| **Day 3** | Phase 5 | Documentation updates | ✅ Docs corrected |

### Week 2: Return to JSON Integration (Week 2 Day 5)

| Day | Phase | Tasks | Deliverable |
|-----|-------|-------|-------------|
| **Day 1** | Week 2 Day 5 | Integration testing (Samsara, Turvo, FrontApp) | ✅ Day 5 complete |
| **Day 2-5** | Week 3 | Staging Lifecycle implementation | Continue per plan |

---

## Expected Outcomes

### Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Model Names Valid | ❌ 0/2 | ✅ 2/2 | 100% |
| graphiti-core Version | 0.20.4 | 0.22.0 | Latest stable |
| Graphiti Tests Passing | 10/11 | 11/11 | 100% |
| Total Tests Passing | 160/161 | 161/161 | 100% |
| Documentation Accurate | ~60% | 100% | 100% |

### Quality Gates

✅ **Phase 1 Complete When:**
- All 3 core files updated with correct model names
- No references to gpt-4.1-* anywhere in codebase

✅ **Phase 2 Complete When:**
- graphiti-core 0.22.0 installed
- Requirements.txt updated
- No breaking changes detected

✅ **Phase 3 Complete When:**
- All 161 tests passing (100%)
- Zero new warnings or errors
- Performance benchmarks stable

✅ **Phase 4 Complete When:**
- Real document ingestion works
- Entity extraction quality maintained/improved
- Neo4j graph structure correct

✅ **Phase 5 Complete When:**
- All documentation accurate
- No false claims about model names
- Examples updated throughout

---

## Risk Mitigation

### Risk 1: Entity Extraction Quality Degradation

**Likelihood:** Medium
**Impact:** High
**Mitigation:**
- Benchmark extraction quality before upgrade
- Compare results after upgrade
- Adjust prompt parameters if needed
- Fallback to 0.21.0 if critical regression

### Risk 2: Breaking Changes in 0.22.0

**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- Review full changelog before upgrade
- Test incrementally (unit → integration → E2E)
- Document any behavioral changes
- Keep 0.20.4 backup if rollback needed

### Risk 3: Unexpected Model Behavior

**Likelihood:** Low
**Impact:** Medium
**Mitigation:**
- GPT-5 models are stable and released
- Test with diverse document types
- Monitor LLM API costs (may differ)
- Validate entity extraction accuracy

### Risk 4: Test Suite Failures

**Likelihood:** Medium
**Impact:** High
**Mitigation:**
- Fix test failures before continuing
- Document root causes
- Update test expectations if justified
- Never skip failing tests

---

## Rollback Plan

**If Critical Issues Arise:**

1. **Revert Model Names** (if GPT-5 models fail)
   ```bash
   # Unlikely - GPT-5 models are official
   # But documented for completeness
   ```

2. **Downgrade graphiti-core** (if 0.22.0 breaks functionality)
   ```bash
   pip install graphiti-core==0.20.4
   # Re-run tests
   # Document regression
   ```

3. **Restore Documentation** (via git)
   ```bash
   git checkout HEAD -- docs/GRAPHITI-OPTIMIZATION.md
   ```

---

## References

### Official Documentation (Tier 1)

1. **OpenAI Platform - Models**
   - URL: https://platform.openai.com/docs/models
   - Verified: 2025-10-19 (screenshot evidence)
   - Models: gpt-5, gpt-5-mini, gpt-5-nano, gpt-5-pro

2. **graphiti-core 0.22.0 Release Notes**
   - URL: https://github.com/getzep/graphiti/releases
   - Published: 2025-10-13
   - Breaking Changes: Prompt refactoring, summary limits

3. **graphiti-core PyPI**
   - URL: https://pypi.org/project/graphiti-core/
   - Latest: 0.22.0
   - Installation: `pip install graphiti-core==0.22.0`

### Internal Documentation

1. **Week 2 Day 4 Implementation**
   - Location: `upgrades/active/temporal-implementation/graphiti-json-integration/`
   - Files: `IMPLEMENTATION.md`, `PROGRESS.md`

2. **Graphiti Optimization Guide**
   - Location: `apex-memory-system/docs/GRAPHITI-OPTIMIZATION.md`
   - Status: Requires correction (false model claims)

3. **Test Failure Analysis**
   - Test: `test_orphaned_episode_cleanup`
   - Error: `Unsupported parameter: 'reasoning.effort'`
   - Root Cause: Non-existent model names

---

## Next Steps (Immediate)

1. ✅ **Upgrade project created** - This document
2. ⏸️ **Mark as "Active - Not Yet Started"** - Don't block Week 2 Day 5
3. 📋 **Complete Week 2 Day 5** - Integration testing (Samsara, Turvo, FrontApp JSON)
4. 🚀 **Execute this upgrade** - After Week 2 completion

**Rationale:** Don't fall behind on current work. This upgrade is critical but can wait 1-2 days for proper scoping.

---

**Document Version:** 1.0
**Last Updated:** 2025-10-19
**Next Review:** Before Phase 1 execution
