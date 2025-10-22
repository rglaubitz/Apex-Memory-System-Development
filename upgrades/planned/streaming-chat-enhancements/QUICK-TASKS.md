# Streaming Chat Enhancements - Quick Task List

**From:** docs/streaming-architecture.md Future Enhancements
**Status:** Planned (not started)
**Timeline:** 4-6 weeks

---

## Backend Enhancements

### 1. Implement Real Tool Executors (2-3 weeks)

**Current:** 1 real (search_knowledge_graph), 4 mock

#### Task 1.1: get_entity_relationships → Neo4j
- **What:** Replace mock with Neo4j Cypher traversal
- **Why:** Real entity relationship data from graph
- **Effort:** 3 days
- **File:** `src/apex_memory/api/chat_stream.py:164-182`

```python
# Current (mock):
return {
    "relationships": [
        {"from": entity_name, "type": "RELATES_TO", "to": "Related Entity 1"}
    ]
}

# Future (real):
cypher = "MATCH (e:Entity {name: $name})-[r]->(related) RETURN ..."
results = await neo4j_client.query(cypher, {"name": entity_name})
return {"relationships": format_relationships(results)}
```

#### Task 1.2: get_temporal_timeline → Graphiti
- **What:** Replace mock with Graphiti temporal query
- **Why:** Real temporal event data
- **Effort:** 4 days
- **File:** `src/apex_memory/api/chat_stream.py:187-207`

```python
# Future:
timeline = await graphiti_client.get_entity_timeline(
    entity_name=tool_input["entity_name"],
    start_date=tool_input.get("start_date"),
    end_date=tool_input.get("end_date")
)
```

#### Task 1.3: find_similar_documents → Qdrant
- **What:** Replace mock with Qdrant vector search
- **Why:** Real document similarity rankings
- **Effort:** 3 days
- **File:** `src/apex_memory/api/chat_stream.py:212-233`

```python
# Future:
results = await qdrant_client.search(
    collection_name="documents",
    query_vector=await get_document_embedding(document_uuid),
    limit=tool_input.get("limit", 5)
)
```

#### Task 1.4: get_graph_statistics → Neo4j
- **What:** Replace mock with Neo4j aggregation
- **Why:** Real graph metrics (node count, density, etc.)
- **Effort:** 2 days
- **File:** `src/apex_memory/api/chat_stream.py:239-247`

```python
# Future:
stats = await neo4j_client.get_statistics()
return {
    "statistics": {
        "total_nodes": stats.node_count,
        "total_relationships": stats.relationship_count,
        "avg_connections": stats.avg_degree
    }
}
```

---

### 2. Tool Result Caching (1 week)

#### Task 2.1: Redis Cache Layer
- **What:** Cache tool results with TTL expiration
- **Why:** Reduce latency, lower API costs for repeated queries
- **Effort:** 1 week
- **File:** `src/apex_memory/api/chat_stream.py` (ToolExecutor class)

```python
async def execute_tool(self, tool_name: str, tool_input: dict):
    # Check cache first
    cache_key = f"tool:{tool_name}:{hash(tool_input)}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Execute and cache
    result = await self._execute_tool_impl(tool_name, tool_input)
    await redis.setex(cache_key, 300, json.dumps(result))  # 5min TTL
    return result
```

**Design Decisions:**
- **TTL:** 5-10 minutes (balance freshness vs hit rate)
- **Cache Key:** `tool:{tool_name}:{hash(sorted(tool_input))}`
- **Target Hit Rate:** >50% after 1 day

---

### 3. Parallel Tool Execution (1 week)

#### Task 3.1: Concurrent Execution
- **What:** Execute independent tools in parallel
- **Why:** Reduce total latency for multi-tool messages
- **Effort:** 1 week
- **Expected Speedup:** 40%+ for multi-tool messages

```python
# Detect independent tools
groups = detect_tool_dependencies(tool_calls)

# Execute each group concurrently
for group in groups:
    results = await asyncio.gather(*[
        execute_tool(tool["name"], tool["input"])
        for tool in group
    ])
```

**Example:**
```
Sequential: search (2s) → relationships (3s) → timeline (2s) = 7s total
Parallel:   search (2s) + relationships (3s) + timeline (2s) = 3s total
Speedup:    57% faster
```

---

### 4. Enhanced Error Handling (3 days)

#### Task 4.1: Timeout & Retry
- **What:** Add 30s timeout per tool, retry transient failures
- **Why:** Prevent hanging requests, improve reliability
- **Effort:** 3 days

```python
@retry(max_attempts=3, backoff=exponential)
@timeout(30)  # 30 second max
async def execute_tool(self, tool_name: str, tool_input: dict):
    # ...
```

---

## Frontend Enhancements

### 5. Artifact Interactions (1-2 weeks)

