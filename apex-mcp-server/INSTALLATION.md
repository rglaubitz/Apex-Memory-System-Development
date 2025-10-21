# Apex MCP Server - Installation Guide

Complete installation instructions for the Apex Model Context Protocol server.

## Prerequisites

### 1. Apex Memory System

The Apex API must be running locally:

```bash
cd /path/to/apex-memory-system

# Start all services (Neo4j, PostgreSQL, Qdrant, Redis, Grafana)
cd docker && docker-compose up -d

# Start Apex API
python -m uvicorn apex_memory.main:app --reload --port 8000
```

Verify it's running:
```bash
curl http://localhost:8000/docs
```

You should see the FastAPI Swagger UI.

### 2. Python 3.11+

```bash
python3 --version
# Should show 3.11.x or higher
```

### 3. Anthropic API Key

Required for `ask_apex()` feature:
1. Create account at https://console.anthropic.com
2. Generate API key
3. Save for later use

---

## Installation Methods

### Method 1: One-Click Install (Recommended)

```bash
cd apex-mcp-server
./install-apex-mcp.sh
```

This script will:
- ✅ Check Python version
- ✅ Verify Apex API is running
- ✅ Install apex-mcp-server package
- ✅ Prompt for Anthropic API key
- ✅ Configure Claude Desktop automatically
- ✅ Create .env file

**After installation:**
1. Restart Claude Desktop
2. Test by asking Claude to "Remember that I prefer Python"

---

### Method 2: Manual Installation

#### Step 1: Install Package

```bash
cd apex-mcp-server
pip install -e .
```

For development (with test dependencies):
```bash
pip install -e ".[dev]"
```

#### Step 2: Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

Required variables:
```env
APEX_API_URL=http://localhost:8000
ANTHROPIC_API_KEY=sk-ant-api03-...
```

#### Step 3: Configure Claude Desktop

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
```

**Linux:**
```bash
cd ~/.config/Claude/
```

Edit or create `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "apex-memory": {
      "command": "python3",
      "args": ["-m", "apex_mcp_server.server"],
      "env": {
        "APEX_API_URL": "http://localhost:8000",
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Step 4: Restart Claude Desktop

Completely quit and restart Claude Desktop for changes to take effect.

---

## Verification

### 1. Test MCP Server Directly

```bash
python -m apex_mcp_server.server
```

Should start without errors. Press Ctrl+C to stop.

### 2. Check Claude Desktop Logs

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

Look for:
```
Apex MCP Server starting...
Tools registered: add_memory, search_memory, ask_apex, ...
```

### 3. Test in Claude Desktop

Try these commands:

```
You: "Remember that I prefer Python for backend development"
Claude: ✅ Memory stored!
        Entities extracted: Python, Backend Development
        Relationships: User → PREFERS → Python

You: "What do you remember about my programming preferences?"
Claude: [Searches and retrieves your preference]

You: "Tell me everything you know about ACME Corporation"
Claude: [Uses ask_apex() to orchestrate multiple queries and synthesize answer]
```

---

## Troubleshooting

### Issue: "Apex API not detected"

**Solution:**
```bash
# Check if Apex API is running
curl http://localhost:8000/docs

# If not, start it:
cd /path/to/apex-memory-system
python -m uvicorn apex_memory.main:app --reload --port 8000
```

### Issue: "ask_apex() not working"

**Solution:**
```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Or check .env file
cat apex-mcp-server/.env | grep ANTHROPIC

# Test API key:
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Issue: Claude Desktop doesn't see Apex tools

**Solution:**
1. Check config location:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Verify JSON syntax:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .
   ```

3. Check for errors in logs:
   ```bash
   tail -100 ~/Library/Logs/Claude/mcp*.log
   ```

4. **Completely quit and restart Claude Desktop** (not just close window)

### Issue: Import errors

**Solution:**
```bash
# Reinstall package
cd apex-mcp-server
pip uninstall apex-mcp-server
pip install -e .

# Verify installation
python -c "import apex_mcp_server; print(apex_mcp_server.__version__)"
```

---

## Updating

```bash
cd apex-mcp-server
git pull  # If using git
pip install -e . --upgrade
```

Restart Claude Desktop after updating.

---

## Uninstalling

```bash
# Remove package
pip uninstall apex-mcp-server

# Remove Claude Desktop config
# Edit ~/Library/Application Support/Claude/claude_desktop_config.json
# Remove the "apex-memory" entry

# Restart Claude Desktop
```

---

## Advanced Configuration

### Custom API URL

If Apex API runs on a different port:

```env
APEX_API_URL=http://localhost:9000
```

### Multi-Tenant Mode

Use different user/group IDs:

```env
DEFAULT_USER_ID=user-123
DEFAULT_GROUP_ID=team-marketing
```

### Adjust ask_apex() Limits

```env
ASK_APEX_MAX_QUERIES=10  # Allow more queries (default: 6)
ASK_APEX_MAX_SYNTHESIS_TOKENS=3000  # Longer answers
```

---

## Next Steps

- Read [EXAMPLES.md](EXAMPLES.md) for usage examples
- See [README.md](README.md) for feature overview
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
