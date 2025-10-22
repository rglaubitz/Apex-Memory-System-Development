# Apex Tool Definitions - Implementation Guide

**Purpose:** Apex-specific Claude tool implementations
**Date Created:** 2025-10-21
**Documentation Tier:** Internal (Apex Memory System)

**Related Documentation:**
- For tool use API basics → see `tool-use-api.md`
- For streaming responses → see `streaming-api.md`
- For orchestration patterns → see `tool-orchestration.md`

---

## Overview

This document provides production-ready tool definitions for integrating Claude with the Apex Memory System's multi-database architecture.

**Apex Capabilities via Tools:**
- Document search (Qdrant + PostgreSQL hybrid)
- Knowledge graph queries (Neo4j)
- Temporal pattern analysis (Graphiti)
- Entity timeline tracking
- Metadata filtering

---

## Tool Definitions

### 1. search_apex_documents

```typescript
{
  name: "search_apex_documents",
  description: "Search the Apex knowledge base for documents matching a query. Returns document IDs, titles, excerpts, and relevance scores.",
  input_schema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Natural language search query"
      },
      filters: {
        type: "object",
        properties: {
          file_type: {
            type: "string",
            enum: ["pdf", "docx", "pptx", "html", "md"],
            description: "Filter by document format"
          },
          date_range: {
            type: "object",
            properties: {
              start: { type: "string", format: "date" },
              end: { type: "string", format: "date" }
            }
          },
          tags: {
            type: "array",
            items: { type: "string" },
            description: "Filter by document tags"
          }
        }
      },
      limit: {
        type: "integer",
        default: 10,
        minimum: 1,
        maximum: 50,
        description: "Maximum number of results to return"
      }
    },
    required: ["query"]
  }
}
```

**Implementation:**
```typescript
async function executeSearchApexDocuments({ query, filters, limit }) {
  const response = await fetch('http://localhost:8000/api/v1/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      filters: filters || {},
      limit: limit || 10
    })
  });

  return await response.json();
}
```

---

### 2. query_apex_graph

```typescript
{
  name: "query_apex_graph",
  description: "Execute a Cypher query on the Neo4j knowledge graph to find entity relationships, connections, and graph patterns.",
  input_schema: {
    type: "object",
    properties: {
      cypher: {
        type: "string",
        description: "Cypher query to execute (e.g., 'MATCH (e:Entity {name: $name})-[r]->(related) RETURN e, r, related')"
      },
      parameters: {
        type: "object",
        description: "Query parameters (e.g., {name: 'ACME Corporation'})",
        additionalProperties: true
      },
      limit: {
        type: "integer",
        default: 100,
        description: "Maximum number of results"
      }
    },
    required: ["cypher"]
  }
}
```

**Implementation:**
```typescript
async function executeQueryApexGraph({ cypher, parameters, limit }) {
  const response = await fetch('http://localhost:8000/api/v1/graph/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      cypher,
      parameters: parameters || {},
      limit: limit || 100
    })
  });

  return await response.json();
}
```

---

### 3. get_apex_temporal_data

```typescript
{
  name: "get_apex_temporal_data",
  description: "Retrieve temporal patterns and trends for an entity using Graphiti. Shows how entity attributes and relationships evolved over time.",
  input_schema: {
    type: "object",
    properties: {
      entity_name: {
        type: "string",
        description: "Name of the entity to analyze (e.g., 'ACME Corporation')"
      },
      time_range: {
        type: "string",
        description: "Time range for analysis (e.g., 'last 30 days', 'last 6 months', 'all time')"
      },
      pattern_type: {
        type: "string",
        enum: ["trends", "seasonality", "anomalies", "all"],
        default: "all",
        description: "Type of temporal patterns to detect"
      }
    },
    required: ["entity_name"]
  }
}
```

**Implementation:**
```typescript
async function executeGetApexTemporalData({ entity_name, time_range, pattern_type }) {
  const response = await fetch('http://localhost:8000/api/v1/temporal/entity', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      entity_name,
      time_range: time_range || 'all time',
      pattern_type: pattern_type || 'all'
    })
  });

  return await response.json();
}
```

---

### 4. get_apex_entity_timeline

```typescript
{
  name: "get_apex_entity_timeline",
  description: "Get chronological timeline of events and mentions for an entity across all documents.",
  input_schema: {
    type: "object",
    properties: {
      entity_name: {
        type: "string",
        description: "Entity to track (e.g., 'Tesla Model 3', 'Project Apollo')"
      },
      start_date: {
        type: "string",
        format: "date",
        description: "Timeline start date (ISO 8601)"
      },
      end_date: {
        type: "string",
        format: "date",
        description: "Timeline end date (ISO 8601)"
      },
      include_related: {
        type: "boolean",
        default: false,
        description: "Include events from related entities"
      }
    },
    required: ["entity_name"]
  }
}
```

