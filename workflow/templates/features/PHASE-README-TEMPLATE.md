# Phase [X]: [Phase Name]

**Status:** [✅ Complete / 🚧 In Progress / ⭕ Not Started]
**Timeline:** Week [X-Y]
**Completion Date:** [Date or "In Progress"]
**Files:** [count] implementation | [count] tests | [count] examples

---

## Overview

[2-3 paragraph description of what this phase accomplishes and why it's important]

**Key objectives:**
- [Objective 1]
- [Objective 2]
- [Objective 3]

**Dependencies:**
- Phase [X-1]: [What was needed from previous phase]
- [External dependency if any]

---

## Components Implemented

### 1. [Component Name]

**File:** `src/[module]/[path]/[component].py` ([line count] lines)
**Purpose:** [Brief description of what this component does]

**Key features:**
- Feature 1: [Description]
- Feature 2: [Description]
- Feature 3: [Description]

**Implementation highlights:**
```python
class [ComponentName]:
    """[Docstring]"""

    def __init__(self, [params]):
        """[Description]"""
        # Key initialization

    async def [main_method](self, [params]):
        """[Description]"""
        # Key logic
```

**Usage example:**
```python
from [module] import [Component]

# Create instance
component = [Component]([params])

# Use it
result = await component.[method]([args])
print(f"Result: {result}")
```

**Research backing:**
- 📚 [[Research Doc]](../../../research/documentation/[topic]/[doc].md) - [Key insight]
- 📚 [[Best Practice]](../../../research/documentation/[topic]/[doc].md) - [Why this approach]

---

### 2. [Component Name]

[Repeat structure for each component]

---

### 3. [Component Name]

[Repeat structure for each component]

---

## Integration Points

### Integrates with Phase [X-1] Components

**Connection to [Previous Component]:**
```python
# File: src/[module]/[component].py

from .[phase_x_component] import [Class]

class [NewComponent]:
    def __init__(self, [phase_x_component]):
        # Uses Phase [X-1] component
        self.[component] = [phase_x_component]

    async def [method](self):
        # Calls Phase [X-1] functionality
        result = await self.[component].[method]()
        return result
```

### Integrates with External Systems

**Connection to [External System]:**
- Purpose: [Why we connect to this]
- Method: [How we connect]
- Configuration: [What's needed]

```python
# Configuration example
system = [ExternalSystem](
    host=os.getenv("[SYSTEM]_HOST"),
    port=int(os.getenv("[SYSTEM]_PORT")),
    # ... other config
)
```

---

## Tests

### Unit Tests

**File:** `tests/unit/test_[component].py` ([count] tests)

**Test coverage:**
```
☑ Happy path scenarios: [count] tests
☑ Edge cases: [count] tests
☑ Error handling: [count] tests
☑ Integration points: [count] tests
```

**Key tests:**

1. **test_[main_functionality]**
   - Tests: [What is being tested]
   - Expected: [Expected behavior]

2. **test_[edge_case]**
   - Tests: [What edge case]
   - Expected: [Expected behavior]

3. **test_[error_handling]**
   - Tests: [What error condition]
   - Expected: [Expected error handling]

**Run tests:**
```bash
# Run all Phase [X] unit tests
pytest tests/unit/test_[component]*.py -v

# Run specific test
pytest tests/unit/test_[component].py::test_[function] -v

# Run with coverage
pytest tests/unit/test_[component].py --cov=[module] --cov-report=html
```

### Integration Tests

**File:** `tests/integration/test_[component]_integration.py` ([count] tests)

**Test scenarios:**
```
☑ End-to-end workflows: [count] tests
☑ Cross-component integration: [count] tests
☑ Database integration: [count] tests
☑ External API integration: [count] tests
```

**Key integration tests:**

1. **test_[workflow_name]**
   - Tests: [Complete workflow description]
   - Components involved: [List]
   - Expected: [Expected outcome]

**Run integration tests:**
```bash
# Run all Phase [X] integration tests
pytest tests/integration/test_[component]_integration.py -v
```

### Test Results

```
==================== [X] passed in [Y]s ====================

Coverage Report:
[module]/[component].py      [XX]%
[module]/[component2].py     [XX]%
---------------------------------
TOTAL                         [XX]%

☑ All tests passing
☑ Coverage >= 80%
```

---

## Examples

### Configuration Example

**File:** `examples/router_config_phase[X].py`

```python
"""
[Feature Name] Configuration - Phase [X] ([Phase Name])

This configuration enables:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Requirements:
- [Requirement 1]
- [Requirement 2]
"""

import os
from [module] import [MainClass]

async def create_phase[X]_[system]():
    """Create [system] with Phase [X] features enabled."""

    [system] = [MainClass](
        # Phase [X-1]: [Previous phase features] (ENABLED)
        [param1]=True,
        [param2]=True,

        # Phase [X]: [Current phase features] (NEW - ENABLED)
        enable_[feature1]=True,      # ← NEW
        enable_[feature2]=True,      # ← NEW
        [feature_param]=[value],     # ← NEW

        # Configuration
        [config_param]=os.getenv("[ENV_VAR]"),
    )

    await [system].initialize()

    print("✅ Phase [X] [system] initialized!")
    print("   - [Feature 1]: ENABLED")
    print("   - [Feature 2]: ENABLED")

    return [system]


if __name__ == "__main__":
    import asyncio
    [system] = asyncio.run(create_phase[X]_[system]())

    # Example usage
    result = asyncio.run([system].[method]([example_args]))
    print(f"\nResult: {result}")
```

### Usage Examples

See [../examples/](../examples/) for complete working examples.

---

## Configuration

### New Parameters

**Added in Phase [X]:**

```python
[SystemClass](
    # ... existing params ...

    # NEW: [Feature 1]
    enable_[feature1]=True,          # Enable [feature description]
    [feature1_param]=[default],      # [Parameter description]

    # NEW: [Feature 2]
    enable_[feature2]=True,          # Enable [feature description]
    [feature2_param]=[default],      # [Parameter description]
)
```

### Environment Variables

**Required:**
```bash
# [Feature 1]
export [ENV_VAR]="[value]"

# [Feature 2]
export [ENV_VAR]="[value]"
```

**Optional:**
```bash
# [Feature tuning]
export [ENV_VAR]="[default_value]"  # Optional: [description]
```

---

## Performance Metrics

### Baseline (Before Phase [X])

| Metric | Value | Measured |
|--------|-------|----------|
| [Metric 1] | [Value] | [Date] |
| [Metric 2] | [Value] | [Date] |
| [Metric 3] | [Value] | [Date] |

### Target (Phase [X] Goals)

| Metric | Target | Expected Improvement |
|--------|--------|---------------------|
| [Metric 1] | [Value] | +[XX]% |
| [Metric 2] | [Value] | +[XX]% |
| [Metric 3] | [Value] | +[XX]% |

### Actual (Phase [X] Results)

| Metric | Actual | Improvement | Status |
|--------|--------|-------------|--------|
| [Metric 1] | [Value] | +[XX]% | [✅/⚠️/❌] |
| [Metric 2] | [Value] | +[XX]% | [✅/⚠️/❌] |
| [Metric 3] | [Value] | +[XX]% | [✅/⚠️/❌] |

---

## Known Issues & Limitations

### Known Issues

1. **[Issue Title]** ([Priority])
   - **Description:** [Brief description]
   - **Workaround:** [Temporary solution]
   - **Fix planned:** Phase [X+1] or [Date]

2. **[Issue Title]** ([Priority])
   - [Same structure]

### Current Limitations

- **[Limitation 1]:** [Description and why it exists]
- **[Limitation 2]:** [Description and why it exists]

### Future Improvements

Planned for Phase [X+1]:
- [ ] [Improvement 1]
- [ ] [Improvement 2]
- [ ] [Improvement 3]

---

## Migration Guide

### Upgrading from Phase [X-1]

**Before Phase [X]:**
```python
[system] = [SystemClass](
    enable_[old_feature]=True,
)
```

**After Phase [X]:**
```python
[system] = [SystemClass](
    # Phase [X-1] features (keep enabled)
    enable_[old_feature]=True,

    # Phase [X] features (opt-in)
    enable_[new_feature]=True,  # ← ADD THIS
    [new_param]=[value],        # ← ADD THIS
)
```

**Breaking changes:** None (backward compatible) ✅

**Deprecations:** None

---

## Dependencies

### New Dependencies Added

```txt
# Added in Phase [X]
[package-name]==[version]  # Purpose: [description]
[package-name]==[version]  # Purpose: [description]
```

**Install:**
```bash
pip install -r requirements.txt
```

### Version Requirements

| Dependency | Required Version | Why |
|------------|-----------------|-----|
| [Package 1] | >= [version] | [Reason/feature needed] |
| [Package 2] | >= [version] | [Reason/feature needed] |

---

## Research & Design Decisions

### Why This Approach?

**Decision:** [Design decision made]
**Alternatives considered:**
- [Alternative 1]: [Why not chosen]
- [Alternative 2]: [Why not chosen]
**Chosen approach:** [Why this was best]

**Research support:**
- 📚 [[Research Doc]](../../../research/documentation/[topic]/[doc].md)
- Benchmark: [Performance numbers]
- Industry standard: [Reference]

### Key Design Patterns

1. **[Pattern Name]**
   - **Where used:** [Component/file]
   - **Why:** [Rationale]
   - **Alternative:** [What we didn't use and why]

2. **[Pattern Name]**
   - [Same structure]

---

## Lessons Learned

### What Went Well ✅

- [Success 1]: [Description]
- [Success 2]: [Description]
- [Success 3]: [Description]

### What Could Be Improved ⚠️

- [Challenge 1]: [Description and learning]
- [Challenge 2]: [Description and learning]

### Recommendations for Future Phases

- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]

---

## Timeline

### Actual Timeline

```
Week [X]:
  Day 1-2:  [Component 1] implementation
  Day 3-4:  [Component 2] implementation
  Day 5-6:  [Component 3] implementation
  Day 7-8:  Testing and examples
  Day 9-10: Documentation and cleanup

Week [Y]:
  Day 1-3:  Integration testing
  Day 4-5:  Performance validation
  Day 6-7:  Context compact and Phase [X+1] prep
```

### Variance from Plan

- **Planned:** [X] days
- **Actual:** [Y] days
- **Variance:** [+/-Z] days
- **Reason:** [Why variance occurred]

---

## Next Steps

### Phase [X+1]: [Next Phase Name]

**Starting:** Week [Y]
**Components planned:**
- [Component 1]
- [Component 2]
- [Component 3]

**Dependencies from Phase [X]:**
- [What Phase [X+1] needs from this phase]

**See:** [README_PHASE[X+1].md](./README_PHASE[X+1].md)

---

## References

### Internal Documentation
- [IMPROVEMENT-PLAN.md](./IMPROVEMENT-PLAN.md) - Overall feature plan
- [IMPLEMENTATION-GUIDE.md](./IMPLEMENTATION-GUIDE.md) - Implementation instructions
- [README.md](./README.md) - Feature overview

### Research Documentation
- [[Research Doc 1]](../../../research/documentation/[topic]/[doc].md)
- [[Research Doc 2]](../../../research/documentation/[topic]/[doc].md)

### Related Phases
- [README_PHASE[X-1].md](./README_PHASE[X-1].md) - Previous phase
- [README_PHASE[X+1].md](./README_PHASE[X+1].md) - Next phase

---

**Phase [X] Status:** [✅ Complete and ready for next phase]
**Context Compacted:** [✅ Yes / ⭕ No]
**Ready for Phase [X+1]:** [✅ Yes / ⭕ No]
