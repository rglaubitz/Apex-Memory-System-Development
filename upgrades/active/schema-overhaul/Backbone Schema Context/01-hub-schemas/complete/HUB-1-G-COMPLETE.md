# HUB 1: G (COMMAND CENTER) - COMPLETE

**Status:** ✅ Complete Baseline (95%)
**Purpose:** Strategic oversight, knowledge management, goal tracking, and life coordination
**Owner:** G (Richard Glaubitz)
**Primary Key Strategy:** user_id = "g_main" for G entity, UUIDs for all sub-entities

---

## Purpose

Hub 1 serves as G's **personal command center** - the strategic brain coordinating all business operations, personal development, and knowledge management. This hub connects high-level strategy to operational execution across OpenHaul (Hub 2), Origin (Hub 3), and financial performance (Hub 5).

**Key Distinction:** This is the only **personal** hub (private to G) with selective **business integration** (projects, goals, insights shared with business systems).

**What Makes This Different:**
- **Top-Down Strategy:** Goals and projects defined here drive activities in other hubs
- **Cross-Hub Intelligence:** Insights aggregate data from all business hubs
- **Private + Business:** Personal data (health, assets) coexists with business data (projects, goals)

---

## Core Entities (7 entities, 195 properties total)

### 1. **G (Person)** - Central Command Entity ⭐

The primary entity representing G across the entire 6-hub system.

**Complete Property List (30 properties):**

```yaml
# Primary Identifiers
user_id: string              # PRIMARY KEY - "g_main" (unique across all hubs)
person_id: string            # Links to Hub 4 Person entity
name: string                 # "G (Richard Glaubitz)"
display_name: string         # "G"

# Contact Information
email: string                # "richard@origintransport.com"
phone: string                # Primary phone
location: string             # "Las Vegas, NV"
timezone: string             # "America/Los_Angeles"

# Strategic Properties
role: string                 # "President | Co-Founder"
vision: text                 # Long-term strategic vision statement
current_focus: array[string] # Active focus areas (e.g., ["OpenHaul Growth", "Fleet Optimization"])
decision_framework: json     # How decisions are made (criteria, priorities)
communication_style: string  # "direct, action-oriented, high-energy"

# Preferences
preferred_meeting_times: array[string]  # ["09:00-12:00", "14:00-16:00"]
working_hours_start: time    # 07:00
working_hours_end: time      # 18:00
notification_preferences: json  # How/when to receive alerts

# Business Ownership (tracked in Hub 6, referenced here)
ownership_stakes: json       # {"Primetime": 100, "OpenHaul": 50, "Origin": 100}

# Personal Context
life_stage: string           # "building_empire", "scaling_businesses"
risk_tolerance: enum         # ["conservative", "moderate", "aggressive", "very_aggressive"]
decision_speed: enum         # ["deliberate", "balanced", "fast", "instant"]

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: timestamp (nullable)
```

**Example G Entity:**
```python
G(
    user_id="g_main",
    person_id="person_g",  # Links to Hub 4
    name="G (Richard Glaubitz)",
    display_name="G",
    email="richard@origintransport.com",
    phone="+1-702-555-0199",
    location="Las Vegas, NV",
    timezone="America/Los_Angeles",
    role="President | Co-Founder",
    vision="Build category-defining companies in logistics while optimizing personal performance",
    current_focus=["OpenHaul Growth Q4 2025", "Fleet Profitability", "Apex Memory Development"],
    communication_style="direct, action-oriented, high-energy",
    preferred_meeting_times=["09:00-12:00", "14:00-16:00"],
    working_hours_start="07:00",
    working_hours_end="18:00",
    ownership_stakes={"Primetime": 100, "OpenHaul": 50, "Origin": 100},
    life_stage="building_empire",
    risk_tolerance="aggressive",
    decision_speed="fast"
)
```

---

### 2. **Project** - Active Initiatives

Business and personal projects tracking strategic work.

**Complete Property List (28 properties):**

```yaml
# Primary Identifiers
project_id: string           # PRIMARY KEY - UUID
project_name: string         # Human-readable name
project_code: string (nullable)  # Short code (e.g., "OH-GROWTH-Q4")

# Classification
project_type: enum           # See Project Types section
category: enum               # See Project Categories section
scope: enum                  # ["personal", "business_single_entity", "business_multi_entity", "enterprise_wide"]
owner_id: string             # Always "g_main"

# Status & Lifecycle
status: enum                 # ["idea", "planning", "active", "on_hold", "completed", "cancelled", "archived"]
priority: integer            # 1 (highest) to 5 (lowest)
urgency: enum                # ["low", "medium", "high", "critical"]
visibility: enum             # ["private", "team", "company", "public"]

# Timeline
start_date: date
target_completion_date: date
actual_completion_date: date (nullable)
last_milestone_date: date (nullable)
next_milestone_date: date (nullable)

# Progress Tracking
progress_percentage: integer # 0-100
completion_criteria: array[string]  # What defines "done"
blockers: array[string]      # What's preventing progress

# Relationships
related_to: array[string]    # ["OpenHaul", "Origin", "Personal", entity IDs]
related_goals: array[string] # goal_id references
involved_people: array[string]  # person_id references
impacted_entities: array[string]  # What entities does this affect (companies, trucks, etc.)

# Content
description: text
objective: text              # What we're trying to achieve
success_metrics: json        # How to measure success

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: timestamp (nullable)
```

