# Tool Orchestration Patterns - Multi-Step Workflows

**Purpose:** Patterns for coordinating multiple tool calls in agentic workflows
**Date Created:** 2025-10-21
**Documentation Tier:** Internal (Apex Memory System)

**Related Documentation:**
- For tool use basics → see `tool-use-api.md`
- For streaming → see `streaming-api.md`
- For Apex tools → see `apex-tool-definitions.md`

---

## Overview

**Tool orchestration** is the practice of coordinating multiple tool calls to complete complex tasks. Claude automatically determines:

- **Parallel execution** - Independent operations run simultaneously
- **Sequential execution** - Downstream tools use upstream results
- **Adaptive workflows** - Adjusting based on intermediate results

**Key Insight:** You don't orchestrate - Claude does. Your job is to provide tools and handle results.

---

## Orchestration Patterns

### Pattern 1: Parallel Tool Calls

**When:** Independent operations that don't depend on each other

**Example:** Fetching weather for multiple cities

```typescript
// User: "What's the weather in SF, NYC, and London?"

// Claude's response (single turn):
[
  { type: "tool_use", id: "1", name: "get_weather", input: { city: "San Francisco" } },
  { type: "tool_use", id: "2", name: "get_weather", input: { city: "New York" } },
  { type: "tool_use", id: "3", name: "get_weather", input: { city: "London" } }
]

// Your response (all at once):
[
  { type: "tool_result", tool_use_id: "1", content: "72°F, Sunny" },
  { type: "tool_result", tool_use_id: "2", content: "68°F, Cloudy" },
  { type: "tool_result", tool_use_id: "3", content: "15°C, Rain" }
]
```

**Benefits:**
- Faster execution (no sequential waiting)
- Single API round-trip
- Reduced latency

---

### Pattern 2: Sequential Tool Calls

**When:** Downstream tools need upstream results

**Example:** Search → Extract → Query pattern

```typescript
// User: "Find information about Tesla's Gigafactory Berlin and analyze its supply chain"

// Turn 1: Search for documents
Claude: [
  { type: "tool_use", id: "1", name: "search_apex_documents",
    input: { query: "Tesla Gigafactory Berlin" } }
]

You: [
  { type: "tool_result", tool_use_id: "1", content: {
    results: [{ document_id: "doc_456", ... }]
  }}
]

// Turn 2: Extract entities from found documents
Claude: [
  { type: "tool_use", id: "2", name: "extract_entities",
    input: { document_id: "doc_456" } }
]

You: [
  { type: "tool_result", tool_use_id: "2", content: {
    entities: ["Bosch", "CATL", "LG Chem"]
  }}
]

// Turn 3: Query relationships
Claude: [
  { type: "tool_use", id: "3", name: "query_apex_graph",
    input: {
      cypher: "MATCH (supplier)-[:SUPPLIES]->(facility {name: $name}) RETURN supplier",
      parameters: { name: "Gigafactory Berlin" }
    }
  }
]
```

**Benefits:**
- Accurate downstream queries (based on actual results)
- Adaptive workflows (Claude adjusts based on findings)
- Efficient token usage (only relevant queries)

---

### Pattern 3: Hybrid Orchestration

**When:** Mix of parallel and sequential operations

**Example:** Multi-source research

```typescript
// User: "Compare ACME Corporation's performance across 2023 and 2024"

// Turn 1: Parallel search across time periods
Claude: [
  { type: "tool_use", id: "1", name: "search_apex_documents",
    input: { query: "ACME Corporation", filters: { date_range: { start: "2023-01-01", end: "2023-12-31" } } } },
  { type: "tool_use", id: "2", name: "search_apex_documents",
    input: { query: "ACME Corporation", filters: { date_range: { start: "2024-01-01", end: "2024-12-31" } } } }
]

// Turn 2: Sequential temporal analysis
Claude: [
  { type: "tool_use", id: "3", name: "get_apex_temporal_data",
    input: { entity_name: "ACME Corporation", time_range: "2023-2024" } }
]

// Turn 3: Parallel detail queries based on temporal insights
Claude: [
  { type: "tool_use", id: "4", name: "query_apex_graph", input: { /* Q1 2023 suppliers */ } },
  { type: "tool_use", id: "5", name: "query_apex_graph", input: { /* Q4 2024 suppliers */ } }
]
```

