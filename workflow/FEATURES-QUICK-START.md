# Features Implementation Workflow - Quick Start

**One-page cheat sheet for the complete workflow**

---

## The 7 Phases

```
Phase 0: Identify → Phase 1: RDF → Phases 2-5: Implement → Phase 6: Deploy Docs → Phase 7: Ship
   (1 day)          (1 week)         (4-6 weeks)            (1 week)            (ongoing)
```

---

## Phase 0: Feature Identification (Day 1)

```bash
# Create feature directory
mkdir -p upgrades/planned/[feature-name]

# Create initial README
# - Problem statement
# - Why it matters
# - High-level approach
# - Timeline estimate
```

✅ **Complete when:** Stakeholders aligned on scope

---

## Phase 1: RDF - Research, Document, Finalize (Week 1)

### Option A: Automated
```bash
/rdf [feature-name]
```

### Option B: Manual
1. Research (Exa AI + GitHub API)
2. Document findings
3. Create IMPROVEMENT-PLAN.md
4. Create IMPLEMENTATION-GUIDE.md
5. Git commit research

✅ **Complete when:**
- 8+ research docs created
- Implementation guide ready
- All sources cited (Tier 1-2)

---

## Phases 2-5: Implementation Loop (Weeks 2-7)

### The 10-Step Pattern (For EACH Phase)

#### 1. 🛑 Enter Plan Mode
```
User: "Let's start Phase X"
Claude: [Enters plan mode]
```

#### 2. 💬 Discuss Requirements
- "What do we need for Phase X?"
- Identify research gaps
- Check dependencies
- Clarify specs

#### 3. 📚 Fill Research Gaps (if needed)
- Fetch additional docs
- Verify versions
- Find code examples

#### 4. ▶️ Exit Plan Mode
```
User: "Let's go" / "Proceed"
Claude: [Exits plan mode]
```

#### 5. 💻 Write Implementation Code
- Real working code (not pseudocode)
- 3-5 files per phase
- Proper error handling
- Structured logging

#### 6. ✨ Generate Tests Proactively
**KEY:** Claude generates tests WITHOUT being asked!
- 15-30 tests per phase
- Unit + integration
- Edge cases covered

#### 7. 📝 Create Working Examples
- Copy-paste ready
- Progressive complexity
- router_config_phase1.py → phase4.py

#### 8. 📄 Update Documentation
- README_PHASEX.md
- CHANGELOG.md
- IMPLEMENTATION_STATE.md

#### 9. 🗜️ Context Compact
**CRITICAL:** Compact before next phase!
```
User: "Let's compact before Phase X"
```

#### 10. ✅ Mark Phase Complete
```
☑ Code implemented
☑ Tests generated (15-30)
☑ Examples created
☑ Docs updated
☑ Context compacted
☑ Ready for next phase
```

---

## Phase 6: Deployment Manual (Week 8)

### Create 4 Guides + Examples

```
upgrades/[feature]/
├── DEPLOYMENT-GUIDE.md          # Hub document
└── deployment/
    ├── TESTING.md                # How to run all tests
    ├── PRODUCTION-ROLLOUT.md     # Stage-by-stage deployment
    ├── TROUBLESHOOTING.md        # Common issues + fixes
    └── examples/                 # 8+ working examples
```

✅ **Complete when:** Anyone can deploy following these docs

---

## Phase 7: Final Commit & Ship (Week 8+)

```bash
# 1. Final review
git status

# 2. Commit everything
git add .
git commit -m "feat: Add [feature] implementation and deployment guide"

# 3. Push
git push origin main

# 4. Follow deployment guide
# - Stage 1: Baseline testing
# - Stage 2: Feature flags at 0%
# - Stage 3: Gradual rollout (5% → 25% → 50% → 100%)
# - Stage 4: Monitor and validate
# - Stage 5: Cleanup

# 5. Move to completed
mv upgrades/[feature] upgrades/completed/[feature]
```

✅ **Complete when:** Feature deployed and stable

---

## Critical Success Factors

### DO ✅

1. **Enter plan mode BEFORE each phase** - Catch issues early
2. **Generate tests proactively** - Quality built-in
3. **Compact between phases** - Prevent context overflow
4. **Create working examples** - Copy-paste ready
5. **Document as you go** - Never falls behind
6. **Use Tier 1-2 sources** - Official docs, 1.5k+ star repos

