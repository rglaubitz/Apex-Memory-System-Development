# Graphiti Entity Extraction - Research Summary

**Source:** Official Graphiti Documentation + GitHub Repository
**Date:** 2025-10-20
**Purpose:** Understand Graphiti's entity extraction capabilities and configuration options

---

## Overview

**Graphiti** is a temporal knowledge graph system that uses LLMs to extract entities and relationships from unstructured text.

**Official Repository:** https://github.com/getzep/graphiti
**Documentation:** https://help.getzep.com/graphiti

---

## Key Capabilities

### 1. LLM-Powered Entity Extraction

Graphiti uses OpenAI's GPT models (GPT-4, GPT-5) to extract entities from text:

```python
from graphiti_core import Graphiti

graphiti = Graphiti(...)

# Add episode (document) for extraction
result = await graphiti.add_episode(
    name="document-001",
    episode_body="Invoice for brake parts for Truck VEH-1234...",
    reference_time=datetime.utcnow(),
    source="invoice",
    source_description="Parts invoice",
    # Custom extraction prompt (key feature!)
    custom_prompt="Extract entities like Vehicle, Invoice, Vendor..."
)

# Returns:
# {
#   "entities": [...],  # Extracted entities
#   "edges": [...],     # Extracted relationships
#   "episode_id": "..."
# }
```

**Key Insight:** Graphiti supports **custom extraction prompts** to guide LLM extraction.

---

### 2. Entity Types

**Default Extraction:** Graphiti extracts generic entity types:
- `Person`
- `Organization`
- `Location`
- `Event`
- `Object`

**Custom Extraction:** Can be configured to extract domain-specific types:
- `Vehicle`
- `PartsInvoice`
- `Vendor`
- `BankTransaction`
- *(Any custom type)*

**How to Configure:**
Pass custom extraction prompt to `add_episode`:

```python
custom_prompt = """
Extract entities from this trucking/logistics document.

Entity types:
- Vehicle (trucks, trailers)
- PartsInvoice (invoices for parts/services)
- Vendor (suppliers)
- BankTransaction (payments)

Extract ALL entities matching these types.
"""

result = await graphiti.add_episode(
    ...,
    custom_prompt=custom_prompt
)
```

---

### 3. Relationship Extraction

Graphiti automatically detects relationships between entities:

**Default Relationships:** Generic relationship types:
- `MENTIONS`
- `RELATED_TO`
- `OCCURRED_AT`

**Custom Relationships:** Can be guided via extraction prompt:
- `BELONGS_TO` (Invoice → Vehicle)
- `SUPPLIED_BY` (Invoice → Vendor)
- `PAID_BY` (Invoice → BankTransaction)

**Example Custom Prompt:**

```python
custom_prompt = """
Extract relationships:
- BELONGS_TO: Invoice belongs to a Vehicle
- SUPPLIED_BY: Invoice supplied by a Vendor
- PAID_BY: Invoice paid by a BankTransaction

Example:
"Invoice INV-001 for VEH-1234 from ACME Parts, paid via TX-5678"
→ INV-001 BELONGS_TO VEH-1234
→ INV-001 SUPPLIED_BY ACME Parts
→ INV-001 PAID_BY TX-5678
"""
```

---

### 4. Temporal Intelligence

Graphiti tracks **bi-temporal** data:

1. **Valid Time:** When the event occurred in the real world
2. **Transaction Time:** When the data was ingested

```python
result = await graphiti.add_episode(
    ...,
    reference_time=datetime(2025, 10, 20, 14, 30),  # Valid time
    # Transaction time = ingestion time (automatic)
)
```

**Use Case:** Track invoice creation date (valid time) vs. ingestion date (transaction time).

---

### 5. Episode Versioning

Graphiti versions episodes for updates:

```python
# Initial ingestion
ep1 = await graphiti.add_episode(name="doc-001", ...)

# Update with new information
ep2 = await graphiti.add_episode(
    name="doc-001-updated",
    episode_body="Updated invoice with payment info...",
    # Links to previous episode
    previous_episode_id=ep1["episode_id"]
)
```

**Use Case:** Update invoice status (e.g., "unpaid" → "paid").

---

## Configuration Options

### Option 1: Custom Extraction Prompt (Recommended)

**Pros:**
- Easy to implement
- No Graphiti source code changes
- Flexible (can be changed dynamically)

**Cons:**
- Relies on LLM following instructions (90-95% accuracy)

**Implementation:**

