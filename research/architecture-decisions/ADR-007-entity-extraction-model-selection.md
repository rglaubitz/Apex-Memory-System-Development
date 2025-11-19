# ADR-007: Entity Extraction and Intent Routing Model Selection

**Status:** Approved
**Date:** 2025-11-15
**Deciders:** Development Team
**Related:** Phase 2 (Conversational Memory Feedback Loop), Phase 5 (Human↔Agent Interface)

---

## Context

The Apex Memory System requires two critical LLM-powered capabilities:

1. **Intent Routing:** Classify user queries to route to appropriate databases (graph, temporal, semantic, metadata, hybrid)
2. **Entity Extraction:** Extract structured entities from conversations and documents for Graphiti knowledge graph ingestion

**Requirements:**
- **Accuracy:** 90%+ entity extraction accuracy for Graphiti integration
- **Latency:** <1s intent routing for real-time user experience
- **Cost:** Minimize operational costs at scale (10,000+ conversations/month)
- **Quality:** Structured JSON outputs with strict schema adherence

**Current Implementation (Phase 2):**
- Model: GPT-5 Nano
- Use Case: Entity extraction from conversations
- Cost: $0.000105 per conversation
- Accuracy: 85%+ (estimated baseline)

**Problem:**
- GPT-5 Nano accuracy (85%) may be insufficient for complex entity extraction (90%+ goal)
- Need to evaluate GPT-5 Mini for better quality vs cost trade-offs

---

## Decision

**Adopt a hybrid architecture using both GPT-5 Nano and GPT-5 Mini strategically:**

### 1. Intent Routing: GPT-5 Nano (Low Reasoning)

**Configuration:**
```python
model = "gpt-5-nano"
reasoning_effort = "low"  # 74.2% accuracy, 500ms latency
temperature = 0.0  # Deterministic classification
```

**Use Cases:**
- Query intent classification (graph, temporal, semantic, metadata, hybrid)
- Agent selection (Oscar, Sarah, Maya, System)
- Complexity assessment (simple vs complex extraction)

**Rationale:**
- 74.2% accuracy sufficient for 5 intent categories
- 500ms latency critical for routing (user-facing)
- 5x cheaper than Mini ($0.000105 vs $0.000525)
- Intent routing benefits from **speed > precision**

---

### 2. Entity Extraction: GPT-5 Mini (Medium Reasoning)

**Configuration:**
```python
model = "gpt-5-mini"
reasoning_effort = "medium"  # Optimal balance (67 intelligence, 2-5s)
response_format = {"type": "json_schema", "strict": True}
temperature = 0.0  # Consistent extraction
```

**Use Cases:**
- ConversationIngestionWorkflow (background extraction)
- Graphiti episode creation (complex entities, relationships)
- Structured data parsing (JSON ingestion)
- Receipt processing (Penske truck rentals)

**Rationale:**
- Better structured output quality (fewer schema violations)
- Stronger coreference resolution ("the truck" → "Truck 247")
- Complex relationship extraction (entity graphs, temporal patterns)
- 90%+ accuracy goal (vs 85% Nano baseline)
- 2-5s latency acceptable for background ingestion

---

## Alternatives Considered

### Alternative 1: All GPT-5 Nano

**Pros:**
- Lowest cost ($1.05/month for 10,000 conversations)
- Simplest implementation (single model)
- 90.8% accuracy at medium reasoning (acceptable)

**Cons:**
- Lower structured output quality (more schema violations)
- Weaker coreference resolution
- Limited complex relationship extraction
- May not achieve 90%+ goal consistently

**Verdict:** ❌ Rejected - Quality insufficient for Graphiti integration

---

### Alternative 2: All GPT-5 Mini

**Pros:**
- Best quality (excellent structured outputs, strong reasoning)
- Single model simplicity
- Most recent knowledge (Oct 2024 vs May 2024)

**Cons:**
- 5x higher cost ($5.25/month for 10,000 conversations)
- Slower routing (2-5s vs 500ms not critical for batch, but suboptimal for routing)
- Overkill for simple intent classification

**Verdict:** ❌ Rejected - Cost inefficient, latency suboptimal for routing

---

### Alternative 3: Hybrid (Nano Routing + Mini Extraction) ⭐ SELECTED

**Pros:**
- Optimal cost/quality balance (36% savings vs all-Mini)
- Fast intent routing (500ms Nano)
- High-quality extraction (90%+ Mini)
- Strategic model selection per use case

**Cons:**
- Slightly more complex implementation (two model configs)
- Requires routing logic (minimal overhead)

**Verdict:** ✅ **Selected** - Best balance of cost, quality, and latency

---

## Cost Analysis

### Monthly Costs (10,000 conversations)

