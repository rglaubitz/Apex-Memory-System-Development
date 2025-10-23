# MCP Integration - Improvement Plan

**Status:** ACTIVE 🚀
**Created:** 2025-10-20
**Priority:** IMPORTANT
**Timeline:** 2 weeks
**Research Phase:** COMPLETE ✅

---

## Executive Summary

**Objective:** Add Model Context Protocol (MCP) support to Apex Memory System, enabling native integration with Claude Desktop, Cursor, and other MCP-compatible AI tools.

**Current State:**
- ✅ REST API fully functional (`/api/v1/messages/*`)
- ✅ Graphiti integration working (LLM entity extraction)
- ✅ Multi-database writes proven (162 tests passing)
- ❌ No MCP protocol support
- ❌ No Claude Desktop integration

**Desired State:**
- ✅ Thin MCP wrapper around existing REST API
- ✅ 10 MCP tools (simple + advanced + Apex-unique)
- ✅ Claude Desktop one-click installation
- ✅ Cursor/SSE support
- ✅ Resources and prompts exposed
- ✅ 20+ MCP integration tests

**Impact:**
- Better discoverability (Claude Desktop extensions)
- Automatic context injection (no manual API calls)
- Competitive parity with OpenMemory and Graphiti MCP
- Standard protocol (works with all MCP clients)

---

## Research Foundation

### Reference Architectures Analyzed

**1. OpenMemory MCP** (Mem0 - Simple & Local-First)

**Architecture:**
```
Claude Desktop → MCP (stdio) → OpenMemory MCP Server
    ↓
4 Simple Tools:
    - add_memories(content, user_id, metadata)
    - search_memory(query, user_id, limit)
    - list_memories(user_id, limit)
    - delete_all_memories(user_id)
    ↓
JSONL File Storage → Knowledge Graph (entities, relations, observations)
```

**Key Lessons:**
- Simplicity wins for adoption (4 tools only)
- Local-first privacy focus
- Single-file persistence
- Clear tool naming conventions

---

**2. Graphiti MCP** (Zep - Sophisticated & Temporal-Aware)

**Architecture:**
```
Claude Desktop / Cursor → MCP (stdio/SSE) → Graphiti MCP Server
    ↓
8 Sophisticated Tools:
    - add_episode(name, episode_body, source, source_description, group_id)
    - search_nodes(query, limit, group_id)
    - search_facts(query, limit, group_id)
    - delete_entity_edge(edge_uuid, group_id)
    - delete_episode(episode_id, group_id)
    - get_entity_edge(edge_uuid, group_id)
    - get_episodes(limit, group_id)
    - clear_graph(group_id)
    ↓
Graphiti Core → Neo4j → Bi-Temporal Knowledge Graph
```

**Key Lessons:**
- Multi-project support via `group_id`
- Dual transport (stdio + SSE)
- Environment-based configuration
- Concurrency control (SEMAPHORE_LIMIT)
- LLM entity extraction integration

---

### Apex MCP Strategy: Best of Both Worlds

**Apex Advantages:**
1. ✅ Multi-database architecture (Neo4j + PostgreSQL + Qdrant + Redis)
2. ✅ Intelligent query routing (intent classification)
3. ✅ Enhanced Saga pattern (distributed transactions)
4. ✅ Production monitoring (Prometheus + Grafana)
5. ✅ Proven reliability (162 tests passing)

**MCP Integration Approach:**
- **Simple API** (OpenMemory-style): 4 tools for ease of use
- **Advanced API** (Graphiti-style): 3 tools for power users
- **Apex-Unique API**: 3 tools leveraging multi-DB architecture

**Total:** 10 MCP tools providing comprehensive functionality

---

## Architecture Design

### Option 1: Thin MCP Wrapper (RECOMMENDED ✅)

```
Claude Desktop
    ↓ MCP Protocol
Apex MCP Server (new: 200-300 lines Python)
    ↓ HTTP calls
Existing REST API (/api/v1/messages/*)
    ↓
GraphitiService → Multi-Database Writes
    ├─ Neo4j (graph)
    ├─ PostgreSQL (metadata)
    ├─ Qdrant (vectors)
    └─ Redis (cache)
```

**Pros:**
- ✅ Minimal code (reuse 100% of existing API)
- ✅ No breaking changes to backend
- ✅ MCP server can be separate package
- ✅ REST API still usable by other clients
- ✅ Easy testing (mock HTTP responses)

**Cons:**
- HTTP overhead (negligible: ~1-5ms)

---

### Option 2: Direct Integration (NOT RECOMMENDED ❌)

```
Claude Desktop
    ↓ MCP Protocol
Apex MCP Server (integrated with GraphitiService)
    ↓ Direct calls
GraphitiService → Multi-Database Writes
```

