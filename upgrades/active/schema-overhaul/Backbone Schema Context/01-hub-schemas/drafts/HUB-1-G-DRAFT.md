# HUB 1: G (COMMAND CENTER)

**Status:** 📝 Draft - Rough Structure
**Purpose:** Personal hub for strategic oversight, knowledge management, and life tracking
**Owner:** G (Richard Glaubitz)
**Primary Key Strategy:** user_id = "g_main" for G entity, unique IDs for sub-entities

---

## Purpose

Hub 1 serves as G's personal command center, tracking everything related to strategic business decisions, personal knowledge, health protocols, relationships, and assets. Much of this hub is private and stand-alone, with selective connections to business hubs (OpenHaul, Origin).

**Key Distinction:** This is the only hub that's personal rather than purely business-focused.

---

## Core Entities

### 1. **G (Person)** - Central Command Entity
The primary entity representing G across the entire system.

**Core Properties:**
- user_id: "g_main" (UNIQUE - primary identifier)
- name: "G (Richard Glaubitz)"
- email: "richard@origintransport.com"
- role: "President | Co-Founder"
- location: "Las Vegas, NV"
- timezone: "America/Los_Angeles"

**Strategic Properties:**
- vision: text (long-term strategic vision)
- current_focus: [] (array of active focus areas)
- decision_framework: {} (JSON - how decisions are made)
- communication_style: "direct, action-oriented, high-energy"

**Temporal:**
- created_at, updated_at, valid_from, valid_to

---

### 2. **Project** - Active Initiatives
Both business and personal projects.

**Core Properties:**
- project_id (UUID)
- name
- description
- status (planning, active, on-hold, completed, cancelled)
- priority (1-5)
- start_date, target_completion, actual_completion
- owner_id (always "g_main")
- related_to (OpenHaul, Origin, Personal, etc.)
- category (business-strategy, tech-implementation, personal-development, health, etc.)

**Example Projects:**
- "Apex Memory System Development"
- "OpenHaul Growth Strategy 2025"
- "Health Protocol Optimization"

---

### 3. **Goal** - Objectives and Targets
Strategic and personal goals with tracking.

**Core Properties:**
- goal_id (UUID)
- title
- description
- category (business, financial, health, personal, relationship)
- status (active, achieved, abandoned)
- target_date
- progress_percentage (0-100)
- related_projects [] (array of project_ids)
- metrics: {} (JSON - how to measure success)

**Example Goals:**
- "Grow OpenHaul revenue to $2M ARR"
- "Optimize Origin fleet profitability"
- "Achieve target health markers"

---

### 4. **KnowledgeItem** - Research & Protocols
Curated knowledge on topics of interest.

**Core Properties:**
- knowledge_id (UUID)
- title
- category (biohacking, business-strategy, technology, health, finance, etc.)
- content: text (or reference to document)
- source: text (where learned)
- date_added
- last_reviewed
- tags [] (array for search)
- related_to [] (other knowledge items, projects, goals)

**Examples:**
- Medical protocols
- Biohacking routines
- Business frameworks
- Technology research

**Document Types:**
- Research articles
- Protocol documents
- How-to guides
- Best practices

---

### 5. **Insight** - Observations & Learnings
AI-generated or manually captured insights about patterns, opportunities, decisions.

**Core Properties:**
- insight_id (UUID)
- title
- description
- category (business, market, operational, personal, relationship)
- date_captured
- source (observation, AI-analysis, conversation, etc.)
- confidence_level (low, medium, high)
- related_entities [] (what this insight is about - could be trucks, loads, people, companies)
- action_items [] (what to do with this insight)

**Examples:**
- "Unit #6520 maintenance costs 15% above fleet average - investigate"
- "Sun-Glo consistently ships on Fridays - optimize carrier availability"
- "Personal energy peaks 9am-12pm - schedule important decisions then"

---

### 6. **Asset** - Important Resources
Logins, passwords, important documents, credentials.

**Core Properties:**
- asset_id (UUID)
- asset_type (login, password, document, credential, license, certificate)
- name/title
- category (business, personal, financial, health, legal)
- access_info: {} (encrypted JSON - login details, credentials)
- related_to (which service/system/company)
- expiration_date (if applicable)
- last_updated

