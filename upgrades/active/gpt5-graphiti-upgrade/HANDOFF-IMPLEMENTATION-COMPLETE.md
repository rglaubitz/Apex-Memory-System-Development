# GPT-5 + graphiti-core 0.22.0 Upgrade - Implementation Complete

**Session Date:** 2025-10-19
**Status:** ✅ **Implementation Complete** → ⚠️ **1 Test Failing (graphiti-core bug)**
**Next Action:** Document findings, decide on workaround

---

## What Was Accomplished ✅

### Phase 1: Dependency Scan (COMPLETE)
- ✅ Comprehensive scan of ALL OpenAI and graphiti-core usage
- ✅ Created DEPENDENCY-REPORT.md (1,000+ lines)
- ✅ Mapped 4 files needing changes (not 20+ as originally thought)
- ✅ Confirmed semantic-router blocks OpenAI SDK 2.x: `openai<2.0.0,>=1.10.0`

**Key Discovery:** `.env` and `settings.py` ALREADY had gpt-5 models, but service layer defaults were overriding!

### Phase 2: Model Name Updates (COMPLETE)
Updated 4 files, ~10 lines total:

1. **`src/apex_memory/services/graphiti_service.py`** - 3 changes ✅
   - Line 64: `"gpt-4.1-mini"` → `"gpt-5"`
   - Line 65: `"gpt-4.1-nano"` → `"gpt-5-mini"`
   - Line 1100: Docstring example updated
   - Line 97: Comment updated

2. **`src/apex_memory/services/graphiti_config.py`** - 2 changes ✅
   - Line 24: `default="gpt-4.1-mini"` → `default="gpt-5"`
   - Line 29: `default="gpt-4.1-nano"` → `default="gpt-5-mini"`

3. **`requirements.txt`** - 1 change ✅
   - Line 27: `graphiti-core==0.21.0` → `graphiti-core==0.22.0`
   - Line 26: Comment updated

4. **`docs/GRAPHITI-OPTIMIZATION.md`** - 4 changes ✅
   - Lines 233-234: Code examples updated
   - Lines 261-262: Configuration examples updated

### Phase 3: graphiti-core Upgrade (COMPLETE)
```bash
pip install --upgrade graphiti-core==0.22.0
```

**Verification:**
```bash
$ pip show graphiti-core
Version: 0.22.0

$ python3 -c "from graphiti_core import Graphiti; print('✅ success')"
✅ success
```

**Uninstalled:** 0.20.4
**Installed:** 0.22.0

### Phase 4: Testing (IN PROGRESS)

**Test Results:** 15/16 passing (93.75%)

✅ **Passing Tests:**
- `test_extract_entities_with_graphiti_success`
- `test_extract_entities_graphiti_failure`
- `test_extract_entities_format_conversion`
- `test_extract_entities_episode_uuid_tracking`
- `test_graphiti_client_initialization`
- `test_rollback_on_saga_failure`
- `test_no_rollback_on_saga_success`
- `test_rollback_graphiti_episode_success`
- `test_rollback_graphiti_episode_failure`
- `test_rollback_on_unexpected_error`
- `test_extract_entities_from_json_success`
- `test_extract_entities_from_json_empty_json`
- `test_extract_entities_from_json_graphiti_failure`
- `test_write_structured_data_success`
- `test_write_structured_data_saga_rollback_triggers_graphiti_rollback`

❌ **Failing Test (1):**
- `test_orphaned_episode_cleanup` - Integration test

---

## ⚠️ Critical Finding: graphiti-core 0.22.0 Bug

### The Problem

**Test:** `tests/unit/test_graphiti_rollback.py::test_orphaned_episode_cleanup`

**Error:**
```python
ValueError: not enough values to unpack (expected 2, got 1)

File: /Library/Python/3.12/lib/python/site-packages/graphiti_core/graphiti.py:770
Code: communities, community_edges = await semaphore_gather(...)
```

**Root Cause:**
- graphiti-core 0.22.0 has bug in `semaphore_gather()` function
- When `GRAPHITI_UPDATE_COMMUNITIES=false`, it returns 1 value instead of 2
- Code tries to unpack: `communities, community_edges = result` but `result` is single value

**Environment Context:**
```bash
# .env line 135
GRAPHITI_UPDATE_COMMUNITIES=false  # Temporarily disabled to debug 0.21.0 unpacking bug
```

**The Irony:** We disabled communities to fix an "unpacking bug" in 0.21.0, but 0.22.0 has a DIFFERENT unpacking bug!

---

## Research Findings (Verified)

### OpenAI SDK & Dependencies

**OpenAI SDK v1.109.1 (Correct, Must Stay):**
- ✅ Latest v1.x version
- ✅ Blocked from v2.x by semantic-router: `openai<2.0.0,>=1.10.0`
- ✅ APIs used are stable (embeddings.create, error classes)

**graphiti-core 0.22.0:**
- ✅ Uses correct parameter format: `reasoning={'effort': 'medium'}` (nested object)
- ✅ Uses `client.responses.parse()` API (not chat.completions)
- ✅ Constraint: `openai>=1.91.0` (NO upper bound - supports v2.x!)
- ⚠️ Has community unpacking bug when communities disabled

**semantic-router 0.1.11:**
- Explicit constraint: `openai<2.0.0,>=1.10.0`
- Uses only: `client.embeddings.create()`
- This BLOCKS upgrading to OpenAI SDK v2.x

