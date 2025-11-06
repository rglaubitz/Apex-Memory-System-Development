# 00-overview: Project Overview Documents

**Purpose:** High-level strategic documents explaining the 6-hub schema philosophy and overall architecture.

---

## Documents in This Folder

### 1. [6-HUB-OVERVIEW.md](6-HUB-OVERVIEW.md)

**What it is:** Master navigation document for the entire 6-hub schema project.

**When to read:** Start here if you're new to the project.

**Contains:**
- Complete hub summary (all 6 hubs with entity counts)
- Cross-hub navigation guide
- Project status tracking
- Quick reference links

**Key Stats:**
- **45 entities** across 6 hubs
- **1,086 properties** total
- **5 databases** (PostgreSQL, Neo4j, Qdrant, Redis, Graphiti)
- **95% completion** for all hubs

---

### 2. [SCHEMA-PHILOSOPHY.md](SCHEMA-PHILOSOPHY.md)

**What it is:** Architectural principles and design decisions guiding the 6-hub schema.

**When to read:** Before making any schema changes or extensions.

**Contains:**
- Multi-database strategy rationale
- Bi-temporal tracking philosophy
- Primary key strategy (string vs UUID)
- Database distribution logic (PRIMARY vs REPLICA vs CACHE)
- Consistency patterns

**Key Principles:**
- PostgreSQL = PRIMARY (single source of truth)
- Neo4j = REPLICA (relationships and graph queries)
- Each database has distinct, complementary role
- Temporal tracking for time-travel queries

---

### 3. [Additional Schema info.md](Additional%20Schema%20info.md)

**What it is:** Supplementary schema information and edge cases.

**When to read:** When working on complex entity relationships or special cases.

**Contains:**
- Edge case handling
- Special relationship types
- Data transformation notes
- Historical context for design decisions

---

## Quick Start

**New to the project?** Read in this order:
1. **6-HUB-OVERVIEW.md** - Get the big picture
2. **SCHEMA-PHILOSOPHY.md** - Understand the "why" behind design decisions
3. **Additional Schema info.md** - Learn about edge cases

**Working on implementation?**
- Skip to [../03-implementation/](../03-implementation/) for production-ready schemas

**Working on validation?**
- Skip to [../02-phase3-validation/](../02-phase3-validation/) for validation documents
