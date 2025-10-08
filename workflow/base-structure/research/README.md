# Research

**Research-first development foundation**

This directory contains all research documentation following research-first principles. All architectural decisions must be grounded in high-quality, verified sources.

---

## Directory Structure

```
research/
├── documentation/           # Official docs, guides, best practices (Tier 1)
│   ├── [framework-name]/   # Per-framework documentation
│   │   ├── README.md       # Framework overview
│   │   └── *.md            # Specific topics
│   └── [topic]/            # Cross-framework topics
│       ├── README.md       # Topic overview
│       └── *.md            # Specific documentation
├── examples/               # Verified code samples (Tier 2, 1.5k+ stars)
│   └── [pattern-name]/    # Implementation patterns
│       ├── README.md       # Example overview
│       └── *.md            # Code examples
├── architecture-decisions/ # ADRs with research citations
│   ├── README.md          # ADR index
│   └── ADR-NNN-*.md       # Individual ADRs
└── references.md          # Index of all sources with quality ratings
```

---

## Source Hierarchy

**Always prioritize in this order:**

### Tier 1: Official Documentation
- Framework official documentation
- API reference docs
- Technology vendor documentation
- Must be current (<2 years old OR explicitly verified)

### Tier 2: Verified Code Examples
- GitHub repositories with 1.5k+ stars
- Verified implementation patterns
- Must demonstrate the pattern being researched

### Tier 3: Technical Standards
- RFCs (Request for Comments)
- W3C specifications
- IEEE standards
- Academic papers from reputable institutions

### Tier 4: Verified Technical Sources
- Known technical blogs (Martin Fowler, etc.)
- Conference talks from major conferences
- Technical articles from verified authors

### Tier 5: Package Registries
- Official npm, PyPI, Maven registries
- Must have verified publishers

---

## Research Quality Standards

### Documentation Requirements

**All research documents must include:**

1. **Source Citations**
   ```markdown
   **Source:** [Document Name](URL)
   **Accessed:** 2025-10-08
   **Tier:** 1 (Official Documentation)
   **Verified:** ✅ Current as of Oct 2025
   ```

2. **Version Numbers**
   ```markdown
   **Technology:** semantic-router
   **Version:** 0.1.11
   **Released:** October 2025
   **Verified via:** GitHub API
   ```

3. **Breaking Changes**
   ```markdown
   **Breaking Changes:**
   - v0.2.0: API restructure (not yet released)
   - v0.1.0 → 0.1.11: Backward compatible
   ```

4. **Comparison Tables**
   ```markdown
   | Feature | Option A | Option B | Recommended |
   |---------|----------|----------|-------------|
   | [Feature] | [Details] | [Details] | Option A (Why) |
   ```

### Validation Requirements

**Before adding research:**
- ✅ Source is Tier 1-3 (Tier 4-5 only as supplements)
- ✅ Documentation is current or explicitly verified as valid
- ✅ Breaking changes are documented
- ✅ Versions are verified via GitHub API or package registry
- ✅ Code examples are tested or from verified repos

---

## Research Workflow

### Phase 1: Research Collection

```bash
# Use Exa AI for web research
/research [topic] [framework]

# Use GitHub API for version verification
# Check package registries for latest versions
```

**Deliverables:**
- 3+ sources per research question
- All Tier 1-2 sources
- Version numbers verified

### Phase 2: Documentation

**Create research documents:**

```markdown
# [Topic] - [Framework Name]

**Status:** Complete
**Last Updated:** [Date]
**Version Researched:** [Version]

## Overview
[2-3 paragraph overview]

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Sources
1. [[Source 1](URL)] - Tier 1 - Official docs
2. [[Source 2](URL)] - Tier 2 - 2.8k stars
```

### Phase 3: Architecture Decisions

**Document decisions in ADRs:**

```markdown
# ADR-001: [Decision Title]

**Status:** Accepted
**Date:** [Date]

## Context
[What problem are we solving?]

## Decision
[What did we decide?]

## Research Support
**Tier 1 Sources:**
- [Source 1]

**Benchmarks:**
- [Performance data]

## Consequences
**Positive:**
- [Benefit 1]

**Negative:**
- [Tradeoff 1]
```

