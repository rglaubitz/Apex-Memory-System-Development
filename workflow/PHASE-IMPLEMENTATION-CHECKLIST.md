# Phase Implementation Checklist

**Detailed checklist for implementing each phase (Phases 2-5)**

Use this checklist for every implementation phase to ensure nothing is missed.

---

## Pre-Phase Checklist

Before starting ANY phase:

```
☐ Previous phase is 100% complete
☐ Previous phase context has been compacted
☐ IMPLEMENTATION-GUIDE.md section for this phase is reviewed
☐ All required research documents are available
☐ Dependencies from previous phases are verified
```

---

## Step 1: Enter Plan Mode 🛑

```
☐ User initiates phase: "Let's start Phase X"
☐ Claude enters plan mode (no tool execution)
☐ Plan mode confirmed active
```

**Expected output:**
```
Claude: "Entering plan mode for Phase X. Let me review the requirements..."
```

---

## Step 2: Discuss Phase Requirements 💬

```
☐ Review implementation guide for this phase
☐ List all components to be implemented
☐ Identify dependencies on other components
☐ Check for unclear specifications
☐ Identify potential challenges
```

**Discussion prompts:**
- "For Phase X, we need to implement: [list]"
- "Dependencies: [list]"
- "Questions: [list]"
- "Do we need additional research for [topic]?"

**Example discussion:**
```
Claude: "For Phase 2 (Intelligent Routing), we need:
         1. Adaptive weights using contextual bandit
         2. GraphRAG hybrid search (Neo4j vector index)
         3. Semantic caching (similarity threshold)

         Dependencies:
         - Phase 1 semantic classifier must be complete
         - Neo4j 5.11+ for vector index support
         - Redis for cache storage

         Questions:
         - Do we need to verify Neo4j version?
         - Should we research cache memory sizing?
         - Do we have example training data for bandit?"
```

---

## Step 3: Identify Research Gaps 📚

```
☐ Check if all framework documentation is available
☐ Verify version numbers are known
☐ Check if code examples exist
☐ Identify missing API documentation
☐ Note any unclear best practices
```

**If gaps found:**
```
☐ Use Exa AI to find official documentation
☐ Use GitHub API to verify versions
☐ Search for code examples (1.5k+ stars)
☐ Create new research document if needed
☐ Save research to research/documentation/
```

**Quality gate:**
- Only Tier 1-2 sources (official docs, high-star repos)
- No blog posts or tutorials
- All sources dated and cited

---

## Step 4: Exit Plan Mode ▶️

```
☐ All questions answered
☐ All research gaps filled
☐ Implementation approach agreed upon
☐ User gives go-ahead signal
☐ Claude exits plan mode
```

**User signals:**
- "Let's go"
- "Proceed"
- "Execute"
- "Start implementation"

**Claude confirms:**
```
Claude: "Plan complete. Proceeding with Phase X implementation."
```

---

## Step 5: Write Implementation Code 💻

```
☐ Create new files (3-5 typical per phase)
☐ Use researched versions and patterns
☐ Add type hints (Python)
☐ Write Google-style docstrings
☐ Use async/await where appropriate
☐ Add proper error handling
☐ Use structured logging (no print statements)
☐ Add circuit breakers for external calls
☐ Include usage examples in docstrings
```

**Code quality checklist:**
```python
# ✅ Good Example
"""Module for semantic intent classification.

Uses semantic-router 0.1.11 for embedding-based routing.
Replaces brittle keyword matching with ML-based classification.
"""

import logging
from typing import Optional
from semantic_router import Route, SemanticRouter

logger = logging.getLogger(__name__)

class SemanticIntentClassifier:
    """Semantic intent classification using embeddings."""

    def __init__(self, openai_api_key: str):
        """Initialize semantic router.

        Args:
            openai_api_key: OpenAI API key for embeddings
        """
        self.router = SemanticRouter(...)
        logger.info("Semantic router initialized")

    async def classify(self, query: str) -> Optional[str]:
        """Classify query intent.

        Args:
            query: Natural language query

        Returns:
            Intent name or None for out-of-scope
        """
        try:
            route = await self.router(query)
            return route.name if route else None
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return None
```

**File naming conventions:**
```
src/apex_memory/query_router/
├── semantic_classifier.py        # NEW for Phase 1
├── query_rewriter.py             # NEW for Phase 1
├── analytics.py                  # NEW for Phase 1
├── adaptive_weights.py           # NEW for Phase 2
├── graphiti_search.py            # NEW for Phase 2
└── semantic_cache.py             # NEW for Phase 2
```

---

## Step 6: Generate Tests Proactively ✨

**CRITICAL:** Generate tests WITHOUT user asking!

```
☐ After coding, automatically start creating tests
☐ Create tests/unit/test_[component].py
☐ Create tests/integration/test_[component]_integration.py
☐ Write 15-30 tests per phase
☐ Cover happy path cases
☐ Cover edge cases
☐ Cover error conditions
☐ Use pytest fixtures
☐ Add clear test descriptions
☐ Make tests runnable
```