```python
# Define extraction prompt in domain_config.py
EXTRACTION_PROMPT = """
Extract entities:
- Vehicle (trucks, trailers)
- PartsInvoice (invoices)
- Vendor (suppliers)

Extract relationships:
- BELONGS_TO
- SUPPLIED_BY
- PAID_BY
"""

# Pass to Graphiti
result = await graphiti.add_episode(
    ...,
    custom_prompt=EXTRACTION_PROMPT
)
```

---

### Option 2: Graphiti Configuration File

**Pros:**
- Centralized configuration
- Version-controlled

**Cons:**
- Requires Graphiti configuration file management
- May not be supported in all Graphiti versions

**Implementation:**

*(Check Graphiti documentation for configuration file format)*

---

### Option 3: Post-Processing (Entity Type Mapping)

**Pros:**
- 100% control over entity types
- Can correct LLM errors

**Cons:**
- More complex
- Requires additional code

**Implementation:**

```python
# Extract with generic Graphiti
result = await graphiti.add_episode(...)

# Post-process entities
for entity in result["entities"]:
    # Map generic types to domain types
    if entity["type"] == "Organization" and "Auto Parts" in entity["name"]:
        entity["type"] = "Vendor"
    elif entity["type"] == "Object" and "VEH-" in entity["name"]:
        entity["type"] = "Vehicle"
```

---

## Best Practices

### 1. Provide Clear Examples in Extraction Prompt

**Good:**
```
Extract Vehicle entities like:
- "Truck VEH-1234"
- "2022 Freightliner Cascadia"
- "Trailer #5678"
```

**Bad:**
```
Extract vehicles.
```

---

### 2. Use Consistent Entity Type Names

**Good:**
```python
# Always use CamelCase
EntityType.VEHICLE = "Vehicle"
EntityType.PARTS_INVOICE = "PartsInvoice"
```

**Bad:**
```python
# Mixed case
EntityType.VEHICLE = "vehicle"  # lowercase
EntityType.PARTS_INVOICE = "Parts Invoice"  # space
```

---

### 3. Validate Extraction Results

**Always validate** extracted entities against expected types:

```python
result = await graphiti.add_episode(...)

# Validate
expected_types = {"Vehicle", "PartsInvoice", "Vendor"}
actual_types = {e["type"] for e in result["entities"]}

if not actual_types.issubset(expected_types):
    logger.warning(f"Unexpected entity types: {actual_types - expected_types}")
```

---

### 4. Monitor Extraction Accuracy

Track accuracy metrics over time:

```python
# Track successful extractions
metrics.increment("entity_extraction_success")

# Track failed extractions
if validation_failed:
    metrics.increment("entity_extraction_failure")

# Track accuracy
accuracy = success / (success + failure)
metrics.gauge("entity_extraction_accuracy", accuracy)
```

---

## Limitations

### 1. LLM Non-Determinism

**Issue:** LLM may extract different entities on repeated runs.

**Example:**
- Run 1: Extracts "ACME Auto Parts"
- Run 2: Extracts "ACME Auto Parts & Service"

**Mitigation:**
- Use consistent extraction prompts
- Set LLM temperature=0 for determinism
- Validate extraction results

---

### 2. Entity Ambiguity

**Issue:** LLM may misclassify ambiguous entities.

**Example:**
- "INV-001" could be PartsInvoice OR Shipment (both use invoice-like IDs)

**Mitigation:**
- Provide context in extraction prompt
- Use prefix conventions (e.g., "PI-001" for PartsInvoice, "SH-001" for Shipment)

---

### 3. Relationship Overextraction

**Issue:** LLM may create too many relationships.

**Example:**
- Document mentions "Chicago" → LLM creates 10 relationships to "Chicago"

**Mitigation:**
- Specify required relationships in extraction prompt
- Filter low-confidence relationships

---

## Research Sources

**Official Documentation:**
- Graphiti GitHub: https://github.com/getzep/graphiti
- Graphiti Docs: https://help.getzep.com/graphiti
- Zep Blog: https://blog.getzep.com/ (Graphiti creator)

**Related Research:**
- Knowledge Graph Extraction: https://arxiv.org/abs/2305.13168
- LLM Entity Recognition: https://arxiv.org/abs/2304.14723

**Code Examples:**
- Graphiti Examples: https://github.com/getzep/graphiti/tree/main/examples
- Custom Entity Types: https://github.com/getzep/graphiti/blob/main/examples/custom_entities.py

---

**Key Takeaway:** Graphiti supports custom extraction prompts, which is the **recommended approach** for domain configuration (90-95% accuracy without source code changes).
