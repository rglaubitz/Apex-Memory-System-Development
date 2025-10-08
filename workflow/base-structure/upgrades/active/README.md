# Active Upgrades

**Features currently being implemented**

This directory contains features that are actively being worked on, following the Features Implementation Workflow.

---

## Purpose

**Active upgrades are:**
- ✅ Implementation in progress
- ✅ Research phase complete OR started
- ✅ Following 7-phase workflow
- ⭕ Not yet deployed to production

**Use this directory to:**
- Track current feature work
- Monitor implementation progress
- Store all phase documentation
- Manage deployment preparation

---

## Current Active Upgrades

**Total:** [X] features in progress

| Feature | Phase | Progress | Timeline | Notes |
|---------|-------|----------|----------|-------|
| [Feature 1] | Phase 3 | 45% | Week 4 of 8 | [Brief status] |
| [Feature 2] | Phase 1 | 15% | Week 1 of 6 | [Brief status] |

---

## Lifecycle Status

```
PLANNED → [ACTIVE] → COMPLETED
           ↑
         You are here

- Research phase begun
- Implementation in progress
- Following 7-phase workflow
- Documentation being created
```

---

## Criteria for Active Status

### Must Have

**To be in active/:**
- ✅ Problem statement clear
- ✅ Stakeholder approval
- ✅ Phase 1 (RDF) started OR completed
- ✅ Developer capacity allocated
- ✅ Timeline estimated

### Progression

**Moves from planned/ when:**
- Ready to start implementation
- Research phase begins
- Developer starts Phase 1 (RDF)

**Moves to completed/ when:**
- All phases complete (Phase 1-7)
- Deployed to production
- Stable for 2+ weeks
- Documentation 100% complete

---

## Features Implementation Workflow

**Active features follow the 7-phase workflow:**

### Phase 1: RDF (Research, Document, Finalize)
- Research latest approaches
- Create IMPROVEMENT-PLAN.md
- Create IMPLEMENTATION-GUIDE.md
- Finalize scope and timeline

**Timeline:** Week 1-2 (varies by complexity)

### Phase 2-5: Implementation Phases
- Implement feature incrementally
- Generate tests proactively
- Create examples
- Update documentation
- Context compact between phases

**Timeline:** Week 3-6 (4 phases x 1 week each)

### Phase 6: Deployment Manual
- Create DEPLOYMENT-GUIDE.md
- Create deployment/TESTING.md
- Create deployment/PRODUCTION-ROLLOUT.md
- Create deployment/TROUBLESHOOTING.md
- Create deployment examples

**Timeline:** Week 7

### Phase 7: Ship It
- Follow deployment guide
- Deploy to production
- Monitor for issues
- Document lessons learned

**Timeline:** Week 8

**For full workflow details, see:** `../../workflow/FEATURES-IMPLEMENTATION-WORKFLOW.md`

---

## Directory Structure

### Minimal Active Feature (Phase 1)

```
upgrades/active/[feature-name]/
├── README.md                      # Feature overview
├── IMPROVEMENT-PLAN.md            # Comprehensive spec
└── IMPLEMENTATION-GUIDE.md        # Step-by-step guide
```

### Mid-Implementation (Phase 3)

```
upgrades/active/[feature-name]/
├── README.md                      # Feature overview
├── IMPROVEMENT-PLAN.md            # Comprehensive spec
├── IMPLEMENTATION-GUIDE.md        # Step-by-step guide
├── IMPLEMENTATION_STATE.md        # Current progress
├── CHANGELOG.md                   # Phase-by-phase changes
├── README_PHASE1.md               # Phase 1 docs
├── README_PHASE2.md               # Phase 2 docs
├── README_PHASE3.md               # Phase 3 docs (current)
└── examples/                      # Feature examples
```

### Complete Active Feature (Ready to Ship)

