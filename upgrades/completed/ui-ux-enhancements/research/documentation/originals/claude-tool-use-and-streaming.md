# Claude Tool Use and Streaming - Official Documentation Summary

**Source:** https://docs.claude.com/en/docs/build-with-claude/tool-use
**Source:** https://docs.claude.com/en/api/messages-streaming
**Date Accessed:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Anthropic Documentation)

---

## Executive Summary

Claude's agentic capabilities are built on **two core patterns**:

1. **Tool Use** - Claude can assess tasks, request tool execution, and integrate results into responses
2. **Streaming API** - Server-Sent Events (SSE) deliver incremental responses for real-time UI updates

**Key Insight:** There is no separate "Agents SDK" - agentic workflows are built by combining tool use + streaming + multi-step orchestration in your application layer.

---

## Part 1: Tool Use

### Overview

Claude can interact with external systems through a standardized tool calling pattern. Tools are defined in API requests, Claude decides when to use them, and your application executes the actual functions.

**Two Types of Tools:**
- **Client Tools** - Executed by your application (database queries, file operations, API calls)
- **Server Tools** - Executed by Anthropic's servers (web search, web fetch) - automatic, no client implementation needed

### Defining Tools

Tools are defined in the Messages API with three components:

```typescript
{
  name: string;           // Identifier (e.g., "get_weather")
  description: string;    // What the tool does
  input_schema: {         // JSON schema for parameters
    type: "object",
    properties: {
      location: { type: "string", description: "City name" },
      units: { type: "string", enum: ["celsius", "fahrenheit"] }
    },
    required: ["location"]
  }
}
```

**Versioned Types:** Server tools use versioned types (e.g., `web_search_20250305`) ensuring model compatibility across updates.

### Tool Calling Flow (4 Steps)

```
┌─────────────────────────────────────────────────────────────┐
│  1. ASSESSMENT                                              │
│  Claude evaluates if tools can help with the query         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2. REQUEST                                                 │
│  Claude constructs tool_use block                          │
│  stop_reason: "tool_use"                                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3. EXECUTION (Your Application)                            │
│  Extract tool name + input, execute function locally       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  4. INTEGRATION                                             │
│  Return results via tool_result block                      │
│  Claude formulates final response                          │
└─────────────────────────────────────────────────────────────┘
```

### Best Practices

#### 1. Chain of Thought

Prompt Sonnet/Haiku to think before calling tools:

```
"Think step-by-step about what information you need before calling tools."
```

**Impact:** Improves parameter assessment, reduces unnecessary tool calls.

#### 2. Parallel vs. Sequential Tool Calls

- **Parallel:** Independent operations (e.g., fetch weather for multiple cities)
- **Sequential:** Downstream tools depend on upstream results (e.g., search → extract URLs → fetch content)

Claude automatically determines the appropriate pattern.

#### 3. Parameter Clarity

Provide sufficient context so Claude infers required parameters accurately:

```
❌ Bad:  "Get the weather"
✅ Good: "Get the current weather for San Francisco in Fahrenheit"
```

**Model Differences:**
- **Opus** - More likely to ask clarifying questions for ambiguous requests
- **Sonnet** - Better at inferring parameters from context

### Multi-Tool Orchestration

**Provide multiple tools in a single request.** Claude selects appropriate tools and may:

- **Call sequentially** - Using one result as input to another
- **Call in parallel** - Independent operations in one response

**Example Flow:**
```typescript
// Request with 3 tools
tools: [search_documents, extract_entities, query_graph]

// Claude's response might include:
[
  tool_use: search_documents → Returns doc IDs
  tool_use: extract_entities  → Parallel with search
]

// Your response includes results:
[
  tool_result: {tool_use_id: "1", content: "..."},
  tool_result: {tool_use_id: "2", content: "..."}
]

// Claude's final response:
tool_use: query_graph → Uses entity IDs from step 2
```

### Handling Tool Results

Return tool results in `tool_result` content blocks:

```typescript
{
  role: "user",
  content: [
    {
      type: "tool_result",
      tool_use_id: "toolu_abc123",  // Must match tool_use block
      content: "Result data here"    // String or object
    }
  ]
}
```

**Critical:** Match `tool_use_id` to maintain parallel execution. Claude analyzes results to refine responses.

### JSON Mode (Structured Output)

Use a single tool with `tool_choice` set to force structured output **without execution**:

```typescript
{
  tools: [{
    name: "extract_data",
    description: "Extract structured data",
    input_schema: { /* your schema */ }
  }],
  tool_choice: { type: "tool", name: "extract_data" }
}
```

Claude will **always** return a `tool_use` block matching your schema. You control whether to actually execute.

### Pricing

Tool use adds tokens from:
- Tool definitions (in request)
- `tool_use` blocks (in response)
- `tool_result` blocks (in subsequent request)
- System prompt overhead: **313-346 tokens** (depending on model and tool_choice setting)

---

## Part 2: Streaming API

### Overview

Claude implements **Server-Sent Events (SSE)** for incremental response delivery. Set `"stream": true` in API requests.