**Project Types (12 types):**
```yaml
project_type:
  - business_strategy        # Strategic initiatives
  - revenue_growth           # Sales, marketing, customer acquisition
  - operational_efficiency   # Process improvements
  - cost_reduction           # Expense optimization
  - technology_implementation  # Software, systems, automation
  - fleet_optimization       # Truck-specific projects
  - market_expansion         # New markets, new services
  - compliance_regulatory    # Legal, regulatory requirements
  - personal_development     # Self-improvement, learning
  - health_optimization      # Health, biohacking
  - relationship_building    # Networking, partnerships
  - knowledge_management     # Research, documentation
```

**Project Categories (8 categories):**
```yaml
category:
  - openhaul_brokerage       # OpenHaul-specific
  - origin_trucking          # Origin-specific
  - corporate_structure      # Legal, compliance, corporate
  - technology_systems       # Tech stack, software
  - financial_management     # Accounting, cash flow
  - personal_growth          # Self-development
  - health_wellness          # Health protocols
  - strategic_planning       # High-level strategy
```

**Example Projects:**
```python
# Business Project
Project(
    project_id="proj_018c3a8b",
    project_name="OpenHaul Q4 2025 Growth Initiative",
    project_code="OH-GROWTH-Q4",
    project_type="revenue_growth",
    category="openhaul_brokerage",
    scope="business_single_entity",
    owner_id="g_main",
    status="active",
    priority=1,
    urgency="high",
    visibility="company",
    start_date="2025-10-01",
    target_completion_date="2025-12-31",
    progress_percentage=45,
    completion_criteria=[
        "Achieve $500K revenue in Q4",
        "Onboard 15 new carrier relationships",
        "Improve margin to 22%"
    ],
    related_to=["OpenHaul", "company_openhaul"],
    related_goals=["goal_openhaul_revenue_2025"],
    involved_people=["person_g", "person_travis"],
    description="Aggressive growth push for OpenHaul in Q4 targeting $500K revenue milestone",
    objective="Establish OpenHaul as profitable, scalable brokerage operation",
    success_metrics={
        "revenue": {"target": 500000, "current": 225000},
        "margin": {"target": 22, "current": 19.5},
        "new_carriers": {"target": 15, "current": 7}
    }
)

# Tech Project
Project(
    project_id="proj_apex_mem",
    project_name="Apex Memory System Development",
    project_code="APEX-MEM",
    project_type="technology_implementation",
    category="technology_systems",
    scope="enterprise_wide",
    owner_id="g_main",
    status="active",
    priority=2,
    urgency="medium",
    visibility="private",
    start_date="2025-06-01",
    target_completion_date="2026-03-31",
    progress_percentage=75,
    completion_criteria=[
        "All 6 hubs defined and integrated",
        "Production deployment complete",
        "Query router achieving 90%+ accuracy"
    ],
    related_to=["OpenHaul", "Origin", "G"],
    related_goals=["goal_business_intelligence"],
    description="Multi-database knowledge graph for unified business intelligence",
    success_metrics={
        "hubs_complete": {"target": 6, "current": 5},
        "deployment_status": {"target": "production", "current": "development"},
        "query_accuracy": {"target": 90, "current": 90}
    }
)
```

---

### 3. **Goal** - Objectives and Targets

Strategic and personal goals with measurable success criteria.

**Complete Property List (26 properties):**

```yaml
# Primary Identifiers
goal_id: string              # PRIMARY KEY - UUID
goal_title: string           # Human-readable title
goal_code: string (nullable) # Short code (e.g., "OH-REV-2M")

# Classification
goal_type: enum              # See Goal Types section
category: enum               # ["business", "financial", "health", "personal", "relationship", "knowledge"]
scope: enum                  # ["personal", "business_unit", "enterprise", "multi_entity"]
owner_id: string             # Always "g_main"

# Status & Lifecycle
status: enum                 # ["draft", "active", "achieved", "abandoned", "deferred"]
priority: integer            # 1 (highest) to 5 (lowest)
visibility: enum             # ["private", "team", "company"]

# Timeline
target_date: date            # When to achieve
start_tracking_date: date    # When goal became active
achieved_date: date (nullable)
deadline_type: enum          # ["hard_deadline", "soft_target", "aspirational"]

# Progress Tracking
progress_percentage: integer # 0-100
current_value: decimal (nullable)  # Current metric value
target_value: decimal (nullable)   # Target metric value
unit_of_measure: string (nullable)  # "dollars", "loads", "percentage", etc.

# Relationships
related_projects: array[string]  # project_id references
measured_by_entities: array[string]  # What entities track this (revenue_ids, expense_ids, etc.)
depends_on_goals: array[string]  # Other goals that must be achieved first

# Measurement
metrics: json                # How to measure success (formula, data sources)
milestone_criteria: array[string]  # Checkpoints along the way
success_definition: text     # What "achieved" means

# Content
description: text
motivation: text             # Why this goal matters
obstacles: array[string]     # Known challenges

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: timestamp (nullable)
```

**Goal Types (10 types):**
```yaml
goal_type:
  - revenue_target           # Revenue goals
  - profitability_target     # Margin, profit goals
  - cost_reduction           # Expense reduction
  - operational_efficiency   # Process improvements
  - market_share             # Competitive positioning
  - customer_acquisition     # New customer targets
  - asset_utilization        # Truck utilization, capacity
  - personal_health          # Health markers, fitness
  - knowledge_acquisition    # Learning, skill development
  - relationship_quality     # Personal/business relationships
```