**Pros:**
- Slightly faster (no HTTP)

**Cons:**
- ❌ More coupling between MCP and backend
- ❌ Duplicates API logic
- ❌ Harder to test
- ❌ Breaks separation of concerns

**Decision:** Use **Option 1 (Thin Wrapper)** for maintainability and flexibility.

---

## MCP Tools Specification

### Category 1: Simple Tools (OpenMemory-style)

**Target Users:** Basic memory use cases, new users

**1. add_memory**
```python
@mcp.tool()
async def add_memory(
    content: str,
    user_id: str = "default",
    metadata: dict = None
) -> dict:
    """Store a memory in Apex knowledge graph (simplified API)."""
    # Maps to: POST /api/v1/messages/message
```

**2. search_memory**
```python
@mcp.tool()
async def search_memory(
    query: str,
    user_id: str = "default",
    limit: int = 10
) -> list:
    """Search Apex memory using intelligent query routing."""
    # Maps to: POST /api/v1/query
```

**3. list_memories**
```python
@mcp.tool()
async def list_memories(
    user_id: str = "default",
    limit: int = 20
) -> list:
    """List recent memories."""
    # Maps to: GET /api/v1/analytics/recent-episodes
```

**4. clear_memories**
```python
@mcp.tool()
async def clear_memories(user_id: str = "default") -> dict:
    """Clear all memories for a user."""
    # Maps to: DELETE /api/v1/maintenance/user-data/{user_id}
```

---

### Category 2: Advanced Tools (Graphiti-style)

**Target Users:** Power users, complex use cases

**5. add_episode**
```python
@mcp.tool()
async def add_episode(
    name: str,
    episode_body: str,
    source: str = "mcp",
    source_description: str = "MCP client",
    group_id: str = "default"
) -> dict:
    """Add episode with full Graphiti capabilities."""
    # Maps to: POST /api/v1/messages/message (with enhanced metadata)
```

**6. search_nodes**
```python
@mcp.tool()
async def search_nodes(
    query: str,
    limit: int = 10,
    group_id: str = "default"
) -> list:
    """Search for entity nodes in knowledge graph."""
    # Maps to: POST /api/v1/query (intent: "graph")
```

**7. search_facts**
```python
@mcp.tool()
async def search_facts(
    query: str,
    limit: int = 10,
    group_id: str = "default"
) -> list:
    """Search for entity relationships."""
    # Maps to: POST /api/v1/query (result_type: "relationships")
```

---

### Category 3: Apex-Unique Tools

**Target Users:** Users leveraging Apex's multi-DB architecture

**8. hybrid_search**
```python
@mcp.tool()
async def hybrid_search(
    query: str,
    databases: list[str] = None,  # ["neo4j", "postgres", "qdrant"]
    limit: int = 10
) -> dict:
    """Search across multiple databases with intelligent routing."""
    # Maps to: POST /api/v1/query (strategy: "hybrid")
    # Apex-unique: Query router selects optimal database(s)
```

**9. get_temporal_context**
```python
@mcp.tool()
async def get_temporal_context(
    query: str,
    timestamp: str = None,
    limit: int = 10
) -> dict:
    """Get knowledge graph state at specific point in time."""
    # Maps to: POST /api/v1/query/temporal
    # Apex-unique: Bi-temporal Graphiti integration
```

**10. get_knowledge_graph_stats**
```python
@mcp.tool()
async def get_knowledge_graph_stats(
    group_id: str = "default"
) -> dict:
    """Get statistics about knowledge graph."""
    # Maps to: GET /api/v1/analytics/graph-stats
    # Apex-unique: Multi-database aggregated stats
```

---

## Resources & Prompts

### Resources (Data Claude Can Read)

**1. Knowledge Graph Snapshot**
```python
@mcp.resource("apex://knowledge-graph")
async def get_knowledge_graph() -> str:
    """Get complete knowledge graph snapshot."""
    # Returns JSON with entities, relationships, communities
```

**2. Recent Patterns**
```python
@mcp.resource("apex://recent-patterns")
async def get_recent_patterns() -> str:
    """Get detected patterns from memory."""
    # Returns trending topics, recurring entities, etc.
```

---

### Prompts (Templates Claude Can Use)

**1. Summarize Conversations**
```python
@mcp.prompt()
async def summarize_conversations(timeframe: str = "24h") -> str:
    """Generate prompt for conversation summary."""
    return f"""
    Based on the knowledge graph, summarize key conversations from the last {timeframe}.
    Focus on:
    - Key decisions made
    - Action items identified
    - Important entities mentioned
    - Relationship changes
    """
```