**Test structure template:**
```python
# tests/unit/test_semantic_classifier.py

import pytest
from src.apex_memory.query_router.semantic_classifier import SemanticIntentClassifier

@pytest.fixture
def classifier():
    """Create classifier instance for testing."""
    return SemanticIntentClassifier(api_key="test-key")

class TestSemanticClassifier:
    """Test suite for semantic classification."""

    def test_graph_query_classification(self, classifier):
        """Test graph queries are correctly classified."""
        queries = [
            "what is connected to ACME Corp",
            "show relationships between X and Y",
            "network of connections for customer"
        ]
        for query in queries:
            result = classifier.classify(query)
            assert result == "graph", f"Failed for: {query}"

    def test_temporal_query_classification(self, classifier):
        """Test temporal queries are correctly classified."""
        queries = [
            "how did this change over time",
            "payment trends last 6 months",
            "evolution of customer behavior"
        ]
        for query in queries:
            result = classifier.classify(query)
            assert result == "temporal", f"Failed for: {query}"

    def test_out_of_scope_detection(self, classifier):
        """Test out-of-scope queries return None."""
        queries = [
            "what is the weather today",
            "how to cook pasta",
            "latest sports scores"
        ]
        for query in queries:
            result = classifier.classify(query)
            assert result is None, f"Should be OOS: {query}"

    def test_error_handling(self, classifier):
        """Test error handling for invalid inputs."""
        # Empty query
        assert classifier.classify("") is None

        # Very long query
        long_query = "test " * 10000
        result = classifier.classify(long_query)
        assert result is not None or result is None  # Should not crash

    @pytest.mark.asyncio
    async def test_async_classification(self, classifier):
        """Test async classification works correctly."""
        result = await classifier.classify("what is connected to ACME")
        assert result == "graph"
```

**Test coverage targets:**
- Unit tests: 80%+ coverage
- Integration tests: Key workflows covered
- Edge cases: All boundary conditions
- Error cases: All exception paths

---

## Step 7: Create Working Examples 📝

```
☐ Create example configuration files
☐ Create setup scripts
☐ Create router configurations (phase1.py, phase2.py, etc.)
☐ Create integration examples
☐ Ensure all examples are copy-paste ready
☐ Remove all TODOs and placeholders
☐ Add comments explaining key decisions
☐ Test examples actually work
```

**Example file structure:**
```python
# upgrades/[feature]/examples/router_config_phase2.py

"""
Query Router Configuration - Phase 2 (Intelligent Routing)

This configuration enables:
- Adaptive score weighting with contextual bandit
- GraphRAG hybrid search
- Semantic caching

Requirements:
- Neo4j 5.11+ (for vector index)
- Redis (for semantic cache)
- Phase 1 components (semantic classifier, query rewriter)
"""

import os
from apex_memory.query_router.router import QueryRouter

async def create_phase2_router():
    """Create router with Phase 2 features enabled."""

    router = QueryRouter(
        # Phase 1: Foundation (ENABLED)
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_semantic_classification=True,
        enable_query_rewriting=True,
        enable_analytics=True,

        # Phase 2: Intelligent Routing (NEW - ENABLED)
        enable_adaptive_routing=True,      # ← NEW
        enable_graphrag=True,              # ← NEW
        enable_semantic_cache=True,        # ← NEW
        bandit_alpha=0.5,                  # Exploration parameter
        cache_similarity_threshold=0.95,   # Semantic cache threshold

        # Database connections
        neo4j_uri=os.getenv("NEO4J_URI"),
        postgres_dsn=os.getenv("POSTGRES_DSN"),
        redis_host=os.getenv("REDIS_HOST"),
    )

    await router.initialize()

    print("✅ Phase 2 router initialized!")
    print("   - Adaptive routing: ENABLED")
    print("   - GraphRAG: ENABLED")
    print("   - Semantic cache: ENABLED")

    return router


if __name__ == "__main__":
    import asyncio
    router = asyncio.run(create_phase2_router())

    # Example query
    result = asyncio.run(router.query("what equipment is connected to ACME Corp"))
    print(f"\nQuery result: {len(result)} documents found")
```

**Example naming conventions:**
```
upgrades/[feature]/examples/
├── router_config_phase1.py       # Foundation only
├── router_config_phase2.py       # Phase 1 + Phase 2
├── router_config_phase3.py       # Phases 1-3
└── router_config_phase4.py       # All phases (full power)
```

---

## Step 8: Update Documentation 📄

```
☐ Create or update README_PHASEX.md
☐ Update CHANGELOG.md with phase section
☐ Update IMPLEMENTATION_STATE.md with completion status
☐ Update main README.md if needed
☐ Add cross-references between docs
☐ Verify all links work
```

**README_PHASEX.md template:**
```markdown
# Phase X: [Phase Name]

**Status:** ✅ COMPLETE
**Timeline:** Week X-Y
**Files:** [count] implementation, [count] tests, [count] examples

---

## Overview

[Brief description of what this phase accomplishes]

---

## Components Implemented

### 1. [Component Name]

**File:** `src/apex_memory/[path]/[file].py`
**Lines:** ~[count]
**Purpose:** [Brief description]

**Key features:**
- Feature 1
- Feature 2
- Feature 3

**Usage example:**
```python
from apex_memory.[path] import [Component]

