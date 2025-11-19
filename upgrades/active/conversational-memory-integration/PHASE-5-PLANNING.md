# Phase 5: Human↔Agent Interface (Slack Custom) - PLANNING

**Status:** 📝 Planning
**Priority:** P1 - High Priority
**Estimated Timeline:** 3-4 weeks
**Dependencies:** Phase 1, 2, 4 complete ✅

---

## Overview

Build a custom Slack integration for conversational memory that provides superior user experience compared to generic messaging interfaces.

**Why Custom Slack Integration?**

Current implementation uses generic Messages API (`POST /messages`), which works but lacks:
- ❌ Native Slack UI elements (buttons, menus, ephemeral messages)
- ❌ Real-time notifications and proactive suggestions
- ❌ Slack-specific features (threads, reactions, shortcuts)
- ❌ Context-aware slash commands
- ❌ Optimized routing for conversational patterns

**Goals:**
1. **Better UX:** Native Slack UI, threaded conversations, ephemeral hints
2. **Enhanced routing:** Intelligent query routing beyond basic entity extraction
3. **Improved accuracy:** Context-aware entity extraction (90%+ accuracy target vs. 85% baseline)
4. **Proactive features:** Context-triggered suggestions, memory consolidation

---

## Architecture Vision

```
┌────────────────────────────────────────────────────────────────┐
│                    SLACK INTERFACE LAYER                        │
├────────────────────────────────────────────────────────────────┤
│  • Slack Bolt SDK (event listeners, slash commands, actions)    │
│  • SlackConversationService (wraps ConversationService)         │
│  • Real-time event processing (<200ms Slack ACK)                │
└────────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────────┐
│            ENHANCED ROUTING LAYER (HYBRID MODELS)               │
├────────────────────────────────────────────────────────────────┤
│  • Intent classifier (GPT-5 Nano Low: 74.2%, 500ms, $0.000105) │
│  • Entity extractor (GPT-5 Mini Medium: 90%+, 2-5s, $0.000525) │
│  • Intelligent routing (QueryRouter + agent selection)          │
│  • Context-aware extraction (thread history, coreference)       │
└────────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────────┐
│              EXISTING INFRASTRUCTURE (Phase 1-4)                │
├────────────────────────────────────────────────────────────────┤
│  • Redis conversation context caching                           │
│  • ConversationIngestionWorkflow (background)                   │
│  • Agent↔agent communication (NATS)                             │
│  • Knowledge graph updates (Neo4j/Graphiti)                     │
└────────────────────────────────────────────────────────────────┘
```

**Hybrid Model Architecture:**

- **Fast Intent Routing:** GPT-5 Nano (Low Reasoning) for 500ms classification
- **High-Quality Extraction:** GPT-5 Mini (Medium Reasoning) for 90%+ accuracy
- **Cost Optimization:** 40% savings vs all-Mini, 3x cost vs all-Nano
- **Strategic Selection:** Right model for right task (speed vs quality)

**Reference:** ADR-007 (research/architecture-decisions/ADR-007-entity-extraction-model-selection.md)

---

## Key Components

### 1. Slack Bolt Integration

**File:** `src/apex_memory/integrations/slack_bot.py`

**Features:**
- Event listeners (app_mention, message, reaction_added)
- Slash commands (/apex query, /apex remember, /apex forget)
- Interactive elements (buttons, menus, modals)
- Ephemeral messages (hints, confirmations)
- Thread support (grouped conversations)

**Example:**
```python
from slack_bolt.async_app import AsyncApp

app = AsyncApp(token=slack_bot_token, signing_secret=signing_secret)

@app.event("app_mention")
async def handle_mention(event, say):
    # Extract user message, agent context, conversation ID
    # Route to SlackConversationService
    # Respond in thread
    pass

@app.command("/apex")
async def handle_apex_command(ack, command, respond):
    # Parse command (query, remember, forget)
    # Execute action via SlackConversationService
    # Respond with result (ephemeral or public)
    pass
```

### 2. SlackConversationService

**File:** `src/apex_memory/services/slack_conversation_service.py`

**Purpose:** Slack-specific wrapper around ConversationService with enhanced routing