#### Task 5.1: Export Artifacts (3 days)
- **What:** Export artifacts to JSON/CSV
- **Why:** Users can save results for offline analysis
- **File:** `src/apex_memory/frontend/src/components/ArtifactSidebar.tsx`

```typescript
function exportArtifact(artifact: Artifact, format: 'json' | 'csv') {
  if (format === 'json') {
    downloadJSON(artifact.data, `${artifact.title}.json`);
  } else {
    downloadCSV(artifactToCSV(artifact), `${artifact.title}.csv`);
  }
}
```

#### Task 5.2: Pin Artifacts (4 days)
- **What:** Pin up to 10 artifacts, persist across sessions
- **Why:** Quick access to frequently referenced results
- **File:** New component `PinnedArtifacts.tsx`

```typescript
const [pinnedArtifacts, setPinnedArtifacts] = useState<Artifact[]>([]);

// Save to localStorage
function pinArtifact(artifact: Artifact) {
  const pinned = [...pinnedArtifacts, artifact].slice(0, 10);
  setPinnedArtifacts(pinned);
  localStorage.setItem('pinnedArtifacts', JSON.stringify(pinned));
}
```

#### Task 5.3: Expand/Collapse (3 days)
- **What:** Click to expand/collapse artifact details
- **Why:** Better space utilization, focus on relevant data
- **File:** `src/apex_memory/frontend/src/components/ArtifactSidebar.tsx`

```typescript
const [isExpanded, setIsExpanded] = useState(false);

return (
  <div onClick={() => setIsExpanded(!isExpanded)}>
    <h3>{artifact.title}</h3>
    {isExpanded ? <FullContent /> : <Preview />}
  </div>
);
```

---

### 6. Tool Use Visualization (1 week)

#### Task 6.1: Animated Progress (3 days)
- **What:** Show per-tool progress bars, estimated completion
- **File:** `src/apex_memory/frontend/src/components/ToolIndicator.tsx`

```typescript
<div className="tool-indicator">
  <Loader2 className="animate-spin" />
  <span>{tool.name}</span>
  <ProgressBar progress={tool.progress} />
  <span>Est. {tool.estimatedSeconds}s</span>
</div>
```

#### Task 6.2: Dependency Graph (4 days)
- **What:** Visualize tool execution flow (parallel vs sequential)
- **Why:** Help users understand what Claude is doing

---

### 7. Conversation Export (3 days)

#### Task 7.1: Download Conversation
- **What:** Export full conversation with artifacts
- **Format:** JSON with metadata
- **File:** `src/apex_memory/frontend/src/pages/ConversationsStreaming.tsx`

```typescript
function exportConversation() {
  const data = {
    conversation_id: activeConversationId,
    messages: messages,
    artifacts: artifacts,
    exported_at: new Date().toISOString()
  };
  downloadJSON(data, `conversation-${conversationId}.json`);
}
```

---

## Testing Requirements

### New Tests Needed

**Backend (12 tests):**
- Real tool executors: 3 tests × 4 tools = 12 tests
- Cache integration: 4 tests (hit, miss, expiration, invalidation)
- Parallel execution: 4 tests (independent, dependent, error, speedup)

**Frontend (8 tests):**
- Export: 2 tests (JSON, CSV)
- Pinned artifacts: 4 tests (pin, unpin, persistence, limit)
- Expand/collapse: 2 tests (expand, collapse)

**Integration (10 tests):**
- End-to-end tool execution with real databases
- Cache hit/miss in realistic scenarios
- Parallel execution with multiple tools
- Artifact export with various data types

**Total:** 30 new tests

---

## Implementation Order (Recommended)

**Priority 1 (Weeks 1-3): Real Tool Executors**
1. get_entity_relationships (Neo4j)
2. get_graph_statistics (Neo4j)
3. find_similar_documents (Qdrant)
4. get_temporal_timeline (Graphiti)

**Priority 2 (Week 4): Caching**
5. Redis cache integration
6. Cache metrics monitoring

**Priority 3 (Week 5): Parallel Execution**
7. Dependency detection
8. Concurrent executor
9. Error handling

**Priority 4 (Weeks 6-7): Frontend Polish**
10. Artifact export
11. Pinned artifacts
12. Expand/collapse
13. Tool visualization

---

## Quick Estimates

| Enhancement | Effort | Impact | Priority |
|-------------|--------|--------|----------|
| Real tool executors | 2-3 weeks | High | P1 |
| Tool caching | 1 week | Medium | P2 |
| Parallel execution | 1 week | Medium | P2 |
| Artifact export | 3 days | Low | P3 |
| Pinned artifacts | 4 days | Medium | P3 |
| Expand/collapse | 3 days | Low | P3 |

**Total Timeline:** 4-6 weeks full-time

---

**Source:** docs/streaming-architecture.md
**Created:** 2025-10-22
**Next Step:** Research phase for database integration patterns