| Scenario | Intent Routing | Entity Extraction | Total | vs All-Mini Savings |
|----------|----------------|-------------------|-------|---------------------|
| **All Nano** | $1.05 | $0 (same model) | $1.05 | 80% |
| **All Mini** | $5.25 | $0 (same model) | $5.25 | 0% (baseline) |
| **Hybrid** | $1.05 (Nano) | $2.10 (Mini, 40%) | **$3.15** | **40%** |

**Assumptions for Hybrid:**
- 100% of queries go through intent routing (Nano)
- 40% of conversations require entity extraction (Mini)
- 60% are simple queries without extraction needed

**Cost Ratio:**
- Hybrid is **3x more expensive than all-Nano** ($3.15 vs $1.05)
- Hybrid is **40% cheaper than all-Mini** ($3.15 vs $5.25)

---

## Performance Analysis

### Intent Routing Comparison

| Model | Reasoning Mode | Accuracy | Latency | Cost per Query |
|-------|----------------|----------|---------|----------------|
| **Nano** | Low | 74.2% | 500ms | $0.000105 |
| **Mini** | Low | 75.0% | 500ms | $0.000525 |
| **Mini** | Medium | 75.7% | 2-5s | $0.000525 (14x cost multiplier) |

**Decision:** Nano Low Reasoning (0.8% accuracy difference, 5x cost savings)

---

### Entity Extraction Comparison

| Model | Reasoning Mode | Accuracy | JSON Quality | Cost per Doc |
|-------|----------------|----------|--------------|--------------|
| **Nano** | Medium | 90.8% | Good | $0.000105 (14x cost) |
| **Mini** | Medium | >90% | Excellent | $0.000525 (14x cost) |

**Decision:** Mini Medium Reasoning (better JSON quality, complex relationships worth 5x cost)

---

## Implementation

### Phase 1: Update ConversationEntityExtractor

**File:** `src/apex_memory/services/conversation_entity_extractor.py`

**Changes:**
```python
class ConversationEntityExtractor:
    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-5-mini",  # Changed from gpt-5-nano
        reasoning_effort: str = "medium",  # NEW: low/medium/high
        temperature: float = 0.0,
        agent_id: str = "system",
    ):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = model
        self.reasoning_effort = reasoning_effort
        # ...

    async def extract_entities(self, messages: list[dict]) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=2000,
            response_format={"type": "json_schema", "strict": True},
            # NEW: reasoning_effort parameter
            extra_body={"reasoning_effort": self.reasoning_effort},
        )
        # ...
```

---

### Phase 2: Create IntentClassifier

**File:** `src/apex_memory/services/intent_classifier.py` (NEW)

**Implementation:**
```python
from openai import AsyncOpenAI

class IntentClassifier:
    """
    Classify user query intent using GPT-5 Nano (low reasoning).

    Intent Categories:
    - graph_query: Entity relationships, connections
    - temporal_query: Time-based patterns, trends
    - semantic_query: Semantic similarity search
    - metadata_query: Filters, aggregations
    - hybrid_query: Combination of above
    """

    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = "gpt-5-nano"
        self.reasoning_effort = "low"  # 74.2% accuracy, 500ms

    async def classify(self, query: str) -> dict:
        """
        Classify query intent.

        Returns:
            {
                "intent": "graph_query",
                "confidence": 0.95,
                "complexity": "simple",  # simple | complex
                "entities": ["Truck 247", "ACME Corp"]
            }
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": query},
            ],
            temperature=0.0,
            response_format={"type": "json_schema", "strict": True},
            extra_body={"reasoning_effort": self.reasoning_effort},
        )

        return json.loads(response.choices[0].message.content)

    def _get_system_prompt(self) -> str:
        return """You are an intent classification system for a knowledge graph database.

Classify queries into one of these intents:
- graph_query: Entity relationships (e.g., "Who operates Truck 247?")
- temporal_query: Time-based patterns (e.g., "Show maintenance trends over Q4")
- semantic_query: Semantic similarity (e.g., "Find documents similar to this invoice")
- metadata_query: Filters/aggregations (e.g., "List all trucks with mileage > 100K")
- hybrid_query: Combination (e.g., "Show Truck 247's operators and recent maintenance")

Also assess complexity:
- simple: Clear entities, straightforward patterns
- complex: Coreference resolution needed, ambiguous entities, multiple relationships

Output JSON:
{
    "intent": "<intent_type>",
    "confidence": <0-1>,
    "complexity": "<simple|complex>",
    "entities": ["entity1", "entity2"]
}"""
```

---

### Phase 3: Update SlackConversationService

**File:** `src/apex_memory/services/slack_conversation_service.py`

