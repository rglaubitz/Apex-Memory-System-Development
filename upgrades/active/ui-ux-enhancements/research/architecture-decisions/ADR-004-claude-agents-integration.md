# ADR-004: Claude Agents SDK Integration

**Status:** Accepted
**Date:** 2025-10-21
**Decision Makers:** Development Team
**Affected Components:** AI Conversation Hub, Backend API, Tool Execution

---

## Context

### Problem Statement

The Apex Memory System UI requires intelligent, multi-turn conversation capabilities with the following requirements:

1. **Multi-Turn Context Management**
   - Maintain conversation history across multiple user turns
   - Synthesize information from previous messages
   - Handle complex queries requiring multiple tool calls

2. **Intelligent Tool Orchestration**
   - Execute multiple knowledge graph queries in sequence
   - Aggregate results from different databases (Neo4j, PostgreSQL, Qdrant)
   - Synthesize coherent narrative responses from fragmented data

3. **State Management**
   - Track conversation state across user sessions
   - Manage tool execution results
   - Handle error recovery and retry logic

4. **User Experience**
   - Sub-second latency for simple queries
   - Progressive streaming for complex multi-tool queries
   - Clear indication of agent reasoning process

### Current Implementation (Phase 2)

**Week 2 delivers:**
- Direct Anthropic API integration with streaming
- Single-turn tool execution (one tool per message)
- Manual message history management
- Basic tool result handling

**Limitations:**
- No multi-turn orchestration (user must manually prompt for follow-ups)
- No automatic tool chaining (user must ask "now search for X")
- Limited context synthesis (results presented as-is)
- No learning from conversation patterns

### Desired State (Phase 2.5)

**Week 5 should enable:**
- **Multi-turn orchestration** - Agent automatically plans 3-6 queries for complex questions
- **Context synthesis** - Agent generates narrative answers from multiple tool results
- **Conversational memory** - Agent remembers entity relationships from earlier in conversation
- **Intelligent follow-ups** - Agent suggests related queries based on results

---

## Decision

**We will integrate the Anthropic Agents SDK (Beta) in Phase 2.5 to enable agent-based conversation features.**

### Implementation Approach

**Phase 2.5 (Week 5) scope:**

1. **Integrate Agents SDK**
   - Add `anthropic-agents` Python package (backend)
   - Create agent orchestration layer (`src/apex_memory/agents/`)
   - Implement tool registry for knowledge graph tools

2. **Enable Multi-Turn Features**
   - Implement conversation context synthesis
   - Enable multi-tool orchestration for complex queries
   - Add agent reasoning transparency (show planning steps)

3. **Maintain Backward Compatibility**
   - Keep direct API streaming for simple queries (Week 2)
   - Add agent orchestration as opt-in feature (feature flag)
   - Preserve existing tool execution patterns

**Rollout strategy:**
- Week 2-4: Direct API with streaming (stable foundation)
- Week 5: Add Agents SDK layer (opt-in with `use_agent=true` query param)
- Week 6+: Evaluate agent performance, potentially make default

---

## Research Support

### Tier 1 Sources (Official Documentation)

**Anthropic Agents SDK Documentation**
- **Source:** https://docs.anthropic.com/agents/
- **Tier:** 1 (Official Documentation)
- **Version:** 0.1.0+ (Beta)
- **Accessed:** 2025-10-21
- **Reference:** RESEARCH-REFERENCES.md (Phase 2.5 section)

**Key capabilities:**
- Multi-turn orchestration with conversation memory
- Automatic tool chaining based on task requirements
- Built-in error recovery and retry logic
- Context synthesis from multiple tool results

**Anthropic Claude API Documentation**
- **Source:** https://docs.anthropic.com/claude/reference/getting-started
- **Tier:** 1 (Official Documentation)
- **Version:** API v1 (2023-06-01)
- **Reference:** RESEARCH-REFERENCES.md (Phase 2 section)

**Comparison:** Direct API provides lower-level control but requires manual orchestration logic. Agents SDK abstracts this complexity.

### Tier 2 Sources (Verified Repositories)

**Anthropic Agents GitHub Repository**
- **Source:** https://github.com/anthropics/anthropic-agents
- **Tier:** 2 (Official Repository)
- **Reference:** RESEARCH-REFERENCES.md (Phase 2.5 section)

