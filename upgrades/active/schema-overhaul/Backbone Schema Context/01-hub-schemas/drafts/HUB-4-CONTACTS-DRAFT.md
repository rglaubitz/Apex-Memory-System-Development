# HUB 4: CONTACTS (CRM)

**Status:** 📝 Draft - Rough Structure
**Purpose:** Relationship management for people and companies across all business contexts
**Primary Key Strategy:** person_id (UUID) for people, company_id (UUID) for companies

---

## Purpose

Hub 4 is the central CRM hub managing all relationship data for people and companies. This includes customers, vendors, employees, partners, and personal relationships.

**Key Features:**
- **Multi-category system:** Entities can have multiple categories (Sun-Glo is both customer AND vendor)
- **Relationship intelligence:** Track communication, preferences, life events, business connections
- **Cross-hub integration:** Contacts link to loads (Hub 2), trucks (Hub 3), invoices (Hub 5), legal entities (Hub 6)
- **Natural expansion:** Start simple (contact info, relationships), expand over time (preferences, communication history)

**Important Distinction:**
- **Origin Drivers:** Operational data in Hub 3 (performance, assignments), personal data in Hub 4 (birthday, contact info)
- **Office Staff:** Primarily in Hub 4 with "employee" category

---

## Core Entities

### 1. **Person** - Individual Contacts
People across all relationship types.

**Core Properties:**
- **person_id** (PRIMARY KEY - UUID)
- first_name, last_name
- email, phone (mobile), phone_work
- birthday
- location (city, state)
- timezone
- preferred_contact_method (email, text, phone, in-person)
- categories [] (array - employee, partner, personal, driver, customer-contact, vendor-contact)
- relationship_to_g (business_partner, employee, friend, family, customer_contact, vendor_contact, driver, etc.)
- active_status (boolean)

**Employment/Affiliation:**
- employer_company_id (which company they work for, if applicable)
- job_title, role
- start_date_at_company

**Preferences & Intelligence:**
- communication_style: text (how they prefer to communicate)
- preferences: {} (JSON - preferences cheat sheet that builds over time)
- important_dates [] (birthdays, anniversaries, work anniversaries)
- life_events [] (promotions, moves, family events - for relationship management)

**Temporal:**
- created_at, updated_at, valid_from, valid_to

**Examples:**
```python
# Business Partner
Person(
    person_id="person_travis",
    first_name="Travis",
    last_name="Arave",
    email="travis@origintransport.com",
    phone="702-555-0123",
    categories=["partner", "employee"],
    relationship_to_g="business_partner",
    employer_company_id="company_origin",
    job_title="Co-Founder",
    preferences={"communication_style": "direct, phone preferred for urgent matters"}
)

# Customer Contact
Person(
    person_id="person_shannon",
    first_name="Shannon",
    last_name="[Last Name]",
    email="shannon@sunglo.com",
    phone="312-555-0199",
    categories=["customer-contact"],
    relationship_to_g="customer_contact",
    employer_company_id="company_sunglo",
    job_title="Logistics Coordinator",
    preferences={"ships_on": "Fridays typically", "prefers_email": True}
)

# Driver (links to Hub 3)
Person(
    person_id="person_robert",
    first_name="Robert",
    last_name="McCullough",
    email="robert.mccullough@origintransport.com",
    phone="702-555-0188",
    birthday="1978-04-15",
    categories=["employee", "driver"],
    relationship_to_g="employee",
    employer_company_id="company_origin",
    job_title="Driver"
    # Operational driver data (current_unit, performance) lives in Hub 3
)
```

---

### 2. **Company** - Organizations
Businesses, vendors, customers, partners.

**Core Properties:**
- **company_id** (PRIMARY KEY - UUID)
- company_name (legal name)
- dba_name (doing business as, if different)
- industry
- website
- phone, email (general contact)
- address (headquarters)
- categories [] (array - customer, vendor, carrier, shipper, receiver, partner, competitor, etc.)

**Financial/Operational:**
- credit_rating (A, B, C, D)
- payment_terms (net-30, net-15, COD, etc.)
- credit_limit (if applicable)
- preferred_vendor (boolean - for vendors we prefer)
- performance_rating (1-5 stars)
- active_status (boolean)

**Relationship Intelligence:**
- primary_contact_person_id (main person at company)
- account_manager_person_id (who at Origin/OpenHaul manages this relationship)
- relationship_since (date when relationship started)
- relationship_strength (weak, moderate, strong)
- annual_volume_estimate (if customer - estimated yearly revenue)

**Temporal:**
- created_at, updated_at, valid_from, valid_to

