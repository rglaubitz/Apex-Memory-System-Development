# Phased Development Workflow

5-phase development process with quality gates for the Apex Memory System.

## Overview

The workflow system ensures high-quality, research-driven development through structured phases with validation at each stage.

```
Phase 1: Vision → Phase 2: Mission → Phase 3: Execution Planning
                                              ↓
                                    Phase 3.5: Review Board ⭐
                                              ↓
                     Phase 4: Implementation → Phase 5: Testing
```

## Phases

### Phase 1: Vision

**Purpose:** Define strategic goals and success criteria

**Activities:**
- Identify business objectives
- Define user needs and pain points
- Establish success metrics
- Create vision document

**Deliverables:**
- Vision statement
- Success criteria
- Key performance indicators (KPIs)

**Quality Gate:** User approval of vision

**Duration:** 1-2 days

---

### Phase 2: Mission

**Purpose:** Research and define technical approach

**Activities:**
- Use research team to gather documentation
- Review best practices and industry standards
- Evaluate technology options
- Create technical approach document

**Research Team Agents:**
- research-manager (coordination)
- documentation-hunter (official docs)
- github-examples-hunter (code examples)
- standards-researcher (best practices)
- competitive-intelligence-analyst (alternatives)

**Deliverables:**
- Research documentation in `research/documentation/`
- Code examples in `research/examples/`
- Technology selection with rationale
- Mission document

**Quality Gate:** Research quality validated by CIO

**Duration:** 3-5 days

---

### Phase 3: Execution Planning

**Purpose:** Create detailed implementation plan

**Activities:**
- Break down work into phases and tasks
- Identify dependencies and risks
- Define implementation approach
- Create comprehensive plan with code examples

**Deliverables:**
- Detailed execution plan (e.g., IMPROVEMENT-PLAN.md)
- Task breakdown
- Risk mitigation strategies
- Timeline estimates

**Quality Gate:** Plan completeness check

**Duration:** 2-3 days

---

### Phase 3.5: Review Board ⭐

**Purpose:** C-suite validation before implementation

**The Review Board consists of 3 C-suite executive agents:**

#### Chief Information Officer (CIO)
**Reviews:** Research quality and documentation completeness

**Validation Criteria:**
- ✅ Research follows source hierarchy (Tier 1-5)
- ✅ Documentation is current (<2 years OR explicitly verified)
- ✅ GitHub examples are high-quality (1.5k+ stars)
- ✅ All sources include citations with URLs
- ✅ Breaking changes and deprecations noted
- ✅ Dependencies clearly documented

**Scoring Rubric (0-100):**
- Research Quality (40 pts)
- Documentation Completeness (30 pts)
- Source Hierarchy Compliance (20 pts)
- Citation Accuracy (10 pts)

#### Chief Technology Officer (CTO)
**Reviews:** Technical architecture and implementation feasibility

**Validation Criteria:**
- ✅ Technology stack is appropriate
- ✅ Architecture is sound and scalable
- ✅ API design follows best practices
- ✅ Data architecture is well-designed
- ✅ Code quality standards are defined
- ✅ Security considerations addressed

**Scoring Rubric (0-100):**
- Technical Architecture (40 pts)
- Implementation Feasibility (30 pts)
- Code Quality Standards (20 pts)
- Security & Performance (10 pts)

#### Chief Operations Officer (COO)
**Reviews:** Operational capacity and goal achievement

**Validation Criteria:**
- ✅ Goals are achievable
- ✅ Timeline is realistic
- ✅ Resources are adequate
- ✅ UX quality is addressed
- ✅ User adoption is likely
- ✅ Business impact is clear

**Scoring Rubric (0-100):**
- Goal Achievement (40 pts)
- Timeline Realism (30 pts)
- Resource Adequacy (20 pts)
- UX & Adoption (10 pts)

**Review Process:**
1. CIO reviews first (research foundation)
2. CTO reviews second (technical architecture)
3. COO reviews last (operational execution)
4. All 3 must approve to proceed

**Possible Verdicts:**
- ✅ **APPROVED** - Proceed to Phase 4
- ⚠️ **APPROVED_WITH_CONCERNS** - Proceed with noted concerns
- ❌ **REJECTED** - Major issues, must revise and resubmit

