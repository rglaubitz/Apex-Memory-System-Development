# Architecture Decision Records (ADRs)

Document architectural decisions with research citations.

## Purpose

ADRs provide a record of significant architectural choices made during the project, including the context, options considered, and rationale for the decision.

## Organization

Each ADR should reference sources from `documentation/` or `examples/`

## ADR Template

```markdown
# ADR-NNN: [Decision Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** YYYY-MM-DD
**Deciders:** [Who made this decision]
**Phase:** [Vision | Mission | Execution | Implementation]

## Context

[What is the issue we're trying to solve?]

## Decision

[What is the change we're proposing?]

## Options Considered

### Option 1: [Name]
**Pros:**
- [Benefit 1]

**Cons:**
- [Limitation 1]

**Research:**
- [Source from documentation/ or examples/]

### Option 2: [Name]
[Same format]

## Chosen Option

**Selected:** Option X

**Rationale:**
- [Why we chose this]

**Research Support:**
- Official docs: [Link to documentation/]
- Implementation example: [Link to examples/]
- Technical standard: [Link or reference]

## Consequences

**Positive:**
- [What we gain]

**Negative:**
- [What we sacrifice]

**Mitigation:**
- [How we address negatives]

## Implementation Notes

[How will this decision be implemented?]

## References

- [Source 1 from research/]
- [Source 2 from research/]

---

*This ADR follows the research-first principle with citations to Tier 1-3 sources*
```

## Example ADRs

- ADR-001: Multi-Database Architecture (Neo4j + PostgreSQL + Qdrant + Redis)
- ADR-002: Saga Pattern for Database Write Consistency
- ADR-003: Intent-Based Query Routing Strategy
- ADR-004: Bi-Temporal Entity Versioning with Graphiti

---

*All architectural decisions must cite research sources*
*Reviewed by CTO during Review Board (Phase 3.5)*