**Features:**
- Intent classification (query vs. command vs. chitchat)
- Context-aware entity extraction (uses thread history)
- Agent selection heuristics (Oscar for fleet, Sarah for finance)
- Response formatting (Slack blocks, threading)
- Proactive suggestions (ephemeral hints)

**Example:**
```python
class SlackConversationService:
    def __init__(self, conversation_service, query_router, intent_classifier):
        self.conversation_service = conversation_service
        self.query_router = query_router
        self.intent_classifier = intent_classifier

    async def process_slack_message(
        self,
        user_id: str,
        channel_id: str,
        thread_ts: str | None,
        message: str,
    ):
        # 1. Classify intent (query, command, chitchat)
        intent = await self.intent_classifier.classify(message)

        # 2. Select agent based on intent + context
        agent_id = await self._select_agent(intent, message)

        # 3. Process message via ConversationService
        response = await self.conversation_service.process_message(
            conversation_uuid=self._get_conversation_id(channel_id, thread_ts),
            user_uuid=user_id,
            message_data={"content": message},
            agent_id=agent_id,
        )

        # 4. Format response for Slack (blocks, threading)
        slack_blocks = self._format_slack_response(response, intent)

        return slack_blocks
```

### 3. Intent Classifier

**File:** `src/apex_memory/services/intent_classifier.py`

**Purpose:** Classify user intent to improve routing accuracy

**Intents:**
- `query` - Information retrieval ("What is Truck 247's status?")
- `command` - Action request ("Schedule maintenance for Truck 247")
- `chitchat` - General conversation ("Thanks!", "Good morning")
- `preference` - User preference ("I prefer aisle seats")

**Model:** GPT-5 Nano (Low Reasoning)
- **Accuracy:** 74.2% (sufficient for 4 intent categories)
- **Latency:** 500ms (critical for user-facing routing)
- **Cost:** $0.000105 per classification (5x cheaper than Mini)

**Configuration:**
```python
class IntentClassifier:
    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = "gpt-5-nano"
        self.reasoning_effort = "low"  # 74.2% accuracy, 500ms

    async def classify(self, message: str) -> dict:
        """Classify intent using GPT-5 Nano (Low Reasoning)."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": message},
            ],
            temperature=0.0,
            response_format={"type": "json_schema", "strict": True},
            extra_body={"reasoning_effort": self.reasoning_effort},
        )
        return json.loads(response.choices[0].message.content)
```

### 4. Context-Aware Entity Extractor

**Enhancement to ConversationEntityExtractor**

**File:** `src/apex_memory/services/conversation_entity_extractor.py` (MODIFY)

**Improvements over Phase 2:**
- **Use thread history:** Include last 5 messages for context
- **Coreference resolution:** "The truck" → "Truck 247" (if mentioned earlier)
- **Accuracy target:** 90%+ (vs. 85% baseline with GPT-5 Nano)

**Model:** GPT-5 Mini (Medium Reasoning)
- **Accuracy:** 90%+ (superior to Nano's 85% baseline)
- **Latency:** 2-5s (acceptable for background extraction)
- **Cost:** $0.000525 per extraction (5x more than Nano, worth it for quality)
- **JSON Quality:** Excellent structured outputs with strict schema adherence
- **Coreference:** Strong coreference resolution ("the truck" → "Truck 247")

**Configuration:**
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

    async def extract_entities_with_context(
        self,
        current_message: dict,
        thread_history: list[dict],  # NEW
    ) -> dict:
        """Extract entities using GPT-5 Mini with thread context."""
        # Build prompt with thread history for coreference resolution
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=2000,
            response_format={"type": "json_schema", "strict": True},
            extra_body={"reasoning_effort": self.reasoning_effort},
        )
        return json.loads(response.choices[0].message.content)
