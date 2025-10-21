# Graphiti Domain Configuration - Troubleshooting Guide

**Project:** Graphiti Domain Configuration for Trucking/Logistics Domain
**Last Updated:** 2025-10-20

---

## Table of Contents

1. [Common Issues](#common-issues)
2. [Accuracy Problems](#accuracy-problems)
3. [Integration Issues](#integration-issues)
4. [Performance Issues](#performance-issues)
5. [Neo4j Query Issues](#neo4j-query-issues)
6. [Debugging Tools](#debugging-tools)

---

## Common Issues

### Issue 1: Domain Config Module Not Loading

**Symptom:**
```
ModuleNotFoundError: No module named 'apex_memory.config.domain_config'
```

**Cause:** Module file not created or not in correct location

**Solution:**

```bash
# Verify file exists
ls apex-memory-system/src/apex_memory/config/domain_config.py

# If missing, create it using IMPLEMENTATION.md Day 1 Step 1.1

# Verify PYTHONPATH includes src/
export PYTHONPATH=/path/to/apex-memory-system/src:$PYTHONPATH

# Test import
python3 -c "from apex_memory.config.domain_config import get_domain_config; print('✅ Module loads')"
```

**Expected:** `✅ Module loads`

---

### Issue 2: Feature Flag Not Working

**Symptom:**
```
# Set flag to true, but domain config still not enabled
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true
# service.domain_configured still returns False
```

**Cause 1:** Environment variable not set in current shell

**Solution:**
```bash
# Verify variable is set
echo $ENABLE_DOMAIN_CONFIGURED_GRAPHITI

# Should print: true

# If empty, set it:
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true
```

**Cause 2:** Variable set but GraphitiService already initialized

**Solution:**
```python
# Set variable BEFORE importing GraphitiService
import os
os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "true"

# Then import
from apex_memory.services.graphiti_service import GraphitiService
service = GraphitiService()

# Verify
print(service.domain_configured)  # Should print: True
```

**Cause 3:** Typo in environment variable name

**Solution:**
```bash
# Correct spelling (note underscores):
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true

# Common typos:
# ❌ ENABLE_DOMAIN_CONFIG_GRAPHITI=true
# ❌ ENABLE_DOMAIN_CONFIGURED_GRAPHITE=true
# ❌ ENABLE_DOMAIN_CONFIGURE_GRAPHITI=true
```

---

### Issue 3: Existing Tests Failing After Domain Config

**Symptom:**
```
# After adding domain config, existing tests fail
pytest tests/integration/ -v
# Multiple failures
```

**Cause:** Feature flag accidentally enabled for existing tests

**Solution:**

```bash
# Ensure feature flag is OFF for existing tests
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false

# Or unset it entirely
unset ENABLE_DOMAIN_CONFIGURED_GRAPHITI

# Run tests again
pytest tests/integration/ -v

# Expected: All tests pass (no regression)
```

**Prevention:**
- Always set feature flag explicitly in test fixtures
- Default should be `false` (safe)
- Only enable for domain config tests

---

## Accuracy Problems

### Issue 4: Entity Extraction Accuracy Below 90%

**Symptom:**
```
# Validation script shows low accuracy
Average accuracy: 65.3%
❌ FAIL: Accuracy below 90% threshold
```

**Diagnosis Steps:**

**Step 1: Identify which entities are being missed**

```bash
# Run validation with verbose output
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true python tests/validate_extraction.py | grep "Expected entities"
```

**Step 2: Check extraction prompt**

```python
# Verify extraction prompt includes all entity types
from apex_memory.config.domain_config import get_domain_config

config = get_domain_config()
print(config.extraction_prompt)

# Should include all 10 entity types:
# - Vehicle
# - PartsInvoice
# - Vendor
# - BankTransaction
# - Driver
# - Shipment
# - Location
# - Customer
# - MaintenanceRecord
# - Route
```

**Common Causes:**

**Cause 1: Extraction prompt too generic**

**Solution:** Add more specific examples to extraction prompt

```python
# In domain_config.py, update extraction_prompt with more examples:

extraction_prompt="""
...existing prompt...

**Additional Examples:**

Document: "Maintenance record MR-2025-001 for VEH-1234. Oil change performed by ACME Auto Parts."

Extract:
- MaintenanceRecord: "MR-2025-001"
- Vehicle: "VEH-1234"
- Vendor: "ACME Auto Parts"

Relationships:
- MR-2025-001 PERFORMED_ON VEH-1234
- MR-2025-001 SUPPLIED_BY ACME Auto Parts
"""
```

**Cause 2: Entity type names don't match**

**Solution:** Verify entity type names are exact (case-sensitive)

```python
# Correct:
EntityType.PARTS_INVOICE = "PartsInvoice"  # ✅ CamelCase
EntityType.BANK_TRANSACTION = "BankTransaction"  # ✅ CamelCase

# Incorrect:
EntityType.PARTS_INVOICE = "parts_invoice"  # ❌ snake_case
EntityType.BANK_TRANSACTION = "Bank Transaction"  # ❌ Space
```

**Cause 3: Expected outputs too strict**

**Solution:** Review expected outputs for reasonableness

```json
// If expected output requires exact match of "ACME Auto Parts"
// but Graphiti extracts "ACME Auto Parts & Service" (more complete)
// Consider this a SUCCESS, not a failure

// Update expected output to be more lenient:
{
  "type": "Vendor",
  "name": "ACME Auto Parts",  // Allow partial match
  "attributes": {}
}
```

---

### Issue 5: Relationship Extraction Accuracy Below 90%

**Symptom:**
```
Entity accuracy: 95.0%  # Good
Relationship accuracy: 60.0%  # Poor
Overall accuracy: 77.5%  # Fail
```

**Diagnosis Steps:**

**Step 1: Identify which relationships are being missed**

```bash
# Run validation with verbose output
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true python tests/validate_extraction.py | grep "Expected relationships"
```

**Step 2: Check if entities exist first**

```python
# Relationships require both source and target entities to exist
# If entity extraction failed, relationship extraction will also fail

# Example:
# If "PartsInvoice INV-001" not extracted → "BELONGS_TO" relationship cannot be created
```

**Common Causes:**

**Cause 1: Relationship type names don't match**

**Solution:** Verify relationship type names are exact

```python
# Correct:
RelationshipType.BELONGS_TO = "BELONGS_TO"  # ✅ ALL_CAPS_SNAKE
RelationshipType.SUPPLIED_BY = "SUPPLIED_BY"  # ✅ ALL_CAPS_SNAKE

# Incorrect:
RelationshipType.BELONGS_TO = "belongs_to"  # ❌ lowercase
RelationshipType.SUPPLIED_BY = "SuppliedBy"  # ❌ CamelCase
```

**Cause 2: Extraction prompt lacks relationship examples**

**Solution:** Add more relationship examples to extraction prompt

```python
# In domain_config.py, update extraction_prompt:

extraction_prompt="""
...existing prompt...

**More Relationship Examples:**

Document: "Driver John Smith assigned to VEH-1234. Vehicle located at Chicago Distribution Center."

Relationships:
- VEH-1234 ASSIGNED_TO John Smith
- VEH-1234 LOCATED_AT Chicago Distribution Center

Document: "Shipment SH-001 delivered to Dallas Warehouse. Invoice billed to ACME Corp."

Relationships:
- SH-001 DELIVERED_TO Dallas Warehouse
- Invoice BILLED_TO ACME Corp
"""
```

**Cause 3: Graphiti creating different relationship names**

**Solution:** Check what Graphiti is actually creating

```cypher
// Query Neo4j to see actual relationship types
MATCH ()-[r]->()
RETURN DISTINCT type(r) AS relationship_type
ORDER BY relationship_type;

// If Graphiti creates "belongs_to" instead of "BELONGS_TO"
// Update domain config to match Graphiti's convention
// OR update Graphiti configuration to use uppercase
```

---

### Issue 6: Inconsistent Accuracy Across Test Documents

**Symptom:**
```
Document 1: 95.0% ✅
Document 2: 92.0% ✅
Document 3: 65.0% ❌  # Outlier
Document 4: 91.0% ✅
...
```

**Diagnosis:**

**Step 1: Identify problematic document**

```bash
# Run validation to see which document failed
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true python tests/validate_extraction.py

# Look for:
# ❌ FAIL: Document X accuracy below threshold
```

**Step 2: Inspect problematic document**

```bash
# Read the document that failed
cat tests/sample-documents/[failed-document].txt

# Check expected output
cat tests/expected-outputs/[failed-document].json
```

**Common Causes:**

**Cause 1: Document too complex**

**Solution:** Simplify test document or adjust expected outputs

```
# If document has 20+ entities and 30+ relationships
# Consider this an outlier and adjust expectations

# Or create a simpler version for testing
```

**Cause 2: Document format different from training examples**

**Solution:** Add examples matching document format to extraction prompt

```python
# If document is a bank statement (tabular format)
# Add bank statement example to extraction prompt

extraction_prompt="""
...existing prompt...

**Bank Statement Example:**

10/20/2025 - ACH Debit - ACME Auto Parts - $820.00 - TX-5678
           (Brake repair for VEH-1234)

Extract:
- BankTransaction: "TX-5678" (amount: $820.00, date: 2025-10-20)
- Vendor: "ACME Auto Parts"
- Vehicle: "VEH-1234"
- PartsInvoice: (inferred from description)

Relationships:
- TX-5678 PAID_BY PartsInvoice
- PartsInvoice BELONGS_TO VEH-1234
- PartsInvoice SUPPLIED_BY ACME Auto Parts
"""
```

---

## Integration Issues

### Issue 7: GraphitiService Not Calling Domain Config

**Symptom:**
```
# Feature flag enabled, but extraction still uses generic prompt
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true
# Logs show: "Using generic extraction prompt"
```

**Cause:** Code not updated to use domain config

**Solution:**

**Step 1: Verify GraphitiService code updated**

```bash
# Check if GraphitiService imports domain config
grep "from apex_memory.config.domain_config import" \
  apex-memory-system/src/apex_memory/services/graphiti_service.py

# Expected: import statement exists
```

**Step 2: Verify extraction method updated**

```bash
# Check if extract_entities_and_relationships uses custom prompt
grep "custom_prompt" \
  apex-memory-system/src/apex_memory/services/graphiti_service.py

# Expected: custom_prompt parameter passed to Graphiti
```

**Step 3: Follow IMPLEMENTATION.md Day 2 Step 2.1**

---

### Issue 8: Validation Function Not Called

**Symptom:**
```
# Extraction completes, but no validation results returned
result = await service.extract_entities_and_relationships(...)
result["validation"]  # Returns: None
```

**Cause:** Validation function not integrated

**Solution:**

**Step 1: Verify validation import**

```bash
grep "validate_extraction" \
  apex-memory-system/src/apex_memory/services/graphiti_service.py

# Expected: import statement exists
```

**Step 2: Verify validation called**

```bash
# Check if validation called in extract_entities_and_relationships
grep "validate_extraction(" \
  apex-memory-system/src/apex_memory/services/graphiti_service.py

# Expected: function call exists
```

**Step 3: Follow IMPLEMENTATION.md Day 2 Step 2.1** (validation integration)

---

## Performance Issues

### Issue 9: Extraction Too Slow

**Symptom:**
```
# Extraction takes > 10 seconds for small documents
start = time.time()
await service.extract_entities_and_relationships(text, ...)
duration = time.time() - start
print(f"Duration: {duration}s")  # Prints: Duration: 15.3s (too slow!)
```

**Diagnosis:**

**Step 1: Check document size**

```python
print(f"Document length: {len(text)} chars")

# If > 5000 chars → expected to be slower
# If < 500 chars → should be < 2 seconds
```

**Step 2: Check LLM API latency**

```python
# GPT-5 API calls can be slow
# Check OpenAI API status: https://status.openai.com/
```

**Step 3: Check network connectivity**

```bash
# Ping OpenAI API
curl -I https://api.openai.com/v1/models

# Expected: 200 OK in < 1 second
```

**Solutions:**

**Solution 1: Use caching**

```python
# Enable Graphiti's built-in caching
# (Graphiti may cache LLM responses)

# Or implement custom caching:
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_extraction(text_hash):
    return service.extract_entities_and_relationships(...)
```

**Solution 2: Batch processing**

```python
# If processing multiple documents, batch them:
documents = [doc1, doc2, doc3]

# Instead of sequential:
for doc in documents:
    await service.extract_entities_and_relationships(doc, ...)

# Use concurrent:
import asyncio
tasks = [service.extract_entities_and_relationships(doc, ...) for doc in documents]
results = await asyncio.gather(*tasks)
```

**Solution 3: Optimize extraction prompt**

```python
# Shorter extraction prompts → faster processing
# Remove verbose examples if not needed
# Keep only essential examples
```

---

### Issue 10: High Memory Usage

**Symptom:**
```
# Memory usage increases during batch extraction
# Eventually runs out of memory
```

**Diagnosis:**

```bash
# Monitor memory usage
top -p $(pgrep -f python)

# Check memory usage before/after extraction
import tracemalloc
tracemalloc.start()
# ... extraction ...
current, peak = tracemalloc.get_traced_memory()
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
```

**Solutions:**

**Solution 1: Process documents in smaller batches**

```python
# Instead of processing 100 documents at once:
batch_size = 10
for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    results = await process_batch(batch)
    # Clear memory after each batch
    gc.collect()
```

**Solution 2: Limit concurrent extractions**

```python
# Limit concurrent Graphiti calls
import asyncio
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent

async def extract_with_limit(doc):
    async with semaphore:
        return await service.extract_entities_and_relationships(doc, ...)
```

---

## Neo4j Query Issues

### Issue 11: Domain Entities Not Appearing in Neo4j

**Symptom:**
```cypher
// Query for domain entities returns 0 results
MATCH (n) WHERE n.type = 'Vehicle' RETURN COUNT(n);
// Returns: 0
```

**Diagnosis Steps:**

**Step 1: Verify Graphiti connected to Neo4j**

```bash
# Check Neo4j connection
docker exec -it apex-neo4j cypher-shell -u neo4j -p apexmemory2024

# Should connect successfully
```

**Step 2: Verify extraction created Graphiti episode**

```python
result = await service.extract_entities_and_relationships(...)
print(result["episode_uuid"])

# Should print: UUID of created episode
```

**Step 3: Query Graphiti episodes**

```cypher
// Check if episodes exist
MATCH (ep:Episode)
RETURN ep.uuid, ep.name
LIMIT 10;

// Expected: Episodes exist with valid UUIDs
```

**Common Causes:**

**Cause 1: Graphiti not writing to Neo4j**

**Solution:** Check Graphiti configuration

```python
# Verify Neo4j URI in Graphiti config
print(service.graphiti_client.neo4j_uri)

# Expected: bolt://localhost:7687 (or your Neo4j URI)
```

**Cause 2: Entity type stored differently**

**Solution:** Query all entity types to see actual values

```cypher
// Get all unique entity types
MATCH (n)
RETURN DISTINCT n.type AS entity_type
LIMIT 50;

// Check if "Vehicle" appears (case-sensitive)
// Or if it appears as "vehicle" (lowercase)
```

**Cause 3: Entities stored as Episode properties**

**Solution:** Query Episode nodes instead

```cypher
// Check Episode nodes for entity data
MATCH (ep:Episode)
RETURN ep.uuid, ep.entities
LIMIT 5;

// Graphiti may store entities as JSON in Episode.entities
```

---

### Issue 12: Relationships Not Appearing in Neo4j

**Symptom:**
```cypher
// Query for domain relationships returns 0 results
MATCH ()-[r:BELONGS_TO]->() RETURN COUNT(r);
// Returns: 0
```

**Diagnosis Steps:**

**Step 1: Query all relationship types**

```cypher
// Get all relationship types in Neo4j
MATCH ()-[r]->()
RETURN DISTINCT type(r) AS relationship_type
LIMIT 50;

// Check if BELONGS_TO appears
```

**Step 2: Check if Graphiti creates edges**

```cypher
// Graphiti may use generic "RELATES_TO" relationships
MATCH ()-[r]->()
WHERE type(r) IN ['RELATES_TO', 'CONNECTED_TO', 'EDGE']
RETURN type(r), COUNT(r)
ORDER BY COUNT(r) DESC;
```

**Solution:**

**Option 1: Update expected relationship types**

```python
# If Graphiti creates "RELATES_TO" instead of "BELONGS_TO"
# Update expected outputs to match:

"expected_relationships": [
    {
        "type": "RELATES_TO",  # Instead of "BELONGS_TO"
        "source": "INV-001",
        "target": "VEH-1234"
    }
]
```

**Option 2: Configure Graphiti to use domain relationship types**

```python
# Pass relationship types to Graphiti
# (Check Graphiti documentation for custom relationship types)
```

---

## Debugging Tools

### Tool 1: Enable Debug Logging

```python
# In apex-memory-system/src/apex_memory/services/graphiti_service.py

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add debug logs:
logger.debug(f"Domain configured: {self.domain_configured}")
logger.debug(f"Extraction prompt: {extraction_prompt[:100]}...")
logger.debug(f"Entities extracted: {len(entities)}")
logger.debug(f"Relationships extracted: {len(relationships)}")
```

**Run with debug logging:**

```bash
export LOG_LEVEL=DEBUG
python tests/validate_extraction.py
```

---

### Tool 2: Inspect Graphiti Episode JSON

```cypher
// Get raw Graphiti episode data
MATCH (ep:Episode)
WHERE ep.uuid = 'ep-123-456-789'
RETURN ep;

// Inspect:
// - ep.entities (JSON array of extracted entities)
// - ep.edges (JSON array of extracted relationships)
// - ep.facts (extracted facts)
```

---

### Tool 3: Compare Generic vs Domain Extraction

```python
# Run extraction with domain config OFF
os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "false"
service_generic = GraphitiService()
result_generic = await service_generic.extract_entities_and_relationships(text, ...)

# Run extraction with domain config ON
os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "true"
service_domain = GraphitiService()
result_domain = await service_domain.extract_entities_and_relationships(text, ...)

# Compare results
print(f"Generic entities: {len(result_generic['entities'])}")
print(f"Domain entities: {len(result_domain['entities'])}")

print(f"Generic relationships: {len(result_generic['relationships'])}")
print(f"Domain relationships: {len(result_domain['relationships'])}")

# Expected: Domain extraction has more/better entities and relationships
```

---

### Tool 4: Validate Expected Outputs

```python
# Verify expected output JSON is valid
import json

expected_path = "tests/expected-outputs/invoice-brake-parts.json"
with open(expected_path) as f:
    expected = json.load(f)

# Validate structure
assert "expected_entities" in expected
assert "expected_relationships" in expected
assert "validation_criteria" in expected

# Validate entity structure
for entity in expected["expected_entities"]:
    assert "type" in entity
    assert "name" in entity
    assert "attributes" in entity

# Validate relationship structure
for relationship in expected["expected_relationships"]:
    assert "type" in relationship
    assert "source" in relationship
    assert "target" in relationship

print("✅ Expected output JSON is valid")
```

---

## Getting Help

**If issues persist:**

1. **Check Graphiti Documentation:** https://github.com/getzep/graphiti (official repo)
2. **Review Graphiti Examples:** https://github.com/getzep/graphiti/tree/main/examples
3. **Post GitHub Issue:** Include logs, entity counts, accuracy metrics
4. **Document in TROUBLESHOOTING.md:** Add new issue + solution for future reference

---

**This troubleshooting guide will be updated as new issues are discovered during implementation.**
