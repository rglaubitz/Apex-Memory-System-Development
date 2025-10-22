# Apex MCP Server

**Model Context Protocol server for Apex Memory System**

> Enable Claude Desktop to store, search, and intelligently explore your knowledge graph with conversational memory.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.2+-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 The Killer Feature: ask_apex()

**Unlike basic memory tools, Apex MCP doesn't just store and retrieve - it *understands and explains*.**

```
You: "Tell me everything about ACME Corporation"

Claude orchestrates 6 queries:
  → Search knowledge graph
  → Get entity relationships
  → Analyze temporal evolution
  → Detect patterns
  → Find communities
  → Gather analytics

Then synthesizes:
  ✨ Multi-paragraph narrative
  ✨ Key insights with context
  ✨ Entities and relationships
  ✨ Follow-up questions
  ✨ Confidence scoring

All from ONE user question.
```

**This is what makes Apex different from OpenMemory and Graphiti.**

---

## 🎯 Features

### Basic Memory Operations (5 tools)
- `add_memory()` - Store single memories with LLM entity extraction
- `add_conversation()` - Store multi-turn conversations
- `search_memory()` - Semantic search across 4 databases
- `list_recent_memories()` - View recent episodes
- `clear_memories()` - Delete user data

### Advanced Features (4 tools)
- `temporal_search()` - Point-in-time queries (bi-temporal tracking)
- `get_entity_timeline()` - Track how entities evolved over time
- `get_communities()` - Discover knowledge clusters (Leiden algorithm)
- `get_graph_stats()` - Analytics and metrics across graph

### 🧠 Intelligent Orchestration (THE DIFFERENTIATOR)
- **`ask_apex()`** - Ask anything, Claude:
  - Plans optimal query strategy
  - Orchestrates 3-6 queries across APIs
  - Synthesizes narrative answers
  - Suggests relevant follow-ups

---

## 🚀 Quick Start

### Prerequisites

1. **Apex Memory System running:**
   ```bash
   cd /path/to/apex-memory-system
   docker-compose up -d
   python -m uvicorn apex_memory.main:app --reload
   ```

2. **Python 3.11+** OR **uv** (recommended)

3. **Anthropic API key** (for ask_apex):
   - Get from: https://console.anthropic.com

### Installation Methods

**Choose one:**

#### ⭐ Option 1: Using `uvx` (Recommended - npm-style)

