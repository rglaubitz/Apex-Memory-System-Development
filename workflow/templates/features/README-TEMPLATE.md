# [Feature Name]

**Status:** [Planning / Active / Complete]
**Priority:** [High / Medium / Low]
**Timeline:** [X weeks]
**Progress:** [X]% complete

---

## Quick Reference

| Phase | Status | Completion | Documents |
|-------|--------|------------|-----------|
| Phase 0: Planning | [✅/🚧/⭕] | [Date] | [IMPROVEMENT-PLAN.md](./IMPROVEMENT-PLAN.md) |
| Phase 1: RDF | [✅/🚧/⭕] | [Date] | [Research docs](../../research/documentation/[topic]/) |
| Phase 2: Foundation | [✅/🚧/⭕] | [Date] | [README_PHASE1.md](./README_PHASE1.md) |
| Phase 3: [Name] | [✅/🚧/⭕] | [Date] | [README_PHASE2.md](./README_PHASE2.md) |
| Phase 4: [Name] | [✅/🚧/⭕] | [Date] | [README_PHASE3.md](./README_PHASE3.md) |
| Phase 5: [Name] | [✅/🚧/⭕] | [Date] | [README_PHASE4.md](./README_PHASE4.md) |
| Phase 6: Deployment | [✅/🚧/⭕] | [Date] | [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) |

**Legend:** ✅ Complete | 🚧 In Progress | ⭕ Not Started

---

## Overview

[Brief 2-3 paragraph description of the feature]

**Why this feature matters:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Expected improvements:**
- **[Metric 1]:** [Baseline] → [Target] ([Improvement]%)
- **[Metric 2]:** [Baseline] → [Target] ([Improvement]%)
- **[Metric 3]:** [Baseline] → [Target] ([Improvement]%)

---

## Research Foundation

This feature is research-backed with comprehensive documentation:

### Official Documentation (Tier 1)
- 📚 [[Framework Name]](../../research/documentation/[topic]/[doc].md) - [Key insight]
- 📚 [[API Documentation]](../../research/documentation/[topic]/[doc].md) - [Key insight]

### Verified Examples (Tier 2)
- 📚 [[Code Example]](../../research/examples/[topic]/[doc].md) - [Key insight]

### Best Practices (Tier 1)
- 📚 [[Best Practices 2025]](../../research/documentation/[topic]/best-practices-2025.md) - [Key insight]

**Research completed:** [Date]
**Total research documents:** [Count]
**All sources verified:** ✅

---

## Key Documents

### Planning Phase
- 📄 [IMPROVEMENT-PLAN.md](./IMPROVEMENT-PLAN.md) - Comprehensive feature specification
- 📄 [IMPLEMENTATION-GUIDE.md](./IMPLEMENTATION-GUIDE.md) - Step-by-step implementation guide

### Implementation Phase
- 📄 [README_PHASE1.md](./README_PHASE1.md) - Phase 1: Foundation
- 📄 [README_PHASE2.md](./README_PHASE2.md) - Phase 2: [Name]
- 📄 [README_PHASE3.md](./README_PHASE3.md) - Phase 3: [Name]
- 📄 [README_PHASE4.md](./README_PHASE4.md) - Phase 4: [Name]

### Deployment Phase
- 📄 [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) - Deployment procedures
- 📄 [deployment/TESTING.md](./deployment/TESTING.md) - Testing guide
- 📄 [deployment/PRODUCTION-ROLLOUT.md](./deployment/PRODUCTION-ROLLOUT.md) - Rollout strategy
- 📄 [deployment/TROUBLESHOOTING.md](./deployment/TROUBLESHOOTING.md) - Issue resolution

### Tracking
- 📄 [CHANGELOG.md](./CHANGELOG.md) - Detailed change log by phase
- 📄 [IMPLEMENTATION_STATE.md](./IMPLEMENTATION_STATE.md) - Current implementation status

---

## Architecture

### Components

```
[Component Architecture Diagram or Description]

Component 1: [Name]
├── Purpose: [Description]
├── Location: src/[path]/[file].py
└── Tests: tests/unit/test_[component].py

Component 2: [Name]
├── Purpose: [Description]
├── Location: src/[path]/[file].py
└── Tests: tests/integration/test_[component].py
```

### Technology Stack

| Component | Technology | Version | Why Chosen |
|-----------|------------|---------|------------|
| [Component 1] | [Tech] | [Version] | [Reason] |
| [Component 2] | [Tech] | [Version] | [Reason] |
| [Component 3] | [Tech] | [Version] | [Reason] |

**All versions verified:** ✅ (as of [Date])

---

## Implementation Progress

### Phase 1: Foundation ✅ COMPLETE

**Completed:** [Date]
**Duration:** [X weeks]

**Components implemented:**
- ✅ [Component 1] ([Line count] lines)
- ✅ [Component 2] ([Line count] lines)
- ✅ [Component 3] ([Line count] lines)

**Tests:** [Count] tests | **Coverage:** [XX]%

**Details:** [README_PHASE1.md](./README_PHASE1.md)

---

### Phase 2: [Name] 🚧 IN PROGRESS

**Started:** [Date]
**Expected completion:** [Date]

**Components to implement:**
- 🚧 [Component 1]
- ⭕ [Component 2]
- ⭕ [Component 3]

**Progress:** [XX]% complete

**Details:** [README_PHASE2.md](./README_PHASE2.md)