**Implementation:**
```typescript
async function executeGetApexEntityTimeline({ entity_name, start_date, end_date, include_related }) {
  const response = await fetch('http://localhost:8000/api/v1/entity/timeline', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      entity_name,
      start_date,
      end_date,
      include_related: include_related || false
    })
  });

  return await response.json();
}
```

---

### 5. get_apex_metadata

```typescript
{
  name: "get_apex_metadata",
  description: "Retrieve document metadata including ingestion date, file size, chunk count, entity count, and processing status.",
  input_schema: {
    type: "object",
    properties: {
      document_id: {
        type: "string",
        description: "Unique document identifier"
      },
      include_stats: {
        type: "boolean",
        default: true,
        description: "Include processing statistics (chunk count, entity count, etc.)"
      }
    },
    required: ["document_id"]
  }
}
```

**Implementation:**
```typescript
async function executeGetApexMetadata({ document_id, include_stats }) {
  const response = await fetch(`http://localhost:8000/api/v1/documents/${document_id}/metadata`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    params: { include_stats: include_stats || true }
  });

  return await response.json();
}
```

---

## Complete Tool Array

```typescript
export const apexTools = [
  {
    name: "search_apex_documents",
    description: "Search the Apex knowledge base for documents matching a query",
    input_schema: { /* see above */ }
  },
  {
    name: "query_apex_graph",
    description: "Execute a Cypher query on the Neo4j knowledge graph",
    input_schema: { /* see above */ }
  },
  {
    name: "get_apex_temporal_data",
    description: "Retrieve temporal patterns and trends for an entity",
    input_schema: { /* see above */ }
  },
  {
    name: "get_apex_entity_timeline",
    description: "Get chronological timeline of events for an entity",
    input_schema: { /* see above */ }
  },
  {
    name: "get_apex_metadata",
    description: "Retrieve document metadata and processing statistics",
    input_schema: { /* see above */ }
  }
];
```

---

## Tool Execution Router

```typescript
async function executeApexTool(toolUse: ToolUse) {
  const { name, input } = toolUse;

  switch (name) {
    case 'search_apex_documents':
      return await executeSearchApexDocuments(input);

    case 'query_apex_graph':
      return await executeQueryApexGraph(input);

    case 'get_apex_temporal_data':
      return await executeGetApexTemporalData(input);

    case 'get_apex_entity_timeline':
      return await executeGetApexEntityTimeline(input);

    case 'get_apex_metadata':
      return await executeGetApexMetadata(input);

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}
```

---

## Streaming with Tool Use

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
        await handleStreamEvent(data);
      }
    }
  }
}

async function handleStreamEvent(event: StreamEvent) {
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
        const result = await executeApexTool(currentBlock);
        // Send result back to Claude
        await continueConversation(result);
      }
      break;
  }
}
```

---

## Example Usage Flows

### Example 1: Document Search

**User Query:** "Find all documents about CAT equipment maintenance"

**Claude's Tool Call:**
```json
{
  "type": "tool_use",
  "id": "toolu_01abc",
  "name": "search_apex_documents",
  "input": {
    "query": "CAT equipment maintenance procedures",
    "filters": {
      "tags": ["equipment", "maintenance"]
    },
    "limit": 10
  }
}
```

**Your Response:**
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01abc",
  "content": {
    "results": [
      {
        "document_id": "doc_123",
        "title": "CAT 320 Excavator Maintenance Guide",
        "excerpt": "Regular maintenance procedures for CAT 320 series...",
        "score": 0.92
      }
    ],
    "total": 5
  }
}
```

### Example 2: Entity Relationships

**User Query:** "Who are ACME Corporation's main suppliers?"

**Claude's Tool Call:**
```json
{
  "type": "tool_use",
  "id": "toolu_02xyz",
  "name": "query_apex_graph",
  "input": {
    "cypher": "MATCH (acme:Entity {name: $company})-[:SUPPLIER]->(supplier) RETURN supplier.name, supplier.relationship_strength ORDER BY supplier.relationship_strength DESC LIMIT 10",
    "parameters": {
      "company": "ACME Corporation"
    }
  }
}
```

---

## References

**Apex API Endpoints:**
- Query API: http://localhost:8000/api/v1/query
- Graph API: http://localhost:8000/api/v1/graph/query
- Temporal API: http://localhost:8000/api/v1/temporal/entity
- Entity Timeline: http://localhost:8000/api/v1/entity/timeline
- Document Metadata: http://localhost:8000/api/v1/documents/{id}/metadata

**Related Documentation:**
- Tool Use API basics → `tool-use-api.md`
- Streaming responses → `streaming-api.md`
- Multi-tool orchestration → `tool-orchestration.md`

**Apex System Architecture:**
- Main codebase: `/apex-memory-system/`
- API documentation: http://localhost:8000/docs

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Type:** Internal Implementation Guide