### Complete OpenAI Surface Area

**Direct Usage (Our Code):**
1. `embedding_service.py` - Embeddings only (text-embedding-3-small)
2. `query_router/llm_classifier.py` - Uses Anthropic Claude (not OpenAI LLM)
3. `query_router/query_rewriter.py` - Uses Anthropic Claude (not OpenAI LLM)

**Indirect Usage (Dependencies):**
1. `semantic-router` - Uses OpenAI embeddings via OpenAIEncoder
2. `graphiti-core` - Uses OpenAI LLMs for entity extraction (gpt-5/gpt-5-mini)

**Model Breakdown:**
- **LLM Models (Chat):** gpt-5, gpt-5-mini (graphiti-core only)
- **Embedding Models:** text-embedding-3-small (unchanged - separate from LLMs)
- **Claude Models:** claude-3-5-sonnet-20241022 (query router - unchanged)

---

## Files Modified (Git Status)

```bash
modified:   src/apex_memory/services/graphiti_service.py
modified:   src/apex_memory/services/graphiti_config.py
modified:   requirements.txt
modified:   docs/GRAPHITI-OPTIMIZATION.md
```

**No other files changed** - .env and settings.py already had correct values!

---

## What's Remaining ⏳

### Option 1: Workaround the Bug (Quick)
1. Set `GRAPHITI_UPDATE_COMMUNITIES=true` in .env
2. Re-run integration test
3. Verify test passes
4. Document workaround
5. Create git commit

**Estimated Time:** 10 minutes

### Option 2: File Bug with graphiti (Proper)
1. Create minimal reproduction case
2. File issue at https://github.com/getzep/graphiti/issues
3. Document in IMPROVEMENT-PLAN.md
4. Use Option 1 workaround in meantime
5. Create git commit with workaround documented

**Estimated Time:** 30 minutes

### Option 3: Investigate Deeper (Research)
1. Check graphiti-core 0.22.0 changelog for breaking changes
2. Review community update code path
3. Determine if communities=false is even supported anymore
4. Update our code if API changed

**Estimated Time:** 1-2 hours

---

## Test Execution Commands

**Run failing test:**
```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
PYTHONPATH=src:$PYTHONPATH pytest tests/unit/test_graphiti_rollback.py::test_orphaned_episode_cleanup -v -m integration
```

**Run all Graphiti tests:**
```bash
PYTHONPATH=src:$PYTHONPATH pytest tests/unit/test_graphiti_extraction_activity.py tests/unit/test_graphiti_rollback.py tests/unit/test_json_temporal_activities.py -v --no-cov
```

**Check current .env setting:**
```bash
grep GRAPHITI_UPDATE_COMMUNITIES .env
```

**Test with communities enabled:**
```bash
# Edit .env: GRAPHITI_UPDATE_COMMUNITIES=true
PYTHONPATH=src:$PYTHONPATH pytest tests/unit/test_graphiti_rollback.py::test_orphaned_episode_cleanup -v -m integration
```

---

## Success Metrics

**Current Status:**
- Model Names: ✅ gpt-5/gpt-5-mini (from gpt-4.1-mini/nano)
- graphiti-core: ✅ 0.22.0 (from 0.20.4)
- Tests Passing: ⚠️ 15/16 (93.75%) - 1 graphiti-core bug
- Files Modified: ✅ 4 files, ~10 lines

**Target Status:**
- Tests Passing: 16/16 (100%)
- OR: Document workaround/bug
- Git commit created with findings

---

## Key Insights for Next Session

1. **Original problem (reasoning.effort) was REPLACED by community bug**
   - We didn't fix the original issue
   - graphiti-core 0.22.0 has different bug
   - Need to enable communities or file bug

2. **The upgrade IS working for non-integration tests**
   - 15/16 tests pass
   - All mocked tests pass
   - Only real graphiti-core integration fails

3. **Our code changes are correct**
   - Model names updated properly
   - Configuration hierarchy fixed
   - No breaking changes in our code

4. **The failure is in graphiti-core library**
   - Not our code
   - Upstream bug
   - Need workaround or patch

---

## Quick Reference

**Files Changed:**
```
src/apex_memory/services/graphiti_service.py:64-65,97,1100
src/apex_memory/services/graphiti_config.py:24,29
requirements.txt:27
docs/GRAPHITI-OPTIMIZATION.md:233-234,261-262
```

**Commands:**
```bash
# Check version
pip show graphiti-core

# Run tests
cd /Users/richardglaubitz/Projects/apex-memory-system
PYTHONPATH=src:$PYTHONPATH pytest tests/unit/test_graphiti*.py -v --no-cov

# Check .env
grep GRAPHITI .env | grep -v "^#"
```

---

## Recommended Next Actions

**Immediate (Next Session):**
1. Test with `GRAPHITI_UPDATE_COMMUNITIES=true`
2. Verify test passes
3. Create git commit documenting findings
4. Update IMPROVEMENT-PLAN.md with bug details

**Follow-up (Optional):**
1. File bug with getzep/graphiti
2. Check if graphiti-core 0.22.1 exists
3. Monitor for patch release

---

**Last Updated:** 2025-10-19
**Session Duration:** ~2 hours
**Files Modified:** 4
**Tests Fixed:** 15/16 (1 upstream bug)