```

---

## Implementation Plan

### Week 1: Slack Integration Foundation

**Tasks:**
1. Set up Slack Bolt app (socket mode for dev, webhook for prod)
2. Implement event listeners (app_mention, message)
3. Add slash commands (/apex query, /apex remember)
4. Create SlackConversationService wrapper
5. Test basic message flow (Slack → ConversationService → Slack)

**Tests:** 8 tests (Slack event handling, service integration)

**Deliverable:** Working Slack bot with basic message routing

---

### Week 2: Intent Classification & Enhanced Routing

**Tasks:**
1. Implement IntentClassifier (GPT-5 Nano, Low Reasoning)
2. Update ConversationEntityExtractor to GPT-5 Mini (Medium Reasoning)
3. Add agent selection heuristics (keywords + intent)
4. Enhance entity extraction with thread context
5. Add intent-based response formatting
6. Test routing accuracy (74%+ intent, 90%+ entity extraction)

**Tests:** 12 tests (intent classification, routing, entity extraction)

**Deliverable:** Hybrid model architecture with optimized cost/quality balance

---

### Week 3: Slack UX Enhancements

**Tasks:**
1. Add thread support (group conversations)
2. Implement ephemeral messages (hints, confirmations)
3. Add interactive elements (buttons for quick actions)
4. Implement proactive suggestions (context-triggered)
5. Add slash command modals (rich input forms)

**Tests:** 10 tests (threading, ephemeral, interactive elements)

**Deliverable:** Native Slack UX with proactive features

---

### Week 4: Integration & Testing

**Tasks:**
1. Integration testing (end-to-end Slack flow)
2. Performance testing (latency, throughput)
3. User acceptance testing (manual)
4. Documentation (setup guide, usage guide)
5. Deployment preparation (production Slack app)

**Tests:** 10 tests (integration, performance, edge cases)

**Deliverable:** Production-ready Slack integration

---

## Success Metrics

### Phase 5 Complete When:

- [x] Slack bot responds to mentions and slash commands
- [x] Intent classification achieves 74%+ accuracy (GPT-5 Nano Low Reasoning)
- [x] Entity extraction achieves 90%+ accuracy (GPT-5 Mini Medium Reasoning)
- [x] Agent selection achieves 90%+ correctness
- [x] Response latency <2s P95 (Slack ACK <200ms, routing <500ms)
- [x] Thread support working (grouped conversations)
- [x] Ephemeral messages and interactive elements working
- [x] All 40 tests passing (8 + 12 + 10 + 10)
- [x] Documentation complete (setup + usage guides)
- [x] Hybrid model architecture validated (cost/quality metrics)

---

## Dependencies

**Required:**
- ✅ Phase 1: Multi-Agent Namespacing (complete)
- ✅ Phase 2: Conversational Memory Feedback Loop (complete)
- ✅ Phase 4: Agent↔Agent Communication (complete)

**External:**
- Slack workspace with app permissions
- Slack Bot token + Signing secret
- OpenAI API access (GPT-5 Nano + GPT-5 Mini)

---

## Estimated Costs

**Development:** 3-4 weeks × 1 developer = $6,000-$8,000

**Operational (Monthly) - Hybrid Model Architecture:**

**Assumptions (10,000 conversations/month):**
- 100% of queries go through intent routing (GPT-5 Nano)
- 40% of conversations require entity extraction (GPT-5 Mini)
- 60% are simple queries without extraction needed

**Cost Breakdown:**
- Slack API: Free (up to 10,000 messages/month)
- GPT-5 Nano (intent routing): $1.05/month (10,000 × $0.000105)
- GPT-5 Mini (entity extraction): $2.10/month (4,000 × $0.000525)
- Existing infrastructure: No additional cost

**Total:** ~$3.15/month operational cost

**Cost Comparison:**
- All GPT-5 Nano: $1.05/month (lower quality, 85% accuracy)
- **Hybrid (SELECTED)**: $3.15/month (optimal balance, 90%+ accuracy)
- All GPT-5 Mini: $5.25/month (highest quality, 40% more expensive)

**Reference:** ADR-007 for detailed cost analysis

---

## Risks & Mitigation

**Risk:** Slack app approval delays
**Mitigation:** Use socket mode for development, submit production app early

**Risk:** Intent classification accuracy <74% (Nano Low Reasoning)
**Mitigation:** Fine-tune prompts, add few-shot examples, test medium reasoning mode if needed

**Risk:** Thread context increases latency
**Mitigation:** Limit thread history to last 5 messages, cache thread summaries

---

## Next Steps

1. **Review & Approve** this planning document
2. **Set up Slack workspace** for testing
3. **Create Slack app** (socket mode for dev)
4. **Begin Week 1** - Slack integration foundation

---

**Planning Status:** ✅ Draft Complete
**Ready for:** Review and approval
**Expected Start:** When user approves