**SDKs Available:**
- Python (sync + async patterns)
- TypeScript (async patterns)
- Direct HTTP/SSE parsing

### Event Types

The streaming response follows a consistent sequence:

| Event | Purpose | When Emitted |
|-------|---------|--------------|
| `message_start` | Initiates stream | Once at start |
| `content_block_start` | New content block begins | Per text/tool_use/thinking block |
| `content_block_delta` | Incremental updates | Multiple times per block |
| `content_block_stop` | Content block complete | End of each block |
| `message_delta` | Top-level changes + token counts | Periodically |
| `message_stop` | Stream finalized | Once at end |
| `ping` | Keepalive | Periodic (prevent timeout) |
| `error` | API issues | On errors (e.g., "Overloaded") |

### Event Flow Example

```
message_start → { id, type, role, content: [], usage }
  ↓
content_block_start → { index: 0, type: "text" }
  ↓
content_block_delta → { index: 0, delta: { type: "text_delta", text: "Hello" } }
content_block_delta → { index: 0, delta: { type: "text_delta", text: " world" } }
  ↓
content_block_stop → { index: 0 }
  ↓
message_delta → { delta: { stop_reason: "end_turn" }, usage: { output_tokens: 15 } }
  ↓
message_stop
```

### Implementing Streaming in Frontend

#### Basic Python Example (SDK)

```python
with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-sonnet-4-5",
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

#### Direct HTTP/SSE Integration

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "stream": true,
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 256
  }'
```

**Response Format:**
```
event: message_start
data: {"type":"message_start","message":{"id":"msg_123",...}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello"}}

...

event: message_stop
data: {"type":"message_stop"}
```

### Handling Partial Responses

Different content types require different handling:

#### Text Blocks
```typescript
let accumulatedText = "";

stream.on('content_block_delta', (event) => {
  if (event.delta.type === 'text_delta') {
    accumulatedText += event.delta.text;
    // Update UI with accumulated text
  }
});
```

#### Tool Use Blocks

**Important:** Tool use emits "one complete key and value property at a time" - potentially creating delays between events.

```typescript
let toolInputJson = "";

stream.on('content_block_delta', (event) => {
  if (event.delta.type === 'input_json_delta') {
    toolInputJson += event.delta.partial_json;
  }
});

stream.on('content_block_stop', () => {
  // Only parse when complete!
  const toolInput = JSON.parse(toolInputJson);
});
```

⚠️ **Do NOT parse partial JSON** - wait for `content_block_stop`.

#### Thinking Blocks (Extended Thinking)

```typescript
let thinkingText = "";

stream.on('content_block_delta', (event) => {
  if (event.delta.type === 'thinking_delta') {
    thinkingText += event.delta.thinking;
    // Optionally show "Claude is thinking..." UI
  }
});

// Verify integrity with signature_delta before block completion
```

### Error Handling During Streams

**Recovery Pattern:**

1. **Capture successful content** before interruption
2. **Construct continuation request** including partial assistant response
3. **Resume from most recent recoverable point**

```typescript
// Partial response before error:
{
  role: "assistant",
  content: [
    { type: "text", text: "Here's what I found so far..." }
  ]
}

// Continuation request:
{
  messages: [
    { role: "user", content: "Original query" },
    { role: "assistant", content: [/* partial response */] },
    { role: "user", content: "Please continue" }
  ]
}
```

⚠️ **Limitation:** Partial `tool_use` and `thinking` blocks **cannot be resumed** - restart from the most recent complete text block.

### Performance Best Practices

1. **Use SDKs** - More reliable than raw HTTP parsing
2. **Enable flush** - `flush=True` in Python displays partial text immediately
3. **Handle ping events** - Gracefully ignore keepalive signals
4. **Accumulate before parsing** - Improves JSON delta efficiency
5. **Monitor token counts** - Track in `message_delta` events for budget management

```python
# Good: Immediate display
for text in stream.text_stream:
    print(text, end="", flush=True)  # ← flush=True

# Bad: Buffered output
for text in stream.text_stream:
    print(text, end="")  # ← No immediate display
```

### Extended Thinking with Streaming

```bash
curl https://api.anthropic.com/v1/messages \
  -d '{
    "model": "claude-sonnet-4-5",
    "stream": true,
    "thinking": {
      "type": "enabled",
      "budget_tokens": 16000
    },
    "messages": [{"role": "user", "content": "What is 27 * 453?"}],
    "max_tokens": 20000
  }'
```