**Example Goals:**
```python
# Business Goal
Goal(
    goal_id="goal_openhaul_revenue_2025",
    goal_title="Grow OpenHaul Revenue to $2M ARR",
    goal_code="OH-REV-2M",
    goal_type="revenue_target",
    category="business",
    scope="business_unit",
    owner_id="g_main",
    status="active",
    priority=1,
    visibility="company",
    target_date="2025-12-31",
    start_tracking_date="2025-01-01",
    progress_percentage=56,
    current_value=1120000.00,
    target_value=2000000.00,
    unit_of_measure="dollars",
    related_projects=["proj_018c3a8b"],  # OH Growth Q4
    measured_by_entities=["revenue"],  # Links to Hub 5 Revenue entities
    metrics={
        "formula": "SUM(revenue WHERE source_entity = 'OpenHaul' AND revenue_date >= '2025-01-01')",
        "data_source": "Hub 5 - Revenue",
        "update_frequency": "daily"
    },
    milestone_criteria=[
        "Q1: $400K (achieved)",
        "Q2: $800K (achieved)",
        "Q3: $1.2M (achieved)",
        "Q4: $2M (in progress)"
    ],
    description="Scale OpenHaul from startup to $2M ARR profitable brokerage",
    motivation="Establish OpenHaul as self-sustaining, scalable business unit",
    obstacles=["Carrier capacity constraints", "Market competition", "Margin pressure"]
)

# Personal Goal
Goal(
    goal_id="goal_health_optimization",
    goal_title="Achieve Target Health Markers",
    goal_type="personal_health",
    category="health",
    scope="personal",
    owner_id="g_main",
    status="active",
    priority=2,
    visibility="private",
    target_date="2025-12-31",
    start_tracking_date="2025-01-01",
    progress_percentage=70,
    milestone_criteria=[
        "VO2 Max > 50",
        "Body fat < 15%",
        "Sleep quality > 85%",
        "Recovery score > 80%"
    ],
    related_projects=["proj_health_protocol_v2"],
    description="Optimize health markers through targeted protocols",
    motivation="Peak cognitive and physical performance for decision-making"
)
```

---

### 4. **Task** - Action Items

Specific action items linked to projects, goals, or standalone.

**Complete Property List (22 properties):**

```yaml
# Primary Identifiers
task_id: string              # PRIMARY KEY - UUID
task_title: string
task_code: string (nullable) # Short reference

# Classification
task_type: enum              # ["action_item", "decision", "follow_up", "research", "communication"]
category: enum               # Match project categories
priority: integer            # 1-5
owner_id: string             # Always "g_main" (or delegated person_id)

# Status & Lifecycle
status: enum                 # ["not_started", "in_progress", "blocked", "completed", "cancelled"]
completion_percentage: integer  # 0-100

# Timeline
due_date: date (nullable)
due_time: time (nullable)
completed_date: date (nullable)
estimated_duration_minutes: integer (nullable)

# Relationships
parent_project_id: string (nullable)
parent_goal_id: string (nullable)
depends_on_tasks: array[string]  # task_id references
blocks_tasks: array[string]      # task_id references
related_entities: array[string]  # What this task relates to

# Content
description: text
notes: text (nullable)
outcome: text (nullable)     # What happened after completion

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Example Tasks:**
```python
Task(
    task_id="task_001",
    task_title="Review Q3 OpenHaul financials with Travis",
    task_type="communication",
    category="openhaul_brokerage",
    priority=2,
    owner_id="g_main",
    status="completed",
    completion_percentage=100,
    due_date="2025-10-15",
    completed_date="2025-10-14",
    parent_project_id="proj_018c3a8b",
    parent_goal_id="goal_openhaul_revenue_2025",
    description="Deep dive on Q3 revenue, margin analysis, Q4 projections",
    outcome="Identified 3 high-margin lanes to prioritize in Q4"
)
```

---

### 5. **KnowledgeItem** - Research & Protocols

Curated knowledge on topics of interest.

**Complete Property List (25 properties):**

```yaml
# Primary Identifiers
knowledge_id: string         # PRIMARY KEY - UUID
title: string
subtitle: string (nullable)

# Classification
knowledge_type: enum         # See Knowledge Types section
category: enum               # See Knowledge Categories section
subcategory: string (nullable)
tags: array[string]          # Flexible tagging

# Content
content: text                # Main content (or reference to document)
summary: text                # TL;DR summary
key_takeaways: array[string] # Bullet points
source: string               # Where learned
source_url: string (nullable)
author: string (nullable)

# Quality & Confidence
confidence_level: enum       # ["low", "medium", "high", "expert_validated"]
evidence_strength: enum      # ["anecdotal", "observational", "research_backed", "peer_reviewed"]
applicability: enum          # ["theoretical", "practical", "proven"]

# Lifecycle
date_added: date
last_reviewed: date
review_frequency: enum       # ["never", "annual", "quarterly", "monthly"]
next_review_date: date (nullable)

# Relationships
related_knowledge: array[string]  # knowledge_id references
related_projects: array[string]   # project_id references
related_goals: array[string]      # goal_id references

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Knowledge Types (8 types):**
```yaml
knowledge_type:
  - research_article         # Academic/industry research
  - protocol_document        # Step-by-step procedures
  - how_to_guide            # Instructional content
  - best_practice           # Industry standards
  - framework               # Decision-making frameworks
  - case_study              # Real-world examples
  - reference_material      # Quick reference guides
  - insight_synthesis       # Aggregated learnings
```

