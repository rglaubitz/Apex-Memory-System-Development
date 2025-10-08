# Upgrades

**Feature and system upgrade tracking**

This directory tracks the complete lifecycle of all features and system upgrades using the Features Implementation Workflow.

---

## Directory Structure

```
upgrades/
├── planned/        # Features identified but not yet started
├── active/         # Features currently being implemented
└── completed/      # Features successfully deployed
```

---

## Upgrade Lifecycle

```
1. PLANNED        →  2. ACTIVE         →  3. COMPLETED
   (Research)         (Implementation)      (Deployed)

   ↓                  ↓                     ↓

- Problem identified  - Phase 1: RDF        - All phases complete
- Initial scope       - Phases 2-5: Code    - Deployed to production
- Stakeholder buy-in  - Phase 6: Docs       - Archived for reference
                      - Phase 7: Ship
```

---

## Status Definitions

### 📝 Planned (`planned/`)

**Criteria:**
- Problem identified
- Initial scope defined
- Not yet started implementation
- Research phase not begun

**Activities:**
- Feature identification
- Problem statement
- Initial README
- Stakeholder alignment

**Files:**
- `planned/[feature-name]/README.md` - Initial scope

**Timeline:** Ongoing (no deadline)

---

### 🚧 Active (`active/`)

**Criteria:**
- Implementation in progress
- Research phase complete OR started
- Not yet deployed to production

**Activities:**
- Phase 1: RDF (Research, Document, Finalize)
- Phases 2-5: Implementation
- Phase 6: Deployment Manual
- Phase 7: Production Deployment

**Files:**
- `active/[feature-name]/IMPROVEMENT-PLAN.md`
- `active/[feature-name]/IMPLEMENTATION-GUIDE.md`
- `active/[feature-name]/README_PHASE[X].md`
- `active/[feature-name]/DEPLOYMENT-GUIDE.md`
- `active/[feature-name]/examples/`

**Timeline:** 4-8 weeks typical

---

### ✅ Completed (`completed/`)

**Criteria:**
- All implementation phases complete
- Deployed to production
- Stable for 2+ weeks
- Documentation 100% complete

**Purpose:**
- Archive for future reference
- Examples for new features
- Lessons learned
- Historical record

**Files:**
- All files from active phase
- Final performance metrics
- Post-deployment notes

**Timeline:** Archived (no further work)

---

## Workflow Integration

### Starting a New Feature

```bash
# 1. Create in planned/
mkdir -p upgrades/planned/[feature-name]
cp workflow/templates/features/README-TEMPLATE.md upgrades/planned/[feature-name]/README.md

# 2. Fill in initial scope
# Edit upgrades/planned/[feature-name]/README.md

# 3. Get stakeholder approval

# 4. Move to active/ when ready to start
mv upgrades/planned/[feature-name] upgrades/active/[feature-name]

# 5. Execute Phase 1 (RDF)
/rdf [feature-name]
# OR manually research and create IMPROVEMENT-PLAN.md
```

### During Implementation

```bash
# Feature stays in active/ throughout implementation

# Phase 1: RDF
# - Create research docs in ../../research/
# - Create IMPROVEMENT-PLAN.md
# - Create IMPLEMENTATION-GUIDE.md

# Phases 2-5: Implementation
# - Implement Phase X
# - Generate tests
# - Create examples
# - Update docs
# - Context compact
# - Move to Phase X+1

# Phase 6: Deployment Manual
# - Create deployment/TESTING.md
# - Create deployment/PRODUCTION-ROLLOUT.md
# - Create deployment/TROUBLESHOOTING.md
# - Create deployment/examples/

# Phase 7: Deploy
# - Follow deployment guide
# - Monitor production
```

### Completing a Feature

```bash
# 1. Verify completion criteria
# ☑ All phases complete
# ☑ Deployed to production
# ☑ Stable for 2+ weeks
# ☑ Documentation 100% complete

# 2. Move to completed/
mv upgrades/active/[feature-name] upgrades/completed/[feature-name]

# 3. Update completed/README.md with entry

# 4. Commit
git add upgrades/
git commit -m "feat: Complete [feature-name] upgrade"
git push
```

---

## Current Status

**Summary:** [X] planned | [Y] active | [Z] completed

### Planned (📝)

| Feature | Priority | Added | Notes |
|---------|----------|-------|-------|
| [Feature 1] | High | [Date] | [Brief note] |
| [Feature 2] | Medium | [Date] | [Brief note] |

