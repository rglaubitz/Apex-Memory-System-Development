# Semantic Router - Fast Intent Classification

**Source:** [aurelio-labs/semantic-router](https://github.com/aurelio-labs/semantic-router)
**Date:** 2024-2025
**Tier:** 2 (Verified GitHub Repository - High Quality)
**Stars:** 1000+

## Overview

Semantic Router is a superfast decision-making layer for LLMs and agents. Rather than waiting for slow LLM generations to make tool-use decisions, it uses semantic vector space to make routing decisions based on semantic meaning.

## Key Features

### Performance
- **10ms routing decisions** - dramatically faster than LLM-based classification
- Semantic vector space matching instead of LLM generation
- Local execution support with HuggingFace models

### Architecture

```
User Query → Encoder → Vector Embedding → Router → Similarity Search → Route Selection
```

### Route Definition

Routes are defined with:
- **Name:** Identifier for the route
- **Utterances:** Example queries that match this route
- **Score Threshold:** Minimum similarity score to match
- **Metadata:** Additional context

Example:
```python
politics = Route(
    name="politics",
    utterances=[
        "isn't politics the best thing ever",
        "why don't you tell me about your political opinions",
        "don't you just love the president"
    ],
    score_threshold=0.7
)
```

### Encoder Options

1. **OpenAI Encoder** - text-embedding-3-small/large
2. **Cohere Encoder** - embed-english-v3.0
3. **HuggingFace Encoder** - Local models
4. **FastEmbed** - Fast local embeddings

### Out-of-Scope Detection

When no route matches above threshold, returns `None` instead of forcing a decision.

## Advantages Over Keyword Matching

- **Semantic understanding** - "connected" and "linked" are understood as similar
- **Paraphrase robust** - handles different phrasings
- **Synonym handling** - understands word relationships
- **Context aware** - uses embedding space for meaning

## Hybrid Route Layer

Supports hybrid search combining:
- Semantic similarity (embeddings)
- Keyword matching (for precision)
- Best of both approaches

## Dynamic Routes

Routes can include function calls and parameter extraction:
```python
route = Route(
    name="get_weather",
    utterances=["what's the weather in {location}"],
    function_schema={...}
)
```

## Integration

- Compatible with LangChain agents
- Pinecone and Qdrant index support
- Multi-modal routing (images + text)

## Performance Benchmarks

- **Misclassification rate:** 63.64% for pure keyword approaches
- **Semantic Router:** <5% misclassification
- **Latency:** 10ms average routing time

## Use Cases for Apex

1. **Intent Classification** - Replace keyword-based analyzer
2. **Out-of-Scope Detection** - Detect irrelevant queries
3. **Fast Pre-routing** - Before expensive database queries
4. **Hybrid with LLM** - Use for simple cases, LLM for complex

## Implementation Approach

### Quick Win
```python
from semantic_router import Route, SemanticRouter
from semantic_router.encoders import OpenAIEncoder

routes = [
    Route(name="graph", utterances=["...", "...", "..."]),
    Route(name="temporal", utterances=["...", "...", "..."]),
    Route(name="semantic", utterances=["...", "...", "..."]),
]

encoder = OpenAIEncoder()  # Already have OpenAI in Apex
router = SemanticRouter(encoder=encoder, routes=routes)

# Fast routing
route = router("find connected equipment")
# Returns Route object with .name
```

### Progressive Enhancement
1. Start with high-confidence routes (threshold > 0.8)
2. Fallback to keyword-based for uncertain cases
3. Log decisions for optimization
4. Retrain thresholds with production data

## References

- GitHub: https://github.com/aurelio-labs/semantic-router
- Docs: https://docs.aurelio.ai/semantic-router
- Course: https://www.aurelio.ai/course/semantic-router
- Paper: Dimitrios Manias et al., IEEE GlobeCom 2024
