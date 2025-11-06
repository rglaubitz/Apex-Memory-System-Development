# Claude Quick Reference - Graphiti + JSON Integration

**Last Updated:** 2025-11-05
**Current Phase:** Week 1, Days 1-2 Complete

---

## 🚀 Quick Resume Commands

### Start All Services
```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
cd docker && docker-compose up -d && cd ..
source venv/bin/activate
```

### Run Test Baseline (Phase 3)
```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
pytest tests/ -v --ignore=tests/load/ | tee /tmp/test-baseline-unified-schemas.log
```

### Verify Services
```bash
# Neo4j
curl http://localhost:7474

# PostgreSQL
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT 1"

# Temporal
curl http://localhost:8233
```

---

## 📂 Key File Locations

### Entity Schemas (NEW)
```
/Users/richardglaubitz/Projects/apex-memory-system/src/apex_memory/models/entities/
├── __init__.py
├── base.py              # BaseEntity, Hub enum, llm_field(), manual_field()
├── customer.py          # 42 Tier 2 properties, 12 LLM-extractable
├── person.py            # 37 Tier 2 properties, 15 LLM-extractable
├── invoice.py           # 18 Tier 2 properties, 6 LLM-extractable
├── truck.py             # 40 Tier 2 properties, 18 LLM-extractable
└── load.py              # 40 Tier 2 properties, 16 LLM-extractable
```

### Entity Helpers (NEW)
```
/Users/richardglaubitz/Projects/apex-memory-system/src/apex_memory/utils/entity_schema_helpers.py
```

### Modified Files
```
/Users/richardglaubitz/Projects/apex-memory-system/src/apex_memory/
├── services/graphiti_service.py           # get_entity_types(), auto-config
├── temporal/activities/ingestion.py       # extract_entities_activity() updated
├── database/neo4j_writer.py               # Hub-based labels (:Customer, :Person)
└── database/postgres_writer.py            # Tier 3 JSONB storage
```

### Documentation
```
/Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/temporal-implementation/graphiti-json-integration/
├── README.md                      # Entry point
├── HANDOFF-WEEK1-DAYS1-2.md      # Complete session documentation
├── PROGRESS.md                    # Progress tracker
├── CLAUDE-QUICK-REFERENCE.md     # This file
├── IMPLEMENTATION.md              # Step-by-step guide
├── TESTING.md                     # Test specifications
└── TROUBLESHOOTING.md             # Common issues
```

---

## 💻 Common Code Patterns

### Pattern 1: Get LLM-Extractable Fields
```python
from apex_memory.utils.entity_schema_helpers import get_llm_extractable_fields
from apex_memory.models.entities import Customer

# Get only fields marked llm_extractable=True
llm_fields = get_llm_extractable_fields(Customer)
# Returns: 12 of 42 fields
```

### Pattern 2: Create LLM Extraction Model
```python
from apex_memory.utils.entity_schema_helpers import create_llm_extraction_model
from apex_memory.models.entities import Person

# Create lightweight model for Graphiti
PersonLLM = create_llm_extraction_model(Person)
# PersonLLM has 15 fields vs Person's 37 fields
```

### Pattern 3: Get Entity Types for Graphiti
```python
from apex_memory.utils.entity_schema_helpers import get_entity_types_for_graphiti

# Get all 5 entity types
entity_types = get_entity_types_for_graphiti()
# Returns: {"Customer": CustomerLLMExtraction, "Person": PersonLLMExtraction, ...}

# Get specific subset
entity_types = get_entity_types_for_graphiti(include_entities=['Customer', 'Person'])
```

### Pattern 4: Hub Assignment
```python
from apex_memory.utils.entity_schema_helpers import (
    get_hub_for_entity_type,
    validate_hub_assignment
)

# Get hub for entity type
hub = get_hub_for_entity_type('customer')  # Returns: 'contacts'

# Validate assignment
is_valid = validate_hub_assignment('customer', 'contacts')  # True
```

### Pattern 5: Use Graphiti with Unified Schemas
```python
from apex_memory.services.graphiti_service import GraphitiService

graphiti = GraphitiService(...)

# Auto-configure all 5 entity types (default)
result = await graphiti.add_document_episode(
    document_uuid="doc-123",
    document_content=content,
    use_unified_schemas=True  # Default
)

# Manual control
entity_types = graphiti.get_entity_types()
result = await graphiti.add_document_episode(
    document_uuid="doc-123",
    document_content=content,
    entity_types=entity_types,
    use_unified_schemas=False
)
```

