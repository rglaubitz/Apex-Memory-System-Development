# Claude Tool Use API - Official Documentation

**Source:** https://docs.claude.com/en/docs/build-with-claude/tool-use
**Date Accessed:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Anthropic Documentation)

**Related Documentation:**
- For streaming responses → see `streaming-api.md`
- For Apex-specific tools → see `apex-tool-definitions.md`
- For multi-step workflows → see `tool-orchestration.md`

---

## Overview

Claude can interact with external systems through a standardized tool calling pattern. Tools are defined in API requests, Claude decides when to use them, and your application executes the actual functions.

**Key Insight:** There is no separate "Agents SDK" - agentic workflows are built by combining tool use + streaming + multi-step orchestration in your application layer.

**Two Types of Tools:**
- **Client Tools** - Executed by your application (database queries, file operations, API calls)
- **Server Tools** - Executed by Anthropic's servers (web search, web fetch) - automatic, no client implementation needed

---

## Defining Tools

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

---

## Tool Calling Flow (4 Steps)

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

---

## Best Practices

### 1. Chain of Thought

Prompt Sonnet/Haiku to think before calling tools:

```
"Think step-by-step about what information you need before calling tools."
```

**Impact:** Improves parameter assessment, reduces unnecessary tool calls.

### 2. Parallel vs. Sequential Tool Calls

- **Parallel:** Independent operations (e.g., fetch weather for multiple cities)
- **Sequential:** Downstream tools depend on upstream results (e.g., search → extract URLs → fetch content)

Claude automatically determines the appropriate pattern.

### 3. Parameter Clarity

Provide sufficient context so Claude infers required parameters accurately:

```
❌ Bad:  "Get the weather"
✅ Good: "Get the current weather for San Francisco in Fahrenheit"
```

**Model Differences:**
- **Opus** - More likely to ask clarifying questions for ambiguous requests
- **Sonnet** - Better at inferring parameters from context

---

## Handling Tool Results

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

---

## JSON Mode (Structured Output)

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

---

## Limitations

- **No infinite loops** - Tool calling has built-in safeguards
- **Token limits** - Tool definitions + results count toward context window
- **Ambiguity handling** - Sonnet may make assumptions; Opus asks clarifying questions
- **Pricing overhead** - 313-346 token system prompt per request

---

## Pricing

Tool use adds tokens from:
- Tool definitions (in request)
- `tool_use` blocks (in response)
- `tool_result` blocks (in subsequent request)
- System prompt overhead: **313-346 tokens** (depending on model and tool_choice setting)

---

## References

**Official Documentation:**
- Tool Use Guide: https://docs.claude.com/en/docs/build-with-claude/tool-use
- Messages API: https://docs.claude.com/en/api/messages
- Prompt Engineering for Tool Use: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering

**SDKs:**
- Python SDK: https://github.com/anthropics/anthropic-sdk-python
- TypeScript SDK: https://github.com/anthropics/anthropic-sdk-typescript

**Related Apex Documentation:**
- Streaming API patterns → `streaming-api.md`
- Apex tool definitions → `apex-tool-definitions.md`
- Multi-step orchestration → `tool-orchestration.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Anthropic Documentation)
