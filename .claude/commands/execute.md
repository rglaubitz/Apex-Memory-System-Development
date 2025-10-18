# Execute Phase Implementation

**Command:** `/execute [phase-number]`
**Purpose:** Guide systematic implementation following the proven 10-step pattern
**Based on:** [Features Implementation Workflow](../../workflow/FEATURES-IMPLEMENTATION-WORKFLOW.md)

---

## Instructions for Claude

You are now executing a feature implementation phase using the battle-tested 10-step pattern. This pattern has delivered zero-rework implementations with 100% documentation coverage.

**Current Phase:** {phase-number or "Next phase in sequence"}

**Your Mission:** Guide through all 10 steps systematically, ensuring quality at each checkpoint.

---

## Step 1: Enter Plan Mode 🛑

**STOP - DO NOT CODE YET!**

You are now in plan mode. No tool execution allowed until Step 4.

**Announce:**
```
🛑 ENTERING PLAN MODE for Phase X implementation

Following the 10-step proven pattern from Features Implementation Workflow.
No code execution until we complete steps 1-3 and mutual agreement is reached.

Let's discuss what we need for this phase...
```

---

## Step 2: Discuss Phase Requirements 💬

**Your Action:** Lead a thorough discussion about phase requirements.

**Ask these questions:**

1. **Phase Scope:**
   - "What are the main deliverables for this phase?"
   - "Which components need to be implemented?"
   - "What are the dependencies on previous phases?"

2. **Research Status:**
   - "Do we have all necessary documentation?"
   - "Are there any framework versions to verify?"
   - "Do we need additional code examples?"

3. **Implementation Details:**
   - "What are the key technical decisions?"
   - "Are there any performance considerations?"
   - "What error handling patterns should we use?"

4. **Testing Strategy:**
   - "What are the critical test scenarios?"
   - "What edge cases need coverage?"
   - "What integration points need testing?"

**Reference:** Check if implementation guide exists for this phase:
- `upgrades/[feature-name]/IMPLEMENTATION-GUIDE.md`
- Phase-specific README if available

**Quality Check:**
- ✅ All phase objectives clearly defined
- ✅ Dependencies identified
- ✅ Technical approach agreed upon
- ✅ Testing strategy outlined

---

## Step 3: Research Gaps (If Needed) 📚

**If gaps identified in Step 2, address them now.**

**Common Gaps:**
- Missing framework documentation → Fetch from official sources
- Unclear version requirements → Verify with GitHub API or package registries
- No code examples → Search high-quality repos (1.5k+ stars)
- API changes → Check latest documentation

**Quality Standards:**
- Tier 1: Official documentation (preferred)
- Tier 2: High-star GitHub repos (1.5k+ stars)
- Tier 3+: Not acceptable for implementation decisions

**Actions:**
- Use Exa AI for web research if needed
- Use GitHub API for version verification
- Save research docs to `research/documentation/[topic]/`
- Update implementation guide with findings

**After Research:**
- "Research gaps filled. Here's what I found: ..."
- Update phase requirements based on research
- Confirm we're ready to proceed

---

## Step 4: Exit Plan Mode ▶️

**Checkpoint: Get explicit confirmation before proceeding.**

**Ask:**
```
✅ Phase requirements discussed and clear
✅ Research gaps filled (if any)
✅ Implementation approach agreed upon
✅ Testing strategy defined

Ready to begin Phase X implementation?

Type "Yes" or "Let's go" to proceed with coding.
```

**Wait for user confirmation.**

**Once confirmed:**
```
▶️ EXITING PLAN MODE

Beginning Phase X implementation with:
- [X] components to build
- [X] tests to generate
- [X] examples to create
- [X] docs to update

Starting with implementation code...
```

---

## Step 5: Write Implementation Code 💻

**Now you can write code!**

**Implementation Standards:**

**Code Quality:**
- ✅ Real, working code (not pseudocode)
- ✅ Type hints (Python: `def func(x: int) -> str:`)
- ✅ Google-style docstrings
- ✅ Async/await where appropriate
- ✅ Structured logging (`logger.info()`, not `print()`)
- ✅ Proper error handling (try/except with specific exceptions)
- ✅ Circuit breakers for external calls

