# Planned Upgrades

**Features identified but not yet started**

This directory contains features that have been identified and scoped but implementation has not begun.

---

## Purpose

**Planned upgrades are:**
- ✅ Identified and documented
- ✅ Problem statement defined
- ✅ Initial scope established
- ⭕ Research not yet started
- ⭕ Implementation not yet started

**Use this directory to:**
- Track future feature work
- Prioritize upcoming work
- Build feature backlog
- Get stakeholder alignment

---

## Current Planned Upgrades

**Total:** [X] features planned

| Feature | Priority | Added | Est. Timeline | Notes |
|---------|----------|-------|---------------|-------|
| [Feature 1] | High | [Date] | 6-8 weeks | [Brief note] |
| [Feature 2] | Medium | [Date] | 4-6 weeks | [Brief note] |
| [Feature 3] | Low | [Date] | 2-4 weeks | [Brief note] |

---

## Adding a New Feature

### 1. Create Feature Directory

```bash
mkdir -p upgrades/planned/[feature-name]
cd upgrades/planned/[feature-name]
```

### 2. Copy README Template

```bash
cp ../../../workflow/templates/features/README-TEMPLATE.md README.md
```

### 3. Fill In Initial Scope

Edit `README.md` with:

```markdown
# [Feature Name]

**Status:** Planned
**Priority:** [High/Medium/Low]
**Est. Timeline:** [X weeks]

## Problem Statement

[2-3 paragraphs describing the problem this feature solves]

**Why this matters:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

## Initial Scope

**What we'll build:**
- [Component 1]
- [Component 2]
- [Component 3]

**What's out of scope:**
- [What we won't do]
- [Future considerations]

## Expected Impact

**Metrics we'll improve:**
- [Metric 1]: [Current] → [Target]
- [Metric 2]: [Current] → [Target]

## Dependencies

**Requires:**
- [Dependency 1]
- [Dependency 2]

**Blocked by:**
- [Blocker if any]

## Next Steps

1. Get stakeholder approval
2. Move to active/
3. Execute Phase 1 (RDF)
```

### 4. Update This README

Add entry to the table above.

### 5. Commit

```bash
git add upgrades/planned/[feature-name]/
git commit -m "plan: Add [feature-name] to planned upgrades"
git push
```

---

## Moving to Active

**When ready to start:**

```bash
# 1. Verify prerequisites
# ☑ Problem statement clear
# ☑ Stakeholders aligned
# ☑ Priority established
# ☑ Timeline estimated

# 2. Move to active
mv upgrades/planned/[feature-name] upgrades/active/[feature-name]

# 3. Begin Phase 1 (RDF)
/rdf [feature-name]
# OR manually create IMPROVEMENT-PLAN.md

# 4. Update tracking
# Update upgrades/active/README.md
# Update upgrades/planned/README.md (remove from list)

# 5. Commit
git add upgrades/
git commit -m "start: Begin [feature-name] implementation"
git push
```

---

## Priority Guidelines

### High Priority

**Criteria:**
- Critical business need
- Blocking other work
- Security/compliance requirement
- High user impact

**Timeline:** Start within 1-2 weeks

### Medium Priority

**Criteria:**
- Important but not urgent
- Improves existing functionality
- Moderate user impact
- Nice-to-have feature

**Timeline:** Start within 1-2 months

### Low Priority

**Criteria:**
- Future enhancement
- Low user impact
- Experimental
- Technical debt

**Timeline:** Start when capacity available

---

## Estimation Guidelines

### 2-4 Weeks (Small Feature)

**Characteristics:**
- Single component
- Limited scope
- Minimal research needed
- Few integration points

**Examples:**
- Bug fix with tests
- Small UI enhancement
- Minor API addition

### 4-6 Weeks (Medium Feature)

**Characteristics:**
- Multiple components
- Moderate scope
- Some research required
- Several integration points

**Examples:**
- New API endpoint with database
- Feature enhancement
- Performance optimization

### 6-8 Weeks (Large Feature)

**Characteristics:**
- Major system change
- Significant scope
- Extensive research required
- Many integration points

**Examples:**
- Query router upgrade
- Authentication system
- Multi-database integration

### 8+ Weeks (Epic)

**Characteristics:**
- System-wide impact
- Very large scope
- Deep research required
- Complex integration

**Consider:** Breaking into smaller features

---

## Template

### Minimal Planned Feature