**2. Extract Key Facts**
```python
@mcp.prompt()
async def extract_key_facts(topic: str) -> str:
    """Generate prompt for fact extraction about a topic."""
    return f"""
    Analyze the knowledge graph and extract key facts about: {topic}
    Include:
    - Core entities related to the topic
    - Relationships between entities
    - Temporal evolution of facts
    - Confidence levels based on source diversity
    """
```

---

## Implementation Plan

### Week 1: Core MCP Server + Claude Desktop

**Day 1-2: Basic MCP Server**

**Tasks:**
1. Create `apex-mcp-server` package structure
2. Implement FastMCP server with 4 simple tools
3. Add environment configuration
4. Test with mock HTTP responses

**Files to Create:**
```
apex-mcp-server/
├── src/
│   ├── apex_mcp_server.py       # Main MCP server
│   ├── config.py                # Environment vars
│   └── tools/
│       ├── simple_tools.py      # 4 simple tools
│       ├── advanced_tools.py    # 3 advanced tools
│       └── apex_tools.py        # 3 Apex-unique tools
├── tests/
│   ├── test_simple_tools.py
│   ├── test_advanced_tools.py
│   └── test_apex_tools.py
├── pyproject.toml
└── README.md
```

**Deliverables:**
- ✅ MCP server runs locally
- ✅ 4 simple tools functional
- ✅ Tests passing (10+ tests)

---

**Day 3: Advanced + Apex-Unique Tools**

**Tasks:**
1. Implement 3 advanced tools (Graphiti-style)
2. Implement 3 Apex-unique tools
3. Add error handling and logging
4. Integration tests with real Apex API

**Deliverables:**
- ✅ All 10 tools functional
- ✅ Error handling robust
- ✅ Integration tests passing

---

**Day 4-5: Claude Desktop Integration**

**Tasks:**
1. Create Claude Desktop config template
2. Write installation script
3. Test with Claude Desktop locally
4. Documentation for end users

**Files to Create:**
```
apex-mcp-server/
├── install-apex-mcp.sh          # Installation script
├── claude_config.json.template  # Config template
└── docs/
    ├── INSTALLATION.md
    └── CLAUDE_DESKTOP_SETUP.md
```

**Deliverables:**
- ✅ One-click installation script
- ✅ Claude Desktop working locally
- ✅ User documentation complete

---

### Week 2: SSE Transport + Advanced Features

**Day 1-2: Cursor/SSE Support**

**Tasks:**
1. Add SSE transport to MCP server
2. Test with Cursor IDE
3. Document Cursor setup
4. Handle transport negotiation

**Updates:**
```python
# apex_mcp_server.py
if args.transport == "sse":
    from mcp.server.sse import SseServerTransport
    transport = SseServerTransport("/messages")
    # Serve on http://localhost:8000/sse
```

**Deliverables:**
- ✅ SSE transport working
- ✅ Cursor integration tested
- ✅ Dual transport support (stdio + SSE)

---

**Day 3: Resources & Prompts**

**Tasks:**
1. Implement 2 resources (knowledge graph, patterns)
2. Implement 2 prompts (summarization, fact extraction)
3. Test resource access from Claude
4. Document prompt usage

**Deliverables:**
- ✅ Resources accessible
- ✅ Prompts usable from Claude
- ✅ Examples documented

---

**Day 4-5: Testing & Documentation**

**Tasks:**
1. Comprehensive test suite (20+ tests)
2. Performance testing (latency, throughput)
3. Complete documentation
4. Example use cases
5. Troubleshooting guide

**Deliverables:**
- ✅ 20+ MCP integration tests passing
- ✅ All 162 existing tests still passing
- ✅ Complete documentation (README, guides, examples)
- ✅ Troubleshooting guide

---

## Success Criteria

### Must Have (Deployment Blocking)

- [ ] Claude Desktop can add memories without API calls
- [ ] Hybrid search across 4 databases works via MCP
- [ ] Temporal queries functional
- [ ] One-click installation script
- [ ] All 162 existing tests still passing
- [ ] 20+ new MCP integration tests passing
- [ ] No breaking changes to REST API

### Nice to Have (Post-MVP)

- [ ] Streaming support for long-running queries
- [ ] Batch operations for efficiency
- [ ] Progress indicators for multi-step operations
- [ ] Desktop notification integration
- [ ] Export functionality (graph as JSON/GraphML)

---

## Testing Strategy

### Unit Tests (10+ tests)

```python
# tests/test_simple_tools.py
async def test_add_memory():
    """Test add_memory tool with mock API."""
    result = await add_memory(
        content="Test message",
        user_id="test-user"
    )
    assert result["success"] is True

async def test_search_memory():
    """Test search_memory tool with mock API."""
    results = await search_memory(
        query="test query",
        user_id="test-user"
    )
    assert isinstance(results, list)
```

