#!/bin/bash
set -e

# Apex MCP Server Installation Script
# Installs the MCP server and configures Claude Desktop

echo "🚀 Apex MCP Server Installation"
echo "================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python 3.11+ required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python version OK ($PYTHON_VERSION)"

# Check if Apex API is running
echo ""
echo "Checking Apex Memory System API..."
if curl -s -f http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Apex API is running at http://localhost:8000"
else
    echo "⚠️  Warning: Apex API not detected at http://localhost:8000"
    echo "   Make sure to start it before using the MCP server:"
    echo "   cd apex-memory-system && docker-compose up -d && uvicorn apex_memory.main:app --reload"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install apex-mcp-server
echo ""
echo "Installing apex-mcp-server..."
pip install -e .
echo "✅ apex-mcp-server installed"

# Ask for Anthropic API key
echo ""
echo "Anthropic API key is required for ask_apex() feature."
read -p "Enter your Anthropic API key (or press Enter to skip): " ANTHROPIC_KEY
echo ""

# Determine Claude Desktop config location
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "Please manually configure Claude Desktop using claude_desktop_config.json as a template."
    exit 1
fi

CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Create Claude config directory if needed
mkdir -p "$CLAUDE_CONFIG_DIR"

# Check if config already exists
if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "⚠️  Claude Desktop config already exists at:"
    echo "   $CLAUDE_CONFIG_FILE"
    echo ""
    read -p "Do you want to backup and replace it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        BACKUP_FILE="$CLAUDE_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$CLAUDE_CONFIG_FILE" "$BACKUP_FILE"
        echo "✅ Backup created: $BACKUP_FILE"
    else
        echo ""
        echo "Please manually add the apex-memory server to your Claude config."
        echo "Template available in: claude_desktop_config.json"
        exit 0
    fi
fi

# Create config
cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "apex-memory": {
      "command": "python3",
      "args": [
        "-m",
        "apex_mcp_server.server"
      ],
      "env": {
        "APEX_API_URL": "http://localhost:8000",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_KEY:-your-api-key-here}",
        "DEFAULT_USER_ID": "default",
        "DEFAULT_GROUP_ID": "default",
        "ASK_APEX_MAX_QUERIES": "6"
      }
    }
  }
}
EOF

echo "✅ Claude Desktop configured at: $CLAUDE_CONFIG_FILE"

# Create .env file
echo ""
echo "Creating .env file..."
cat > .env << EOF
# Apex Memory System Configuration
APEX_API_URL=http://localhost:8000
APEX_API_TIMEOUT=30

# LLM Configuration (for ask_apex() orchestration)
ANTHROPIC_API_KEY=${ANTHROPIC_KEY:-your-anthropic-api-key-here}
ANTHROPIC_MODEL=claude-3-7-sonnet-20250219

# Optional: User/Group ID for multi-tenant support
DEFAULT_USER_ID=default
DEFAULT_GROUP_ID=default

# Optional: ask_apex() configuration
ASK_APEX_MAX_QUERIES=6
ASK_APEX_MAX_SYNTHESIS_TOKENS=2000
ASK_APEX_ENABLE_CACHING=true
EOF

echo "✅ .env file created"

# Final instructions
echo ""
echo "================================"
echo "✅ Installation Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop"
echo "2. Start Apex API if not already running:"
echo "   cd /path/to/apex-memory-system"
echo "   docker-compose up -d"
echo "   python -m uvicorn apex_memory.main:app --reload"
echo ""
echo "3. Test in Claude Desktop:"
echo "   Try: 'Remember that I prefer Python for backend development'"
echo "   Or:  'Tell me what you know about ACME Corporation'"
echo ""
echo "Troubleshooting:"
echo "- Check logs: ~/Library/Logs/Claude/mcp*.log (macOS)"
echo "- Verify API: curl http://localhost:8000/docs"
echo "- Test MCP: python -m apex_mcp_server.server"
echo ""
echo "Documentation: README.md"
echo ""
