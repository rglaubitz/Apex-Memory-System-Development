# OpenAI API - Complete Model Documentation

**Last Updated:** 2025-10-06
**Verified:** October 2025 (Current SOTA)
**Official Source:** https://platform.openai.com/docs/

---

## Overview

OpenAI provides state-of-the-art AI models for language understanding, generation, embeddings, and reasoning. This document covers all models available as of October 2025.

---

## 🔥 Language Models (LLMs)

### GPT-5 (August 2025) - Current SOTA

**Official Announcement:** https://openai.com/index/introducing-gpt-5/

**Release Date:** August 7, 2025
**Status:** Generally Available
**Model ID:** `gpt-5`

#### Key Capabilities

- **State-of-the-art performance** across coding, math, writing, health, visual perception
- **Advanced reasoning:** Knows when to respond quickly vs think longer for expert-level responses
- **Multimodal:** Text, images, vision in unified system
- **Context Window:** 128K tokens (standard), 200K+ with extended context
- **Knowledge Cutoff:** June 2024

#### Benchmarks (vs GPT-4o)

| Benchmark | GPT-5 | GPT-4o | Improvement |
|-----------|-------|--------|-------------|
| **AIME 2025** (Math) | 94.6% | ~50% | +89% |
| **SWE-bench Verified** (Coding) | 74.9% | ~40% | +87% |
| **MMMU** (Multimodal) | 84.2% | ~70% | +20% |
| **HealthBench Hard** | 46.2% | ~30% | +54% |

#### Factual Accuracy

- **With web search:** ~45% less likely to contain factual errors than GPT-4o
- **When thinking:** ~80% less likely to contain factual errors than OpenAI o3

#### Variants

**GPT-5 (Standard):**
- General purpose, all users
- Faster responses for most queries

**GPT-5 Pro:**
- Extended reasoning capability
- Available to Pro subscribers
- Can spend more time thinking on complex problems

**GPT-5 Instant:**
- Low-latency variant
- Optimized for real-time applications
- Recognizes emotional distress patterns (mental health trained)

#### Pricing

*(Check official pricing page for current rates)*
**Pricing Page:** https://openai.com/api/pricing/

---

### GPT-5-Codex (September 2025)

**Official Announcement:** https://techcrunch.com/2025/09/15/openai-upgrades-codex-with-a-new-version-of-gpt-5/

**Release Date:** September 15, 2025
**Status:** Generally Available
**Model ID:** `gpt-5-codex`

#### Key Features

- **Dynamic thinking time:** Can spend anywhere from seconds to 7+ hours on coding tasks
- **Customized version of GPT-5** optimized for code generation
- **Advanced code understanding:** Better at complex refactoring, architectural decisions
- **Extended reasoning:** Spends thinking time dynamically based on complexity

#### Use Cases

- Complex codebase refactoring
- Architecture design
- Multi-file code generation
- Bug hunting in large codebases
- Algorithm optimization

---

### GPT-4.1 Series (April 2025)

**Official Announcement:** https://openai.com/index/gpt-4-1/
**Release Date:** April 14, 2025
**Context Window:** 1 million tokens (all variants)

The GPT-4.1 series represents major improvements on coding, instruction following, and long context—plus OpenAI's first-ever nano model.

---

#### GPT-4.1 (Standard)

**Model ID:** `gpt-4.1`
**Status:** API-only (not in ChatGPT)

**Key Features:**
- Up to 1M tokens of context (up from 128K in GPT-4o)
- Outperforms GPT-4o across the board
- Refreshed knowledge cutoff: June 2024
- Major gains in coding and instruction following

---

#### GPT-4.1-mini

**Model ID:** `gpt-4.1-mini`
**Status:** Generally Available

**Key Features:**
- **Performance:** Matches or exceeds GPT-4o in intelligence evals
- **Speed:** Nearly 50% lower latency than GPT-4o
- **Cost:** 83% cheaper than GPT-4o
- **Context:** 1M tokens
- **Use Case:** Significant leap in small model performance

**Pricing:**
- **Input:** $0.40/million tokens
- **Output:** $1.60/million tokens

**Benchmarks:**
- Beats GPT-4o in many benchmarks
- Ideal for high-volume applications where cost matters

---

#### GPT-4.1-nano ⚡ (First Nano Model)

**Model ID:** `gpt-4.1-nano`
**Status:** Generally Available

**Key Features:**
- **Fastest and cheapest** OpenAI model available
- **Exceptional performance** at small size
- **Context:** 1M tokens
- **Low latency:** Optimized for real-time applications

