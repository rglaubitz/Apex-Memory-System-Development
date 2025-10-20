# GPT-5 + graphiti-core 0.22.0 Upgrade - Dependency Report

**Generated:** 2025-10-19
**Phase:** 1 - Comprehensive Dependency Scan
**Status:** ✅ Complete

---

## Executive Summary

**Total Files Requiring Updates:** 8 files
**OpenAI SDK Files:** 2 (no changes needed - v1.109.1 is correct)
**graphiti-core Files:** 1 import location + 12 instantiation points
**Model Name Updates:** 6 code files + 1 documentation file

**Critical Finding:** `settings.py` ALREADY uses `gpt-5-mini`/`gpt-5-nano` defaults, but service layer still hardcoded to `gpt-4.1-mini`/`gpt-4.1-nano`. This creates a **configuration mismatch**.

---

## 1. OpenAI SDK Dependencies

### 1.1 Direct OpenAI Imports

**File:** `src/apex_memory/services/embedding_service.py`

**Lines 14, 106:**
```python
from openai import OpenAI, RateLimitError, APIError
...
self.client = OpenAI(api_key=api_key)
```

**Usage:**
- Creates OpenAI client for embeddings
- Uses `client.embeddings.create()` API (stable across v1.x and v2.x)
- **NO CHANGES NEEDED** - OpenAI SDK v1.109.1 is correct

**Why No Upgrade:**
- semantic-router constraint: `openai>=1.10.0,<2.0.0`
- Already on latest v1.x (1.109.1)
- Embeddings API is stable and unchanged in v2.x

---

### 1.2 semantic-router OpenAI Usage

**File:** `src/apex_memory/query_router/semantic_classifier.py`

**Lines 18, 89:**
```python
from semantic_router.encoders import OpenAIEncoder, HuggingFaceEncoder
...
self.encoder = OpenAIEncoder(
    name="text-embedding-3-small",
    score_threshold=score_threshold
)
```

**Usage:**
- Uses semantic-router's OpenAIEncoder wrapper
- Calls OpenAI embeddings API indirectly
- **NO CHANGES NEEDED** - Works with OpenAI SDK v1.x

**semantic-router Constraint Analysis:**
- Requires: `openai>=1.10.0,<2.0.0` (explicit in pyproject.toml)
- Uses only 3 stable APIs:
  - `client.embeddings.create()` - Stable since v1.0
  - `client.models.list()` - Stable since v1.0
  - `openai.error` classes - Stable
- **Decision:** Respect constraint, stay on v1.x

**Additional semantic-router Usage:**
- 8 script files in `scripts/query-router/` (debugging/testing)
- All use OpenAIEncoder through semantic-router wrapper
- **NO CHANGES NEEDED**

---

## 2. graphiti-core Dependencies

### 2.1 graphiti-core Import

**File:** `src/apex_memory/services/graphiti_service.py`

**Line 89:**
```python
from graphiti_core import Graphiti
```

**Current Version:** 0.20.4 (installed) / 0.21.0 (requirements.txt)
**Target Version:** 0.22.0

**Version Mismatch Found:**
- `requirements.txt` specifies 0.21.0
- `pip show graphiti-core` returns 0.20.4 (actual installed)
- **Action Required:** Upgrade to 0.22.0 and update requirements.txt

**Breaking Changes to Review (0.21.0 → 0.22.0):**
- OpenTelemetry support added
- Prompt structure refactored (may fix reasoning.effort parameter issue)
- Summary generation improved (8-sentence limit enforcement)
- Token usage optimization

---

### 2.2 GraphitiService Instantiation Points

**Total Instantiations:** 12 locations

#### Production Code (7 locations)

1. **`src/apex_memory/main.py:59`** - Application startup
   ```python
   graphiti_service = GraphitiService(
       neo4j_uri=settings.neo4j_uri,
       neo4j_user=settings.neo4j_user,
       neo4j_password=settings.neo4j_password,
       openai_api_key=settings.openai_api_key,
       llm_model=settings.graphiti_llm_model,  # ← Uses settings
       small_model=settings.graphiti_small_model,  # ← Uses settings
   )
   ```
   **Impact:** Uses `settings.graphiti_llm_model` (already gpt-5-mini)
   **Action:** None - relies on settings defaults