### Pattern 6: Unified Entity Format
```python
# Entity dict structure after extraction
entity = {
    # Tier 1: Core (always present)
    'uuid': 'person_john_xyz',
    'name': 'John Doe',
    'hub': 'contacts',
    'entity_type': 'person',

    # Tier 2: LLM-Extracted (optional, when available)
    'full_name': 'John Doe',
    'phone': '555-1234',
    'email': 'john@example.com',

    # Tier 3: Catch-all (always present)
    'additional_properties': {
        'custom_field': 'value'
    },
    'extracted_fields_not_in_schema': [
        'custom_field'
    ]
}
```

---

## 🧪 Testing Commands

### Run All Tests
```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Exclude load tests
pytest tests/ -v --ignore=tests/load/

# Single test file
PYTHONPATH=src:$PYTHONPATH pytest tests/unit/test_graphiti_extraction_activity.py -v
```

### Test with Coverage
```bash
pytest tests/ --cov=apex_memory --cov-report=html
open htmlcov/index.html
```

---

## 🔍 Debugging Commands

### Check Neo4j Labels
```cypher
// Neo4j Browser: http://localhost:7474
MATCH (n) RETURN DISTINCT labels(n) AS labels, count(n) AS count
```

### Check PostgreSQL Entity Metadata
```sql
-- psql connection
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory

-- Query entity metadata
SELECT
    uuid,
    entity_type,
    name,
    metadata->'_hub' as hub,
    metadata->'_additional_properties' as tier3,
    metadata->'_extracted_fields_not_in_schema' as audit
FROM hub6_corporate.entities
LIMIT 10;
```

### Check Graphiti Episodes
```bash
# View Temporal UI
open http://localhost:8233

# Check Graphiti episode count
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory \
  -c "SELECT COUNT(*) FROM graphiti.episodes"
```

---

## 📊 Entity Schema Quick Reference

| Entity | Hub | Tier 2 Props | LLM Extract | Example Fields |
|--------|-----|--------------|-------------|----------------|
| Customer | Contacts | 42 | 12 (29%) | company_name, website, phone, address |
| Person | Contacts | 37 | 15 (41%) | full_name, email, phone, title, department |
| Invoice | Financials | 18 | 6 (33%) | invoice_number, total_amount, due_date |
| Truck | Origin | 40 | 18 (45%) | unit_number, make, model, vin, year |
| Load | OpenHaul | 40 | 16 (40%) | load_number, pickup_date, delivery_date |

**Total:** 177 Tier 2 properties, 67 LLM-extractable (38%)

---

## 🛠️ Troubleshooting

### Issue: Tests failing with `:Entity` labels
**Cause:** Tests expect old `:Entity` label, now using `:Customer`, `:Person`, etc.
**Fix:** Update test expectations in Phase 3, Task 3.1

### Issue: Tier 2 fields not populated
**Expected:** Tier 2 population requires Graphiti Node objects (Week 1, Day 3-4 enhancement)
**Current:** Only Tier 1 fields populated (uuid, name, hub, entity_type)

### Issue: Entity type misclassification
**Cause:** Pattern-based inference may misclassify ambiguous names
**Mitigation:** Enhance patterns in `infer_entity_type()` function
**Future:** Graphiti will provide explicit entity typing

---

## 📚 Hub Registry (45 Entities)

```python
# Hub 1: G (Command Center) - 8 entities
task, goal, project, note, reminder, calendar_event, decision, strategy

# Hub 2: OpenHaul (Brokerage) - 8 entities
load, carrier, rate_confirmation, bill_of_lading, proof_of_delivery,
carrier_packet, dispatch, freight_claim

# Hub 3: Origin Transport - 7 entities
truck, trailer, driver, fuel_transaction, maintenance_record,
insurance, accident_report

# Hub 4: Contacts/CRM - 7 entities
customer, person, vendor, broker, shipper, consignee, contact_interaction

# Hub 5: Financials - 8 entities
expense, revenue, invoice, payment, loan, bank_account,
intercompany_transfer, budget

# Hub 6: Corporate - 7 entities
legal_entity, license, permit, insurance_policy, contract,
compliance_record, property
```

---

## 🎯 Next Tasks (Phase 3)

### Task 3.1: Fix Test Failures (2 hours)
```bash
# Run baseline
pytest tests/ -v --ignore=tests/load/ > /tmp/failures.txt

# Fix test expectations
# - Update `:Entity` → `:Customer`, `:Person`, etc.
# - Verify JSONB storage
# - Validate hub assignments
```

### Task 3.2: Create Staging Infrastructure (1 hour)
```bash
# Create StagingManager service
# - /tmp/apex-staging/ directory structure
# - TTL cleanup for failed ingestions
```

### Task 3.3: Fix Staging Tests (1 hour)
```bash
# Update staging tests for unified schema format
```

---

**Quick Start:** Copy "Start All Services" commands above to resume work immediately.