**File Organization:**
```python
# File: src/apex_memory/[component]/[module].py (NEW or MODIFY)

"""Module-level docstring explaining purpose.

Author: Apex Infrastructure Team
Created: YYYY-MM-DD
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ComponentName:
    """Component description.

    This component handles [what it does].

    Args:
        param1: Description.
        param2: Description.

    Examples:
        >>> component = ComponentName()
        >>> result = component.method()
    """

    def __init__(self, param1: str, param2: Optional[int] = None):
        """Initialize component."""
        self.param1 = param1
        self.param2 = param2
        logger.info(f"Initialized {self.__class__.__name__}")

    async def method(self) -> Dict[str, Any]:
        """Method description.

        Returns:
            Dictionary with results.

        Raises:
            ValueError: If validation fails.
        """
        try:
            # Implementation
            result = await self._internal_method()
            return result
        except Exception as e:
            logger.error(f"Method failed: {e}")
            raise
```

**Expected Output:**
- 3-5 implementation files per phase
- 200-500 lines per file (modular design)
- Complete implementations (no TODOs in production code)

**As you code, announce progress:**
```
📝 Creating [component-name]...
   File: src/[path]/[file].py (NEW/MODIFY)
   Lines: ~XXX
   Purpose: [Brief description]
```

---

## Step 6: Generate Tests Proactively ✨

**CRITICAL:** Generate tests WITHOUT being asked!

**This is automatic behavior:** After implementing code, you IMMEDIATELY start creating tests.

**Test Structure:**

```python
# File: tests/unit/test_[component].py (NEW)

"""Unit tests for [component].

Tests verify:
- Core functionality
- Edge cases
- Error handling
- Integration points

Author: Apex Infrastructure Team
Created: YYYY-MM-DD
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from apex_memory.[module] import ComponentName


@pytest.fixture
def component():
    """Fixture providing test component instance."""
    return ComponentName(param1="test-value")


@pytest.mark.asyncio
async def test_core_functionality(component):
    """Test primary use case."""
    result = await component.method()

    assert result is not None
    assert result["status"] == "success"


@pytest.mark.asyncio
async def test_edge_case_empty_input(component):
    """Test handling of empty input."""
    result = await component.method_with_input("")

    assert result["status"] == "skipped"


@pytest.mark.asyncio
async def test_error_handling(component):
    """Test error handling for invalid input."""
    with pytest.raises(ValueError):
        await component.method_with_validation("invalid")


@pytest.mark.asyncio
async def test_integration_with_external_service(component):
    """Test integration with external service."""
    with patch("apex_memory.external.service_call") as mock_service:
        mock_service.return_value = {"data": "test"}

        result = await component.call_external_service()

        assert result["data"] == "test"
        mock_service.assert_called_once()
```

**Test Coverage per Phase:**
- 15-30 tests minimum
- Unit tests (component isolation)
- Integration tests (component interaction)
- Edge cases (boundary conditions)
- Error tests (exception handling)

**Announce as you create tests:**
```
✨ Generating tests for [component-name]...
   File: tests/unit/test_[component].py (NEW)
   Tests: XX scenarios
   Coverage: Core functionality, edge cases, errors, integration
```

**Quality Check:**
- ✅ All public methods tested
- ✅ Edge cases covered
- ✅ Error conditions tested
- ✅ Integration points tested
- ✅ Tests are runnable (`pytest tests/...`)

---

## Step 7: Create Working Examples 📝

**Create copy-paste ready examples demonstrating the implementation.**

**Example Types:**

**1. Configuration Examples:**
```python
# File: upgrades/[feature]/examples/config_phase_X.py

"""Phase X configuration example.

This example shows how to configure [component] for [use case].

Author: Apex Infrastructure Team
Created: YYYY-MM-DD
"""

from apex_memory.[component] import ComponentName

# Example configuration
config = {
    "param1": "production-value",
    "param2": 100,
    "feature_flags": {
        "enable_caching": True,
        "enable_monitoring": True,
    },
}

# Initialize component
component = ComponentName(**config)

# Usage example
async def example_usage():
    """Example showing typical usage pattern."""
    result = await component.method()
    print(f"Result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
```

**2. Integration Examples:**
```python
# File: upgrades/[feature]/examples/integration_phase_X.py

"""Phase X integration example.

Shows how Phase X components integrate with existing system.

Author: Apex Infrastructure Team
Created: YYYY-MM-DD
"""

# Complete working example with imports, setup, execution
```

**3. Migration/Setup Scripts:**
```python
# File: upgrades/[feature]/examples/setup_phase_X.py

"""Setup script for Phase X deployment.

Run this script to configure Phase X in your environment.

Usage:
    python examples/setup_phase_X.py --env production

Author: Apex Infrastructure Team
Created: YYYY-MM-DD
"""

# Script with argument parsing, validation, execution
```

