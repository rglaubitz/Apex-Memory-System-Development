# Agent Index

Complete reference for all 20 specialized agents in the Apex Memory System development workspace.

## Agent Organization

| Category | Count | Purpose |
|----------|-------|---------|
| **C-Suite Executives** | 3 | Quality gates, Review Board validation |
| **Research Leadership** | 3 | Research coordination and documentation |
| **Specialized Hunters** | 3 | Finding official docs and code examples |
| **Analysts** | 5 | Deep research and competitive intelligence |
| **Quality & Validation** | 3 | Source validation and code quality |
| **Specialized Engineers** | 3 | Pattern analysis and testing |
| **TOTAL** | **20** | Multi-agent development orchestration |

## C-Suite Executives (Review Board)

These agents validate execution plans during **Phase 3.5 (Review Board)** before implementation begins.

| Agent | Role | Key Responsibilities | Tools |
|-------|------|---------------------|-------|
| **CIO** | Chief Information Officer | Research quality validation, source hierarchy enforcement, documentation completeness | Read, Grep, Glob, WebSearch, WebFetch, Write |
| **CTO** | Chief Technology Officer | Technical architecture review, technology stack validation, code quality standards | Read, Grep, Glob, WebSearch, WebFetch, Write |
| **COO** | Chief Operations Officer | Operational capacity review, execution feasibility, UX quality validation | Read, Grep, Glob, Write, TodoWrite |

**Review Process:**
- All 3 must approve before Phase 4 (Implementation)
- Each provides scored rubric (0-100) and verdict
- Verdicts: APPROVED, APPROVED_WITH_CONCERNS, REJECTED
- REJECTED = veto power, blocks implementation

---

## Research Team (17 Agents)

### Core Research Leadership (3)

| Agent | Role | Key Responsibilities | Tools | When to Use |
|-------|------|---------------------|-------|-------------|
| **research-manager** | Research Coordinator | Coordinates all research efforts, monitors documentation updates, manages knowledge base | WebSearch, WebFetch, Bash, Read, Write, Grep | Starting major research initiatives, checking documentation status |
| **research-coordinator** | Tactical Orchestration | Orchestrates multi-agent research tasks, delegates to specialized agents | Task, Read, Write, Grep, Bash | Complex research requiring multiple specialized agents |
| **documentation-expert** | Documentation Quality | Maintains documentation structure, creates guides, ensures cohesion and flow | Read, Write, Edit, MultiEdit, WebFetch, Grep | Documentation architecture, improving existing docs |

### Specialized Hunters (3)

| Agent | Role | Key Responsibilities | Tools | When to Use |
|-------|------|---------------------|-------|-------------|
| **documentation-hunter** | Official Docs Finder | Finds official documentation from authoritative sources (Tier 1) | WebSearch, WebFetch, Read, Write | Need official API docs, framework guides, specifications |
| **github-examples-hunter** | Code Examples Finder | Finds high-quality code examples from verified repositories (1.5k+ stars) | WebSearch, Read, Write | Need proven implementation patterns, reference code |
| **api-documentation-specialist** | API Specs Expert | Retrieves API specifications, OpenAPI schemas, GraphQL documentation | WebFetch, Read, Write | API integration, endpoint documentation, schema design |

### Analysts (5)

| Agent | Role | Key Responsibilities | Tools | When to Use |
|-------|------|---------------------|-------|-------------|
| **deep-researcher** | Complex Research | Multi-source research synthesis, complex problem analysis, technical deep-dives | WebSearch, WebFetch, Write | Complex technical questions, architectural research |
| **standards-researcher** | Standards Expert | Industry standards, best practices, compliance research from authoritative sources | WebSearch, WebFetch, Read, Write | Need technical standards, RFCs, W3C specs, compliance |
| **company-researcher** | Company Analysis | Company-specific research, vendor analysis, product comparisons | WebSearch, WebFetch, Read, Write | Researching specific companies, vendors, products |
| **competitive-intelligence-analyst** | Competitor Analysis | Alternative solutions, competitor feature comparison, market intelligence | WebSearch, Read, Write | Competitive analysis, feature comparisons, market research |
| **technical-trend-analyst** | Trends Expert | Technology trends, emerging technologies, deprecation tracking | WebSearch, WebFetch, Read, Write | Understanding industry direction, future planning |

