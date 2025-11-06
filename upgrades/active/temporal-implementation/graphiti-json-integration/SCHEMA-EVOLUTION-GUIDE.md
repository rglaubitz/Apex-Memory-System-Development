# Schema Evolution Guide - Option D+ Architecture

**Created:** 2025-11-05
**Last Updated:** 2025-11-05
**Status:** Active
**Architecture:** Option D+ (Hub Rigidity + Property Flexibility)

---

## Table of Contents

1. [Overview](#overview)
2. [Three-Tier Property System](#three-tier-property-system)
3. [Evolution Philosophy](#evolution-philosophy)
4. [Weekly Review Process](#weekly-review-process)
5. [Promotion Criteria](#promotion-criteria)
6. [Migration Workflow](#migration-workflow)
7. [Tools & APIs](#tools--apis)
8. [Examples](#examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Schema Evolution System enables data-driven promotion of fields from **Tier 3** (unstructured catch-all) to **Tier 2** (structured schema) based on actual usage patterns.

### Key Principles

1. **Never lose data** - Everything goes into Tier 3 if it doesn't match Tier 2
2. **Evidence-based evolution** - Promote fields based on usage metrics (>40% threshold)
3. **Backward compatible** - Old entities continue to work with new schemas
4. **Hub rigidity maintained** - Schema evolution doesn't allow new hubs (architectural governance)

### Architecture Benefits

- **Flexible ingestion** - Accept any data from Graphiti/JSON sources
- **Structured querying** - Query promoted fields efficiently
- **Audit trail** - Track which extracted fields didn't match schema
- **Data-driven** - Promote only fields that prove useful

---

## Three-Tier Property System

Every entity in Apex Memory uses a three-tier property system:

```
┌─────────────────────────────────────────────────────────┐
│ TIER 1: CORE (REQUIRED)                                 │
│ - uuid, name, hub, entity_type, created_at, updated_at  │
│ - RIGID: Must exist for entity to be valid              │
│ - Never changes without major architecture review       │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│ TIER 2: STRUCTURED (OPTIONAL)                           │
│ - Typed Backbone schema fields                          │
│ - llm_extractable flag (some LLM-extractable, some not) │
│ - SEMI-FLEXIBLE: Can add new fields via evolution       │
│ - Examples: full_name, company_name, phone, email       │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│ TIER 3: DYNAMIC (CATCH-ALL)                             │
│ - additional_properties: Dict[str, Any]                 │
│ - extracted_fields_not_in_schema: List[str] (audit)     │
│ - FLEXIBLE: Anything goes here                          │
│ - Future candidates for Tier 2 promotion                │
└─────────────────────────────────────────────────────────┘
```

### Storage Locations

| Tier | Neo4j | PostgreSQL |
|------|-------|------------|
| Tier 1 | Node labels + core properties | Dedicated columns |
| Tier 2 | Node properties | `metadata` JSONB column |
| Tier 3 | `additional_properties` JSON | `metadata->>'_additional_properties'` |

---

## Evolution Philosophy

### When to Promote a Field

✅ **Promote when:**
- Field appears in >40% of entities of a given type
- Consistent data type across usages (e.g., always string)
- Meaningful semantic value (not UUID fragments, random data)
- Need to query/index this field frequently
- Field provides business value for analytics

❌ **Don't promote when:**
- Field usage is sporadic (<40%)
- Data type inconsistent (sometimes string, sometimes number)
- Temporary/experimental field
- Field only used in specific edge cases
- Already covered by existing Tier 2 field

### Promotion Threshold: 40%

**Why 40%?**
- High enough to avoid schema bloat from rare fields
- Low enough to catch genuinely useful patterns
- Balances structured querying vs. flexibility
- Evidence-based (not arbitrary)

**Examples:**
- 10% usage → Stay in Tier 3 (too rare)
- 45% usage → Promote to Tier 2 ✅ (useful pattern)
- 80% usage → Definitely promote ✅✅ (critical field)

---

## Weekly Review Process

### Schedule

**Frequency:** Every Monday @ 10:00 AM
**Duration:** 30-60 minutes
**Owner:** Engineering Lead + Data Team

### Steps

#### 1. Run Analysis (5 minutes)

```bash
# Navigate to main codebase
cd /Users/richardglaubitz/Projects/apex-memory-system

# Run schema evolution analysis
export PYTHONPATH=src:$PYTHONPATH
python -m apex_memory.utils.schema_evolution --output weekly_report.json

# Or use API:
curl -X GET "http://localhost:8000/api/admin/schema/evolution/analyze" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### 2. Review Promotion Candidates (15 minutes)

For each candidate field (>40% usage):

**Questions to ask:**
- Is this field semantically meaningful?
- Does it provide business value for queries/analytics?
- Is the data type consistent?
- Would indexing this field improve performance?
- Is this a duplicate of an existing Tier 2 field?

**Decision:**
- ✅ **Promote** - If yes to most questions
- ⏸️ **Wait** - If uncertain, wait another week
- ❌ **Reject** - If field is noise/temporary

#### 3. Generate Migration Plans (10 minutes)

For each field approved for promotion:

```bash
# Using CLI
python -m apex_memory.utils.schema_migration_generator \
  emergency_contact person str \
  --hub contacts \
  --llm-extractable \
  --description "Emergency contact phone number" \
  --usage-percentage 67.3 \
  --output-dir migrations/2025-11-05/

# Or use API:
curl -X POST "http://localhost:8000/api/admin/schema/evolution/promote" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "emergency_contact",
    "entity_type": "person",
    "python_type": "str",
    "hub": "contacts",
    "llm_extractable": true,
    "description": "Emergency contact phone number"
  }'
```

#### 4. Execute Migrations (20 minutes)

For each promotion (see [Migration Workflow](#migration-workflow) below):

1. Update Pydantic entity model
2. Run tests
3. Apply PostgreSQL migration (optional JSONB index)
4. Apply Neo4j migration (data migration)
5. Verify success
6. Commit changes

#### 5. Document Decisions (10 minutes)

Log decisions in tracking spreadsheet:

| Date | Field Name | Entity Type | Usage % | Decision | Reason |
|------|------------|-------------|---------|----------|--------|
| 2025-11-05 | emergency_contact | person | 67.3% | ✅ Promoted | High usage, consistent type |
| 2025-11-05 | temp_field_xyz | customer | 12.4% | ❌ Rejected | Low usage, experimental |

---

## Promotion Criteria

### Criteria Checklist

For a field to be promoted from Tier 3 → Tier 2, it must meet:

#### 1. Usage Threshold ✅
- **Requirement:** >40% usage rate for entity type
- **Check:** `field.usage_percentage > 40.0`
- **Example:** If "emergency_contact" appears in 67% of Person entities → Promote

#### 2. Data Type Consistency ✅
- **Requirement:** Dominant data type >80% of usages
- **Check:** `max(field.data_types.values()) / field.usage_count > 0.8`
- **Example:** If "phone" is string in 95% of cases → Promote

#### 3. Semantic Value ✅
- **Requirement:** Field provides business/analytical value
- **Check:** Manual review (is this queryable? useful for insights?)
- **Example:** "customer_tier" (Bronze/Silver/Gold) → High value, promote

#### 4. No Duplication ✅
- **Requirement:** Field doesn't duplicate existing Tier 2 field
- **Check:** Review existing entity schema
- **Example:** If "full_name" already exists, don't promote "name_full"

#### 5. Stability ✅
- **Requirement:** Field is not experimental/temporary
- **Check:** Field appears consistently over time (check first_seen/last_seen)
- **Example:** Field appeared 3 months ago, still in use → Stable, promote

---

## Migration Workflow

### Complete Workflow (15-30 minutes per field)

#### Step 1: Generate Migration Plan

```bash
# Generate complete migration artifacts
python -m apex_memory.utils.schema_migration_generator \
  website customer str \
  --hub contacts \
  --llm-extractable \
  --description "Company website URL" \
  --usage-percentage 72.1 \
  --usage-count 184 \
  --output-dir migrations/2025-11-05-website/

# Output:
# migrations/2025-11-05-website/
# ├── PROMOTION_PLAN_website.md       # Summary
# ├── pydantic_website_promotion.txt  # Pydantic instructions
# ├── alembic_website_migration.py    # PostgreSQL index migration
# └── neo4j_website_migration.cypher  # Neo4j data migration
```

#### Step 2: Update Pydantic Entity Model

```bash
# Open entity file
code src/apex_memory/models/entities/customer.py

# Add field to Customer class (copy from pydantic_website_promotion.txt)
```

**Example:**
```python
class Customer(BaseEntity):
    """Customer entity with full Backbone schema."""

    # ... existing fields ...

    # NEW FIELD (promoted from Tier 3)
    website: Optional[str] = Field(
        None,
        description="Company website URL",
        json_schema_extra={'llm_extractable': True}
    )
```

#### Step 3: Run Tests

```bash
# Verify schema still valid
cd /Users/richardglaubitz/Projects/apex-memory-system
export PYTHONPATH=src:$PYTHONPATH

# Test entity schemas
pytest tests/unit/test_entity_schemas.py -v

# Test Graphiti extraction with new field
pytest tests/unit/test_graphiti_extraction_activity.py -v
```

#### Step 4: Apply PostgreSQL Migration (Optional)

**Note:** For Option D+, we store Tier 2 in metadata JSONB, so column additions aren't needed. However, we can add GIN index for query performance.

```bash
# Apply Alembic migration
cd migrations
alembic upgrade head

# Or run migration SQL manually:
psql -U apex -d apex_memory -f alembic_website_migration.py
```

#### Step 5: Apply Neo4j Migration

**Purpose:** Migrate existing data from additional_properties → top-level property

```bash
# Execute Cypher migration
cat neo4j_website_migration.cypher | cypher-shell \
  -u neo4j \
  -p apexmemory2024 \
  --database neo4j

# Verify migration
cypher-shell -u neo4j -p apexmemory2024 << EOF
MATCH (c:Customer)
WHERE c.website IS NOT NULL
RETURN count(c) AS migrated_customers;
EOF
```

#### Step 6: Verify Success

```bash
# PostgreSQL verification
psql -U apex -d apex_memory -c "
SELECT
  COUNT(*) FILTER (WHERE metadata->>'website' IS NOT NULL) AS with_website,
  COUNT(*) AS total_customers
FROM hub6_corporate.entities
WHERE entity_type = 'customer';
"

# Neo4j verification (run Cypher queries from migration file)
# Check: entities_with_website count
# Check: entities_still_in_additional_props = 0 (should be zero)
```

#### Step 7: Commit Changes

```bash
git add src/apex_memory/models/entities/customer.py
git add migrations/2025-11-05-website/
git commit -m "feat: Add website to Customer schema (Tier 3→2 promotion)

- Field: website (str)
- Usage: 184/255 (72.1%)
- Reason: High usage, LLM-extractable, consistent type

Migration includes:
- Pydantic field addition
- PostgreSQL GIN index (optional)
- Neo4j data migration

Backward compatible: old entities remain in metadata JSONB"

git push origin main
```

---

## Tools & APIs

### 1. Schema Evolution Analyzer (Python Module)

**Purpose:** Analyze additional_properties usage patterns

```python
from apex_memory.utils.schema_evolution import SchemaEvolutionAnalyzer

# Initialize analyzer
analyzer = SchemaEvolutionAnalyzer()

# Run analysis for all entities
report = analyzer.analyze_additional_properties()

# Filter to specific entity type
report = analyzer.analyze_additional_properties(entity_type_filter='customer')

# Filter to specific hub
report = analyzer.analyze_additional_properties(hub_filter='contacts')

# Access results
print(f"Promotion candidates: {len(report.promotion_candidates)}")
for field in report.promotion_candidates:
    print(f"  - {field.field_name}: {field.usage_percentage:.1f}%")
```

### 2. Schema Migration Generator (Python Module)

**Purpose:** Generate migration artifacts for field promotions

```python
from apex_memory.utils.schema_migration_generator import (
    SchemaMigrationGenerator,
    FieldPromotion,
)

# Initialize generator
generator = SchemaMigrationGenerator()

# Create promotion specification
promotion = FieldPromotion(
    field_name='emergency_contact',
    python_type='str',
    entity_type='person',
    hub='contacts',
    llm_extractable=True,
    description='Emergency contact phone number',
    usage_percentage=67.3,
    usage_count=172,
)

# Generate complete migration plan
artifacts = generator.generate_complete_promotion_plan(
    promotion,
    output_dir='migrations/2025-11-05-emergency-contact/',
)

# Access artifacts
print(artifacts['pydantic'])   # Pydantic field instructions
print(artifacts['neo4j'])      # Neo4j Cypher migration
print(artifacts['alembic'])    # Alembic migration
print(artifacts['summary'])    # Summary
```

### 3. Admin API Endpoints

**Base URL:** `http://localhost:8000/api/admin/schema/evolution`

**Authentication:** All endpoints require admin authentication (Bearer token)

#### GET /analyze

Analyze schema evolution opportunities.

```bash
curl -X GET "http://localhost:8000/api/admin/schema/evolution/analyze?entity_type=customer&min_usage=5" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response:**
```json
{
  "analysis_timestamp": "2025-11-05T10:00:00Z",
  "total_entities_analyzed": 255,
  "total_unique_fields": 12,
  "promotion_candidates": [
    {
      "field_name": "website",
      "usage_count": 184,
      "usage_percentage": 72.1,
      "dominant_entity_type": "customer",
      "dominant_data_type": "string",
      "recommended_for_promotion": true,
      "example_values": ["acme.com", "example.org", ...]
    }
  ],
  "low_usage_fields": [...],
  "hub_breakdown": {...},
  "entity_type_breakdown": {...}
}
```

#### GET /field/{field_name}

Get detailed statistics for a specific field.

```bash
curl -X GET "http://localhost:8000/api/admin/schema/evolution/field/emergency_contact?entity_type=person" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### POST /promote

Generate field promotion plan.

```bash
curl -X POST "http://localhost:8000/api/admin/schema/evolution/promote" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "website",
    "entity_type": "customer",
    "python_type": "str",
    "hub": "contacts",
    "llm_extractable": true,
    "description": "Company website URL"
  }'
```

**Response:**
```json
{
  "field_name": "website",
  "entity_type": "customer",
  "promotion_plan_summary": "...",
  "pydantic_instructions": "...",
  "neo4j_migration": "...",
  "alembic_migration": "...",
  "next_steps": [
    "1. Review Pydantic field addition instructions",
    "2. Edit customer.py to add field to schema",
    "3. Run tests: pytest tests/unit/test_entity_schemas.py",
    ...
  ]
}
```

#### GET /promote/{field_name}/pydantic

Get Pydantic field addition instructions (plain text for copy-paste).

#### GET /promote/{field_name}/neo4j

Get Neo4j Cypher migration script (plain text for execution).

---

## Examples

### Example 1: Promote "website" to Customer Schema

**Scenario:** Analysis shows "website" appears in 72% of Customer entities

**Steps:**

1. **Run Analysis**
   ```bash
   python -m apex_memory.utils.schema_evolution --entity-type customer
   # Output: website (72.1% usage) - RECOMMENDED FOR PROMOTION
   ```

2. **Generate Migration**
   ```bash
   python -m apex_memory.utils.schema_migration_generator \
     website customer str \
     --hub contacts \
     --llm-extractable \
     --description "Company website URL" \
     --usage-percentage 72.1 \
     --output-dir migrations/website/
   ```

3. **Update Schema**
   ```python
   # customer.py
   website: Optional[str] = Field(
       None,
       description="Company website URL",
       json_schema_extra={'llm_extractable': True}
   )
   ```

4. **Test**
   ```bash
   pytest tests/unit/test_entity_schemas.py
   ```

5. **Migrate Data**
   ```cypher
   MATCH (c:Customer)
   WHERE c.additional_properties.website IS NOT NULL
   SET c.website = c.additional_properties.website
   ```

6. **Commit**
   ```bash
   git commit -m "feat: Add website to Customer schema (72% usage)"
   ```

### Example 2: Reject Low-Usage Field

**Scenario:** Analysis shows "temp_field_abc" appears in 8% of entities

**Decision:** Reject promotion (below 40% threshold)

**Action:** No migration needed, field stays in Tier 3

---

## Best Practices

### 1. Regular Reviews

- **Schedule weekly reviews** - Don't let fields pile up in Tier 3
- **Document decisions** - Track why fields were promoted or rejected
- **Monitor trends** - Some fields grow in usage over time

### 2. Semantic Naming

- **Use clear field names** - "emergency_contact" not "ec_num"
- **Match existing conventions** - Check entity schema for naming patterns
- **Avoid abbreviations** - Unless domain-standard (e.g., "url" is fine)

### 3. Type Consistency

- **Validate data types** - Ensure 80%+ consistency before promotion
- **Handle edge cases** - Document known type variations
- **Use Optional[T]** - Most promoted fields should be optional

### 4. Testing

- **Test before promotion** - Verify Pydantic model is valid
- **Test after migration** - Verify data migrated correctly
- **Test extraction** - Ensure Graphiti populates new field

### 5. Documentation

- **Update entity docstrings** - Document newly promoted fields
- **Update API docs** - Regenerate OpenAPI spec if needed
- **Create ADR** - For significant schema changes

---

## Troubleshooting

### Issue 1: Field promoted but Graphiti doesn't extract it

**Symptom:** New Tier 2 field remains None after extraction

**Cause:** Field not marked `llm_extractable=True` OR Graphiti context doesn't include this field

**Fix:**
1. Verify `json_schema_extra={'llm_extractable': True}` in Pydantic field
2. Check `get_llm_extractable_fields()` returns this field
3. Verify Graphiti prompt includes this field in entity_types

### Issue 2: Neo4j migration timeout

**Symptom:** Cypher migration fails with timeout error

**Cause:** Large number of entities to migrate

**Fix:**
```cypher
// Batch migration (process 1000 at a time)
MATCH (e:Customer)
WHERE e.additional_properties.website IS NOT NULL
WITH e LIMIT 1000
SET e.website = e.additional_properties.website
RETURN count(e);

// Repeat until count = 0
```

### Issue 3: Type inconsistency after promotion

**Symptom:** Some entities have field as string, others as int

**Cause:** Promoted field without checking data type consistency

**Fix:**
1. Rollback promotion
2. Add data cleaning migration to standardize type
3. Re-promote after cleaning

---

## Appendix: Promotion Decision Tree

```
Start: New field in additional_properties
  |
  v
Usage > 40%?
  ├─ No  → Stay in Tier 3
  └─ Yes → Continue
       |
       v
     Consistent data type (>80%)?
       ├─ No  → Clean data first, then re-evaluate
       └─ Yes → Continue
            |
            v
          Semantic value for queries/analytics?
            ├─ No  → Stay in Tier 3
            └─ Yes → Continue
                 |
                 v
               Duplicates existing Tier 2 field?
                 ├─ Yes → Merge or reject
                 └─ No  → Continue
                      |
                      v
                    Stable over time (not experimental)?
                      ├─ No  → Wait, re-evaluate next week
                      └─ Yes → ✅ PROMOTE TO TIER 2
```

---

**Last Updated:** 2025-11-05
**Maintainer:** Apex Memory Engineering Team
**Questions?** See [Troubleshooting](#troubleshooting) or contact engineering lead