**Response includes:**
- `thinking_delta` events (Claude's reasoning)
- `signature_delta` events (integrity verification)
- Final `text_delta` events (answer)

---

## Integration Patterns for Apex Memory System

### Pattern 1: Agentic Conversation Flow

```
User Query
  ↓
Claude Assessment (with streaming)
  ↓
Tool Calls (parallel/sequential):
  - search_apex_documents
  - extract_apex_entities
  - query_apex_graph
  - get_apex_temporal_data
  ↓
Tool Results Returned
  ↓
Claude Integration (streaming response)
  ↓
User sees progressive answer with citations
```

### Pattern 2: Multi-Step Reasoning UI

```typescript
// Show different stages in UI:

1. "Analyzing query..."        → content_block_start (thinking)
2. "Searching documents..."     → tool_use: search_apex_documents
3. "Extracting entities..."     → tool_use: extract_apex_entities
4. "Querying knowledge graph..."→ tool_use: query_apex_graph
5. "Synthesizing answer..."     → content_block_start (text)
6. Progressive text rendering   → content_block_delta (text_delta)
```

### Pattern 3: Artifacts Integration

```typescript
// Claude can generate content that appears in Artifacts sidebar:

Tool: create_apex_artifact
  Parameters:
    - type: "code" | "diagram" | "document" | "query"
    - content: string
    - title: string

// Example: User asks "Create a Cypher query to find all CAT equipment"
// Claude calls: create_apex_artifact({ type: "query", content: "MATCH ..." })
// UI shows: Artifacts sidebar with executable Cypher query
```

---

## Limitations & Considerations

### Tool Use Limitations

- **No infinite loops** - Tool calling has built-in safeguards
- **Token limits** - Tool definitions + results count toward context window
- **Ambiguity handling** - Sonnet may make assumptions; Opus asks clarifying questions
- **Pricing overhead** - 313-346 token system prompt per request

### Streaming Limitations

- **No partial tool_use resumption** - Must restart from last complete text block
- **JSON parsing delays** - Tool use emits "one complete key and value at a time"
- **Network interruptions** - Requires continuation pattern implementation
- **Thinking blocks** - Optional; adds latency but improves reasoning

---

## Code Examples for Apex Integration

### 1. Define Apex Tools

```typescript
const apexTools = [
  {
    name: "search_apex_documents",
    description: "Search the Apex knowledge base for documents matching a query",
    input_schema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Natural language search query" },
        filters: {
          type: "object",
          properties: {
            file_type: { type: "string", enum: ["pdf", "docx", "pptx"] },
            date_range: { type: "object" }
          }
        }
      },
      required: ["query"]
    }
  },
  {
    name: "query_apex_graph",
    description: "Execute a Cypher query on the Neo4j knowledge graph",
    input_schema: {
      type: "object",
      properties: {
        cypher: { type: "string", description: "Cypher query to execute" },
        parameters: { type: "object", description: "Query parameters" }
      },
      required: ["cypher"]
    }
  },
  {
    name: "get_apex_temporal_data",
    description: "Retrieve temporal patterns and trends for an entity",
    input_schema: {
      type: "object",
      properties: {
        entity_name: { type: "string" },
        time_range: { type: "string", description: "e.g., 'last 30 days'" }
      },
      required: ["entity_name"]
    }
  }
];
```

### 2. Stream with Tool Use

```typescript
async function streamApexConversation(userQuery: string) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': process.env.ANTHROPIC_API_KEY,
      'content-type': 'application/json',
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-5',
      stream: true,
      max_tokens: 4096,
      tools: apexTools,
      messages: [
        { role: 'user', content: userQuery }
      ]
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        handleStreamEvent(data);
      }
    }
  }
}

function handleStreamEvent(event) {
  switch (event.type) {
    case 'content_block_start':
      if (event.content_block.type === 'tool_use') {
        // Show "Calling tool: {name}" in UI
        showToolCallIndicator(event.content_block.name);
      }
      break;

    case 'content_block_delta':
      if (event.delta.type === 'text_delta') {
        // Append text to UI
        appendText(event.delta.text);
      }
      break;

    case 'content_block_stop':
      // Execute tool if needed
      if (currentBlock.type === 'tool_use') {
        executeApexTool(currentBlock);
      }
      break;
  }
}
```

### 3. Execute Apex Tools

```typescript
async function executeApexTool(toolUse) {
  const { name, input } = toolUse;

  switch (name) {
    case 'search_apex_documents':
      return await fetch('/api/v1/query', {
        method: 'POST',
        body: JSON.stringify({
          query: input.query,
          filters: input.filters
        })
      });

    case 'query_apex_graph':
      return await fetch('/api/v1/graph/query', {
        method: 'POST',
        body: JSON.stringify({
          cypher: input.cypher,
          parameters: input.parameters
        })
      });

    case 'get_apex_temporal_data':
      return await fetch('/api/v1/temporal/entity', {
        method: 'POST',
        body: JSON.stringify({
          entity_name: input.entity_name,
          time_range: input.time_range
        })
      });
  }
}
```

---

## References

**Official Documentation:**
- Tool Use Guide: https://docs.claude.com/en/docs/build-with-claude/tool-use
- Streaming API: https://docs.claude.com/en/api/messages-streaming
- Messages API: https://docs.claude.com/en/api/messages

**SDKs:**
- Python SDK: https://github.com/anthropics/anthropic-sdk-python
- TypeScript SDK: https://github.com/anthropics/anthropic-sdk-typescript

**Best Practices:**
- Prompt Engineering for Tool Use: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering
- Rate Limits: https://docs.claude.com/en/api/rate-limits

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Anthropic Documentation)