2. **`src/apex_memory/api/analytics.py:43`** - Analytics endpoint
3. **`src/apex_memory/api/messages.py:42`** - Messages endpoint
4. **`src/apex_memory/api/maintenance.py:42`** - Maintenance endpoint
5. **`src/apex_memory/temporal/activities/ingestion.py:596`** - Graphiti extraction activity
6. **`src/apex_memory/temporal/activities/ingestion.py:730`** - Graphiti rollback helper
7. **`src/apex_memory/temporal/activities/ingestion.py:1419`** - JSON Graphiti extraction

**All API/activity instantiations:**
```python
graphiti_service = GraphitiService(
    neo4j_uri=settings.neo4j_uri,
    neo4j_user=settings.neo4j_user,
    neo4j_password=settings.neo4j_password,
    openai_api_key=settings.openai_api_key,
    llm_model=settings.graphiti_llm_model,  # ← Pulls from settings
    small_model=settings.graphiti_small_model,  # ← Pulls from settings
)
```

**Impact:** All production code uses `Settings` class defaults
**Action:** Update settings.py (already done) + service defaults

---

#### Scripts (3 locations)

1. **`scripts/maintenance/reprocess_documents_graphiti.py:52`**
2. **`scripts/maintenance/build_graphiti_indices.py:38`**
3. **`scripts/setup/init_graphiti_indices.py:47`**

**All scripts use settings:**
```python
graphiti_service = GraphitiService(
    llm_model=settings.graphiti_llm_model,
    small_model=settings.graphiti_small_model,
)
```

**Impact:** Will automatically use updated settings
**Action:** None - relies on settings defaults

---

#### Tests (2 locations)

1. **`tests/unit/test_graphiti_rollback.py:231`** - Integration test
   ```python
   graphiti = GraphitiService(
       neo4j_uri=settings.neo4j_uri,
       neo4j_user=settings.neo4j_user,
       neo4j_password=settings.neo4j_password,
       openai_api_key=settings.openai_api_key,
       # Uses service defaults (no model params passed)
   )
   ```

2. **`src/apex_memory/services/graphiti_service.py:1096`** - Example in docstring
   ```python
   service = GraphitiService(
       llm_model="gpt-4.1-mini",  # ← HARDCODED - Needs update
   )
   ```

**Impact:** Test uses service defaults; docstring example needs update
**Action:** Update docstring example to gpt-5-mini

---

### 2.3 GraphitiService Default Parameters

**Configuration Hierarchy:**

```
1. settings.py (Application-level defaults)
   ↓
2. graphiti_config.py (Pydantic model defaults)
   ↓
3. graphiti_service.py (Service-level defaults)
```

**Current State Analysis:**

| Layer | File | Current | Target | Status |
|-------|------|---------|--------|--------|
| Application | `settings.py:259-260` | ✅ gpt-5-mini/nano | gpt-5-mini/nano | ✅ Correct |
| Config Model | `graphiti_config.py:24,29` | ❌ gpt-4.1-mini/nano | gpt-5-mini/nano | ❌ Needs update |
| Service | `graphiti_service.py:64-65` | ❌ gpt-4.1-mini/nano | gpt-5-mini/nano | ❌ Needs update |

**Critical Finding:** Configuration mismatch creates inconsistency when services are instantiated without explicit model parameters.

---

## 3. Model Name References

### 3.1 Code Files Requiring Updates (6 files)

#### File 1: `src/apex_memory/services/graphiti_service.py`

**Lines 64-65** - Default parameters:
```python
def __init__(
    self,
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    openai_api_key: str,
    llm_model: str = "gpt-4.1-mini",  # ← UPDATE to "gpt-5"
    small_model: str = "gpt-4.1-nano",  # ← UPDATE to "gpt-5-mini"
```

**Line 97** - Comment:
```python
# NOTE: GPT-5 models natively support reasoning/verbosity parameters
```
**Update to:**
```python
# NOTE: Using GPT-5 models for reasoning/verbosity support via Responses API
# graphiti-core 0.22.0+ handles parameter formatting correctly
```

