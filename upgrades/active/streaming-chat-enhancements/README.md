# Streaming Chat Enhancements

**Status:** 📝 Planned
**Priority:** Medium
**Estimated Timeline:** 4-6 weeks
**Dependencies:** Phase 2.5 Complete (streaming infrastructure operational)

---

## Overview

Enhancement package for the streaming chat system implementing production-grade features: real tool executors, caching, parallel execution, and enhanced UX.

**Current State (Phase 2.5 Complete):**
- ✅ SSE-based streaming chat
- ✅ Claude tool use integration (5 tools)
- ✅ Progressive artifact visualization
- ✅ 20 passing tests
- ⚠️ 1 real tool executor, 4 mock implementations

**This Upgrade Delivers:**
- ✅ All 5 tools with real database integrations
- ✅ Redis-based tool result caching
- ✅ Parallel tool execution for independent calls
- ✅ Enhanced artifact interactions (export, pin, expand)
- ✅ Improved error handling and retry logic

---

## Motivation

### Current Limitations

1. **Mock Tool Executors (4/5 tools)**
   - `get_entity_relationships` returns placeholder data
   - `get_temporal_timeline` returns placeholder data
   - `find_similar_documents` returns placeholder data
   - `get_graph_statistics` returns placeholder data
   - **Impact:** Cannot deliver real graph insights to users

2. **No Result Caching**
   - Repeated tool calls execute fully each time
   - **Impact:** Slower response times, higher API costs

3. **Sequential Tool Execution**
   - Tools execute one-at-a-time even when independent
   - **Impact:** Longer total execution time

4. **Limited Artifact Interactions**
   - Cannot export artifacts
   - Cannot pin artifacts across messages
   - Cannot expand/collapse for detail viewing
   - **Impact:** Reduced usability for power users

---

## Goals

### Primary Goals

1. **Implement Real Tool Executors** - Replace all 4 mock tools with actual database queries
2. **Tool Result Caching** - Redis-based caching with TTL expiration
3. **Parallel Tool Execution** - Concurrent execution for independent tools
4. **Enhanced Artifacts** - Export, pin, expand/collapse interactions

### Success Metrics

- ✅ All 5 tools return real data from Apex databases
- ✅ Cache hit rate >50% for repeated queries
- ✅ Parallel execution reduces latency by 40%+ for multi-tool messages
- ✅ Artifact export supports JSON and CSV formats
- ✅ Users can pin up to 10 artifacts per conversation

---

## Research Phase

### Required Research

**Database Integration (1 week):**
1. Neo4j Cypher for relationship traversal
2. Graphiti temporal query API
3. Qdrant vector similarity search
4. Neo4j aggregation queries

**Caching Strategy (3 days):**
1. Redis key design for tool results
2. TTL tuning (balance freshness vs hit rate)
3. Cache invalidation strategies
4. Memory usage estimation

**Parallel Execution (2 days):**
1. Tool dependency detection
2. asyncio.gather best practices
3. Error handling in concurrent execution

**Frontend Enhancements (3 days):**
1. Export libraries (JSON, CSV)
2. State persistence for pinned artifacts
3. Expand/collapse UX patterns

### Research Deliverables

- [ ] Neo4j query patterns document
- [ ] Graphiti integration guide
- [ ] Redis caching design document
- [ ] Parallel execution architecture
- [ ] Frontend enhancement mockups

---

## Implementation Plan

### Phase 1: Real Tool Executors (2-3 weeks)

#### Week 1: Neo4j Tools

**Task 1.1: get_entity_relationships (3 days)**
```python
async def execute_tool(self, tool_name: str, tool_input: dict):
    if tool_name == "get_entity_relationships":
        # Replace mock with Neo4j Cypher
        cypher = """
        MATCH (entity:Entity {name: $entity_name})-[r]->(related)
        RETURN entity.name, type(r), related.name, properties(r)
        LIMIT 20
        """
        results = await self.neo4j_client.query(cypher, {
            "entity_name": tool_input["entity_name"]
        })
        return {"relationships": format_relationships(results)}
```

