# Architecture Decision Records (ADRs) - Index

This directory contains Architecture Decision Records for the Apex Memory System project. ADRs document significant architectural decisions with research-backed rationale and consequences.

## ADR Index

### ADR-004: Bi-Temporal Versioning with Graphiti
**Status**: Proposed
**Created**: 2025-10-06
**Author**: deep-researcher

**Summary**: Adopts Graphiti's bi-temporal versioning model to track knowledge evolution over time using two independent time dimensions: transaction time (when we learned something) and valid time (when it was actually true).

**Key Decision**: Implement bi-temporal data model across all knowledge graph edges and PostgreSQL metadata tables to support time-travel queries, retroactive corrections, and audit compliance.

**Files**:
- [ADR-004-bi-temporal-versioning-graphiti.md](./ADR-004-bi-temporal-versioning-graphiti.md) - Full decision record
- [ADR-004-RESEARCH-CITATIONS.md](./ADR-004-RESEARCH-CITATIONS.md) - Source quality assessment

**Research Quality**: ⭐⭐⭐⭐⭐ Excellent (17 sources, 10+ cross-validated)

---

## ADR Template

When creating new ADRs, use this structure:

```markdown
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Rejected | Deprecated | Superseded by ADR-YYY]

## Context
What problem are we solving? Why is this decision necessary?

## Options Considered

### Option A: [Name]
**Description**: ...
**Pros**: ...
**Cons**: ...
**Verdict**: ✅/❌

### Option B: [Name]
...

## Decision
What did we choose and why?

## Research Support

### Tier 1: Official Documentation
- Source 1 (with URL)
- Source 2

### Tier 2: Verified Examples (1.5k+ stars)
- Example 1 (with GitHub stars)

### Tier 3: Technical Standards
- Standard 1

## Implementation Details
Code examples, schema changes, migration plans

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Negative
- Drawback 1 (with mitigation strategy)

## References
All sources with URLs
```

---

## Research-First Principles

All ADRs must comply with Apex Memory System research-first standards:

### Source Quality Requirements

1. **Tier 1 Sources** (highest priority):
   - Official documentation (Anthropic, Neo4j, PostgreSQL, Graphiti, etc.)
   - Must be current (<2 years old OR explicitly verified)

2. **Tier 2 Sources**:
   - Verified GitHub repositories (1.5k+ stars minimum)
   - Must demonstrate the pattern being researched

3. **Tier 3 Sources**:
   - Technical standards (RFCs, W3C, academic papers)
   - Reputable institutions only

### Validation Standards

- **Minimum Sources**: 10+ sources per ADR
- **Cross-Validation**: All major claims referenced in 3+ sources
- **Citations**: Include URLs, star counts, publication dates
- **Breaking Changes**: Document deprecations and compatibility issues

### Review Process

1. **Author**: Deep researcher or specialized research agent
2. **Quality Gate**: CIO validates research quality (Phase 3.5)
3. **Technical Review**: CTO validates architecture feasibility
4. **Operational Review**: COO validates execution capacity
5. **Approval**: All 3 C-suite executives must approve

---

## Quick Links

- [Project CLAUDE.md](../../CLAUDE.md) - Project overview
- [Research Documentation](../documentation/) - Official docs collection
- [Research Examples](../examples/) - Code examples and patterns
- [Main Codebase](../../apex-memory-system/) - Implementation symlink

---

## Document Metadata
- **Created**: 2025-10-06
- **Last Updated**: 2025-10-06
- **Maintainer**: research-manager
- **Total ADRs**: 1 (ADR-004)
