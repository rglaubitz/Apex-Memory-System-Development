# Features Implementation Workflow

**Version:** 1.0
**Created:** October 2025
**Based on:** Query Router Upgrade Success
**Status:** Production-Ready

---

## Overview

This is the **proven, repeatable workflow** for implementing major features in the Apex Memory System. This workflow was battle-tested during the Query Router upgrade (October 2025) and delivered:

- ✅ 8 comprehensive research documents
- ✅ 20+ production-ready implementation files
- ✅ 30+ tests (unit + integration)
- ✅ 8 deployment examples
- ✅ 4 complete deployment guides
- ✅ Zero rework required
- ✅ 100% documentation coverage

**Use this workflow for:**
- Major feature implementations (multi-week, multi-phase)
- System upgrades requiring research
- Features touching multiple components
- Anything requiring deployment planning

**Don't use this workflow for:**
- Bug fixes (too heavyweight)
- Simple code changes
- Quick patches
- Exploratory work

---

## Table of Contents

1. [The 7-Phase Process](#the-7-phase-process)
2. [Phase Implementation Pattern](#phase-implementation-pattern)
3. [Directory Structure](#directory-structure)
4. [Best Practices](#best-practices)
5. [Success Metrics](#success-metrics)
6. [Real Example: Query Router](#real-example-query-router)

---

## The 7-Phase Process

### Phase 0: Feature Identification (Day 1)

**Goal:** Identify and scope the feature

**Artifacts:**
- `upgrades/planned/[feature-name]/README.md`
- High-level problem statement
- Initial scope

**Activities:**
1. Create feature directory in `upgrades/planned/`
2. Write initial README with:
   - Problem statement
   - Why this feature matters
   - High-level approach
   - Expected timeline
3. Get stakeholder buy-in

**Example:**
```markdown
# Query Router Improvement

**Problem:** Current router uses brittle keyword matching (63% misclassification rate)

**Why it matters:** Missing 21-28 point relevance improvement from query rewriting

**Approach:** Semantic classification + query rewriting + adaptive weights

**Timeline:** 8 weeks (4 phases × 2 weeks)
```

---

### Phase 1: RDF (Research, Document, Finalize) (Week 1)

**Goal:** Research-backed planning with latest versions and best practices

**Artifacts:**
- `upgrades/[feature-name]/IMPROVEMENT-PLAN.md`
- `upgrades/[feature-name]/IMPLEMENTATION-GUIDE.md`
- `research/documentation/[topic]/*.md` (8+ docs for query-router)

**Activities:**

1. **Research Phase:**
   - Use Exa AI for web research (official docs, articles, benchmarks)
   - Use GitHub API for version verification and code examples
   - Only Tier 1-2 sources (official docs, 1.5k+ star repos)
   - Answer critical questions:
     - What are the latest versions?
     - Are there better alternatives?
     - What are 2025 best practices?
     - Do we need training data?

2. **Document Phase:**
   - Create research analysis docs (`research/documentation/[topic]/`)
   - Create IMPROVEMENT-PLAN.md (comprehensive feature spec)
   - Create IMPLEMENTATION-GUIDE.md (step-by-step instructions)
   - Create supporting examples (`upgrades/[name]/examples/`)

3. **Finalize Phase:**
   - Review all created files
   - Git add, commit, push
   - Move from `planned/` to `upgrades/[name]/`

**Key Decision:**
- Run `/rdf [feature-name]` command (automated)
- OR manually execute research + documentation

**Quality Gate:**
- ✅ Minimum 3 sources per decision
- ✅ All sources cited with URLs
- ✅ Latest versions verified
- ✅ Complete code examples (no pseudocode)

---

### Phases 2-5: Implementation Loop (Weeks 2-7)

**Goal:** Systematic implementation with quality built-in

Each phase follows the **10-step pattern** (see next section).

**Typical Phase Breakdown:**
- **Phase 1 (Foundation):** Core components, basic functionality
- **Phase 2 (Intelligent Features):** Smart routing, optimization
- **Phase 3 (Advanced Features):** Complex logic, multi-component
- **Phase 4 (Polish):** Feature flags, monitoring, production-ready

**Timeline:** 2 weeks per phase (adjust based on complexity)

**Critical Success Factor:** Context compact between EVERY phase!

---

### Phase 6: Deployment Manual (Week 8)

**Goal:** Complete operational documentation for production deployment

**Artifacts:**
- `upgrades/[feature-name]/DEPLOYMENT-GUIDE.md` (hub)
- `upgrades/[feature-name]/deployment/TESTING.md`
- `upgrades/[feature-name]/deployment/PRODUCTION-ROLLOUT.md`
- `upgrades/[feature-name]/deployment/TROUBLESHOOTING.md`
- `upgrades/[feature-name]/deployment/examples/*.py` (8+ for query-router)

**Activities:**

1. **Testing Guide:**
   - How to run all tests
   - Environment setup requirements
   - Expected test output
   - Common test failures and fixes

2. **Production Rollout Guide:**
   - Stage-by-stage deployment strategy
   - Feature flag configuration
   - Monitoring setup
   - Rollout percentages (5% → 25% → 50% → 100%)
   - Safety checks at each stage

3. **Troubleshooting Guide:**
   - Common issues and solutions
   - Error messages and meanings
   - Debug procedures
   - Rollback procedures

4. **Working Examples:**
   - Configuration files
   - Setup scripts
   - Monitoring setup
   - Gradual rollout scripts

**Quality Gate:**
- ✅ Anyone can deploy following these docs
- ✅ All examples are copy-paste ready
- ✅ Rollback procedures tested
- ✅ Complete troubleshooting coverage

---

### Phase 7: Final Commit & Deployment (Week 8+)

**Goal:** Package everything and deploy

**Activities:**

1. **Final Review:**
   - All documentation complete
   - All tests passing
   - All examples working
   - Cross-references correct

2. **Git Commit:**
   - Commit message: "feat: Add [feature] implementation and deployment guide"
   - Include all files in single atomic commit

3. **Deployment:**
   - Follow deployment guide step-by-step
   - Stage 1: Baseline testing
   - Stage 2: Feature flags at 0%
   - Stage 3: Gradual rollout (5% → 100%)
   - Stage 4: Monitor and validate
   - Stage 5: Cleanup and optimization

4. **Move to Completed:**
   - Move from `upgrades/[name]/` to `upgrades/completed/[name]/`
   - Update upgrade tracking system
   - Archive for future reference

---

## Phase Implementation Pattern

This is the **critical 10-step pattern** used for each implementation phase (Phases 2-5).

### Step 1: Enter Plan Mode 🛑

**What happens:**
- Explicit pause before coding
- Enter "plan mode" (no tool execution)
- Discussion phase begins

**Why it matters:**
- Prevents premature coding
- Catches missing information early
- Ensures alignment before execution

### Step 2: Discuss Phase Requirements 💬

**What to discuss:**
- "What do we need for Phase X?"
- Review implementation guide for this phase
- Identify dependencies
- Check if we have all necessary context

**Questions to ask:**
- Do we need additional research?
- Are there missing framework docs?
- Do we need code examples?
- Are there unclear specifications?

**Example (Query Router Phase 2):**
```
User: "Let's start Phase 2"
Claude: [Enters plan mode]
Claude: "For Phase 2, we need:
         1. Adaptive weights (contextual bandit)
         2. GraphRAG hybrid search
         3. Semantic caching

         I have the research docs. Do we need:
         - Neo4j version verification for vector index?
         - Redis memory sizing for semantic cache?
         - Example training data for bandit?"
User: "Yes, check Neo4j version"
Claude: [Verifies Neo4j 5.11+ required]
Claude: "Confirmed. Ready to proceed?"
User: "Yes, let's go"
```

### Step 3: Research Gaps (If Needed) 📚

**If gaps identified:**
- Fetch additional documentation
- Verify versions
- Find code examples
- Review framework APIs

**Quality standard:**
- Official documentation (Tier 1)
- High-star GitHub repos (Tier 2)
- No blog posts or tutorials (Tier 3-4)

### Step 4: Exit Plan Mode ▶️

**What happens:**
- Mutual agreement reached
- Exit plan mode
- Ready to execute

**Signal:**
- User says: "Let's go" / "Proceed" / "Execute"
- OR Claude asks: "Ready to implement Phase X?"

### Step 5: Write Implementation Code 💻

**What to write:**
- Real, working code (not pseudocode)
- Follow implementation guide specs
- Use researched versions and patterns
- Proper error handling
- Structured logging (not print statements)

**Code quality standards:**
- Type hints (Python)
- Docstrings (Google style)
- Async/await where appropriate
- Circuit breakers for external calls
- Proper exception handling

**Example output:**
```python
# File: src/apex_memory/query_router/semantic_classifier.py (NEW)

"""Semantic Intent Classification using semantic-router library."""

import logging
from typing import Optional
from semantic_router import Route, SemanticRouter
from semantic_router.encoders import OpenAIEncoder

logger = logging.getLogger(__name__)

class SemanticIntentClassifier:
    """Semantic intent classification using embeddings."""

    def __init__(self, openai_api_key: str):
        # ... implementation ...
```

**Typical file count per phase:** 3-5 implementation files

### Step 6: Generate Tests Proactively ✨

**KEY BEHAVIOR:** Generate tests WITHOUT being asked!

**What happens:**
- After coding, Claude automatically starts creating tests
- User doesn't prompt for this
- Tests appear naturally as part of implementation

**Test structure:**
```python
# tests/unit/test_semantic_classifier.py (NEW)

import pytest
from src.apex_memory.query_router.semantic_classifier import SemanticIntentClassifier

@pytest.fixture
def classifier():
    return SemanticIntentClassifier(api_key="test-key")

def test_graph_queries(classifier):
    """Test graph query classification."""
    assert classifier.classify("what is connected to ACME") == "graph"
    assert classifier.classify("show relationships") == "graph"

def test_temporal_queries(classifier):
    """Test temporal query classification."""
    assert classifier.classify("how did this change") == "temporal"

def test_out_of_scope(classifier):
    """Test out-of-scope detection."""
    assert classifier.classify("what is the weather") is None
```

**Test coverage per phase:** 15-30 tests

**Test types:**
- Unit tests (component isolation)
- Integration tests (component interaction)
- Edge cases (error conditions, boundary values)

**Why this matters:**
- Quality built-in from the start
- No separate "testing phase" needed
- Catches issues immediately
- Makes refactoring safe

### Step 7: Create Working Examples 📝

**What to create:**
- Configuration examples
- Setup scripts
- Router configurations (phase1.py, phase2.py, etc.)
- Integration examples

**Example naming pattern:**
```
upgrades/[feature]/examples/
├── router_config_phase1.py  # Progressive complexity
├── router_config_phase2.py
├── router_config_phase3.py
└── router_config_phase4.py
```

**Quality standard:**
- Copy-paste ready
- Real configuration values
- Comments explaining key decisions
- No placeholders or TODOs

### Step 8: Update Documentation 📄

**Files to update:**
- `upgrades/[feature]/README_PHASEX.md` (create if needed)
- `upgrades/[feature]/CHANGELOG.md` (add phase section)
- `upgrades/[feature]/IMPLEMENTATION_STATE.md` (mark progress)

**Documentation updates:**
```markdown
## Phase 2: Intelligent Routing ✅ COMPLETE

**Implemented:**
- ✅ Adaptive score weighting (contextual bandit)
- ✅ GraphRAG hybrid search (Neo4j vector index)
- ✅ Semantic caching (similarity threshold 0.95)

**Tests:** 15 new tests (45 total)
**Files:** 5 implementation files, 3 test files, 4 examples
**Performance:** +30% accuracy improvement validated
```

### Step 9: Context Compact 🗜️

**CRITICAL:** Compact context before next phase!

**Why:**
- Prevents context window overflow
- Maintains conversation continuity
- Keeps focus on current work

**When:**
- After completing each phase
- Before starting discussion for next phase
- When context starts getting full

**Signal:**
- User says: "Let's compact before Phase X"
- OR Claude suggests: "Ready to compact before Phase 3?"

**What gets preserved:**
- Implementation state (what's done)
- Critical decisions made
- Links to key files
- Next phase plan

### Step 10: Mark Phase Complete ✅

**Activities:**
1. Verify all phase objectives met
2. Update tracking documents
3. Note completion in IMPLEMENTATION_STATE.md
4. Quick summary of achievements

**Phase completion checklist:**
```
☑ All code implemented
☑ Tests written and passing (15-30 tests)
☑ Examples created and working
☑ Documentation updated
☑ Context compacted
☑ Ready for next phase
```

---

## Directory Structure

### Standard Feature Directory Layout

```
upgrades/[feature-name]/
├── README.md                      # Quick reference
├── IMPROVEMENT-PLAN.md            # Comprehensive spec
├── IMPLEMENTATION-GUIDE.md        # Step-by-step guide
├── IMPLEMENTATION_STATE.md        # Progress tracking
├── CHANGELOG.md                   # Phase-by-phase changes
├── README_PHASE1.md               # Phase 1 documentation
├── README_PHASE2.md               # Phase 2 documentation
├── README_PHASE3.md               # Phase 3 documentation
├── README_PHASE4.md               # Phase 4 documentation
├── DEPLOYMENT-GUIDE.md            # Deployment hub
├── deployment/
│   ├── TESTING.md                 # Testing guide
│   ├── PRODUCTION-ROLLOUT.md      # Rollout strategy
│   ├── TROUBLESHOOTING.md         # Common issues
│   └── examples/                  # Deployment examples
│       ├── router_config_phase1.py
│       ├── router_config_phase2.py
│       ├── router_config_phase3.py
│       ├── router_config_phase4.py
│       ├── feature_flag_setup.py
│       ├── gradual_rollout_script.py
│       ├── monitoring_setup.py
│       └── online_learning_setup.py
└── examples/                      # General examples
    └── [feature-specific examples]
```

### Research Directory Layout

```
research/documentation/[topic]/
├── README.md                      # Topic overview
├── [framework-name]-guide.md      # Framework documentation
├── [feature]-analysis.md          # Feature analysis
├── [comparison]-study.md          # Comparison studies
└── best-practices-2025.md         # Current best practices
```

---

## Best Practices

### Research Phase

**Do:**
- ✅ Use Exa AI for latest documentation
- ✅ Verify versions with GitHub API
- ✅ Only use Tier 1-2 sources
- ✅ Save all research docs in `research/documentation/`
- ✅ Include URLs and access dates
- ✅ Create comparison tables

**Don't:**
- ❌ Skip research phase
- ❌ Use outdated documentation
- ❌ Rely on blog posts or tutorials
- ❌ Trust version numbers without verification
- ❌ Make assumptions without data

### Implementation Phase

**Do:**
- ✅ Enter plan mode before EVERY phase
- ✅ Discuss requirements thoroughly
- ✅ Generate tests proactively
- ✅ Create working examples
- ✅ Update docs as you go
- ✅ Compact between phases

**Don't:**
- ❌ Start coding without plan mode
- ❌ Skip test generation
- ❌ Leave TODOs in examples
- ❌ Defer documentation
- ❌ Skip context compaction

### Testing Phase

**Do:**
- ✅ Generate 15-30 tests per phase
- ✅ Cover unit + integration
- ✅ Test edge cases
- ✅ Test error conditions
- ✅ Make tests runnable

**Don't:**
- ❌ Wait for user to ask for tests
- ❌ Skip edge cases
- ❌ Write tests without running them
- ❌ Leave failing tests

### Documentation Phase

**Do:**
- ✅ Document as you code
- ✅ Update CHANGELOG per phase
- ✅ Create phase READMEs
- ✅ Write deployment guides
- ✅ Include troubleshooting

**Don't:**
- ❌ Defer documentation to the end
- ❌ Write vague instructions
- ❌ Skip deployment guides
- ❌ Omit troubleshooting

---

## Success Metrics

### Research Quality
- ✅ 8+ research documents created
- ✅ All sources Tier 1-2 (official docs, 1.5k+ stars)
- ✅ Latest versions verified
- ✅ Complete comparison tables

### Implementation Quality
- ✅ 20+ implementation files
- ✅ 30+ tests (unit + integration)
- ✅ 80%+ code coverage
- ✅ All async where appropriate
- ✅ Zero print() statements (use logging)

### Example Quality
- ✅ 8+ deployment examples
- ✅ Copy-paste ready
- ✅ No placeholders or TODOs
- ✅ Progressive complexity

### Documentation Quality
- ✅ 100% documentation coverage
- ✅ Deployment guide complete
- ✅ Testing guide complete
- ✅ Troubleshooting guide complete
- ✅ All cross-references correct

### Timeline Quality
- ✅ 8 weeks for major feature (4 phases × 2 weeks)
- ✅ Context compacted 4 times
- ✅ Zero rework required
- ✅ Deployment-ready on schedule

---

## Real Example: Query Router

### Timeline

**Week 1:** RDF Phase
- 8 research documents created
- IMPROVEMENT-PLAN.md (2,500 lines)
- IMPLEMENTATION-GUIDE.md (950 lines)
- Research committed

**Weeks 2-3:** Phase 1 (Foundation)
- Plan mode → Discuss → Execute
- Semantic classifier (300 lines)
- Query rewriter (400 lines)
- Analytics infrastructure (500 lines)
- 15 tests generated proactively
- 4 examples created
- Context compacted ✅

**Weeks 3-4:** Phase 2 (Intelligent Routing)
- Plan mode → Discuss → Execute
- Adaptive weights (contextual bandit)
- GraphRAG hybrid search
- Semantic caching
- 15 tests generated proactively
- 4 examples created
- Context compacted ✅

**Weeks 5-6:** Phase 3 (Agentic Evolution)
- Plan mode → Discuss → Execute
- Complexity analyzer
- Multi-router architecture
- Self-correction loop
- 15 tests generated proactively
- 4 examples created
- Context compacted ✅

**Weeks 7:** Phase 4 (Advanced Features)
- Plan mode → Discuss → Execute
- Feature flags (300 lines)
- Online learning (400 lines)
- 15 tests generated proactively
- 8 deployment examples created
- Context compacted ✅

**Week 8:** Deployment Manual
- DEPLOYMENT-GUIDE.md created
- TESTING.md created
- PRODUCTION-ROLLOUT.md created
- TROUBLESHOOTING.md created
- 8 deployment examples finalized

### Results

**Research Phase:**
- 8 research documents (40,000+ words)
- All sources cited (official docs, verified repos)
- Latest versions confirmed (semantic-router 0.1.11, anthropic 0.39.0)

**Implementation Phase:**
- 20 implementation files
- 30+ tests (15 per major component)
- 80%+ code coverage
- Zero rework required

**Deployment Phase:**
- 4 comprehensive guides
- 8 working deployment examples
- Complete troubleshooting coverage
- Safe gradual rollout strategy (5% → 100%)

**Quality Metrics:**
- ✅ Research-first principle followed
- ✅ Context compacted 4 times
- ✅ Tests generated proactively (user never asked)
- ✅ 100% documentation coverage
- ✅ Deployment-ready on schedule

---

## Templates

See `workflow/templates/features/` for:
- `IMPROVEMENT-PLAN-TEMPLATE.md`
- `IMPLEMENTATION-GUIDE-TEMPLATE.md`
- `DEPLOYMENT-GUIDE-TEMPLATE.md`
- `README-TEMPLATE.md`
- `PHASE-README-TEMPLATE.md`

---

## Related Resources

- [Quick Start Guide](./FEATURES-QUICK-START.md) - One-page cheat sheet
- [Phase Implementation Checklist](./PHASE-IMPLEMENTATION-CHECKLIST.md) - Detailed checklist
- [RDF Workflow Guide](../.claude/RDF-WORKFLOW-GUIDE.md) - Automated research workflow
- [Workflow README](./README.md) - All workflow documentation

---

**This workflow is production-proven and ready to use for any major feature implementation.**

**Next feature:** Run through this workflow start to finish. Follow the 7 phases. Don't skip steps. Document everything. You'll have deployment-ready code with zero rework.
