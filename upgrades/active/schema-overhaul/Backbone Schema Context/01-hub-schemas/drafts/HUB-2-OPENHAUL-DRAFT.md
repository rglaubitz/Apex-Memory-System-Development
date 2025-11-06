# HUB 2: OPENHAUL (BROKERAGE OPERATIONS)

**Status:** 📝 Draft - Rough Structure
**Purpose:** Freight brokerage front-end operations - booking, execution, carrier management
**Company:** OpenHaul LLC
**Primary Key Strategy:** load_number (e.g., "OH-321678")

---

## Purpose

Hub 2 tracks all OpenHaul brokerage operations - the "front-end" of the business. This includes customer sales orders, load bookings, carrier assignments, pickup/delivery execution, and document management.

**Key Distinction:** This hub focuses on OPERATIONAL work (booking, execution). The FINANCIAL side (invoices, payments) lives in Hub 5 (Financials).

**Relationship to Origin:** Origin Transport trucks are treated as "just another carrier" for OpenHaul loads. Normal load payments flow through Hub 5. Intercompany transfers (credit lines, bill coverage) are also tracked in Hub 5.

---

## Core Entities

### 1. **Load** - The Central Entity ⭐
The primary entity representing a freight movement. Everything links back to the load number.

**Core Properties:**
- **load_number** (PRIMARY KEY - format: "OH-321678")
- customer_id (who bought this shipment)
- carrier_id (who hauls it - could be Origin truck or external carrier)
- pickup_location_id
- delivery_location_id
- pickup_date, delivery_date
- equipment_type (dry van, reefer, flatbed, etc.)
- weight_lbs
- commodity_description
- status (booked, dispatched, in-transit, delivered, invoiced, completed)

**Financial Properties (linked to Hub 5):**
- customer_rate (how much OpenHaul charges customer)
- carrier_rate (how much OpenHaul pays carrier)
- margin (customer_rate - carrier_rate)
- accessorial_charges [] (lumper fees, detention, etc.)

**Temporal:**
- created_at, updated_at, booked_date, completed_date
- valid_from, valid_to

**Example:**
```python
Load(
    load_number="OH-321678",
    customer_id="cust_sun_glo",
    carrier_id="carr_origin_6520",  # Origin truck as carrier
    pickup_location_id="loc_chicago_warehouse",
    delivery_location_id="loc_dallas_dc",
    pickup_date="2025-11-05",
    delivery_date="2025-11-07",
    customer_rate=2500.00,
    carrier_rate=2000.00,
    margin=500.00,
    status="delivered"
)
```

---

### 2. **Carrier** - Trucking Companies & Drivers
Companies or owner-operators who haul freight for OpenHaul.

**Core Properties:**
- carrier_id (UUID or standardized ID)
- carrier_name
- carrier_type (asset-based, owner-operator, broker)
- mc_number (FMCSA authority)
- dot_number
- contact_person_id (links to Hub 4 - Contacts)
- phone, email
- insurance_expiry_date
- preferred_lanes [] (array of route preferences)
- rating (1-5 stars)
- active_status (boolean)

**Special Case - Origin Transport:**
```python
Carrier(
    carrier_id="carr_origin",
    carrier_name="Origin Transport LLC",
    carrier_type="asset-based",
    mc_number="MC-123456",  # Origin's actual MC
    dot_number="DOT-789012",
    contact_person_id="person_g",  # G in Hub 4
    rating=5,
    active_status=True,
    notes="Internal carrier - Primetime-owned"
)
```

**When Origin Truck Hauls OpenHaul Load:**
```cypher
// Load links to carrier "Origin" and specific unit
(Load {load_number: "OH-321678"})-[:HAULED_BY]->(Carrier {carrier_id: "carr_origin"})
(Load)-[:ASSIGNED_UNIT {unit_number: "6520"}]->(Tractor)  // Hub 3 link
```

---

### 3. **Location** - Pickup & Delivery Points
Shipper and receiver facilities.

**Core Properties:**
- location_id (UUID)
- location_name
- location_type (shipper, receiver, both)
- address (street, city, state, zip)
- contact_person_id (links to Hub 4)
- phone
- operating_hours
- appointment_required (boolean)
- dock_count
- restrictions [] (no reefers, no teams, etc.)
- notes