**Examples:**
```python
# Customer & Vendor (Multi-category!)
Company(
    company_id="company_sunglo",
    company_name="Sun-Glo Corporation",
    industry="Manufacturing",
    categories=["customer"],  # Customer of OpenHaul
    credit_rating="A",
    payment_terms="net-30",
    primary_contact_person_id="person_shannon",
    relationship_since="2019-03-01",
    relationship_strength="strong",
    annual_volume_estimate=500000  # $500k/year
)

# Origin & OpenHaul as Companies (Multi-category!)
Company(
    company_id="company_origin",
    company_name="Origin Transport LLC",
    categories=["carrier", "vendor", "customer"],  # Vendor AND customer of OpenHaul!
    relationship_to_g="owned_company",
    owner_entity_id="entity_primetime"  # Links to Hub 6
)

Company(
    company_id="company_openhaul",
    company_name="OpenHaul LLC",
    categories=["broker", "customer", "vendor"],  # Customer AND vendor of Origin!
    relationship_to_g="owned_company",
    owner_entity_id="entity_primetime"  # Links to Hub 6
)

# Vendor Example
Company(
    company_id="company_bosch",
    company_name="Bosch Automotive Service Solutions",
    categories=["vendor"],  # Vendor to Origin (maintenance/parts)
    industry="Automotive Parts & Service",
    payment_terms="net-15",
    preferred_vendor=True,
    performance_rating=5
)
```

---

### 3. **CommunicationLog** - Interaction History
Track communication with people/companies over time.

**Core Properties:**
- communication_id (UUID)
- person_id or company_id (who we communicated with)
- communication_type (email, phone, text, in-person, meeting)
- date, time
- direction (inbound, outbound)
- subject/topic
- summary/highlights (AI-extracted or manual - NOT full email text)
- sentiment (positive, neutral, negative)
- action_items [] (followups needed)
- related_entities [] (load_number, unit_number, invoice_number if applicable)

**Note:** Start with email highlights only. Can expand to full text search later if needed.

**Example:**
```python
CommunicationLog(
    communication_id="comm_001",
    person_id="person_shannon",
    company_id="company_sunglo",
    communication_type="email",
    date="2025-11-01",
    direction="inbound",
    subject="Weekly load request - Chicago to Dallas",
    summary="Shannon requesting Friday pickup for 40k lbs. Standard route. Rate discussion - holding at $2,500.",
    action_items=["Book carrier by Wed", "Confirm pickup window"],
    related_entities={"load_number": "OH-321678"}
)
```

---

### 4. **BusinessCard** (Optional - Document Entity)
Physical or digital business cards received.

**Core Properties:**
- card_id (UUID)
- person_id (who the card belongs to)
- company_id
- date_received
- source (networking event, trade show, cold call, etc.)
- document_path (scan/photo of card)
- notes

---

### 5. **Contract** (Document Entity)
Contracts with vendors, customers, carriers.

**Core Properties:**
- contract_id (UUID)
- company_id (who contract is with)
- contract_type (vendor_agreement, customer_contract, carrier_agreement, NDA, etc.)
- start_date, end_date
- auto_renewal (boolean)
- renewal_terms
- document_path (PDF location)
- key_terms: {} (JSON - important contract provisions)
- status (active, expired, terminated)

---

## Primary Relationships

### Person ↔ Company
```cypher
// Employment
(Shannon:Person)-[:WORKS_FOR {role: "Logistics Coordinator"}]->(SunGlo:Company)
(Travis:Person)-[:WORKS_FOR {role: "Co-Founder"}]->(Origin:Company)

// Ownership (Links to Hub 6)
(Travis:Person)-[:OWNS {percentage: 50}]->(OpenHaul:Company)
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:Company)

// Contact relationship
(Shannon:Person)-[:PRIMARY_CONTACT_FOR]->(SunGlo:Company)
(Person)-[:ACCOUNT_MANAGER_FOR]->(Company)
```

### Person ↔ Person
```cypher
// Business relationships
(G:Person)-[:BUSINESS_PARTNER_WITH]->(Travis:Person)
(G:Person)-[:MANAGES]->(Robert:Person)  // Manager/employee

// Personal relationships
(G:Person)-[:FRIEND_OF]->(Person)
(G:Person)-[:FAMILY_MEMBER {relationship: "spouse"}]->(Person)
```

### Company ↔ Company
```cypher
// Business relationships with multi-category support
(Origin:Company)-[:VENDOR_OF]->(OpenHaul:Company)
(Origin:Company)-[:CUSTOMER_OF]->(OpenHaul:Company)
(OpenHaul:Company)-[:CUSTOMER_OF]->(Origin:Company)

// Industry relationships
(Company)-[:COMPETITOR_OF]->(Company)
(Company)-[:PARTNER_WITH]->(Company)
```