**Example implementations:**
- Multi-database RAG agent (similar to our use case)
- Tool chaining patterns
- State management strategies

**Vercel AI SDK**
- **Source:** https://sdk.vercel.ai/docs
- **Tier:** 1 (Official Documentation)
- **Version:** 3.0+
- **Stars:** 7k+
- **Reference:** RESEARCH-REFERENCES.md (Phase 2.5 section)

**Alternative approach:** Vercel AI SDK provides similar abstractions but is more React-focused. Agents SDK is Python-native and better suited for backend orchestration.

---

## Alternatives Considered

### Alternative 1: Continue with Direct API + Manual Orchestration

**Approach:**
- Build custom orchestration layer on top of direct Claude API
- Implement conversation memory in Redis
- Create custom tool chaining logic

**Pros:**
- ✅ Full control over orchestration logic
- ✅ No dependency on beta SDK
- ✅ Can optimize for specific use cases

**Cons:**
- ❌ 2-3 weeks additional development time
- ❌ Reinventing patterns already in Agents SDK
- ❌ Higher maintenance burden
- ❌ Miss out on Anthropic optimizations

**Decision:** Rejected - Not worth reinventing the wheel when official SDK exists

---

### Alternative 2: LangChain Agents

**Approach:**
- Use LangChain's agent framework
- Implement custom tools using LangChain patterns
- Integrate with Claude via LangChain's Anthropic adapter

**Pros:**
- ✅ Mature ecosystem (1+ years production use)
- ✅ Extensive documentation and examples
- ✅ Large community support
- ✅ Multi-provider support (can switch LLM providers)

**Cons:**
- ❌ Heavy dependency (LangChain + all its transitive deps)
- ❌ More abstraction layers between us and Claude
- ❌ Not optimized specifically for Claude's capabilities
- ❌ Slower streaming performance (extra abstraction overhead)