**Knowledge Categories (10 categories):**
```yaml
category:
  - biohacking              # Health optimization
  - business_strategy       # Strategic frameworks
  - technology              # Software, systems
  - health_medical          # Medical knowledge
  - finance_investing       # Financial concepts
  - operations              # Operational excellence
  - leadership              # Leadership principles
  - logistics_transport     # Industry-specific
  - personal_development    # Self-improvement
  - decision_making         # Decision frameworks
```

**Example Knowledge Items:**
```python
KnowledgeItem(
    knowledge_id="know_001",
    title="Zone 2 Cardio for Executive Performance",
    knowledge_type="protocol_document",
    category="biohacking",
    subcategory="cardiovascular_health",
    tags=["cardio", "performance", "longevity", "vo2max"],
    content="Detailed protocol for Zone 2 training...",
    summary="60-90 min Zone 2 cardio 3-4x/week improves mitochondrial density, cognitive function",
    key_takeaways=[
        "Target 60-70% max heart rate",
        "Conversational pace (can talk in full sentences)",
        "Minimum 45 minutes per session",
        "Cognitive benefits within 4-6 weeks"
    ],
    source="Huberman Lab Podcast Episode #24",
    confidence_level="expert_validated",
    evidence_strength="research_backed",
    applicability="proven",
    date_added="2025-03-15",
    last_reviewed="2025-10-01",
    review_frequency="quarterly",
    related_goals=["goal_health_optimization"]
)
```

---

### 6. **Insight** - Observations & Learnings

AI-generated or manually captured insights about patterns, opportunities, decisions.

**Complete Property List (28 properties):**

```yaml
# Primary Identifiers
insight_id: string           # PRIMARY KEY - UUID
title: string
insight_code: string (nullable)

# Classification
insight_type: enum           # See Insight Types section
category: enum               # ["business", "market", "operational", "financial", "personal", "relationship"]
domain: enum                 # ["openhaul", "origin", "corporate", "personal", "cross_entity"]
priority: integer            # 1-5 (importance)

# Content
description: text            # What was observed
implication: text            # What it means
recommendation: array[string]  # What to do about it
evidence: array[string]      # Supporting data points

# Quality & Confidence
source: enum                 # See Insight Sources section
confidence_level: enum       # ["low", "medium", "high", "validated"]
impact_potential: enum       # ["low", "medium", "high", "transformative"]
timeframe_relevance: enum    # ["immediate", "short_term", "medium_term", "long_term"]

# Relationships
related_entities: array[string]  # What this insight is about
related_projects: array[string]  # Projects this informs
related_goals: array[string]     # Goals this impacts
action_items: array[string]      # task_id references created from this insight

# Lifecycle
date_captured: date
date_validated: date (nullable)
date_actioned: date (nullable)
expiration_date: date (nullable)  # When insight becomes stale
status: enum                 # ["new", "under_review", "validated", "actioned", "invalidated", "expired"]

# Metrics
value_estimate: decimal (nullable)  # Estimated value if acted upon
cost_estimate: decimal (nullable)   # Cost to implement

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Insight Types (12 types):**
```yaml
insight_type:
  - pattern_detection        # Recurring patterns identified
  - opportunity_identified   # New opportunity discovered
  - risk_warning            # Potential risk flagged
  - performance_anomaly     # Outlier performance (good or bad)
  - cost_optimization       # Cost-saving opportunity
  - revenue_opportunity     # Revenue-generating insight
  - market_intelligence     # Competitive/market insight
  - operational_inefficiency  # Process improvement needed
  - relationship_insight    # People/relationship observation
  - decision_recommendation # Suggested decision
  - trend_forecast          # Predictive insight
  - hypothesis_test         # Testable hypothesis
```

**Insight Sources (6 sources):**
```yaml
source:
  - ai_analysis             # Generated by AI from data
  - manual_observation      # G's personal observation
  - conversation            # Insight from meeting/call
  - data_aggregation        # Query/report revealed pattern
  - external_intelligence   # Market research, news
  - system_alert            # Automated threshold alert
```

**Example Insights:**
```python
# Operational Insight
Insight(
    insight_id="insight_001",
    title="Unit #6520 Maintenance Costs 15% Above Fleet Average",
    insight_type="performance_anomaly",
    category="operational",
    domain="origin",
    priority=2,
    description="Unit #6520 maintenance costs are $4,250/month vs fleet average $3,700/month",
    implication="Either truck has mechanical issues OR driver (Robert) is harder on equipment",
    recommendation=[
        "Review maintenance history for recurring issues",
        "Cross-reference with driver behavior data from Samsara",
        "Consider driver training or truck replacement"
    ],
    evidence=[
        "Last 6 months maintenance costs: $25,500 for #6520 vs $22,200 fleet avg",
        "Brake service frequency: 3x for #6520 vs 1.5x fleet avg",
        "Current driver: Robert (assigned 10 months)"
    ],
    source="ai_analysis",
    confidence_level="high",
    impact_potential="medium",
    timeframe_relevance="short_term",
    related_entities=["tractor_6520", "driver_robert"],
    related_projects=["proj_fleet_optimization"],
    value_estimate=6600.00,  # Annual savings if fixed
    status="validated"
)