---

## Cross-Hub Relationships

### Hub 4 → Hub 1 (G Command)
```cypher
(G:Person)-[:KNOWS]->(Person)
(G:Person)-[:RELATIONSHIP_WITH {type: "business_partner"}]->(Travis:Person)
(Project)-[:INVOLVES]->(Company)  // Project in Hub 1 involves Company in Hub 4
```

### Hub 4 → Hub 2 (OpenHaul)
```cypher
// Loads link to customers
(Load)-[:BOOKED_FOR]->(Customer:Company)
(Load)-[:CONTACT_PERSON]->(Person)

// Carriers link to companies
(Carrier)-[:MANAGED_BY]->(Person)
(Carrier)-[:COMPANY_ENTITY]->(Company)

// Locations link to companies
(Location)-[:BELONGS_TO]->(Company)
(Location)-[:PRIMARY_CONTACT]->(Person)
```

### Hub 4 → Hub 3 (Origin)
```cypher
// Drivers are people
(Driver)-[:PERSON_RECORD]->(Person)  // Operational in Hub 3, personal in Hub 4
(Person {categories: ["driver"]})-[:DRIVES]->(Tractor)  // Alternative link

// Vendors service trucks
(MaintenanceRecord)-[:PERFORMED_BY]->(Vendor:Company)
(Insurance)-[:PROVIDED_BY]->(Vendor:Company)
```

### Hub 4 → Hub 5 (Financials)
```cypher
// Invoices link to companies
(Invoice)-[:BILLED_TO]->(Customer:Company)
(Invoice)-[:PAID_BY]->(Company)
(Expense)-[:PAID_TO]->(Vendor:Company)

// Payments track company relationships
(Payment)-[:FROM]->(Company)
(Payment)-[:TO]->(Company)
```

### Hub 4 → Hub 6 (Corporate)
```cypher
// Companies are owned by legal entities
(Company)-[:LEGAL_ENTITY]->(LegalEntity)  // Hub 6

// People own legal entities
(Person)-[:OWNS]->(LegalEntity)
(Travis:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)
```

---

## Database Distribution

### Neo4j (Relationship Memory)
**Stores:**
- Person and Company nodes (basic identifying info)
- ALL relationships (person → company, person → person, company → company)
- Cross-hub relationships (person → load, company → invoice, person → tractor)
- Multi-category relationships (company has many category labels)

**Why:** Graph traversal - "Show all customers who are also vendors", "Find all people at Sun-Glo", "Map G's business network"

---

### PostgreSQL (Factual Memory)
**Stores:**
- Complete person profiles (contact info, preferences, employment)
- Complete company profiles (credit rating, payment terms, industry)
- Communication log entries
- Contract metadata
- Business card scans metadata

**Why:** Structured queries - "List all contacts with birthdays this month", "Companies with credit rating below B", "Communication history for customer"

---

### Qdrant (Semantic Memory)
**Stores:**
- Communication log embeddings (email summaries, highlights)
- Company notes/descriptions embeddings
- Person preferences/notes embeddings
- Contract document embeddings

**Why:** Semantic search - "Find similar customers to Sun-Glo", "Search communications mentioning pricing issues", "Find vendors with capabilities X"

---

### Redis (Working Memory)
**Stores:**
- Recent communication (last 7 days) for quick access
- Active customer list (for dispatch/sales)
- Preferred vendor list (for maintenance lookups)

**Why:** Fast access for operations - "Who did we talk to today?", "Quick vendor lookup for truck repair"

---

### Graphiti (Temporal Memory)
**Stores:**
- Relationship evolution (customer since 2019, vendor added in 2021)
- Communication pattern tracking (frequency, sentiment trends)
- Person employment history (Shannon moved from Company A to Sun-Glo in 2020)
- Company category changes (became vendor AND customer)

**Why:** Temporal queries - "When did Sun-Glo become a customer?", "How has communication frequency changed?", "Track relationship strength over time"

---

## Primary Keys & Cross-Database Identity

**Person Entity:**
```python
# Neo4j
(:Person {person_id: "person_shannon", name: "Shannon", employer: "Sun-Glo"})

# PostgreSQL
SELECT * FROM people WHERE person_id = 'person_shannon'

# Qdrant
filter={"person_id": "person_shannon"}

# Graphiti
Person(person_id="person_shannon", name="Shannon", ...)
```

**Company Entity:**
```python
# Neo4j
(:Company {company_id: "company_sunglo", name: "Sun-Glo", categories: ["customer"]})

# PostgreSQL
SELECT * FROM companies WHERE company_id = 'company_sunglo'

# Qdrant
filter={"company_id": "company_sunglo"}

# Graphiti
Company(company_id="company_sunglo", name="Sun-Glo", ...)
```

