# Phase 2: Manual Testing Guide

**Status:** Ready to Execute
**Prerequisites:**
- ✅ Apex API running at http://localhost:8000
- ✅ .env file configured with Anthropic API key
- ✅ Claude Desktop configured with apex-memory MCP server
- ⏳ **NEXT:** Restart Claude Desktop (⌘+Q then reopen)

---

## 🚀 Quick Start

**Copy the following commands into Claude Desktop to test each feature:**

---

## Test 1: Verify MCP Server Loaded ✅

**In Claude Desktop, ask:**
```
What MCP tools do you have available from apex-memory?
```

**Expected Result:** Should list 10 tools:
- add_memory
- add_conversation
- search_memory
- list_recent_memories
- clear_memories
- temporal_search
- get_entity_timeline
- get_communities
- get_graph_stats
- ask_apex

---

## Test 2: Basic Storage - add_memory() 📝

**In Claude Desktop, ask:**
```
Remember that I prefer Python for backend development and TypeScript for frontend.
```

**Expected Behavior:**
- Claude should use `add_memory()` tool
- Should store the preference in Apex Memory
- Should confirm storage with episode UUID

**Verification:**
```
What programming languages do I prefer?
```
Should retrieve and cite the stored memory.

---

## Test 3: Conversation Storage - add_conversation() 💬

**In Claude Desktop, have a multi-turn conversation:**
```
Let's discuss ACME Corporation. They had $5.2M revenue in Q4 2024, representing 15% YoY growth. They work with Bosch as their main supplier. Can you remember this entire conversation?
```

**Expected Behavior:**
- Claude should use `add_conversation()` tool
- Should store entire conversation context
- Should return episode UUIDs for each turn

**Verification:**
```
What do you know about ACME Corporation's financials?
```
Should retrieve the Q4 2024 revenue and growth data.

---

## Test 4: Semantic Search - search_memory() 🔍

**In Claude Desktop, ask:**
```
Search for memories about programming preferences.
```

**Expected Behavior:**
- Claude should use `search_memory()` tool
- Should return relevant memories with scores
- Should show document titles and excerpts

**Expected Results:**
- Python/TypeScript preference from Test 2
- Relevance scores (0.0-1.0)
- Episode UUIDs

---

## Test 5: Recent Memories - list_recent_memories() 📅

**In Claude Desktop, ask:**
```
Show me my 5 most recent memories.
```

**Expected Behavior:**
- Claude should use `list_recent_memories()` tool
- Should return chronological list
- Should include timestamps

**Expected Results:**
- ACME Corporation conversation (most recent)
- Programming preferences
- Timestamps in ISO format

---

## Test 6: Temporal Search - temporal_search() ⏰

**In Claude Desktop, ask:**
```
What did I know about ACME Corporation as of October 23, 2024?
```

**Expected Behavior:**
- Claude should use `temporal_search()` tool
- Should perform point-in-time query
- Should return facts valid at that date

**Expected Results:**
- Only memories created before/on Oct 23, 2024
- Time-aware result filtering

---

## Test 7: Entity Timeline - get_entity_timeline() 📊

**In Claude Desktop, ask:**
```
Show me the complete timeline for ACME Corporation.
```

**Expected Behavior:**
- Claude should use `get_entity_timeline()` tool
- Should return chronological entity evolution
- Should show all facts/relationships over time

**Expected Results:**
- Revenue fact ($5.2M)
- Growth fact (15% YoY)
- Supplier relationship (Bosch)
- Timestamps for each fact

---

## Test 8: Knowledge Clusters - get_communities() 🕸️

**In Claude Desktop, ask:**
```
What knowledge communities exist in my memory?
```

**Expected Behavior:**
- Claude should use `get_communities()` tool
- Should return community clusters
- Should show entities and relationships

**Expected Results:**
- Programming community (Python, TypeScript)
- Business community (ACME Corp, Bosch)
- Community sizes and member counts

---

## Test 9: Graph Analytics - get_graph_stats() 📈

**In Claude Desktop, ask:**
```
Give me analytics about my knowledge graph.
```

**Expected Behavior:**
- Claude should use `get_graph_stats()` tool
- Should return comprehensive statistics

**Expected Results:**
- Total entities count
- Total facts/edges count
- Community count
- Temporal coverage
- Top entities by connections

---

## Test 10: Multi-Query Orchestration - ask_apex() 🧠 ⭐ THE KILLER FEATURE

**In Claude Desktop, ask:**
```
Tell me everything you know about ACME Corporation - their financials, relationships, history, and patterns.
```

**Expected Behavior:**
- Claude should use `ask_apex()` tool (NOT individual tools)
- Should automatically plan 3-6 queries
- Should execute: search, timeline, relationships, communities, patterns, analytics
- Should synthesize results into narrative answer

**Expected Results:**
- Multi-paragraph narrative response
- Entity overview with metrics
- Key relationships (Bosch 83% supplier)
- Temporal insights (growth trends)
- Strategic insights
- **THIS IS THE FEATURE THAT DIFFERENTIATES APEX FROM OTHER MCP SERVERS**

---

## Test 11: Clear Memories - clear_memories() 🗑️

**WARNING: This deletes data. Test LAST.**

**In Claude Desktop, ask:**
```
Clear all my test memories for ACME Corporation and programming preferences.
```

**Expected Behavior:**
- Claude should use `clear_memories()` tool
- Should ask for confirmation before deleting
- Should return count of deleted episodes

---

## Error Handling Tests 🛡️

### Test E1: Missing Anthropic API Key
**Setup:** Remove ANTHROPIC_API_KEY from .env
**Test:** Ask Claude to use ask_apex()
**Expected:** Should fail gracefully with clear error message

### Test E2: Apex API Down
**Setup:** Stop Apex API (docker-compose down)
**Test:** Try to add_memory()
**Expected:** Should show connection error with helpful message

### Test E3: Invalid Input
**Setup:** Normal operation
**Test:** Search with empty query: "Search for nothing"
**Expected:** Should validate input and show error

---

## Verification Checklist ✅

After completing all tests:

- [ ] All 10 tools executed successfully
- [ ] ask_apex() orchestrated multiple queries automatically
- [ ] Memories stored and retrieved accurately
- [ ] Temporal queries worked correctly
- [ ] Entity timelines showed evolution
- [ ] Communities detected correctly
- [ ] Graph stats returned valid metrics
- [ ] Error handling worked gracefully
- [ ] MCP logs show no errors: `~/Library/Logs/Claude/mcp*.log`

---

## Success Criteria 🎯

**Phase 2 is COMPLETE when:**
1. ✅ All 10 tools tested and working
2. ✅ ask_apex() orchestration demonstrated
3. ✅ Error handling verified
4. ✅ No critical bugs found
5. ✅ Performance acceptable (<5s for orchestration)

---

## Next Steps After Testing ⏭️

Once Phase 2 is complete:
1. Document results in PHASE-2-TESTING-RESULTS.md
2. Proceed to Phase 3: PyPI Publishing Setup
3. Phase 4: TestPyPI Publishing
4. Phase 5: Production PyPI Publishing

---

**Status:** 🟡 READY TO TEST - Restart Claude Desktop and begin Test 1
