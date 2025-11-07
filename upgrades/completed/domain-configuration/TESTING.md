# Graphiti Domain Configuration - Testing Specifications

**Project:** Graphiti Domain Configuration for Trucking/Logistics Domain
**Test Coverage:** 10 sample documents + 15 automated tests
**Success Criteria:** 90%+ extraction accuracy, 100% test pass rate

---

## Table of Contents

1. [Test Strategy](#test-strategy)
2. [Sample Documents](#sample-documents)
3. [Expected Outputs](#expected-outputs)
4. [Automated Tests](#automated-tests)
5. [Manual Validation](#manual-validation)
6. [Performance Benchmarks](#performance-benchmarks)

---

## Test Strategy

### Testing Approach

**3-Layer Validation:**

1. **Unit Tests** - Validate domain config module functions
2. **Integration Tests** - Validate end-to-end extraction with domain config
3. **Manual Validation** - Visual inspection of Neo4j graph

### Success Metrics

**Minimum Requirements:**

- **Entity Accuracy:** 90%+ across all test documents
- **Relationship Accuracy:** 90%+ across all test documents
- **Feature Flag:** Works correctly (on/off)
- **Baseline Preservation:** All existing 162 tests still pass
- **No Breaking Changes:** Generic extraction still works

**Nice to Have:**

- Entity attribute accuracy (e.g., amounts, dates, IDs)
- Multi-hop relationship paths
- Temporal reasoning capabilities

---

## Sample Documents

### Document 1: Parts Invoice

**File:** `tests/sample-documents/invoice-brake-parts.txt`

**Content:**
```
ACME Auto Parts
Invoice #INV-2025-10-20-001
Date: October 20, 2025

Bill To:
ACME Trucking LLC
123 Fleet Street
Chicago, IL 60601

Vehicle: Truck VEH-1234 (2022 Freightliner Cascadia)

Parts and Services:
- Brake pads (front axle): $345.00
- Labor (brake replacement): $450.00
- Shop supplies: $25.00

Total: $820.00

Payment Method: ACH Transfer #TX-2025-5678
Payment Date: October 21, 2025

Technician: Mike Johnson
Service completed on October 20, 2025

Notes: Routine brake maintenance for VEH-1234. Brake pads replaced due to wear.
Next service recommended in 6 months.
```

**Expected Entities:** 5 (PartsInvoice, Vehicle, Vendor, BankTransaction, Customer)
**Expected Relationships:** 4 (BELONGS_TO, SUPPLIED_BY, PAID_BY, BILLED_TO)

---

### Document 2: Shipment Delivery Record

**File:** `tests/sample-documents/shipment-delivery-record.txt`

**Content:**
```
DELIVERY RECORD

Shipment ID: SH-2025-10-19-001
Origin: Chicago Distribution Center (123 Warehouse Rd, Chicago, IL)
Destination: Dallas Customer Warehouse (456 Commerce St, Dallas, TX)

Driver: John Smith (CDL #IL-1234567)
Vehicle: Truck VEH-5678 (2023 Kenworth T680)

Cargo:
- 15 pallets of electronics
- Total weight: 12,500 lbs
- Customer: Johnson Manufacturing LLC (Customer #C-5678)

Route: Interstate I-35 corridor (Route #R-100)
Estimated distance: 950 miles

Departure: October 19, 2025 at 06:00 AM
Arrival: October 20, 2025 at 10:30 PM
Status: DELIVERED

Driver signature: John Smith
Customer signature: Sarah Williams (Receiving Manager)

Invoice #INV-2025-10-20-100 billed to Johnson Manufacturing LLC for $2,450.00
```

**Expected Entities:** 8 (Shipment, Driver, Vehicle, 2x Location, Customer, Route, PartsInvoice)
**Expected Relationships:** 5 (ASSIGNED_TO x2, DELIVERED_TO, BILLED_TO, FOLLOWS_ROUTE)

---

### Document 3: Maintenance Record

**File:** `tests/sample-documents/maintenance-oil-change.txt`

**Content:**
```
MAINTENANCE RECORD

Record ID: MR-2025-10-18-001
Vehicle: Truck VEH-1234 (2022 Freightliner Cascadia)
Date: October 18, 2025

Service Type: Routine Oil Change
Mileage: 125,450 miles

Parts Used:
- Oil filter: $45.00
- 12 quarts synthetic oil: $156.00

Labor: $85.00
Total: $286.00

Technician: Mike Johnson
Service Provider: ACME Auto Parts & Service
Location: 456 Service Rd, Chicago, IL

Payment: Corporate Account #ACCT-1234
Payment Date: October 18, 2025

Notes: Routine maintenance completed. Next oil change recommended at 135,000 miles.
Vehicle in good condition.
```

**Expected Entities:** 5 (MaintenanceRecord, Vehicle, Vendor, Location, BankTransaction)
**Expected Relationships:** 3 (PERFORMED_ON, SUPPLIED_BY, LOCATED_AT)

---

### Document 4: Bank Statement

**File:** `tests/sample-documents/bank-statement.txt`

**Content:**
```
ACME TRUCKING LLC
Corporate Account Statement
Account #ACCT-1234
Statement Period: October 1-31, 2025

Transactions:

10/18/2025 - ACH Debit - ACME Auto Parts & Service - $286.00 - TX-2025-001
            (Oil change for VEH-1234)

10/20/2025 - ACH Debit - ACME Auto Parts - $820.00 - TX-2025-5678
            (Brake repair for VEH-1234)

10/21/2025 - Wire Transfer - Johnson Manufacturing LLC - $2,450.00 - TX-2025-100
            (Payment for Shipment SH-2025-10-19-001)

10/22/2025 - ACH Debit - Shell Fuel - $425.00 - TX-2025-150
            (Fuel for VEH-5678)

Total Debits: $1,531.00
Total Credits: $2,450.00
Net: $919.00
```

**Expected Entities:** 8 (4x BankTransaction, 3x Vendor, 2x Vehicle, 1x Shipment, 1x Customer)
**Expected Relationships:** 8 (PAID_BY x3, BELONGS_TO x2, DELIVERED_TO, SUPPLIED_BY x2)

---

### Document 5: GPS Tracking Report

**File:** `tests/sample-documents/gps-tracking.txt`

**Content:**
```
GPS TRACKING REPORT
Vehicle: Truck VEH-5678 (2023 Kenworth T680)
Driver: John Smith (CDL #IL-1234567)
Date: October 19-20, 2025
Route: R-100 (Chicago to Dallas via I-35)

Location Updates:

10/19/2025 06:00 AM - Chicago Distribution Center (123 Warehouse Rd, Chicago, IL)
Status: Departed with Shipment SH-2025-10-19-001

10/19/2025 12:30 PM - Kansas City Terminal (789 Terminal Blvd, Kansas City, MO)
Status: Refueling stop

10/19/2025 06:45 PM - Oklahoma City Truck Stop (456 Highway 35, Oklahoma City, OK)
Status: Driver rest break

10/20/2025 10:30 PM - Dallas Customer Warehouse (456 Commerce St, Dallas, TX)
Status: Shipment delivered to Johnson Manufacturing LLC

Total Distance: 952 miles
Average Speed: 58 mph
Fuel Efficiency: 6.8 mpg
```

**Expected Entities:** 8 (Vehicle, Driver, 4x Location, Route, Shipment, Customer)
**Expected Relationships:** 6 (ASSIGNED_TO x2, LOCATED_AT x4, FOLLOWS_ROUTE, DELIVERED_TO)

---

### Document 6: Fuel Purchase Invoice

**File:** `tests/sample-documents/fuel-purchase.txt`

**Content:**
```
SHELL FUEL STATION
Transaction Receipt
Station #SH-4567
456 Highway 35, Oklahoma City, OK

Date: October 19, 2025
Time: 06:50 PM

Vehicle: Truck VEH-5678
Driver: John Smith

Fuel Type: Diesel
Gallons: 85.5
Price per gallon: $3.45
Total: $295.00

Payment Method: Fleet Card #FC-1234
Transaction ID: TX-2025-150

Odometer: 89,250 miles
MPG since last fill: 6.8 mpg

Driver signature: John Smith
```

**Expected Entities:** 5 (PartsInvoice, Vehicle, Driver, Vendor, Location, BankTransaction)
**Expected Relationships:** 4 (BELONGS_TO, SUPPLIED_BY, PAID_BY, LOCATED_AT)

---

### Document 7: Driver Assignment

**File:** `tests/sample-documents/driver-assignment.txt`

**Content:**
```
DRIVER ASSIGNMENT NOTICE

Driver: Sarah Johnson
CDL #: IL-9876543
Date: October 21, 2025

Assigned Vehicle: Truck VEH-1234 (2022 Freightliner Cascadia)
Effective Date: October 21, 2025

Assignment Details:
- Primary route: R-200 (Chicago to Atlanta via I-65)
- Customer: Williams Distribution LLC (Customer #C-9876)
- Expected weekly mileage: 2,500 miles

Vehicle current location: Chicago Distribution Center
Vehicle status: Maintenance complete, ready for assignment

Next scheduled shipment: SH-2025-10-22-001
Origin: Chicago Distribution Center
Destination: Atlanta Warehouse
Cargo: 18 pallets of automotive parts

Assignment approved by: Fleet Manager Tom Brown
```

**Expected Entities:** 7 (Driver, Vehicle, 2x Location, Route, Customer, Shipment)
**Expected Relationships:** 5 (ASSIGNED_TO x2, LOCATED_AT, DELIVERED_TO, FOLLOWS_ROUTE)

---

### Document 8: Route Planning Document

**File:** `tests/sample-documents/route-planning.txt`

**Content:**
```
ROUTE PLANNING DOCUMENT

Route ID: R-200
Route Name: Chicago-Atlanta Corridor
Primary Highway: Interstate I-65

Waypoints:
1. Chicago Distribution Center (123 Warehouse Rd, Chicago, IL) - Origin
2. Indianapolis Terminal (456 Terminal Dr, Indianapolis, IN) - Refueling
3. Louisville Warehouse (789 Commerce Blvd, Louisville, KY) - Optional stop
4. Atlanta Warehouse (321 Industrial Pkwy, Atlanta, GA) - Destination

Total Distance: 715 miles
Estimated Travel Time: 11 hours (excluding breaks)

Assigned Drivers:
- Sarah Johnson (CDL #IL-9876543) - Primary
- Mike Davis (CDL #IL-1122334) - Backup

Assigned Vehicles:
- VEH-1234 (2022 Freightliner Cascadia)
- VEH-9999 (2023 Volvo VNL)

Typical Cargo:
- Automotive parts
- Electronics
- Industrial supplies

Primary Customer: Williams Distribution LLC (Customer #C-9876)

Scheduled Shipments (Next 7 days):
- SH-2025-10-22-001 (VEH-1234, Sarah Johnson)
- SH-2025-10-24-001 (VEH-9999, Mike Davis)
```

**Expected Entities:** 10 (Route, 4x Location, 2x Driver, 2x Vehicle, 2x Shipment, Customer)
**Expected Relationships:** 8+ (ASSIGNED_TO x4, DELIVERED_TO x2, FOLLOWS_ROUTE x2, LOCATED_AT)

---

### Document 9: Customer Contract

**File:** `tests/sample-documents/customer-contract.txt`

**Content:**
```
CUSTOMER SERVICE AGREEMENT

Customer: Williams Distribution LLC
Customer ID: C-9876
Contract ID: CONT-2025-001
Effective Date: January 1, 2025

Service Details:
- Weekly shipments from Chicago to Atlanta
- Route: R-200 (Chicago-Atlanta Corridor)
- Estimated volume: 15-20 shipments per month

Assigned Fleet:
- Primary Vehicle: VEH-1234 (2022 Freightliner Cascadia)
- Backup Vehicle: VEH-9999 (2023 Volvo VNL)

Assigned Drivers:
- Primary Driver: Sarah Johnson (CDL #IL-9876543)
- Backup Driver: Mike Davis (CDL #IL-1122334)

Delivery Locations:
- Main: Atlanta Warehouse (321 Industrial Pkwy, Atlanta, GA)
- Secondary: Louisville Warehouse (789 Commerce Blvd, Louisville, KY)

Billing Terms:
- Rate: $2.50 per mile
- Invoice frequency: Weekly
- Payment terms: Net 30 days
- Payment method: ACH transfer to Account #ACCT-1234

Recent Invoices:
- INV-2025-10-15-001: $1,787.50 (715 miles @ $2.50/mile)
- INV-2025-10-22-001: $1,787.50 (715 miles @ $2.50/mile)

Contract Manager: Tom Brown
Customer Contact: Jennifer Williams (jwilliams@williamsdist.com)
```

**Expected Entities:** 12+ (Customer, Route, 2x Vehicle, 2x Driver, 2x Location, 2x PartsInvoice, BankTransaction)
**Expected Relationships:** 10+ (ASSIGNED_TO x4, DELIVERED_TO x2, BILLED_TO x2, PAID_BY, FOLLOWS_ROUTE)

---

### Document 10: Multi-Vehicle Maintenance Schedule

**File:** `tests/sample-documents/maintenance-schedule.txt`

**Content:**
```
FLEET MAINTENANCE SCHEDULE
Week of October 21-27, 2025

Vehicle: VEH-1234 (2022 Freightliner Cascadia)
Current Mileage: 125,750
Location: Chicago Distribution Center
Assigned Driver: Sarah Johnson

Scheduled Maintenance:
- 10/25/2025: Tire rotation (Record #MR-2025-10-25-001)
  Vendor: Johnson Tire & Service
  Estimated Cost: $150.00
  Location: 123 Service Rd, Chicago, IL

- 10/28/2025: DOT inspection (Record #MR-2025-10-28-001)
  Vendor: State Inspection Station
  Estimated Cost: $75.00
  Location: 456 State Rd, Chicago, IL

Vehicle: VEH-5678 (2023 Kenworth T680)
Current Mileage: 89,500
Location: Dallas Customer Warehouse
Assigned Driver: John Smith

Scheduled Maintenance:
- 10/23/2025: Oil change (Record #MR-2025-10-23-001)
  Vendor: ACME Auto Parts & Service
  Estimated Cost: $286.00
  Location: 789 Service Rd, Dallas, TX

Vehicle: VEH-9999 (2023 Volvo VNL)
Current Mileage: 45,200
Location: Chicago Distribution Center
Assigned Driver: Mike Davis

Scheduled Maintenance:
- 10/26/2025: Brake inspection (Record #MR-2025-10-26-001)
  Vendor: Johnson Tire & Service
  Estimated Cost: $125.00
  Location: 123 Service Rd, Chicago, IL

Payment: All services billed to Corporate Account #ACCT-1234
Expected total cost: $636.00
```

**Expected Entities:** 15+ (3x Vehicle, 3x Driver, 4x MaintenanceRecord, 3x Vendor, 3x Location, BankTransaction)
**Expected Relationships:** 12+ (PERFORMED_ON x4, ASSIGNED_TO x3, LOCATED_AT x7, SUPPLIED_BY x4, PAID_BY)

---

## Expected Outputs

### Expected Output Template

Each test document has a corresponding expected output JSON file in `tests/expected-outputs/`.

**Format:**
```json
{
  "document": "filename.txt",
  "expected_entities": [
    {
      "type": "EntityType",
      "name": "Entity Name or ID",
      "attributes": {
        "key": "value"
      }
    }
  ],
  "expected_relationships": [
    {
      "type": "RELATIONSHIP_TYPE",
      "source": "Source Entity Name",
      "target": "Target Entity Name"
    }
  ],
  "validation_criteria": {
    "min_entities": 5,
    "min_relationships": 4,
    "required_entity_types": ["PartsInvoice", "Vehicle"],
    "accuracy_threshold": 0.90
  }
}
```

### Accuracy Calculation

**Entity Accuracy:**
```
Entity Accuracy = (Correctly Extracted Entities) / (Total Expected Entities)
```

**Relationship Accuracy:**
```
Relationship Accuracy = (Correctly Extracted Relationships) / (Total Expected Relationships)
```

**Overall Accuracy:**
```
Overall Accuracy = (Entity Accuracy + Relationship Accuracy) / 2
```

**Pass Criteria:**
```
Pass if Overall Accuracy >= 90%
```

---

## Automated Tests

### Test 1: Domain Config Module Loads

**File:** `apex-memory-system/tests/unit/test_domain_config.py`

```python
"""Unit tests for domain configuration module."""

import pytest
from apex_memory.config.domain_config import (
    get_domain_config,
    validate_extraction,
    EntityType,
    RelationshipType,
    TRUCKING_DOMAIN_CONFIG
)


def test_domain_config_loads():
    """Test that domain config loads successfully."""
    config = get_domain_config()

    assert config is not None
    assert len(config.entities) == 10  # 10 entity types
    assert len(config.relationships) == 8  # 8 relationship types
    assert config.extraction_prompt is not None
    assert len(config.extraction_prompt) > 100  # Non-trivial prompt


def test_all_entity_types_defined():
    """Test that all entity types are defined."""
    config = get_domain_config()

    entity_types = [e.type.value for e in config.entities]

    assert "Vehicle" in entity_types
    assert "PartsInvoice" in entity_types
    assert "Vendor" in entity_types
    assert "BankTransaction" in entity_types
    assert "Driver" in entity_types
    assert "Shipment" in entity_types
    assert "Location" in entity_types
    assert "Customer" in entity_types
    assert "MaintenanceRecord" in entity_types
    assert "Route" in entity_types


def test_all_relationship_types_defined():
    """Test that all relationship types are defined."""
    config = get_domain_config()

    rel_types = [r.type.value for r in config.relationships]

    assert "BELONGS_TO" in rel_types
    assert "SUPPLIED_BY" in rel_types
    assert "PAID_BY" in rel_types
    assert "ASSIGNED_TO" in rel_types
    assert "DELIVERED_TO" in rel_types
    assert "BILLED_TO" in rel_types
    assert "LOCATED_AT" in rel_types
    assert "PERFORMED_ON" in rel_types


def test_validation_function():
    """Test validation function with mock data."""
    config = get_domain_config()

    # Mock extracted entities
    entities = [
        {"type": "Vehicle", "name": "VEH-1234"},
        {"type": "PartsInvoice", "name": "INV-001"},
        {"type": "Vendor", "name": "ACME Auto Parts"}
    ]

    # Mock extracted relationships
    relationships = [
        {"type": "BELONGS_TO", "source": "INV-001", "target": "VEH-1234"},
        {"type": "SUPPLIED_BY", "source": "INV-001", "target": "ACME Auto Parts"}
    ]

    # Validate
    result = validate_extraction(entities, relationships, config)

    assert result["valid"] is True
    assert result["entity_count"] == 3
    assert result["relationship_count"] == 2
    assert len(result["errors"]) == 0


def test_validation_fails_with_too_few_entities():
    """Test validation fails when too few entities extracted."""
    config = get_domain_config()
    config.validation_rules["min_entities_per_document"] = 5

    # Only 2 entities
    entities = [
        {"type": "Vehicle", "name": "VEH-1234"},
        {"type": "PartsInvoice", "name": "INV-001"}
    ]
    relationships = []

    result = validate_extraction(entities, relationships, config)

    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_entity_schemas_have_examples():
    """Test that all entity schemas include examples."""
    config = get_domain_config()

    for entity_schema in config.entities:
        assert len(entity_schema.examples) > 0, f"{entity_schema.type} missing examples"


def test_relationship_schemas_have_examples():
    """Test that all relationship schemas include examples."""
    config = get_domain_config()

    for rel_schema in config.relationships:
        assert len(rel_schema.examples) > 0, f"{rel_schema.type} missing examples"
```

**Run:**
```bash
cd apex-memory-system
pytest tests/unit/test_domain_config.py -v
```

**Expected:** 8/8 tests pass

---

### Test 2: GraphitiService Uses Domain Config

**File:** `apex-memory-system/tests/unit/test_graphiti_service_domain.py`

```python
"""Unit tests for GraphitiService with domain configuration."""

import os
import pytest
from unittest.mock import AsyncMock, patch
from apex_memory.services.graphiti_service import GraphitiService


@pytest.fixture
def enable_domain_config():
    """Enable domain configuration for tests."""
    os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "true"
    yield
    os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "false"


def test_domain_config_disabled_by_default():
    """Test that domain config is disabled by default."""
    service = GraphitiService()
    assert service.domain_configured is False
    assert service.domain_config is None


def test_domain_config_enabled(enable_domain_config):
    """Test that domain config is enabled when flag set."""
    service = GraphitiService()
    assert service.domain_configured is True
    assert service.domain_config is not None
    assert len(service.domain_config.entities) == 10


@pytest.mark.asyncio
async def test_extraction_uses_domain_prompt(enable_domain_config):
    """Test that extraction uses domain-specific prompt."""
    service = GraphitiService()

    # Mock Graphiti client
    with patch.object(service.graphiti_client, 'add_episode', new_callable=AsyncMock) as mock_add:
        mock_add.return_value = {
            "entities": [{"type": "Vehicle", "name": "VEH-1234"}],
            "edges": [],
            "episode_id": "ep-123"
        }

        # Extract entities
        result = await service.extract_entities_and_relationships(
            text="Test document",
            source="test",
            metadata={"document_id": "doc-123"}
        )

        # Verify custom prompt was passed
        call_kwargs = mock_add.call_args.kwargs
        assert "custom_prompt" in call_kwargs
        assert call_kwargs["custom_prompt"] is not None
        assert "Vehicle" in call_kwargs["custom_prompt"]  # Domain-specific


@pytest.mark.asyncio
async def test_extraction_validates_results(enable_domain_config):
    """Test that extraction validates results against domain config."""
    service = GraphitiService()

    # Mock Graphiti client
    with patch.object(service.graphiti_client, 'add_episode', new_callable=AsyncMock) as mock_add:
        mock_add.return_value = {
            "entities": [
                {"type": "Vehicle", "name": "VEH-1234"},
                {"type": "PartsInvoice", "name": "INV-001"}
            ],
            "edges": [
                {"type": "BELONGS_TO", "source": "INV-001", "target": "VEH-1234"}
            ],
            "episode_id": "ep-123"
        }

        # Extract entities
        result = await service.extract_entities_and_relationships(
            text="Invoice for vehicle VEH-1234",
            source="test",
            metadata={"document_id": "doc-123"}
        )

        # Verify validation results included
        assert result["validation"] is not None
        assert result["validation"]["valid"] is True
        assert result["validation"]["entity_count"] == 2
        assert result["validation"]["relationship_count"] == 1
```

**Run:**
```bash
cd apex-memory-system
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true pytest tests/unit/test_graphiti_service_domain.py -v
```

**Expected:** 4/4 tests pass

---

### Test 3: End-to-End Document Extraction

**File:** `apex-memory-system/tests/integration/test_domain_extraction_e2e.py`

```python
"""End-to-end integration tests for domain-configured extraction."""

import os
import pytest
from pathlib import Path
from apex_memory.services.graphiti_service import GraphitiService


@pytest.fixture
def enable_domain_config():
    """Enable domain configuration for tests."""
    os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "true"
    yield
    os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "false"


@pytest.fixture
def sample_invoice():
    """Sample invoice document."""
    return """
ACME Auto Parts
Invoice #INV-2025-10-20-001
Date: October 20, 2025

Bill To: ACME Trucking LLC
Vehicle: Truck VEH-1234 (2022 Freightliner Cascadia)

Parts and Services:
- Brake pads: $345.00
- Labor: $450.00
Total: $795.00

Payment: ACH Transfer #TX-5678
"""


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invoice_extraction(enable_domain_config, sample_invoice):
    """Test extraction of invoice document."""
    service = GraphitiService()

    result = await service.extract_entities_and_relationships(
        text=sample_invoice,
        source="test",
        metadata={"document_id": "test-invoice-001"}
    )

    entities = result["entities"]
    relationships = result["relationships"]

    # Should extract at least: PartsInvoice, Vehicle, Vendor, BankTransaction
    assert len(entities) >= 4

    # Should create at least: BELONGS_TO, SUPPLIED_BY, PAID_BY
    assert len(relationships) >= 3

    # Verify entity types are domain-specific
    entity_types = [e["type"] for e in entities]
    assert "PartsInvoice" in entity_types or "Vehicle" in entity_types

    # Verify validation passed
    assert result["validation"]["valid"] is True
```

**Run:**
```bash
cd apex-memory-system
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true pytest tests/integration/test_domain_extraction_e2e.py -v -m integration
```

**Expected:** 1/1 test passes

---

### Test 4: Baseline Preservation

**File:** Existing test suite

**Test:** Verify all existing 162 tests still pass with domain config DISABLED

```bash
cd apex-memory-system

# Disable domain config
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false

# Run full test suite
pytest tests/ --ignore=tests/load/ -v

# Expected: 162 tests pass (Enhanced Saga baseline preserved)
```

**Expected:** 162/162 tests pass (no regression)

---

### Test 5: Feature Flag Toggle

**File:** `apex-memory-system/tests/integration/test_feature_flag.py`

```python
"""Test feature flag functionality."""

import os
import pytest
from apex_memory.services.graphiti_service import GraphitiService


def test_feature_flag_off_by_default():
    """Test feature flag is off by default."""
    os.environ.pop("ENABLE_DOMAIN_CONFIGURED_GRAPHITI", None)

    service = GraphitiService()
    assert service.domain_configured is False


def test_feature_flag_on():
    """Test feature flag enables domain config."""
    os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "true"

    service = GraphitiService()
    assert service.domain_configured is True


def test_feature_flag_off_explicit():
    """Test feature flag can be explicitly disabled."""
    os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "false"

    service = GraphitiService()
    assert service.domain_configured is False


def test_feature_flag_case_insensitive():
    """Test feature flag is case insensitive."""
    os.environ["ENABLE_DOMAIN_CONFIGURED_GRAPHITI"] = "TRUE"

    service = GraphitiService()
    assert service.domain_configured is True
```

**Run:**
```bash
cd apex-memory-system
pytest tests/integration/test_feature_flag.py -v
```

**Expected:** 4/4 tests pass

---

## Manual Validation

### Neo4j Visual Inspection

**After running validation script, verify entities in Neo4j Browser:**

**Step 1: Open Neo4j Browser**
```
http://localhost:7474
```

**Step 2: Count Entity Types**
```cypher
MATCH (n)
WHERE n.type IN [
  'Vehicle', 'PartsInvoice', 'Vendor', 'BankTransaction',
  'Driver', 'Shipment', 'Location', 'Customer',
  'MaintenanceRecord', 'Route'
]
RETURN n.type AS entity_type, COUNT(n) AS count
ORDER BY count DESC;
```

**Expected:** All 10 entity types present with counts > 0

**Step 3: Count Relationship Types**
```cypher
MATCH ()-[r]->()
WHERE type(r) IN [
  'BELONGS_TO', 'SUPPLIED_BY', 'PAID_BY', 'ASSIGNED_TO',
  'DELIVERED_TO', 'BILLED_TO', 'LOCATED_AT', 'PERFORMED_ON'
]
RETURN type(r) AS relationship_type, COUNT(r) AS count
ORDER BY count DESC;
```

**Expected:** All 8 relationship types present with counts > 0

**Step 4: Visualize Invoice → Vehicle Path**
```cypher
MATCH path = (invoice:PartsInvoice)-[:BELONGS_TO]->(vehicle:Vehicle)
RETURN path
LIMIT 10;
```

**Expected:** Visual graph showing invoice nodes connected to vehicle nodes

**Step 5: Visualize Multi-Hop Path**
```cypher
MATCH path = (invoice:PartsInvoice)-[:BELONGS_TO]->(vehicle:Vehicle)
            -[:ASSIGNED_TO]->(driver:Driver)
RETURN path
LIMIT 5;
```

**Expected:** Visual graph showing invoice → vehicle → driver paths

---

## Performance Benchmarks

### Extraction Latency

**Test:** Measure time to extract entities from sample documents

**Acceptable Range:**
- Small documents (<500 chars): <2 seconds
- Medium documents (500-2000 chars): <5 seconds
- Large documents (>2000 chars): <10 seconds

**Benchmark Script:**

```python
import time
import asyncio
from apex_memory.services.graphiti_service import GraphitiService

async def benchmark_extraction():
    service = GraphitiService()

    documents = [
        ("small", "Invoice for $100"),
        ("medium", open("tests/sample-documents/invoice-brake-parts.txt").read()),
        ("large", open("tests/sample-documents/maintenance-schedule.txt").read())
    ]

    for doc_type, text in documents:
        start = time.time()
        await service.extract_entities_and_relationships(
            text=text,
            source="benchmark",
            metadata={"doc_type": doc_type}
        )
        duration = time.time() - start
        print(f"{doc_type}: {duration:.2f}s")

asyncio.run(benchmark_extraction())
```

**Expected Output:**
```
small: 1.23s
medium: 3.45s
large: 8.67s
```

---

### Accuracy Over Time

**Test:** Track extraction accuracy over multiple runs

**Goal:** Consistent 90%+ accuracy across all runs

**Tracking:**
```bash
# Run validation 3 times
for i in {1..3}; do
  echo "Run $i:"
  ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true python tests/validate_extraction.py | grep "Average accuracy"
done
```

**Expected:**
```
Run 1: Average accuracy: 92.5%
Run 2: Average accuracy: 93.1%
Run 3: Average accuracy: 91.8%
```

All runs should show 90%+ average accuracy (consistent quality).

---

## Test Execution Checklist

### Pre-Implementation Tests

- [ ] Baseline tests pass (162/162)
- [ ] Feature flag off by default
- [ ] No domain config loaded

### Post-Implementation Tests

- [ ] Domain config module tests pass (8/8)
- [ ] GraphitiService domain tests pass (4/4)
- [ ] End-to-end extraction test passes (1/1)
- [ ] Feature flag tests pass (4/4)
- [ ] Baseline preservation tests pass (162/162)

### Validation Tests

- [ ] Validation script runs successfully
- [ ] 90%+ average accuracy achieved
- [ ] All 10 test documents pass
- [ ] Neo4j contains domain entity types
- [ ] Neo4j contains domain relationship types

### Performance Tests

- [ ] Extraction latency within acceptable range
- [ ] Consistent accuracy across multiple runs
- [ ] No memory leaks during batch extraction

---

## Success Criteria Summary

**Minimum Requirements for Phase 3 IMPLEMENTED:**

1. ✅ **90%+ Extraction Accuracy** (measured across 10 test documents)
2. ✅ **All 10 Entity Types Recognized** (Vehicle, PartsInvoice, Vendor, etc.)
3. ✅ **All 8 Relationship Types Created** (BELONGS_TO, SUPPLIED_BY, etc.)
4. ✅ **Feature Flag Works** (on/off toggle with safe defaults)
5. ✅ **Baseline Preserved** (all 162 existing tests still pass)
6. ✅ **Zero Breaking Changes** (generic extraction still works)

**When all criteria met, Phase 3 verification can be marked FULLY IMPLEMENTED.**

---

**Next Steps:** After passing all tests, proceed to deployment using instructions in IMPLEMENTATION.md.