---

## Organization Patterns

### Per-Framework Documentation

```
research/documentation/neo4j/
├── README.md                    # Neo4j overview
├── vector-index-guide.md        # Vector search feature
├── cypher-best-practices.md     # Query optimization
└── graph-algorithms.md          # Algorithm library
```

### Cross-Framework Topics

```
research/documentation/query-routing/
├── README.md                    # Query routing overview
├── semantic-router.md           # Semantic classification
├── query-rewriting-rag.md       # Query rewriting patterns
└── adaptive-routing-learning.md # Adaptive weight learning
```

### Verified Examples

```
research/examples/multi-database-rag/
├── README.md                    # Example overview
├── lettria-case-study.md        # Production example (1.5k+ stars)
└── implementation-notes.md      # Key insights
```

---

## Best Practices

### DO ✅

1. **Always cite sources** - Every claim needs a source
2. **Verify versions** - Check GitHub API or package registry
3. **Document breaking changes** - Critical for upgrades
4. **Create comparison tables** - Help decision-making
5. **Use Tier 1-2 sources** - Official docs and verified code
6. **Update research regularly** - Technology evolves

### DON'T ❌

1. **Use blog posts as primary sources** - Supplement only
2. **Trust version numbers without verification** - Always verify
3. **Skip breaking changes** - Critical information
4. **Make assumptions** - Research, don't guess
5. **Use outdated documentation** - Verify currency
6. **Skip citations** - Always include sources

---

## Integration with Implementation

**Research documents support:**

1. **Improvement Plans**
   - Research links in IMPROVEMENT-PLAN.md
   - Decisions backed by research
   - Alternatives documented

2. **Implementation Guides**
   - Reference research docs for approach
   - Use verified code examples
   - Follow researched best practices

3. **Architecture Decision Records**
   - Cite research in ADRs
   - Document alternatives considered
   - Show data-driven decisions

---

## Research Templates

### Framework Documentation Template

```markdown
# [Framework Name] - Documentation

**Version Researched:** [version]
**Last Updated:** [Date]
**Official Docs:** [URL]

## Overview
[Framework description]

## Key Features
- Feature 1
- Feature 2

## Best Practices
1. Practice 1
2. Practice 2

## Common Patterns
### Pattern 1
[Description and example]

## Sources
1. [[Official Docs](URL)] - Tier 1
2. [[GitHub Repo](URL)] - Tier 2 - [stars]
```

### Comparison Analysis Template

```markdown
# [Topic] - Comparison Analysis

**Last Updated:** [Date]
**Decision:** [Recommended option]

## Options Compared
1. Option A
2. Option B
3. Option C

## Comparison Matrix

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Performance | [Details] | [Details] | [Details] |
| Cost | [Details] | [Details] | [Details] |
| Maturity | [Details] | [Details] | [Details] |

## Recommendation
[Recommended option with rationale]

## Sources
[All sources cited]
```

---

## Quality Metrics

**Research quality checklist:**

```
☑ All sources Tier 1-3 (Tier 4-5 only supplements)
☑ Minimum 3 sources per decision
☑ All versions verified via GitHub API
☑ Breaking changes documented
☑ Comparison tables included
☑ All sources cited with URLs
☑ Documentation currency verified
☑ Code examples tested or from verified repos (1.5k+ stars)
```

---

## Getting Started

### For a New Topic

1. **Identify research questions:**
   - What are the latest versions?
   - What are the alternatives?
   - What are the best practices?
   - What are the breaking changes?

2. **Collect sources:**
   - Use Exa AI for official docs
   - Use GitHub API for version verification
   - Search for verified code examples (1.5k+ stars)

3. **Document findings:**
   - Create markdown files in appropriate subdirectory
   - Include all citations
   - Document versions and breaking changes

4. **Create ADR if needed:**
   - Document architectural decisions
   - Cite research support
   - List alternatives considered

---

## Maintenance

**Research should be updated:**
- Before starting implementation of related features
- When new versions are released
- When breaking changes are announced
- When new alternatives emerge
- Quarterly review of all documentation

---

**Research-first development ensures better decisions, fewer rewrites, and production-ready code.**
