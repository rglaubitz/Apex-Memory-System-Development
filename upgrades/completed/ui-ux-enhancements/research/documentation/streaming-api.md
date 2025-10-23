# Claude Streaming API - Official Documentation

**Source:** https://docs.claude.com/en/api/messages-streaming
**Date Accessed:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Anthropic Documentation)

**Related Documentation:**
- For tool use patterns → see `tool-use-api.md`
- For Vercel AI SDK streaming → see `vercel-ai-sdk-overview.md`
- For UI streaming patterns → see `streaming-ui-patterns.md`

---

## Overview

Claude implements **Server-Sent Events (SSE)** for incremental response delivery. Set `"stream": true` in API requests.

**SDKs Available:**
- Python (sync + async patterns)
- TypeScript (async patterns)
- Direct HTTP/SSE parsing

---

## Event Types

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

---

## Event Flow Example

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

---

## Implementation Examples

### Basic Python Example (SDK)

```python
with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-sonnet-4-5",
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Direct HTTP/SSE Integration

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

---

## Handling Partial Responses

Different content types require different handling:

### Text Blocks

```typescript
let accumulatedText = "";

stream.on('content_block_delta', (event) => {
  if (event.delta.type === 'text_delta') {
    accumulatedText += event.delta.text;
    // Update UI with accumulated text
  }
});
```

### Tool Use Blocks

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

### Thinking Blocks (Extended Thinking)

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

---

## Error Handling During Streams

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

---

## Performance Best Practices

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

---

## Extended Thinking with Streaming

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

## Limitations

- **No partial tool_use resumption** - Must restart from last complete text block
- **JSON parsing delays** - Tool use emits "one complete key and value at a time"
- **Network interruptions** - Requires continuation pattern implementation
- **Thinking blocks** - Optional; adds latency but improves reasoning

---

## References

**Official Documentation:**
- Streaming API: https://docs.claude.com/en/api/messages-streaming
- Messages API: https://docs.claude.com/en/api/messages
- Rate Limits: https://docs.claude.com/en/api/rate-limits

**SDKs:**
- Python SDK: https://github.com/anthropics/anthropic-sdk-python
- TypeScript SDK: https://github.com/anthropics/anthropic-sdk-typescript

**Related Apex Documentation:**
- Tool use patterns → `tool-use-api.md`
- Vercel AI SDK streaming → `vercel-ai-sdk-overview.md`
- UI streaming patterns → `streaming-ui-patterns.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Anthropic Documentation)