---

## Employee Dual-Tracking Pattern

**Origin Drivers:**
```cypher
// Hub 3 (Origin) - Operational Data
(Driver {
    driver_id: "driver_robert",
    name: "Robert McCullough",
    cdl_number: "NV-123456",
    current_unit: "6520",
    status: "active",
    ytd_miles: 125000,
    safety_rating: 5
})

// Hub 4 (Contacts) - Personal Data
(Person {
    person_id: "person_robert",
    first_name: "Robert",
    last_name: "McCullough",
    birthday: "1978-04-15",
    phone: "702-555-0188",
    categories: ["employee", "driver"],
    employer_company_id: "company_origin"
})

// Link between hubs
(Driver {driver_id: "driver_robert"})-[:PERSON_RECORD]->(Person {person_id: "person_robert"})
```

**Office Staff:**
```cypher
// Primarily in Hub 4 (less operational tracking)
(Person {
    person_id: "person_dispatcher",
    first_name: "Sarah",
    last_name: "Johnson",
    categories: ["employee"],
    employer_company_id: "company_openhaul",
    job_title: "Dispatcher",
    birthday: "1985-06-22"
})
```

---

## Multi-Category Pattern

**Company with Multiple Categories:**
```cypher
// Sun-Glo is ONLY a customer
(SunGlo:Company {
    company_id: "company_sunglo",
    categories: ["customer"]
})

// Origin is carrier, vendor, AND customer to OpenHaul
(Origin:Company {
    company_id: "company_origin",
    categories: ["carrier", "vendor", "customer"]
})

// Relationships reflect categories
(Origin)-[:VENDOR_OF]->(OpenHaul)      // Origin maintains OpenHaul's trucks
(Origin)-[:CUSTOMER_OF]->(OpenHaul)    // Origin uses OpenHaul for brokerage
(Origin)-[:CARRIER_FOR]->(OpenHaul)    // Origin hauls OpenHaul loads
```

---

## TODO - Information Needed

### Missing Details
- [ ] **Complete Category List:** All possible person categories (employee, partner, driver, customer-contact, vendor-contact, personal, friend, family, etc.)
- [ ] **Complete Company Categories:** All possible company categories (customer, vendor, carrier, shipper, receiver, broker, competitor, partner, etc.)
- [ ] **Relationship Types:** Full enumeration (business_partner, friend, family, manager, employee, etc.)
- [ ] **Credit Rating System:** Define A/B/C/D criteria
- [ ] **Communication Types:** Complete list (email, phone, text, in-person, meeting, video-call, etc.)
- [ ] **Sentiment Analysis:** How to determine positive/neutral/negative from communication?

### Preferences Schema
- [ ] **What goes in preferences JSON?** (communication style, shipping patterns, billing preferences, product preferences, etc.)
- [ ] **How to build preferences over time?** Manual entry vs AI-extracted from communication?
- [ ] **Preference categories:** Communication, operational, financial, personal

### Document Examples
- [ ] Sample business cards (scanned)
- [ ] Sample vendor contracts
- [ ] Sample customer agreements
- [ ] Sample credit applications
- [ ] Sample email communication (for summary extraction)

### Integration Questions
- [ ] **Driver Sync:** How often to sync operational data (Hub 3) with personal data (Hub 4)?
- [ ] **Communication Import:** How to import emails? Gmail API? Manual upload? Highlights only or full text?
- [ ] **Birthday Reminders:** Should this trigger notifications? (Implementation, not schema - but note)
- [ ] **Relationship Strength Calculation:** Manual rating or calculated from communication frequency/recency/deal size?

### Cross-Hub Clarifications
- [ ] Should vendors in Hub 4 automatically link to Expense payees in Hub 5?
- [ ] Should all Hub 2 Carriers also be Companies in Hub 4?
- [ ] How to handle anonymous/one-time contacts (e.g., random lumper service)?

---

## Next Steps

1. **Review this draft** - Does dual-entity (Person/Company) + multi-category make sense?
2. **Define complete category lists** - All person and company categories
3. **Design preferences structure** - What goes in the preferences JSON?
4. **Clarify employee tracking** - Confirm Hub 3 (operational) + Hub 4 (personal) pattern works
5. **Get document examples** - Business cards, contracts, emails for extraction
6. **Deep dive** - Expand to full detail matching Hub 3 baseline

---

**Draft Created:** November 3, 2025
**Schema Version:** v2.0 (Draft)
**Completion Status:** ~35% (structure defined, category lists needed)