# Revenue Insight
Insight(
    insight_id="insight_002",
    title="Sun-Glo Consistently Ships Fridays - Optimize Carrier Availability",
    insight_type="pattern_detection",
    category="business",
    domain="openhaul",
    priority=3,
    description="Sun-Glo places 78% of orders on Fridays for Monday pickup",
    implication="Can pre-position carriers or negotiate better rates knowing pattern",
    recommendation=[
        "Alert preferred carriers Wednesday-Thursday for Friday booking opportunity",
        "Consider dedicated carrier agreement for this lane",
        "Negotiate better rates due to predictability"
    ],
    evidence=[
        "14 of 18 loads booked on Fridays (Jan-Oct 2025)",
        "Average lead time: 72 hours (Friday to Monday)",
        "Lane: Chicago to Dallas (consistent)"
    ],
    source="data_aggregation",
    confidence_level="high",
    impact_potential="medium",
    timeframe_relevance="immediate",
    related_entities=["company_sunglo", "load_pattern"],
    related_goals=["goal_openhaul_revenue_2025"],
    value_estimate=8000.00,  # Annual margin improvement
    status="actioned"
)
```

---

### 7. **Asset** - Important Resources (Credentials)

Logins, passwords, important documents, credentials (⚠️ HIGH SECURITY).

**Complete Property List (22 properties):**

```yaml
# Primary Identifiers
asset_id: string             # PRIMARY KEY - UUID
asset_name: string
asset_code: string (nullable)

# Classification
asset_type: enum             # See Asset Types section
category: enum               # ["business", "personal", "financial", "health", "legal", "technical"]
sensitivity_level: enum      # ["public", "internal", "confidential", "highly_confidential"]

# Content (⚠️ ENCRYPTED)
access_info: json            # ENCRYPTED - login details, credentials, passwords
access_url: string (nullable)  # Login URL
username: string (nullable)  # Username/email (may be encrypted)
notes: text (nullable)       # Additional access notes

# Relationships
related_to_entity: string (nullable)  # Which company/system (e.g., "OpenHaul", "Origin")
related_to_service: string (nullable)  # Which service (e.g., "QuickBooks", "Samsara")
owner_id: string             # Always "g_main"

# Lifecycle
created_date: date
last_accessed_date: date (nullable)
last_updated_date: date (nullable)
expiration_date: date (nullable)  # For credentials that expire
renewal_required: boolean
renewal_frequency: enum (nullable)  # ["monthly", "quarterly", "annual", "biennial"]

# Security
encryption_key_id: string    # Which encryption key used
access_level_required: enum  # ["g_only", "g_plus_delegate", "shared"]
audit_log_enabled: boolean

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Asset Types (15 types):**
```yaml
asset_type:
  - bank_account_login       # Bank/financial institution access
  - password_vault_entry     # Password manager entry
  - api_key                  # Service API keys
  - ssh_key                  # Server access keys
  - ssl_certificate          # Web certificates
  - software_license         # Software license keys
  - domain_registration      # Domain account access
  - cloud_service_account    # AWS, GCP, Azure
  - email_account            # Email access
  - database_credential      # Database access
  - personal_document        # Important personal docs
  - professional_certificate # Certifications, licenses
  - legal_document           # Contracts, agreements
  - health_record_access     # Medical portal logins
  - insurance_portal         # Insurance account access
```

**Security Note:** ⚠️ This entity requires:
- Encryption at rest (access_info, username fields)
- Row-level security (G access only)
- Audit logging (who accessed what, when)
- Separate encryption key management
- **Schema defines structure; encryption is implementation concern**

**Example Assets (generic examples - NOT real credentials):**
```python
Asset(
    asset_id="asset_001",
    asset_name="Origin Bank Account - Wells Fargo Business",
    asset_type="bank_account_login",
    category="business",
    sensitivity_level="highly_confidential",
    access_info={
        "encrypted": True,
        "username": "[ENCRYPTED]",
        "password": "[ENCRYPTED]",
        "security_questions": "[ENCRYPTED]",
        "two_factor_method": "SMS"
    },
    access_url="https://wellsfargo.com/business",
    related_to_entity="Origin",
    related_to_service="Wells Fargo Business Banking",
    owner_id="g_main",
    last_accessed_date="2025-11-01",
    expiration_date="2026-02-01",  # Password expiry
    renewal_required=True,
    renewal_frequency="quarterly",
    encryption_key_id="key_001",
    access_level_required="g_only",
    audit_log_enabled=True
)
```

---

### 8. **Communication** - Messages & Conversations

Important communications tracked for context.

**Complete Property List (24 properties):**