```
upgrades/active/[feature-name]/
├── README.md                      # Feature overview
├── IMPROVEMENT-PLAN.md            # Comprehensive spec
├── IMPLEMENTATION-GUIDE.md        # Step-by-step guide
├── IMPLEMENTATION_STATE.md        # Current progress
├── CHANGELOG.md                   # Phase-by-phase changes
├── README_PHASE1.md               # Phase 1 docs
├── README_PHASE2.md               # Phase 2 docs
├── README_PHASE3.md               # Phase 3 docs
├── README_PHASE4.md               # Phase 4 docs
├── DEPLOYMENT-GUIDE.md            # Deployment procedures
├── deployment/
│   ├── TESTING.md                 # Testing guide
│   ├── PRODUCTION-ROLLOUT.md      # Rollout strategy
│   ├── TROUBLESHOOTING.md         # Issue resolution
│   └── examples/                  # Deployment examples
└── examples/                      # Feature examples
```

---

## File Descriptions

### Core Documents

**README.md**
- Feature overview and current status
- Problem statement
- Expected impact
- Progress tracking
- Links to all other docs

**IMPROVEMENT-PLAN.md**
- Comprehensive specification
- Research foundation
- Technical approach
- Success metrics
- Implementation phases

**IMPLEMENTATION-GUIDE.md**
- Step-by-step implementation guide
- Phase breakdowns
- Code snippets
- Testing strategy
- Deployment preparation

**IMPLEMENTATION_STATE.md**
- Current phase and progress
- What's been completed
- What's next
- Blockers and issues
- Timeline tracking

**CHANGELOG.md**
- Phase-by-phase changes
- What was added/changed/fixed
- Decisions made
- Lessons learned

### Phase Documentation

**README_PHASE[X].md**
- Phase-specific implementation notes
- What was built in this phase
- Key decisions made
- Tests generated
- Context compaction summary

### Deployment Documentation

**DEPLOYMENT-GUIDE.md**
- Pre-deployment checklist
- Deployment steps
- Post-deployment validation
- Rollback procedures

**deployment/TESTING.md**
- Testing strategy
- Test cases
- Performance benchmarks
- Edge cases

**deployment/PRODUCTION-ROLLOUT.md**
- Rollout timeline
- Monitoring setup
- Success criteria
- Rollback triggers

**deployment/TROUBLESHOOTING.md**
- Common issues
- Resolution steps
- Contact information
- Escalation procedures

### Supporting Materials

