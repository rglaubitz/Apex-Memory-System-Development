# Agent Registry

**Purpose:** Central registry of all AI agents in the OpenHaul system
**Last Updated:** 2025-11-14
**Status:** Living document - update when adding new agents

---

## Overview

The Conversational Memory Integration system supports multiple specialized agents sharing the same knowledge infrastructure. Each agent has:
- Unique agent ID (lowercase identifier)
- Domain specialization
- Agent-specific namespaces in databases
- Dedicated collections/schemas/labels

**Design Philosophy:** "One knowledge base, multiple specialized access patterns"

---

## Active Agents

### Oscar - Fleet Manager (Primary Agent)

**Agent ID:** `oscar`
**Status:** ✅ Active (Phase 1)
**Domain:** Fleet Management & Operations
**Implementation:** Phase 1 (Weeks 1-8)

**Responsibilities:**
- Truck fleet monitoring and management
- Maintenance scheduling and tracking
- Load assignment and route optimization
- Equipment performance analysis
- Driver communication and support

**Data Scope:**
- Fleet entities (trucks, trailers, equipment)
- Maintenance records and schedules
- Load assignments and deliveries
- Route performance metrics
- Equipment specifications and history

**Database Namespaces:**
- **Redis:** `oscar:*` (e.g., `oscar:conversation:123:context`)
- **Qdrant:** `oscar_fleet_knowledge` collection
- **PostgreSQL:** `oscar` schema (Phase 2)
- **Neo4j:** `:Oscar_Domain` label (Phase 2)

**Example Queries:**
- "What trucks need maintenance this week?"
- "Show me Truck 247's service history"
- "Which drivers are available for Chicago-Dallas runs?"
- "What's the average fuel efficiency for our Freightliner fleet?"

---

## Planned Agents

### Sarah - CFO / Finance Agent

**Agent ID:** `sarah`
**Status:** 📝 Planned (Phase 2 - Weeks 9-14)
**Domain:** Financial Management & Analysis
**Implementation:** Phase 2 (when multi-agent specialization activated)

**Responsibilities:**
- Invoice analysis and vendor management
- Cost tracking and budget monitoring
- Overcharge detection (e.g., Penske pattern detection)
- Financial reporting and forecasting
- Vendor negotiation support

**Data Scope:**
- Financial entities (invoices, vendors, payments)
- Cost patterns and overcharge detection
- Budget tracking and variance analysis
- Vendor performance metrics
- Financial forecasts and reports

**Database Namespaces:**
- **Redis:** `sarah:*` (e.g., `sarah:invoice:456:analysis`)
- **Qdrant:** `sarah_financial_knowledge` collection
- **PostgreSQL:** `sarah` schema
- **Neo4j:** `:Sarah_Domain` label

**Example Queries:**
- "Show me all Penske invoices from last quarter"
- "Has Vendor X been overcharging us?"
- "What's our average fuel cost per mile?"
- "Forecast next month's operating expenses"

**Cross-Domain Insights:**
- Maintenance costs (from Oscar) → Budget impact (Sarah analysis)
- Rental overcharges (Sarah detection) → Equipment availability (Oscar context)

---

### Maya - Sales / CRM Agent

**Agent ID:** `maya`
**Status:** 📝 Planned (Phase 2 - Weeks 9-14)
**Domain:** Sales, Customer Management & Pricing
**Implementation:** Phase 2 (when multi-agent specialization activated)

**Responsibilities:**
- Customer relationship management
- Quote generation and pricing optimization
- Lane performance analysis
- Deal tracking and win/loss analysis
- Customer satisfaction monitoring

**Data Scope:**
- Customer entities (customers, contacts, relationships)
- Sales data (quotes, deals, contracts)
- Lane performance (pricing, margins, win rates)
- Customer feedback and satisfaction
- Market analysis and competitor intelligence

**Database Namespaces:**
- **Redis:** `maya:*` (e.g., `maya:quote:789:context`)
- **Qdrant:** `maya_sales_knowledge` collection
- **PostgreSQL:** `maya` schema
- **Neo4j:** `:Maya_Domain` label

**Example Queries:**
- "What's our win rate for Chicago-Dallas quotes?"
- "Show me Customer ABC's quote history"
- "What margin should we quote for Atlanta-Miami?"
- "Which customers have complained about late deliveries?"

**Cross-Domain Insights:**
- Equipment reliability (from Oscar) → Customer satisfaction (Maya analysis)
- Cost trends (from Sarah) → Pricing strategy (Maya adjustments)

---

## System Agent (Default)

### System - Shared Operations

**Agent ID:** `system`
**Status:** ✅ Active (Default for all shared operations)
**Domain:** Cross-agent shared knowledge
**Implementation:** Phase 1 (built-in default)

**Responsibilities:**
- Shared entity management (entities visible to all agents)
- Cross-agent conversation storage
- System-wide analytics and reporting
- Shared document storage
- Background jobs without specific agent context

**Data Scope:**
- All conversations (from all agents)
- Shared entities (companies, locations, generic entities)
- Cross-agent insights and patterns
- System configuration and metadata

**Database Namespaces:**
- **Redis:** `system:*` or `shared:*` (e.g., `shared:entity:999:metadata`)
- **Qdrant:** `shared_documents` collection
- **PostgreSQL:** `core` schema (all shared tables)
- **Neo4j:** `:Shared` label (entities visible to all)

**Example Queries:**
- "Show me all conversations across all agents"
- "What companies are mentioned most often?"
- "Cross-agent analytics: cost vs revenue by customer"

---

## Adding New Agents

### Process