**Success Criteria:**
- Returns real entity relationships from Neo4j
- Supports configurable max_depth (1-3 levels)
- Handles entities with 0 relationships gracefully

**Task 1.2: get_graph_statistics (2 days)**
```python
async def execute_tool(self, tool_name: str, tool_input: dict):
    if tool_name == "get_graph_statistics":
        # Replace mock with Neo4j aggregation
        stats = await self.neo4j_client.get_statistics()
        return {
            "statistics": {
                "total_nodes": stats.node_count,
                "total_relationships": stats.relationship_count,
                "entity_types": stats.label_count,
                "avg_connections": stats.avg_degree,
                "graph_density": stats.density
            }
        }
```

**Success Criteria:**
- Returns real graph metrics from Neo4j
- Execution time <500ms
- Accurate counts and calculations

#### Week 2: Graphiti + Qdrant Tools

**Task 1.3: get_temporal_timeline (4 days)**
```python
async def execute_tool(self, tool_name: str, tool_input: dict):
    if tool_name == "get_temporal_timeline":
        # Replace mock with Graphiti temporal query
        timeline = await self.graphiti_client.get_entity_timeline(
            entity_name=tool_input["entity_name"],
            start_date=tool_input.get("start_date"),
            end_date=tool_input.get("end_date")
        )
        return {"timeline": format_timeline(timeline)}
```

**Success Criteria:**
- Returns real temporal events from Graphiti
- Supports date range filtering
- Events sorted chronologically

**Task 1.4: find_similar_documents (3 days)**
```python
async def execute_tool(self, tool_name: str, tool_input: dict):
    if tool_name == "find_similar_documents":
        # Replace mock with Qdrant vector search
        results = await self.qdrant_client.search(
            collection_name="documents",
            query_vector=await get_document_embedding(
                tool_input["document_uuid"]
            ),
            limit=tool_input.get("limit", 5)
        )
        return {"similar_documents": format_similar_docs(results)}
```

**Success Criteria:**
- Returns real similarity results from Qdrant
- Similarity scores accurate (cosine similarity)
- Configurable result limit

#### Week 3: Testing + Integration

**Task 1.5: Update Tests (3 days)**
- Replace mock assertions with real data checks
- Add integration tests for each tool
- Test error cases (entity not found, etc.)

**Task 1.6: Performance Optimization (2 days)**
- Add query timeouts (30s max)
- Optimize Cypher queries for large graphs
- Benchmark all tools under load

---

### Phase 2: Tool Result Caching (1 week)

#### Week 4: Redis Cache Implementation

**Task 2.1: Cache Key Design (1 day)**
```python
def get_cache_key(tool_name: str, tool_input: dict) -> str:
    """Generate deterministic cache key."""
    input_hash = hashlib.md5(
        json.dumps(tool_input, sort_keys=True).encode()
    ).hexdigest()
    return f"tool:{tool_name}:{input_hash}"
```

**Task 2.2: Cache Integration (2 days)**
```python
async def execute_tool(self, tool_name: str, tool_input: dict):
    # Check cache first
    cache_key = get_cache_key(tool_name, tool_input)
    cached = await self.redis.get(cache_key)

    if cached:
        return json.loads(cached)

    # Execute tool
    result = await self._execute_tool_impl(tool_name, tool_input)

    # Cache result with TTL
    await self.redis.setex(
        cache_key,
        self.cache_ttl_seconds,  # 5-10 minutes
        json.dumps(result)
    )

    return result
```

**Task 2.3: Cache Metrics (2 days)**
- Track cache hit/miss rates
- Monitor cache memory usage
- Log cache performance in Prometheus

**Success Criteria:**
- Cache hit rate >50% after 1 day of usage
- Cache TTL configurable (default 5 minutes)
- Cache invalidation on data updates

---

### Phase 3: Parallel Tool Execution (1 week)

#### Week 5: Concurrent Execution