```yaml
# Primary Identifiers
communication_id: string     # PRIMARY KEY - UUID
subject: string (nullable)
communication_code: string (nullable)

# Classification
communication_type: enum     # ["email", "phone_call", "meeting", "text_message", "video_call", "voice_memo"]
direction: enum              # ["inbound", "outbound", "bidirectional"]
category: enum               # ["business", "personal", "strategic", "operational", "administrative"]
priority: enum               # ["low", "normal", "high", "urgent"]

# Participants
owner_id: string             # Always "g_main"
participants: array[string]  # person_id references
primary_contact: string (nullable)  # Main person_id

# Content
content_summary: text        # Summary of communication
key_points: array[string]    # Main takeaways
action_items: array[string]  # task_id references created from this
decision_made: text (nullable)  # Decisions reached

# Relationships
related_to_entities: array[string]  # What entities this relates to
related_to_projects: array[string]  # Projects discussed
related_to_goals: array[string]     # Goals referenced

# Timeline
communication_date: timestamp
duration_minutes: integer (nullable)
follow_up_required: boolean
follow_up_date: date (nullable)

# Storage
transcript: text (nullable)  # Full transcript if available
recording_url: string (nullable)  # Audio/video recording
attachments: array[string]   # Document references

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Example Communication:**
```python
Communication(
    communication_id="comm_001",
    subject="Q4 Strategy Discussion with Travis",
    communication_type="video_call",
    direction="bidirectional",
    category="strategic",
    priority="high",
    owner_id="g_main",
    participants=["person_g", "person_travis"],
    primary_contact="person_travis",
    content_summary="Reviewed OpenHaul Q3 performance, discussed Q4 growth targets, agreed on carrier recruitment strategy",
    key_points=[
        "Q3 margin improved to 19.5% (from 17% Q2)",
        "Targeting $500K Q4 revenue",
        "Need 15 new carrier relationships",
        "Focus on high-margin midwest lanes"
    ],
    action_items=["task_carrier_recruitment", "task_lane_analysis"],
    decision_made="Prioritize carrier recruitment over customer acquisition in Q4",
    related_to_entities=["company_openhaul"],
    related_to_projects=["proj_018c3a8b"],
    related_to_goals=["goal_openhaul_revenue_2025"],
    communication_date="2025-10-14T14:00:00Z",
    duration_minutes=45,
    follow_up_required=True,
    follow_up_date="2025-10-21"
)
```

---

## Entity Summary

| Entity | Properties | Primary Key | Business/Personal | Cross-Hub Links |
|--------|------------|-------------|-------------------|-----------------|
| **G (Person)** | 30 | user_id (string) | Both | All hubs (ownership) |
| **Project** | 28 | project_id (UUID) | Both | Hubs 2, 3, 5 (drives activities) |
| **Goal** | 26 | goal_id (UUID) | Both | Hubs 2, 5 (measured by) |
| **Task** | 22 | task_id (UUID) | Both | Projects, Goals |
| **KnowledgeItem** | 25 | knowledge_id (UUID) | Both | Projects, Goals |
| **Insight** | 28 | insight_id (UUID) | Both | All hubs (about entities) |
| **Asset** | 22 | asset_id (UUID) | Both | Hub 6 (credentials for entities) |
| **Communication** | 24 | communication_id (UUID) | Both | Hub 4 (participants), Projects, Goals |
| **Total** | **195** | **8 entities** | **Private + Business** | **Strategic integration** |

---

## Key Relationships

### Ownership & Control

```cypher
// G owns businesses (via Hub 6)
(G:Person {user_id: "g_main"})-[:OWNS {percentage: 100}]->(Primetime:LegalEntity)
(G:Person)-[:OWNS {percentage: 50, co_owner: "person_travis"}]->(OpenHaul:LegalEntity)
(Primetime)-[:OWNS {percentage: 100}]->(Origin:LegalEntity)

// G creates strategic entities
(G:Person)-[:CREATED]->(Project)
(G:Person)-[:OWNS]->(Project)
(G:Person)-[:SET_GOAL]->(Goal)
(G:Person)-[:TRACKS]->(Goal)
```

### Strategic Direction (Top-Down)

```cypher
// Goals drive projects
(Goal {title: "Grow OpenHaul Revenue"})-[:DRIVES]->(Project {name: "OpenHaul Q4 Growth"})

// Projects impact operations
(Project)-[:TARGETS]->(Load)     // Hub 2: OpenHaul loads
(Project)-[:TARGETS]->(Tractor)  // Hub 3: Fleet optimization
(Project)-[:TARGETS]->(Expense)  // Hub 5: Cost reduction

// Projects create tasks
(Project)-[:HAS_TASK]->(Task)
(Goal)-[:HAS_TASK]->(Task)
```

### Intelligence Aggregation (Bottom-Up)

```cypher
// Insights emerge from data
(Insight)-[:ABOUT]->(Tractor {unit_number: "6520"})  // Hub 3
(Insight)-[:ABOUT]->(Load {load_number: "OH-321678"})  // Hub 2
(Insight)-[:ABOUT]->(Customer)  // Hub 4
(Insight)-[:ABOUT]->(Expense)   // Hub 5

// Insights inform strategy
(Insight)-[:INFORMS]->(Project)
(Insight)-[:IMPACTS]->(Goal)
(Insight)-[:CREATES]->(Task)
```

### Knowledge Management

```cypher
// Knowledge supports execution
(KnowledgeItem)-[:SUPPORTS]->(Project)
(KnowledgeItem)-[:INFORMS]->(Goal)
(KnowledgeItem)-[:RELATED_TO]->(KnowledgeItem)  // Knowledge graph
```

### Measurement

```cypher
// Goals measured by business metrics
(Goal {title: "Grow Revenue"})-[:MEASURED_BY]->(Revenue)  // Hub 5
(Goal {title: "Reduce Costs"})-[:MEASURED_BY]->(Expense)  // Hub 5
(Goal {title: "Improve Utilization"})-[:MEASURED_BY]->(Tractor)  // Hub 3
```

---

## Database Distribution

### Neo4j (Relationship Memory)

**PRIMARY for:** Relationships only (no entity details)

**Stores:**
- G entity as central node (basic properties only)
- All ownership relationships (G → Companies)
- Project/Goal creation relationships
- Task/Project/Goal links
- Knowledge connections
- Insight → Entity links
- Cross-hub strategic relationships

**Example Queries:**
```cypher
// Strategic overview
MATCH (g:Person {user_id: "g_main"})-[:OWNS]->(entity:LegalEntity)
RETURN g, entity

// Project impact analysis
MATCH (p:Project {project_id: "proj_018c3a8b"})-[:TARGETS]->(loads:Load)
RETURN p, count(loads) as impacted_loads

