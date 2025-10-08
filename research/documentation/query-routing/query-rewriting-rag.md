# Query Rewriting for RAG Optimization (2024-2025)

**Sources:** Multiple research papers and industry implementations
**Date:** 2024-2025
**Tier:** 1 (Official Documentation + Academic Research)

## Overview

Query rewriting addresses issues with users' original queries (inaccurate wording, lack of semantic information) and can improve RAG retrieval relevance by 12-28 points (Microsoft 2024).

## Problem Statement

User queries often:
- Use imprecise language
- Lack domain terminology
- Have grammatical errors
- Are too vague or too specific
- Miss semantic context

Result: Poor retrieval, irrelevant results, missed documents

## Key Techniques

### 1. Query Normalization

**Purpose:** Fix basic query issues
**Methods:**
- Grammar correction
- Spelling fixes
- Lowercasing
- Stop word removal
- Standardization

**Example:**
```
Input:  "wht r the overdu invoices frm last mnth?"
Output: "what are the overdue invoices from last month"
```

### 2. HyDE (Hypothetical Document Embeddings)

**Source:** [Precise Zero-Shot Dense Retrieval](https://arxiv.org/abs/2212.10496)

**Concept:** Generate hypothetical answer, use it for retrieval

**Process:**
1. User asks: "How does temporal tracking work?"
2. LLM generates hypothetical answer
3. Embed the answer (not the question)
4. Search for real documents matching the answer
5. Real documents are more similar to answers than questions

**Performance:** 15-20% improvement in retrieval relevance

**Implementation:**
```python
# Generate hypothetical answer
hyde_prompt = f"Write a passage that answers: {query}"
hypothetical_doc = llm.generate(hyde_prompt)

# Embed and search
embedding = embed(hypothetical_doc)
results = vector_db.search(embedding)
```

### 3. Query Decomposition

**Purpose:** Break complex queries into focused sub-queries

**Example:**
```
Complex: "Compare customer payment behavior in Q1 vs Q2 for ACME Corp"

Decomposed:
1. "ACME Corp payment behavior Q1 2024"
2. "ACME Corp payment behavior Q2 2024"
3. "Compare Q1 Q2 payment trends"
```

**Benefits:**
- Each sub-query retrieves precise documents
- Reduces noise in results
- Better for multi-hop reasoning

### 4. Query Expansion

**Purpose:** Add synonyms, related terms, context

**Example:**
```
Original: "truck maintenance"

Expanded: "truck maintenance OR vehicle service OR fleet upkeep
           OR preventive maintenance OR equipment repair"
```

**Methods:**
- Synonym expansion (WordNet, embeddings)
- Domain-specific thesaurus
- Related term injection
- Metadata enrichment

### 5. Step-Back Prompting

**Source:** [Step-Back Prompting](https://arxiv.org/abs/2310.06117)

**Concept:** Generate broader question first, then specific

**Example:**
```
Specific: "Why did Invoice #12345 fail validation?"

Step-back: "What are common reasons for invoice validation failures?"

Process:
1. Answer step-back question (general principles)
2. Use context to answer specific question
```

## State-of-the-Art: Microsoft Azure AI (2024)

**Innovation:** Generative query rewriting with semantic ranker

**Performance:**
- **Speed:** 10 rewrites for 32-token query in 147ms
- **Improvement:** +12 to +28 points relevance (average +21)
- **Languages:** Works across all content segments and languages

**Architecture:**
1. Query → Rewriter (10 variations)
2. All variations → Retrieval
3. Semantic Ranker → Best results
4. Aggregation → Final response

**Key Insight:** Multiple query variations capture different aspects of intent

## RaFe Framework (EMNLP 2024)

**Source:** [RaFe: Ranking Feedback for Query Rewriting](https://aclanthology.org/2024.findings-emnlp.49/)

**Innovation:** Use reranker feedback to train query rewriting

**Process:**
1. Generate query rewrites
2. Retrieve with each rewrite
3. Reranker scores results
4. Use scores as training signal
5. Improve rewriter model

**Advantage:** No manual annotations needed, learns from ranking preferences

## LLM-QE (2025)

**Source:** [LLM Query Expansion with Ranking Preferences](https://arxiv.org/html/2502.17057v1)

**Innovation:** Align query rewriting with both retriever and LLM preferences

**Architecture:**
- Learns from reranking scores
- Optimizes for end-to-end RAG performance
- Focuses on what actually helps the LLM answer correctly

## Implementation Strategies

### Zero-Shot Rewriting
```python
prompt = f"""Rewrite this query to be more specific and effective:
Original: {query}
Rewritten:"""

rewritten = llm.generate(prompt)
```

### Few-Shot Rewriting
```python
prompt = f"""Rewrite queries for better search:

Example 1:
Original: "truck problems"
Rewritten: "equipment failures and maintenance issues for trucks"

Example 2:
Original: "late payments"
Rewritten: "overdue invoices and payment delays by customer"

Now rewrite:
Original: {query}
Rewritten:"""
```

### Fine-Tuned Model
- Train on (query, good_rewrite, bad_rewrite) triplets
- Use reranker scores as labels
- Optimize for retrieval performance

## Best Practices for Apex

### When to Rewrite
1. **Always:** Normalize (grammar, spelling)
2. **Hybrid queries:** Decompose into sub-queries
3. **Vague queries:** Expand with synonyms
4. **Complex queries:** Use HyDE for context
5. **Domain-specific:** Add technical terms

### Multi-Strategy Approach
```python
def rewrite_query(query, query_type):
    # Always normalize
    normalized = normalize(query)

    if query_type == "SEMANTIC":
        # Use HyDE for semantic search
        return generate_hypothetical_answer(normalized)

    elif query_type == "HYBRID":
        # Decompose complex queries
        return decompose_query(normalized)

    elif query_type == "METADATA":
        # Expand with filters
        return expand_metadata_terms(normalized)

    return normalized
```

### Progressive Rollout
1. **Phase 1:** Normalization only
2. **Phase 2:** Add HyDE for SEMANTIC queries
3. **Phase 3:** Query decomposition for HYBRID
4. **Phase 4:** Full multi-variation rewriting

## Performance Expectations

Based on 2024-2025 research:

| Technique | Relevance Gain | Latency | Complexity |
|-----------|---------------|---------|------------|
| Normalization | +2-5% | <1ms | Low |
| HyDE | +15-20% | 50-100ms | Medium |
| Decomposition | +10-15% | 20-50ms | Medium |
| Multi-variation | +21-28% | 100-200ms | High |
| RaFe (trained) | +25-30% | 50ms | High |

## Integration with Apex Query Router

**Current Flow:**
```
Query → Analyzer → Databases → Results
```

**Enhanced Flow:**
```
Query → Rewriter → Analyzer → Databases → Reranker → Results
                                               ↓
                                     Feedback to Rewriter
```

## References

1. Microsoft Azure AI Search - Query Rewriting (2024)
   https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/raising-the-bar-for-rag-excellence-query-rewriting-and-new-semantic-ranker/4302729

2. HyDE: Precise Zero-Shot Dense Retrieval (2022)
   https://arxiv.org/abs/2212.10496

3. RaFe: Ranking Feedback Improves Query Rewriting (EMNLP 2024)
   https://aclanthology.org/2024.findings-emnlp.49/

4. LLM-QE: Query Expansion with Ranking Preferences (2025)
   https://arxiv.org/html/2502.17057v1

5. Step-Back Prompting (2023)
   https://arxiv.org/abs/2310.06117

6. Advanced RAG Query Optimization
   https://www.myscale.com/blog/advanced-rag-query-optimization/