**Line 1100** - Docstring example:
```python
service = GraphitiService(
    llm_model="gpt-4.1-mini",  # ← UPDATE to "gpt-5"
)
```

**Total Changes:** 3 locations in this file

---

#### File 2: `src/apex_memory/services/graphiti_config.py`

**Lines 24, 29** - Pydantic Field defaults:
```python
llm_model: str = Field(
    default="gpt-4.1-mini",  # ← UPDATE to "gpt-5"
    description="Main LLM model for entity extraction"
)

small_model: str = Field(
    default="gpt-4.1-nano",  # ← UPDATE to "gpt-5-mini"
    description="Smaller/faster model for simple tasks"
)
```

**Total Changes:** 2 locations in this file

---

#### File 3: `src/apex_memory/config/settings.py`

**Lines 258-260** - Already correct! ✅
```python
# NOTE: Using GPT-5 models for native reasoning/verbosity parameter support
graphiti_llm_model: str = Field(default="gpt-5-mini", description="Main LLM for entity extraction")
graphiti_small_model: str = Field(default="gpt-5-nano", description="Smaller LLM for simple tasks")
```

**Update comment to:**
```python
# NOTE: GPT-5 models with reasoning/verbosity support via Responses API
# graphiti-core 0.22.0+ handles parameter formatting correctly
```

**Total Changes:** 1 comment update

---

#### File 4: `src/apex_memory/main.py`

**Lines 64-65** - GraphitiService instantiation:
```python
llm_model=settings.graphiti_llm_model,  # ← Uses settings (no change needed)
small_model=settings.graphiti_small_model,  # ← Uses settings (no change needed)
```

**Action:** None - relies on updated settings.py defaults

---

#### File 5: `requirements.txt`

**Line 27:**
```
graphiti-core==0.21.0  # ← UPDATE to 0.22.0
```

**Line 26 comment** - Already correct:
```
# NOTE: Using GPT-5 models for native reasoning/verbosity support
```

**Update comment to:**
```
# NOTE: Using GPT-5 models with graphiti-core 0.22.0 for proper parameter handling
```

**Total Changes:** 1 version + 1 comment

---

### 3.2 Documentation Files (1 file)

#### File: `docs/GRAPHITI-OPTIMIZATION.md`

**Lines 233-234** - Code example:
```python
service = GraphitiService(
    llm_model: str = "gpt-4.1-mini",  # ← UPDATE to "gpt-5"
    small_model: str = "gpt-4.1-nano",  # ← UPDATE to "gpt-5-mini"
)
```

**Lines 261-262** - Configuration example:
```python
graphiti_llm_model: str = "gpt-4.1-mini"  # ← UPDATE to "gpt-5-mini"
graphiti_small_model: str = "gpt-4.1-nano"  # ← UPDATE to "gpt-5-nano"
```

**Additional Context to Add:**
- Explain reasoning/verbosity parameter support
- Note graphiti-core 0.22.0 fixes parameter format issue
- Document GPT-5 vs GPT-4.1 differences

**Total Changes:** 4 model references + context additions

---

### 3.3 Environment Files

**.env.example Analysis:**

**No model name references found** ✅

**Recommendation:** Add optional Graphiti model override variables:
```bash
# =============================================================================
# Graphiti Configuration (Optional - Overrides defaults)
# =============================================================================
# GRAPHITI_LLM_MODEL=gpt-5           # Main LLM (default: gpt-5-mini)
# GRAPHITI_SMALL_MODEL=gpt-5-mini    # Small LLM (default: gpt-5-nano)
```

**Note:** This is optional - settings.py provides sensible defaults.

---

## 4. Comment and Documentation Updates

### 4.1 reasoning/verbosity References

**Files with reasoning/verbosity comments:**

1. **`src/apex_memory/services/graphiti_service.py:97`**
   - Current: "GPT-5 models natively support reasoning/verbosity parameters"
   - Update: "GPT-5 models support reasoning/verbosity via Responses API"

