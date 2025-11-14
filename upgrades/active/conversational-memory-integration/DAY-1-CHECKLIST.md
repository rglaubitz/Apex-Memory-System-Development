# Day 1 Checklist - Multi-Agent Namespacing

**Purpose:** Critical pre-flight checks before Phase 1 implementation
**Time:** 30-45 minutes
**Status:** Track progress with checkboxes

---

## ✅ Checklist

### 1. Commit Documentation Changes (5 min)

```bash
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development

# Check what needs to be committed
git status

# Commit the multi-agent namespacing docs
git add upgrades/active/conversational-memory-integration/
git commit -m "docs: Add multi-agent namespacing strategy (Option A - Fluid Mind patterns)

- Created agent-registry.md with Oscar, Sarah, Maya, System definitions
- Updated ARCHITECTURE.md with Multi-Agent Namespacing Strategy section
- Updated README.md with agent-aware data flow diagrams
- Timeline: 7-9 weeks (6-8 weeks + 1 week for multi-agent patterns)
- Added Redis namespaces, Qdrant collections, PostgreSQL schema prep patterns"

git push
```

**Status:** [ ] Complete

---

### 2. Verify Baseline Tests Pass (10 min)

```bash
cd apex-memory-system

# Activate virtual environment
source venv/bin/activate

# Run baseline tests (MUST pass before proceeding)
pytest tests/ --ignore=tests/load/ -v --tb=short

# Expected: All tests passing (156+ tests)
```

**Document Results:**
- [ ] All tests passing
- Baseline count: _____ tests passing
- Any failures: _____ (MUST be 0 to proceed)

**🔴 BLOCKER:** If any tests fail, fix before proceeding.

---

### 3. Verify All Services Running (5 min)

```bash
cd apex-memory-system/docker
docker-compose ps

# Expected services UP:
# ✅ neo4j (port 7474)
# ✅ postgresql (port 5432)
# ✅ qdrant (port 6333)
# ✅ redis (port 6379)
# ✅ temporal (port 8088)
```

**Status:** [ ] All services running

**Action if services down:**
```bash
docker-compose up -d
```

---

### 4. Run Database Validations (15 min)

#### 4a. Redis Validation

```bash
cd apex-memory-system
source venv/bin/activate
python scripts/validation/test_redis_namespacing.py
```

**Expected Output:**
```
✅ Redis connection successful
✅ Test 1 PASSED: Keys isolated correctly
✅ Test 2 PASSED: TTL working
✅ Test 3 PASSED: Shared and agent keys coexist
✅ ALL REDIS TESTS PASSED
```

**Status:** [ ] Redis validation passed

---

#### 4b. Qdrant Validation

```bash
python scripts/validation/test_qdrant_collections.py
```

**Expected Output:**
```
✅ Qdrant connection successful
✅ Created: test_oscar_fleet
✅ Created: test_sarah_finance
✅ Created: test_maya_sales
✅ Collections isolated correctly
✅ ALL QDRANT TESTS PASSED
```

**Status:** [ ] Qdrant validation passed

---

#### 4c. PostgreSQL Validation

```bash
python scripts/validation/test_postgresql_schemas.py
```

**Expected Output:**
```
✅ PostgreSQL connection successful
✅ Created schema: test_oscar
✅ Created schema: test_sarah
✅ Created schema: test_maya
✅ Created schema: test_core
✅ Schema isolation working correctly
✅ ALL POSTGRESQL TESTS PASSED
```

**Status:** [ ] PostgreSQL validation passed

**⚠️ Important:** Note if `agent_id` column exists:
- [ ] agent_id column EXISTS (no migration needed)
- [ ] agent_id column DOES NOT EXIST (will add in Phase 1)

---

#### 4d. Run All Validations (Quick Script)

```bash
# Alternative: Run all three tests at once
./scripts/validation/run_all_validations.sh
```

**Status:** [ ] All validations passed

---

### 5. Check Current Database Schema (5 min)

```bash
# Check conversations table structure
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "\d conversations"

# Look for: agent_id column
```

**Document Schema:**
```
Column            |  Type  | Modifiers
------------------+--------+-----------
uuid              | uuid   | PRIMARY KEY
user_id           | uuid   |
agent_id          | ???    | ← Does this exist?
created_at        | timestamp |
```

**Status:**
- [ ] Schema reviewed
- [ ] agent_id exists: YES / NO

---

## Go/No-Go Decision

### 🟢 PROCEED TO PHASE 1 if ALL checked:

- [ ] Documentation committed and pushed
- [ ] All baseline tests passing (_____ tests)
- [ ] All services running (Neo4j, PostgreSQL, Qdrant, Redis, Temporal)
- [ ] Redis validation passed
- [ ] Qdrant validation passed
- [ ] PostgreSQL validation passed

### 🔴 DO NOT PROCEED if ANY of these:

- [ ] Any baseline tests failing
- [ ] Services not running
- [ ] Database connection issues
- [ ] Validation scripts failed

---

## Next Steps After Completion

Once all checklist items are ✅:

1. **Create implementation branch**
   ```bash
   git checkout -b feature/multi-agent-namespacing
   ```

2. **Begin Day 2: Database Schema Updates**
   - Create `config/agent_registry.py`
   - Create Alembic migration for `agent_id` column (if needed)

3. **Update todo list for Phase 1**

---

## Troubleshooting

### Redis Connection Failed
```bash
# Check if Redis is running
docker ps | grep redis

# Restart if needed
cd apex-memory-system/docker
docker-compose restart redis
```

### Qdrant Connection Failed
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart if needed
docker-compose restart qdrant
```

### PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart if needed
docker-compose restart postgresql
```

### Baseline Tests Failing
```bash
# Run tests with more verbose output
pytest tests/ --ignore=tests/load/ -v --tb=long

# Identify specific failure
# Fix issue before proceeding
```

---

**Completion Time:** _____ minutes (target: 30-45 min)
**Ready for Phase 1:** YES / NO
**Date:** ___________

---

**Next Document:** Begin Phase 1 implementation (create config module, database migration)
