# Code Examples & References

Store code samples from high-quality sources (GitHub 1.5k+ stars).

**Source hierarchy priority: HIGH (Tier 2)**

## What Goes Here

- Working code examples from verified repositories (1.5k+ stars minimum)
- Reference implementations demonstrating key patterns
- Best practice examples from authoritative sources
- Proven architectural patterns

## Organization

```
examples/
├── multi-database-rag/        # Parallel database patterns (Microsoft GraphRAG, etc.)
├── vector-search/             # HNSW implementations, indexing strategies
├── temporal-intelligence/     # Bi-temporal tracking, pattern detection
├── document-processing/       # PDF/DOCX/PPTX parsing (Docling integration)
├── fastapi-async/             # Async patterns, background tasks
└── implementation-patterns/   # Best practices, design patterns
```

## Quality Standards

- **Minimum 1.5k GitHub stars** for repository source
- Code must be actively maintained (commits in last 12 months)
- Include link to source repository
- Note star count and last commit date
- Verify license compatibility (MIT, Apache 2.0, etc.)

## Example Entry Format

When saving an example, include metadata:

```markdown
# [Pattern Name]

**Source:** https://github.com/org/repo
**Stars:** ⭐ 3.2k
**Last Updated:** 2025-09-15
**License:** MIT
**Demonstrates:** [What pattern this shows]

## Code Sample

[The actual code]

## Key Takeaways

- [What we learned]
- [How it applies to our project]
```

## Active Applications

### Query Router Upgrade (October 2025)

Examples from this directory are being applied to the **Query Router Improvement Plan**:

| Example Category | Application | Impact |
|------------------|-------------|--------|
| **multi-database-rag/** | Microsoft GraphRAG pattern | 99% precision hybrid search |
| **vector-search/** | HNSW optimization | Faster semantic search |
| **implementation-patterns/** | Best practices | Code quality improvements |

**See:** `../../upgrades/query-router/` for how these examples are being used

**Research:** See `../documentation/query-routing/` for theoretical foundation

## Cross-References

- **Documentation:** `../documentation/` for official framework docs (Tier 1)
- **ADRs:** `../architecture-decisions/` for architectural decisions citing examples
- **Upgrades:** `../../upgrades/` for active improvement plans using these patterns
- **Review Process:** `../review-board/` for Phase 3.5 validation

---

*Tier 2 sources - High priority for implementation patterns*