### DON'T ❌

1. **Skip plan mode discussion** - Leads to rework
2. **Wait for user to ask for tests** - Generate proactively!
3. **Skip context compaction** - Context will overflow
4. **Leave TODOs in examples** - Make them complete
5. **Defer documentation** - Do it during implementation
6. **Use outdated sources** - Verify versions with GitHub API

---

## Timeline (Major Feature)

```
Week 1:   Phase 1 (RDF)                    → 8 research docs
Week 2-3: Phase 1 (Foundation)             → Code + 15 tests → COMPACT
Week 3-4: Phase 2 (Intelligent Features)   → Code + 15 tests → COMPACT
Week 5-6: Phase 3 (Advanced Features)      → Code + 15 tests → COMPACT
Week 7:   Phase 4 (Polish)                 → Code + 15 tests → COMPACT
Week 8:   Phase 6 (Deployment Manual)      → 4 guides + 8 examples
Week 8+:  Phase 7 (Ship)                   → Deploy + monitor

Total: 8 weeks for major feature
Context compacts: 4 (critical!)
```

---

## Phase Implementation Checklist

Copy this for each phase:

```
☐ 1. Enter plan mode
☐ 2. Discuss phase requirements
☐ 3. Identify research/context gaps
☐ 4. Exit plan mode
☐ 5. Write implementation code (3-5 files)
☐ 6. Generate tests proactively (15-30 tests)
☐ 7. Create examples (copy-paste ready)
☐ 8. Update documentation (README, CHANGELOG)
☐ 9. Context compact
☐ 10. Mark phase complete ✅
```

---

## Quality Metrics

### Research Phase
- ✅ 8+ research documents
- ✅ All sources Tier 1-2
- ✅ Latest versions verified

### Implementation Phase
- ✅ 20+ implementation files
- ✅ 30+ tests (without being asked!)
- ✅ 80%+ code coverage

### Example Quality
- ✅ 8+ deployment examples
- ✅ Copy-paste ready
- ✅ No placeholders

### Documentation
- ✅ 100% coverage
- ✅ Deployment guide complete
- ✅ Testing guide complete
- ✅ Troubleshooting guide complete

---

## Real Example: Query Router

**Timeline:** 8 weeks
**Context Compacts:** 4
**Implementation Files:** 20
**Tests:** 30+ (generated proactively!)
**Research Docs:** 8
**Deployment Examples:** 8
**Guides:** 4
**Rework Required:** 0
**Result:** Production-ready, deployment successful

---

## Templates Available

```
workflow/templates/features/
├── IMPROVEMENT-PLAN-TEMPLATE.md
├── IMPLEMENTATION-GUIDE-TEMPLATE.md
├── DEPLOYMENT-GUIDE-TEMPLATE.md
├── README-TEMPLATE.md
└── PHASE-README-TEMPLATE.md
```

---

## Related Resources

- [Full Workflow Guide](./FEATURES-IMPLEMENTATION-WORKFLOW.md) - Complete documentation
- [Phase Checklist](./PHASE-IMPLEMENTATION-CHECKLIST.md) - Detailed checklist
- [RDF Workflow](../.claude/RDF-WORKFLOW-GUIDE.md) - Automated research
- [Workflow README](./README.md) - All workflows

---

## Quick Decision Tree

```
Starting a feature?
├─ Major feature (multi-week)? → Use this workflow
├─ Bug fix? → Don't use (too heavyweight)
├─ Simple change? → Don't use (regular flow)
└─ Research needed? → Start with Phase 1 (RDF)

During implementation?
├─ Starting new phase? → Enter plan mode first!
├─ Just finished coding? → Generate tests proactively
├─ Phase complete? → Context compact!
└─ All phases done? → Create deployment manual

Ready to ship?
├─ All tests passing? → Create deployment guides
├─ Guides complete? → Final commit
├─ Deployed? → Move to completed/
└─ Done! 🎉
```

---

**Remember:** This workflow delivered a production-ready query router upgrade with zero rework. Follow it step-by-step for your next feature!