**Task 3.1: Dependency Detection (2 days)**
```python
def detect_tool_dependencies(tool_calls: list[dict]) -> dict:
    """Detect which tools can run in parallel."""
    # Tools are independent if they don't share input parameters
    groups = []
    for tool in tool_calls:
        can_merge = False
        for group in groups:
            if not shares_inputs(tool, group):
                group.append(tool)
                can_merge = True
                break
        if not can_merge:
            groups.append([tool])
    return groups
```

**Task 3.2: Parallel Executor (3 days)**
```python
async def execute_tools_parallel(self, tool_calls: list[dict]):
    """Execute independent tools concurrently."""
    groups = detect_tool_dependencies(tool_calls)

    all_results = []
    for group in groups:
        # Execute tools in this group concurrently
        results = await asyncio.gather(*[
            self.execute_tool(tool["name"], tool["input"])
            for tool in group
        ])
        all_results.extend(results)

    return all_results
```

**Task 3.3: Error Handling (2 days)**
- Handle partial failures (some tools succeed, some fail)
- Implement retry logic for transient errors
- Stream partial results as they complete

**Success Criteria:**
- Multi-tool messages execute 40%+ faster
- Partial results streamed progressively
- Error in one tool doesn't block others

---

### Phase 4: Enhanced Artifacts (1-2 weeks)

#### Week 6-7: Frontend Enhancements

**Task 4.1: Artifact Export (3 days)**
```typescript
function exportArtifact(artifact: Artifact, format: 'json' | 'csv') {
  if (format === 'json') {
    downloadJSON(artifact.data, `${artifact.title}.json`);
  } else {
    downloadCSV(artifactToCSV(artifact), `${artifact.title}.csv`);
  }
}
```

**Features:**
- Export to JSON (full data)
- Export to CSV (tabular artifacts only)
- Download with descriptive filename

**Task 4.2: Pinned Artifacts (4 days)**
```typescript
interface PinnedArtifact extends Artifact {
  pinnedAt: Date;
  conversationId: string;
}

// State management
const [pinnedArtifacts, setPinnedArtifacts] = useState<PinnedArtifact[]>([]);

// Pin/unpin actions
function pinArtifact(artifact: Artifact) {
  setPinnedArtifacts(prev => [...prev, { ...artifact, pinnedAt: new Date() }]);
  localStorage.setItem('pinnedArtifacts', JSON.stringify(pinnedArtifacts));
}
```

**Features:**
- Pin up to 10 artifacts per conversation
- Pinned artifacts persist across page refreshes
- Quick access dropdown for pinned artifacts

**Task 4.3: Expand/Collapse (3 days)**
```typescript
function ArtifactCard({ artifact }: { artifact: Artifact }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="artifact-card">
      <div className="artifact-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>{artifact.title}</h3>
        <ChevronIcon expanded={isExpanded} />
      </div>
      {isExpanded && <ArtifactContent data={artifact.data} />}
    </div>
  );
}
```

**Features:**
- Expand/collapse artifact details
- Preview mode shows first 3 items
- Smooth animations

**Task 4.4: Testing (2 days)**
- Add tests for export functions
- Test pinned artifacts persistence
- Test expand/collapse behavior

---

## Testing Strategy

### Unit Tests (20 new tests)

**Backend (12 tests):**
- Real tool executors (3 tests per tool)
- Cache hit/miss scenarios (4 tests)
- Parallel execution logic (4 tests)

**Frontend (8 tests):**
- Artifact export (2 tests)
- Pinned artifacts (4 tests)
- Expand/collapse (2 tests)

### Integration Tests (10 tests)

- End-to-end tool execution with real databases
- Cache integration with Redis
- Parallel execution with multiple tools
- Artifact export with various data types

### Performance Tests (5 tests)

- Tool execution latency under load
- Cache hit rate measurement
- Parallel execution speedup validation
- Memory usage with large artifacts

---

## Deployment Plan

### Prerequisites