**Pricing:**
- **Input:** $0.10/million tokens
- **Output:** $0.40/million tokens

**Benchmarks:**
- **MMLU:** 80.1%
- **GPQA:** 50.3%
- **Aider Polyglot:** 9.8%
- Higher scores than GPT-4o mini

**Ideal For:**
- High-frequency API calls
- Real-time chat applications
- Cost-sensitive deployments
- Simple reasoning tasks

---

## 📊 Embedding Models

### text-embedding-3-large (Best Performance)

**Model ID:** `text-embedding-3-large`
**Released:** January 2024
**Status:** Current SOTA for embeddings

#### Specifications

- **Dimensions:** 3,072 (default, configurable via API)
- **Max Input Tokens:** 8,191
- **Pricing:** $0.13 per 1M tokens
- **Performance:** Best embedding model available

#### Benchmarks

| Benchmark | text-embedding-3-large | text-embedding-ada-002 | Improvement |
|-----------|------------------------|------------------------|-------------|
| **MIRACL** | 54.9% | 31.4% | +75% |
| **MTEB** | 64.6% | 61.0% | +6% |

#### Use Cases

- Highest accuracy semantic search
- Advanced RAG systems
- Clustering and classification
- When performance > cost

#### Example

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Your text here"
)

embedding = response.data[0].embedding
# Returns 3,072-dimensional vector
```

---

### text-embedding-3-small (Most Efficient)

**Model ID:** `text-embedding-3-small`
**Released:** January 2024
**Status:** Current (cost-optimized)

#### Specifications

- **Dimensions:** 1,536 (default, configurable via API)
- **Max Input Tokens:** 8,191
- **Pricing:** $0.02 per 1M tokens (5x cheaper than 3-large)
- **Performance:** Good balance of quality and cost

#### Benchmarks

| Benchmark | text-embedding-3-small | text-embedding-ada-002 | Improvement |
|-----------|------------------------|------------------------|-------------|
| **MIRACL** | 44.0% | 31.4% | +40% |
| **MTEB** | 62.3% | 61.0% | +2% |

#### Use Cases

- Cost-sensitive applications
- High-volume embedding generation
- Good enough accuracy for most RAG systems
- When speed matters

#### Example

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Your text here"
)

embedding = response.data[0].embedding
# Returns 1,536-dimensional vector
```

---

### Embedding Model Comparison

| Model | Dimensions | Price/1M tokens | MTEB Score | Use Case |
|-------|------------|----------------|------------|----------|
| **text-embedding-3-large** | 3,072 | $0.13 | 64.6% | Best performance |
| **text-embedding-3-small** | 1,536 | $0.02 | 62.3% | Best cost/performance |
| text-embedding-ada-002 | 1,536 | $0.10 | 61.0% | Legacy (not recommended) |

**Recommendation:** Use `text-embedding-3-large` for highest accuracy, `text-embedding-3-small` for production cost optimization.

---

## 🔧 Common Embedding Features

### Dimension Reduction

Both text-embedding-3 models support dimension reduction:

```python
# Reduce dimensions without losing concept-representing properties
response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Sample text",
    dimensions=1024  # Reduce from 3,072 to 1,024
)
```

### Batch Processing

Process multiple texts in one API call:

```python
texts = ["text1", "text2", "text3"]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

for i, data in enumerate(response.data):
    embedding = data.embedding
```

---

## 🎯 Model Selection Guide

### When to Use GPT-5

- Need absolute best performance
- Complex reasoning tasks
- Multimodal understanding
- Latest knowledge (June 2024 cutoff)
- Budget allows for premium

### When to Use GPT-5-Codex

- Complex coding tasks
- Architectural decisions
- Large codebase refactoring
- Can benefit from extended thinking time

### When to Use GPT-4.1-mini

- High-volume applications
- Cost optimization important
- Performance needs exceed GPT-4o
- 1M context window needed

### When to Use GPT-4.1-nano

- Highest-frequency API calls
- Real-time applications
- Extremely cost-sensitive
- Simple reasoning sufficient

### When to Use text-embedding-3-large

- Highest accuracy required
- Research/academic applications
- Small dataset (cost not issue)
- Best RAG performance needed

### When to Use text-embedding-3-small

- Production RAG systems
- High-volume embedding generation
- Good accuracy sufficient
- Cost optimization important

---

## 📡 API Reference

### Chat Completions Endpoint

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

response = client.chat.completions.create(
    model="gpt-5",  # or gpt-4.1-mini, gpt-4.1-nano, gpt-5-codex
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    max_tokens=1000,
    temperature=0.7
)