**Security Note:** ⚠️ Requires encryption layer - highly sensitive data

**Examples:**
- Bank account logins
- Password vault entries
- Important personal documents
- Professional certifications

---

### 7. **HealthProtocol** - Medical & Wellness
Medical protocols, biohacking routines, health tracking.

**Core Properties:**
- protocol_id (UUID)
- name
- category (medical, biohacking, nutrition, exercise, sleep, supplements)
- description
- frequency (daily, weekly, as-needed)
- active_status (boolean)
- start_date, end_date
- results/notes: text
- related_goals [] (health goals this supports)

**Examples:**
- Daily supplement stack
- Exercise routines
- Sleep optimization protocols
- Medical treatments

---

## Primary Relationships

### Ownership & Control
```cypher
// G owns businesses
(G:Person {user_id: "g_main"})-[:OWNS {percentage: 100}]->(Primetime:Company)
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:Company)
(G:Person)-[:OWNS {percentage: 100, via: "Primetime"}]->(Origin:Company)

// G creates projects
(G:Person)-[:CREATED]->(Project)
(G:Person)-[:OWNS]->(Project)

// G sets goals
(G:Person)-[:SET_GOAL]->(Goal)
(G:Person)-[:TRACKS]->(Goal)
```

### Knowledge Management
```cypher
// Knowledge connections
(G:Person)-[:RESEARCHED]->(KnowledgeItem)
(KnowledgeItem)-[:SUPPORTS]->(Project)
(KnowledgeItem)-[:INFORMS]->(Goal)

// Insights link to entities across hubs
(Insight)-[:ABOUT]->(Tractor)  // Hub 3
(Insight)-[:ABOUT]->(Load)     // Hub 2
(Insight)-[:ABOUT]->(Customer) // Hub 4
(Insight)-[:INFORMS]->(Project)
```

### Cross-Hub Strategic Links
```cypher
// Projects drive business activities
(Project {name: "OpenHaul Growth"})-[:DRIVES]->(SalesOrder)  // Hub 2
(Project {name: "Fleet Optimization"})-[:TARGETS]->(Tractor) // Hub 3

// Goals measure business performance
(Goal {title: "Grow OpenHaul Revenue"})-[:MEASURED_BY]->(Revenue) // Hub 5
(Goal {title: "Reduce Fleet Costs"})-[:MEASURED_BY]->(Expense)   // Hub 5
```

---

## Database Distribution

### Neo4j (Relationship Memory)
**Stores:**
- G entity as central node
- All ownership relationships (G → Companies)
- Project/Goal creation relationships
- Knowledge connections
- Cross-hub strategic links

**Why:** Graph traversal - "Show all projects related to OpenHaul", "What goals drive this expense category?"

---

### PostgreSQL (Factual Memory)
**Stores:**
- Project details (descriptions, dates, status)
- Goal tracking data (progress, metrics)
- KnowledgeItem content (if text-based)
- HealthProtocol records
- Asset metadata (NOT encrypted credentials - those go in secure vault)

**Why:** Structured queries - "Show all active projects by priority", "List goals with completion dates in Q1 2025"

---

### Qdrant (Semantic Memory)
**Stores:**
- KnowledgeItem embeddings (research articles, protocols)
- Insight embeddings (for semantic search)
- Project documentation embeddings

**Why:** Semantic search - "Find all knowledge about biohacking protocols similar to this", "Search insights about truck profitability"

---

### Redis (Working Memory)
**Stores:**
- Current focus areas (60s TTL)
- Active project list (for dashboard)
- Recent insights (rolling 7-day window)

**Why:** Fast access for dashboards - "What is G focused on right now?"

---

### Graphiti (Temporal Memory)
**Stores:**
- Goal evolution (active → achieved → archived)
- Project lifecycle (planning → active → completed)
- Focus shift tracking (what G was focused on 3 months ago)
- Insight emergence patterns

**Why:** Temporal queries - "How has G's strategic focus changed over the last 6 months?", "When did this goal become active?"

---

## Primary Keys & Cross-Database Identity

**G Entity:**
```python
# Neo4j
(:Person {user_id: "g_main", name: "G"})

# PostgreSQL
SELECT * FROM people WHERE user_id = 'g_main'

# Qdrant
filter={"user_id": "g_main"}

# Graphiti
Person(user_id="g_main", name="G")
```

