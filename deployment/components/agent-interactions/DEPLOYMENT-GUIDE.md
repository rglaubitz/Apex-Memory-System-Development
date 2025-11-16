# Agent Interactions - Deployment Guide

**Feature:** Agent-to-Agent Communication Logging & Analysis
**Status:** ✅ Implemented (**DEFERRED to Post-Initial Deployment**)
**Impact:** Low - Nice-to-have, not core functionality
**Deployment Week:** Post-Initial

---

## ⚠️ DEFERRED TO POST-INITIAL DEPLOYMENT

**Rationale:**
- Nice-to-have feature, not critical for initial deployment
- Requires full agent ecosystem to be operational
- Better to deploy after production deployment is stable and validated
- Can be added incrementally without disrupting existing services

**When to Deploy:**
- After initial production deployment is stable (4-8 weeks post-launch)
- When multi-agent communication patterns are established
- If analytics on agent interactions become a business requirement

---

## Overview

Agent Interaction Service automatically logs and analyzes agent-to-agent communication, extracting entities and creating Graphiti episodes for high-importance interactions (importance >=0.6).

**Features:**
- Logs all interactions to PostgreSQL
- Extracts entities from interaction content
- Calculates importance scores
- Links to conversation context
- Creates knowledge graph episodes

**Dependencies:**
- PostgreSQL (agent_interactions table)
- GraphitiService
- NATS (if inter-agent messaging is used)

**Files:**
- Service: `src/apex_memory/services/agent_interaction_service.py` (17,208 bytes)
- Communication: `src/apex_memory/services/agent_communication.py` (18,636 bytes)
- API: `src/apex_memory/api/agent_interactions.py`

---

## Implementation Status

✅ **Code:** Fully implemented
✅ **Database:** Migration exists (`alembic/versions/1bf6df45f545_add_agent_interactions_table.py`)
✅ **Tests:** Integration tests exist (`tests/integration/test_agent_communication_e2e.py`)
❌ **Deployment:** Not included in initial deployment plan

---

## Future Deployment Steps

When ready to deploy (post-initial):

### Step 1: Run Migration

```bash
cd apex-memory-system
alembic upgrade head

# Verify table
export PGPASSWORD=apexmemory2024
psql -h POSTGRES_IP -U apex -d apex_memory -c "\d agent_interactions"
```

### Step 2: Enable in Application Code

No feature flags needed - service is opt-in via explicit calls.

### Step 3: Integrate with Agent Communication

Update agent communication code to call `AgentInteractionService.log_interaction()` for all inter-agent messages.

### Step 4: Verify API Endpoints

```bash
# List interactions
curl "$API_URL/api/v1/agent-interactions/"

# Get specific interaction
curl "$API_URL/api/v1/agent-interactions/{interaction_id}"
```

---

## Cost Impact

**$0/month** - Uses existing infrastructure

---

## References

- **Implementation:** `src/apex_memory/services/agent_interaction_service.py`
- **Migration:** `alembic/versions/1bf6df45f545_add_agent_interactions_table.py`
- **Tests:** `tests/integration/test_agent_communication_e2e.py`

---

**Deployment Status:** 📝 Deferred to Post-Initial Deployment
**Recommendation:** Deploy 4-8 weeks after initial production launch
**Next Step:** Proceed to Frontend (deferred)
