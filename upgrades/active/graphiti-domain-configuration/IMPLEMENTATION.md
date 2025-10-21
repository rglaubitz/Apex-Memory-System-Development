# Graphiti Domain Configuration - Implementation Guide

**Project:** Graphiti Domain Configuration for Trucking/Logistics Domain
**Timeline:** 2-3 days
**Status:** Ready for Implementation
**Prerequisites:** Phase 2 Complete Data Pipeline verified and operational

---

## Table of Contents

1. [Overview](#overview)
2. [Day 1: Schema Definition](#day-1-schema-definition)
3. [Day 2: Configuration Module & Integration](#day-2-configuration-module--integration)
4. [Day 3: Validation & Testing](#day-3-validation--testing)
5. [Validation Criteria](#validation-criteria)
6. [Rollback Plan](#rollback-plan)

---

## Overview

### What We're Building

A domain-specific configuration system for Graphiti that provides:

1. **Entity Type Definitions** - 8-10 trucking/logistics entity types
2. **Relationship Type Definitions** - 6-8 semantic relationships
3. **Custom Extraction Prompts** - Domain knowledge to guide GPT-5
4. **Validation Framework** - Ensure 90%+ extraction accuracy

### Architecture Overview

```
Current (Generic):
Document → Graphiti (generic extraction) → Neo4j
Problem: Random entity types, missing relationships

After Domain Configuration:
Document → Graphiti (domain-configured) → Neo4j
Result: Accurate entity types, semantic relationships
```

### Implementation Strategy

**Principle:** Additive, non-breaking changes with feature flag

- All changes behind `ENABLE_DOMAIN_CONFIGURED_GRAPHITI` feature flag
- Existing generic extraction remains default (safe fallback)
- Domain configuration opt-in via environment variable
- Zero impact on existing workflows

---

## Day 1: Schema Definition

**Goal:** Define entity types, relationship types, and extraction prompts

**Estimated Time:** 4-6 hours

### Step 1.1: Create Domain Configuration Module

**File:** `apex-memory-system/src/apex_memory/config/domain_config.py`

```python
"""
Domain-specific configuration for Graphiti entity extraction.

This module defines entity types, relationship types, and extraction
prompts for the trucking/logistics domain.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """
    Domain-specific entity types for trucking/logistics.

    These types guide Graphiti's LLM extraction to recognize
    industry-specific entities instead of generic ones.
    """
    VEHICLE = "Vehicle"
    PARTS_INVOICE = "PartsInvoice"
    VENDOR = "Vendor"
    BANK_TRANSACTION = "BankTransaction"
    DRIVER = "Driver"
    SHIPMENT = "Shipment"
    LOCATION = "Location"
    CUSTOMER = "Customer"
    MAINTENANCE_RECORD = "MaintenanceRecord"
    ROUTE = "Route"


class RelationshipType(str, Enum):
    """
    Domain-specific relationship types for trucking/logistics.

    These relationships define how entities connect in the
    knowledge graph (Neo4j via Graphiti).
    """
    BELONGS_TO = "BELONGS_TO"  # Invoice → Vehicle, Driver → Customer
    SUPPLIED_BY = "SUPPLIED_BY"  # Invoice → Vendor
    PAID_BY = "PAID_BY"  # Invoice → BankTransaction
    ASSIGNED_TO = "ASSIGNED_TO"  # Vehicle → Driver, Shipment → Driver
    DELIVERED_TO = "DELIVERED_TO"  # Shipment → Location
    BILLED_TO = "BILLED_TO"  # Invoice → Customer
    LOCATED_AT = "LOCATED_AT"  # Vehicle → Location
    PERFORMED_ON = "PERFORMED_ON"  # MaintenanceRecord → Vehicle
    FOLLOWS_ROUTE = "FOLLOWS_ROUTE"  # Shipment → Route
    CONTAINS = "CONTAINS"  # Shipment → Items


class EntitySchema(BaseModel):
    """Schema for a domain entity type."""
    type: EntityType
    description: str
    required_attributes: List[str] = Field(default_factory=list)
    optional_attributes: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)


class RelationshipSchema(BaseModel):
    """Schema for a domain relationship type."""
    type: RelationshipType
    description: str
    source_entity: EntityType
    target_entity: EntityType
    examples: List[str] = Field(default_factory=list)


class DomainConfig(BaseModel):
    """Complete domain configuration for Graphiti extraction."""
    entities: List[EntitySchema]
    relationships: List[RelationshipSchema]
    extraction_prompt: str
    validation_rules: Dict[str, any] = Field(default_factory=dict)


# Entity Schemas
VEHICLE_SCHEMA = EntitySchema(
    type=EntityType.VEHICLE,
    description="A truck, trailer, or other vehicle in the fleet",
    required_attributes=["vehicle_id", "type"],
    optional_attributes=["make", "model", "year", "vin", "license_plate"],
    examples=[
        "Truck VEH-1234",
        "2022 Freightliner Cascadia VIN ABC123",
        "Trailer #5678"
    ]
)

PARTS_INVOICE_SCHEMA = EntitySchema(
    type=EntityType.PARTS_INVOICE,
    description="An invoice for parts, repairs, or services",
    required_attributes=["invoice_id", "amount"],
    optional_attributes=["date", "vendor", "parts_list", "labor_cost"],
    examples=[
        "Invoice INV-2025-001 for $1,234.56",
        "Parts invoice from ACME Auto Parts",
        "Repair bill #45678 dated 2025-10-20"
    ]
)

VENDOR_SCHEMA = EntitySchema(
    type=EntityType.VENDOR,
    description="A supplier of parts, services, or fuel",
    required_attributes=["vendor_name"],
    optional_attributes=["vendor_id", "contact_info", "category"],
    examples=[
        "ACME Auto Parts",
        "Johnson Tire & Service",
        "Shell Fuel Station #1234"
    ]
)

BANK_TRANSACTION_SCHEMA = EntitySchema(
    type=EntityType.BANK_TRANSACTION,
    description="A bank transaction, payment, or financial record",
    required_attributes=["transaction_id", "amount"],
    optional_attributes=["date", "account", "payee", "category"],
    examples=[
        "Payment #TX-5678 for $1,234.56",
        "ACH transfer to ACME Auto Parts",
        "Debit $500.00 on 2025-10-20"
    ]
)

DRIVER_SCHEMA = EntitySchema(
    type=EntityType.DRIVER,
    description="A driver employed by or contracted to the company",
    required_attributes=["driver_name"],
    optional_attributes=["driver_id", "cdl_number", "contact_info"],
    examples=[
        "Driver John Smith",
        "CDL holder #1234567",
        "Contract driver Sarah Johnson"
    ]
)

SHIPMENT_SCHEMA = EntitySchema(
    type=EntityType.SHIPMENT,
    description="A delivery, load, or shipment",
    required_attributes=["shipment_id"],
    optional_attributes=["origin", "destination", "cargo", "status", "date"],
    examples=[
        "Shipment #SH-2025-001 from Chicago to Dallas",
        "Load #45678 containing electronics",
        "Delivery to warehouse on 2025-10-21"
    ]
)

LOCATION_SCHEMA = EntitySchema(
    type=EntityType.LOCATION,
    description="A warehouse, terminal, customer site, or geographic location",
    required_attributes=["location_name"],
    optional_attributes=["address", "city", "state", "zip", "coordinates"],
    examples=[
        "Chicago Distribution Center",
        "Customer warehouse at 123 Main St, Dallas TX",
        "Terminal #5 in Atlanta"
    ]
)

CUSTOMER_SCHEMA = EntitySchema(
    type=EntityType.CUSTOMER,
    description="A customer or client receiving services",
    required_attributes=["customer_name"],
    optional_attributes=["customer_id", "contact_info", "billing_address"],
    examples=[
        "ACME Corporation",
        "Customer #C-1234",
        "Johnson Manufacturing LLC"
    ]
)

MAINTENANCE_RECORD_SCHEMA = EntitySchema(
    type=EntityType.MAINTENANCE_RECORD,
    description="A maintenance or repair record for a vehicle",
    required_attributes=["record_id", "vehicle_id"],
    optional_attributes=["date", "type", "description", "cost", "vendor"],
    examples=[
        "Maintenance record #MR-2025-001 for VEH-1234",
        "Oil change on 2025-10-15",
        "Brake repair by Johnson Tire & Service"
    ]
)

ROUTE_SCHEMA = EntitySchema(
    type=EntityType.ROUTE,
    description="A route or path for deliveries",
    required_attributes=["route_id"],
    optional_attributes=["origin", "destination", "waypoints", "distance"],
    examples=[
        "Route #R-100 from Chicago to Dallas",
        "Weekly delivery route covering 5 stops",
        "Interstate route I-35 corridor"
    ]
)

# Relationship Schemas
BELONGS_TO_SCHEMA = RelationshipSchema(
    type=RelationshipType.BELONGS_TO,
    description="Entity belongs to or is owned by another entity",
    source_entity=EntityType.PARTS_INVOICE,
    target_entity=EntityType.VEHICLE,
    examples=[
        "Invoice INV-001 BELONGS_TO Vehicle VEH-1234",
        "Driver John Smith BELONGS_TO Customer ACME Corp"
    ]
)

SUPPLIED_BY_SCHEMA = RelationshipSchema(
    type=RelationshipType.SUPPLIED_BY,
    description="Invoice or parts supplied by a vendor",
    source_entity=EntityType.PARTS_INVOICE,
    target_entity=EntityType.VENDOR,
    examples=[
        "Invoice INV-001 SUPPLIED_BY Vendor ACME Auto Parts"
    ]
)

PAID_BY_SCHEMA = RelationshipSchema(
    type=RelationshipType.PAID_BY,
    description="Invoice paid by a bank transaction",
    source_entity=EntityType.PARTS_INVOICE,
    target_entity=EntityType.BANK_TRANSACTION,
    examples=[
        "Invoice INV-001 PAID_BY Transaction TX-5678"
    ]
)

ASSIGNED_TO_SCHEMA = RelationshipSchema(
    type=RelationshipType.ASSIGNED_TO,
    description="Vehicle or shipment assigned to a driver",
    source_entity=EntityType.VEHICLE,
    target_entity=EntityType.DRIVER,
    examples=[
        "Vehicle VEH-1234 ASSIGNED_TO Driver John Smith",
        "Shipment SH-001 ASSIGNED_TO Driver Sarah Johnson"
    ]
)

DELIVERED_TO_SCHEMA = RelationshipSchema(
    type=RelationshipType.DELIVERED_TO,
    description="Shipment delivered to a location",
    source_entity=EntityType.SHIPMENT,
    target_entity=EntityType.LOCATION,
    examples=[
        "Shipment SH-001 DELIVERED_TO Location Chicago Distribution Center"
    ]
)

BILLED_TO_SCHEMA = RelationshipSchema(
    type=RelationshipType.BILLED_TO,
    description="Invoice billed to a customer",
    source_entity=EntityType.PARTS_INVOICE,
    target_entity=EntityType.CUSTOMER,
    examples=[
        "Invoice INV-001 BILLED_TO Customer ACME Corporation"
    ]
)

LOCATED_AT_SCHEMA = RelationshipSchema(
    type=RelationshipType.LOCATED_AT,
    description="Vehicle currently located at a location",
    source_entity=EntityType.VEHICLE,
    target_entity=EntityType.LOCATION,
    examples=[
        "Vehicle VEH-1234 LOCATED_AT Location Dallas Terminal"
    ]
)

PERFORMED_ON_SCHEMA = RelationshipSchema(
    type=RelationshipType.PERFORMED_ON,
    description="Maintenance performed on a vehicle",
    source_entity=EntityType.MAINTENANCE_RECORD,
    target_entity=EntityType.VEHICLE,
    examples=[
        "MaintenanceRecord MR-001 PERFORMED_ON Vehicle VEH-1234"
    ]
)


# Complete Domain Configuration
TRUCKING_DOMAIN_CONFIG = DomainConfig(
    entities=[
        VEHICLE_SCHEMA,
        PARTS_INVOICE_SCHEMA,
        VENDOR_SCHEMA,
        BANK_TRANSACTION_SCHEMA,
        DRIVER_SCHEMA,
        SHIPMENT_SCHEMA,
        LOCATION_SCHEMA,
        CUSTOMER_SCHEMA,
        MAINTENANCE_RECORD_SCHEMA,
        ROUTE_SCHEMA
    ],
    relationships=[
        BELONGS_TO_SCHEMA,
        SUPPLIED_BY_SCHEMA,
        PAID_BY_SCHEMA,
        ASSIGNED_TO_SCHEMA,
        DELIVERED_TO_SCHEMA,
        BILLED_TO_SCHEMA,
        LOCATED_AT_SCHEMA,
        PERFORMED_ON_SCHEMA
    ],
    extraction_prompt="""
You are extracting entities and relationships from trucking/logistics documents.

**Entity Types to Extract:**
- Vehicle: Trucks, trailers, fleet vehicles (VEH-1234, VIN ABC123)
- PartsInvoice: Invoices for parts, repairs, services (INV-2025-001, $1,234.56)
- Vendor: Suppliers of parts, services, fuel (ACME Auto Parts, Shell)
- BankTransaction: Payments, transfers, financial records (TX-5678, $500.00)
- Driver: Employed or contracted drivers (John Smith, CDL #1234567)
- Shipment: Deliveries, loads, cargo (SH-2025-001, Chicago → Dallas)
- Location: Warehouses, terminals, customer sites (Chicago Distribution Center)
- Customer: Clients receiving services (ACME Corporation, Customer #C-1234)
- MaintenanceRecord: Maintenance/repair records (MR-2025-001, oil change)
- Route: Delivery routes or paths (Route #R-100, I-35 corridor)

**Relationship Types to Extract:**
- BELONGS_TO: Invoice → Vehicle, Driver → Customer
- SUPPLIED_BY: Invoice → Vendor
- PAID_BY: Invoice → BankTransaction
- ASSIGNED_TO: Vehicle → Driver, Shipment → Driver
- DELIVERED_TO: Shipment → Location
- BILLED_TO: Invoice → Customer
- LOCATED_AT: Vehicle → Location
- PERFORMED_ON: MaintenanceRecord → Vehicle

**Examples:**

Document: "Invoice INV-2025-10-20-001 for $1,234.56 from ACME Auto Parts for brake pads for Truck VEH-1234. Paid via ACH transfer TX-5678."

Extract:
- PartsInvoice: "INV-2025-10-20-001" (amount: $1,234.56)
- Vendor: "ACME Auto Parts"
- Vehicle: "VEH-1234" (type: Truck)
- BankTransaction: "TX-5678"

Relationships:
- INV-2025-10-20-001 BELONGS_TO VEH-1234
- INV-2025-10-20-001 SUPPLIED_BY ACME Auto Parts
- INV-2025-10-20-001 PAID_BY TX-5678

**Instructions:**
1. Extract ALL relevant entities (don't skip any)
2. Use exact entity type names (case-sensitive)
3. Create relationships to connect related entities
4. If uncertain about entity type, choose the most specific match
5. Preserve IDs, amounts, dates as attributes
""",
    validation_rules={
        "min_entities_per_document": 2,
        "min_relationships_per_document": 1,
        "required_entity_types": ["PartsInvoice", "Vehicle", "Vendor"],
        "accuracy_threshold": 0.90
    }
)


def get_domain_config() -> DomainConfig:
    """
    Get the active domain configuration.

    Returns:
        DomainConfig: The trucking/logistics domain configuration
    """
    return TRUCKING_DOMAIN_CONFIG


def validate_extraction(
    entities: List[Dict],
    relationships: List[Dict],
    config: DomainConfig
) -> Dict[str, any]:
    """
    Validate extracted entities and relationships against domain config.

    Args:
        entities: List of extracted entities
        relationships: List of extracted relationships
        config: Domain configuration

    Returns:
        Dict with validation results and errors
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "entity_count": len(entities),
        "relationship_count": len(relationships)
    }

    # Check minimum entities
    min_entities = config.validation_rules.get("min_entities_per_document", 0)
    if len(entities) < min_entities:
        results["errors"].append(
            f"Expected at least {min_entities} entities, got {len(entities)}"
        )
        results["valid"] = False

    # Check minimum relationships
    min_relationships = config.validation_rules.get("min_relationships_per_document", 0)
    if len(relationships) < min_relationships:
        results["errors"].append(
            f"Expected at least {min_relationships} relationships, got {len(relationships)}"
        )
        results["valid"] = False

    # Check entity types are valid
    valid_entity_types = {e.type.value for e in config.entities}
    for entity in entities:
        entity_type = entity.get("type")
        if entity_type not in valid_entity_types:
            results["warnings"].append(
                f"Unknown entity type: {entity_type}"
            )

    # Check relationship types are valid
    valid_relationship_types = {r.type.value for r in config.relationships}
    for relationship in relationships:
        rel_type = relationship.get("type")
        if rel_type not in valid_relationship_types:
            results["warnings"].append(
                f"Unknown relationship type: {rel_type}"
            )

    return results
```

**Action:** Create this file and verify it imports correctly.

```bash
cd apex-memory-system
python3 -c "from apex_memory.config.domain_config import get_domain_config; print('✅ Domain config module created successfully')"
```

**Expected Output:** `✅ Domain config module created successfully`

---

### Step 1.2: Create Example Configurations

**Directory:** `upgrades/active/graphiti-domain-configuration/examples/`

**File 1:** `examples/entity-types.yaml`

```yaml
# Entity Type Definitions for Trucking/Logistics Domain
# This file documents all supported entity types for Graphiti extraction

entity_types:
  - type: Vehicle
    description: A truck, trailer, or other vehicle in the fleet
    required_attributes:
      - vehicle_id
      - type
    optional_attributes:
      - make
      - model
      - year
      - vin
      - license_plate
    examples:
      - "Truck VEH-1234"
      - "2022 Freightliner Cascadia VIN ABC123"
      - "Trailer #5678"

  - type: PartsInvoice
    description: An invoice for parts, repairs, or services
    required_attributes:
      - invoice_id
      - amount
    optional_attributes:
      - date
      - vendor
      - parts_list
      - labor_cost
    examples:
      - "Invoice INV-2025-001 for $1,234.56"
      - "Parts invoice from ACME Auto Parts"

  - type: Vendor
    description: A supplier of parts, services, or fuel
    required_attributes:
      - vendor_name
    optional_attributes:
      - vendor_id
      - contact_info
      - category
    examples:
      - "ACME Auto Parts"
      - "Johnson Tire & Service"

  - type: BankTransaction
    description: A bank transaction, payment, or financial record
    required_attributes:
      - transaction_id
      - amount
    optional_attributes:
      - date
      - account
      - payee
      - category
    examples:
      - "Payment #TX-5678 for $1,234.56"
      - "ACH transfer to ACME Auto Parts"

  - type: Driver
    description: A driver employed by or contracted to the company
    required_attributes:
      - driver_name
    optional_attributes:
      - driver_id
      - cdl_number
      - contact_info
    examples:
      - "Driver John Smith"
      - "CDL holder #1234567"

  - type: Shipment
    description: A delivery, load, or shipment
    required_attributes:
      - shipment_id
    optional_attributes:
      - origin
      - destination
      - cargo
      - status
      - date
    examples:
      - "Shipment #SH-2025-001 from Chicago to Dallas"
      - "Load #45678 containing electronics"

  - type: Location
    description: A warehouse, terminal, customer site, or geographic location
    required_attributes:
      - location_name
    optional_attributes:
      - address
      - city
      - state
      - zip
      - coordinates
    examples:
      - "Chicago Distribution Center"
      - "Customer warehouse at 123 Main St, Dallas TX"

  - type: Customer
    description: A customer or client receiving services
    required_attributes:
      - customer_name
    optional_attributes:
      - customer_id
      - contact_info
      - billing_address
    examples:
      - "ACME Corporation"
      - "Customer #C-1234"

  - type: MaintenanceRecord
    description: A maintenance or repair record for a vehicle
    required_attributes:
      - record_id
      - vehicle_id
    optional_attributes:
      - date
      - type
      - description
      - cost
      - vendor
    examples:
      - "Maintenance record #MR-2025-001 for VEH-1234"
      - "Oil change on 2025-10-15"

  - type: Route
    description: A route or path for deliveries
    required_attributes:
      - route_id
    optional_attributes:
      - origin
      - destination
      - waypoints
      - distance
    examples:
      - "Route #R-100 from Chicago to Dallas"
      - "Weekly delivery route covering 5 stops"
```

**File 2:** `examples/relationship-types.yaml`

```yaml
# Relationship Type Definitions for Trucking/Logistics Domain
# This file documents all supported relationship types for Graphiti extraction

relationship_types:
  - type: BELONGS_TO
    description: Entity belongs to or is owned by another entity
    source_entity: PartsInvoice
    target_entity: Vehicle
    examples:
      - "Invoice INV-001 BELONGS_TO Vehicle VEH-1234"
      - "Driver John Smith BELONGS_TO Customer ACME Corp"

  - type: SUPPLIED_BY
    description: Invoice or parts supplied by a vendor
    source_entity: PartsInvoice
    target_entity: Vendor
    examples:
      - "Invoice INV-001 SUPPLIED_BY Vendor ACME Auto Parts"

  - type: PAID_BY
    description: Invoice paid by a bank transaction
    source_entity: PartsInvoice
    target_entity: BankTransaction
    examples:
      - "Invoice INV-001 PAID_BY Transaction TX-5678"

  - type: ASSIGNED_TO
    description: Vehicle or shipment assigned to a driver
    source_entity: Vehicle
    target_entity: Driver
    examples:
      - "Vehicle VEH-1234 ASSIGNED_TO Driver John Smith"
      - "Shipment SH-001 ASSIGNED_TO Driver Sarah Johnson"

  - type: DELIVERED_TO
    description: Shipment delivered to a location
    source_entity: Shipment
    target_entity: Location
    examples:
      - "Shipment SH-001 DELIVERED_TO Location Chicago Distribution Center"

  - type: BILLED_TO
    description: Invoice billed to a customer
    source_entity: PartsInvoice
    target_entity: Customer
    examples:
      - "Invoice INV-001 BILLED_TO Customer ACME Corporation"

  - type: LOCATED_AT
    description: Vehicle currently located at a location
    source_entity: Vehicle
    target_entity: Location
    examples:
      - "Vehicle VEH-1234 LOCATED_AT Location Dallas Terminal"

  - type: PERFORMED_ON
    description: Maintenance performed on a vehicle
    source_entity: MaintenanceRecord
    target_entity: Vehicle
    examples:
      - "MaintenanceRecord MR-001 PERFORMED_ON Vehicle VEH-1234"
```

**File 3:** `examples/extraction-prompt.txt`

```
You are extracting entities and relationships from trucking/logistics documents.

**Entity Types to Extract:**
- Vehicle: Trucks, trailers, fleet vehicles (VEH-1234, VIN ABC123)
- PartsInvoice: Invoices for parts, repairs, services (INV-2025-001, $1,234.56)
- Vendor: Suppliers of parts, services, fuel (ACME Auto Parts, Shell)
- BankTransaction: Payments, transfers, financial records (TX-5678, $500.00)
- Driver: Employed or contracted drivers (John Smith, CDL #1234567)
- Shipment: Deliveries, loads, cargo (SH-2025-001, Chicago → Dallas)
- Location: Warehouses, terminals, customer sites (Chicago Distribution Center)
- Customer: Clients receiving services (ACME Corporation, Customer #C-1234)
- MaintenanceRecord: Maintenance/repair records (MR-2025-001, oil change)
- Route: Delivery routes or paths (Route #R-100, I-35 corridor)

**Relationship Types to Extract:**
- BELONGS_TO: Invoice → Vehicle, Driver → Customer
- SUPPLIED_BY: Invoice → Vendor
- PAID_BY: Invoice → BankTransaction
- ASSIGNED_TO: Vehicle → Driver, Shipment → Driver
- DELIVERED_TO: Shipment → Location
- BILLED_TO: Invoice → Customer
- LOCATED_AT: Vehicle → Location
- PERFORMED_ON: MaintenanceRecord → Vehicle

**Examples:**

Document: "Invoice INV-2025-10-20-001 for $1,234.56 from ACME Auto Parts for brake pads for Truck VEH-1234. Paid via ACH transfer TX-5678."

Extract:
- PartsInvoice: "INV-2025-10-20-001" (amount: $1,234.56)
- Vendor: "ACME Auto Parts"
- Vehicle: "VEH-1234" (type: Truck)
- BankTransaction: "TX-5678"

Relationships:
- INV-2025-10-20-001 BELONGS_TO VEH-1234
- INV-2025-10-20-001 SUPPLIED_BY ACME Auto Parts
- INV-2025-10-20-001 PAID_BY TX-5678

**Instructions:**
1. Extract ALL relevant entities (don't skip any)
2. Use exact entity type names (case-sensitive)
3. Create relationships to connect related entities
4. If uncertain about entity type, choose the most specific match
5. Preserve IDs, amounts, dates as attributes
```

**Action:** Create these example configuration files.

```bash
cd upgrades/active/graphiti-domain-configuration
cat examples/entity-types.yaml
cat examples/relationship-types.yaml
cat examples/extraction-prompt.txt
```

**Expected:** All 3 files exist and contain configuration examples.

---

### Day 1 Completion Checklist

- [ ] `domain_config.py` module created (700+ lines)
- [ ] Module imports successfully
- [ ] 10 entity schemas defined
- [ ] 8 relationship schemas defined
- [ ] Custom extraction prompt written
- [ ] Validation function implemented
- [ ] Example YAML configurations created
- [ ] Example extraction prompt created

**Outcome:** Domain schema fully defined and documented.

---

## Day 2: Configuration Module & Integration

**Goal:** Integrate domain configuration into Graphiti extraction activity

**Estimated Time:** 6-8 hours

### Step 2.1: Update Graphiti Service

**File:** `apex-memory-system/src/apex_memory/services/graphiti_service.py`

**Current State:** Generic Graphiti extraction with no domain configuration

**Changes Required:**

1. Import domain configuration
2. Pass domain-specific extraction prompt to Graphiti
3. Validate extracted entities/relationships
4. Add feature flag support

**Implementation:**

```python
# Add imports at top of file
from apex_memory.config.domain_config import (
    get_domain_config,
    validate_extraction,
    DomainConfig
)
import os

class GraphitiService:
    def __init__(self):
        self.graphiti_client = Graphiti(
            neo4j_uri=os.getenv("NEO4J_URI"),
            neo4j_user=os.getenv("NEO4J_USER"),
            neo4j_password=os.getenv("NEO4J_PASSWORD")
        )

        # Load domain configuration if enabled
        self.domain_configured = os.getenv("ENABLE_DOMAIN_CONFIGURED_GRAPHITI", "false").lower() == "true"
        if self.domain_configured:
            self.domain_config = get_domain_config()
            logger.info("✅ Domain-configured Graphiti extraction enabled")
        else:
            self.domain_config = None
            logger.info("⚠️ Using generic Graphiti extraction (domain config disabled)")

    async def extract_entities_and_relationships(
        self,
        text: str,
        source: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Extract entities and relationships from text using Graphiti.

        If domain configuration is enabled, uses custom extraction prompt
        and validates results against domain schema.

        Args:
            text: Text to extract from
            source: Source of the text
            metadata: Optional metadata

        Returns:
            Dict with entities, relationships, and validation results
        """
        try:
            # Build extraction prompt
            if self.domain_configured and self.domain_config:
                # Use domain-specific prompt
                extraction_prompt = self.domain_config.extraction_prompt
                logger.info("Using domain-configured extraction prompt")
            else:
                # Use generic prompt
                extraction_prompt = "Extract entities and relationships from this text."
                logger.info("Using generic extraction prompt")

            # Call Graphiti extraction
            result = await self.graphiti_client.add_episode(
                name=f"{source}-{metadata.get('document_id', 'unknown')}",
                episode_body=text,
                reference_time=metadata.get('timestamp', datetime.utcnow()),
                source=source,
                source_description=metadata.get('description', ''),
                # Pass custom extraction prompt
                custom_prompt=extraction_prompt if self.domain_configured else None
            )

            # Extract entities and relationships from result
            entities = result.get("entities", [])
            relationships = result.get("edges", [])

            # Validate extraction if domain configured
            validation_results = None
            if self.domain_configured and self.domain_config:
                validation_results = validate_extraction(
                    entities,
                    relationships,
                    self.domain_config
                )

                if not validation_results["valid"]:
                    logger.warning(
                        f"⚠️ Domain validation failed: {validation_results['errors']}"
                    )
                else:
                    logger.info(
                        f"✅ Domain validation passed: "
                        f"{validation_results['entity_count']} entities, "
                        f"{validation_results['relationship_count']} relationships"
                    )

            return {
                "entities": entities,
                "relationships": relationships,
                "episode_uuid": result.get("episode_id"),
                "validation": validation_results,
                "domain_configured": self.domain_configured
            }

        except Exception as e:
            logger.error(f"❌ Graphiti extraction failed: {e}")
            raise
```

**Action:** Update `graphiti_service.py` with domain configuration support.

**Validation:**

```bash
cd apex-memory-system

# Test without domain config (default)
python3 -c "
from apex_memory.services.graphiti_service import GraphitiService
service = GraphitiService()
print(f'Domain configured: {service.domain_configured}')
print('Expected: False')
"

# Test with domain config enabled
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true python3 -c "
from apex_memory.services.graphiti_service import GraphitiService
service = GraphitiService()
print(f'Domain configured: {service.domain_configured}')
print(f'Domain config loaded: {service.domain_config is not None}')
print('Expected: True, True')
"
```

**Expected Output:**
```
Domain configured: False
Expected: False

✅ Domain-configured Graphiti extraction enabled
Domain configured: True
Domain config loaded: True
Expected: True, True
```

---

### Step 2.2: Update Extract Entities Activity

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**Function:** `extract_entities_activity` (line ~274)

**Changes:** Pass domain configuration to GraphitiService

```python
@activity.defn(name="extract_entities_activity")
async def extract_entities_activity(
    document_id: str,
    text: str,
    source: str
) -> Dict[str, Any]:
    """
    Extract entities and relationships from document text using Graphiti.

    This activity uses Graphiti's LLM-powered extraction to identify
    entities and relationships. If domain configuration is enabled,
    uses trucking/logistics-specific entity types and relationships.

    Args:
        document_id: Document UUID
        text: Parsed document text
        source: Document source

    Returns:
        Dict with entities, relationships, and Graphiti episode UUID
    """
    start_time = time.time()

    try:
        logger.info(
            f"🔍 Extracting entities for document {document_id} "
            f"(source: {source}, text length: {len(text)} chars)"
        )

        # Initialize Graphiti service (with domain config if enabled)
        graphiti_service = GraphitiService()

        # Extract entities and relationships
        result = await graphiti_service.extract_entities_and_relationships(
            text=text,
            source=source,
            metadata={"document_id": document_id}
        )

        entities = result["entities"]
        relationships = result["relationships"]
        episode_uuid = result["episode_uuid"]
        validation = result.get("validation")
        domain_configured = result.get("domain_configured", False)

        # Log extraction results
        logger.info(
            f"✅ Extracted {len(entities)} entities, {len(relationships)} relationships "
            f"for document {document_id} (episode: {episode_uuid})"
        )

        if domain_configured:
            logger.info(f"✅ Domain-configured extraction used")
            if validation:
                if validation["valid"]:
                    logger.info(f"✅ Domain validation passed")
                else:
                    logger.warning(
                        f"⚠️ Domain validation failed: {validation['errors']}"
                    )

        # Record metrics
        duration = time.time() - start_time
        metrics.record_activity_duration("extract_entities", duration)
        metrics.record_entity_extraction(len(entities), len(relationships))

        return {
            "entities": entities,
            "relationships": relationships,
            "episode_uuid": episode_uuid,
            "entity_count": len(entities),
            "relationship_count": len(relationships),
            "validation": validation,
            "domain_configured": domain_configured
        }

    except Exception as e:
        logger.error(f"❌ Entity extraction failed for document {document_id}: {e}")
        metrics.record_activity_error("extract_entities", str(e))
        raise
```

**Action:** Update `extract_entities_activity` to support domain configuration.

**Validation:**

```bash
cd apex-memory-system

# Run unit test for extract_entities_activity
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true pytest \
  tests/unit/test_extract_entities_activity.py::test_extract_entities_domain_configured \
  -v
```

**Expected:** Test passes, shows domain-configured extraction being used.

---

### Step 2.3: Add Environment Variable

**File:** `apex-memory-system/.env`

**Add:**

```bash
# Graphiti Domain Configuration
# Set to 'true' to enable domain-configured entity extraction for trucking/logistics
# Set to 'false' to use generic Graphiti extraction (default)
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false
```

**Action:** Add this to `.env.example` and `.env`

**Validation:**

```bash
cd apex-memory-system
grep "ENABLE_DOMAIN_CONFIGURED_GRAPHITI" .env
grep "ENABLE_DOMAIN_CONFIGURED_GRAPHITI" .env.example
```

**Expected:** Variable exists in both files, default is `false` (safe).

---

### Day 2 Completion Checklist

- [ ] `GraphitiService` updated with domain configuration
- [ ] `extract_entities_activity` updated
- [ ] Environment variable added (default: `false`)
- [ ] Feature flag tested (on/off)
- [ ] Validation function integrated
- [ ] Logging shows domain vs generic extraction
- [ ] No breaking changes (existing workflows still work)

**Outcome:** Domain configuration integrated but disabled by default (safe).

---

## Day 3: Validation & Testing

**Goal:** Validate domain configuration with real documents, achieve 90%+ accuracy

**Estimated Time:** 6-8 hours

### Step 3.1: Create Test Documents

**Directory:** `upgrades/active/graphiti-domain-configuration/tests/sample-documents/`

**Action:** Create 10 realistic test documents representing common scenarios.

**Test Document 1:** `invoice-brake-parts.txt`

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

**Test Document 2:** `shipment-delivery-record.txt`

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

**Additional 8 test documents** should cover:

3. Maintenance record with vendor information
4. Bank statement with multiple transactions
5. GPS tracking report with location data
6. Fuel purchase invoice
7. Driver assignment document
8. Route planning document
9. Multi-vehicle maintenance schedule
10. Customer contract document

**Action:** Create all 10 test documents in `tests/sample-documents/`

---

### Step 3.2: Define Expected Outputs

**Directory:** `upgrades/active/graphiti-domain-configuration/tests/expected-outputs/`

**File:** `expected-outputs/invoice-brake-parts.json`

```json
{
  "document": "invoice-brake-parts.txt",
  "expected_entities": [
    {
      "type": "PartsInvoice",
      "name": "INV-2025-10-20-001",
      "attributes": {
        "date": "2025-10-20",
        "amount": 820.00,
        "vendor": "ACME Auto Parts"
      }
    },
    {
      "type": "Vehicle",
      "name": "VEH-1234",
      "attributes": {
        "type": "Truck",
        "make": "Freightliner",
        "model": "Cascadia",
        "year": 2022
      }
    },
    {
      "type": "Vendor",
      "name": "ACME Auto Parts",
      "attributes": {}
    },
    {
      "type": "BankTransaction",
      "name": "TX-2025-5678",
      "attributes": {
        "amount": 820.00,
        "date": "2025-10-21",
        "type": "ACH Transfer"
      }
    },
    {
      "type": "Customer",
      "name": "ACME Trucking LLC",
      "attributes": {
        "address": "123 Fleet Street, Chicago, IL 60601"
      }
    }
  ],
  "expected_relationships": [
    {
      "type": "BELONGS_TO",
      "source": "INV-2025-10-20-001",
      "target": "VEH-1234"
    },
    {
      "type": "SUPPLIED_BY",
      "source": "INV-2025-10-20-001",
      "target": "ACME Auto Parts"
    },
    {
      "type": "PAID_BY",
      "source": "INV-2025-10-20-001",
      "target": "TX-2025-5678"
    },
    {
      "type": "BILLED_TO",
      "source": "INV-2025-10-20-001",
      "target": "ACME Trucking LLC"
    }
  ],
  "validation_criteria": {
    "min_entities": 5,
    "min_relationships": 4,
    "required_entity_types": ["PartsInvoice", "Vehicle", "Vendor", "BankTransaction"],
    "accuracy_threshold": 0.90
  }
}
```

**File:** `expected-outputs/shipment-delivery-record.json`

```json
{
  "document": "shipment-delivery-record.txt",
  "expected_entities": [
    {
      "type": "Shipment",
      "name": "SH-2025-10-19-001",
      "attributes": {
        "origin": "Chicago Distribution Center",
        "destination": "Dallas Customer Warehouse",
        "cargo": "15 pallets of electronics",
        "weight": "12,500 lbs",
        "status": "DELIVERED"
      }
    },
    {
      "type": "Driver",
      "name": "John Smith",
      "attributes": {
        "cdl_number": "IL-1234567"
      }
    },
    {
      "type": "Vehicle",
      "name": "VEH-5678",
      "attributes": {
        "type": "Truck",
        "make": "Kenworth",
        "model": "T680",
        "year": 2023
      }
    },
    {
      "type": "Location",
      "name": "Chicago Distribution Center",
      "attributes": {
        "address": "123 Warehouse Rd, Chicago, IL"
      }
    },
    {
      "type": "Location",
      "name": "Dallas Customer Warehouse",
      "attributes": {
        "address": "456 Commerce St, Dallas, TX"
      }
    },
    {
      "type": "Customer",
      "name": "Johnson Manufacturing LLC",
      "attributes": {
        "customer_id": "C-5678"
      }
    },
    {
      "type": "Route",
      "name": "R-100",
      "attributes": {
        "description": "Interstate I-35 corridor",
        "distance": "950 miles"
      }
    },
    {
      "type": "PartsInvoice",
      "name": "INV-2025-10-20-100",
      "attributes": {
        "amount": 2450.00
      }
    }
  ],
  "expected_relationships": [
    {
      "type": "ASSIGNED_TO",
      "source": "SH-2025-10-19-001",
      "target": "John Smith"
    },
    {
      "type": "ASSIGNED_TO",
      "source": "VEH-5678",
      "target": "John Smith"
    },
    {
      "type": "DELIVERED_TO",
      "source": "SH-2025-10-19-001",
      "target": "Dallas Customer Warehouse"
    },
    {
      "type": "BILLED_TO",
      "source": "INV-2025-10-20-100",
      "target": "Johnson Manufacturing LLC"
    },
    {
      "type": "FOLLOWS_ROUTE",
      "source": "SH-2025-10-19-001",
      "target": "R-100"
    }
  ],
  "validation_criteria": {
    "min_entities": 8,
    "min_relationships": 5,
    "required_entity_types": ["Shipment", "Driver", "Vehicle", "Location", "Customer"],
    "accuracy_threshold": 0.90
  }
}
```

**Action:** Create expected output files for all 10 test documents.

---

### Step 3.3: Create Validation Script

**File:** `upgrades/active/graphiti-domain-configuration/tests/validate_extraction.py`

```python
"""
Validation script for domain-configured Graphiti extraction.

This script:
1. Reads sample documents
2. Extracts entities/relationships using domain-configured Graphiti
3. Compares actual vs expected results
4. Calculates accuracy metrics
5. Reports pass/fail for each test

Usage:
    ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true python tests/validate_extraction.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "apex-memory-system" / "src"))

from apex_memory.services.graphiti_service import GraphitiService
from apex_memory.config.domain_config import get_domain_config


def load_test_document(filename: str) -> str:
    """Load a test document from sample-documents/"""
    doc_path = Path(__file__).parent / "sample-documents" / filename
    return doc_path.read_text()


def load_expected_output(filename: str) -> Dict:
    """Load expected output from expected-outputs/"""
    output_path = Path(__file__).parent / "expected-outputs" / filename.replace(".txt", ".json")
    return json.loads(output_path.read_text())


def calculate_entity_accuracy(actual: List[Dict], expected: List[Dict]) -> float:
    """
    Calculate entity extraction accuracy.

    Accuracy = (correctly extracted entities) / (total expected entities)
    """
    if not expected:
        return 1.0

    correct = 0
    for exp_entity in expected:
        # Check if entity exists in actual with correct type
        for act_entity in actual:
            if (act_entity.get("type") == exp_entity.get("type") and
                act_entity.get("name") == exp_entity.get("name")):
                correct += 1
                break

    return correct / len(expected)


def calculate_relationship_accuracy(actual: List[Dict], expected: List[Dict]) -> float:
    """
    Calculate relationship extraction accuracy.

    Accuracy = (correctly extracted relationships) / (total expected relationships)
    """
    if not expected:
        return 1.0

    correct = 0
    for exp_rel in expected:
        # Check if relationship exists in actual
        for act_rel in actual:
            if (act_rel.get("type") == exp_rel.get("type") and
                act_rel.get("source") == exp_rel.get("source") and
                act_rel.get("target") == exp_rel.get("target")):
                correct += 1
                break

    return correct / len(expected)


async def validate_single_document(
    doc_filename: str,
    graphiti_service: GraphitiService
) -> Dict[str, Any]:
    """Validate extraction for a single document."""
    print(f"\n{'='*80}")
    print(f"Testing: {doc_filename}")
    print(f"{'='*80}")

    # Load document and expected output
    text = load_test_document(doc_filename)
    expected = load_expected_output(doc_filename)

    print(f"📄 Document length: {len(text)} characters")
    print(f"📊 Expected entities: {len(expected['expected_entities'])}")
    print(f"📊 Expected relationships: {len(expected['expected_relationships'])}")

    # Extract entities using domain-configured Graphiti
    result = await graphiti_service.extract_entities_and_relationships(
        text=text,
        source="validation_test",
        metadata={"document": doc_filename}
    )

    actual_entities = result["entities"]
    actual_relationships = result["relationships"]

    print(f"✅ Extracted entities: {len(actual_entities)}")
    print(f"✅ Extracted relationships: {len(actual_relationships)}")

    # Calculate accuracy
    entity_accuracy = calculate_entity_accuracy(
        actual_entities,
        expected["expected_entities"]
    )
    relationship_accuracy = calculate_relationship_accuracy(
        actual_relationships,
        expected["expected_relationships"]
    )
    overall_accuracy = (entity_accuracy + relationship_accuracy) / 2

    print(f"\n📈 Accuracy Metrics:")
    print(f"   Entity accuracy: {entity_accuracy:.1%}")
    print(f"   Relationship accuracy: {relationship_accuracy:.1%}")
    print(f"   Overall accuracy: {overall_accuracy:.1%}")

    # Check validation criteria
    criteria = expected.get("validation_criteria", {})
    threshold = criteria.get("accuracy_threshold", 0.90)

    passed = overall_accuracy >= threshold

    if passed:
        print(f"\n✅ PASS: Accuracy {overall_accuracy:.1%} >= {threshold:.1%}")
    else:
        print(f"\n❌ FAIL: Accuracy {overall_accuracy:.1%} < {threshold:.1%}")

    return {
        "document": doc_filename,
        "passed": passed,
        "entity_accuracy": entity_accuracy,
        "relationship_accuracy": relationship_accuracy,
        "overall_accuracy": overall_accuracy,
        "threshold": threshold
    }


async def run_validation():
    """Run validation for all test documents."""
    print("\n" + "="*80)
    print("GRAPHITI DOMAIN CONFIGURATION VALIDATION")
    print("="*80)

    # Check environment variable
    if os.getenv("ENABLE_DOMAIN_CONFIGURED_GRAPHITI", "false").lower() != "true":
        print("\n❌ ERROR: ENABLE_DOMAIN_CONFIGURED_GRAPHITI must be set to 'true'")
        print("   Run: ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true python tests/validate_extraction.py")
        sys.exit(1)

    # Initialize Graphiti service
    print("\n🚀 Initializing domain-configured Graphiti service...")
    graphiti_service = GraphitiService()

    if not graphiti_service.domain_configured:
        print("\n❌ ERROR: Domain configuration not loaded")
        sys.exit(1)

    print("✅ Domain configuration loaded successfully")

    # Get all test documents
    sample_dir = Path(__file__).parent / "sample-documents"
    test_documents = [f.name for f in sample_dir.glob("*.txt")]

    print(f"\n📋 Found {len(test_documents)} test documents")

    # Run validation for each document
    results = []
    for doc in sorted(test_documents):
        try:
            result = await validate_single_document(doc, graphiti_service)
            results.append(result)
        except Exception as e:
            print(f"\n❌ ERROR validating {doc}: {e}")
            results.append({
                "document": doc,
                "passed": False,
                "error": str(e)
            })

    # Print summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)

    total = len(results)
    passed = sum(1 for r in results if r.get("passed", False))
    failed = total - passed

    print(f"\n📊 Total tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if results:
        avg_accuracy = sum(r.get("overall_accuracy", 0) for r in results) / total
        print(f"📈 Average accuracy: {avg_accuracy:.1%}")

    print("\n" + "="*80)

    # Exit with appropriate code
    if failed == 0:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_validation())
```

**Action:** Create validation script.

**Run Validation:**

```bash
cd upgrades/active/graphiti-domain-configuration

# Enable domain configuration
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true

# Run validation
python tests/validate_extraction.py
```

**Expected Output:**

```
================================================================================
GRAPHITI DOMAIN CONFIGURATION VALIDATION
================================================================================

🚀 Initializing domain-configured Graphiti service...
✅ Domain configuration loaded successfully

📋 Found 10 test documents

================================================================================
Testing: invoice-brake-parts.txt
================================================================================
📄 Document length: 456 characters
📊 Expected entities: 5
📊 Expected relationships: 4
✅ Extracted entities: 5
✅ Extracted relationships: 4

📈 Accuracy Metrics:
   Entity accuracy: 100.0%
   Relationship accuracy: 100.0%
   Overall accuracy: 100.0%

✅ PASS: Accuracy 100.0% >= 90.0%

[... 8 more documents ...]

================================================================================
VALIDATION SUMMARY
================================================================================

📊 Total tests: 10
✅ Passed: 9
❌ Failed: 1
📈 Average accuracy: 92.5%

================================================================================
✅ ALL TESTS PASSED (if average >= 90%)
```

---

### Step 3.4: Neo4j Validation Queries

**Directory:** `upgrades/active/graphiti-domain-configuration/tests/validation-queries/`

**File:** `validation-queries/check-entity-types.cypher`

```cypher
// Check that domain-configured entity types exist in Neo4j

// Count entities by type
MATCH (n)
WHERE n.type IN [
  'Vehicle', 'PartsInvoice', 'Vendor', 'BankTransaction',
  'Driver', 'Shipment', 'Location', 'Customer',
  'MaintenanceRecord', 'Route'
]
RETURN n.type AS entity_type, COUNT(n) AS count
ORDER BY count DESC;
```

**File:** `validation-queries/check-relationships.cypher`

```cypher
// Check that domain-configured relationship types exist in Neo4j

// Count relationships by type
MATCH ()-[r]->()
WHERE type(r) IN [
  'BELONGS_TO', 'SUPPLIED_BY', 'PAID_BY', 'ASSIGNED_TO',
  'DELIVERED_TO', 'BILLED_TO', 'LOCATED_AT', 'PERFORMED_ON'
]
RETURN type(r) AS relationship_type, COUNT(r) AS count
ORDER BY count DESC;
```

**File:** `validation-queries/invoice-to-vehicle-path.cypher`

```cypher
// Verify invoice → vehicle → driver → location path exists

MATCH path = (invoice:PartsInvoice)-[:BELONGS_TO]->(vehicle:Vehicle)
            -[:ASSIGNED_TO]->(driver:Driver)
            -[:LOCATED_AT]->(location:Location)
RETURN invoice.name, vehicle.name, driver.name, location.name
LIMIT 5;
```

**Action:** Create Neo4j validation queries.

**Run Queries:**

```bash
# Connect to Neo4j
docker exec -it apex-neo4j cypher-shell -u neo4j -p apexmemory2024

# Run validation queries
:source /path/to/validation-queries/check-entity-types.cypher
```

**Expected:** Entity types and relationships from domain config appear in results.

---

### Day 3 Completion Checklist

- [ ] 10 test documents created
- [ ] 10 expected output files created
- [ ] Validation script created and runs
- [ ] 90%+ average accuracy achieved
- [ ] Neo4j queries validate domain entities exist
- [ ] Neo4j queries validate domain relationships exist
- [ ] Feature flag tested (on/off)
- [ ] No breaking changes to existing workflows

**Outcome:** Domain configuration validated, achieving 90%+ extraction accuracy.

---

## Validation Criteria

### Success Metrics

**Must Have (Blocking):**

1. ✅ **90%+ Extraction Accuracy**
   - Entity extraction accuracy >= 90%
   - Relationship extraction accuracy >= 90%
   - Measured across 10 test documents

2. ✅ **All 10 Entity Types Recognized**
   - Vehicle, PartsInvoice, Vendor, BankTransaction
   - Driver, Shipment, Location, Customer
   - MaintenanceRecord, Route

3. ✅ **All 8 Relationship Types Created**
   - BELONGS_TO, SUPPLIED_BY, PAID_BY, ASSIGNED_TO
   - DELIVERED_TO, BILLED_TO, LOCATED_AT, PERFORMED_ON

4. ✅ **Feature Flag Works**
   - `ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false` → generic extraction (existing behavior)
   - `ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true` → domain extraction (new behavior)

5. ✅ **Zero Breaking Changes**
   - All existing 162 tests still pass
   - Existing workflows unaffected when feature flag disabled

**Nice to Have (Non-Blocking):**

- Entity attribute extraction (e.g., invoice amount, vehicle VIN)
- Temporal reasoning (e.g., "occurred before/after")
- Multi-hop relationships (e.g., invoice → vehicle → driver → location)

### Acceptance Tests

**Test 1: Generic Extraction Still Works**

```bash
# Disable domain config
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false

# Run existing tests
cd apex-memory-system
pytest tests/integration/test_temporal_ingestion_workflow.py -v

# Expected: All tests pass (no regression)
```

**Test 2: Domain Extraction Works**

```bash
# Enable domain config
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true

# Run validation script
cd upgrades/active/graphiti-domain-configuration
python tests/validate_extraction.py

# Expected: 90%+ average accuracy, 9+ tests pass
```

**Test 3: Neo4j Contains Domain Entities**

```bash
# Query Neo4j for domain entity types
docker exec -it apex-neo4j cypher-shell -u neo4j -p apexmemory2024 \
  "MATCH (n) WHERE n.type IN ['Vehicle', 'PartsInvoice', 'Vendor'] RETURN COUNT(n);"

# Expected: > 0 (entities exist)
```

**Test 4: Existing Baseline Preserved**

```bash
# Run Enhanced Saga baseline tests
cd apex-memory-system
pytest tests/ --ignore=tests/load/ -v

# Expected: 162 tests pass (Enhanced Saga baseline preserved)
```

---

## Rollback Plan

### If Implementation Fails

**Step 1: Disable Feature Flag**

```bash
# Set feature flag to false in .env
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false

# Or edit apex-memory-system/.env
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false
```

**Result:** System reverts to generic extraction (existing behavior).

**Step 2: Verify Rollback**

```bash
cd apex-memory-system
pytest tests/integration/test_temporal_ingestion_workflow.py -v
```

**Expected:** All tests pass (no impact from domain config).

---

### If Accuracy Below 90%

**Option 1: Refine Extraction Prompt**

- Edit `domain_config.py` → `extraction_prompt`
- Add more examples for problematic entity types
- Re-run validation script

**Option 2: Adjust Entity/Relationship Schemas**

- Review failed test cases
- Identify missing or incorrect entity types
- Update schemas in `domain_config.py`
- Re-run validation

**Option 3: Defer Domain Configuration**

- Document findings in `TROUBLESHOOTING.md`
- Mark Phase 3 as PARTIAL (code complete, domain config incomplete)
- Deploy without domain configuration (generic extraction)
- Iterate post-deployment

---

## Implementation Notes

### Best Practices

1. **Always Test with Feature Flag Off First**
   - Ensure existing behavior preserved
   - Run full test suite before enabling domain config

2. **Validate Incrementally**
   - Test 1-2 documents at a time
   - Don't wait until all 10 are complete
   - Catch issues early

3. **Document Failures**
   - If accuracy below 90%, document which entities/relationships failed
   - Update `TROUBLESHOOTING.md` with findings
   - Create GitHub issues for tracking

4. **Monitor Production**
   - After deployment, monitor Grafana dashboard for entity extraction metrics
   - Check Neo4j for unexpected entity types
   - Validate relationship counts match expectations

### Common Issues

See `TROUBLESHOOTING.md` for complete list of common issues and solutions.

---

## Deployment Checklist

**Before Deployment:**

- [ ] All 3 days of implementation complete
- [ ] 90%+ extraction accuracy achieved
- [ ] Feature flag tested (on/off)
- [ ] Existing 162 tests still pass
- [ ] Domain config documented
- [ ] Rollback plan tested

**After Deployment:**

- [ ] Enable domain config in production (`.env` file)
- [ ] Monitor Grafana metrics for entity extraction
- [ ] Query Neo4j to verify domain entities exist
- [ ] Review first 100 documents for extraction quality
- [ ] Document any issues in GitHub

---

## Summary

**Timeline:** 2-3 days
**Outcome:** Domain-configured Graphiti extraction with 90%+ accuracy
**Impact:** Accurate entity types, semantic relationships, better knowledge graph quality
**Risk:** Low (feature flag allows safe rollback)

**This implementation enables Phase 3 verification to be marked FULLY IMPLEMENTED.**

---

**Next Steps:** After completion, proceed to `TESTING.md` for comprehensive test specifications.