### Integration Tests (10+ tests)

```python
# tests/test_mcp_integration.py
async def test_add_memory_e2e(apex_api_running):
    """Test add_memory with real Apex API."""
    result = await add_memory(
        content="ACME Corp ordered 50 brake parts"
    )
    assert result["success"] is True
    assert len(result["entities_extracted"]) > 0

async def test_hybrid_search_e2e(apex_api_running):
    """Test hybrid search across multiple databases."""
    results = await hybrid_search(
        query="brake parts",
        databases=["neo4j", "qdrant"]
    )
    assert len(results["neo4j"]) > 0
    assert len(results["qdrant"]) > 0
```

### Manual Tests

**Claude Desktop:**
1. Install Apex MCP via script
2. Restart Claude Desktop
3. Test conversation:
   - "Remember that ACME Corp ordered 50 brake parts"
   - "What did ACME Corp order?"
   - "Show me the knowledge graph"

**Cursor:**
1. Configure SSE endpoint
2. Test context injection
3. Verify memory persistence

---

## Deployment Plan

### Phase 1: Internal Testing (Week 1, Day 5)

- Deploy to local development environment
- Test all 10 tools manually
- Verify Claude Desktop integration
- Fix any issues found

### Phase 2: Beta Release (Week 2, Day 3)

- Package for PyPI
- Create GitHub release
- Beta testing with selected users
- Gather feedback

### Phase 3: Production Release (Week 2, Day 5)

- Address beta feedback
- Final testing
- PyPI stable release
- Documentation published
- Announcement (blog post, social media)

---

## Risk Mitigation

### Risk 1: MCP SDK API Changes

**Mitigation:**
- Pin MCP SDK version in pyproject.toml
- Monitor MCP SDK releases
- Test with latest SDK in CI/CD

### Risk 2: Breaking Changes to Apex API

**Mitigation:**
- All changes tested with existing 162 tests
- No modifications to REST API contract
- MCP server is separate package (loose coupling)

### Risk 3: Claude Desktop Config Conflicts

**Mitigation:**
- Use unique server name ("apex-memory")
- Document conflict resolution
- Provide config validation tool

---

## Dependencies

### External

- `mcp` (Python SDK): ^1.2.1
- `requests`: ^2.32.0
- `pydantic`: ^2.0.0

### Internal

- Apex Memory System API (localhost:8000)
- All existing Apex dependencies preserved

---

## Documentation Deliverables

### User Documentation

1. **README.md** - Quick start guide
2. **INSTALLATION.md** - Step-by-step installation
3. **CLAUDE_DESKTOP_SETUP.md** - Claude Desktop configuration
4. **CURSOR_SETUP.md** - Cursor IDE configuration
5. **TOOLS_REFERENCE.md** - Complete tool documentation
6. **EXAMPLES.md** - Example use cases
7. **TROUBLESHOOTING.md** - Common issues and solutions

### Developer Documentation

1. **ARCHITECTURE.md** - MCP server architecture
2. **CONTRIBUTING.md** - How to contribute
3. **TESTING.md** - Testing guide
4. **API_MAPPING.md** - MCP tools → REST API mapping

---

## Competitive Advantages

**Apex MCP vs. OpenMemory:**
- ✅ Multi-database architecture (4 DBs vs 1 SQLite)
- ✅ Intelligent query routing
- ✅ Temporal intelligence (bi-temporal tracking)
- ✅ LLM entity extraction (Graphiti)
- ✅ Hybrid search (semantic + keyword + graph)

**Apex MCP vs. Graphiti MCP:**
- ✅ Multi-database support (Neo4j + PostgreSQL + Qdrant + Redis)
- ✅ Query router intelligence (intent classification)
- ✅ Enhanced Saga pattern (distributed transactions)
- ✅ Production monitoring (Prometheus + Grafana)
- ✅ 162 passing tests (proven reliability)

**Result:** Apex becomes the **most sophisticated memory MCP** available.

---

## Timeline Summary

**Week 1:**
- Day 1-2: Basic MCP server (4 simple tools)
- Day 3: Advanced + Apex-unique tools (6 more tools)
- Day 4-5: Claude Desktop integration

**Week 2:**
- Day 1-2: SSE transport for Cursor
- Day 3: Resources & prompts
- Day 4-5: Testing & documentation

**Total Effort:** 10 days (2 weeks)

---

## Next Steps

1. ✅ Improvement plan approved
2. 🚀 Begin Week 1, Day 1 implementation
3. Create `apex-mcp-server` package
4. Implement 4 simple tools
5. Write unit tests

---

**Status:** Ready for implementation ✅
**Blockers:** None
**Dependencies:** Apex Memory System API (already running)
