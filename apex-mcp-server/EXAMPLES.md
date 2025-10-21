# Apex MCP Server - Usage Examples

Real-world examples of using Apex Memory with Claude Desktop.

## Basic Memory Storage

### Store Simple Memory

```
You: "Remember that I prefer Python over JavaScript for backend development"

Claude: ✅ Memory stored successfully!

        Entities extracted:
        - Python
        - JavaScript
        - Backend Development

        Relationships created:
        - User → PREFERS → Python
        - Python → USE_CASE_FOR → Backend Development

        This memory is now stored across your 4-database knowledge graph.
```

### Store Conversation

```
You: "Here's a conversation I had:
     User: I need help with Invoice INV-001
     Agent: I see INV-001 for ACME Corp. How can I help?
     User: Can you update the payment status to paid?"

Claude: ✅ Conversation stored!

        3 messages processed
        Entities extracted: Invoice INV-001, ACME Corp, Payment Status
        Relationships: Invoice → BELONGS_TO → ACME Corp

        I can now answer questions about this invoice.
```

---

## Searching Memories

### Basic Search

```
You: "What do you know about ACME Corporation?"

Claude: [Searches knowledge graph]

        I found 7 results about ACME Corporation:

        1. ACME Corp ordered 50 brake parts from Bosch (Jan 15)
        2. ACME Invoice INV-001 payment status updated to paid
        3. ACME Corp is in the Manufacturing community
        ...
```

### Semantic Search

```
You: "What companies have I worked with on brake systems?"

Claude: [Semantic search across entities]

        Based on your knowledge graph:

        1. ACME Corporation - Primary customer, 12 documents
        2. Bosch - Supplier for brake parts
        3. Brembo - Secondary supplier (added March 2025)

        All three are connected through brake systems relationships.
```

---

## The Power of ask_apex()

### Comprehensive Entity Exploration

```
You: "Tell me everything you know about ACME Corporation"

Claude: [Orchestrates 6 queries: search + graph + temporal + patterns + communities + analytics]

        I've analyzed ACME Corporation across your entire knowledge graph. Here's what I found:

        📊 Overview
        ACME Corporation is one of your most important entities with:
        - 12 associated documents
        - 8 connected entities
        - 3 months of tracked history
        - Member of 2 communities (Manufacturing, Suppliers)

        🔗 Key Relationships
        Primary supplier: Bosch (83% of orders)
        - 7 orders placed, totaling 350 brake parts
        - Relationship established: December 2024

        Secondary supplier: Brembo (17% of orders)
        - Recently added: March 2025
        - 2 orders placed, totaling 100 parts

        📈 Patterns Detected
        ✨ Recurring ordering pattern: Every 3-4 weeks (89% consistency)
        ✨ Typical order size: 50-75 brake parts
        ✨ Recent supplier diversification suggests strategic risk management

        📍 Timeline
        Dec 2024: Relationship established
        Jan 2025: First order (50 brake pads from Bosch)
        Feb 2025: Ordering pattern stabilized
        Mar 2025: Added Brembo as secondary supplier

        💡 Insights
        ACME is a stable, predictable customer. Their recent supplier change
        from Bosch-only to Bosch+Brembo indicates strategic risk mitigation.
        They're highly connected (8 relationships) making them a hub entity
        in your supply chain knowledge graph.

        Would you like me to investigate:
        - Why did ACME switch suppliers in March?
        - Compare ACME's ordering patterns to other customers
        - Show me ACME's complete supplier history
```

### Temporal Analysis

```
You: "What changed in my knowledge graph this week?"

Claude: [Orchestrates: temporal search + analytics + pattern detection]

        Knowledge graph changes (last 7 days):

        📊 Overview
        - 5 new entities added (3 organizations, 2 people)
        - 12 new relationships created
        - 2 communities updated

        ✨ Key Changes
        1. ACME Corporation switched suppliers
           - Before: Bosch only
           - Now: Bosch (primary) + Brembo (secondary)
           - Detected: March 1, 2025

        2. New community formed: "Brake Systems Suppliers"
           - Members: Bosch, Brembo, ACME Corp, You
           - Confidence: 0.92

        3. Invoice INV-001 payment completed
           - Status change: Pending → Paid
           - Date: March 3, 2025

        📈 Emerging Patterns
        - Supplier diversification trend detected (2 customers)
        - Average order size increased 15% this week
        - 3 new brake systems projects mentioned

        Next steps suggested:
        - Analyze supplier diversification trend
        - Compare week-over-week growth
        - Check for similar patterns in other entities
```

### Relationship Exploration

```
You: "How are ACME and Bosch connected?"

Claude: [Orchestrates: search both + find path + temporal context]

        ACME and Bosch connection analysis:

        🔗 Direct Connections (3 paths found)
        1. ACME → ORDERED_FROM → Bosch (Primary)
           - Strength: 7 orders
           - First: Jan 15, 2025
           - Last: Feb 28, 2025

        2. ACME → USES_PARTS_FROM → Bosch
           - Brake pads, brake rotors
           - Quality rating: High

        3. Via You (shared context):
           - You → WORKS_WITH → ACME
           - You → EVALUATES → Bosch

        📈 Evolution Over Time
        Dec 2024: No connection
        Jan 2025: First order established
        Feb 2025: Relationship strengthened (5 more orders)
        Mar 2025: ACME added Brembo, Bosch share decreased to 83%

        💡 Insights
        Bosch has been ACME's primary supplier for brake systems for 3 months.
        Recent addition of Brembo suggests ACME is reducing supplier risk,
        but Bosch remains dominant with 83% share.

        Follow-up questions:
        - Why did ACME add Brembo as a supplier?
        - What other customers use Bosch?
        - Compare Bosch and Brembo pricing/quality
```