**Projects/Goals:**
- Use UUID as primary key
- Consistent across all databases
- Example: project_id = "proj_018c3a8b-9f6e-7890-abcd-ef1234567890"

---

## Cross-Hub Links

### Hub 1 → Hub 2 (OpenHaul)
```cypher
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:Company)
(Project {name: "OpenHaul Growth"})-[:DRIVES]->(Load)
(Insight)-[:ABOUT]->(Carrier)
```

### Hub 1 → Hub 3 (Origin)
```cypher
(G:Person)-[:OWNS {via: "Primetime"}]->(Origin:Company)
(Project {name: "Fleet Optimization"})-[:TARGETS]->(Tractor)
(Insight)-[:ABOUT]->(Tractor {unit_number: "6520"})
```

### Hub 1 → Hub 4 (Contacts)
```cypher
(G:Person)-[:KNOWS]->(Person)
(G:Person)-[:RELATIONSHIP_WITH {type: "business_partner"}]->(Travis:Person)
(Project)-[:INVOLVES]->(Customer:Company)
```

### Hub 1 → Hub 5 (Financials)
```cypher
(Goal {title: "Grow Revenue"})-[:MEASURED_BY]->(Revenue)
(Project)-[:IMPACTS]->(Expense)
(Insight)-[:ABOUT]->(IntercompanyTransfer)
```

### Hub 1 → Hub 6 (Corporate)
```cypher
(G:Person)-[:OWNS]->(Primetime:LegalEntity)
(Project {name: "Corporate Structure Optimization"})-[:TARGETS]->(LegalEntity)
```

---

## Security & Privacy Considerations

**⚠️ CRITICAL: Much of this hub contains private, sensitive data.**

### Access Levels
1. **Private to G** (most data)
   - Personal health protocols
   - Asset credentials
   - Personal goals
   - Financial insights

2. **Shared with Business Systems** (selective)
   - Business projects
   - Company-related goals
   - Business insights

3. **Encrypted** (highest sensitivity)
   - Asset credentials (logins, passwords)
   - Personal health records
   - Financial account details

### Implementation Requirements
- Row-level security in PostgreSQL
- Separate Qdrant collection for private documents
- Encryption at rest for Asset entity
- Access control layer in API (NOT part of schema, but note for implementation)

---

## TODO - Information Needed

### Missing Details
- [ ] **Project Categories:** Define comprehensive list (business-strategy, tech-implementation, health, personal-development, etc.)
- [ ] **Goal Metrics Structure:** How to define measurable success criteria in JSON format
- [ ] **KnowledgeItem Taxonomy:** Standardized categories and tagging system
- [ ] **Insight Confidence Levels:** Criteria for low/medium/high confidence
- [ ] **Health Protocol Categories:** Full list of protocol types
- [ ] **Asset Types:** Complete enumeration of asset categories

### Document Examples
- [ ] Example project documentation (what does a project doc look like?)
- [ ] Example knowledge item (research article, protocol doc)
- [ ] Example health protocol documentation
- [ ] Example insight format (AI-generated vs manual)

### Integration Questions
- [ ] **Security Model:** Exact implementation of access control (schema notes only, not full implementation)
- [ ] **Encryption Strategy:** Which fields require encryption vs standard database security
- [ ] **Dashboard Requirements:** What real-time data needs Redis caching?
- [ ] **Temporal Tracking:** Which entity state changes are most important to track?

### Cross-Hub Clarifications
- [ ] How do business projects link to specific loads/trucks/customers?
- [ ] Should insights auto-generate from data patterns (AI-driven) or manual entry only?
- [ ] How do personal goals integrate with business metrics?

---

## Next Steps

1. **Review this draft** - Does the structure make sense?
2. **Clarify TODOs** - Answer missing information questions
3. **Define categories** - Create comprehensive category lists
4. **Deep dive** - Expand to full detail matching Hub 3 (Origin) baseline
5. **Security design** - Define access control patterns (note in schema, implement later)

---

**Draft Created:** November 3, 2025
**Schema Version:** v2.0 (Draft)
**Completion Status:** ~40% (structure defined, details needed)