**Quality Standards:**
- ✅ Copy-paste ready (no placeholders)
- ✅ Real configuration values
- ✅ Executable code (can run immediately)
- ✅ Comments explaining key decisions
- ✅ Progressive complexity (basic → advanced)

**Expected Output:**
- 3-5 examples per phase
- Each example demonstrates different aspect
- Examples build on each other (phase1.py → phase2.py → phase3.py)

---

## Step 8: Update Documentation 📄

**Update documentation as you complete implementation.**

**Files to Update:**

**1. Phase README:**
```markdown
# File: upgrades/[feature]/README_PHASE_X.md (CREATE if new)

## Phase X: [Phase Name] ✅ COMPLETE

**Timeline:** Week X-Y
**Status:** Complete
**Date Completed:** YYYY-MM-DD

### Implemented

- ✅ [Component 1] - [Brief description]
- ✅ [Component 2] - [Brief description]
- ✅ [Component 3] - [Brief description]

### Key Decisions

**[Decision 1]:** [Rationale based on research]
- Source: [Link to research doc or official docs]
- Why: [Explanation]

**[Decision 2]:** [Rationale]
- Source: [Link]
- Why: [Explanation]

### Tests Created

- **Unit Tests:** XX tests covering [components]
- **Integration Tests:** XX tests covering [scenarios]
- **Edge Cases:** XX tests covering [conditions]
- **Total:** XX tests

**Coverage:** XX% (target: 80%+)

### Examples Created

1. `examples/config_phase_X.py` - Configuration example
2. `examples/integration_phase_X.py` - Integration example
3. `examples/setup_phase_X.py` - Setup script

### Performance Metrics

- [Metric 1]: [Expected improvement]
- [Metric 2]: [Expected improvement]

### Next Phase

**Phase X+1:** [Next phase name]
- Dependencies: Phase X complete
- Expected timeline: Week X-Y
- Key objectives: [Brief list]
```

**2. Implementation State:**
```markdown
# File: upgrades/[feature]/IMPLEMENTATION_STATE.md (UPDATE)

## Current State: Phase X Complete ✅

### Phase Progress

- [x] Phase 1: [Name] ✅ Complete
- [x] Phase 2: [Name] ✅ Complete
- [x] Phase X: [Name] ✅ Complete (Just finished!)
- [ ] Phase X+1: [Name] 🔄 Next

### Statistics

**Code:**
- Implementation files: XX (+Y new this phase)
- Lines of code: XXXX (+YYY this phase)
- Test files: XX (+Y new this phase)
- Test coverage: XX%

**Documentation:**
- Research docs: XX
- Phase READMEs: XX
- Examples: XX (+Y new this phase)
- Deployment guides: XX

**Quality Metrics:**
- Tests passing: XXX/XXX (100%)
- Code coverage: XX% (target: 80%+)
- Zero TODO/FIXME in production code
- All examples executable
```

**3. Changelog:**
```markdown
# File: upgrades/[feature]/CHANGELOG.md (UPDATE)

## Phase X: [Phase Name] (YYYY-MM-DD)

### Added
- [Component 1] for [purpose]
- [Component 2] for [purpose]
- [Feature] supporting [capability]

### Changed
- [Existing component] now supports [new capability]
- [Configuration] updated to include [new options]

### Tests
- Added XX unit tests for [components]
- Added XX integration tests for [scenarios]
- Total test count: XXX (was YYY)

### Examples
- `examples/config_phase_X.py` - Configuration example
- `examples/integration_phase_X.py` - Integration example
- `examples/setup_phase_X.py` - Setup script

### Documentation
- Created `README_PHASE_X.md`
- Updated `IMPLEMENTATION_STATE.md`
- Updated main `README.md` with phase X info
```

**4. Main Feature README:**
```markdown
# File: upgrades/[feature]/README.md (UPDATE)

# [Feature Name] Implementation

**Status:** 🚀 Phase X Complete
**Progress:** [Progress bar] XX% complete (X/Y phases)
**Last Updated:** YYYY-MM-DD

## Quick Links

- [IMPROVEMENT-PLAN.md](./IMPROVEMENT-PLAN.md) - Feature specification
- [IMPLEMENTATION-GUIDE.md](./IMPLEMENTATION-GUIDE.md) - Implementation steps
- [README_PHASE_X.md](./README_PHASE_X.md) - Latest phase (just completed!)
- [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) - Deployment procedures (when ready)

## Implementation Progress

### ✅ Completed Phases

- [x] **Phase 1: [Name]** (Week 1-2) - [Brief description]
- [x] **Phase 2: [Name]** (Week 3-4) - [Brief description]
- [x] **Phase X: [Name]** (Week X-Y) - [Brief description] ← JUST COMPLETED

### 🔄 Current Phase

- [ ] **Phase X+1: [Name]** (Week X-Y) - [Brief description]

### 📋 Upcoming Phases

- [ ] **Phase X+2: [Name]** (Week X-Y) - [Brief description]
```