# Example usage
component = Component(...)
result = component.method(...)
```

### 2. [Component Name]
... (repeat for each component)

---

## Tests

**Total:** [count] tests
**Coverage:** [percentage]%

**Test files:**
- `tests/unit/test_[component].py` ([count] tests)
- `tests/integration/test_[component]_integration.py` ([count] tests)

**Run tests:**
```bash
pytest tests/unit/test_[component].py -v
```

---

## Examples

**Created:**
- `examples/router_config_phase[X].py`
- `examples/[other_example].py`

**Run example:**
```bash
python examples/router_config_phase[X].py
```

---

## Configuration

**New parameters:**
```python
router = QueryRouter(
    enable_[feature]=True,  # NEW
    [param]=[value],        # NEW
)
```

---

## Performance Metrics

**Expected improvements:**
- [Metric 1]: [baseline] → [target]
- [Metric 2]: [baseline] → [target]

---

## Next Steps

Phase [X+1]: [Next phase name]
```

**CHANGELOG.md update:**
```markdown
## Phase X: [Phase Name] (Week X-Y)

### Added
- ✅ [Component 1]: [Description]
- ✅ [Component 2]: [Description]
- ✅ [Component 3]: [Description]

### Tests
- ✅ [count] unit tests
- ✅ [count] integration tests
- ✅ [percentage]% code coverage

### Examples
- ✅ router_config_phase[X].py
- ✅ [other examples]

### Performance
- [Metric]: [improvement]

### Dependencies
- [New dependency]: [version]
```

---

## Step 9: Context Compact 🗜️

**CRITICAL STEP - DO NOT SKIP!**

```
☐ Phase implementation is 100% complete
☐ All files committed to git
☐ User initiates compact: "Let's compact before Phase X+1"
☐ Claude saves conversation state
☐ Context compact executes
☐ New conversation begins with preserved context
```

**What to preserve:**
```
✅ Implementation state (what's done)
✅ Key decisions made
✅ Links to important files
✅ Next phase plan
✅ Outstanding issues/notes
```

**What to discard:**
```
❌ Detailed code discussions
❌ Debugging sessions
❌ Multiple iterations of same code
❌ Verbose research discussions
```

**User signal:**
```
User: "Let's compact before Phase 3"
User: "Context compact time"
User: "Ready to compact"
```

---

## Step 10: Mark Phase Complete ✅

```
☐ All code implemented and working
☐ All tests written and passing (15-30 tests)
☐ All examples created and tested
☐ All documentation updated
☐ Context compacted
☐ Git committed
☐ Ready to start next phase
```

**Completion message template:**
```
✅ Phase X Complete!

**Implemented:**
- Component 1
- Component 2
- Component 3

**Tests:** [count] new tests ([total] total)
**Files:** [count] implementation, [count] tests, [count] examples
**Documentation:** README_PHASEX.md, CHANGELOG.md updated
**Context:** Compacted

**Next:** Phase [X+1] - [Phase Name]
```

---

## Quality Gates

### Before exiting Step 1 (Plan Mode)
- ✅ All requirements understood
- ✅ All research gaps identified
- ✅ Implementation approach clear
- ✅ Dependencies verified

### Before exiting Step 5 (Code)
- ✅ All files created
- ✅ No print() statements
- ✅ Proper error handling
- ✅ Type hints present
- ✅ Docstrings complete

### Before exiting Step 6 (Tests)
- ✅ 15-30 tests generated
- ✅ Happy path covered
- ✅ Edge cases covered
- ✅ Error cases covered
- ✅ All tests pass

### Before exiting Step 7 (Examples)
- ✅ Copy-paste ready
- ✅ No TODOs/placeholders
- ✅ Examples tested
- ✅ Comments added

### Before exiting Step 9 (Compact)
- ✅ All work committed
- ✅ Documentation updated
- ✅ Tests passing
- ✅ Phase 100% complete

---

## Common Pitfalls

### ❌ Skipping plan mode
**Impact:** Missing requirements, rework needed
**Fix:** Always enter plan mode before coding

### ❌ Not generating tests
**Impact:** Quality issues, bugs in production
**Fix:** Generate tests proactively after coding

### ❌ Skipping context compact
**Impact:** Context overflow, loss of conversation
**Fix:** Compact after EVERY phase

### ❌ Leaving TODOs in examples
**Impact:** Examples not usable
**Fix:** Complete all examples fully

### ❌ Deferring documentation
**Impact:** Documentation falls behind, never catches up
**Fix:** Update docs during implementation

---

## Success Metrics Per Phase

```
✅ 3-5 implementation files created
✅ 15-30 tests generated proactively
✅ 80%+ code coverage
✅ 2-4 working examples
✅ Phase README created
✅ CHANGELOG updated
✅ Context compacted
✅ Zero rework required
```

---

**Print this checklist and use it for every phase. Following it ensures zero rework and production-ready code.**