---

## Temporal Queries

### Point-in-Time Query

```
You: "What was ACME's supplier situation in January?"

Claude: [Temporal search at Jan 31, 2025]

        ACME Corporation supplier status (January 2025):

        Active Supplier:
        - Bosch (exclusive supplier)
        - First order: Jan 15, 2025
        - Status: Active

        No other suppliers in January.

        Note: Brembo was added as secondary supplier in March 2025.
```

### Entity Timeline

```
You: "Show me how ACME evolved over time"

Claude: [Gets entity timeline]

        ACME Corporation Timeline:

        📅 December 2024
        - Dec 1: Entity first mentioned
        - Dec 15: Relationship with Bosch established

        📅 January 2025
        - Jan 15: First order placed (50 brake pads)
        - Jan 22: Second order (75 brake rotors)

        📅 February 2025
        - Feb 5: Order pattern stabilized (weekly orders)
        - Feb 12: Third order (50 brake pads)
        - Feb 19: Fourth order (60 brake rotors)

        📅 March 2025
        - Mar 1: Brembo added as secondary supplier
        - Mar 5: First Brembo order (50 brake pads)

        Growth: From 1 entity → 8 connected entities in 3 months
```

---

## Analytics & Insights

### Graph Statistics

```
You: "Give me an overview of my knowledge graph"

Claude: [Gets graph stats]

        Knowledge Graph Overview:

        📊 Size
        - Total Entities: 1,247
        - Total Relationships: 3,891
        - Total Communities: 23

        📈 Growth
        - Entities added this week: 5
        - Relationships added this week: 12
        - Graph density: 0.42 (well-connected)

        🏆 Top Entities (by connections)
        1. ACME Corporation (45 connections)
        2. Bosch (38 connections)
        3. Brake Systems (35 connections)

        🏘️ Communities
        - Manufacturing (48 members)
        - Suppliers (35 members)
        - Projects (27 members)

        ✅ Graph Health
        - Orphaned entities: 5 (0.4% - excellent)
        - Average relationships per entity: 3.1
        - Health score: 94/100
```

---

## Advanced Patterns

### Pattern Detection

```
You: "What patterns do you see in customer orders?"

Claude: [Orchestrates pattern detection]

        Order Pattern Analysis:

        ✨ Recurring Patterns Detected

        1. Weekly Ordering Cycle
           - 3 customers order every 7 days (±1 day)
           - Consistency: 89%
           - Customers: ACME, Beta Inc, Gamma Co

        2. Order Size Clustering
           - Small: 20-40 units (40% of orders)
           - Medium: 50-75 units (45% of orders)
           - Large: 100+ units (15% of orders)

        3. Supplier Diversification Trend
           - 2 customers added secondary suppliers this month
           - Risk mitigation pattern detected

        4. Seasonal Variation
           - Order frequency increases 20% early in month
           - Likely tied to monthly budget cycles

        Recommendations:
        - Prepare for early-month demand spike
        - Consider bulk pricing for medium orders (50-75 units)
        - Monitor supplier diversification trend
```

---

## Multi-Turn Conversations

```
You: "Remember my conversation with the sales team:
     Me: What's our Q1 revenue target?
     Sales: $500K, focusing on brake systems
     Me: Which customers are priority?
     Sales: ACME and Beta Inc"

Claude: ✅ Conversation stored!

You: "What was the Q1 target?"

Claude: Based on your conversation with the sales team:
        Q1 revenue target: $500K
        Focus area: Brake systems
        Priority customers: ACME Corp, Beta Inc

You: "Are we on track?"

Claude: Let me check the current status against your Q1 target...

        [Searches orders, calculates totals]

        Current Status (as of March 5):
        - Total revenue: $325K (65% of $500K target)
        - From brake systems: $310K (95% of revenue)
        - From priority customers: $280K (86% of revenue)

        You're tracking well! 2 months remaining to reach $500K.
        Current run rate suggests you'll hit $487K by end of Q1.
```

---

## Tips & Best Practices

### 1. Be Specific with ask_apex()

**Good:**
```
"Tell me everything you know about ACME Corporation's supplier relationships"
```

**Better:**
```
"Analyze ACME Corporation's supplier relationships over the last 3 months.
 Include ordering patterns, supplier changes, and any detected trends."
```

### 2. Use Temporal Context

**Instead of:**
```
"What changed?"
```

**Try:**
```
"What changed in my knowledge graph this week?"
"How did ACME evolve from January to March?"
"What was the supplier situation in February?"
```

### 3. Leverage Communities

```
You: "What are my main knowledge clusters?"

Claude: [Gets communities]

        You have 23 knowledge communities:

        Top 5:
        1. Work (48 entities) - ACME, Projects, Suppliers
        2. Programming (37 entities) - Python, JavaScript, Tools
        3. Personal (25 entities) - Hobbies, Travel, Family
        ...

You: "Tell me about my Work community"

Claude: [Deep dive into Work community context]
```

### 4. Ask for Comparisons

```
"Compare ACME and Beta Inc as customers"
"Which supplier has better order consistency - Bosch or Brembo?"
"How does my Q1 performance compare to Q4?"
```

---

## Next Steps

- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Read [README.md](README.md) for complete feature list
- Check [INSTALLATION.md](INSTALLATION.md) for setup details
