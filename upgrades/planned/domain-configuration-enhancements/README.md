# Domain Configuration Enhancements

**Status:** 📝 Planned
**Priority:** Medium
**Timeline:** 2-3 weeks
**Prerequisites:** Domain Configuration (Phase 1-4) complete ✅

---

## Overview

Extend the Domain Configuration system with additional domains, enhanced metrics, real-time validation, and auto-detection capabilities.

**Current State (Complete):**
- ✅ Logistics domain (46 entities, 30 edges, 13 examples, 7 rules)
- ✅ API → Workflow → Activity integration
- ✅ 88/88 tests passing
- ✅ 85-90% extraction accuracy for logistics documents

**Planned Enhancements:**
1. Additional domains (personal, medical, manufacturing)
2. Domain-specific metrics and monitoring
3. Real-time validation during extraction
4. Auto-detection of domain from document content

---

## Enhancement 1: Additional Domains

### Personal Knowledge Management Domain

**Goal:** Support personal document ingestion (emails, notes, journal entries)

**Entity Types (25-30 expected):**
- Person, Contact, Friend, Family, Colleague
- Event, Meeting, Appointment, Task
- Note, Journal, Idea, Goal
- Email, Message, Call
- Location, Place, Address
- Project, Hobby, Interest

**Edge Types (15-20 expected):**
- KNOWS, WORKS_WITH, RELATED_TO
- ATTENDS, SCHEDULED_FOR
- MENTIONS, REFERENCES
- SENT_TO, RECEIVED_FROM
- LOCATED_AT

**Few-Shot Examples (10-12):**
- Email correspondence patterns
- Journal entry extraction
- Meeting notes and action items
- Contact information updates

**Validation Rules (5-7):**
- Contact must have name and at least one contact method
- Events must have date/time
- Relationships must be bidirectional where appropriate

**Timeline:** 1 week
**Test Target:** 30-40 tests

### Medical/Healthcare Domain

**Goal:** Support clinical documents (discharge summaries, lab results, prescriptions)

**Entity Types (35-40 expected):**
- Patient, Provider, Hospital, Clinic
- Diagnosis, Symptom, Condition, Allergy
- Medication, Prescription, Dosage
- Procedure, Treatment, Surgery
- LabTest, LabResult, Vital
- Appointment, Visit, Admission

**Edge Types (20-25 expected):**
- DIAGNOSED_WITH, TREATS
- PRESCRIBES, TAKES
- PERFORMS, UNDERGOES
- ORDERS, HAS_RESULT
- SCHEDULED_AT

**Few-Shot Examples (12-15):**
- Discharge summary extraction
- Lab result interpretation
- Prescription details
- Clinical note patterns

**Validation Rules (8-10):**
- Medications must have dosage and frequency
- Lab results must have reference ranges
- Diagnoses must have ICD codes
- Dates must be chronologically consistent

**Timeline:** 1.5 weeks
**Test Target:** 50-60 tests

**⚠️ Note:** Requires HIPAA compliance review before production use

### Manufacturing/Supply Chain Domain

**Goal:** Support manufacturing documents (BOMs, work orders, quality reports)

**Entity Types (30-35 expected):**
- Part, Component, Assembly, Product
- Supplier, Manufacturer, Vendor
- WorkOrder, ProductionRun, Batch
- QualityInspection, Defect, ReworkOrder
- Warehouse, Location, Bin
- Purchase Order, ShippingManifest

**Edge Types (18-22 expected):**
- CONTAINS, ASSEMBLED_FROM
- SUPPLIES, MANUFACTURES
- PRODUCES, INSPECTS
- STORED_AT, SHIPS_TO
- ORDERED_FROM

**Few-Shot Examples (10-12):**
- Bill of materials extraction
- Work order details
- Quality inspection reports
- Inventory movements

**Validation Rules (7-9):**
- Parts must have part numbers
- BOMs must have quantities and units
- Quality scores must be 0-100 range
- Dates must follow production sequence

**Timeline:** 1 week
**Test Target:** 40-50 tests

---

## Enhancement 2: Domain-Specific Metrics

### Goal
Track usage, accuracy, and performance by domain to enable data-driven improvements.

### Metrics to Add

**Domain Usage Metrics:**
```python
temporal_domain_usage_total{domain_name="logistics"} = 1250
temporal_domain_usage_total{domain_name="personal"} = 380
temporal_domain_usage_total{domain_name="medical"} = 95
```

**Extraction Accuracy by Domain:**
```python
extraction_accuracy_by_domain{domain="logistics"} = 0.87
extraction_accuracy_by_domain{domain="personal"} = 0.82
extraction_accuracy_by_domain{domain="medical"} = 0.91
```

**Validation Results:**
```python
validation_errors_total{domain="logistics", rule="LoadValidationRule"} = 45
validation_warnings_total{domain="logistics", rule="RepairCostRule"} = 12
```

**Entity Type Distribution:**
```python
entities_extracted_by_type{domain="logistics", entity_type="Load"} = 890
entities_extracted_by_type{domain="logistics", entity_type="Truck"} = 456
```

### Implementation

1. **Extend `monitoring/metrics.py`:**
   - Add domain-specific counters and gauges
   - Track validation results
   - Measure extraction time by domain

2. **Update Activity Layer:**
   - Record domain metrics after extraction
   - Log validation results
   - Track entity type distribution

3. **Grafana Dashboard:**
   - Create "Domain Configuration" dashboard
   - Panel: Domain usage over time
   - Panel: Accuracy by domain
   - Panel: Validation error trends
   - Panel: Entity type distribution

**Timeline:** 3-4 days
**Test Target:** 10-15 tests