**examples/**
- Code examples
- Usage demonstrations
- Integration patterns
- Best practices

**deployment/examples/**
- Deployment scripts
- Configuration examples
- Monitoring dashboards
- Alert rules

---

## Progress Tracking

### Phase Progress

**Track progress using:**

```markdown
## Implementation Progress

**Current Phase:** Phase 3 - [Phase Name]
**Overall Progress:** 45%

### Completed ✅
- ✅ Phase 1: RDF (Week 1-2)
- ✅ Phase 2: [Phase Name] (Week 3)

### In Progress 🚧
- 🚧 Phase 3: [Phase Name] (Week 4)
  - ✅ Feature A implemented
  - 🚧 Feature B in progress (60%)
  - ⭕ Feature C not started

### Upcoming ⭕
- ⭕ Phase 4: [Phase Name] (Week 5)
- ⭕ Phase 5: [Phase Name] (Week 6)
- ⭕ Phase 6: Deployment Manual (Week 7)
- ⭕ Phase 7: Ship It (Week 8)
```

### Timeline Tracking

**Update weekly:**

```markdown
## Timeline

**Start Date:** [Date]
**Target Completion:** [Date]
**Current Week:** Week 4 of 8

**Status:** ✅ On Track | ⚠️ At Risk | 🚨 Delayed

**Milestones:**
- [x] Phase 1 Complete - [Date] ✅
- [x] Phase 2 Complete - [Date] ✅
- [ ] Phase 3 Complete - [Target Date]
- [ ] Phase 4 Complete - [Target Date]
- [ ] Deployment Ready - [Target Date]
- [ ] Production Deployment - [Target Date]
```

---

## Best Practices

### DO ✅

1. **Follow the 7-phase workflow** - Don't skip phases
2. **Context compact between phases** - Prevent context overflow
3. **Generate tests proactively** - Don't wait to be asked
4. **Update progress regularly** - Keep documentation current
5. **Create examples** - Help future users understand
6. **Document decisions** - Explain why, not just what
7. **Complete deployment manual** - Don't skip Phase 6
8. **Reference research** - Link to research docs in implementation

### DON'T ❌

1. **Skip Phase 1 (RDF)** - Research first, always
2. **Skip context compaction** - Leads to context overflow
3. **Skip test generation** - Tests are mandatory
4. **Skip deployment manual** - Phase 6 is critical
5. **Leave incomplete docs** - Finish all documentation
6. **Make assumptions** - Ground decisions in research
7. **Implement without plan** - IMPROVEMENT-PLAN.md comes first
8. **Deploy without testing** - Follow TESTING.md thoroughly

---

## Moving Through Phases

### Starting Phase 1 (RDF)

**When moving from planned/ to active/:**

```bash
# 1. Move feature to active
mv upgrades/planned/[feature-name] upgrades/active/[feature-name]

# 2. Begin Phase 1 (RDF)
# - Research latest approaches
# - Create IMPROVEMENT-PLAN.md
# - Create IMPLEMENTATION-GUIDE.md

# 3. Update tracking
# Update upgrades/active/README.md
# Update upgrades/planned/README.md (remove from list)

# 4. Commit
git add upgrades/
git commit -m "start: Begin [feature-name] implementation"
git push
```

### Between Implementation Phases

**After completing each phase:**

```bash
# 1. Context compact
# - Summarize phase work in README_PHASE[X].md
# - Update IMPLEMENTATION_STATE.md
# - Update CHANGELOG.md

# 2. Generate tests
# - Create/update test files
# - Run test suite
# - Document coverage

# 3. Update progress
# - Mark phase complete in README.md
# - Update progress percentage
# - Note any timeline changes

# 4. Commit phase work
git add .
git commit -m "feat([feature]): Complete Phase [X] - [Phase Name]"
git push

# 5. Begin next phase
# - Review IMPLEMENTATION-GUIDE.md for next phase
# - Update IMPLEMENTATION_STATE.md
# - Start implementation
```

### Completing Feature

**After Phase 7 (Ship It):**

```bash
# 1. Verify completion criteria
# ☑ All phases complete (1-7)
# ☑ Deployed to production
# ☑ Stable for 2+ weeks
# ☑ Documentation 100% complete
# ☑ Tests passing
# ☑ No critical issues

# 2. Create post-deployment notes
# Document lessons learned
# Note any issues encountered
# Record final metrics

# 3. Move to completed/
mv upgrades/active/[feature-name] upgrades/completed/[feature-name]

# 4. Update tracking
# Update upgrades/completed/README.md (add entry)
# Update upgrades/active/README.md (remove from list)

# 5. Commit
git add upgrades/
git commit -m "feat: Complete [feature-name] upgrade"
git push
```

---

## Integration with Workflow

### Research Integration

**Link research documents:**

```markdown
## Research Foundation

**Official Documentation (Tier 1):**
- [Framework Guide](../../research/documentation/[framework]/[doc].md)
- [API Reference](../../research/documentation/[framework]/[api].md)

**Verified Examples (Tier 2):**
- [Pattern Example](../../research/examples/[pattern]/[example].md)

**Architecture Decisions:**
- [ADR-001](../../research/architecture-decisions/ADR-001-[title].md)
```

### Project Integration

**Reference implementation:**

```markdown
## Implementation Location

**Source Files:**
- `../[project-name]/src/[module]/[file].py`
- `../[project-name]/src/[module]/[file].py`

**Tests:**
- `../[project-name]/tests/unit/test_[feature].py`
- `../[project-name]/tests/integration/test_[feature].py`
```

### Claude Integration

**Use project-specific commands:**

```bash
# Run tests for this feature
/test-feature [feature-name]

# Deploy to staging
/deploy-staging [feature-name]

# Review implementation
/review [feature-name]
```

---

## Monitoring Active Features

### Weekly Status Review

**Review all active features:**

```markdown
## Weekly Status Review - [Date]

### Feature 1: [Name]
- Phase: 3 of 7
- Progress: 45%
- Status: ✅ On Track
- Notes: [Any updates]

### Feature 2: [Name]
- Phase: 1 of 7
- Progress: 15%
- Status: ⚠️ Blocked
- Notes: Waiting on API access

**Actions Needed:**
- [ ] Resolve Feature 2 blocker
- [ ] Review Feature 1 Phase 3 PR
```

### Risk Management

**Track risks:**

```markdown
## Risks

### Feature 1: [Name]

**Timeline Risk:** ⚠️ Medium
- Phase 3 taking longer than expected
- Mitigation: Added 1 week buffer

**Technical Risk:** ✅ Low
- Clear implementation path
- All dependencies verified

**Dependency Risk:** ✅ Low
- No external blockers
- All APIs accessible
```

---

## Success Metrics

### Quality Metrics

**Track for each feature:**

```markdown
## Success Metrics

**Documentation:**
- ✅ 100% documentation coverage
- ✅ All templates completed
- ✅ Examples provided

**Testing:**
- ✅ 80%+ test coverage
- ✅ All edge cases covered
- ✅ Integration tests passing

**Timeline:**
- ✅ On schedule (within 1 week of estimate)
- ✅ Phases completed as planned
- ✅ No major surprises

**Impact:**
- ✅ Measurable improvement
- ✅ User feedback positive
- ✅ Performance targets met
```

### Performance Tracking

**Monitor implementation velocity:**

```markdown
## Velocity Metrics

**Phase Completion:**
- Phase 1: 2 weeks (estimated: 2 weeks) ✅
- Phase 2: 1 week (estimated: 1 week) ✅
- Phase 3: 1.5 weeks (estimated: 1 week) ⚠️

**Context Management:**
- Context compactions: 4
- Average context size: 60k tokens
- No context overflow: ✅

**Test Generation:**
- Tests written: 28
- Coverage: 85%
- Proactive generation: ✅
```

---

## Common Patterns

### Small Feature (2-4 weeks)

**Characteristics:**
- Single component
- 2-3 implementation phases
- Minimal research needed
- Few integration points

**Example timeline:**
- Week 1: Phase 1 (RDF)
- Week 2: Phases 2-3 (Implementation)
- Week 3: Phase 6 (Deployment Manual)
- Week 4: Phase 7 (Ship It)

### Medium Feature (4-6 weeks)

**Characteristics:**
- Multiple components
- 4 implementation phases
- Moderate research required
- Several integration points

**Example timeline:**
- Week 1-2: Phase 1 (RDF)
- Week 3-5: Phases 2-5 (Implementation)
- Week 6: Phase 6 (Deployment Manual)
- Week 7: Phase 7 (Ship It)

### Large Feature (6-8+ weeks)

**Characteristics:**
- Major system change
- 4+ implementation phases
- Extensive research required
- Many integration points

**Example timeline:**
- Week 1-2: Phase 1 (RDF)
- Week 3-6: Phases 2-5 (Implementation)
- Week 7: Phase 6 (Deployment Manual)
- Week 8: Phase 7 (Ship It)

---

## Examples

### Well-Tracked Active Feature

```markdown
# Query Router Upgrade

**Status:** Active - Phase 3 of 7
**Priority:** High
**Timeline:** 8 weeks (Week 4 of 8)

## Progress

**Overall:** 45% complete

✅ Phase 1: RDF (Week 1-2) - Complete
✅ Phase 2: Foundation (Week 3) - Complete
🚧 Phase 3: Intelligent (Week 4) - 60% complete
⭕ Phase 4: Agentic (Week 5) - Not started
⭕ Phase 5: Advanced (Week 6) - Not started
⭕ Phase 6: Deployment Manual (Week 7) - Not started
⭕ Phase 7: Ship It (Week 8) - Not started

## Current Work

**This week (Phase 3):**
- ✅ Adaptive weight learning implemented
- 🚧 Semantic caching in progress
- ⭕ GraphRAG hybrid search next

## Metrics

**Tests:** 28 (85% coverage)
**Docs:** 100% complete
**Performance:** +15% query speed improvement so far
```

---

## Troubleshooting

### Feature Stuck in Active

**Problem:** Feature has been in active/ for >12 weeks

**Solutions:**
1. **Re-scope:** Break into smaller features
2. **Pause:** Move back to planned/ until capacity available
3. **Cancel:** Document reason and remove
4. **Get help:** Add additional developer

### Context Overflow

**Problem:** Context size exceeding limits

**Solutions:**
1. **Compact now:** Summarize current work immediately
2. **Split phase:** Break current phase into sub-phases
3. **Archive:** Move verbose logs to separate files
4. **Review:** Check if unnecessary content in context

### Timeline Delays

**Problem:** Feature falling behind schedule

**Solutions:**
1. **Add buffer:** Extend timeline by 1-2 weeks
2. **Reduce scope:** Move some features to future phase
3. **Get help:** Add resources or pair programming
4. **Reassess:** Check if original estimate was realistic

### Documentation Incomplete

**Problem:** Docs falling behind implementation

**Solutions:**
1. **Pause implementation:** Catch up on docs first
2. **Set reminder:** Update docs after each commit
3. **Use templates:** Speed up doc creation
4. **Review checklist:** Ensure all required docs present

---

## Templates

**All feature templates available in:**
- `../../workflow/templates/features/`

**Available templates:**
- IMPROVEMENT-PLAN-TEMPLATE.md
- IMPLEMENTATION-GUIDE-TEMPLATE.md
- DEPLOYMENT-GUIDE-TEMPLATE.md
- README-TEMPLATE.md
- PHASE-README-TEMPLATE.md

---

## Related Documentation

- [Features Implementation Workflow](../../workflow/FEATURES-IMPLEMENTATION-WORKFLOW.md) - Complete guide
- [Quick Start](../../workflow/FEATURES-QUICK-START.md) - One-page cheat sheet
- [Phase Checklist](../../workflow/PHASE-IMPLEMENTATION-CHECKLIST.md) - Detailed checklist
- [Research Organization](../research/README.md) - Research standards
- [Upgrades Overview](../README.md) - Upgrade lifecycle

---

## Decision Criteria

### Should This Feature Stay Active?

**YES, keep active if:**
- ✅ Work is actively progressing
- ✅ Developer capacity allocated
- ✅ Timeline is realistic
- ✅ No major blockers
- ✅ Documentation current

**NO, reconsider if:**
- ❌ No progress in >2 weeks
- ❌ Developer unavailable
- ❌ Timeline unrealistic
- ❌ Blocked indefinitely
- ❌ Documentation abandoned

**Consider:**
- Move back to planned/ if blocked long-term
- Move to completed/ if finished
- Cancel if no longer needed (document reason)

---

## Next Steps

### For New Active Feature

1. **Move from planned/:**
   ```bash
   mv upgrades/planned/[feature-name] upgrades/active/[feature-name]
   ```

2. **Begin Phase 1 (RDF):**
   - Research latest approaches
   - Create IMPROVEMENT-PLAN.md
   - Create IMPLEMENTATION-GUIDE.md

3. **Set up tracking:**
   - Create IMPLEMENTATION_STATE.md
   - Update progress in README.md
   - Add to active/ tracking table

4. **Follow workflow:**
   - Execute phases 2-7
   - Context compact between phases
   - Generate tests proactively

### For Ongoing Feature

1. **Update progress regularly:**
   - Update IMPLEMENTATION_STATE.md
   - Update README.md progress section
   - Update CHANGELOG.md with changes

2. **Between phases:**
   - Context compact
   - Generate tests
   - Update documentation

3. **Monitor timeline:**
   - Weekly progress reviews
   - Adjust estimates if needed
   - Document delays and reasons

4. **When complete:**
   - Verify all criteria met
   - Create post-deployment notes
   - Move to completed/

---

**Active features represent current development work. Keep them well-documented, properly tracked, and moving forward.**