---

### Phase 3: [Name] ⭕ NOT STARTED

**Planned start:** [Date]
**Expected completion:** [Date]

**Components planned:**
- ⭕ [Component 1]
- ⭕ [Component 2]
- ⭕ [Component 3]

**Details:** [README_PHASE3.md](./README_PHASE3.md)

---

### Phase 4: [Name] ⭕ NOT STARTED

**Planned start:** [Date]
**Expected completion:** [Date]

**Components planned:**
- ⭕ [Component 1]
- ⭕ [Component 2]
- ⭕ [Component 3]

**Details:** [README_PHASE4.md](./README_PHASE4.md)

---

## Testing

### Test Coverage

| Test Type | Count | Coverage |
|-----------|-------|----------|
| Unit Tests | [count] | [XX]% |
| Integration Tests | [count] | [XX]% |
| E2E Tests | [count] | [XX]% |
| **Total** | **[count]** | **[XX]%** |

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific phase tests
pytest tests/unit/test_[phase]*.py -v

# Run with coverage
pytest --cov=[module] --cov-report=html
```

---

## Examples

Working examples are available in `examples/` and `deployment/examples/`:

### Configuration Examples
- [router_config_phase1.py](./examples/router_config_phase1.py) - Phase 1 configuration
- [router_config_phase2.py](./examples/router_config_phase2.py) - Phase 2 configuration
- [router_config_phase3.py](./examples/router_config_phase3.py) - Phase 3 configuration
- [router_config_phase4.py](./examples/router_config_phase4.py) - Full configuration

### Deployment Examples
- [feature_flag_setup.py](./deployment/examples/feature_flag_setup.py) - Feature flag configuration
- [gradual_rollout_script.py](./deployment/examples/gradual_rollout_script.py) - Gradual rollout automation
- [monitoring_setup.py](./deployment/examples/monitoring_setup.py) - Monitoring configuration

**All examples are copy-paste ready** ✅

---

## Performance Metrics

### Baseline (Before Implementation)

| Metric | Value | Measured |
|--------|-------|----------|
| [Metric 1] | [Value] | [Date] |
| [Metric 2] | [Value] | [Date] |
| [Metric 3] | [Value] | [Date] |

### Target (After Implementation)

| Metric | Target | Expected Improvement |
|--------|--------|---------------------|
| [Metric 1] | [Value] | +[XX]% |
| [Metric 2] | [Value] | +[XX]% |
| [Metric 3] | [Value] | +[XX]% |

### Actual (Post-Deployment)

| Metric | Actual | Improvement | Status |
|--------|--------|-------------|--------|
| [Metric 1] | [Value] | +[XX]% | [✅/⚠️/❌] |
| [Metric 2] | [Value] | +[XX]% | [✅/⚠️/❌] |
| [Metric 3] | [Value] | +[XX]% | [✅/⚠️/❌] |

---

## Deployment Status

### Current Stage

**Stage:** [Baseline / Canary / Gradual / Complete]
**Rollout:** [X]% of users
**Last updated:** [Date]

### Rollout Schedule

```
✅ Stage 1: Baseline (Day 0)       - Complete
✅ Stage 2: Feature flags (Day 0)  - Complete
🚧 Stage 3: Canary (Day 1-3)       - 5% rollout (IN PROGRESS)
⭕ Stage 4: Gradual (Day 4-14)     - 25% → 50% → 100%
⭕ Stage 5: Cleanup (Day 15+)      - Remove old code
```

### Monitoring

- **Grafana Dashboard:** http://localhost:3000/d/[dashboard-id]
- **Prometheus Metrics:** http://localhost:9090
- **Logs:** `docker logs -f [service-name]`

---

## Known Issues

### Active Issues

1. **[Issue #1]** ([Priority])
   - **Description:** [Brief description]
   - **Impact:** [Impact description]
   - **Status:** [In Progress / Blocked / Investigating]
   - **Tracking:** [Link to issue tracker]

2. **[Issue #2]** ([Priority])
   - [Same structure]

### Resolved Issues

1. **[Issue #1]** ✅
   - **Was:** [Description]
   - **Resolved:** [Date]
   - **Solution:** [Brief solution description]

---

## Next Steps

### Immediate (This Week)
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

### Short-term (This Month)
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

### Long-term (This Quarter)
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

---

## Team

| Role | Name | Responsibility |
|------|------|----------------|
| Tech Lead | [Name] | Architecture, implementation oversight |
| Developer | [Name] | [Specific components] |
| DevOps | [Name] | Deployment, monitoring |
| QA | [Name] | Testing, validation |

---

## Related Features

This feature integrates with:

1. **[[Related Feature 1]](../[feature-name]/README.md)** - [Relationship description]
2. **[[Related Feature 2]](../[feature-name]/README.md)** - [Relationship description]

---

## References

### Internal Documentation
- [IMPROVEMENT-PLAN.md](./IMPROVEMENT-PLAN.md) - Complete feature specification
- [IMPLEMENTATION-GUIDE.md](./IMPLEMENTATION-GUIDE.md) - Implementation instructions
- [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) - Deployment procedures

### Research Documentation
- [Research documentation index](../../research/documentation/[topic]/README.md)

### External Resources
- [Resource 1 Name](URL) - [Description]
- [Resource 2 Name](URL) - [Description]

---

**Last Updated:** [Date]
**Status:** [Current status]
**Next Review:** [Date]
