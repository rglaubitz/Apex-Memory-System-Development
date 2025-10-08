# Claude Code Agent System

This directory contains the configuration for Claude Code's agent orchestration system, including 20 specialized agents and MCP (Model Context Protocol) server integration.

## Directory Contents

```
.claude/
├── README.md              # This file
├── agents/                # 20 specialized agent definitions
│   ├── CIO.md            # Chief Information Officer (Review Board)
│   ├── CTO.md            # Chief Technology Officer (Review Board)
│   ├── COO.md            # Chief Operations Officer (Review Board)
│   └── ... (17 more)     # Research team agents
├── .mcp.json             # MCP server configuration
└── settings.local.json   # Local settings (gitignored)
```

## Agent Architecture

### Overview

The Apex Memory System uses **20 specialized agents** organized into functional groups:

1. **C-Suite Executives (3)** - Review Board for quality gates
2. **Research Team (17)** - Continuous knowledge acquisition

### C-Suite Executives (Review Board)

These agents form the **Phase 3.5 Review Board** and validate all execution plans before implementation begins.

#### Chief Information Officer (CIO)

**Role:** Research quality and documentation completeness

**Responsibilities:**
- Validates research quality and source hierarchy compliance
- Enforces Tier 1-5 source standards (official docs, 1.5k+ star repos)
- Reviews dependencies, references, and code examples
- Ensures documentation completeness and citation accuracy

**Tools:** Read, Grep, Glob, WebSearch, WebFetch, Write

**File:** [agents/CIO.md](agents/CIO.md)

#### Chief Technology Officer (CTO)

**Role:** Technical architecture and implementation feasibility

**Responsibilities:**
- Reviews technical architecture and system design
- Validates technology stack choices and API design
- Ensures code quality standards and security considerations
- Evaluates data architecture and database design

**Tools:** Read, Grep, Glob, WebSearch, WebFetch, Write

**File:** [agents/CTO.md](agents/CTO.md)

#### Chief Operations Officer (COO)

**Role:** Operational capacity and goal achievement

**Responsibilities:**
- Reviews operational capacity and execution feasibility
- Validates resource adequacy and timeline realism
- Ensures UX quality and aesthetic polish
- Evaluates user adoption likelihood and business impact

**Tools:** Read, Grep, Glob, Write, TodoWrite

**File:** [agents/COO.md](agents/COO.md)

### Research Team (17 Agents)

Specialized agents for continuous knowledge acquisition and documentation.

#### Core Research Leadership (3)

| Agent | Role | Tools |
|-------|------|-------|
| **research-manager** | Coordinates research efforts, monitors documentation | WebSearch, WebFetch, Bash, Read, Write, Grep |
| **research-coordinator** | Orchestrates multi-agent research tasks | Task, Read, Write, Grep, Bash |
| **documentation-expert** | Maintains documentation quality, structure | Read, Write, Edit, MultiEdit, WebFetch, Grep |

#### Specialized Hunters (3)

| Agent | Role | Tools |
|-------|------|-------|
| **documentation-hunter** | Finds official docs from authoritative sources | WebSearch, WebFetch, Read, Write |
| **github-examples-hunter** | Finds high-quality code (1.5k+ stars) | WebSearch, Read, Write |
| **api-documentation-specialist** | API specs, OpenAPI schemas, GraphQL | WebFetch, Read, Write |

#### Analysts (4)

| Agent | Role | Tools |
|-------|------|-------|
| **deep-researcher** | Complex multi-source research synthesis | WebSearch, WebFetch, Write |
| **standards-researcher** | Technical standards, best practices | WebSearch, WebFetch, Read, Write |
| **company-researcher** | Company-specific competitive analysis | WebSearch, WebFetch, Read, Write |
| **competitive-intelligence-analyst** | Alternative solutions, competitor features | WebSearch, Read, Write |
| **technical-trend-analyst** | Industry trends, emerging tech, deprecations | WebSearch, WebFetch, Read, Write |

#### Quality & Validation (3)

| Agent | Role | Tools |
|-------|------|-------|
| **citation-manager** | Maintains references.md, tracks sources | Read, Write, Edit, WebFetch |
| **technical-validator** | Verifies technical claims, tests hypotheses | Bash, Read |
| **code-quality-validator** | Validates code examples meet quality standards | Bash, Read |

#### Specialized Engineers (2)

| Agent | Role | Tools |
|-------|------|-------|
| **memory-system-engineer** | Knowledge graphs, persistence layers | Bash, Read, Write, Edit, Grep, MultiEdit |
| **pattern-implementation-analyst** | Analyzes and documents code patterns | Read, Write |
| **agent-testing-engineer** | Validates agent behavior, testing strategies | Bash, Read, Write, Task, Grep, TodoWrite |

📋 **[Full Agent Index](agents/README.md)**

## MCP Integration

### What is MCP?

**Model Context Protocol (MCP)** enables Claude Code to connect to external services and databases through standardized servers.

### Configured Servers

The `.mcp.json` configuration includes:

1. **GitHub MCP** - Repository search, file operations, PR management
2. **PostgreSQL MCP** - Direct database queries (read-only)
3. **Exa MCP** - Web search and code context retrieval
4. **Serena MCP** - Semantic code understanding and navigation

### Configuration File

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "..."
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "..."
      }
    }
  }
}
```

**File:** [.mcp.json](.mcp.json)

## Local Settings

**File:** `settings.local.json` (gitignored)

Contains user-specific configuration:
- API keys and credentials
- Local file paths
- User preferences
- Environment-specific settings

**Security:** This file is excluded from version control via `.gitignore`

## Usage Guidelines

### When to Use Agents

**C-Suite Executives (Review Board):**
- Automatically invoked during Phase 3.5 (Review Board)
- Can be manually invoked for quality validation of plans
- All 3 must approve before Phase 4 (Implementation)

**Research Team:**
- Invoked as needed for specific research tasks
- Can work in parallel for comprehensive research
- Coordinate through research-manager or research-coordinator

### Agent Invocation

Agents are invoked through Claude Code's Task tool:

```markdown
Use the research-manager agent to coordinate research on GraphRAG systems
Use the CIO agent to validate research quality of the execution plan
Use the github-examples-hunter to find vector database examples
```

### Quality Gates

**Phase 3.5 Review Board:**
1. COO reviews operational feasibility
2. CIO reviews research quality
3. CTO reviews technical architecture
4. All must approve (APPROVED or APPROVED_WITH_CONCERNS)
5. REJECTED verdict blocks implementation

## Development

### Adding New Agents

1. Create agent definition in `agents/[agent-name].md`
2. Follow existing agent template structure
3. Define role, responsibilities, and tool access
4. Update this README with agent details
5. Update `agents/README.md` index

### Modifying MCP Configuration

1. Edit `.mcp.json` for new servers
2. Test configuration locally
3. Document in this README
4. DO NOT commit sensitive credentials

### Local Settings

1. Copy `settings.local.json.example` (if exists)
2. Add your local configuration
3. Never commit `settings.local.json` (gitignored)

## References

- **Claude Code Documentation:** https://docs.claude.com/en/docs/claude-code
- **MCP Protocol:** https://modelcontextprotocol.io/
- **Agent System Design:** Based on multi-agent orchestration patterns
- **Review Board Process:** Inspired by C-suite approval workflows

---

**Note:** This configuration is specific to the Apex Memory System Development workspace and may reference agents, tools, and patterns custom to this project.
