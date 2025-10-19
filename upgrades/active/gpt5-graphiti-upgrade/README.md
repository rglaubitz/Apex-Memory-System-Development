# OpenAI GPT-5 + graphiti-core 0.22.0 Upgrade

**Status:** 🔴 **CRITICAL - Active (Not Yet Started)**
**Priority:** High
**Timeline:** 3-4 days
**Blocking:** Week 2 Day 4 test failure

---

## TL;DR

**Problem:** Apex Memory System uses **non-existent OpenAI model names** (`gpt-4.1-mini`, `gpt-4.1-nano`) causing test failures and potential production issues.

**Solution:** Replace with correct models (`gpt-5-mini`, `gpt-5-nano`) and upgrade graphiti-core to 0.22.0.

**Impact:** 20+ files affected across codebase

**Risk:** HIGH - Affects LLM-powered entity extraction in production ingestion pipeline

---

## Quick Facts

| Aspect | Current | Target | Change |
|--------|---------|--------|--------|
| **Model Names** | gpt-4.1-mini/nano ❌ | gpt-5-mini/nano ✅ | CRITICAL FIX |
| **graphiti-core** | 0.20.4 | 0.22.0 | Upgrade |
| **Tests Passing** | 160/161 (99.4%) | 161/161 (100%) | +1 fix |
| **Files Affected** | 20+ | Same | Updates needed |

---

## Evidence

**Screenshot from Official OpenAI Platform Documentation (2025-10-19):**

✅ **Models that EXIST:**
- `gpt-5`
- `gpt-5-mini`
- `gpt-5-nano`
- `gpt-5-pro`

❌ **Models in our code (DO NOT EXIST):**
- `gpt-4.1-mini` ← Used in 3+ files
- `gpt-4.1-nano` ← Used in 3+ files

---

## Why This Matters

### Current Impact

1. **Test Failure:** `test_orphaned_episode_cleanup` failing
   ```
   Unsupported parameter: 'reasoning.effort' is not supported with this model
   ```

2. **False Documentation:** `GRAPHITI-OPTIMIZATION.md` states:
   > "GPT-4.1-mini/nano are correct, latest 2025 models"
   **This is INCORRECT**

3. **Version Mismatch:**
   - Installed: graphiti-core 0.20.4
   - requirements.txt: graphiti-core 0.21.0
   - Latest: graphiti-core 0.22.0

### Production Risk

If models don't exist:
- Entity extraction may fail silently
- Graphiti episodes won't be created
- Fallback to custom service (lower quality)
- Higher LLM API costs (retries)

---

## Affected Files

### Core Service Files (CRITICAL)

1. **`apex-memory-system/src/apex_memory/services/graphiti_service.py:64-65`**
   ```python
   llm_model: str = "gpt-4.1-mini",  # ← DOESN'T EXIST
   small_model: str = "gpt-4.1-nano",  # ← DOESN'T EXIST
   ```

2. **`apex-memory-system/src/apex_memory/services/graphiti_config.py:24,29`**
   ```python
   llm_model: str = Field(default="gpt-4.1-mini", ...)  # ← FIX
   small_model: str = Field(default="gpt-4.1-nano", ...)  # ← FIX
   ```

3. **`apex-memory-system/docs/GRAPHITI-OPTIMIZATION.md:31,233,261,291`**
   - Documents false claims about "GPT-4.1 being latest 2025 models"

### Configuration Files (16+ files)

All files with `llm_model` references need review:
- settings.py
- .env.example
- API route files
- Maintenance scripts
- Test files
- Documentation

---

## Expected Gains

### ✅ Immediate Fixes

- **Test Suite:** 161/161 passing (currently 160/161)
- **Model Names:** 100% valid OpenAI models
- **Documentation:** Accurate model references
- **graphiti-core:** Latest stable version

### ✅ Secondary Benefits

- **OpenTelemetry Support:** New in 0.22.0
- **Optimized Prompts:** Token reduction (0.22.0)
- **Better Summaries:** 8-sentence limit enforcement
- **Bug Fixes:** All 0.22.0 improvements

---

## Implementation Plan

### Phase 1: Model Name Updates (Day 1)

- ✅ Update `graphiti_service.py` → `gpt-5-mini`, `gpt-5-nano`
- ✅ Update `graphiti_config.py` → Correct defaults
- ✅ Update `GRAPHITI-OPTIMIZATION.md` → Remove false claims
- ✅ Search & replace across 16+ files

### Phase 2: graphiti-core Upgrade (Day 1-2)

- ✅ `pip install graphiti-core==0.22.0`
- ✅ Review breaking changes
- ✅ Test entity extraction quality
- ✅ Validate prompt changes

### Phase 3: Testing (Day 2-3)

- ✅ Graphiti baseline tests (11 tests)
- ✅ JSON temporal activities (5 tests)
- ✅ Integration tests (5 tests)
- ✅ Database writers (14 tests)
- ✅ Enhanced Saga baseline (126 tests)
- **Total:** 161 tests (100% passing)

### Phase 4: Integration Validation (Day 3)

- ✅ Real document ingestion tests
- ✅ Performance benchmarking
- ✅ Error monitoring

### Phase 5: Documentation (Day 3-4)

- ✅ Update all docs with correct models
- ✅ Fix examples and comments
- ✅ Remove false claims

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Entity extraction degraded | Medium | High | Benchmark before/after |
| Breaking changes in 0.22.0 | Medium | Medium | Test incrementally |
| Unexpected model behavior | Low | Medium | Diverse document tests |
| Test suite failures | Medium | High | Fix before continuing |

**Rollback Plan:** Documented in IMPROVEMENT-PLAN.md

---

## Timeline

**Target Start:** After Week 2 Day 5 completion
**Duration:** 3-4 days
**Target Complete:** Week 2 completion + 4 days

**Why Wait?** Don't fall behind on current work (Week 2 JSON Integration). This upgrade is critical but can wait 1-2 days for proper execution.

---

## Research Foundation

### Tier 1 Sources (Official Documentation)

1. **OpenAI Platform - Models**
   - https://platform.openai.com/docs/models
   - Screenshot verified: 2025-10-19
   - Models: gpt-5, gpt-5-mini, gpt-5-nano, gpt-5-pro

2. **graphiti-core 0.22.0 Release**
   - https://github.com/getzep/graphiti/releases
   - Published: 2025-10-13
   - Title: "OpenTelemetry Support; Bug fixes and improvements"

3. **graphiti-core PyPI**
   - https://pypi.org/project/graphiti-core/
   - Latest: 0.22.0

---

## Files in This Upgrade

```
gpt5-graphiti-upgrade/
├── README.md                  # ← You are here (Quick reference)
├── IMPROVEMENT-PLAN.md        # Complete implementation plan
└── PROGRESS.md                # Execution tracker (created when started)
```

---

## Next Steps

1. ✅ **Review this README** - Understand scope and impact
2. ✅ **Read IMPROVEMENT-PLAN.md** - Full implementation details
3. ⏸️ **Wait for Week 2 Day 5 completion** - Don't block current work
4. 🚀 **Execute upgrade** - Follow 5-phase plan

---

## Quick Links

- **Full Plan:** [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md)
- **Week 2 JSON Integration:** `../temporal-implementation/graphiti-json-integration/`
- **Test Artifacts:** `../temporal-implementation/tests/`
- **Graphiti Docs:** `../../apex-memory-system/docs/GRAPHITI-OPTIMIZATION.md`

---

**Document Version:** 1.0
**Created:** 2025-10-19
**Status:** Active - Ready to Execute After Week 2 Day 5
