# Next Session: GPT-5 + graphiti-core 0.22.0 Upgrade

**Resume Date:** After context compact
**Status:** ✅ Research Complete → 📋 Ready for Phase 1 (Dependency Scan)

---

## Quick Summary

### ✅ What We Discovered (Research Complete)

**Original Plan Was WRONG:**
- Believed: gpt-4.1-mini/nano don't exist ❌
- Reality: They DO exist in your account ✅
- **Real Problem:** graphiti-core 0.20.4 passing `reasoning.effort` in wrong format

**Root Cause:**
```
Error: "Unsupported parameter: 'reasoning.effort' is not supported with this model"

Why: graphiti-core using dotted parameter (reasoning.effort)
Should be: Nested object for GPT-5 Responses API
  reasoning = { "effort": "medium" }
```

### ✅ Decisions Made

1. **Upgrade to GPT-5 Models**
   - gpt-4.1-mini → gpt-5
   - gpt-4.1-nano → gpt-5-mini
   - Reason: Proven reasoning/verbosity support, better performance

2. **Upgrade graphiti-core**
   - 0.20.4 → 0.22.0
   - Likely fixes parameter format issue
   - Refactored prompts, token reduction

3. **Keep OpenAI SDK at 1.x**
   - Already on latest (1.109.1)
   - semantic-router blocks v2.x
   - No upgrade needed

---

## 🚀 Start Here (Next Session)

### Step 1: Read Context

```bash
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/gpt5-graphiti-upgrade

# Read complete research
cat IMPROVEMENT-PLAN.md  # 1,083 lines of findings
```

### Step 2: Begin Phase 1 - Dependency Scan

**Objective:** Find ALL code that needs updating

**Commands:**
```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Find OpenAI imports
grep -r "from openai import\|import openai" src/ tests/ --include="*.py" -n

# Find graphiti-core imports
grep -r "from graphiti_core import\|import graphiti_core" src/ tests/ --include="*.py" -n

# Find model name references
grep -r "gpt-4\.1\|gpt-5\|llm_model\|small_model" src/ tests/ docs/ --include="*.py" --include="*.md" -n

# Create dependency report
# See IMPROVEMENT-PLAN.md Phase 1 for full commands
```

**Deliverable:** DEPENDENCY-REPORT.md with complete inventory

### Step 3: Continue Implementation

Follow IMPROVEMENT-PLAN.md phases:
- ✅ Phase 0: Research (COMPLETE)
- ⏳ Phase 1: Dependency scan (START HERE)
- ⏳ Phase 2: Model name updates
- ⏳ Phase 3: graphiti-core upgrade
- ⏳ Phase 4: Testing
- ⏳ Phase 5: Validation & docs

---

## 📊 Key Research Findings

**Your OpenAI Account Has (Verified via API):**
- 12 GPT-5 models ✅
- 3 GPT-4.1 models ✅
- 27 GPT-4o models ✅
- **Total:** 71 models

**GPT-5 Reasoning/Verbosity:**
- ✅ Supports reasoning (minimal/low/medium/high)
- ✅ Supports verbosity (low/medium/high)
- ⚠️ Requires Responses API nested format
- 📚 Source: Official OpenAI Cookbook

**GPT-4.1 Reasoning:**
- ❓ **UNDOCUMENTED** (no official docs found)
- Risk: Unknown if supported
- **Decision:** Upgrade to GPT-5 instead

---

## 📋 Files to Modify (Known)

**Phase 2 Changes:**
1. `src/apex_memory/services/graphiti_service.py:64-65`
2. `src/apex_memory/services/graphiti_config.py:24,29`
3. `src/apex_memory/config/settings.py:258`
4. `requirements.txt:26-27`
5. `.env.example` (if model vars exist)
6. All documentation mentioning gpt-4.1

**Phase 3 Changes:**
1. `requirements.txt` (graphiti-core==0.22.0)
2. Verify imports still work
3. Check for new config options

---

## 🎯 Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| Model Names | gpt-5/gpt-5-mini | gpt-4.1-mini/nano |
| graphiti-core | 0.22.0 | 0.20.4 |
| Tests Passing | 161/161 (100%) | 160/161 (99.4%) |
| reasoning.effort Error | ✅ Fixed | ❌ Failing |

---

## ⚡ Quick Commands

**Check current status:**
```bash
# Model names
grep -n "gpt-4.1" src/apex_memory/services/graphiti_service.py

# graphiti-core version
pip show graphiti-core | grep Version

# Test status
cd /Users/richardglaubitz/Projects/apex-memory-system
PYTHONPATH=src:$PYTHONPATH pytest tests/integration/test_document_workflow_staging.py::test_staging_end_to_end_success -v
```

**Start dependency scan:**
```bash
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/gpt5-graphiti-upgrade

# Copy Phase 1 commands from IMPROVEMENT-PLAN.md
# Execute dependency scan
# Create DEPENDENCY-REPORT.md
```

---

## 📖 Documentation

**Primary Reference:**
- [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md) - Complete research findings (1,083 lines)

**Supporting Docs:**
- [README.md](README.md) - Quick reference
- [NEXT-SESSION.md](NEXT-SESSION.md) - This file (handoff)

**To Be Created:**
- DEPENDENCY-REPORT.md (Phase 1)
- PROGRESS.md (during implementation)
- HANDOFF.md (Phase 5 complete)

---

## ⏱️ Estimated Timeline

**Remaining Work:**
- Phase 1: 2 hours (dependency scan)
- Phase 2: 1 hour (model updates)
- Phase 3: 2 hours (graphiti upgrade)
- Phase 4: 4 hours (testing)
- Phase 5: 2 hours (validation/docs)
- **Total:** 11 hours

---

## 🔗 Quick Links

**Research Sources:**
- OpenAI Cookbook: https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools
- graphiti-core 0.22.0: https://github.com/getzep/graphiti/releases
- Your API verification results: See IMPROVEMENT-PLAN.md

**Next Project (After Upgrade):**
- Week 3 JSON Integration: `../temporal-implementation/graphiti-json-integration/`

---

**Last Updated:** 2025-10-20
**Next Action:** Phase 1 Dependency Scan
**Expected Duration:** 2 hours
