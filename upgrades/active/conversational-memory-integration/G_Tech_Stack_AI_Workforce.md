# G's Tech Stack 2025 - AI Workforce Edition
*The Arsenal for Building an AI-Human Hybrid Organization*

## 🤖 AI WORKFORCE PLATFORM (NEW SECTION)

### Agent Infrastructure
- **MCP (Model Context Protocol)** - Custom servers for each domain (fleet, finance, sales)
- **LangGraph** - Stateful agent workflows (COMMIT TO THIS for agent state)
- **Slack SDK** - Agent-human interface (bots, webhooks, commands)
- **Redis Pub/Sub** - Real-time inter-agent communication

### Agent Development
- **Agent Templates** - Reusable agent blueprints (Oscar template → deploy Sarah)
- **Tool Builder Framework** - Custom tool creation for agents
- **Skill System** - Hot-swappable agent capabilities
- **Sub-Agent Orchestration** - Hierarchical agent management

### Agent Operations
- **Rate Limiting** - Prevent API abuse (FastAPI middleware)
- **Secret Management** - GCP Secret Manager for API keys
- **Agent Registry** - Track active agents, capabilities, status
- **Conversation Memory** - Persistent Slack thread context

## 🧠 AI & Agent Development

### Core Framework
- **Claude Code** - AI coding assistant
- **Claude SDK** - Anthropic integration
- **Pydantic AI** - Type-safe agents (THE CHEAT CODE)
- **Archon** - Development framework (task management, memory, database)

### Agent Orchestration (DECISION NEEDED)
Pick ONE primary framework:
- **LangGraph** ⭐ RECOMMENDED - Best for stateful, complex agent workflows
- **AutoGen** - Good for research/experimentation
- **CrewAI** - Good for role-based teams but less flexible

### Observability
- **Langfuse** - LLM tracing and debugging
- **Grafana + Prometheus** - Metrics and monitoring
- **Sentry** - Error tracking
- **Agent-specific dashboards** - Track each AI employee's performance

## 💾 Data Layer

### The Apex Memory System (YOUR Enterprise Platform)
**GitHub:** github.com/rglaubitz/apex-memory-system
**Status:** Production Ready v1.3.0 - 39,499 lines of code, 477 tests

Your parallel multi-database intelligence platform that achieves:
- **<100ms cached queries, <1s complex queries**
- **90% routing accuracy, 90%+ entity extraction**
- **20-25% accuracy improvement over single-database RAG**

**Architecture:**
- **PostgreSQL** - SOPs, procedures, business rules, transaction data
- **Neo4j + Graphiti** - Agent relationships, vendor networks, temporal patterns
- **Qdrant** - Semantic search for similar problems/solutions
- **Redis** - Real-time agent coordination + cache
- **Semantic Router** - Routes queries to right agent AND right database

**AI Workforce Features:**
- Shared memory across ALL agents
- Agent learning persistence
- Cross-functional knowledge graphs
- Temporal reasoning for pattern detection

## 🔄 Workflows & Orchestration

### Core Systems
- **Temporal.io** - Durable workflow execution (agent task orchestration)
- **Apache Kafka** - Event streaming (Samsara + inter-agent events)
- **Redis Pub/Sub** - Lightweight agent-to-agent messaging

### Workflow Patterns
- **Human-in-the-loop** - Approval workflows via Slack
- **Agent collaboration** - Multi-agent task coordination
- **Saga pattern** - Distributed transactions across agents
- **Event sourcing** - Complete audit trail of agent actions

## 🌐 Search & Automation

### Primary Tools
- **Exa** - AI-native search (with research add-on)
- **crawl4ai** - Web scraping and crawling
- **Playwright** - Browser automation
- **Apify** - People/social research only

### Visual Automation (COMMIT TO THIS)
- **n8n** ⭐ MOVE TO PRIMARY - Visual workflow builder for non-technical team
  - Let humans design agent workflows
  - Connect agents without code
  - Visual debugging of agent interactions

## ☁️ Infrastructure & Deployment

### Cloud & Containers
- **Google Cloud Platform (GCP)** - Primary cloud
  - Cloud Run - Agent deployment
  - Secret Manager - API keys
  - Cloud Scheduler - Scheduled agent tasks
  - Vertex AI - Model hosting
- **Docker** - Agent containerization
- **Railway** - Quick agent deployment for testing

### Infrastructure as Code
- **Pulumi** - IaC with Python/TypeScript
- **Agent deployment templates** - Standardized agent setup

### CI/CD & Monitoring
- **GitHub Actions** - CI/CD pipelines
- **GitHub** - Version control, agent code management
- **Grafana** - Agent performance dashboards
- **Prometheus** - Agent metrics collection
- **Sentry** - Agent error tracking

### Agent-Specific Monitoring
- **Agent uptime** - Is Oscar responding?
- **Task completion rate** - How effective is each agent?
- **Cost per agent** - LLM API costs tracking
- **Human escalation rate** - How often agents need help