// Goal measurement chain
MATCH (goal:Goal)-[:MEASURED_BY]->(revenue:Revenue)
WHERE goal.goal_id = "goal_openhaul_revenue_2025"
RETURN goal, sum(revenue.amount) as current_revenue
```

---

### PostgreSQL (Factual Memory)

**PRIMARY for:** All entity details

**Stores:**
- Complete Project records (descriptions, dates, status, progress)
- Complete Goal records (metrics, progress, targets)
- Complete Task records
- Complete KnowledgeItem content
- Complete Insight records
- Complete Asset metadata (NOT encrypted credentials)
- Complete Communication logs

**Example Queries:**
```sql
-- Active projects by priority
SELECT project_name, priority, progress_percentage, target_completion_date
FROM projects
WHERE status = 'active' AND owner_id = 'g_main'
ORDER BY priority ASC, target_completion_date ASC;

-- Goals with completion dates in Q1 2025
SELECT goal_title, target_date, progress_percentage
FROM goals
WHERE target_date BETWEEN '2025-01-01' AND '2025-03-31'
  AND status = 'active';

-- High-confidence insights needing action
SELECT title, category, impact_potential, recommendation
FROM insights
WHERE confidence_level IN ('high', 'validated')
  AND status = 'validated'
  AND impact_potential IN ('high', 'transformative')
ORDER BY priority ASC;
```

---

### Qdrant (Semantic Memory)

**PRIMARY for:** Document embeddings

**Stores:**
- KnowledgeItem embeddings (protocols, research, guides)
- Insight embeddings (for semantic search)
- Project documentation embeddings
- Communication transcript embeddings (if available)

**Example Queries:**
```python
# Find knowledge similar to current problem
qdrant.search(
    collection_name="knowledge_items",
    query_vector=embedding_of_current_problem,
    filter={"category": "biohacking"},
    limit=5
)

# Search insights about specific topic
qdrant.search(
    collection_name="insights",
    query_text="truck maintenance cost optimization",
    filter={"domain": "origin", "confidence_level": {"$gte": "medium"}},
    limit=10
)
```

---

### Redis (Working Memory)

**PRIMARY for:** Nothing (cache only)

**Stores (with TTL):**
- Current focus areas (60s TTL) → `focus:g_main`
- Active project list (300s TTL) → `projects:active:g_main`
- Recent insights (86400s TTL = 24h) → `insights:recent:g_main`
- Top priority tasks (300s TTL) → `tasks:priority:g_main`
- Goal progress dashboard (3600s TTL) → `goals:dashboard:g_main`

**Example Queries:**
```python
# Get current focus
redis.get("focus:g_main")
# Returns: ["OpenHaul Growth Q4 2025", "Fleet Profitability"]

# Get active projects (cached)
redis.get("projects:active:g_main")
# Returns: JSON array of active projects

# Get recent high-priority insights
redis.lrange("insights:recent:high_priority", 0, 9)
# Returns: Last 10 high-priority insights
```

---

### Graphiti (Temporal Memory)

**PRIMARY for:** Temporal entity tracking

**Stores:**
- Goal evolution (draft → active → achieved → archived)
- Project lifecycle (planning → active → completed)
- Focus shift tracking (what G was focused on 3 months ago)
- Insight emergence patterns
- Task completion velocity
- Priority shifts over time

**Example Queries:**
```python
# How has G's strategic focus changed?
graphiti.query_temporal(
    entity_type="Person",
    entity_id="g_main",
    property="current_focus",
    start_date="2025-01-01",
    end_date="2025-11-01"
)

# When did this goal become active?
graphiti.get_state_change(
    entity_type="Goal",
    entity_id="goal_openhaul_revenue_2025",
    property="status",
    value="active"
)

# Project completion timeline
graphiti.query_temporal(
    entity_type="Project",
    property="status",
    value="completed",
    start_date="2025-01-01"
)
```

---

## Cross-Hub Integration

### Hub 1 → Hub 2 (OpenHaul)

**Strategic Links:**
```cypher
// Ownership
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)

// Projects drive loads
(Project {name: "OpenHaul Q4 Growth"})-[:DRIVES]->(Load)

// Goals measured by revenue
(Goal {title: "Grow OpenHaul Revenue"})-[:MEASURED_BY]->(Revenue)

// Insights about carriers/loads
(Insight)-[:ABOUT]->(Carrier)
(Insight)-[:ABOUT]->(Load)
```

**Example Integration:**
- Project "OpenHaul Q4 Growth" targets $500K revenue
- Query Hub 2 for all loads where `source_entity = "OpenHaul"`
- Aggregate revenue from Hub 5
- Update Goal progress in Hub 1

---

### Hub 1 → Hub 3 (Origin)

**Strategic Links:**
```cypher
// Ownership
(G:Person)-[:OWNS {via: "Primetime", percentage: 100}]->(Origin:LegalEntity)

// Projects target fleet
(Project {name: "Fleet Optimization"})-[:TARGETS]->(Tractor)

// Goals measured by truck utilization
(Goal {title: "Improve Fleet Utilization"})-[:MEASURED_BY]->(Tractor)

// Insights about specific trucks/drivers
(Insight {title: "Unit #6520 high maintenance"})-[:ABOUT]->(Tractor {unit_number: "6520"})
```

**Example Integration:**
- Insight detects Unit #6520 has high maintenance costs
- Create Task: "Investigate Unit #6520 maintenance pattern"
- Link Task → Project: "Fleet Cost Reduction"
- Track in Goal: "Reduce Fleet Operating Costs 10%"

---

### Hub 1 → Hub 4 (Contacts)

**Strategic Links:**
```cypher
// G is a Person in Hub 4
(G:Person {user_id: "g_main"})-[:PERSON_RECORD]->(Person {person_id: "person_g"})