---

## Agentic Conversation Flow

### Complete Flow Diagram

```
User Query: "Tell me everything about ACME Corporation"
  ↓
┌─────────────────────────────────────────────────────┐
│ TURN 1: Claude Assessment (with streaming)         │
│ - Determines needed information                     │
│ - Plans tool calls                                  │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ TURN 1: Parallel Tool Calls                        │
│ - search_apex_documents (find docs)                │
│ - query_apex_graph (find relationships)            │
│ - get_apex_entity_timeline (get history)           │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ Your Application: Execute Tools                     │
│ - Call Apex APIs                                    │
│ - Return results to Claude                          │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ TURN 2: Claude Analysis                            │
│ - Reviews initial results                           │
│ - Identifies gaps (e.g., no supplier data)         │
│ - Requests additional tools                         │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ TURN 2: Sequential Tool Call                       │
│ - get_apex_temporal_data (supplier changes)        │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│ TURN 3: Claude Integration (streaming response)    │
│ - Synthesizes all data                              │
│ - Provides comprehensive answer                     │
│ - Cites sources                                     │
└─────────────────────────────────────────────────────┘
  ↓
User sees progressive answer with citations
```

---

## UI Visualization Patterns

### Multi-Step Reasoning UI

Show Claude's thinking process in the interface:

```typescript
// Stage indicators shown progressively during orchestration:

interface WorkflowStage {
  stage: string;
  status: 'pending' | 'in_progress' | 'complete';
  tool?: string;
  duration?: number;
}

// Example stages:
const stages: WorkflowStage[] = [
  { stage: "Analyzing query...", status: "complete", duration: 250 },
  { stage: "Searching documents...", status: "complete", tool: "search_apex_documents", duration: 1200 },
  { stage: "Extracting entities...", status: "complete", tool: "extract_entities", duration: 800 },
  { stage: "Querying knowledge graph...", status: "in_progress", tool: "query_apex_graph" },
  { stage: "Synthesizing answer...", status: "pending" }
];
```

**UI Component:**
```tsx
export function WorkflowProgress({ stages }: { stages: WorkflowStage[] }) {
  return (
    <div className="space-y-2">
      {stages.map((stage, i) => (
        <div key={i} className="flex items-center gap-3">
          <StatusIcon status={stage.status} />
          <span className="text-sm">{stage.stage}</span>
          {stage.tool && (
            <Badge variant="secondary">{stage.tool}</Badge>
          )}
          {stage.duration && (
            <span className="text-xs text-muted-foreground">
              {stage.duration}ms
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
```

---

## Artifacts Integration Pattern

Claude can generate content for the Artifacts sidebar as part of orchestration:

### Artifact Tool Definition

```typescript
{
  name: "create_apex_artifact",
  description: "Create an artifact to display in the sidebar (code, diagram, document, or query)",
  input_schema: {
    type: "object",
    properties: {
      type: {
        type: "string",
        enum: ["code", "diagram", "document", "query"],
        description: "Type of artifact to create"
      },
      title: {
        type: "string",
        description: "Display title for the artifact"
      },
      content: {
        type: "string",
        description: "Artifact content (code, Mermaid diagram, markdown, or Cypher query)"
      },
      language: {
        type: "string",
        description: "Programming language (for code artifacts)"
      }
    },
    required: ["type", "title", "content"]
  }
}
```

### Example Flow

**User:** "Create a Cypher query to find all CAT equipment suppliers"