## 🎨 Frontend Development

### Core Stack
- **React** - UI library
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Component library
- **Vite** - Build tool

### Agent Interfaces
- **Slack Apps** - Primary agent interaction
- **Admin Dashboard** - Agent management UI
- **Performance Dashboard** - Agent metrics visualization

## ⚡ Backend Development

### API Framework
- **FastAPI** - Agent API endpoints + webhooks
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time agent communication
- **httpx** - Agent HTTP client for external APIs

### Authentication & Security
- **Auth0** - Human authentication
- **API Key Management** - Agent authentication
- **Role-Based Access** - Who can command which agents

## 🛠 Development Environment

### Currently Using
- **Cursor** - Primary IDE
- **Docker** - Containers
- **Git/GitHub** - Version control
- **Obsidian** - Knowledge management
- **Slack** - Team communication + AGENT COMMAND CENTER
- **Node.js v25.1.0** - Installed (needs PATH fix)

### Python Development Suite ✅ INSTALLED
- **ruff** - Lightning fast linter/formatter (replaces black, flake8, isort!)
- **uv** - Modern Python package manager (faster than pip)
- **Python 3.14** - Latest Python via Homebrew
- **pip3** - Traditional package manager
- **pandas, numpy** - Data manipulation

### Command Line Arsenal (What Your Agents Use) ✅ INSTALLED
- **grep/sed/awk** - Text processing trinity
- **jq** - JSON manipulation (your agents love this)
- **find/xargs** - File operations
- **curl** - API testing
- **make** - Build automation
- **tree** - Directory visualization
- **rsync/tar/zip** - File management
- **gh** - GitHub CLI for git operations

### Security & Quality Tools ✅ INSTALLED
- **gitleaks** - Scan for secrets in code
- **semgrep** - Static code analysis
- **sentry-cli** - Error tracking deployment

### Database Tools ✅ INSTALLED
- **supabase** - Supabase CLI
- **just** - Command runner for complex tasks

### Document Processing ✅ INSTALLED
- **pypdf, python-docx, python-pptx** - Document manipulation
- **Docling** - Advanced document processing
- **Watchdog** - File system monitoring

### Missing But Recommended
- **ripgrep (rg)** - Faster grep alternative
- **pytest** - Python testing framework
- **mypy** - Type checking
- **pre-commit** - Git hooks for code quality
- **htop** - Better process monitoring

### ⚠️ CRITICAL PATH FIX NEEDED
Run this to enable ALL your tools:
```bash
sh ~/Desktop/fix_all_paths.sh
source ~/.zshrc
```
This adds:
- `/opt/homebrew/bin` - All Homebrew tools
- `/usr/local/bin` - Node.js

### Agent Development Tools
- **Agent Testing Framework** - Test agent responses
- **Prompt Engineering Tools** - Optimize agent prompts
- **Agent Simulator** - Test multi-agent interactions
- **Cost Calculator** - Predict agent running costs

## 📊 MCP Servers (Custom Integrations)

### Domain-Specific MCPs to Build
- **Fleet MCP** - Samsara, ELD, maintenance systems
- **Finance MCP** - QuickBooks, banking, Stripe
- **Sales MCP** - CRM, email, calendar
- **Operations MCP** - Google Drive, internal tools
- **Communication MCP** - Slack, email, SMS

## 🎯 Agent Deployment Strategy

### Phase 1: Oscar (Fleet Manager)
```
Claude SDK + Pydantic AI
Apex Memory System
Temporal workflows
Fleet MCP (Samsara)
Slack bot interface
```

### Phase 2: Sarah (Finance)
```
Reuse Oscar's framework
Add Finance MCP
Connect to QuickBooks
Share Apex memory
```

### Phase 3: Multi-Agent Team
```
LangGraph for orchestration
Agent-to-agent communication
Shared task management
Human approval workflows
```

## 🚨 CRITICAL DECISIONS NEEDED

1. **COMMIT to LangGraph** for agent orchestration (drop AutoGen/CrewAI evaluation)
2. **MOVE n8n to primary** for visual workflow building
3. **ADD MCP development** to immediate priorities
4. **BUILD agent templates** for rapid deployment
5. **DESIGN inter-agent communication** protocol

## 🚀 Next Actions (Updated for AI Workforce)

1. **Deploy Apex to GCP** - Foundation for all agents
2. **Build Oscar v1** - First AI employee
3. **Create Slack bot framework** - Reusable for all agents
4. **Design MCP architecture** - Plan domain integrations
5. **Set up n8n** - Visual workflow designer
6. **Create agent template** - Standardize agent creation

---

*Total Tools: ~50 (added AI workforce specific)*
*Focus: Building AI EMPLOYEES, not tools*
*Vision: AI-Human Hybrid Organization*