**Integration:**
```python
class SlackConversationService:
    def __init__(
        self,
        conversation_service,
        query_router,
        intent_classifier,  # NEW: GPT-5 Nano classifier
        entity_extractor,    # GPT-5 Mini extractor
    ):
        self.conversation_service = conversation_service
        self.query_router = query_router
        self.intent_classifier = intent_classifier  # Nano
        self.entity_extractor = entity_extractor    # Mini

    async def process_slack_message(
        self,
        user_id: str,
        channel_id: str,
        thread_ts: str | None,
        message: str,
    ):
        # Step 1: Classify intent (Nano - 500ms)
        intent = await self.intent_classifier.classify(message)

        # Step 2: Route to appropriate handler
        if intent["intent"] == "chitchat":
            # Quick response, no extraction needed
            return await self._handle_chitchat(message)

        # Step 3: Extract entities if needed (Mini - 2-5s, background)
        if intent["complexity"] == "complex":
            # Background extraction with Mini (high quality)
            asyncio.create_task(
                self.entity_extractor.extract_entities([{"content": message}])
            )

        # Step 4: Process via ConversationService
        response = await self.conversation_service.process_message(...)

        return response
```

---

## Consequences

### Positive

1. **Cost Optimized:** 40% savings vs all-Mini ($3.15 vs $5.25/month)
2. **Fast Routing:** 500ms intent classification (user-facing)
3. **High-Quality Extraction:** 90%+ accuracy for Graphiti (Mini medium reasoning)
4. **Strategic Model Selection:** Right model for right task
5. **Scalable:** Costs grow linearly with usage
6. **Future-Proof:** Easy to adjust routing thresholds based on accuracy requirements

### Negative

1. **Increased Complexity:** Two model configurations instead of one
2. **Routing Logic:** Need to implement intent classification → model selection
3. **Monitoring:** Track performance metrics for both models separately
4. **Higher Cost than All-Nano:** 3x more expensive ($3.15 vs $1.05)

### Mitigation

1. **Complexity:** Abstract model selection behind service layer (IntentClassifier + EntityExtractor)
2. **Routing Logic:** Simple if/else based on intent complexity (< 20 lines)
3. **Monitoring:** Add per-model metrics in existing Grafana dashboards
4. **Cost:** Acceptable trade-off for 90%+ accuracy goal (critical for Graphiti)

---

## Monitoring & Validation

### Key Metrics to Track

**Intent Classification (Nano):**
- Classification accuracy (target: 74%+)
- Latency P50/P95 (target: <500ms)
- Cost per query (target: $0.000105)
- Cache hit rate (target: 90%+)

**Entity Extraction (Mini):**
- Extraction accuracy (target: 90%+)
- JSON schema compliance (target: 99%+)
- Latency P50/P95 (target: <5s)
- Cost per document (target: $0.000525)
- Cache hit rate (target: 88%+)

### Validation Plan

**Week 1:** Implement IntentClassifier with GPT-5 Nano
- Measure classification accuracy on 100 sample queries
- Validate 500ms latency target
- Confirm cost at $0.000105/query

**Week 2:** Update ConversationEntityExtractor to GPT-5 Mini
- Measure extraction accuracy on 100 sample conversations
- Validate JSON schema compliance
- Compare accuracy vs Nano baseline (target: +5%)

**Week 3:** A/B Testing
- Run both models in parallel on 1,000 queries
- Compare accuracy, latency, cost metrics
- Adjust reasoning modes if needed (low vs medium)

**Week 4:** Production Deployment
- Deploy hybrid architecture
- Monitor costs daily
- Track accuracy with manual spot checks (weekly)

---

## References

### Research Documentation
- **GPT-5 Nano vs Mini Comparison:** `research/documentation/openai/GPT-5-NANO-VS-MINI-COMPARISON.md`

### Official Sources
- OpenAI API Pricing: https://openai.com/api/pricing/
- GPT-5 Platform Docs: https://platform.openai.com/docs/models/gpt-5-mini
- Reasoning Modes Guide: https://platform.openai.com/docs/guides/reasoning

### Benchmarks
- Label Studio GPT-5 Benchmarks: 90.8% entity extraction (medium reasoning)
- Intent Classification Study: 74.2% Nano (low reasoning), 75.7% Mini (medium reasoning)

---

## Decision Rationale Summary

**Intent Routing → GPT-5 Nano (Low Reasoning):**
- Speed critical for user experience (500ms vs 2-5s)
- 74.2% accuracy sufficient for 5 intent categories
- 5x cost savings vs Mini ($0.000105 vs $0.000525)

**Entity Extraction → GPT-5 Mini (Medium Reasoning):**
- Quality critical for Graphiti integration (90%+ goal)
- Better structured outputs (fewer schema violations)
- Complex relationships worth 5x cost premium
- 2-5s latency acceptable for background ingestion

**Hybrid Architecture:**
- 40% cost savings vs all-Mini
- Fast routing + high-quality extraction
- Best balance of cost, quality, latency

---

**Status:** ✅ Approved
**Next Steps:**
1. Update Phase 5 planning document with hybrid architecture
2. Implement IntentClassifier (Week 1)
3. Update ConversationEntityExtractor model config (Week 2)
4. A/B test accuracy (Week 3)
5. Deploy to production (Week 4)