```typescript
// Turn 1: Claude creates artifact
Claude: [
  { type: "tool_use", id: "1", name: "create_apex_artifact",
    input: {
      type: "query",
      title: "CAT Equipment Suppliers Query",
      content: "MATCH (supplier)-[:SUPPLIES]->(equipment:Equipment {manufacturer: 'CAT'}) RETURN supplier.name, COUNT(equipment) as equipment_count ORDER BY equipment_count DESC"
    }
  }
]

// Your application:
// 1. Store artifact in state
// 2. Show in Artifacts sidebar
// 3. Provide execution button
// 4. Return confirmation to Claude

You: [
  { type: "tool_result", tool_use_id: "1",
    content: { artifact_id: "art_789", status: "created" }
  }
]

// Turn 2: Claude explains the query
Claude: "I've created a Cypher query in the sidebar that finds all suppliers... [streaming explanation]"
```

---

## Best Practices

### 1. Design Self-Contained Tools

Each tool should:
- Have a clear, single purpose
- Return complete, structured data
- Include error states in responses
- Provide metadata (timing, cache status, etc.)

**Good:**
```typescript
{
  name: "search_documents",
  returns: {
    results: Array<Document>,
    total: number,
    query_time_ms: number,
    cached: boolean
  }
}
```

**Bad:**
```typescript
{
  name: "do_everything",  // ❌ Too broad
  returns: "whatever"     // ❌ Unstructured
}
```

### 2. Provide Multiple Tools

Give Claude options so it can orchestrate effectively:

```typescript
// ✅ Good: Granular, composable tools
const tools = [
  "search_documents",
  "get_entity_details",
  "query_relationships",
  "analyze_temporal_patterns",
  "create_artifact"
];

// ❌ Bad: Single monolithic tool
const tools = ["do_research"];
```

### 3. Stream Progress Updates

Show tool calls in real-time:

```typescript
stream.on('content_block_start', (event) => {
  if (event.content_block.type === 'tool_use') {
    showToolIndicator({
      name: event.content_block.name,
      status: 'executing'
    });
  }
});

stream.on('content_block_stop', () => {
  if (currentBlock.type === 'tool_use') {
    updateToolIndicator({
      name: currentBlock.name,
      status: 'complete',
      duration: Date.now() - startTime
    });
  }
});
```

### 4. Handle Orchestration Failures

```typescript
async function executeWithFallback(toolUse: ToolUse) {
  try {
    return await executeApexTool(toolUse);
  } catch (error) {
    // Return structured error, not exception
    return {
      error: true,
      message: error.message,
      fallback_suggestion: "Try searching documents instead"
    };
  }
}
```

---

## Performance Considerations

### Token Efficiency

**Problem:** Each tool call adds tokens (definition + input + result)

**Solutions:**
1. Use concise tool descriptions
2. Return only necessary data
3. Cache expensive operations
4. Summarize large results

```typescript
// ❌ Bad: Returns full documents
{
  results: [
    { full_content: "50,000 word document..." }
  ]
}

// ✅ Good: Returns excerpts + IDs
{
  results: [
    {
      document_id: "doc_123",
      excerpt: "Most relevant 200 words...",
      score: 0.92
    }
  ]
}
```

### Latency Optimization

**Parallel execution** is automatic, but you can optimize:

```typescript
// Execute tools in parallel on your end
const results = await Promise.all([
  executeSearchApexDocuments(input1),
  executeQueryApexGraph(input2),
  executeGetApexTemporalData(input3)
]);
```

---

## References

**Official Patterns:**
- Tool Use Guide: https://docs.claude.com/en/docs/build-with-claude/tool-use
- Multi-step reasoning: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering

**Related Documentation:**
- Tool use basics → `tool-use-api.md`
- Streaming responses → `streaming-api.md`
- Apex tool definitions → `apex-tool-definitions.md`

**Apex Implementation:**
- ConversationHub.tsx: Main orchestration UI
- ToolUseIndicator.tsx: Visual feedback for tool calls
- WorkflowProgress.tsx: Multi-step progress visualization

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Type:** Internal Patterns Guide