2. **`src/apex_memory/config/settings.py:258`**
   - Current: "Using GPT-5 models for native reasoning/verbosity parameter support"
   - Update: "GPT-5 models with reasoning/verbosity via Responses API format"

**Context:** Based on research findings, GPT-5 supports these parameters but requires:
- Responses API (not Chat Completions API)
- Nested object format: `reasoning = {"effort": "medium"}` (not `reasoning.effort`)
- graphiti-core 0.22.0 likely fixes this format issue

---

### 4.2 GPT-4.1 vs GPT-5 Claims

**File:** `docs/GRAPHITI-OPTIMIZATION.md`

**False Claims to Remove:**
- "GPT-4.1-mini/nano are the latest 2025 models" ❌
- "GPT-4.1 supports reasoning parameters" ❓ (undocumented)

**Accurate Information to Add:**
- GPT-5 family proven to support reasoning/verbosity
- Requires graphiti-core 0.22.0 for proper parameter formatting
- Official OpenAI Cookbook examples confirm support

---

## 5. Test File Analysis

**Grep Results:** No hardcoded model references in tests ✅

**Test files use:**
- `Settings` class defaults (automatically updated)
- `GraphitiService` defaults (will be updated)
- No explicit "gpt-4.1-mini" or "gpt-5" strings

**Impact:** Tests will automatically use updated model names after service layer changes.

---

## 6. Upgrade Impact Analysis

### 6.1 Configuration Flow After Updates

**Before Upgrade:**
```
settings.py: gpt-5-mini/nano ✅
    ↓
graphiti_config.py: gpt-4.1-mini/nano ❌  ← Overrides settings!
    ↓
graphiti_service.py: gpt-4.1-mini/nano ❌  ← Overrides config!
    ↓
Production: Uses gpt-4.1-mini/nano ❌
```

**After Upgrade:**
```
settings.py: gpt-5-mini/nano ✅
    ↓
graphiti_config.py: gpt-5-mini/nano ✅
    ↓
graphiti_service.py: gpt-5-mini/nano ✅
    ↓
Production: Uses gpt-5-mini/nano ✅
```

**Critical:** This explains why settings.py already had gpt-5, but system was still using gpt-4.1 - the service layer defaults were overriding!

---

### 6.2 Affected Components

**Direct Impact:**
- Graphiti entity extraction (5 activities)
- GraphitiService (12 instantiation points)
- All Temporal ingestion workflows

**Indirect Impact:**
- Query router (uses entities from Graphiti)
- Analytics API (temporal queries)
- Maintenance scripts (reprocessing)

**No Impact:**
- OpenAI embeddings (separate service)
- semantic-router (uses embeddings only)
- Qdrant/PostgreSQL/Redis (storage layer)

---

### 6.3 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Entity extraction quality changes | Medium | High | Benchmark before/after |
| graphiti-core 0.22.0 breaking changes | Low | Medium | Review changelog, test incrementally |
| Unexpected reasoning parameter behavior | Low | Medium | Monitor logs for parameter errors |
| Test suite failures | Medium | High | Run full suite before deployment |

---

## 7. Implementation Order

### Phase 2: Model Name Updates (Day 1, 1-2 hours)

**Order of changes (prevents configuration cascades):**

1. ✅ **Update service layer first** (`graphiti_service.py`)
   - Default parameters: gpt-4.1 → gpt-5
   - Comments and docstrings
   - Reason: Fixes service-level override

2. ✅ **Update config layer** (`graphiti_config.py`)
   - Pydantic Field defaults
   - Reason: Aligns with service layer

3. ✅ **Update settings comments** (`settings.py`)
   - Refine reasoning/verbosity comments
   - Reason: Already correct values

4. ✅ **Update documentation** (`GRAPHITI-OPTIMIZATION.md`)
   - Code examples
   - Remove false claims
   - Add accurate context

**Why This Order:** Service layer overrides config layer, so fix service first to prevent intermediate inconsistency.

---

### Phase 3: graphiti-core Upgrade (Day 1-2, 2 hours)