---

## Step 9: Context Compact 🗜️

**CRITICAL REMINDER:** Compact context before next phase!

**Why Context Compact Matters:**
- Prevents context window overflow
- Maintains conversation continuity
- Keeps focus on current work
- Essential for multi-phase projects

**Announce:**
```
🗜️ CONTEXT COMPACT REMINDER

Phase X implementation is complete. Before starting Phase X+1, we should compact the context.

**What gets preserved:**
- Implementation state (Phase X complete)
- Critical decisions made
- Links to created files
- Next phase plan
- Key metrics and progress

**What gets summarized:**
- Detailed implementation discussions
- Step-by-step code creation
- Test generation details
- Documentation updates

Ready to compact before Phase X+1?
```

**Wait for user confirmation:**
- User says: "Let's compact" / "Yes, compact" / "Proceed"
- Then perform context compact operation

**After Compact:**
```
✅ Context compacted successfully

Preserved:
- Phase X complete (XX files, XX tests, XX examples)
- All documentation updated
- Ready for Phase X+1

Next: When ready, run `/execute X+1` to begin next phase.
```

---

## Step 10: Mark Phase Complete ✅

**Final step: Confirm phase completion and readiness for next phase.**

**Phase Completion Checklist:**
```
☑ Implementation Complete
  ☑ All planned components implemented (X/X)
  ☑ All code follows quality standards
  ☑ No TODO/FIXME in production code
  ☑ Proper error handling throughout
  ☑ Structured logging (no print statements)

☑ Tests Complete
  ☑ Unit tests written (XX tests)
  ☑ Integration tests written (XX tests)
  ☑ Edge cases covered
  ☑ Error scenarios tested
  ☑ All tests passing (XXX/XXX = 100%)
  ☑ Coverage ≥80% target

☑ Examples Complete
  ☑ Configuration examples (X files)
  ☑ Integration examples (X files)
  ☑ Setup scripts (X files)
  ☑ All examples executable
  ☑ No placeholders or TODOs

☑ Documentation Complete
  ☑ Phase README created/updated
  ☑ Implementation state updated
  ☑ Changelog updated
  ☑ Main README updated
  ☑ All cross-references correct

☑ Quality Gates Passed
  ☑ Code review self-check complete
  ☑ Performance considerations addressed
  ☑ Security considerations addressed
  ☑ No breaking changes (or documented)

☑ Ready for Next Phase
  ☑ Context compacted (or ready to compact)
  ☑ Dependencies for next phase identified
  ☑ Team aligned on next steps
  ☑ Timeline on track
```

**Summary Message:**
```
🎉 PHASE X IMPLEMENTATION COMPLETE!

**Delivered:**
- ✅ XX implementation files (XXXX lines)
- ✅ XX test files (XXX tests, 100% passing)
- ✅ XX examples (all executable)
- ✅ Complete documentation (README, changelog, state)

**Quality Metrics:**
- Test coverage: XX% (target: 80%+)
- Zero TODO/FIXME in production code
- All examples copy-paste ready
- Documentation 100% complete

**Timeline:**
- Planned: Week X-Y
- Actual: Week X-Y
- Status: ✅ On Schedule

**Next Steps:**
1. Compact context (when ready)
2. Review Phase X deliverables
3. Run `/execute X+1` for next phase

Ready for Phase X+1 when you are!
```

---

## Quick Reference

**Command Usage:**
```bash
/execute          # Execute next phase (auto-detect)
/execute 2        # Execute specific phase number
```

**Quality Standards:**
- 3-5 implementation files per phase
- 15-30 tests per phase (unit + integration + edge cases)
- 3-5 examples per phase (copy-paste ready)
- 100% documentation coverage
- Context compact between phases

**Success Metrics:**
- ✅ All code implemented and tested
- ✅ Zero rework required
- ✅ Documentation complete as you go
- ✅ Examples working immediately
- ✅ Ready for next phase

---

**Reference:** [Features Implementation Workflow](../../workflow/FEATURES-IMPLEMENTATION-WORKFLOW.md)

**This command implements the proven pattern that delivered the Query Router upgrade with zero rework and 100% documentation coverage.**