**Step 1: Define Agent**
- Choose unique agent ID (lowercase, descriptive: e.g., "alex")
- Define domain and responsibilities
- Document data scope

**Step 2: Update This Registry**
- Add agent section above
- Document database namespaces
- Provide example queries

**Step 3: Create Database Namespaces**

**Redis:** No action needed (dynamic namespacing)
```python
# Just pass new agent_id - works instantly
cache = CacheService(redis, agent_id="alex")
```

**Qdrant:** Create collection
```python
await qdrant.create_collection(
    collection_name="alex_domain_knowledge",
    vectors_config={"size": 1536, "distance": "Cosine"}
)
```

**PostgreSQL:** Create schema (Phase 2 only)
```sql
CREATE SCHEMA IF NOT EXISTS alex;
```

**Neo4j:** Use label (Phase 2 only)
```cypher
CREATE (e:Entity:Alex_Domain {name: "Example"})
```

**Step 4: Update Configuration**

**File:** `apex-memory-system/config/agent_registry.py`
```python
AGENT_COLLECTIONS = {
    "oscar": "oscar_fleet_knowledge",
    "sarah": "sarah_financial_knowledge",
    "maya": "maya_sales_knowledge",
    "alex": "alex_domain_knowledge",  # ← Add here
    "system": "shared_documents"
}
```

**Total Time:** 15-30 minutes per new agent

---

## Agent Interaction Patterns

### Single-Agent Operations (Most Common)

**Scenario:** Oscar receives message about truck maintenance

```python
# Redis cache (Oscar namespace)
cache = CacheService(redis, agent_id="oscar")
await cache.cache_conversation_context(conv_id, context)
# Key: oscar:conversation:123:context

# Qdrant search (Oscar collection)
vector = VectorService(qdrant, agent_id="oscar")
results = await vector.search(query_vector)
# Searches: oscar_fleet_knowledge
```

---

### Cross-Agent Operations (Advanced)

**Scenario:** "How do maintenance costs (Oscar) affect our margins (Sarah)?"

```python
# Query Oscar's fleet data
oscar_service = VectorService(qdrant, agent_id="oscar")
fleet_data = await oscar_service.search(query_vector)

# Query Sarah's financial data
sarah_service = VectorService(qdrant, agent_id="sarah")
cost_data = await sarah_service.search(query_vector)

# Synthesize cross-domain insight
insight = synthesize_cross_domain(fleet_data, cost_data)
```

**Implementation:** Phase 2 (Fluid Mind patterns)

---

## Agent Configuration Reference

### Redis Namespace Patterns

| Agent | Namespace Format | Example |
|-------|------------------|---------|
| Oscar | `oscar:resource:id:detail` | `oscar:conversation:123:context` |
| Sarah | `sarah:resource:id:detail` | `sarah:invoice:456:analysis` |
| Maya | `maya:resource:id:detail` | `maya:quote:789:pricing` |
| System | `system:resource:id:detail` or `shared:*` | `shared:entity:999:metadata` |

### Qdrant Collections

| Agent | Collection Name | Purpose |
|-------|-----------------|---------|
| Oscar | `oscar_fleet_knowledge` | Fleet, trucks, maintenance, drivers |
| Sarah | `sarah_financial_knowledge` | Invoices, vendors, costs, budgets |
| Maya | `maya_sales_knowledge` | Customers, quotes, lanes, deals |
| System | `shared_documents` | Cross-agent documents and entities |

### PostgreSQL Schemas (Phase 2)

| Agent | Schema Name | Purpose |
|-------|-------------|---------|
| All | `core` | Shared tables (conversations, entities, chunks) |
| Oscar | `oscar` | Fleet-specific tables (fleet_metrics, maintenance_schedules) |
| Sarah | `sarah` | Finance-specific tables (vendor_patterns, invoice_analysis) |
| Maya | `maya` | Sales-specific tables (quotes, customer_lanes, win_loss) |

### Neo4j Labels (Phase 2)

| Agent | Label Format | Example |
|-------|--------------|---------|
| Oscar | `:Entity:Oscar_Domain` | Truck nodes, maintenance nodes |
| Sarah | `:Entity:Sarah_Domain` | Invoice nodes, vendor nodes |
| Maya | `:Entity:Maya_Domain` | Customer nodes, quote nodes |
| System | `:Entity:Shared` | Company nodes, location nodes |

---

## Monitoring & Metrics

**Per-Agent Metrics (Grafana Dashboard):**
- Cache hit rate per agent
- Query latency (P50/P95) per agent
- Qdrant collection size per agent
- Query volume per agent
- Cost per agent (LLM API usage)

**Cross-Agent Metrics:**
- Cross-domain query frequency
- Agent collaboration patterns
- Shared entity access rates

---

## Security & Access Control

### Phase 1 (Current)
- **No access control** - All agents can access all data
- **Trust-based** - Application layer ensures agent queries appropriate data

### Phase 2 (Fluid Mind Patterns)
- **Schema-level RBAC** - PostgreSQL role permissions per schema
- **Label-based filtering** - Neo4j queries filtered by agent label
- **Collection permissions** - Qdrant collection access control
- **API key authentication** - Agent identity via JWT claims

---

## References

**Architecture:** `ARCHITECTURE.md` - Section "Multi-Agent Namespacing Strategy"
**Implementation:** `research/future-enhancements/fluid-mind-patterns-to-adopt.md`
**Analysis:** `research/architectural-analysis/fluid-mind-vs-conversational-memory.md`

---

**Last Updated:** 2025-11-14
**Next Review:** Phase 2 (when Sarah/Maya agents activate)
**Maintainer:** Conversational Memory Integration Team