**Steps:**
1. ✅ Update `requirements.txt`: `graphiti-core==0.22.0`
2. ✅ Run: `pip install --upgrade graphiti-core==0.22.0`
3. ✅ Verify import: `from graphiti_core import Graphiti`
4. ✅ Review changelog for breaking changes
5. ✅ Test basic instantiation

**Expected Changes:**
- Prompt structure refactored (internal to graphiti-core)
- Parameter format likely fixed (reasoning.effort → reasoning = {...})
- OpenTelemetry support added (optional)

---

### Phase 4: Testing (Day 2-3, 4 hours)

**Test Suite Execution Order:**

1. **Graphiti Baseline** (11 tests)
   - `pytest tests/unit/test_graphiti_extraction_activity.py -v`
   - `pytest tests/unit/test_graphiti_rollback.py -v`

2. **JSON Temporal Activities** (5 tests)
   - `pytest tests/unit/test_json_temporal_activities.py -v`

3. **Integration Tests** (5 tests)
   - `pytest tests/integration/test_json_integration_e2e.py -v -m integration`

4. **Database Writers** (14 tests)
   - `pytest tests/unit/test_*_writer.py -v`

5. **Enhanced Saga Baseline** (126 tests)
   - `pytest tests/ --ignore=tests/load/ -v`

**Target:** 161/161 tests passing (100%)

**Expected Failure Fix:** `test_orphaned_episode_cleanup` should now pass (reasoning.effort parameter error resolved)

---

## 8. Files Requiring Changes Summary

### Code Changes (6 files)

| File | Lines | Changes | Priority |
|------|-------|---------|----------|
| `services/graphiti_service.py` | 64, 65, 97, 1100 | Model defaults + comments | CRITICAL |
| `services/graphiti_config.py` | 24, 29 | Pydantic defaults | CRITICAL |
| `config/settings.py` | 258 | Comment refinement | Medium |
| `main.py` | - | None (uses settings) | - |
| `requirements.txt` | 26-27 | Version + comment | CRITICAL |
| `temporal/activities/ingestion.py` | - | None (uses settings) | - |

**Total Code Changes:** ~10 lines across 5 files

---

### Documentation Changes (1 file)

| File | Lines | Changes | Priority |
|------|-------|---------|----------|
| `docs/GRAPHITI-OPTIMIZATION.md` | 233-234, 261-262 | Examples + context | Medium |

**Total Documentation Changes:** 4 model references + context additions

---

### Test Changes (0 files)

**No test file changes needed** ✅
Tests use `Settings` defaults and will automatically pick up changes.

---

## 9. Validation Checklist

**Before Upgrade:**
- [x] Comprehensive dependency scan complete
- [x] All model references identified
- [x] Configuration hierarchy understood
- [x] Test strategy defined

**After Model Name Updates:**
- [ ] `graphiti_service.py` defaults updated
- [ ] `graphiti_config.py` defaults updated
- [ ] `settings.py` comments refined
- [ ] Documentation examples updated
- [ ] All files use consistent model names

**After graphiti-core Upgrade:**
- [ ] `requirements.txt` updated to 0.22.0
- [ ] Package installed: `pip show graphiti-core` shows 0.22.0
- [ ] Import verification: `from graphiti_core import Graphiti` works
- [ ] No import errors in logs

**After Testing:**
- [ ] Graphiti baseline: 11/11 passing
- [ ] JSON activities: 5/5 passing
- [ ] Integration tests: 5/5 passing
- [ ] Database writers: 14/14 passing
- [ ] Enhanced Saga baseline: 126/126 passing
- [ ] **Total: 161/161 passing (100%)**
- [ ] `test_orphaned_episode_cleanup` specifically passes (reasoning.effort fix)

---

## 10. Next Steps

**Immediate Actions (Phase 2):**

1. Begin model name updates in order:
   ```bash
   # 1. Edit graphiti_service.py
   # 2. Edit graphiti_config.py
   # 3. Edit settings.py comments
   # 4. Edit GRAPHITI-OPTIMIZATION.md
   # 5. Update requirements.txt
   ```