**Relationship to Contacts Hub:**
```cypher
(Location)-[:BELONGS_TO]->(Company)  // Hub 4
(Location)-[:CONTACT_PERSON]->(Person)  // Hub 4
```

**Example:**
```python
Location(
    location_id="loc_chicago_warehouse",
    location_name="Sun-Glo Chicago Warehouse",
    location_type="shipper",
    address="123 Industrial Blvd, Chicago, IL 60601",
    contact_person_id="person_shannon",  // Shannon from Hub 4
    appointment_required=True,
    operating_hours="Mon-Fri 8am-5pm"
)
```

---

### 4. **SalesOrder** (Document Entity)
Customer's purchase order or commitment.

**Core Properties:**
- sales_order_id (UUID)
- load_number (links to Load entity)
- customer_id
- order_number (customer's reference)
- order_date
- document_path (where PDF is stored)
- extracted_data: {} (JSON - key fields extracted from PDF)

**Note:** This is a DOCUMENT entity, not the primary operational entity. The **Load** is the primary entity.

**Relationship:**
```cypher
(SalesOrder)-[:FOR_LOAD]->(Load {load_number: "OH-321678"})
(SalesOrder)-[:FROM_CUSTOMER]->(Customer)  // Hub 4
```

---

### 5. **RateConfirmation** (Document Entity)
Agreement with carrier on rate and terms.

**Core Properties:**
- rate_con_id (UUID)
- load_number (links to Load entity)
- carrier_id
- rate_con_date
- agreed_rate
- terms_text
- document_path (PDF location)
- signed (boolean)
- signature_date

**Note:** This is a DOCUMENT entity. The carrier assignment and rate are ALSO stored on the Load entity for quick access.

**Relationship:**
```cypher
(RateConfirmation)-[:FOR_LOAD]->(Load {load_number: "OH-321678"})
(RateConfirmation)-[:WITH_CARRIER]->(Carrier)
```

---

### 6. **BOL** (Bill of Lading) - Document Entity
Proof of pickup and freight details.

**Core Properties:**
- bol_id (UUID)
- load_number (links to Load)
- bol_number (BOL reference number)
- pickup_date
- pickup_signature
- piece_count
- weight_lbs
- document_path (PDF)
- extracted_data: {} (JSON)

---

### 7. **POD** (Proof of Delivery) - Document Entity
Proof of delivery and receiver sign-off.

**Core Properties:**
- pod_id (UUID)
- load_number (links to Load)
- delivery_date
- delivery_signature
- receiver_name
- delivery_notes
- document_path (PDF)
- extracted_data: {} (JSON)

---

### 8. **Factor** - Factoring Company
Quick-pay financing services.

**Core Properties:**
- factor_id (UUID)
- factor_name (e.g., "Triumph Business Capital")
- contact_person_id (Hub 4)
- fee_percentage (e.g., 3.5%)
- advance_percentage (e.g., 95%)
- payment_terms (e.g., "same-day funding")
- active_status

**Relationship to Financials:**
```cypher
(Invoice)-[:FACTORED_BY]->(Factor)  // Hub 5
(Factor)-[:CHARGES_FEE]->(Expense)  // Hub 5
```

---

## Primary Relationships

### Load-Centric Relationships
```cypher
// Core load structure
(Load {load_number: "OH-321678"})-[:BOOKED_FOR]->(Customer)      // Hub 4
(Load)-[:HAULED_BY]->(Carrier)
(Load)-[:PICKS_UP_AT]->(Location {type: "shipper"})
(Load)-[:DELIVERS_TO]->(Location {type: "receiver"})

// Document relationships
(SalesOrder)-[:FOR_LOAD]->(Load)
(RateConfirmation)-[:FOR_LOAD]->(Load)
(BOL)-[:FOR_LOAD]->(Load)
(POD)-[:FOR_LOAD]->(Load)

// Financial links (to Hub 5)
(Load)-[:GENERATES]->(Revenue)           // Hub 5
(Load)-[:INCURS]->(Expense)              // Hub 5 (carrier payment)
(Load)-[:INVOICED_AS]->(Invoice)         // Hub 5 (customer invoice)
```

### Carrier Relationships
```cypher
// Carrier to contacts
(Carrier)-[:MANAGED_BY]->(Person)        // Hub 4 - contact person
(Carrier)-[:COMPANY_ENTITY]->(Company)   // Hub 4

// Carrier to loads
(Carrier)-[:HAULED]->(Load)

// Special case: Origin as carrier
(Carrier {carrier_name: "Origin Transport"})-[:IS_INTERNAL_TO]->(OpenHaul)
(Load)-[:HAULED_BY]->(Carrier {carrier_id: "carr_origin"})
(Load)-[:ASSIGNED_UNIT {unit_number: "6520"}]->(Tractor)  // Hub 3 link
```

### Location Relationships
```cypher
(Location)-[:BELONGS_TO]->(Company)      // Hub 4
(Location)-[:PRIMARY_CONTACT]->(Person)  // Hub 4
(Load)-[:PICKS_UP_AT]->(Location)
(Load)-[:DELIVERS_TO]->(Location)
```

---

## Database Distribution

### Neo4j (Relationship Memory)
**Stores:**
- Load nodes with basic identifying info
- Carrier nodes
- Location nodes
- All relationships (load → customer, load → carrier, load → locations)
- Cross-hub relationships (load → invoice, load → tractor)

**Why:** Graph traversal - "Show all loads for Sun-Glo", "Which carriers haul from Chicago?", "Track load → invoice → payment chain"

---

### PostgreSQL (Factual Memory)
**Stores:**
- Complete load details (dates, rates, margins, descriptions)
- Carrier profiles (MC numbers, insurance, ratings)
- Location details (addresses, hours, restrictions)
- Document metadata (SalesOrder, RateConfirmation, BOL, POD)
- Factor details

**Why:** Structured queries - "Total loads delivered in October", "Average margin by customer", "Carriers with expiring insurance"

---

### Qdrant (Semantic Memory)
**Stores:**
- Document embeddings (SalesOrder PDFs, RateCon PDFs, BOLs, PODs)
- Location notes/restrictions embeddings
- Carrier performance notes

**Why:** Semantic search - "Find loads similar to this one", "Search BOLs mentioning damage", "Find carriers with specific equipment"

---

### Redis (Working Memory)
**Stores:**
- Active loads (status = in-transit) with ETA (60s TTL)
- Available carriers by lane (for quick dispatch)
- Recent load bookings (rolling 24-hour window)

**Why:** Real-time dispatch dashboard - "Which loads are in transit right now?", "Available carriers for Chicago → Dallas?"

---

### Graphiti (Temporal Memory)
**Stores:**
- Load lifecycle (booked → dispatched → in-transit → delivered → invoiced)
- Carrier performance trends over time
- Customer shipping pattern evolution
- Margin changes by lane over time

**Why:** Temporal queries - "When did this load status change?", "How has carrier performance changed in Q4?", "Customer shipping volume trends"

---

## Primary Keys & Cross-Database Identity

**Load Entity:**
```python
# Neo4j
(:Load {load_number: "OH-321678", customer_id: "...", carrier_id: "..."})

# PostgreSQL
SELECT * FROM loads WHERE load_number = 'OH-321678'

# Qdrant (for load-related documents)
filter={"load_number": "OH-321678"}

# Redis
GET load:OH-321678:status
GET load:OH-321678:eta

# Graphiti
Load(load_number="OH-321678", ...)
```

**Carriers use carrier_id**, **Locations use location_id** - consistent across all databases.

---

## Cross-Hub Links

### Hub 2 → Hub 3 (Origin Transport)
```cypher
// When Origin truck hauls OpenHaul load
(Load {load_number: "OH-321678"})-[:HAULED_BY]->(Carrier {carrier_id: "carr_origin"})
(Load)-[:ASSIGNED_UNIT {unit_number: "6520"}]->(Tractor)  // Link to Hub 3

// Unit #6520 relationship
(Tractor {unit_number: "6520"})-[:HAULS]->(Load {load_number: "OH-321678"})
```

### Hub 2 → Hub 4 (Contacts)
```cypher
// Customer relationships
(Load)-[:BOOKED_FOR]->(Customer:Company)
(SalesOrder)-[:FROM_CUSTOMER]->(Customer)

// Carrier relationships
(Carrier)-[:MANAGED_BY]->(Person)
(Carrier)-[:COMPANY_ENTITY]->(Company)

// Location contacts
(Location)-[:BELONGS_TO]->(Company)
(Location)-[:PRIMARY_CONTACT]->(Person)
```

### Hub 2 → Hub 5 (Financials)
```cypher
// Revenue generation
(Load)-[:GENERATES]->(Revenue {amount: 2500, source: "customer_payment"})

// Expense creation (carrier payment)
(Load)-[:INCURS]->(Expense {amount: 2000, category: "carrier_payment"})

// Invoice linkage
(Load)-[:CUSTOMER_INVOICE]->(Invoice {type: "customer"})  // What we bill
(Load)-[:CARRIER_INVOICE]->(Invoice {type: "carrier"})    // What we pay

// Factoring
(Invoice)-[:FACTORED_BY]->(Factor)
```

### Hub 2 → Hub 6 (Corporate)
```cypher
// Company ownership
(OpenHaul:Company)-[:BOOKS]->(Load)
(Load)-[:BOOKED_BY]->(OpenHaul)

// License requirements
(Load)-[:REQUIRES]->(License {type: "broker_authority", number: "MC-123456"})
```

---

## Key Operational Patterns

### Load Lifecycle
```
1. Customer sends SalesOrder → Create Load entity (status: booked)
2. Dispatcher books carrier → Create RateConfirmation
3. Carrier picks up → BOL created (status: in-transit)
4. Carrier delivers → POD created (status: delivered)
5. Accounting invoices customer → Invoice created in Hub 5 (status: invoiced)
6. Payment received → Payment recorded in Hub 5 (status: completed)
```

### Origin Truck Booking Flow
```
1. OpenHaul needs coverage for load OH-321678
2. Dispatcher checks available Origin trucks (Hub 3)
3. Unit #6520 available in Chicago
4. Book load: carrier_id = "carr_origin", assign unit_number = "6520"
5. Payment flows through Hub 5 (not special intercompany transaction)
```

### Intercompany Transaction (Different Flow)
```
1. OpenHaul needs $10k cash flow
2. Origin sends $10k to OpenHaul
3. This is INTERCOMPANY_TRANSFER in Hub 5 (NOT load-related payment)
4. Links: (Origin)-[:TRANSFERRED_TO]->(OpenHaul)
```

---

## TODO - Information Needed

### Missing Details
- [ ] **Equipment Types:** Complete list (dry van, reefer, flatbed, step deck, etc.)
- [ ] **Load Statuses:** Full lifecycle status list (booked, dispatched, in-transit, delivered, invoiced, completed, cancelled)
- [ ] **Accessorial Charges:** Common types (lumper fees, detention, layover, TONU, etc.)
- [ ] **Document Types:** Complete list of all document types tracked
- [ ] **Carrier Rating Criteria:** How are carriers rated 1-5 stars?
- [ ] **Location Restrictions:** Common restriction types

### Document Examples
- [ ] Sample SalesOrder (customer PO)
- [ ] Sample RateConfirmation (carrier booking)
- [ ] Sample BOL
- [ ] Sample POD
- [ ] Sample lumper receipt
- [ ] Sample NOA (Notice of Assignment)

### Integration Questions
- [ ] **Factor Integration:** How does factoring flow work in detail? (OpenHaul → Factor → Funding)
- [ ] **Detention Tracking:** How to track and bill detention/layover charges?
- [ ] **Multi-Stop Loads:** How to handle loads with multiple pickups/deliveries?
- [ ] **Carrier Onboarding:** What documents required? (W-9, insurance cert, MC authority)

### Cross-Hub Clarifications
- [ ] When Origin hauls for OpenHaul, does driver get paid separately or via Origin payroll? (Likely Hub 5 question)
- [ ] How to track OpenHaul factoring fees as expenses? (Hub 5)
- [ ] Should customer locations link to Customer entity or stand alone?

---

## Next Steps

1. **Review this draft** - Does load-centric model make sense?
2. **Get document examples** - Real sales orders, rate cons, BOLs, PODs
3. **Define complete status/category lists**
4. **Clarify Origin-as-carrier workflow** - Ensure payment flow is clear
5. **Deep dive** - Expand to full detail matching Hub 3 baseline

---

**Draft Created:** November 3, 2025
**Schema Version:** v2.0 (Draft)
**Completion Status:** ~35% (structure defined, examples needed)