### Quality & Validation (3)

| Agent | Role | Key Responsibilities | Tools | When to Use |
|-------|------|---------------------|-------|-------------|
| **citation-manager** | Source Tracking | Maintains references.md, tracks all sources, ensures citation quality | Read, Write, Edit, WebFetch | Managing research citations, verifying source URLs |
| **technical-validator** | Claims Verification | Verifies technical claims, tests hypotheses, validates accuracy | Bash, Read | Need to verify technical claims, test assumptions |
| **code-quality-validator** | Code Review | Validates code examples meet quality standards, checks for best practices | Bash, Read | Reviewing code examples, validating implementations |

### Specialized Engineers (3)

| Agent | Role | Key Responsibilities | Tools | When to Use |
|-------|------|---------------------|-------|-------------|
| **memory-system-engineer** | Knowledge Systems | Designs knowledge persistence layers, agent memory systems, knowledge graphs | Bash, Read, Write, Edit, Grep, MultiEdit | Building memory systems, knowledge graph design |
| **pattern-implementation-analyst** | Pattern Analysis | Analyzes and documents patterns from code examples, creates implementation guides | Read, Write | Documenting implementation patterns, creating guides |
| **agent-testing-engineer** | Agent Validation | Validates agent behavior, comprehensive testing strategies, quality assurance | Bash, Read, Write, Task, Grep, TodoWrite | Testing agents, validation strategies, QA |

---

## Usage Patterns

### Single Agent Tasks

For focused tasks, invoke specific agents directly:

```
Use the documentation-hunter to find official Neo4j documentation
Use the github-examples-hunter to find vector search implementations (1.5k+ stars)
Use the technical-validator to verify GraphRAG performance claims
```

### Multi-Agent Coordination

For complex research, use coordinators:

```
Use the research-coordinator to orchestrate research on query routing systems:
- documentation-hunter: Find official docs
- github-examples-hunter: Find code examples
- standards-researcher: Find best practices
- citation-manager: Track all sources
```

### Review Board

Automatic during Phase 3.5:

```
Phase 3.5 Review Board:
1. CIO reviews research quality
2. CTO reviews technical architecture
3. COO reviews operational feasibility
→ All must approve before Phase 4
```

## Agent Selection Guide

### When researching official documentation:
→ **documentation-hunter** or **api-documentation-specialist**

### When researching code examples:
→ **github-examples-hunter** (ensures 1.5k+ stars)

### When researching industry standards:
→ **standards-researcher**

### When researching competitors:
→ **competitive-intelligence-analyst** or **company-researcher**

### When validating claims:
→ **technical-validator** or **code-quality-validator**

### When coordinating complex research:
→ **research-coordinator** or **research-manager**

### When validating execution plans:
→ **C-Suite Review Board** (CIO, CTO, COO)

## Quality Standards

All agents follow the **Research-First Principle:**

### Source Hierarchy (Priority)

1. **Tier 1:** Official Documentation
2. **Tier 2:** Verified GitHub (1.5k+ stars)
3. **Tier 3:** Technical Standards (RFCs, specs)
4. **Tier 4:** Verified Technical Sources
5. **Tier 5:** Package Registries

### Validation Requirements

- ✅ Documentation must be current (<2 years OR explicitly verified)
- ✅ GitHub examples must demonstrate the pattern researched
- ✅ All sources must include citations with URLs
- ✅ Breaking changes and deprecations must be noted

## Files

All agent definitions are located in this directory:

```
.claude/agents/
├── CIO.md
├── COO.md
├── CTO.md
├── agent-testing-engineer.md
├── api-documentation-specialist.md
├── citation-manager.md
├── code-quality-validator.md
├── company-researcher.md
├── competitive-intelligence-analyst.md
├── deep-researcher.md
├── documentation-expert.md
├── documentation-hunter.md
├── github-examples-hunter.md
├── memory-system-engineer.md
├── pattern-implementation-analyst.md
├── research-coordinator.md
├── research-manager.md
├── standards-researcher.md
├── technical-trend-analyst.md
└── technical-validator.md
```

---

**Total Agents:** 20
**Review Board:** 3 C-Suite Executives
**Research Team:** 17 Specialized Agents
**Quality Gate:** Phase 3.5 requires approval from CIO + CTO + COO