// G has relationships
(G:Person)-[:RELATIONSHIP_WITH {type: "business_partner"}]->(Travis:Person)

// Projects involve people
(Project)-[:INVOLVES]->(Person)

// Communications link to contacts
(Communication)-[:WITH]->(Person)
```

**Example Integration:**
- Communication with Travis (Hub 4 Person)
- Creates Task "Follow up with Travis on carrier recruitment"
- Links to Project "OpenHaul Q4 Growth"

---

### Hub 1 → Hub 5 (Financials)

**Strategic Links:**
```cypher
// Goals measured by financial metrics
(Goal {title: "Grow Revenue"})-[:MEASURED_BY]->(Revenue)
(Goal {title: "Reduce Costs"})-[:MEASURED_BY]->(Expense)

// Projects impact finances
(Project)-[:IMPACTS]->(Expense)
(Project)-[:DRIVES]->(Revenue)

// Insights about financial patterns
(Insight {title: "Q3 margin improvement"})-[:ABOUT]->(Revenue)
(Insight {title: "Fuel costs trending up"})-[:ABOUT]->(Expense)
```

**Example Integration:**
- Goal "Grow OpenHaul to $2M ARR"
- Query Hub 5: `SUM(revenue WHERE source_entity = 'OpenHaul')`
- Update Goal.progress_percentage based on current vs target
- Create Insight if revenue velocity changes

---

### Hub 1 → Hub 6 (Corporate)

**Strategic Links:**
```cypher
// G owns legal entities
(G:Person)-[:OWNS]->(Primetime:LegalEntity)
(G:Person)-[:OWNS]->(OpenHaul:LegalEntity {percentage: 50})

// Projects target corporate structure
(Project {name: "Corporate Structure Optimization"})-[:TARGETS]->(LegalEntity)

// Assets link to entities
(Asset {name: "Origin Bank Account"})-[:BELONGS_TO]->(Origin:LegalEntity)
```

**Example Integration:**
- Asset "Wells Fargo Business Account" belongs to Origin (Hub 6)
- Task "Review Origin bank reconciliation" links to both Hub 1 and Hub 6
- Goal "Optimize intercompany cash flow" measured by Hub 5 IntercompanyTransfer, linked to Hub 6 LegalEntity ownership structure

---

## Security & Privacy

**⚠️ CRITICAL: Hub 1 contains private, sensitive data**

### Access Levels

**1. Private to G (80% of data):**
- Personal health protocols
- Asset credentials (encrypted)
- Personal goals
- Private insights
- Personal communications
- Personal knowledge items

**2. Shared with Business Systems (20% of data):**
- Business projects
- Business goals
- Business insights
- Business-related communications
- Business knowledge items

**3. Encrypted (10% of data):**
- Asset.access_info (credentials)
- Asset.username (if sensitive)
- Personal health records (if tracked)
- Financial account details in Assets

### Implementation Requirements (Schema Notes Only)

**PostgreSQL:**
- Row-level security (RLS) filtering by `owner_id = 'g_main'`
- Encryption at rest for `Asset.access_info` field
- Audit logging for Asset access

**Qdrant:**
- Separate collection for private documents
- Filter by `visibility` field in metadata

**Neo4j:**
- Property-level access control (G relationships visible only to G)

**Redis:**
- Key namespacing: `g:private:*` vs `g:business:*`

**Note:** Schema defines structure and notes security requirements. **Implementation handles actual encryption, access control, and audit logging.**

---

## Validation Queries

### Cross-Database Consistency

**Test 1: G Entity Consistent Across Databases**
```cypher
// Neo4j
MATCH (g:Person {user_id: "g_main"})
RETURN g.name, g.email

// PostgreSQL
SELECT name, email FROM people WHERE user_id = 'g_main';

// Expected: Same values
```

**Test 2: Project Links to Goals**
```cypher
// Neo4j
MATCH (p:Project {project_id: "proj_018c3a8b"})-[:SUPPORTS]->(g:Goal)
RETURN p.project_name, collect(g.goal_title) as goals

// PostgreSQL
SELECT p.project_name, g.goal_title
FROM projects p
JOIN project_goals pg ON p.project_id = pg.project_id
JOIN goals g ON pg.goal_id = g.goal_id
WHERE p.project_id = 'proj_018c3a8b';

// Expected: Same goal lists
```

**Test 3: Insights Link to Cross-Hub Entities**
```cypher
// Verify insights reference valid entities
MATCH (i:Insight)-[:ABOUT]->(entity)
WHERE NOT exists(entity.unit_number)
  AND NOT exists(entity.load_number)
  AND NOT exists(entity.company_id)
RETURN count(i) as orphaned_insights

// Expected: 0 orphaned insights
```

---

## Success Criteria

**Hub 1 Complete Baseline (95%):**
- ✅ 8 entities defined with complete property lists (195 properties total)
- ✅ All relationships documented with properties
- ✅ Database distribution specified for every entity
- ✅ Cross-hub links defined for Hubs 2-6
- ✅ Security requirements documented (implementation separate)
- ✅ Real-world examples for each entity
- ✅ Validation queries provided
- ✅ Primary keys consistent with Phase 3 standards
- ✅ Temporal properties standardized
- ✅ Cross-database identity strategy validated

---

**Baseline Established:** November 4, 2025
**Schema Version:** v2.0 (Complete)
**Completion Status:** 95%
**Next:** Cross-hub validation with completed Hub 1