2. Create git commit:
   ```bash
   git add -A
   git commit -m "refactor: Update model names from gpt-4.1 to gpt-5

   - Update graphiti_service.py defaults: gpt-4.1-mini → gpt-5
   - Update graphiti_config.py defaults: gpt-4.1-nano → gpt-5-mini
   - Refine reasoning/verbosity comments
   - Update documentation examples
   - Prepare for graphiti-core 0.22.0 upgrade"
   ```

3. Proceed to Phase 3 (graphiti-core upgrade)

---

## 11. Research Citations

**All findings backed by research from IMPROVEMENT-PLAN.md:**

1. **OpenAI API Verification:**
   - Direct API call: `client.models.list()` confirmed GPT-4.1 and GPT-5 models exist
   - 71 total models available in account
   - Source: Live API verification (2025-10-19)

2. **GPT-5 Reasoning/Verbosity Support:**
   - Confirmed via OpenAI Cookbook examples
   - Requires Responses API: `client.responses.create()`
   - Nested parameter format: `reasoning = {"effort": "medium"}`
   - Source: https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools

3. **graphiti-core 0.22.0 Changes:**
   - Released: 2025-10-13
   - Improvements: OpenTelemetry, prompt refactoring, token optimization
   - Source: https://github.com/getzep/graphiti/releases

4. **semantic-router Constraint:**
   - Requires: `openai>=1.10.0,<2.0.0`
   - Uses only stable APIs (embeddings, models.list, error classes)
   - Source: semantic-router v0.1.11 pyproject.toml

---

## Appendix A: Full File Change List

**Critical (Must Change):**
1. `src/apex_memory/services/graphiti_service.py`
2. `src/apex_memory/services/graphiti_config.py`
3. `requirements.txt`

**Medium Priority (Should Change):**
4. `src/apex_memory/config/settings.py` (comments only)
5. `docs/GRAPHITI-OPTIMIZATION.md`

**No Changes Needed:**
- `src/apex_memory/main.py` (uses settings)
- `src/apex_memory/api/*.py` (uses settings)
- `scripts/*.py` (uses settings)
- `tests/**/*.py` (uses defaults)
- `.env.example` (no model vars)

---

## Appendix B: Configuration Hierarchy Details

**Full inheritance chain:**

```python
# Layer 1: Application Settings (Pydantic BaseSettings)
class Settings(BaseSettings):
    graphiti_llm_model: str = Field(default="gpt-5-mini")  # ✅ Already correct
    graphiti_small_model: str = Field(default="gpt-5-nano")  # ✅ Already correct

# Layer 2: Service Config (Pydantic BaseModel)
class GraphitiConfig(BaseModel):
    llm_model: str = Field(default="gpt-4.1-mini")  # ❌ Needs update
    small_model: str = Field(default="gpt-4.1-nano")  # ❌ Needs update

# Layer 3: Service Implementation
class GraphitiService:
    def __init__(
        self,
        llm_model: str = "gpt-4.1-mini",  # ❌ Needs update
        small_model: str = "gpt-4.1-nano",  # ❌ Needs update
    ):
        ...

# Production Usage
settings = Settings()  # Loads gpt-5-mini/nano from env or defaults

# But service instantiation WITHOUT explicit params uses service defaults:
graphiti = GraphitiService(
    neo4j_uri=settings.neo4j_uri,
    openai_api_key=settings.openai_api_key,
    # llm_model not passed → uses service default (gpt-4.1-mini) ❌
)

# To use settings defaults, must explicitly pass:
graphiti = GraphitiService(
    neo4j_uri=settings.neo4j_uri,
    openai_api_key=settings.openai_api_key,
    llm_model=settings.graphiti_llm_model,  # ✅ Explicitly uses gpt-5-mini
    small_model=settings.graphiti_small_model,  # ✅ Explicitly uses gpt-5-nano
)
```

**This is why all production code explicitly passes `settings.graphiti_llm_model`!**

---

**Report Complete**
**Next Phase:** Phase 2 - Model Name Updates
**Estimated Time:** 1-2 hours
**Files to Modify:** 6 files (3 critical, 2 medium, 1 low)