1. **Neo4j Available** - Graph database accessible
2. **Graphiti Configured** - Temporal graph ready
3. **Qdrant Running** - Vector database operational
4. **Redis Configured** - Cache layer ready

### Rollout Strategy

**Phase 1: Backend Tools (Week 1-3)**
- Deploy real tool executors behind feature flag
- Monitor performance and error rates
- Gradually enable for all users

**Phase 2: Caching (Week 4)**
- Enable Redis caching for all tools
- Monitor cache metrics daily
- Tune TTL based on hit rate data

**Phase 3: Parallel Execution (Week 5)**
- Enable parallel execution for beta users
- Validate performance improvements
- Roll out to all users

**Phase 4: Frontend Enhancements (Week 6-7)**
- Deploy export feature first
- Release pinned artifacts next
- Enable expand/collapse last

### Monitoring

**Key Metrics:**
- Tool execution latency (P50, P95, P99)
- Cache hit rate (target >50%)
- Parallel execution speedup (target 40%+)
- Error rates per tool (<1%)
- Artifact export usage
- Pinned artifacts per user (avg)

---

## Dependencies

### Internal

- **Streaming Chat Infrastructure** (Phase 2.5) - Must be complete
- **Neo4j Database** - Must be populated with entities
- **Graphiti Integration** - Must be operational
- **Qdrant Database** - Must have document embeddings
- **Redis Cache** - Must be configured

### External

- **Anthropic SDK** - No changes needed
- **Vercel AI SDK** - No changes needed
- **React Libraries** - May need export libraries (file-saver, papaparse)

---

## Risks & Mitigations

### Technical Risks

**Risk 1: Tool Performance Degradation**
- Real queries may be slower than mocks
- **Mitigation:** Optimize queries, add timeouts, implement caching

**Risk 2: Cache Invalidation Complexity**
- Stale cache results after data updates
- **Mitigation:** Conservative TTLs (5-10 minutes), manual invalidation API

**Risk 3: Parallel Execution Errors**
- Harder to debug concurrent failures
- **Mitigation:** Comprehensive logging, error isolation, fallback to sequential

### Operational Risks

**Risk 1: Redis Failure**
- Cache unavailable breaks all tools
- **Mitigation:** Graceful degradation (bypass cache on error)

**Risk 2: Database Overload**
- Parallel tools create query spikes
- **Mitigation:** Rate limiting, query timeouts, connection pooling

---

## Future Considerations

**Post-Upgrade Enhancements:**

1. **Tool Composition** - Allow tools to call other tools
2. **Custom Tools** - User-defined tool plugins
3. **Tool Analytics** - Dashboard showing tool usage patterns
4. **Streaming Artifacts** - Update artifacts as data arrives (not just on completion)
5. **Artifact Sharing** - Share artifacts via URL

---

## References

### Source Documentation

- **Streaming Architecture:** `docs/streaming-architecture.md`
- **QueryRouter:** `docs/query-router-architecture.md`
- **Neo4j Integration:** `research/documentation/neo4j/README.md`
- **Graphiti Integration:** `research/documentation/graphiti/README.md`

### Code Locations

- **ToolExecutor:** `src/apex_memory/api/chat_stream.py:139-251`
- **Frontend Hook:** `src/apex_memory/frontend/src/hooks/useApexChat.ts`
- **Artifacts Sidebar:** `src/apex_memory/frontend/src/components/ArtifactSidebar.tsx`

---

## Approval Criteria

**Ready for Phase 2 (Mission) when:**
- ✅ All research deliverables complete
- ✅ Database schemas validated
- ✅ Cache design approved
- ✅ Frontend mockups reviewed

**Ready for Phase 4 (Implementation) when:**
- ✅ Phase 3 (Execution Plan) approved by Review Board
- ✅ All dependencies verified operational
- ✅ Test strategy documented
- ✅ Rollout plan finalized

---

**Created:** 2025-10-22
**Status:** 📝 Planned (Phase 1: Vision Complete)
**Next Step:** Research Phase (Phase 2: Mission)
**Estimated Completion:** 4-6 weeks from start