**See:** [`planned/README.md`](./planned/README.md)

---

### Active (🚧)

| Feature | Phase | Progress | Timeline |
|---------|-------|----------|----------|
| [Feature 1] | Phase X | XX% | Week Y of Z |

**See:** [`active/README.md`](./active/README.md)

---

### Completed (✅)

| Feature | Completed | Impact | Stats |
|---------|-----------|--------|-------|
| [Feature 1] | [Date] | [Impact rating] | [Files/Tests/Docs] |

**See:** [`completed/README.md`](./completed/README.md)

---

## Best Practices

### DO ✅

1. **Start in planned/** - Don't skip initial planning
2. **Move to active/ when starting** - Clear status
3. **Keep active/ organized** - One directory per feature
4. **Complete all phases** - Don't skip deployment manual
5. **Archive to completed/** - Preserve for reference
6. **Update status regularly** - Keep README current

### DON'T ❌

1. **Skip planned/ phase** - Always scope first
2. **Start multiple active features** - Focus on one
3. **Leave features in active/ forever** - Complete or cancel
4. **Delete completed/** - Archive, don't delete
5. **Skip documentation** - Always complete docs
6. **Forget to update status** - Keep tracking current

---

## File Organization

### Planned Feature

```
upgrades/planned/[feature-name]/
└── README.md              # Initial scope and problem statement
```

### Active Feature

```
upgrades/active/[feature-name]/
├── README.md                      # Feature overview and progress
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

### Completed Feature

```
upgrades/completed/[feature-name]/
├── [All files from active]
└── POST-DEPLOYMENT-NOTES.md       # Lessons learned
```

---

## Metrics & Reporting

### Feature Complexity

**Small Feature:** 2-4 weeks
- 1 research doc
- 10+ implementation files
- 15+ tests
- 2-3 deployment examples

**Medium Feature:** 4-6 weeks
- 3-5 research docs
- 15+ implementation files
- 25+ tests
- 4-6 deployment examples

**Large Feature:** 6-8 weeks
- 8+ research docs
- 20+ implementation files
- 30+ tests
- 8+ deployment examples

### Success Metrics

**Quality:**
- ✅ 100% documentation coverage
- ✅ 80%+ test coverage
- ✅ Zero rework required
- ✅ All examples working

**Timeline:**
- ✅ On schedule (within 1 week of estimate)
- ✅ Predictable (timeline known in Phase 1)
- ✅ Manageable (context compacted 4+ times)

**Impact:**
- ✅ Measurable improvement
- ✅ Production-stable
- ✅ Team adoption
- ✅ User satisfaction

---

## Templates

All feature templates available in:
- [`../workflow/templates/features/`](../workflow/templates/features/)

**Available templates:**
- IMPROVEMENT-PLAN-TEMPLATE.md
- IMPLEMENTATION-GUIDE-TEMPLATE.md
- DEPLOYMENT-GUIDE-TEMPLATE.md
- README-TEMPLATE.md
- PHASE-README-TEMPLATE.md

---

## Related Documentation

- [Features Implementation Workflow](../workflow/FEATURES-IMPLEMENTATION-WORKFLOW.md) - Complete guide
- [Quick Start](../workflow/FEATURES-QUICK-START.md) - One-page cheat sheet
- [Phase Checklist](../workflow/PHASE-IMPLEMENTATION-CHECKLIST.md) - Detailed checklist
- [Research Organization](../research/README.md) - Research standards

---

## Examples

### Successful Feature: Query Router (October 2025)

**Timeline:** 8 weeks
**Lifecycle:** Planned → Active → Completed

**Stats:**
- 8 research documents
- 20 implementation files
- 30+ tests
- 8 deployment examples
- 4 deployment guides
- Zero rework

**See full example:** [`completed/query-router/`](./completed/query-router/)

---

## Next Steps

### To Start a New Feature

1. Read [Features Implementation Workflow](../workflow/FEATURES-IMPLEMENTATION-WORKFLOW.md)
2. Create in `planned/[feature-name]/`
3. Fill in initial scope
4. Move to `active/` when ready
5. Execute Phase 1 (RDF)
6. Follow 7-phase workflow
7. Move to `completed/` when done

### To Track Progress

- Update feature README regularly
- Mark phases complete in IMPLEMENTATION_STATE.md
- Update this README with current status
- Keep metrics current

---

**The upgrades directory provides complete visibility into all feature work from identification to completion.**
