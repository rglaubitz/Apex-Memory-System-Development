# Apex MCP Server - Troubleshooting Guide

Common issues and solutions when using Apex MCP Server with Claude Desktop.

## Installation Issues

### Error: "Python 3.11+ required"

**Problem:** Older Python version installed

**Solution:**
```bash
# Check version
python3 --version

# Install Python 3.11+ (macOS with Homebrew)
brew install python@3.11

# Or use pyenv
pyenv install 3.11.7
pyenv global 3.11.7
```

---

### Error: "Apex API not detected"

**Problem:** Apex Memory System API isn't running

**Solution:**
```bash
# Start Apex services
cd /path/to/apex-memory-system
cd docker && docker-compose up -d

# Start API
python -m uvicorn apex_memory.main:app --reload --port 8000

# Verify
curl http://localhost:8000/docs
```

---

## Claude Desktop Integration

### Claude Desktop doesn't see Apex tools

**Symptoms:**
- Claude responds normally but can't use memory tools
- No error messages

**Solutions:**

1. **Verify config file location:**
   ```bash
   # macOS
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Linux
   cat ~/.config/Claude/claude_desktop_config.json
   ```

2. **Check JSON syntax:**
   ```bash
   # Should show formatted JSON with no errors
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .
   ```

3. **Completely restart Claude Desktop:**
   - Quit Claude Desktop (⌘+Q on macOS)
   - Wait 5 seconds
   - Restart Claude Desktop
   - **Not** just closing the window - full quit

4. **Check logs:**
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log

   # Linux
   tail -f ~/.config/Claude/logs/mcp*.log
   ```

   Look for:
   ```
   Apex MCP Server starting...
   Tools registered: ...
   ```

---

### Error in MCP logs: "ModuleNotFoundError: apex_mcp_server"

**Problem:** Package not installed or not in Python path

**Solution:**
```bash
cd apex-mcp-server
pip install -e .

# Verify
python -c "import apex_mcp_server; print('OK')"
```

---

### Error: "Connection refused to localhost:8000"

**Problem:** Apex API not running or on different port

**Solutions:**

1. **Check if API is running:**
   ```bash
   curl http://localhost:8000/docs
   ```

2. **Check API is on port 8000:**
   ```bash
   lsof -i :8000
   # Should show python process
   ```

3. **If API runs on different port, update config:**
   ```json
   {
     "mcpServers": {
       "apex-memory": {
         "env": {
           "APEX_API_URL": "http://localhost:9000"
         }
       }
     }
   }
   ```

---

## ask_apex() Issues

### ask_apex() returns error about API key

**Problem:** Anthropic API key not configured

**Solution:**
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Set in Claude Desktop config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Add under "env":
{
  "mcpServers": {
    "apex-memory": {
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-..."
      }
    }
  }
}

# Restart Claude Desktop
```

---

### ask_apex() returns empty or incomplete answers

**Symptoms:**
- Partial answers
- Missing insights
- Low confidence scores

**Possible Causes & Solutions:**

1. **Limited data in knowledge graph:**
   - Add more memories first
   - ask_apex() works best with rich graph data

2. **Increase query limit:**
   ```json
   {
     "env": {
       "ASK_APEX_MAX_QUERIES": "10"
     }
   }
   ```

3. **Check API responses:**
   Enable raw data to debug:
   ```
   You: "Tell me about ACME (include raw data)"
   ```

---

## Memory Storage Issues

### Entities not being extracted

**Symptoms:**
- `entities_extracted: []`
- No relationships created

**Solutions:**

1. **Check Graphiti is enabled:**
   ```bash
   curl http://localhost:8000/docs
   # Look for /api/v1/messages endpoints
   ```

2. **Verify Neo4j is running:**
   ```bash
   docker ps | grep neo4j
   # Should show running neo4j container
   ```

3. **Check OpenAI API key** (for Graphiti LLM):
   ```bash
   # In apex-memory-system
   cat .env | grep OPENAI_API_KEY
   ```

---

### Search returns no results

**Symptoms:**
- `result_count: 0`
- Empty results array

**Solutions:**

1. **Verify data was stored:**
   ```bash
   # Check Neo4j
   docker exec -it neo4j cypher-shell -u neo4j -p apexmemory2024
   # Run: MATCH (n) RETURN count(n);
   ```