---

## Enhancement 3: Real-Time Validation

### Goal
Run validation rules during extraction (not just after) and provide immediate feedback.

### Current State
- Validation rules exist but not integrated into extraction flow
- Validation happens manually via `validate_entity()` utility

### Proposed Flow

```
extract_entities_activity()
    ↓
GraphitiService.add_document_episode()
    ↓ [entities extracted]
For each entity:
    ↓
validate_entity(entity, domain.validation_rules)
    ↓ [if errors]
Log validation errors + store in result
    ↓ [if warnings]
Log validation warnings + store in result
    ↓
Return enriched result with validation status
```

### Features

1. **Validation Integration:**
   - Run all domain validation rules after extraction
   - Store validation results in extraction response
   - Log critical errors vs. warnings

2. **Validation Metrics:**
   - Track validation error rates by rule
   - Identify frequently failing rules
   - Monitor validation performance

3. **Validation API:**
   - Return validation results in workflow response
   - Include validation summary in status endpoint
   - Optional flag to fail on validation errors

### Implementation

1. **Update `extract_entities_activity`:**
   ```python
   # After Graphiti extraction
   validation_results = []
   for entity in entities:
       results = validate_entity(entity, domain.validation_rules)
       validation_results.extend(results)

   # Return enriched response
   return {
       'entities': entities,
       'validation_results': validation_results,
       'validation_errors': get_all_errors(validation_results),
       'validation_warnings': get_all_warnings(validation_results),
   }
   ```

2. **Update Workflow:**
   - Store validation results in workflow state
   - Log validation summary
   - Optional: Fail workflow on critical errors

3. **Update API Response:**
   - Include validation summary in response
   - Add validation warnings to status endpoint

**Timeline:** 4-5 days
**Test Target:** 20-25 tests

---

## Enhancement 4: Auto-Detection

### Goal
Automatically detect domain from document content (no manual domain parameter needed).

### Approach

**Option A: Keyword-Based Detection (Simple)**
```python
def detect_domain(content: str) -> str:
    """Detect domain from content keywords."""

    # Logistics keywords
    logistics_keywords = ["load", "freight", "carrier", "truck", "shipment", "invoice"]

    # Personal keywords
    personal_keywords = ["meeting", "note", "journal", "email", "appointment"]

    # Score each domain
    scores = {
        "logistics": count_keywords(content, logistics_keywords),
        "personal": count_keywords(content, personal_keywords),
    }

    # Return highest scoring domain (or None if below threshold)
    max_score = max(scores.values())
    if max_score < 3:  # Minimum 3 keyword matches
        return None

    return max(scores, key=scores.get)
```

**Option B: LLM-Based Detection (Advanced)**
```python
async def detect_domain_llm(content: str) -> str:
    """Use LLM to classify document domain."""

    prompt = f"""
    Classify this document into one of these domains:
    - logistics: Freight, trucking, shipping, invoices, loads
    - personal: Emails, notes, journal entries, meetings
    - medical: Clinical notes, lab results, prescriptions
    - None: Does not match any domain

    Document:
    {content[:500]}  # First 500 chars

    Domain:
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    return response.choices[0].message.content.strip().lower()
```

### Implementation

1. **Add Detection Function:**
   - Create `src/apex_memory/config/domain_detector.py`
   - Implement keyword-based detection (Phase 1)
   - Add LLM-based detection (Phase 2)

2. **Update Activity:**
   ```python
   async def extract_entities_activity(parsed_doc, domain_name=None):
       # Auto-detect if not specified
       if not domain_name:
           content = parsed_doc.get('content', '')
           domain_name = detect_domain(content)
           if domain_name:
               logger.info(f"Auto-detected domain: {domain_name}")

       # Load domain and continue...
   ```

3. **Add Metrics:**
   - Track auto-detection usage
   - Measure detection accuracy
   - Log detection confidence

**Timeline:** 3-4 days (keyword) + 2-3 days (LLM)
**Test Target:** 15-20 tests

---

## Timeline & Priorities

### Phase 1 (Week 1): Additional Domains
- Personal domain implementation
- Manufacturing domain implementation
- Test coverage for new domains
- **Deliverable:** 2 new domains, 70-90 tests

### Phase 2 (Week 2): Metrics & Validation
- Domain-specific metrics
- Real-time validation integration
- Grafana dashboard updates
- **Deliverable:** Enhanced monitoring, validation feedback

### Phase 3 (Week 3): Auto-Detection
- Keyword-based detection
- LLM-based detection (optional)
- Detection metrics and monitoring
- **Deliverable:** Automatic domain selection

---

## Success Criteria

1. ✅ **3+ Domains Available:** Logistics, Personal, Manufacturing (optional: Medical)
2. ✅ **Domain Metrics:** Usage, accuracy, validation tracked per domain
3. ✅ **Real-Time Validation:** Validation results returned with extraction
4. ✅ **Auto-Detection:** 80%+ accuracy on domain classification
5. ✅ **Test Coverage:** 150+ total tests across all domains
6. ✅ **Documentation:** Each domain has examples and usage guide

---

## References

- **Completed:** `upgrades/completed/domain-configuration/` - Phases 1-4
- **Logistics Domain:** `src/apex_memory/config/logistics_domain.py`
- **Validation Framework:** `src/apex_memory/validators/logistics_rules.py`
- **Integration:** `src/apex_memory/temporal/activities/document_ingestion.py`

---

**Priority:** Medium
**Estimated Duration:** 2-3 weeks
**Test Target:** 150+ tests
**Status:** 📝 Planned - Ready to start after logistics domain is validated in production
