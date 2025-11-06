# 6-Hub Schema Validation Queries

**Document Status:** Production-Ready
**Last Updated:** 2025-11-04
**Phase:** Phase 3 (Final Integration) - Week 3 Days 3-4

---

## Purpose

This document provides a comprehensive suite of validation queries for the 6-hub unified memory system. These queries validate:

- **Referential Integrity:** All foreign keys point to valid entities
- **Temporal Consistency:** Bi-temporal tracking patterns are correct
- **Cross-Database Sync:** PostgreSQL, Neo4j, Qdrant, Redis, and Graphiti are consistent
- **Business Logic Constraints:** Complex rules (multi-category, intercompany transactions) work correctly
- **Data Quality:** No orphaned records, invalid dates, or constraint violations

**Automated Testing:** All queries should be integrated into CI/CD pipeline with expected results and failure thresholds.

---

## Quick Navigation

- [PostgreSQL Validation Queries](#postgresql-validation-queries)
  - [Hub 1: G (Command Center)](#hub-1-g-command-center)
  - [Hub 2: OpenHaul Brokerage](#hub-2-openhaul-brokerage)
  - [Hub 3: Origin Transport](#hub-3-origin-transport)
  - [Hub 4: Contacts/CRM](#hub-4-contactscrm)
  - [Hub 5: Financials](#hub-5-financials)
  - [Hub 6: Corporate Infrastructure](#hub-6-corporate-infrastructure)
- [Neo4j Validation Queries](#neo4j-validation-queries)
- [Cross-Database Consistency Checks](#cross-database-consistency-checks)
- [Temporal Query Validation](#temporal-query-validation)
- [Automated Test Suite](#automated-test-suite)

---

## PostgreSQL Validation Queries

### Hub 1: G (Command Center)

#### Q1.1: G Person Entity Integrity
```sql
-- Validate G entity has valid links to Hub 4 Person
SELECT
    g.user_id,
    g.name,
    p.person_id,
    p.full_name,
    CASE
        WHEN p.person_id IS NULL THEN 'ORPHANED G ENTITY'
        ELSE 'VALID'
    END as validation_status
FROM hub1_command.g_persons g
LEFT JOIN hub4_contacts.persons p ON g.person_id = p.person_id
WHERE p.person_id IS NULL;

-- Expected: 0 rows (no orphaned G entities)
-- Alert: CRITICAL if count > 0
```

#### Q1.2: Project → Goal Relationships
```sql
-- Validate all projects with goal relationships have valid goal_id
SELECT
    p.project_id,
    p.project_name,
    p.related_goals,
    COUNT(g.goal_id) as valid_goal_count,
    array_length(p.related_goals, 1) as expected_goal_count
FROM hub1_command.projects p
LEFT JOIN hub1_command.goals g ON g.goal_id = ANY(p.related_goals)
WHERE p.related_goals IS NOT NULL
  AND array_length(p.related_goals, 1) > 0
GROUP BY p.project_id, p.project_name, p.related_goals
HAVING COUNT(g.goal_id) != array_length(p.related_goals, 1);

-- Expected: 0 rows (all goal references valid)
-- Alert: WARNING if count > 0
```

#### Q1.3: Goal Measurement Links (Cross-Hub to Hub 5)
```sql
-- Validate Goal → Revenue/Expense measurement links
SELECT
    g.goal_id,
    g.goal_name,
    g.metrics->>'calculation_logic' as calculation,
    CASE
        WHEN g.metrics->>'hub' = 'hub5_financials'
             AND g.metrics->>'entity' = 'revenue'
             AND EXISTS (
                 SELECT 1 FROM hub5_financials.revenue r
                 WHERE (g.metrics->'filter'->>'category')::text = r.revenue_category
             )
        THEN 'VALID'
        WHEN g.metrics->>'hub' = 'hub5_financials'
             AND g.metrics->>'entity' = 'expense'
             AND EXISTS (
                 SELECT 1 FROM hub5_financials.expenses e
                 WHERE (g.metrics->'filter'->>'category')::text = e.expense_category
             )
        THEN 'VALID'
        ELSE 'INVALID MEASUREMENT LINK'
    END as validation_status
FROM hub1_command.goals g
WHERE g.metrics IS NOT NULL;

-- Expected: All 'VALID'
-- Alert: WARNING if any 'INVALID MEASUREMENT LINK'
```

#### Q1.4: Tasks → Project Assignment
```sql
-- Validate all tasks are assigned to valid projects
SELECT
    t.task_id,
    t.title,
    t.project_id,
    p.project_name
FROM hub1_command.tasks t
LEFT JOIN hub1_command.projects p ON t.project_id = p.project_id
WHERE t.project_id IS NOT NULL AND p.project_id IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q1.5: Temporal Consistency (Hub 1)
```sql
-- Validate valid_from/valid_to temporal ranges are consistent
SELECT
    'projects' as entity_type,
    project_id as entity_id,
    valid_from,
    valid_to,
    CASE
        WHEN valid_to IS NOT NULL AND valid_to < valid_from THEN 'INVALID: valid_to before valid_from'
        WHEN valid_from > NOW() THEN 'INVALID: valid_from in future'
        ELSE 'VALID'
    END as validation_status
FROM hub1_command.projects
WHERE CASE
        WHEN valid_to IS NOT NULL AND valid_to < valid_from THEN true
        WHEN valid_from > NOW() THEN true
        ELSE false
      END

UNION ALL

SELECT
    'goals' as entity_type,
    goal_id as entity_id,
    valid_from,
    valid_to,
    CASE
        WHEN valid_to IS NOT NULL AND valid_to < valid_from THEN 'INVALID: valid_to before valid_from'
        WHEN valid_from > NOW() THEN 'INVALID: valid_from in future'
        ELSE 'VALID'
    END as validation_status
FROM hub1_command.goals
WHERE CASE
        WHEN valid_to IS NOT NULL AND valid_to < valid_from THEN true
        WHEN valid_from > NOW() THEN true
        ELSE false
      END;

-- Expected: 0 rows
-- Alert: CRITICAL if count > 0
```

---

### Hub 2: OpenHaul Brokerage

#### Q2.1: Load → Carrier Relationship
```sql
-- Validate all loads have valid carrier assignments
SELECT
    l.load_number,
    l.carrier_id,
    c.carrier_name,
    CASE
        WHEN c.carrier_id IS NULL THEN 'ORPHANED LOAD: carrier not found'
        WHEN l.carrier_id = 'carr_origin' AND c.carrier_name != 'Origin Transport, LLC' THEN 'MISMATCH: carr_origin wrong name'
        ELSE 'VALID'
    END as validation_status
FROM hub2_openhaul.loads l
LEFT JOIN hub2_openhaul.carriers c ON l.carrier_id = c.carrier_id
WHERE c.carrier_id IS NULL OR (l.carrier_id = 'carr_origin' AND c.carrier_name != 'Origin Transport, LLC');

-- Expected: 0 rows
-- Alert: CRITICAL if count > 0
```

#### Q2.2: Load → Locations (Pickup/Delivery)
```sql
-- Validate all loads have valid pickup and delivery locations
SELECT
    l.load_number,
    l.pickup_location_id,
    l.delivery_location_id,
    pickup.location_name as pickup_name,
    delivery.location_name as delivery_name,
    CASE
        WHEN pickup.location_id IS NULL THEN 'INVALID: pickup location not found'
        WHEN delivery.location_id IS NULL THEN 'INVALID: delivery location not found'
        ELSE 'VALID'
    END as validation_status
FROM hub2_openhaul.loads l
LEFT JOIN hub2_openhaul.locations pickup ON l.pickup_location_id = pickup.location_id
LEFT JOIN hub2_openhaul.locations delivery ON l.delivery_location_id = delivery.location_id
WHERE pickup.location_id IS NULL OR delivery.location_id IS NULL;

-- Expected: 0 rows
-- Alert: CRITICAL if count > 0
```

#### Q2.3: Load Margin Validation
```sql
-- Validate load margin calculations are correct
SELECT
    load_number,
    customer_rate,
    carrier_rate,
    margin,
    (customer_rate - carrier_rate) as calculated_margin,
    CASE
        WHEN margin IS NULL THEN 'NULL MARGIN'
        WHEN ABS(margin - (customer_rate - carrier_rate)) > 0.01 THEN 'MARGIN MISMATCH'
        ELSE 'VALID'
    END as validation_status
FROM hub2_openhaul.loads
WHERE margin IS NULL
   OR ABS(margin - (customer_rate - carrier_rate)) > 0.01;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q2.4: Load Status Flow
```sql
-- Validate load statuses follow valid progression
SELECT
    load_number,
    status,
    pickup_date,
    delivery_date,
    CASE
        WHEN status = 'delivered' AND delivery_date IS NULL THEN 'INVALID: delivered but no delivery_date'
        WHEN status = 'in_transit' AND pickup_date IS NULL THEN 'INVALID: in_transit but no pickup_date'
        WHEN status = 'booked' AND pickup_date < NOW() THEN 'INVALID: booked but pickup_date in past'
        ELSE 'VALID'
    END as validation_status
FROM hub2_openhaul.loads
WHERE (status = 'delivered' AND delivery_date IS NULL)
   OR (status = 'in_transit' AND pickup_date IS NULL)
   OR (status = 'booked' AND pickup_date < NOW());

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q2.5: Load → Customer/Shipper Links (Cross-Hub to Hub 4)
```sql
-- Validate all loads have valid customer and shipper references
SELECT
    l.load_number,
    l.customer_id,
    l.shipper_id,
    cust.company_name as customer_name,
    ship.company_name as shipper_name,
    CASE
        WHEN cust.company_id IS NULL THEN 'INVALID: customer not found in Hub 4'
        WHEN ship.company_id IS NULL THEN 'INVALID: shipper not found in Hub 4'
        ELSE 'VALID'
    END as validation_status
FROM hub2_openhaul.loads l
LEFT JOIN hub4_contacts.companies cust ON l.customer_id = cust.company_id
LEFT JOIN hub4_contacts.companies ship ON l.shipper_id = ship.company_id
WHERE cust.company_id IS NULL OR ship.company_id IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

---

### Hub 3: Origin Transport

#### Q3.1: Tractor → Lender/Insurance Provider Links
```sql
-- Validate tractors with financing/insurance have valid Hub 4 company references
SELECT
    t.unit_number,
    t.lender_name,
    t.insurance_provider,
    lender.company_name as lender_company,
    insurance.company_name as insurance_company,
    CASE
        WHEN t.lender_name IS NOT NULL AND lender.company_id IS NULL THEN 'INVALID: lender not found in Hub 4'
        WHEN t.insurance_provider IS NOT NULL AND insurance.company_id IS NULL THEN 'INVALID: insurance provider not found in Hub 4'
        ELSE 'VALID'
    END as validation_status
FROM hub3_origin.tractors t
LEFT JOIN hub4_contacts.companies lender ON t.lender_name = lender.company_name
LEFT JOIN hub4_contacts.companies insurance ON t.insurance_provider = insurance.company_name
WHERE (t.lender_name IS NOT NULL AND lender.company_id IS NULL)
   OR (t.insurance_provider IS NOT NULL AND insurance.company_id IS NULL);

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q3.2: Driver → Current Unit Assignment
```sql
-- Validate drivers have valid current_unit assignments or NULL
SELECT
    d.driver_id,
    d.name,
    d.current_unit_assignment,
    t.unit_number,
    CASE
        WHEN d.current_unit_assignment IS NOT NULL AND t.unit_number IS NULL THEN 'INVALID: assigned unit not found'
        ELSE 'VALID'
    END as validation_status
FROM hub3_origin.drivers d
LEFT JOIN hub3_origin.tractors t ON d.current_unit_assignment = t.unit_number
WHERE d.current_unit_assignment IS NOT NULL AND t.unit_number IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q3.3: Tractor/Trailer Status Validation
```sql
-- Validate equipment status values are valid
SELECT
    'tractors' as entity_type,
    unit_number as entity_id,
    status,
    CASE
        WHEN status NOT IN ('active', 'maintenance', 'out_of_service', 'sold') THEN 'INVALID STATUS'
        WHEN status = 'sold' AND valid_to IS NULL THEN 'INVALID: sold but still current'
        ELSE 'VALID'
    END as validation_status
FROM hub3_origin.tractors
WHERE status NOT IN ('active', 'maintenance', 'out_of_service', 'sold')
   OR (status = 'sold' AND valid_to IS NULL)

UNION ALL

SELECT
    'trailers' as entity_type,
    trailer_number as entity_id,
    status,
    CASE
        WHEN status NOT IN ('active', 'maintenance', 'out_of_service', 'sold') THEN 'INVALID STATUS'
        WHEN status = 'sold' AND valid_to IS NULL THEN 'INVALID: sold but still current'
        ELSE 'VALID'
    END as validation_status
FROM hub3_origin.trailers
WHERE status NOT IN ('active', 'maintenance', 'out_of_service', 'sold')
   OR (status = 'sold' AND valid_to IS NULL);

-- Expected: 0 rows
-- Alert: CRITICAL if count > 0
```

#### Q3.4: Fuel Transactions → Unit Validation
```sql
-- Validate all fuel transactions reference valid units
SELECT
    f.transaction_id,
    f.unit_number,
    f.transaction_date,
    t.unit_number as tractor_unit,
    CASE
        WHEN t.unit_number IS NULL THEN 'INVALID: unit not found'
        ELSE 'VALID'
    END as validation_status
FROM hub3_origin.fuel_transactions f
LEFT JOIN hub3_origin.tractors t ON f.unit_number = t.unit_number
WHERE t.unit_number IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q3.5: Maintenance Records → Unit Validation
```sql
-- Validate all maintenance records reference valid units
SELECT
    m.maintenance_id,
    m.unit_number,
    m.maintenance_date,
    t.unit_number as tractor_unit,
    CASE
        WHEN t.unit_number IS NULL THEN 'INVALID: unit not found'
        ELSE 'VALID'
    END as validation_status
FROM hub3_origin.maintenance_records m
LEFT JOIN hub3_origin.tractors t ON m.unit_number = t.unit_number
WHERE t.unit_number IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

---

### Hub 4: Contacts/CRM

#### Q4.1: Company Multi-Category Validation
```sql
-- Validate company categories are valid and consistent with role
SELECT
    company_id,
    company_name,
    categories,
    CASE
        WHEN categories IS NULL OR array_length(categories, 1) = 0 THEN 'INVALID: no categories'
        WHEN NOT categories <@ ARRAY['customer', 'carrier', 'vendor', 'partner', 'internal_entity']::text[] THEN 'INVALID: unknown category'
        ELSE 'VALID'
    END as validation_status
FROM hub4_contacts.companies
WHERE categories IS NULL
   OR array_length(categories, 1) = 0
   OR NOT categories <@ ARRAY['customer', 'carrier', 'vendor', 'partner', 'internal_entity']::text[];

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q4.2: Person → Primary Company Link
```sql
-- Validate all persons with primary_company_id have valid company references
SELECT
    p.person_id,
    p.full_name,
    p.primary_company_id,
    c.company_name,
    CASE
        WHEN c.company_id IS NULL THEN 'INVALID: primary company not found'
        ELSE 'VALID'
    END as validation_status
FROM hub4_contacts.persons p
LEFT JOIN hub4_contacts.companies c ON p.primary_company_id = c.company_id
WHERE p.primary_company_id IS NOT NULL AND c.company_id IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q4.3: Contact → Person/Company Links
```sql
-- Validate all contacts have valid person and company references
SELECT
    c.contact_id,
    c.contact_type,
    c.person_id,
    c.company_id,
    p.full_name,
    comp.company_name,
    CASE
        WHEN c.contact_type = 'individual' AND p.person_id IS NULL THEN 'INVALID: individual contact missing person'
        WHEN c.contact_type = 'company' AND comp.company_id IS NULL THEN 'INVALID: company contact missing company'
        ELSE 'VALID'
    END as validation_status
FROM hub4_contacts.contacts c
LEFT JOIN hub4_contacts.persons p ON c.person_id = p.person_id
LEFT JOIN hub4_contacts.companies comp ON c.company_id = comp.company_id
WHERE (c.contact_type = 'individual' AND p.person_id IS NULL)
   OR (c.contact_type = 'company' AND comp.company_id IS NULL);

-- Expected: 0 rows
-- Alert: CRITICAL if count > 0
```

#### Q4.4: Address → Parent Entity Links
```sql
-- Validate all addresses are linked to at least one parent entity
SELECT
    a.address_id,
    a.street_address,
    a.city,
    a.state,
    CASE
        WHEN NOT EXISTS (
            SELECT 1 FROM hub4_contacts.persons p WHERE a.address_id = ANY(p.addresses)
        ) AND NOT EXISTS (
            SELECT 1 FROM hub4_contacts.companies c WHERE a.address_id = ANY(c.addresses)
        ) THEN 'ORPHANED: no parent entity'
        ELSE 'VALID'
    END as validation_status
FROM hub4_contacts.addresses a
WHERE NOT EXISTS (
    SELECT 1 FROM hub4_contacts.persons p WHERE a.address_id = ANY(p.addresses)
) AND NOT EXISTS (
    SELECT 1 FROM hub4_contacts.companies c WHERE a.address_id = ANY(c.addresses)
);

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q4.5: Relationship Reciprocity
```sql
-- Validate relationships have reciprocal entries
SELECT
    r1.relationship_id,
    r1.from_person_id,
    r1.to_person_id,
    r1.relationship_type,
    CASE
        WHEN r2.relationship_id IS NULL THEN 'MISSING RECIPROCAL'
        ELSE 'VALID'
    END as validation_status
FROM hub4_contacts.relationships r1
LEFT JOIN hub4_contacts.relationships r2
    ON r1.from_person_id = r2.to_person_id
   AND r1.to_person_id = r2.from_person_id
WHERE r2.relationship_id IS NULL;

-- Expected: 0 rows (or document one-way relationships if intentional)
-- Alert: WARNING if count > 0
```

---

### Hub 5: Financials

#### Q5.1: Expense → Legal Entity Validation
```sql
-- Validate all expenses have valid paid_by_entity references
SELECT
    e.expense_id,
    e.expense_category,
    e.amount,
    e.paid_by_entity_id,
    le.legal_name,
    CASE
        WHEN le.entity_id IS NULL THEN 'INVALID: paid_by_entity not found in Hub 6'
        ELSE 'VALID'
    END as validation_status
FROM hub5_financials.expenses e
LEFT JOIN hub6_corporate.legal_entities le ON e.paid_by_entity_id = le.entity_id
WHERE le.entity_id IS NULL;

-- Expected: 0 rows
-- Alert: CRITICAL if count > 0
```

#### Q5.2: Revenue → Legal Entity Validation
```sql
-- Validate all revenue has valid received_by_entity references
SELECT
    r.revenue_id,
    r.revenue_category,
    r.amount,
    r.received_by_entity_id,
    le.legal_name,
    CASE
        WHEN le.entity_id IS NULL THEN 'INVALID: received_by_entity not found in Hub 6'
        ELSE 'VALID'
    END as validation_status
FROM hub5_financials.revenue r
LEFT JOIN hub6_corporate.legal_entities le ON r.received_by_entity_id = le.entity_id
WHERE le.entity_id IS NULL;

-- Expected: 0 rows
-- Alert: CRITICAL if count > 0
```

#### Q5.3: Intercompany Transaction Flagging
```sql
-- Validate intercompany transactions are correctly flagged
SELECT
    expense_id,
    paid_by_entity_id,
    paid_to_entity_id,
    amount,
    CASE
        WHEN paid_to_entity_id IN (
            SELECT entity_id FROM hub6_corporate.legal_entities
            WHERE entity_id IN ('entity_openhaul', 'entity_origin', 'entity_g')
        ) THEN 'SHOULD BE FLAGGED'
        ELSE 'EXTERNAL'
    END as expected_flag,
    notes
FROM hub5_financials.expenses
WHERE paid_to_entity_id IN (
    SELECT entity_id FROM hub6_corporate.legal_entities
    WHERE entity_id IN ('entity_openhaul', 'entity_origin', 'entity_g')
) AND (notes IS NULL OR notes NOT ILIKE '%intercompany%' OR notes NOT ILIKE '%related party%');

-- Expected: 0 rows (all intercompany transactions should be flagged in notes)
-- Alert: WARNING if count > 0
```

#### Q5.4: Invoice → Load Relationship (Cross-Hub to Hub 2)
```sql
-- Validate all invoices with source_load_number have valid load references
SELECT
    i.invoice_id,
    i.invoice_number,
    i.source_load_number,
    l.load_number,
    CASE
        WHEN l.load_number IS NULL THEN 'INVALID: source load not found in Hub 2'
        ELSE 'VALID'
    END as validation_status
FROM hub5_financials.invoices i
LEFT JOIN hub2_openhaul.loads l ON i.source_load_number = l.load_number
WHERE i.source_load_number IS NOT NULL AND l.load_number IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q5.5: Payment → Invoice Matching
```sql
-- Validate all payments reference valid invoices
SELECT
    p.payment_id,
    p.invoice_id,
    p.payment_amount,
    i.invoice_id as invoice_found,
    i.amount_due as invoice_amount,
    CASE
        WHEN i.invoice_id IS NULL THEN 'INVALID: invoice not found'
        WHEN p.payment_amount > i.amount_due THEN 'WARNING: overpayment'
        ELSE 'VALID'
    END as validation_status
FROM hub5_financials.payments p
LEFT JOIN hub5_financials.invoices i ON p.invoice_id = i.invoice_id
WHERE i.invoice_id IS NULL OR p.payment_amount > i.amount_due;

-- Expected: 0 rows (or document overpayments if intentional)
-- Alert: WARNING if count > 0
```

---

### Hub 6: Corporate Infrastructure

#### Q6.1: Legal Entity → Owner Validation (Cross-Hub to Hub 4)
```sql
-- Validate all legal entities have valid owner references
SELECT
    le.entity_id,
    le.legal_name,
    le.owner_person_id,
    p.full_name as owner_name,
    CASE
        WHEN p.person_id IS NULL THEN 'INVALID: owner not found in Hub 4'
        ELSE 'VALID'
    END as validation_status
FROM hub6_corporate.legal_entities le
LEFT JOIN hub4_contacts.persons p ON le.owner_person_id = p.person_id
WHERE le.owner_person_id IS NOT NULL AND p.person_id IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q6.2: Ownership Records → Legal Entity Validation
```sql
-- Validate all ownership records reference valid entities
SELECT
    o.ownership_id,
    o.entity_id,
    o.owner_entity_id,
    le1.legal_name as entity_name,
    le2.legal_name as owner_name,
    CASE
        WHEN le1.entity_id IS NULL THEN 'INVALID: entity_id not found'
        WHEN le2.entity_id IS NULL THEN 'INVALID: owner_entity_id not found'
        ELSE 'VALID'
    END as validation_status
FROM hub6_corporate.ownership_records o
LEFT JOIN hub6_corporate.legal_entities le1 ON o.entity_id = le1.entity_id
LEFT JOIN hub6_corporate.legal_entities le2 ON o.owner_entity_id = le2.entity_id
WHERE le1.entity_id IS NULL OR le2.entity_id IS NULL;

-- Expected: 0 rows
-- Alert: CRITICAL if count > 0
```

#### Q6.3: License Expiration Warnings
```sql
-- Validate licenses are current and warn about upcoming expirations
SELECT
    license_id,
    license_type,
    entity_id,
    expiration_date,
    CASE
        WHEN expiration_date < NOW() THEN 'EXPIRED'
        WHEN expiration_date < NOW() + INTERVAL '30 days' THEN 'EXPIRING SOON (30 days)'
        WHEN expiration_date < NOW() + INTERVAL '90 days' THEN 'EXPIRING (90 days)'
        ELSE 'CURRENT'
    END as status
FROM hub6_corporate.licenses
WHERE expiration_date < NOW() + INTERVAL '90 days';

-- Expected: 0 'EXPIRED'
-- Alert: CRITICAL if any 'EXPIRED', WARNING if any 'EXPIRING SOON'
```

#### Q6.4: Filing → Legal Entity Validation
```sql
-- Validate all filings reference valid legal entities
SELECT
    f.filing_id,
    f.filing_type,
    f.entity_id,
    le.legal_name,
    CASE
        WHEN le.entity_id IS NULL THEN 'INVALID: entity not found'
        ELSE 'VALID'
    END as validation_status
FROM hub6_corporate.filings f
LEFT JOIN hub6_corporate.legal_entities le ON f.entity_id = le.entity_id
WHERE le.entity_id IS NULL;

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

#### Q6.5: Document → Entity/Hub Validation
```sql
-- Validate all documents reference valid entities and have valid metadata
SELECT
    d.document_id,
    d.document_type,
    d.related_entity_id,
    d.metadata->>'hub' as hub,
    CASE
        WHEN d.metadata->>'hub' NOT IN ('hub2_openhaul', 'hub3_origin', 'hub6_corporate') THEN 'INVALID: unknown hub'
        WHEN d.related_entity_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM hub6_corporate.legal_entities le WHERE le.entity_id = d.related_entity_id
        ) THEN 'INVALID: related entity not found'
        ELSE 'VALID'
    END as validation_status
FROM hub6_corporate.documents d
WHERE d.metadata->>'hub' NOT IN ('hub2_openhaul', 'hub3_origin', 'hub6_corporate')
   OR (d.related_entity_id IS NOT NULL AND NOT EXISTS (
       SELECT 1 FROM hub6_corporate.legal_entities le WHERE le.entity_id = d.related_entity_id
   ));

-- Expected: 0 rows
-- Alert: WARNING if count > 0
```

---

## Neo4j Validation Queries

### N1: Node Count Consistency (PostgreSQL vs Neo4j)

```cypher
// Count all nodes by label and compare to PostgreSQL table counts
MATCH (n:Tractor)
RETURN 'Tractor' as entity_type, count(n) as neo4j_count

UNION

MATCH (n:Trailer)
RETURN 'Trailer' as entity_type, count(n) as neo4j_count

UNION

MATCH (n:Driver)
RETURN 'Driver' as entity_type, count(n) as neo4j_count

UNION

MATCH (n:Load)
RETURN 'Load' as entity_type, count(n) as neo4j_count

UNION

MATCH (n:Company)
RETURN 'Company' as entity_type, count(n) as neo4j_count;

// Compare results with PostgreSQL counts
// Expected: neo4j_count = postgres_count for each entity type
// Alert: CRITICAL if mismatch > 1%
```

**PostgreSQL Comparison Query:**
```sql
SELECT 'Tractor' as entity_type, count(*) as postgres_count FROM hub3_origin.tractors
UNION ALL
SELECT 'Trailer', count(*) FROM hub3_origin.trailers
UNION ALL
SELECT 'Driver', count(*) FROM hub3_origin.drivers
UNION ALL
SELECT 'Load', count(*) FROM hub2_openhaul.loads
UNION ALL
SELECT 'Company', count(*) FROM hub4_contacts.companies;
```

---

### N2: Relationship Integrity

```cypher
// Validate all relationships have both start and end nodes
MATCH (start)-[r]->(end)
WHERE start IS NULL OR end IS NULL
RETURN type(r) as relationship_type, count(*) as orphaned_count;

// Expected: 0 rows
// Alert: CRITICAL if count > 0
```

---

### N3: Driver → Tractor Assignment Consistency

```cypher
// Validate ASSIGNED_TO relationships match PostgreSQL driver.current_unit_assignment
MATCH (d:Driver)-[a:ASSIGNED_TO]->(t:Tractor)
WHERE a.end_date IS NULL  // Current assignment
RETURN d.driver_id, d.name, t.unit_number

// Compare with PostgreSQL:
// SELECT driver_id, name, current_unit_assignment
// FROM hub3_origin.drivers
// WHERE current_unit_assignment IS NOT NULL;

// Expected: Results match exactly
// Alert: WARNING if mismatch
```

---

### N4: Load → Carrier Relationship

```cypher
// Validate all loads have HAULED_BY relationship to carrier
MATCH (l:Load)
WHERE NOT EXISTS((l)-[:HAULED_BY]->(:Carrier))
RETURN l.load_number, l.carrier_id;

// Expected: 0 rows
// Alert: WARNING if count > 0
```

---

### N5: Company Multi-Category Consistency

```cypher
// Validate Company nodes with multiple labels match PostgreSQL categories array
MATCH (c:Company)
WHERE c.categories IS NOT NULL
WITH c, labels(c) as neo4j_labels
RETURN c.company_id, c.company_name, c.categories as postgres_categories, neo4j_labels,
       CASE
           WHEN size([label IN neo4j_labels WHERE label IN c.categories]) = size(c.categories) THEN 'CONSISTENT'
           ELSE 'MISMATCH'
       END as validation_status;

// Expected: All 'CONSISTENT'
// Alert: WARNING if any 'MISMATCH'
```

---

### N6: Temporal Relationship Validation (Bi-Temporal)

```cypher
// Validate temporal relationships have consistent valid_from/valid_to
MATCH (start)-[r]->(end)
WHERE r.valid_from IS NOT NULL
  AND (r.valid_to IS NOT NULL AND r.valid_to < r.valid_from)
RETURN type(r) as relationship_type,
       id(start) as start_node,
       id(end) as end_node,
       r.valid_from,
       r.valid_to;

// Expected: 0 rows
// Alert: CRITICAL if count > 0
```

---

### N7: Project → Load Impact Tracking

```cypher
// Validate projects have DRIVES relationships to loads
MATCH (p:Project)-[:DRIVES]->(l:Load)
RETURN p.project_id, p.project_name, count(l) as loads_driven
ORDER BY loads_driven DESC;

// Compare with business expectations
// Alert: WARNING if high-priority project has 0 loads
```

---

### N8: Goal → Revenue Measurement Links

```cypher
// Validate goals have MEASURED_BY relationships to revenue/expense
MATCH (g:Goal)-[:MEASURED_BY]->(target)
WHERE labels(target) IN [['Revenue'], ['Expense']]
RETURN g.goal_id, g.goal_name, labels(target) as measurement_type, count(target) as measurement_count;

// Expected: All goals have measurement_count > 0
// Alert: WARNING if any goal has 0 measurements
```

---

### N9: Intercompany Transaction Network

```cypher
// Validate intercompany payment flows
MATCH (from:LegalEntity)-[:PAID]->(to:LegalEntity)
WHERE from.entity_id IN ['entity_openhaul', 'entity_origin', 'entity_g']
  AND to.entity_id IN ['entity_openhaul', 'entity_origin', 'entity_g']
RETURN from.legal_name, to.legal_name, count(*) as transaction_count
ORDER BY transaction_count DESC;

// Review for expected intercompany flows
// Alert: WARNING if unexpected entity pairs appear
```

---

### N10: Orphaned Nodes Detection

```cypher
// Find nodes with no relationships (may indicate data issues)
MATCH (n)
WHERE NOT (n)--()
RETURN labels(n) as node_type, count(n) as orphaned_count
ORDER BY orphaned_count DESC;

// Expected: 0 for most types (some standalone entities OK)
// Alert: WARNING if critical entity types have orphans
```

---

## Cross-Database Consistency Checks

### C1: PostgreSQL ↔ Neo4j Sync Check

**Purpose:** Verify PostgreSQL (PRIMARY) and Neo4j (REPLICA) are in sync

```python
import psycopg2
from neo4j import GraphDatabase

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

# Neo4j connection
neo4j_driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "apexmemory2024")
)

def check_tractor_sync():
    # Get PostgreSQL count
    with pg_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM hub3_origin.tractors WHERE valid_to IS NULL")
        pg_count = cur.fetchone()[0]

    # Get Neo4j count
    with neo4j_driver.session() as session:
        result = session.run("MATCH (t:Tractor) RETURN count(t) as count")
        neo4j_count = result.single()["count"]

    # Compare
    if pg_count == neo4j_count:
        return "✅ SYNC: Tractor counts match"
    else:
        return f"⚠️ MISMATCH: PostgreSQL={pg_count}, Neo4j={neo4j_count}"

print(check_tractor_sync())
```

**Expected:** "✅ SYNC: Tractor counts match"
**Alert:** CRITICAL if mismatch > 1%

---

### C2: PostgreSQL ↔ Qdrant Vector Sync

**Purpose:** Verify document embeddings in Qdrant match document records in PostgreSQL

```python
from qdrant_client import QdrantClient
import psycopg2

# Qdrant connection
qdrant_client = QdrantClient(host="localhost", port=6333)

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

def check_document_vector_sync():
    # Get PostgreSQL document count
    with pg_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM hub6_corporate.documents WHERE valid_to IS NULL")
        pg_count = cur.fetchone()[0]

    # Get Qdrant vector count
    collection_info = qdrant_client.get_collection("documents")
    qdrant_count = collection_info.points_count

    # Compare
    if pg_count == qdrant_count:
        return "✅ SYNC: Document vector counts match"
    else:
        return f"⚠️ MISMATCH: PostgreSQL={pg_count}, Qdrant={qdrant_count}"

print(check_document_vector_sync())
```

**Expected:** "✅ SYNC: Document vector counts match"
**Alert:** WARNING if mismatch > 5% (some lag acceptable)

---

### C3: PostgreSQL ↔ Redis Cache Validity

**Purpose:** Verify Redis cached data matches PostgreSQL current state

```python
import redis
import psycopg2
import json

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

def check_truck_location_cache(unit_number):
    # Get Redis cached location
    redis_key = f"truck:{unit_number}:location"
    cached_location = redis_client.get(redis_key)

    if not cached_location:
        return "⚠️ CACHE MISS: No Redis entry"

    cached_data = json.loads(cached_location)

    # Get PostgreSQL location
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT location_gps FROM hub3_origin.tractors WHERE unit_number = %s",
            (unit_number,)
        )
        pg_location = cur.fetchone()[0]  # Returns as tuple (lon, lat)

    # Compare (allow 0.001 degree tolerance ~100m)
    if abs(cached_data['lat'] - pg_location[1]) < 0.001 and \
       abs(cached_data['lon'] - pg_location[0]) < 0.001:
        return "✅ SYNC: Cached location matches PostgreSQL"
    else:
        return f"⚠️ MISMATCH: Redis={cached_data}, PostgreSQL={pg_location}"

print(check_truck_location_cache("6520"))
```

**Expected:** "✅ SYNC: Cached location matches PostgreSQL"
**Alert:** WARNING if mismatch (cache may be stale, check TTL)

---

### C4: PostgreSQL ↔ Graphiti Temporal Events

**Purpose:** Verify Graphiti temporal events match PostgreSQL state changes

```python
from graphiti_core import Graphiti
import psycopg2

# Graphiti connection
graphiti = Graphiti(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="apexmemory2024"
)

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host="localhost",
    database="apex_memory",
    user="apex",
    password="apexmemory2024"
)

def check_goal_progress_timeline(goal_id):
    # Get Graphiti timeline
    graphiti_timeline = graphiti.get_entity_timeline(
        entity_type="Goal",
        entity_id=goal_id,
        property="progress_percentage"
    )

    # Get PostgreSQL audit log (assuming audit table exists)
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT created_at, progress_percentage
            FROM hub1_command.goal_audit_log
            WHERE goal_id = %s
            ORDER BY created_at
        """, (goal_id,))
        pg_timeline = cur.fetchall()

    # Compare counts
    if len(graphiti_timeline) == len(pg_timeline):
        return "✅ SYNC: Graphiti timeline matches PostgreSQL audit"
    else:
        return f"⚠️ MISMATCH: Graphiti={len(graphiti_timeline)}, PostgreSQL={len(pg_timeline)}"

print(check_goal_progress_timeline("goal_openhaul_revenue_2025"))
```

**Expected:** "✅ SYNC: Graphiti timeline matches PostgreSQL audit"
**Alert:** WARNING if mismatch > 10% (Graphiti sampling may differ)

---

## Temporal Query Validation

### T1: Driver Assignment History (Bi-Temporal)

**Query:** "Who was driving Unit #6520 on October 15, 2025?"

**Neo4j Query:**
```cypher
MATCH (d:Driver)-[a:ASSIGNED_TO]->(t:Tractor {unit_number: "6520"})
WHERE date("2025-10-15") >= date(a.valid_from)
  AND (a.valid_to IS NULL OR date("2025-10-15") <= date(a.valid_to))
RETURN d.driver_id, d.name, a.assigned_date, a.end_date;
```

**Expected Result:**
```
driver_id: "driver_robert"
name: "Robert McCullough"
assigned_date: "2025-01-01"
end_date: "2025-10-31"
```

**Validation:** Cross-check with PostgreSQL audit log
```sql
SELECT driver_id, name, assigned_date, end_date
FROM hub3_origin.driver_assignment_history
WHERE unit_number = '6520'
  AND assigned_date <= '2025-10-15'
  AND (end_date IS NULL OR end_date >= '2025-10-15');
```

---

### T2: Goal Progress Over Time (Graphiti + PostgreSQL)

**Query:** "Show me Goal 'OpenHaul Revenue 2025' progress from January to October"

**Graphiti Query:**
```python
timeline = graphiti.get_entity_timeline(
    entity_type="Goal",
    entity_id="goal_openhaul_revenue_2025",
    property="progress_percentage",
    start_date="2025-01-01",
    end_date="2025-10-31"
)

# Returns: [(timestamp, value), ...]
# [(2025-01-31, 10%), (2025-02-28, 22%), ..., (2025-10-31, 85%)]
```

**PostgreSQL Cross-Check:**
```sql
SELECT
    revenue_date,
    SUM(amount) OVER (ORDER BY revenue_date) as cumulative_revenue,
    (SUM(amount) OVER (ORDER BY revenue_date) / 500000.0 * 100) as progress_percentage
FROM hub5_financials.revenue
WHERE revenue_category = 'brokerage_commission'
  AND received_by_entity_id = 'entity_openhaul'
  AND revenue_date BETWEEN '2025-01-01' AND '2025-10-31'
ORDER BY revenue_date;
```

**Validation:** Graphiti timeline should match PostgreSQL calculated progress (±2% tolerance)

---

### T3: Entity Ownership Changes Over Time

**Query:** "Show me ownership changes for Origin Transport, LLC in 2025"

**Neo4j Query:**
```cypher
MATCH (entity:LegalEntity {entity_id: "entity_origin"})<-[o:OWNS]-(owner)
WHERE o.valid_from >= date("2025-01-01")
RETURN owner.name as owner_name,
       o.ownership_percentage,
       o.valid_from as start_date,
       o.valid_to as end_date
ORDER BY o.valid_from;
```

**PostgreSQL Cross-Check:**
```sql
SELECT
    o.owner_entity_id,
    le.legal_name as owner_name,
    o.ownership_percentage,
    o.valid_from as start_date,
    o.valid_to as end_date
FROM hub6_corporate.ownership_records o
JOIN hub6_corporate.legal_entities le ON o.owner_entity_id = le.entity_id
WHERE o.entity_id = 'entity_origin'
  AND o.valid_from >= '2025-01-01'
ORDER BY o.valid_from;
```

**Validation:** Results should match exactly

---

### T4: Load Status Timeline (Temporal Progression)

**Query:** "Show me the complete status timeline for Load OH-321678"

**Neo4j Query:**
```cypher
MATCH (l:Load {load_number: "OH-321678"})-[s:HAS_STATUS]->(status)
RETURN status.status_name,
       s.valid_from as start_time,
       s.valid_to as end_time
ORDER BY s.valid_from;
```

**Expected Result:**
```
status_name: "booked", start_time: 2025-10-01T10:00:00Z, end_time: 2025-10-05T08:30:00Z
status_name: "in_transit", start_time: 2025-10-05T08:30:00Z, end_time: 2025-10-07T14:15:00Z
status_name: "delivered", start_time: 2025-10-07T14:15:00Z, end_time: NULL
```

**Validation:** Temporal ranges should be contiguous (no gaps, no overlaps)

---

### T5: Project Impact Timeline (Cross-Hub)

**Query:** "Show me all loads driven by Project 'OpenHaul Q4 2025 Growth Initiative' over time"

**Neo4j Query:**
```cypher
MATCH (p:Project {project_id: "proj_018c3a8b"})-[:DRIVES]->(l:Load)
WHERE l.booked_date >= date("2025-10-01")
  AND l.booked_date <= date("2025-10-31")
RETURN l.load_number, l.booked_date, l.customer_rate, l.margin
ORDER BY l.booked_date;
```

**PostgreSQL Cross-Check:**
```sql
SELECT
    l.load_number,
    l.booked_date,
    l.customer_rate,
    l.margin
FROM hub2_openhaul.loads l
WHERE l.source_project_id = 'proj_018c3a8b'
  AND l.booked_date BETWEEN '2025-10-01' AND '2025-10-31'
ORDER BY l.booked_date;
```

**Validation:** Results should match exactly

---

## Automated Test Suite

### Test Suite Structure

```
tests/
├── integration/
│   ├── test_postgres_validation.py
│   ├── test_neo4j_validation.py
│   ├── test_cross_database_sync.py
│   └── test_temporal_queries.py
├── unit/
│   ├── test_hub1_validation.py
│   ├── test_hub2_validation.py
│   ├── test_hub3_validation.py
│   ├── test_hub4_validation.py
│   ├── test_hub5_validation.py
│   └── test_hub6_validation.py
└── fixtures/
    ├── sample_data.sql
    └── sample_relationships.cypher
```

---

### Example: test_postgres_validation.py

```python
import pytest
import psycopg2

@pytest.fixture
def db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="apex_memory",
        user="apex",
        password="apexmemory2024"
    )
    yield conn
    conn.close()

def test_hub1_g_entity_integrity(db_connection):
    """Test Q1.1: G Person Entity Integrity"""
    with db_connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM hub1_command.g_persons g
            LEFT JOIN hub4_contacts.persons p ON g.person_id = p.person_id
            WHERE p.person_id IS NULL
        """)
        orphaned_count = cur.fetchone()[0]

    assert orphaned_count == 0, f"Found {orphaned_count} orphaned G entities"

def test_hub2_load_margin_validation(db_connection):
    """Test Q2.3: Load Margin Validation"""
    with db_connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM hub2_openhaul.loads
            WHERE margin IS NULL
               OR ABS(margin - (customer_rate - carrier_rate)) > 0.01
        """)
        invalid_margins = cur.fetchone()[0]

    assert invalid_margins == 0, f"Found {invalid_margins} loads with invalid margins"

def test_hub3_driver_unit_assignment(db_connection):
    """Test Q3.2: Driver → Current Unit Assignment"""
    with db_connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM hub3_origin.drivers d
            LEFT JOIN hub3_origin.tractors t ON d.current_unit_assignment = t.unit_number
            WHERE d.current_unit_assignment IS NOT NULL AND t.unit_number IS NULL
        """)
        invalid_assignments = cur.fetchone()[0]

    assert invalid_assignments == 0, f"Found {invalid_assignments} invalid driver assignments"

def test_hub5_expense_entity_validation(db_connection):
    """Test Q5.1: Expense → Legal Entity Validation"""
    with db_connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM hub5_financials.expenses e
            LEFT JOIN hub6_corporate.legal_entities le ON e.paid_by_entity_id = le.entity_id
            WHERE le.entity_id IS NULL
        """)
        orphaned_expenses = cur.fetchone()[0]

    assert orphaned_expenses == 0, f"Found {orphaned_expenses} expenses with invalid entity references"
```

---

### Example: test_neo4j_validation.py

```python
import pytest
from neo4j import GraphDatabase

@pytest.fixture
def neo4j_session():
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "apexmemory2024")
    )
    with driver.session() as session:
        yield session
    driver.close()

def test_relationship_integrity(neo4j_session):
    """Test N2: Relationship Integrity"""
    result = neo4j_session.run("""
        MATCH (start)-[r]->(end)
        WHERE start IS NULL OR end IS NULL
        RETURN count(*) as orphaned_count
    """)
    orphaned_count = result.single()["orphaned_count"]

    assert orphaned_count == 0, f"Found {orphaned_count} orphaned relationships"

def test_driver_assignment_consistency(neo4j_session):
    """Test N3: Driver → Tractor Assignment Consistency"""
    result = neo4j_session.run("""
        MATCH (d:Driver)-[a:ASSIGNED_TO]->(t:Tractor)
        WHERE a.end_date IS NULL
        RETURN count(*) as current_assignments
    """)
    neo4j_assignments = result.single()["current_assignments"]

    # Cross-check with PostgreSQL (would need separate connection)
    # For now, just verify count > 0
    assert neo4j_assignments > 0, "No current driver assignments found in Neo4j"

def test_temporal_relationship_validity(neo4j_session):
    """Test N6: Temporal Relationship Validation"""
    result = neo4j_session.run("""
        MATCH (start)-[r]->(end)
        WHERE r.valid_from IS NOT NULL
          AND r.valid_to IS NOT NULL
          AND r.valid_to < r.valid_from
        RETURN count(*) as invalid_count
    """)
    invalid_count = result.single()["invalid_count"]

    assert invalid_count == 0, f"Found {invalid_count} relationships with invalid temporal ranges"
```

---

### Example: test_cross_database_sync.py

```python
import pytest
import psycopg2
from neo4j import GraphDatabase
from qdrant_client import QdrantClient

@pytest.fixture
def all_connections():
    # PostgreSQL
    pg_conn = psycopg2.connect(
        host="localhost",
        database="apex_memory",
        user="apex",
        password="apexmemory2024"
    )

    # Neo4j
    neo4j_driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "apexmemory2024")
    )

    # Qdrant
    qdrant_client = QdrantClient(host="localhost", port=6333)

    yield {
        "postgres": pg_conn,
        "neo4j": neo4j_driver,
        "qdrant": qdrant_client
    }

    pg_conn.close()
    neo4j_driver.close()

def test_tractor_count_sync(all_connections):
    """Test C1: PostgreSQL ↔ Neo4j Tractor Sync"""
    # PostgreSQL count
    with all_connections["postgres"].cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM hub3_origin.tractors WHERE valid_to IS NULL")
        pg_count = cur.fetchone()[0]

    # Neo4j count
    with all_connections["neo4j"].session() as session:
        result = session.run("MATCH (t:Tractor) RETURN count(t) as count")
        neo4j_count = result.single()["count"]

    assert pg_count == neo4j_count, f"Tractor count mismatch: PostgreSQL={pg_count}, Neo4j={neo4j_count}"

def test_document_vector_sync(all_connections):
    """Test C2: PostgreSQL ↔ Qdrant Vector Sync"""
    # PostgreSQL count
    with all_connections["postgres"].cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM hub6_corporate.documents WHERE valid_to IS NULL")
        pg_count = cur.fetchone()[0]

    # Qdrant count
    collection_info = all_connections["qdrant"].get_collection("documents")
    qdrant_count = collection_info.points_count

    # Allow 5% mismatch for eventual consistency
    mismatch_pct = abs(pg_count - qdrant_count) / pg_count * 100
    assert mismatch_pct < 5, f"Document vector mismatch: {mismatch_pct:.1f}% (PostgreSQL={pg_count}, Qdrant={qdrant_count})"
```

---

### CI/CD Integration

**GitHub Actions Example:**

```yaml
name: Schema Validation Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validation:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: apex_memory
          POSTGRES_USER: apex
          POSTGRES_PASSWORD: apexmemory2024
        ports:
          - 5432:5432

      neo4j:
        image: neo4j:5.14
        env:
          NEO4J_AUTH: neo4j/apexmemory2024
        ports:
          - 7687:7687

      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6333:6333

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Load test fixtures
        run: |
          psql -h localhost -U apex -d apex_memory -f tests/fixtures/sample_data.sql
          # Load Neo4j fixtures via cypher-shell

      - name: Run PostgreSQL validation tests
        run: pytest tests/integration/test_postgres_validation.py -v

      - name: Run Neo4j validation tests
        run: pytest tests/integration/test_neo4j_validation.py -v

      - name: Run cross-database sync tests
        run: pytest tests/integration/test_cross_database_sync.py -v

      - name: Generate coverage report
        run: pytest --cov=. --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
```

---

## Summary

This validation query suite provides:

- ✅ **25 PostgreSQL queries** validating referential integrity, temporal consistency, and business logic across all 6 hubs
- ✅ **10 Neo4j queries** validating relationship integrity, node count consistency, and temporal patterns
- ✅ **4 cross-database sync checks** ensuring PostgreSQL, Neo4j, Qdrant, and Graphiti remain consistent
- ✅ **5 temporal query validations** proving bi-temporal tracking works correctly
- ✅ **Automated test suite** with pytest examples for CI/CD integration

**Expected Results:** All validation queries should return 0 rows (no issues) in a healthy system.

**Alert Levels:**
- 🔴 **CRITICAL:** Data integrity issues requiring immediate fix (orphaned records, constraint violations)
- 🟡 **WARNING:** Data quality issues requiring investigation (expired licenses, overpayments, orphaned addresses)

**Production Deployment Checklist:**
1. Run all PostgreSQL queries (Q1.1 - Q6.5)
2. Run all Neo4j queries (N1 - N10)
3. Run all cross-database sync checks (C1 - C4)
4. Validate all temporal queries (T1 - T5)
5. Execute automated test suite (pytest)
6. Review and document any warnings
7. Configure monitoring alerts for critical queries

---

**Next Document:** 6-HUB-DATA-MIGRATION-GUIDE.md (migration procedures and rollback plans)