**Research Support:**
- **Source:** LangChain Agent Documentation (https://python.langchain.com/docs/modules/agents/)
- **Tier:** 1 (Official Documentation)
- **Reference:** RESEARCH-REFERENCES.md (Phase 2.5 section)

**Decision:** Rejected - Too heavyweight for our needs, Anthropic's SDK is more optimized

---

### Alternative 3: Vercel AI SDK (Frontend-Heavy Approach)

**Approach:**
- Use Vercel AI SDK's `useChat` hook for orchestration
- Move orchestration logic to frontend React components
- Backend becomes thin API proxy

**Pros:**
- ✅ React-native patterns
- ✅ Excellent developer experience for frontend devs
- ✅ Built-in streaming and state management

**Cons:**
- ❌ Orchestration logic in frontend (security concerns)
- ❌ API keys exposed to browser (even with proxy, more attack surface)
- ❌ Cannot leverage backend-only features (direct DB access)
- ❌ Harder to implement caching and optimization

**Research Support:**
- **Source:** Vercel AI SDK Documentation (https://sdk.vercel.ai/docs)
- **Tier:** 1 (Official Documentation)
- **Version:** 3.0+
- **Reference:** RESEARCH-REFERENCES.md (Phase 2.5 section)

**Decision:** Rejected - Orchestration should remain backend-controlled for security and performance

---

### Alternative 4: Hybrid Approach (No Agents SDK, Just Better Prompts)

**Approach:**
- Use direct Claude API with enhanced system prompts
- Prompt engineering to encourage multi-turn thinking
- Implement conversation memory with careful message history management

**Pros:**
- ✅ Minimal new dependencies
- ✅ Full control over prompting strategies
- ✅ Easier to debug (no SDK abstraction)

**Cons:**
- ❌ Prompt engineering is brittle (depends on model version)
- ❌ No built-in tool chaining patterns
- ❌ Manual conversation state management
- ❌ Miss out on Anthropic's research on agent orchestration

**Decision:** Rejected - Prompt engineering alone won't achieve the multi-turn orchestration quality we need

---

## Consequences

### Positive Consequences

**1. Intelligent Multi-Turn Conversations** ⭐ PRIMARY BENEFIT
- Users can ask complex questions like "Tell me everything about ACME Corporation"
- Agent automatically orchestrates 3-6 queries (graph search, relationships, temporal patterns)
- Synthesizes coherent narrative response from fragmented results

**Example:**
```
User: "Tell me everything about ACME Corporation"

Agent Planning (transparent to user):
1. Search knowledge graph for ACME entities
2. Get relationship graph (suppliers, customers, partners)
3. Query temporal patterns (how relationships evolved)
4. Search for recent documents mentioning ACME
5. Aggregate statistics (document count, connection strength)
6. Synthesize narrative response

Response: "ACME Corporation is a manufacturing company mentioned in
12 documents over 3 months. Key supplier relationships include Bosch
(83% of orders) and emerging partnership with Siemens. Temporal analysis
shows increasing diversification of suppliers in March 2025..."
```

**2. Reduced Development Time** (2-3 weeks saved)
- Agent orchestration patterns provided by SDK
- Conversation memory management built-in
- Tool chaining logic abstracted

**3. Future-Proof Architecture**
- Built on official Anthropic patterns
- Will receive updates as Agents SDK matures
- Can leverage future Anthropic research on agent optimization

**4. Better User Experience**
- Progressive streaming of reasoning steps (users see agent thinking)
- Automatic follow-up suggestions based on results
- More natural conversation flow

**5. Easier Testing**
- SDK provides test utilities for agent behavior
- Can mock agent responses for UI testing
- Clear separation between agent logic and UI

---

### Negative Consequences

**1. Beta SDK Dependency** ⚠️ PRIMARY RISK
- Agents SDK is currently in beta (0.1.0+)
- API may change before 1.0 release
- Potential breaking changes require code updates

**Mitigation:**
- Implement abstraction layer (`src/apex_memory/agents/agent_wrapper.py`)
- Isolate SDK calls behind interface
- Keep direct API fallback for critical paths
- Monitor Anthropic changelogs closely

**2. Performance Overhead**
- Agent orchestration adds 200-500ms latency for complex queries
- Multi-tool chains take longer than single queries
- More token usage (agent planning + synthesis)

**Mitigation:**
- Use agents only for complex queries (feature flag `use_agent=true`)
- Keep direct API for simple queries (<100ms requirements)
- Implement aggressive caching for agent responses
- Monitor P95 latency, adjust orchestration strategy if needed

**3. Less Control Over Orchestration**
- Agent makes autonomous decisions about tool selection
- Harder to debug "why did agent choose this tool?"
- Less deterministic behavior

**Mitigation:**
- Enable agent reasoning transparency (show planning steps)
- Implement logging for all agent decisions
- Create debug mode to surface agent's internal reasoning
- Add override mechanism for specific query patterns

**4. Additional Dependency Complexity**
- New package to maintain (`anthropic-agents`)
- Potential conflicts with existing `anthropic` package
- More points of failure

**Mitigation:**
- Pin SDK version in requirements.txt
- Test upgrades in staging before production
- Monitor Anthropic SDK health/status
- Document rollback procedures

**5. Learning Curve**
- Team needs to learn Agents SDK patterns
- Different mental model from direct API
- More abstraction layers to understand

**Mitigation:**
- Phase 2 (Weeks 2-4) team builds expertise with direct API
- Phase 2.5 (Week 5) team explores Agents SDK on top of solid foundation
- Create internal documentation for agent patterns
- Pair programming during initial implementation

---

## Implementation Notes

### Phase 2 Foundation (Weeks 2-4) - PREREQUISITE

**Must complete before adding Agents SDK:**
- ✅ Direct API streaming working end-to-end
- ✅ Tool execution (search_knowledge_graph, get_entity_relationships, etc.)
- ✅ Message history management
- ✅ Error handling and retry logic
- ✅ 30+ tests for direct API patterns

**Why this matters:** Agents SDK is a layer on TOP of the direct API. Team must understand the underlying patterns before adding abstraction.

---

### Phase 2.5 Implementation (Week 5)

**Backend Changes:**

```python
# src/apex_memory/agents/agent_wrapper.py
from anthropic_agents import Agent, Tool
from typing import List, Dict, Any

class ApexAgent:
    """Wrapper for Anthropic Agents SDK with Apex-specific tools."""

    def __init__(self, api_key: str):
        self.agent = Agent(
            model="claude-3-5-sonnet-20241022",
            api_key=api_key,
            max_turns=5,  # Limit multi-turn orchestration
            tools=self._register_tools()
        )

    def _register_tools(self) -> List[Tool]:
        """Register Apex knowledge graph tools with agent."""
        return [
            Tool(
                name="search_knowledge_graph",
                description="Search the knowledge graph for entities and documents",
                parameters={
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results"}
                },
                execute=self._execute_search
            ),
            Tool(
                name="get_entity_relationships",
                description="Get relationships for a specific entity",
                parameters={
                    "entity_name": {"type": "string", "description": "Entity name"}
                },
                execute=self._execute_relationships
            ),
            # ... more tools
        ]

    async def orchestrate(self, query: str, context: Dict[str, Any] = None) -> str:
        """
        Orchestrate multi-turn response with tool execution.

        Returns narrative synthesis from agent.
        """
        response = await self.agent.run(
            messages=[{"role": "user", "content": query}],
            context=context or {}
        )

        return response.synthesized_response
```

**API Endpoint Changes:**

```python
# src/apex_memory/api/routes/chat.py

@router.post("/chat")
async def chat(
    request: ChatRequest,
    use_agent: bool = Query(False, description="Use agent orchestration for complex queries"),
    user: User = Depends(get_current_user)
):
    """
    Chat endpoint with optional agent orchestration.

    - use_agent=False (default): Direct API streaming (Week 2 implementation)
    - use_agent=True: Agent orchestration with multi-turn (Week 5 implementation)
    """
    if use_agent:
        # Agent orchestration path (Phase 2.5)
        agent = ApexAgent(api_key=settings.ANTHROPIC_API_KEY)
        response = await agent.orchestrate(
            query=request.messages[-1]["content"],
            context={"user_id": user.id, "conversation_id": request.conversation_id}
        )
        return {"response": response, "orchestrated": True}
    else:
        # Direct API streaming path (Phase 2)
        return StreamingResponse(
            stream_chat_response(request.messages, user),
            media_type="text/event-stream"
        )
```

**Frontend Changes:**

```typescript
// src/components/ConversationHub/ConversationHub.tsx

const ConversationHub: React.FC = () => {
  const [useAgent, setUseAgent] = useState(false); // Feature flag toggle

  const handleSendMessage = async (message: string) => {
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [...conversationHistory, { role: 'user', content: message }],
        use_agent: useAgent  // Pass feature flag
      })
    });

    if (useAgent) {
      // Agent orchestration response (JSON)
      const data = await response.json();
      setMessages([...messages, { role: 'assistant', content: data.response }]);
    } else {
      // Direct API streaming response (SSE)
      // ... existing streaming logic
    }
  };

  return (
    <div>
      {/* Feature flag toggle (Week 5) */}
      <Toggle
        label="Use Agent Orchestration"
        checked={useAgent}
        onChange={setUseAgent}
      />
      {/* ... existing UI */}
    </div>
  );
};
```

---

### Testing Strategy

**Unit Tests (Backend):**
```python
class TestApexAgent:
    """Test agent orchestration logic."""

    @pytest.mark.asyncio
    async def test_simple_query_single_tool(self):
        """Test agent uses single tool for simple queries."""
        agent = ApexAgent(api_key="test-key")

        # Mock SDK
        agent.agent.run = AsyncMock(return_value=MockAgentResponse(
            tools_used=["search_knowledge_graph"],
            synthesized_response="Found 5 documents about ACME Corp."
        ))

        response = await agent.orchestrate("What do we know about ACME Corp?")

        assert "ACME Corp" in response
        assert len(agent.agent.run.call_args[0][0]) == 1  # Single turn

    @pytest.mark.asyncio
    async def test_complex_query_multi_tool(self):
        """Test agent orchestrates multiple tools for complex queries."""
        agent = ApexAgent(api_key="test-key")

        # Mock SDK with multi-turn orchestration
        agent.agent.run = AsyncMock(return_value=MockAgentResponse(
            tools_used=[
                "search_knowledge_graph",
                "get_entity_relationships",
                "get_temporal_patterns"
            ],
            synthesized_response="ACME Corporation is a manufacturing company..."
        ))

        response = await agent.orchestrate("Tell me everything about ACME Corporation")

        assert len(agent.agent.run.call_args[1]["tools_used"]) >= 3  # Multi-tool
        assert "manufacturing" in response.lower()
```

**Integration Tests:**
```python
class TestAgentOrchestrationE2E:
    """Test end-to-end agent orchestration."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_orchestrates_real_query(self):
        """Test agent with real Anthropic API (uses test credits)."""
        agent = ApexAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = await agent.orchestrate(
            "What entities are connected to ACME Corporation?"
        )

        # Should return narrative synthesis
        assert len(response) > 100  # Substantial response
        assert "ACME" in response

        # Should have called multiple tools (check logs)
        # Note: Exact tool selection is non-deterministic
```

**Feature Flag Tests:**
```python
class TestChatEndpointAgentToggle:
    """Test chat endpoint with use_agent toggle."""

    @pytest.mark.asyncio
    async def test_use_agent_false_uses_direct_api(self, client, auth_headers):
        """Test use_agent=False uses direct API streaming."""
        response = await client.post(
            "/api/v1/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "use_agent": False
            },
            headers=auth_headers
        )

        # Should return SSE stream
        assert response.headers["content-type"] == "text/event-stream"

    @pytest.mark.asyncio
    async def test_use_agent_true_uses_orchestration(self, client, auth_headers):
        """Test use_agent=True uses agent orchestration."""
        response = await client.post(
            "/api/v1/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "use_agent": True
            },
            headers=auth_headers
        )

        # Should return JSON
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "orchestrated" in data
        assert data["orchestrated"] is True
```

---

### Rollback Plan

**If Agents SDK proves problematic:**

1. **Immediate rollback** (< 1 hour)
   - Set `USE_AGENTS_SDK=False` environment variable
   - All traffic routes to direct API (Phase 2 implementation)
   - No code changes needed (feature flag design)

2. **Remove SDK dependency** (< 1 day)
   - Remove `anthropic-agents` from requirements.txt
   - Delete `src/apex_memory/agents/` directory
   - Remove `use_agent` query parameter from API
   - Revert to Phase 2 baseline

**Rollback triggers:**
- ❌ P95 latency >2 seconds (vs. <1s baseline)
- ❌ Error rate >5% for agent-orchestrated queries
- ❌ Breaking SDK changes without migration path
- ❌ Significant token cost increase (>50% vs. direct API)

---

### Success Metrics

**Performance targets:**
- ✅ P50 latency <500ms for simple queries (with agent)
- ✅ P95 latency <2s for complex multi-tool queries
- ✅ Error rate <1% for agent-orchestrated queries
- ✅ Token usage <2x direct API (agent planning overhead)

**User experience targets:**
- ✅ 80% user satisfaction with narrative synthesis quality
- ✅ 50% of complex queries use agent orchestration (opt-in adoption)
- ✅ 30% reduction in follow-up queries (agent anticipates needs)

**Quality targets:**
- ✅ 90%+ test coverage for agent code paths
- ✅ Zero production incidents related to agent orchestration
- ✅ Complete documentation for agent patterns

---

### Future Enhancements (Post-Phase 2.5)

**Once Agents SDK is stable:**

1. **Make agents default** (currently opt-in with `use_agent=True`)
   - Evaluate performance after 2-4 weeks
   - If metrics meet targets, flip default to `use_agent=True`
   - Keep direct API as fallback for simple queries

2. **Custom agent personalities**
   - "Analyst" agent (focus on data analysis and trends)
   - "Explorer" agent (focus on relationship discovery)
   - "Summarizer" agent (focus on document summarization)

3. **Agent learning from user feedback**
   - Track which agent responses get positive/negative feedback
   - Fine-tune orchestration strategies based on patterns
   - A/B test different agent prompting strategies

4. **Multi-agent collaboration**
   - Specialized agents for different knowledge domains
   - Agent handoff for complex multi-domain queries
   - Consensus building across agent responses

---

## References

**Primary Research:**
- See `RESEARCH-REFERENCES.md` - Phase 2.5 section
- See `PLANNING.md` - Week 5 (Phase 2.5) section
- See `IMPLEMENTATION.md` - Week 5 implementation steps

**Related ADRs:**
- ADR-005: Artifacts Sidebar Pattern (agent reasoning transparency)
- ADR-006: Shadcn/ui Component Library (UI for agent status)

**External Documentation:**
- Anthropic Agents SDK: https://docs.anthropic.com/agents/
- Anthropic Claude API: https://docs.anthropic.com/claude/reference/
- Vercel AI SDK (comparison): https://sdk.vercel.ai/docs

---

**Last Updated:** 2025-10-21
**Status:** Accepted for Phase 2.5 implementation
**Review Date:** 2025-11-21 (after 1 month of usage)