2. **Try different search terms:**
   ```
   # Instead of specific names
   You: "Search for ACME"

   # Try broader terms
   You: "Search for customers"
   You: "Search for companies"
   ```

3. **Check cache:**
   Disable cache to force fresh search:
   ```
   You: "Search for ACME (bypass cache)"
   ```

---

## Performance Issues

### Slow responses (>10 seconds)

**Possible Causes & Solutions:**

1. **Apex API is slow:**
   ```bash
   # Test API directly
   time curl http://localhost:8000/api/v1/query \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "limit": 10}'
   ```

2. **Databases not optimized:**
   ```bash
   # Check Neo4j indexes
   docker exec neo4j cypher-shell -u neo4j -p apexmemory2024 "SHOW INDEXES"

   # Rebuild if needed
   curl -X POST http://localhost:8000/api/v1/maintenance/rebuild-indices
   ```

3. **ask_apex() doing too many queries:**
   Reduce max queries:
   ```json
   {
     "env": {
       "ASK_APEX_MAX_QUERIES": "3"
     }
   }
   ```

---

## Data Inconsistencies

### Different results from ask_apex() vs search_memory()

**This is expected!**

- `search_memory()` = Single database query
- `ask_apex()` = Multi-query orchestration + synthesis

ask_apex() may return more comprehensive answers by combining:
- Search results
- Graph traversal
- Temporal context
- Pattern detection
- Analytics

---

### Memories disappearing

**Solutions:**

1. **Check if accidentally cleared:**
   Memories can only be deleted explicitly via `clear_memories()`

2. **Check database health:**
   ```bash
   curl http://localhost:8000/api/v1/analytics/graph-health
   ```

3. **Verify backups:**
   ```bash
   # Neo4j backup
   docker exec neo4j neo4j-admin dump --to=/backups/neo4j-backup.dump
   ```

---

## Testing & Debugging

### Run tests to verify functionality

```bash
cd apex-mcp-server

# Run all tests
pytest

# Run specific test file
pytest tests/test_ask_apex.py -v

# Run with coverage
pytest --cov=apex_mcp_server --cov-report=html
```

---

### Enable debug logging

```python
# In server.py, change log level
logging.basicConfig(level=logging.DEBUG)
```

Then restart and check logs.

---

### Test MCP server directly (bypass Claude Desktop)

```bash
# Start server
python -m apex_mcp_server.server

# Should show:
# Apex MCP Server starting...
# Tools registered: ...
```

Press Ctrl+C to stop.

---

## Getting Help

### Check logs

**macOS:**
```bash
# MCP logs
tail -100 ~/Library/Logs/Claude/mcp*.log

# Apex API logs
# (wherever you're running uvicorn)
```

**Linux:**
```bash
tail -100 ~/.config/Claude/logs/mcp*.log
```

### Collect diagnostic info

```bash
# System info
python --version
pip show apex-mcp-server

# Apex API status
curl http://localhost:8000/docs

# Test API call
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 1}'

# Database status
docker ps | grep -E "neo4j|postgres|qdrant|redis"
```

### Report issues

Include:
1. Error messages from logs
2. Steps to reproduce
3. Python version
4. Apex API version
5. OS (macOS/Linux)

---

## Common Patterns

### "It worked yesterday, now it doesn't"

**Checklist:**
1. ✅ Restart Apex API
2. ✅ Restart Claude Desktop (full quit)
3. ✅ Check databases are running (`docker ps`)
4. ✅ Verify config file unchanged
5. ✅ Check API key hasn't expired

---

### "ask_apex() is amazing but slow"

**This is by design!**

ask_apex() orchestrates 3-6 queries + LLM synthesis:
- Query planning: ~1-2s
- Execute queries: ~2-5s (depends on data)
- Synthesis: ~2-4s

**Total: 5-11 seconds** is normal for comprehensive answers.

To speed up:
- Reduce `ASK_APEX_MAX_QUERIES`
- Use simpler questions
- Use `search_memory()` for quick lookups

---

## Still Having Issues?

1. Read [INSTALLATION.md](INSTALLATION.md) - verify setup
2. Check [EXAMPLES.md](EXAMPLES.md) - see working examples
3. Review [README.md](README.md) - understand features
4. Test Apex API directly - isolate the issue

**MCP vs Apex API:**
- If Apex API works directly → MCP config issue
- If Apex API fails → Backend issue (see apex-memory-system docs)