```
upgrades/planned/[feature-name]/
└── README.md              # Problem statement and initial scope
```

### Content Requirements

**Required sections:**
- Problem statement
- Why it matters
- Initial scope
- Expected impact
- Dependencies

**Optional sections:**
- Research questions
- Technical considerations
- Alternatives considered
- Risk assessment

---

## Review Process

### Weekly Planning Review

**Review all planned features:**
- Priority still correct?
- Dependencies resolved?
- Ready to move to active?
- Should be deprioritized?

### Quarterly Planning

**Strategic review:**
- Align with business goals
- Reprioritize based on learnings
- Add new features
- Remove obsolete features

---

## Best Practices

### DO ✅

1. **Document problem clearly** - Why are we doing this?
2. **Set priority honestly** - Don't make everything high
3. **Estimate realistically** - Use past features as guide
4. **Track dependencies** - Note what's blocking
5. **Review regularly** - Keep list current

### DON'T ❌

1. **Skip problem statement** - Always explain why
2. **Make everything high priority** - Prioritize thoughtfully
3. **Underestimate timeline** - Be realistic
4. **Leave features planned forever** - Move or remove
5. **Skip stakeholder alignment** - Get buy-in early

---

## Decision Criteria

### Should This Feature Be Planned?

**YES, plan it if:**
- ✅ Clear business need
- ✅ Defined scope (even if rough)
- ✅ Stakeholder interest
- ✅ Feasible to build
- ✅ Aligns with goals

**NO, don't plan if:**
- ❌ Vague idea without clear need
- ❌ No stakeholder interest
- ❌ Technically infeasible
- ❌ Conflicts with strategy
- ❌ Already exists

---

## Examples

### Well-Defined Planned Feature

```markdown
# Security Layer Enhancement

**Status:** Planned
**Priority:** High
**Est. Timeline:** 6-8 weeks

## Problem Statement

Current system lacks authentication and authorization, exposing
APIs to unauthorized access. This is a security risk and blocks
enterprise customer adoption.

**Why this matters:**
- Security vulnerability
- Regulatory compliance requirement
- Blocking $500k+ enterprise deals
- Industry standard expectation

## Initial Scope

**What we'll build:**
- OAuth2 authentication
- Role-based authorization (RBAC)
- Rate limiting per user
- Audit logging

**Out of scope (v1):**
- SSO integration (future v2)
- Multi-factor auth (future v2)

## Expected Impact

**Metrics:**
- Security score: 60/100 → 95/100
- Enterprise readiness: Blocked → Ready
- API abuse: Untracked → 0 incidents

## Dependencies

**Requires:**
- Redis for rate limiting (already available)
- PostgreSQL for user store (already available)

**Blocked by:**
- None (ready to start)

## Next Steps

1. ✅ Stakeholder approval (approved by security team)
2. ⭕ Move to active/ (when capacity available)
3. ⭕ Execute Phase 1 (RDF)
```

---

## Moving Features Out

### To Active

```bash
# When starting implementation
mv upgrades/planned/[feature-name] upgrades/active/[feature-name]
```

### To Completed (Skip Active)

```bash
# If already implemented elsewhere
mv upgrades/planned/[feature-name] upgrades/completed/[feature-name]
```

### Remove from Planned

```bash
# If no longer needed
# Document reason in commit message
rm -rf upgrades/planned/[feature-name]
git commit -m "plan: Remove [feature-name] (reason: [why])"
```

---

## Metrics

**Healthy planning metrics:**
- 3-10 features planned (not too few, not too many)
- Mix of priorities (not all high)
- Regular movement to active (features getting built)
- Regular review (quarterly at minimum)

**Warning signs:**
- 20+ features planned (too much, narrow focus)
- All features high priority (prioritization problem)
- No movement to active (planning but not building)
- Old features (>6 months) still planned (need decision)

---

## Next Steps

1. **Add your first feature:**
   ```bash
   mkdir -p upgrades/planned/your-feature
   cp ../../workflow/templates/features/README-TEMPLATE.md upgrades/planned/your-feature/README.md
   # Edit README.md
   ```

2. **Define problem clearly**
3. **Set priority**
4. **Estimate timeline**
5. **Get stakeholder approval**
6. **Move to active/ when ready to start**

---

**Keep this directory focused. Not everything needs to be planned immediately. Add features when they become concrete enough to scope.**