**Veto Power:** Any executive can REJECT and block implementation

**Duration:** 1-2 days

**Output:** Review Board reports in `research/review-board/`

---

### Phase 4: Implementation

**Purpose:** Execute the approved plan

**Activities:**
- Follow phased implementation approach
- Track progress with TodoWrite
- Create ADRs for significant decisions
- Regular progress updates

**Quality Standards:**
- Follow approved plan
- Maintain code quality (black, isort, flake8, mypy)
- Write tests for new functionality
- Document as you go

**Progress Tracking:**
- Use TodoWrite for task management
- Update upgrade README with status
- Regular check-ins

**Quality Gate:** COO validates execution progress

**Duration:** Varies by project (4-8 weeks typical)

---

### Phase 5: Testing

**Purpose:** Validate implementation against requirements

**Activities:**
- Run comprehensive test suite
- Benchmark performance against targets
- Validate success criteria from Phase 1
- Document actual results vs. expected

**Testing Types:**
- Unit tests (pytest)
- Integration tests
- Performance benchmarks
- User acceptance testing (if applicable)

**Deliverables:**
- Test results report
- Performance benchmarks
- Comparison: actual vs. expected gains
- Lessons learned

**Quality Gate:** CTO validates technical achievement

**Duration:** 1-2 weeks

---

## Quality Gates Summary

| Phase | Quality Gate | Validator | Criteria |
|-------|-------------|-----------|----------|
| 1: Vision | User approval | User | Vision aligns with needs |
| 2: Mission | Research quality | CIO | Follows source hierarchy |
| 3: Execution Planning | Plan completeness | - | All sections complete |
| **3.5: Review Board** | **C-suite approval** | **CIO + CTO + COO** | **All 3 approve** |
| 4: Implementation | Execution progress | COO | Following approved plan |
| 5: Testing | Technical achievement | CTO | Meets success criteria |

## Workflow Commands

**Note:** Workflow commands are managed through Claude Code slash commands.

Example commands (hypothetical):
```
/start-vision <project-name>
/start-mission <project-name>
/start-execution-planning <project-name>
/start-review-board <project-name>
/start-implementation <project-name>
/start-testing <project-name>
```

## Example: Query Router Upgrade

**Phase 1: Vision** (Complete)
- Goal: Improve query routing to 2025 standards
- Success: 85-95% accuracy, <500ms P90 latency

**Phase 2: Mission** (Complete)
- Research: 5 documents covering Semantic Router, Query Rewriting, Agentic RAG, Adaptive Routing, GraphRAG
- Sources: Microsoft, Neo4j, arXiv papers, industry benchmarks

**Phase 3: Execution Planning** (Complete)
- Plan: `upgrades/query-router/IMPROVEMENT-PLAN.md`
- Timeline: 8 weeks, 4 phases
- Expected gains: +21-28 points relevance, 99% precision

**Phase 3.5: Review Board** (Ready)
- CIO: Validates research quality (5 Tier 1-2 sources)
- CTO: Validates technical architecture
- COO: Validates 8-week timeline feasibility

**Phase 4: Implementation** (Not Started)
- Waiting for Review Board approval

**Phase 5: Testing** (Planned)
- Benchmarks against current system
- Validate 85-95% accuracy target

## Best Practices

### Do's ✅
- Follow phases in order (no skipping)
- Get Review Board approval before implementation
- Track all research with citations
- Create ADRs for significant decisions
- Update documentation as you go
- Use agents for specialized tasks

### Don'ts ❌
- Skip Review Board (Phase 3.5)
- Implement without approved plan
- Use research without citations
- Make architectural decisions without ADRs
- Ignore quality gate feedback
- Bypass C-suite executives

## References

- **C-Suite Agents:** `../.claude/agents/` (CIO, CTO, COO)
- **Research Team:** `../.claude/agents/README.md`
- **Upgrades:** `../upgrades/README.md`
- **ADR Template:** `../research/architecture-decisions/README.md`

---

**Process Owner:** Development Coordination
**Quality Enforcement:** C-Suite Review Board
**Last Updated:** October 2025
