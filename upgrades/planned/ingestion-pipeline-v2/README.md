# Ingestion Pipeline v2

**Priority:** Medium
**Status:** 📝 Research Phase
**Timeline:** TBD
**Research Progress:** 0%

---

## Problem Statement

The current ingestion pipeline has several limitations that impact document processing quality and efficiency:

### Current Issues

1. **Document Parsing Quality:**
   - PDF extraction loses formatting context
   - DOCX tables extracted as plain text
   - PPTX slide structure not preserved
   - Inconsistent handling of embedded images

2. **Limited Multi-Modal Support:**
   - Text-only focus (images ignored)
   - Tables lose semantic structure
   - Diagrams and charts not processed
   - No audio/video transcription

3. **Parallel Processing Inefficiencies:**
   - Target: 10+ docs/second not consistently met
   - Saga pattern could be optimized
   - Batch processing underutilized
   - Embedding generation bottleneck

4. **Entity Extraction Quality:**
   - LLM-based extraction inconsistent with smaller models
   - Short numeric entities cause noise
   - Entity deduplication needs improvement
   - Domain-specific entity types missing

---

## Goals

### Primary Goals

- ✅ **Improve document parsing quality** - 95%+ format preservation
- ✅ **Add multi-modal support** - Process images, tables, diagrams
- ✅ **Optimize parallel processing** - Consistently achieve 10+ docs/sec
- ✅ **Enhance entity extraction** - 90%+ accuracy with quality scoring

### Secondary Goals

- Semantic chunking strategies (vs fixed-size chunks)
- Incremental re-processing (update changed docs only)
- Document versioning and change detection
- Quality metrics and monitoring

---

## Research Needed

### Document Parsing Libraries

**To Research:**
- Docling (IBM Research) - Document layout analysis
- Unstructured.io - Multi-format parsing
- PyMuPDF4LLM - PDF extraction optimized for LLMs
- python-docx improvements
- python-pptx enhancements

**Questions:**
- Which library has best PDF table extraction?
- How do they handle embedded images?
- What's the performance/quality trade-off?

### Multi-Modal Embedding Models

**To Research:**
- CLIP (OpenAI) - Image-text embeddings
- ImageBind (Meta) - Multi-modal unified space
- GPT-5 vision capabilities (Oct 2025)
- Table structure preservation techniques

**Questions:**
- Can we use same vector DB for multi-modal embeddings?
- How to handle dimension mismatches?
- What's the storage overhead?

### Parallel Processing Patterns

**To Research:**
- Async Python best practices
- Saga pattern optimizations
- Batch embedding generation
- Database bulk write operations

**Questions:**
- Where are current bottlenecks?
- Can we parallelize entity extraction?
- How to optimize embedding API calls?

### Entity Extraction Techniques

**To Research:**
- NER (Named Entity Recognition) libraries
- LLM-based entity extraction prompts
- Entity quality scoring methods
- Domain-specific entity ontologies

**Questions:**
- Hybrid NER + LLM approach?
- How to filter low-quality entities?
- Entity deduplication strategies?

---

## Next Steps

### Phase 1: Research (TBD)

1. **Document Parsing:**
   - Evaluate Docling, Unstructured.io, PyMuPDF4LLM
   - Benchmark parsing quality on test corpus
   - Document findings in `research/documentation/`

2. **Multi-Modal:**
   - Research multi-modal embedding models
   - Prototype image + text ingestion
   - Evaluate storage implications

3. **Performance:**
   - Profile current ingestion pipeline
   - Identify bottlenecks
   - Benchmark competitor systems

4. **Entity Extraction:**
   - Test NER libraries (spaCy, Stanza)
   - Evaluate LLM extraction quality
   - Design quality scoring system

### Phase 2: Planning (TBD)

1. Create comprehensive IMPROVEMENT-PLAN.md
2. Define phased implementation (4-6 weeks estimated)
3. Establish success metrics and benchmarks
4. Submit to Review Board for approval

### Phase 3: Graduation to Active (TBD)

1. Receive Review Board approval
2. Move to `upgrades/ingestion-pipeline-v2/`
3. Begin implementation Phase 1

---

## Expected Outcomes (Preliminary)

**Document Parsing:**
- 95%+ format preservation across PDF, DOCX, PPTX
- Table structure maintained (not flattened to text)
- Embedded images extracted and processed

**Multi-Modal Support:**
- Images ingested and searchable
- Tables queryable with structure awareness
- Cross-modal retrieval (text query → image results)

**Performance:**
- Consistent 10+ documents/second throughput
- <5 second P90 latency per document
- Optimized embedding generation (batching)

**Entity Quality:**
- 90%+ entity extraction accuracy
- Quality scores filter low-value entities
- Domain-specific entity types supported

---

## Related Research

**Existing Documentation:**
- `../../../research/examples/document-processing/` - Current patterns
- `../../../research/documentation/docling/` - (To be created)

**Related Upgrades:**
- Query Router Improvement Plan - May benefit from better entities
- Multi-Modal RAG (Planned) - Shares multi-modal requirements

**ADRs:**
- ADR-002: Saga Pattern - May need refinement for v2

---

## Priority Rationale

**Why Medium Priority:**
- Current pipeline functional (not broken)
- Query Router upgrade takes precedence
- Quality improvements vs critical fixes
- Enables future multi-modal work

**Could Elevate to High If:**
- Document parsing quality becomes blocker
- User demand for multi-modal support increases
- Performance degrades below targets
- Entity quality impacts retrieval accuracy

---

**Status:** 📝 Awaiting research phase kickoff
**Owner:** TBD
**Next Review:** TBD