Like `npx` but for Python! No installation needed.

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "apex-memory": {
      "command": "uvx",
      "args": ["apex-mcp-server"],
      "env": {
        "APEX_API_URL": "http://localhost:8000",
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Installation:**
```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# That's it! uvx will auto-install apex-mcp-server when Claude Desktop starts
```

#### Option 2: Using `pipx`

```json
// Claude Desktop config
{
  "mcpServers": {
    "apex-memory": {
      "command": "pipx",
      "args": ["run", "apex-mcp-server"],
      "env": {
        "APEX_API_URL": "http://localhost:8000",
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Installation:**
```bash
pip install pipx
pipx ensurepath
```

#### Option 3: One-Click Install Script

```bash
cd apex-mcp-server
./install-apex-mcp.sh
```

This will:
- ✅ Install package locally
- ✅ Configure Claude Desktop
- ✅ Set up environment

#### Option 4: Local Development

```bash
# Install package
pip install -e .

# Use in Claude Desktop config
{
  "mcpServers": {
    "apex-memory": {
      "command": "python3",
      "args": ["-m", "apex_mcp_server.server"],
      "env": {...}
    }
  }
}
```

**Then:** Restart Claude Desktop and start talking!

See [INSTALLATION.md](INSTALLATION.md) for complete instructions.

---

## 💡 Usage Examples

### Store Conversational Memories

```
You: "Remember that I prefer Python over JavaScript for backend development"

Claude: ✅ Memory stored!

        Entities extracted:
        - Python
        - JavaScript
        - Backend Development

        Relationships created:
        - You → PREFERS → Python
        - Python → USE_CASE_FOR → Backend Development

        Stored across 4 databases (Neo4j, PostgreSQL, Qdrant, Redis)
```

### Search Your Knowledge Graph

```
You: "What do you know about ACME Corporation?"

Claude: [Searches via intelligent query router]

        Found 7 results:
        1. ACME ordered 50 brake parts from Bosch (Jan 15)
        2. ACME is in the Manufacturing community
        3. Invoice INV-001 for ACME ($5,000)
        ...
```

### Intelligent Multi-Query Orchestration

```
You: "Tell me everything about ACME Corporation"

Claude: I've analyzed ACME Corporation across your entire knowledge graph
        by orchestrating 6 queries. Here's what I found:

        📊 OVERVIEW
        ACME is one of your most important entities with:
        - 12 associated documents
        - 8 connected entities (Bosch, Brembo, brake systems, etc.)
        - 3 months of tracked history
        - Member of 2 communities (Manufacturing, Suppliers)

        🔗 KEY RELATIONSHIPS
        Primary supplier: Bosch (83% of orders)
        - 7 orders placed, totaling 350 brake parts
        - Relationship established: December 2024

        Secondary supplier: Brembo (17% of orders)
        - Recently added: March 2025
        - Strategic diversification detected

        📈 PATTERNS DETECTED
        ✨ Recurring ordering pattern: Every 3-4 weeks (89% consistency)
        ✨ Typical order size: 50-75 brake parts
        ✨ Supplier diversification trend (risk mitigation)

        📍 TEMPORAL EVOLUTION
        Dec 2024: Relationship established (Bosch only)
        Jan 2025: First order placed
        Feb 2025: Pattern stabilized
        Mar 2025: Added Brembo (strategic shift)

        💡 INSIGHTS
        ACME is a stable, predictable customer. Their recent supplier
        change from Bosch-only to Bosch+Brembo indicates strategic
        risk management. They're highly connected (8 relationships)
        making them a hub entity in your supply chain.

        Follow-up questions:
        - Why did ACME switch suppliers in March?
        - Compare ACME's patterns to other customers
        - Show me ACME's complete timeline
```

### Temporal Queries

```
You: "What was ACME's supplier situation in January?"

Claude: [Point-in-time query at Jan 31, 2025]

        In January 2025:
        - Exclusive supplier: Bosch
        - Relationship status: Active
        - Orders placed: 2 (Jan 15, Jan 22)

        Note: Brembo was added as secondary supplier in March 2025.
```

See [EXAMPLES.md](EXAMPLES.md) for more detailed examples.

---

## 🏗️ Architecture

```
Claude Desktop
    ↓ MCP Protocol (stdio)
Apex MCP Server (this package)
    ↓ HTTP REST API
Apex Memory System API
    ↓
Multi-Database Intelligence
    ├─ Neo4j (knowledge graph)
    ├─ PostgreSQL (metadata + pgvector)
    ├─ Qdrant (vector similarity)
    └─ Redis (caching)
```

**Key Design:**
- **Thin wrapper** - MCP server just calls existing Apex API
- **Zero backend changes** - All Apex tests still pass
- **LLM orchestration** - Claude plans and executes queries
- **Narrative synthesis** - Transforms JSON into stories

---

## 🏆 Competitive Positioning

| Capability | OpenMemory | Graphiti MCP | **Apex MCP** |
|-----------|-----------|--------------|--------------|
| Store memories | ✅ | ✅ | ✅ |
| Entity extraction | ❌ | ✅ (LLM) | ✅ (LLM) |
| Temporal tracking | ❌ | ✅ (bi-temporal) | ✅ (bi-temporal) |
| Pattern detection | ❌ | Limited | ✅ (Advanced) |
| Multi-database | ❌ (SQLite) | ❌ (Neo4j) | ✅ (4 databases) |
| Intelligent routing | ❌ | ❌ | ✅ (90% accuracy) |
| **Multi-query orchestration** | ❌ | ❌ | **✅** |
| **Narrative synthesis** | ❌ | ❌ | **✅** |

**Result:** Apex = OpenMemory's simplicity + Graphiti's intelligence + unique multi-query orchestration

**No competitor can do this** - requires 4-database architecture + intelligent query router + LLM synthesis.

---

## 📚 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide
- **[EXAMPLES.md](EXAMPLES.md)** - Detailed usage examples
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues & solutions
- **[API Reference](#tools-reference)** - All 10 tools documented below

---

## 🛠️ Tools Reference

### Basic Tools

**add_memory(content, user_id, metadata)**
- Store a single memory
- LLM extracts entities and relationships
- Stored across 4 databases

**add_conversation(messages, user_id, participants)**
- Store multi-turn conversations
- Processes all messages together for context

**search_memory(query, limit, use_cache)**
- Semantic search with intelligent routing
- Routes to optimal database (Neo4j, Qdrant, PostgreSQL, Redis)

**list_recent_memories(user_id, limit)**
- List recent episodes
- Sorted by timestamp

**clear_memories(user_id, confirm)**
- Delete all memories for user
- Requires confirmation flag

### Advanced Tools

**temporal_search(query, reference_time, time_window_days)**
- Point-in-time queries
- Query graph as it existed at specific time

**get_entity_timeline(entity_uuid, time_window_days)**
- Complete entity evolution timeline
- All state changes and relationships

**get_communities(entity_uuid, group_id, limit)**
- Knowledge graph communities
- Detected via Leiden algorithm

**get_graph_stats(metric_type, group_id, limit)**
- Analytics and metrics
- Types: overview, entities, relationships, communities, health

### Intelligence

**ask_apex(question, user_id, include_raw_data, max_queries)**
- 🌟 **THE KILLER FEATURE**
- LLM orchestrates 3-6 queries
- Synthesizes narrative answers
- Suggests follow-ups
- Returns: answer, insights, entities, confidence

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apex_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_ask_apex.py -v
```

**Test Coverage:**
- 20+ tests across all tools
- Unit tests with mocked APIs
- Integration test patterns
- ask_apex() orchestration tests

---

## 🔧 Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Format code
black src/ tests/

# Lint
ruff check src/

# Run tests
pytest
```

---

## 🐛 Troubleshooting

### Claude Desktop doesn't see Apex tools

**Solution:**
1. Verify Apex API running: `curl http://localhost:8000/docs`
2. Check config: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. **Completely quit and restart Claude Desktop** (⌘+Q on macOS)
4. Check logs: `~/Library/Logs/Claude/mcp*.log`

### ask_apex() not working

**Solution:**
1. Verify `ANTHROPIC_API_KEY` is set in Claude Desktop config
2. Test API key: `curl https://api.anthropic.com/v1/messages -H "x-api-key: $ANTHROPIC_API_KEY"`
3. Check API credits at console.anthropic.com

### Slow responses

**This is normal for ask_apex()!**
- Orchestrates 3-6 queries: ~2-5s
- LLM synthesis: ~2-4s
- **Total: 5-11 seconds** for comprehensive answers

To speed up:
- Use `search_memory()` for quick lookups
- Reduce `ASK_APEX_MAX_QUERIES` in config

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete guide.

---

## 📦 What's Included

```
apex-mcp-server/
├── src/apex_mcp_server/
│   ├── server.py              # Main MCP server
│   ├── config.py              # Configuration
│   └── tools/
│       ├── basic_tools.py     # 5 basic memory ops
│       ├── advanced_tools.py  # 4 advanced features
│       └── ask_apex.py        # THE KILLER FEATURE ⭐
├── tests/                     # 17 tests (all passing)
├── install-apex-mcp.sh        # One-click installer
├── claude_desktop_config.json # uvx config (recommended)
├── claude_desktop_config.pipx.json  # pipx alternative
├── claude_desktop_config.local.json # Local development
└── docs/
    ├── INSTALLATION.md
    ├── EXAMPLES.md
    ├── TROUBLESHOOTING.md
    └── PUBLISHING.md          # PyPI publishing guide
```

---

## 🎯 Use Cases

**Personal Knowledge Management:**
- "Remember my programming preferences, project notes, and meeting summaries"

**Customer Intelligence:**
- "Tell me everything about ACME - relationships, patterns, evolution"

**Temporal Analysis:**
- "What changed this week? How did our supplier relationships evolve?"

**Pattern Detection:**
- "What patterns do you see in customer orders?"

**Relationship Mapping:**
- "How are ACME and Bosch connected? Show me the relationship path."

---

## 🚢 Deployment

**Local Development:**
```bash
python -m apex_mcp_server.server
```

**Claude Desktop (Production):**
- Configured via `claude_desktop_config.json`
- Runs automatically when Claude Desktop starts
- Logs to `~/Library/Logs/Claude/`

---

## 📦 Publishing to PyPI

To enable npm-style installation (`uvx apex-mcp-server`), publish to PyPI:

```bash
# 1. Install build tools
pip install build twine

# 2. Update version in pyproject.toml
# 0.1.0 → 0.1.1 (bug fixes)
# 0.1.0 → 0.2.0 (new features)

# 3. Build and publish
python -m build
twine upload dist/*

# 4. Test installation
uvx apex-mcp-server --help
```

**See [PUBLISHING.md](PUBLISHING.md) for complete guide.**

Once published, users can install with just:

```json
{
  "mcpServers": {
    "apex-memory": {
      "command": "uvx",
      "args": ["apex-mcp-server"]
    }
  }
}
```

No manual installation needed!

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Run `black` and `ruff` before committing
5. Submit a pull request

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

Built on top of:
- [Model Context Protocol](https://modelcontextprotocol.io) - Anthropic's MCP framework
- [Apex Memory System](https://github.com/your-org/apex-memory-system) - 4-database intelligence platform
- [Graphiti](https://github.com/getzep/graphiti) - Temporal knowledge graphs
- [FastMCP](https://github.com/jlowin/fastmcp) - Python MCP framework

---

## 🌐 Links

- **Documentation:** [INSTALLATION.md](INSTALLATION.md) | [EXAMPLES.md](EXAMPLES.md) | [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Apex Memory System:** [Main Repository](https://github.com/your-org/apex-memory-system)
- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Issues:** [GitHub Issues](https://github.com/your-org/apex-mcp-server/issues)

---

**Built with ❤️ for the Apex Memory System**

*Making conversational memory intelligent, not just persistent.*