print(response.choices[0].message.content)
```

### Embeddings Endpoint

```python
response = client.embeddings.create(
    model="text-embedding-3-large",  # or text-embedding-3-small
    input="Text to embed",
    encoding_format="float"
)

embedding = response.data[0].embedding
```

---

## 🔐 Best Practices

### API Key Security

```python
import os
from openai import OpenAI

# ALWAYS use environment variables
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
```

### Error Handling

```python
from openai import OpenAI, OpenAIError

client = OpenAI(api_key="YOUR_API_KEY")

try:
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": "Hello"}]
    )
except OpenAIError as e:
    print(f"API error: {e}")
```

### Rate Limiting

Implement exponential backoff:

```python
import time
from openai import OpenAI, RateLimitError

def create_with_retry(client, **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)
```

---

## 📚 Official Resources

### Documentation
- **Main Docs:** https://platform.openai.com/docs/
- **API Reference:** https://platform.openai.com/docs/api-reference/
- **Models Page:** https://platform.openai.com/docs/models/
- **GPT-5 Announcement:** https://openai.com/index/introducing-gpt-5/
- **GPT-4.1 Announcement:** https://openai.com/index/gpt-4-1/

### Tools & Libraries
- **Python Library:** https://github.com/openai/openai-python
- **Node.js Library:** https://github.com/openai/openai-node
- **Pricing:** https://openai.com/api/pricing/
- **Rate Limits:** https://platform.openai.com/account/rate-limits

### Community
- **Developer Forum:** https://community.openai.com/
- **Cookbook:** https://cookbook.openai.com/
- **GitHub Examples:** https://github.com/openai/openai-cookbook

---

## 🔄 Migration Guide

### From GPT-4o to GPT-5

```python
# Old
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...]
)

# New
response = client.chat.completions.create(
    model="gpt-5",  # or gpt-5-pro
    messages=[...]
)
# 80% better reasoning, multimodal, same API
```

### From GPT-4o to GPT-4.1-mini (Cost Optimization)

```python
# Old: GPT-4o
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...]
)

# New: 83% cheaper, 50% faster, better performance
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[...]
)
```

### From ada-002 to text-embedding-3

```python
# Old
embedding = client.embeddings.create(
    model="text-embedding-ada-002",
    input="text"
)

# New (best performance)
embedding = client.embeddings.create(
    model="text-embedding-3-large",
    input="text"
)

# New (cost-optimized)
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="text"
)
```

---

## ⚠️ Breaking Changes & Deprecations

### Current Status (October 2025)

- **text-embedding-ada-002:** Not deprecated, but not recommended for new projects
- **GPT-4o:** Still available, but GPT-5 is superior
- **GPT-4 Turbo:** Superseded by GPT-4.1 series
- **GPT-3.5 Turbo:** Legacy, use GPT-4.1-nano instead

### Deprecated Models

- GPT-3 (legacy)
- GPT-3.5 (use GPT-4.1-nano)
- text-embedding-ada-001 (use text-embedding-3-small)

---

## 📊 Performance Comparison Matrix

| Model | Released | Context | Speed | Cost | Best For |
|-------|----------|---------|-------|------|----------|
| **GPT-5** | Aug 2025 | 128K+ | Medium | High | SOTA reasoning |
| **GPT-5-Codex** | Sep 2025 | 128K+ | Variable | High | Complex coding |
| **GPT-4.1** | Apr 2025 | 1M | Medium | High | Long context |
| **GPT-4.1-mini** | Apr 2025 | 1M | Fast | Low | Cost-optimized |
| **GPT-4.1-nano** | Apr 2025 | 1M | Fastest | Lowest | High-frequency |
| **text-embedding-3-large** | Jan 2024 | 8K | Fast | Medium | Best accuracy |
| **text-embedding-3-small** | Jan 2024 | 8K | Fast | Low | Production RAG |

---

**Quality Rating:** ⭐⭐⭐⭐⭐ Tier 1 - Official Documentation
**Source Type:** Official API Documentation + Release Announcements
**Last Verified:** 2025-10-06
**Next Review:** 2025-11-01 (monthly)

---

## Version History

- **2025-10-06:** Major update - Added GPT-5, GPT-5-Codex, GPT-4.1 series, text-embedding-3-large
- **2025-10-06 (original):** Initial version - Only text-embedding-3-small (OUTDATED)

---

## Cross-References

- **Research:** `../query-routing/` - Query routing research (uses OpenAI embeddings)
- **Upgrades:** `../../../upgrades/query-router/` - Query Router improvement plan
- **ADRs:** `../../architecture-decisions/ADR-001` - Multi-database architecture
