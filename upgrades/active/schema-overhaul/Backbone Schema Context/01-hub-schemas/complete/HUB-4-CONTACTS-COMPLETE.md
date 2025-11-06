# HUB 4: CONTACTS (CRM)

**Status:** ✅ Complete Baseline - Full Detail Documented
**Purpose:** Relationship management for people and companies across all business contexts
**Primary Key Strategy:** person_id (UUID) for people, company_id (UUID) for companies
**Category System:** ✅ Multi-category support - entities can have multiple roles simultaneously

---

## Purpose

Hub 4 is the central CRM hub managing all relationship data for people and companies. This includes customers, vendors, employees, partners, carriers, brokers, and personal relationships.

**Key Objectives:**
1. **Relationship Intelligence** - Track who knows whom, communication patterns, preferences, relationship strength
2. **Multi-Category Support** - Same entity can be customer AND vendor (Origin = carrier AND customer of OpenHaul)
3. **Cross-Hub Integration** - People/companies link to loads (Hub 2), trucks (Hub 3), invoices (Hub 5), legal entities (Hub 6)
4. **Natural Expansion** - Start simple (contact info), expand over time (preferences, communication history, insights)

**The Multi-Hub Contact Intelligence System:**

Hub 4 doesn't exist in isolation - it's the relationship memory layer that gives identity to all other hubs:

- **Hub 2 Load** booked for Customer → Hub 4 tracks customer relationship, preferences, communication history
- **Hub 3 Truck** serviced by Vendor → Hub 4 tracks vendor performance, payment terms, contact history
- **Hub 5 Invoice** billed to Customer → Hub 4 provides customer credit rating, payment behavior
- **Hub 3 Driver** is Employee → Hub 4 tracks personal info (birthday, contact), Hub 3 tracks operational (performance)

This creates **ONE relationship brain** across 5 databases, not separate contact silos.

---

## Core Entities (5 Entities, 120+ Properties Total)

### 1. **Person** - Individual Contacts

Every person tracked with **complete profile** - identity, employment, preferences, relationships.

**Primary Key:**
- **person_id** (UUID) - `person_shannon`, `person_robert`, `person_travis`

**Core Identity (15 properties):**
- first_name (String) - `Shannon`
- last_name (String) - Required
- preferred_name (String) - Nickname or preferred first name
- email (String) - Primary email address
- phone_mobile (String) - Mobile/cell phone
- phone_work (String) - Work phone
- birthday (Date) - `1985-06-15`
- location_city (String)
- location_state (String)
- location_country (String) - Default `USA`
- timezone (String) - `America/Chicago`
- preferred_contact_method (Enum) - `email`, `text`, `phone`, `in-person`
- categories (Array[String]) - Can have multiple: `["employee", "driver"]`
- relationship_to_g (Enum) - `business_partner`, `employee`, `customer_contact`, `vendor_contact`, `friend`, `family`, `driver`, `carrier_contact`
- active_status (Boolean) - `True` = currently active contact

**Employment/Affiliation (8 properties):**
- employer_company_id (UUID) - Links to Company entity
- employer_company_name (String) - Cached for quick access
- job_title (String) - `Logistics Coordinator`, `Driver`, `Co-Founder`
- role (String) - More specific than title: `Lead Dispatcher`, `Owner-Operator`
- start_date_at_company (Date)
- end_date_at_company (Date) - Nullable (current employee)
- employment_status (Enum) - `active`, `terminated`, `resigned`, `retired`, `contractor`
- direct_manager_id (UUID) - Links to another Person

**Preferences & Intelligence (12 properties):**
- communication_style (Text) - Free-form notes: "Direct communicator, prefers phone for urgent matters"
- preferences (JSON) - Structured preferences (see schema below)
- important_dates (Array[JSON]) - `[{"date": "2025-06-15", "type": "birthday"}, {"date": "2020-03-01", "type": "work_anniversary"}]`
- life_events (Array[JSON]) - `[{"date": "2024-10-15", "event": "Promoted to Director"}]`
- last_contact_date (Date) - Most recent communication
- contact_frequency (String) - `weekly`, `monthly`, `quarterly`, `annually`, `sporadic`
- relationship_strength (Enum) - `weak`, `moderate`, `strong`, `strategic`
- vip_status (Boolean) - High-priority contact
- referral_source (String) - How did we meet? `trade_show`, `referral`, `cold_outreach`, `linkedin`
- notes (Text) - Free-form relationship notes
- tags (Array[String]) - `["decision_maker", "technical_contact", "billing_contact"]`
- social_profiles (JSON) - `{"linkedin": "url", "twitter": "handle"}`

**Temporal Tracking (4 properties):**
- created_at (Timestamp)
- updated_at (Timestamp)
- valid_from (Timestamp) - Bi-temporal
- valid_to (Timestamp) - Bi-temporal (nullable)

**Total Person Properties: 39**

---

**Person Categories (User-Provided + Extended):**

1. **employees** - W-2 employees (office staff, dispatchers, management)
2. **drivers** - CDL drivers (operational data in Hub 3, personal in Hub 4)
3. **VIP** - High-priority contacts (major customers, strategic partners)
4. **carriers** - Owner-operators, carrier company contacts
5. **partner** - Business partners (Travis, strategic partners)
6. **customer-contact** - Point of contact at customer companies
7. **vendor-contact** - Point of contact at vendor companies
8. **broker-contact** - Point of contact at brokerage companies
9. **personal** - Personal relationships (non-business)
10. **friend** - Personal friends
11. **family** - Family members
12. **prospect** - Potential customers/partners not yet active

**Multi-Category Example:**
```python
Person(
    categories=["employee", "driver"]  # Robert is both employee AND driver
)

Person(
    categories=["partner", "VIP"]  # Travis is business partner AND VIP
)
```

---

**Person Examples (Category-Specific):**

```python
# Business Partner (VIP, Partner)
Person(
    person_id="person_travis",
    first_name="Travis",
    last_name="Arave",
    email="travis@origintransport.com",
    phone_mobile="702-555-0123",
    categories=["partner", "VIP", "employee"],
    relationship_to_g="business_partner",
    employer_company_id="company_origin",
    employer_company_name="Origin Transport LLC",
    job_title="Co-Founder",
    start_date_at_company="2015-01-01",
    employment_status="active",
    relationship_strength="strategic",
    vip_status=True,
    communication_style="Direct communicator, phone preferred for urgent matters. Responds within 1-2 hours typically.",
    preferences={
        "communication": {
            "preferred_method": "phone",
            "preferred_time": "morning",
            "response_expectation": "same_day"
        },
        "operational": {
            "decision_maker": True,
            "areas_of_expertise": ["fleet_management", "vendor_relationships"]
        }
    },
    important_dates=[
        {"date": "1980-08-15", "type": "birthday"},
        {"date": "2015-01-01", "type": "work_anniversary"}
    ],
    last_contact_date="2025-11-03",
    contact_frequency="daily"
)

# Customer Contact
Person(
    person_id="person_shannon",
    first_name="Shannon",
    last_name="Martinez",
    email="shannon@sunglo.com",
    phone_mobile="312-555-0199",
    phone_work="312-555-0100",
    categories=["customer-contact"],
    relationship_to_g="customer_contact",
    employer_company_id="company_sunglo",
    employer_company_name="Sun-Glo Corporation",
    job_title="Logistics Coordinator",
    start_date_at_company="2019-03-01",
    employment_status="active",
    relationship_strength="strong",
    vip_status=False,
    communication_style="Prefers email, responds within 24 hours. Books loads on Fridays for Monday pickups typically.",
    preferences={
        "communication": {
            "preferred_method": "email",
            "preferred_time": "afternoon",
            "cc_on_emails": ["manager@sunglo.com"]
        },
        "operational": {
            "typical_ship_day": "Friday",
            "preferred_pickup_time": "morning",
            "preferred_carriers": ["Origin Transport"],
            "typical_shipment_size": "40,000 lbs",
            "typical_route": "Chicago to Dallas"
        }
    },
    important_dates=[
        {"date": "1990-06-15", "type": "birthday"}
    ],
    last_contact_date="2025-11-01",
    contact_frequency="weekly",
    referral_source="trade_show",
    tags=["decision_maker", "booking_contact"]
)

# Driver (Employee)
Person(
    person_id="person_robert",
    first_name="Robert",
    last_name="McCullough",
    email="robert.mccullough@origintransport.com",
    phone_mobile="702-555-0188",
    birthday="1978-04-15",
    categories=["employee", "driver"],
    relationship_to_g="employee",
    employer_company_id="company_origin",
    employer_company_name="Origin Transport LLC",
    job_title="Driver",
    start_date_at_company="2020-03-15",
    employment_status="active",
    relationship_strength="strong",
    communication_style="Text preferred for dispatch. Calls for urgent issues.",
    preferences={
        "communication": {
            "preferred_method": "text",
            "response_expectation": "within_hour"
        },
        "operational": {
            "preferred_routes": ["western_states"],
            "home_time_preference": "every_2_weeks"
        }
    },
    important_dates=[
        {"date": "1978-04-15", "type": "birthday"},
        {"date": "2020-03-15", "type": "work_anniversary"}
    ],
    last_contact_date="2025-11-03",
    contact_frequency="daily"
    # Operational driver data (current_unit: "6520", performance metrics) in Hub 3
)

# Vendor Contact
Person(
    person_id="person_service_manager",
    first_name="Mike",
    last_name="Johnson",
    email="mjohnson@boschservice.com",
    phone_work="702-555-0234",
    categories=["vendor-contact"],
    relationship_to_g="vendor_contact",
    employer_company_id="company_bosch",
    employer_company_name="Bosch Service Center",
    job_title="Service Manager",
    employment_status="active",
    relationship_strength="strong",
    communication_style="Phone preferred. Can get trucks in same-day for emergencies.",
    preferences={
        "communication": {
            "preferred_method": "phone"
        },
        "operational": {
            "emergency_contact": True,
            "after_hours_available": True,
            "specialties": ["brake_service", "tire_service", "PM_maintenance"]
        }
    },
    last_contact_date="2025-11-01",
    contact_frequency="monthly",
    tags=["emergency_contact", "preferred_vendor"]
)

# Carrier Contact (Owner-Operator)
Person(
    person_id="person_oo_driver",
    first_name="John",
    last_name="Smith",
    email="john.smith.trucking@gmail.com",
    phone_mobile="480-555-0167",
    categories=["carrier", "drivers"],
    relationship_to_g="carrier_contact",
    employer_company_id="company_smith_trucking",  # His own authority
    job_title="Owner-Operator",
    relationship_strength="moderate",
    communication_style="Text or call. Books loads last-minute sometimes.",
    preferences={
        "operational": {
            "equipment_type": "dry_van",
            "typical_lanes": ["southwest"],
            "rate_expectations": "$2.50_per_mile",
            "availability": "flexible"
        }
    },
    last_contact_date="2025-10-25",
    contact_frequency="monthly",
    tags=["reliable", "spot_market"]
)
```

---

### 2. **Company** - Organizations

Every company tracked with **complete profile** - identity, financials, operational data, relationship intelligence.

**Primary Key:**
- **company_id** (UUID) - `company_sunglo`, `company_origin`, `company_bosch`

**Core Identity (18 properties):**
- company_name (String) - Legal name: `Sun-Glo Corporation`
- dba_name (String) - Doing Business As (if different from legal)
- industry (String) - `Manufacturing`, `Logistics`, `Automotive Parts`
- website (String) - `https://sunglo.com`
- phone (String) - Main phone number
- email (String) - General contact email
- address_line1 (String)
- address_line2 (String) - Suite/unit
- city (String)
- state (String)
- zip (String)
- country (String) - Default `USA`
- categories (Array[String]) - Can have multiple: `["customer", "vendor"]`
- date_founded (Date)
- company_size (Enum) - `1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1000+`
- ownership_type (Enum) - `private`, `public`, `sole_proprietorship`, `partnership`, `LLC`, `corporation`
- tax_id_last_4 (String) - Last 4 of EIN (security - don't store full)
- active_status (Boolean)

**Financial/Operational (14 properties):**
- credit_rating (Enum) - `A`, `B`, `C`, `D`, `F`, `not_rated`
- payment_terms (String) - `net-30`, `net-15`, `net-60`, `COD`, `quick-pay`
- credit_limit (Decimal) - Maximum outstanding balance allowed
- current_ar_balance (Decimal) - Current accounts receivable balance
- payment_behavior_score (Integer) - 1-100 calculated from payment history
- preferred_vendor (Boolean) - For vendors we prefer to use
- approved_vendor (Boolean) - Passed vetting process
- performance_rating (Integer) - 1-5 stars
- insurance_required (Boolean) - Do they require COI?
- broker_authority (String) - MC number if broker
- carrier_authority (String) - DOT/MC if carrier
- shipper_status (Boolean) - Do they ship freight?
- receiver_status (Boolean) - Do they receive freight?
- factoring_company_id (UUID) - If they use factoring

**Relationship Intelligence (10 properties):**
- primary_contact_person_id (UUID) - Main contact person
- account_manager_person_id (UUID) - Who at Origin/OpenHaul manages this
- relationship_since (Date) - When relationship started
- relationship_strength (Enum) - `weak`, `moderate`, `strong`, `strategic`
- relationship_type (Enum) - `transactional`, `partnership`, `strategic_alliance`
- annual_volume_estimate (Decimal) - Estimated yearly revenue (if customer)
- last_transaction_date (Date) - Most recent business transaction
- communication_frequency (String) - `daily`, `weekly`, `monthly`, `quarterly`
- acquisition_source (String) - How acquired: `referral`, `trade_show`, `cold_outreach`, `linkedin`, `website`
- nps_score (Integer) - Net Promoter Score (if customer): -100 to 100

**Temporal Tracking (2 properties):**
- created_at (Timestamp)
- updated_at (Timestamp)

**Total Company Properties: 44**

---

**Company Categories (User-Provided + Extended):**

1. **Prospect** - Potential customers not yet active
2. **Customer** - Active customers who pay us
3. **Vendor** - Companies we pay for goods/services
4. **Carrier** - Companies that haul freight (for OpenHaul brokerage)
5. **Broker** - Freight brokers
6. **Partner** - Strategic partners
7. **shipper** - Companies that ship freight (load origin points)
8. **receiver** - Companies that receive freight (load destination points)
9. **competitor** - Competing companies
10. **factoring_company** - Invoice factoring services (Triumph)

**Multi-Category Example:**
```python
Company(
    categories=["carrier", "vendor", "customer"]  # Origin is carrier, vendor, AND customer to OpenHaul
)

Company(
    categories=["customer", "shipper", "receiver"]  # Sun-Glo is customer, ships freight, receives freight
)
```

---

**Company Examples (Category-Specific):**

```python
# Customer (Active)
Company(
    company_id="company_sunglo",
    company_name="Sun-Glo Corporation",
    industry="Manufacturing",
    website="https://sunglo.com",
    phone="312-555-0100",
    email="logistics@sunglo.com",
    address_line1="1234 Industrial Blvd",
    city="Chicago",
    state="IL",
    zip="60601",
    country="USA",
    categories=["customer", "shipper", "receiver"],
    date_founded="1995-06-01",
    company_size="201-500",
    ownership_type="private",
    credit_rating="A",
    payment_terms="net-30",
    credit_limit=50000.00,
    current_ar_balance=2525.00,
    payment_behavior_score=95,  # Excellent payment history
    insurance_required=True,
    shipper_status=True,
    receiver_status=True,
    primary_contact_person_id="person_shannon",
    account_manager_person_id="person_g",  # G manages this account
    relationship_since="2019-03-01",
    relationship_strength="strong",
    relationship_type="partnership",
    annual_volume_estimate=500000.00,  # $500k/year
    last_transaction_date="2025-11-03",
    communication_frequency="weekly",
    acquisition_source="trade_show",
    nps_score=85,  # Promoter
    active_status=True
)

# Vendor (Preferred)
Company(
    company_id="company_bosch",
    company_name="Bosch Automotive Service Solutions",
    industry="Automotive Parts & Service",
    website="https://boschservice.com",
    phone="702-555-0200",
    email="service@boschservice.com",
    address_line1="5678 Service Rd",
    city="Las Vegas",
    state="NV",
    zip="89101",
    categories=["vendor"],
    company_size="51-200",
    ownership_type="corporation",
    payment_terms="net-15",
    preferred_vendor=True,
    approved_vendor=True,
    performance_rating=5,  # Excellent service
    primary_contact_person_id="person_service_manager",
    account_manager_person_id="person_travis",
    relationship_since="2016-08-01",
    relationship_strength="strong",
    last_transaction_date="2025-11-01",
    communication_frequency="monthly",
    acquisition_source="referral",
    active_status=True
)

# Multi-Category: Origin (Carrier, Vendor, Customer to OpenHaul)
Company(
    company_id="company_origin",
    company_name="Origin Transport LLC",
    industry="Trucking",
    website="https://origintransport.com",
    phone="702-555-0300",
    categories=["carrier", "vendor", "customer"],  # Multi-category!
    carrier_authority="DOT-789012, MC-654321",
    relationship_to_g="owned_company",  # Special relationship
    owner_entity_id="entity_primetime",  # Links to Hub 6
    relationship_since="2015-01-01",
    active_status=True
)

# Multi-Category: OpenHaul (Broker, Customer, Vendor to Origin)
Company(
    company_id="company_openhaul",
    company_name="OpenHaul LLC",
    industry="Freight Brokerage",
    website="https://openhaul.com",
    phone="702-555-0400",
    categories=["broker", "customer", "vendor"],  # Multi-category!
    broker_authority="MC-987654",
    relationship_to_g="owned_company",
    owner_entity_id="entity_primetime",  # Links to Hub 6
    relationship_since="2019-01-01",
    active_status=True
)

# Factoring Company
Company(
    company_id="company_triumph",
    company_name="Triumph Business Capital",
    industry="Financial Services",
    website="https://triumphcapital.com",
    categories=["factoring_company", "vendor"],
    payment_terms="advance",  # Immediate advance
    relationship_since="2020-06-01",
    relationship_strength="moderate",
    active_status=True
)

# Carrier (for OpenHaul brokerage)
Company(
    company_id="company_carrier_abc",
    company_name="ABC Trucking LLC",
    industry="Trucking",
    categories=["carrier"],
    carrier_authority="DOT-123456, MC-789012",
    insurance_required=True,
    performance_rating=4,
    primary_contact_person_id="person_carrier_dispatcher",
    relationship_since="2021-03-15",
    relationship_strength="moderate",
    last_transaction_date="2025-10-20",
    communication_frequency="weekly",
    active_status=True
)

# Prospect (Not Yet Customer)
Company(
    company_id="company_prospect_xyz",
    company_name="XYZ Manufacturing Inc",
    industry="Manufacturing",
    website="https://xyzmanufacturing.com",
    categories=["prospect"],
    shipper_status=True,
    acquisition_source="linkedin",
    relationship_since="2025-09-15",
    relationship_strength="weak",
    communication_frequency="monthly",
    active_status=True
)
```

---

### 3. **CommunicationLog** - Interaction History

Track communication with people/companies over time. Focus on **highlights and action items**, not full email text.

**Primary Key:**
- **communication_id** (UUID)

**Core Properties (20 properties):**
- person_id (UUID) - If communicating with person
- company_id (UUID) - If communicating with company (can have both)
- communication_type (Enum) - `email`, `phone`, `text`, `in-person`, `meeting`, `video_call`
- date (Date)
- time (Time)
- duration_minutes (Integer) - For calls/meetings
- direction (Enum) - `inbound`, `outbound`, `bidirectional` (meeting)
- initiated_by_person_id (UUID) - Who started the communication
- subject (String) - Email subject or call/meeting topic
- summary (Text) - AI-extracted or manual highlights (NOT full email text)
- key_points (Array[String]) - Bullet points of key discussion items
- decisions_made (Array[String]) - Any decisions reached
- action_items (Array[JSON]) - `[{"item": "Book carrier by Wed", "assigned_to": "person_g", "due_date": "2025-11-06"}]`
- sentiment (Enum) - `positive`, `neutral`, `negative`, `mixed`
- sentiment_score (Integer) - -100 to 100
- related_entities (JSON) - `{"load_number": "OH-321678", "unit_number": "6520", "invoice_id": "inv_001"}`
- document_path (String) - Path to full email/document if archived
- next_followup_date (Date)
- created_at (Timestamp)
- updated_at (Timestamp)

**Examples:**

```python
# Customer Email (Load Booking)
CommunicationLog(
    communication_id="comm_001",
    person_id="person_shannon",
    company_id="company_sunglo",
    communication_type="email",
    date="2025-11-01",
    time="14:30:00",
    direction="inbound",
    initiated_by_person_id="person_shannon",
    subject="Weekly load request - Chicago to Dallas",
    summary="Shannon requesting Friday pickup for 40,000 lbs general freight. Standard Chicago to Dallas route. Rate discussion - Shannon initially requested $2,300, holding at $2,500. Needs carrier confirmation by Wednesday.",
    key_points=[
        "40,000 lbs general freight",
        "Chicago pickup Friday morning",
        "Dallas delivery Monday",
        "Rate agreed: $2,500",
        "Carrier confirmation needed by Wed"
    ],
    decisions_made=[
        "Rate confirmed at $2,500",
        "Pickup window: Friday 8am-10am"
    ],
    action_items=[
        {
            "item": "Book carrier by Wednesday",
            "assigned_to": "person_g",
            "due_date": "2025-11-06"
        },
        {
            "item": "Send rate confirmation to Shannon",
            "assigned_to": "person_g",
            "due_date": "2025-11-01"
        }
    ],
    sentiment="positive",
    sentiment_score=80,
    related_entities={
        "load_number": "OH-321678"
    },
    next_followup_date="2025-11-06"
)

# Vendor Phone Call (Emergency Service)
CommunicationLog(
    communication_id="comm_002",
    person_id="person_service_manager",
    company_id="company_bosch",
    communication_type="phone",
    date="2025-11-01",
    time="08:15:00",
    duration_minutes=10,
    direction="outbound",
    initiated_by_person_id="person_travis",
    subject="Emergency brake service for Unit #6520",
    summary="Travis called Mike at Bosch for emergency brake service. Unit #6520 failed pre-trip inspection. Mike confirmed can take truck same-day at 10am. Estimated 4-6 hours for complete brake overhaul. Estimated cost $3,200 plus parts.",
    key_points=[
        "Emergency brake service needed",
        "Unit #6520 failed pre-trip",
        "Same-day service available at 10am",
        "4-6 hour repair time",
        "Estimated $3,200 plus parts"
    ],
    decisions_made=[
        "Drop truck at Bosch at 10am",
        "Reassign loads to Unit #6525"
    ],
    action_items=[
        {
            "item": "Drop Unit #6520 at Bosch at 10am",
            "assigned_to": "person_robert",
            "due_date": "2025-11-01"
        }
    ],
    sentiment="neutral",
    related_entities={
        "unit_number": "6520",
        "maintenance_record_id": "maint_001"
    }
)

# Partner Meeting (Strategic Planning)
CommunicationLog(
    communication_id="comm_003",
    person_id="person_travis",
    company_id="company_origin",
    communication_type="meeting",
    date="2025-11-01",
    time="09:00:00",
    duration_minutes=60,
    direction="bidirectional",
    subject="Q4 Fleet Expansion Planning",
    summary="G and Travis discussed Q4 fleet expansion strategy. Reviewed performance of existing 18 units. Decision to add 3 new trucks in Q1 2026. Budget approved: $360k. Focus on newer model Kenworth T680s with better fuel economy.",
    key_points=[
        "Current fleet performance strong",
        "Q1 2026 expansion: 3 new trucks",
        "Budget: $360k ($120k per truck)",
        "Target: Kenworth T680 2024+ models",
        "Financing: 5-year terms at ~6% APR"
    ],
    decisions_made=[
        "Add 3 trucks in Q1 2026",
        "Budget approved: $360k",
        "Travis to lead truck sourcing"
    ],
    action_items=[
        {
            "item": "Research truck dealers and pricing",
            "assigned_to": "person_travis",
            "due_date": "2025-11-15"
        },
        {
            "item": "Get financing pre-approval",
            "assigned_to": "person_g",
            "due_date": "2025-11-20"
        },
        {
            "item": "Hire 3 new drivers",
            "assigned_to": "person_travis",
            "due_date": "2026-01-15"
        }
    ],
    sentiment="positive",
    sentiment_score=90,
    related_entities={
        "project_id": "project_fleet_expansion"
    },
    next_followup_date="2025-11-15"
)
```

---

### 4. **Contract** - Agreements with Companies

Legal agreements with vendors, customers, carriers.

**Primary Key:**
- **contract_id** (UUID)

**Core Properties (15 properties):**
- company_id (UUID) - Which company contract is with
- company_name (String) - Cached
- contract_type (Enum) - `vendor_agreement`, `customer_contract`, `carrier_agreement`, `service_agreement`, `NDA`, `lease_agreement`, `employment_contract`
- contract_number (String) - Internal contract number
- start_date (Date)
- end_date (Date) - Nullable if indefinite
- term_length_months (Integer)
- auto_renewal (Boolean)
- renewal_terms (String) - `30_day_notice`, `60_day_notice`, `annual_review`
- notice_period_days (Integer) - Days required for termination notice
- document_path (String) - PDF location in Qdrant
- key_terms (JSON) - Important contract provisions (see schema below)
- annual_value (Decimal) - Estimated annual contract value
- status (Enum) - `draft`, `active`, `expired`, `terminated`, `renewed`
- created_at (Timestamp)

**Examples:**

```python
# Customer Service Agreement (Sun-Glo)
Contract(
    contract_id="contract_sunglo_001",
    company_id="company_sunglo",
    company_name="Sun-Glo Corporation",
    contract_type="customer_contract",
    contract_number="CUST-2019-001",
    start_date="2019-03-01",
    end_date="2026-02-28",  # 7-year term
    term_length_months=84,
    auto_renewal=True,
    renewal_terms="60_day_notice",
    notice_period_days=60,
    document_path="qdrant://contracts/sun-glo-service-agreement-2019.pdf",
    key_terms={
        "service_level": "Standard brokerage services",
        "payment_terms": "net-30",
        "rate_structure": "Per-load negotiated rates",
        "volume_commitment": "Minimum 100 loads per year",
        "termination_clause": "60 days written notice",
        "liability_limits": "$1M cargo insurance required",
        "dispute_resolution": "Binding arbitration in Nevada"
    },
    annual_value=500000.00,
    status="active"
)

# Vendor Service Agreement (Bosch)
Contract(
    contract_id="contract_bosch_001",
    company_id="company_bosch",
    company_name="Bosch Service Center",
    contract_type="vendor_agreement",
    contract_number="VEND-2020-003",
    start_date="2020-06-01",
    end_date=None,  # Indefinite
    auto_renewal=False,
    notice_period_days=30,
    document_path="qdrant://contracts/bosch-service-agreement-2020.pdf",
    key_terms={
        "services_provided": "Fleet maintenance, tire service, PM, emergency repairs",
        "payment_terms": "net-15",
        "rate_structure": "Posted rates, 10% fleet discount",
        "emergency_service": "Same-day service for emergency repairs",
        "warranty": "90 days on parts, 60 days on labor",
        "termination_clause": "30 days written notice"
    },
    annual_value=85000.00,  # Estimated annual spend
    status="active"
)

# Factoring Agreement (Triumph)
Contract(
    contract_id="contract_triumph_001",
    company_id="company_triumph",
    company_name="Triumph Business Capital",
    contract_type="service_agreement",
    contract_number="FACT-2020-001",
    start_date="2020-06-01",
    end_date="2025-05-31",
    term_length_months=60,
    auto_renewal=True,
    renewal_terms="30_day_notice",
    notice_period_days=30,
    document_path="qdrant://contracts/triumph-factoring-agreement-2020.pdf",
    key_terms={
        "service": "Invoice factoring",
        "advance_rate": "95%",
        "factoring_fee": "2.5% per invoice",
        "recourse": "Non-recourse",
        "customer_notification": "Not required",
        "minimum_volume": "None",
        "termination_clause": "30 days written notice, settle all outstanding invoices"
    },
    annual_value=0,  # Fee-based, not fixed value
    status="active"
)

# NDA (Prospect)
Contract(
    contract_id="contract_nda_xyz_001",
    company_id="company_prospect_xyz",
    company_name="XYZ Manufacturing Inc",
    contract_type="NDA",
    contract_number="NDA-2025-012",
    start_date="2025-09-15",
    end_date="2027-09-14",  # 2-year NDA
    term_length_months=24,
    auto_renewal=False,
    document_path="qdrant://contracts/nda-xyz-manufacturing-2025.pdf",
    key_terms={
        "scope": "Mutual NDA",
        "purpose": "Explore freight services partnership",
        "confidential_info": "Pricing, shipping volumes, operational details",
        "termination": "2 years from signing",
        "return_of_materials": "Required upon termination"
    },
    status="active"
)
```

---

### 5. **BusinessCard** - Physical/Digital Cards

Track business cards received from networking.

**Primary Key:**
- **card_id** (UUID)

**Core Properties (10 properties):**
- person_id (UUID) - Who the card belongs to
- company_id (UUID) - Their company
- date_received (Date)
- source (String) - `trade_show`, `networking_event`, `cold_call`, `meeting`, `mail`
- source_detail (String) - Specific event name or location
- document_path (String) - Scan/photo of card
- card_type (Enum) - `physical`, `digital`, `vcard`
- followup_needed (Boolean)
- followup_date (Date)
- notes (Text)

**Example:**

```python
BusinessCard(
    card_id="card_001",
    person_id="person_shannon",
    company_id="company_sunglo",
    date_received="2019-02-15",
    source="trade_show",
    source_detail="Mid-America Trucking Show 2019 - Louisville, KY",
    document_path="qdrant://business-cards/shannon-martinez-sun-glo-2019.jpg",
    card_type="physical",
    followup_needed=False,  # Already contacted
    notes="Met at MATS 2019. Very interested in regular Chicago-Dallas lanes. Became customer 2 weeks later."
)
```

---

## Preferences JSON Structure

**Standard structure for Person and Company preferences:**

### Person Preferences Schema

```json
{
  "communication": {
    "preferred_method": "email | phone | text | in-person",
    "preferred_time": "morning | afternoon | evening | flexible",
    "response_expectation": "immediate | within_hour | same_day | 24_hours | flexible",
    "cc_on_emails": ["email1@example.com", "email2@example.com"],
    "call_before_text": true | false
  },
  "operational": {
    "decision_maker": true | false,
    "areas_of_expertise": ["area1", "area2"],
    "typical_ship_day": "Monday | Tuesday | ... | Friday | varies",
    "preferred_pickup_time": "morning | afternoon | evening | flexible",
    "preferred_carriers": ["Origin Transport", "ABC Trucking"],
    "typical_shipment_size": "20,000 lbs | 40,000 lbs | varies",
    "typical_route": "Chicago to Dallas | varies",
    "special_requirements": []
  },
  "financial": {
    "budget_authority": true | false,
    "approval_threshold": 10000.00,
    "preferred_payment_method": "ACH | check | wire | credit_card"
  },
  "personal": {
    "interests": ["golf", "fishing", "family"],
    "conversation_topics": ["sports", "family", "industry_news"],
    "dietary_restrictions": ["vegetarian", "gluten-free"],
    "travel_preferences": {}
  }
}
```

### Company Preferences Schema

```json
{
  "communication": {
    "primary_method": "email | phone | portal",
    "invoicing_method": "email | portal | mail",
    "invoice_recipients": ["email1@example.com", "email2@example.com"]
  },
  "operational": {
    "shipping_instructions": "Call before delivery | Drop and hook | Live load/unload",
    "typical_ship_days": ["Monday", "Friday"],
    "preferred_carriers": ["Origin Transport"],
    "equipment_requirements": ["dry_van", "reefer", "flatbed"],
    "special_handling": ["fragile", "temperature_sensitive"],
    "dock_hours": "8am-5pm Monday-Friday",
    "appointment_required": true | false
  },
  "financial": {
    "payment_method": "ACH | check | wire | factoring",
    "remittance_email": "ap@example.com",
    "purchase_order_required": true | false,
    "tax_exempt": true | false,
    "tax_exempt_states": ["TX", "CA"]
  },
  "compliance": {
    "insurance_requirements": {
      "cargo": 100000,
      "liability": 1000000,
      "auto": 1000000
    },
    "coi_required": true | false,
    "broker_packet_required": true | false
  }
}
```

---

## Primary Relationships

### Person ↔ Company

```cypher
// Employment
(Shannon:Person {person_id: "person_shannon"})-[:WORKS_FOR {
    role: "Logistics Coordinator",
    start_date: "2019-03-01",
    employment_status: "active"
}]->(SunGlo:Company {company_id: "company_sunglo"})

(Travis:Person)-[:WORKS_FOR {role: "Co-Founder"}]->(Origin:Company)
(Robert:Person)-[:WORKS_FOR {role: "Driver"}]->(Origin:Company)

// Ownership (Links to Hub 6)
(Travis:Person)-[:OWNS {percentage: 50, since: "2019-01-01"}]->(OpenHaul:Company)
(G:Person)-[:OWNS {percentage: 50, since: "2019-01-01"}]->(OpenHaul:Company)

// Primary Contact
(Shannon:Person)-[:PRIMARY_CONTACT_FOR]->(SunGlo:Company)

// Account Management
(G:Person)-[:ACCOUNT_MANAGER_FOR {since: "2019-03-01"}]->(SunGlo:Company)
(Travis:Person)-[:ACCOUNT_MANAGER_FOR]->(Bosch:Company)
```

### Person ↔ Person

```cypher
// Business relationships
(G:Person)-[:BUSINESS_PARTNER_WITH {since: "2015-01-01"}]->(Travis:Person)
(Travis:Person)-[:BUSINESS_PARTNER_WITH]->(G:Person)  // Bidirectional

// Management hierarchy
(Travis:Person)-[:MANAGES]->(Robert:Person)
(Robert:Person)-[:REPORTS_TO]->(Travis:Person)

// Personal relationships
(G:Person)-[:FRIEND_OF]->(Person)
(G:Person)-[:FAMILY_MEMBER {relationship: "spouse"}]->(Person)

// Professional network
(G:Person)-[:INTRODUCED_BY {date: "2019-02-15"}]->(Travis:Person)-[:INTRODUCED]->(Shannon:Person)
```

### Company ↔ Company

```cypher
// Customer/Vendor Relationships
(Origin:Company)-[:VENDOR_OF {service: "maintenance", since: "2020-06-01"}]->(OpenHaul:Company)
(Origin:Company)-[:CUSTOMER_OF {since: "2019-01-01"}]->(OpenHaul:Company)
(OpenHaul:Company)-[:CUSTOMER_OF]->(Origin:Company)

// Carrier Relationships
(Origin:Company)-[:CARRIER_FOR {since: "2019-01-01"}]->(OpenHaul:Company)
(ABCTrucking:Company)-[:CARRIER_FOR]->(OpenHaul:Company)

// Industry Relationships
(Origin:Company)-[:COMPETITOR_OF]->(XYZTrucking:Company)
(OpenHaul:Company)-[:PARTNER_WITH {type: "strategic_alliance"}]->(PartnerBroker:Company)

// Factoring Relationships
(OpenHaul:Company)-[:USES_FACTORING]->(Triumph:Company)
```

### Communication Links

```cypher
// Communication to person/company
(CommunicationLog)-[:WITH_PERSON]->(Person)
(CommunicationLog)-[:WITH_COMPANY]->(Company)
(CommunicationLog)-[:INITIATED_BY]->(Person)

// Communication references entities
(CommunicationLog)-[:REGARDING]->(Load)
(CommunicationLog)-[:REGARDING]->(Tractor)
(CommunicationLog)-[:REGARDING]->(Invoice)
```

### Contract Links

```cypher
// Contract parties
(Contract)-[:WITH_COMPANY]->(Company)
(Contract)-[:MANAGED_BY]->(Person)  // Account manager

// Contract references
(Contract)-[:GOVERNS]->(Transaction)
(Contract)-[:APPLIES_TO]->(ServiceType)
```

---

## Cross-Hub Relationships

### Hub 4 → Hub 1 (G Command)

```cypher
// G's personal network
(G:Person)-[:KNOWS]->(Person)
(G:Person)-[:RELATIONSHIP_WITH {type: "business_partner"}]->(Travis:Person)

// Projects involve companies
(Project {project_id: "project_fleet_expansion"})-[:INVOLVES]->(Origin:Company)
(Project)-[:KEY_CONTACT]->(Travis:Person)

// Goals track relationships
(Goal {title: "Grow Sun-Glo to $1M annual"})-[:MEASURED_BY]->(SunGlo:Company)

// Insights about people/companies
(Insight {content: "Sun-Glo ships more in Q4"})-[:ABOUT]->(SunGlo:Company)
```

---

### Hub 4 → Hub 2 (OpenHaul)

```cypher
// Loads linked to customers
(Load {load_number: "OH-321678"})-[:BOOKED_FOR]->(Customer:Company {company_id: "company_sunglo"})
(Load)-[:CONTACT_PERSON]->(Shannon:Person)

// Carriers linked to companies
(Carrier {carrier_id: "carr_origin"})-[:COMPANY_ENTITY]->(Origin:Company)
(Carrier)-[:PRIMARY_CONTACT]->(Person)

// Locations belong to companies
(Location {location_id: "loc_sunglo_chicago"})-[:BELONGS_TO]->(SunGlo:Company)
(Location)-[:PRIMARY_CONTACT]->(Shannon:Person)
(Location)-[:SHIPPING_CONTACT]->(Person)

// Factor relationship
(Invoice)-[:FACTORED_BY]->(Triumph:Company)
```

---

### Hub 4 → Hub 3 (Origin)

```cypher
// Drivers are people
(Driver {driver_id: "driver_robert"})-[:PERSON_RECORD]->(Person {person_id: "person_robert"})

// Maintenance vendors
(MaintenanceRecord)-[:PERFORMED_BY]->(Vendor:Company {company_id: "company_bosch"})
(MaintenanceRecord)-[:CONTACT_PERSON]->(Person {person_id: "person_service_manager"})

// Insurance providers
(Insurance)-[:PROVIDED_BY]->(Vendor:Company)
(Insurance)-[:AGENT_CONTACT]->(Person)

// Fuel vendors
(FuelTransaction)-[:PURCHASED_FROM]->(Vendor:Company {company_id: "company_fleetone"})
```

---

### Hub 4 → Hub 5 (Financials)

```cypher
// Invoices link to companies and people
(Invoice {type: "customer"})-[:BILLED_TO]->(Customer:Company)
(Invoice)-[:BILLED_TO_ATTENTION]->(Person)  // Shannon at Sun-Glo
(Invoice {type: "vendor"})-[:RECEIVED_FROM]->(Vendor:Company)

// Expenses paid to vendors
(Expense)-[:PAID_TO]->(Vendor:Company)

// Revenue from customers
(Revenue)-[:RECEIVED_FROM]->(Customer:Company)

// Payments between companies
(Payment)-[:FROM]->(Company)
(Payment)-[:TO]->(Company)

// Loans from banks
(Loan)-[:FROM_LENDER]->(Bank:Company)
(Loan)-[:CONTACT_PERSON]->(Person)

// Credit behavior tracking
(Company)-[:PAYMENT_BEHAVIOR {
    average_days_to_pay: 18,
    on_time_percentage: 95,
    payment_behavior_score: 95
}]
```

---

### Hub 4 → Hub 6 (Corporate)

```cypher
// Companies are owned by legal entities
(Company {company_id: "company_origin"})-[:LEGAL_ENTITY]->(LegalEntity {entity_id: "entity_origin"})
(Company {company_id: "company_openhaul"})-[:LEGAL_ENTITY]->(LegalEntity {entity_id: "entity_openhaul"})

// People own legal entities
(Travis:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)
(G:Person)-[:OWNS {percentage: 100}]->(Primetime:LegalEntity)

// Licenses reference companies
(License {license_type: "DOT"})-[:ISSUED_TO]->(Origin:Company)
(License)-[:CONTACT_PERSON]->(Person)
```

---

## Database Distribution

### Neo4j (Relationship Memory)

**Stores:**
- Person and Company nodes (lightweight - basic identifying info only)
- ALL relationships:
  - Person → Company (employment, ownership, contacts)
  - Person → Person (business partners, management hierarchy, referrals)
  - Company → Company (customer/vendor, carrier, competitor, partner)
  - Person/Company → CommunicationLog
  - Person/Company → Contract
- Cross-hub relationships:
  - Person/Company → Load (Hub 2)
  - Person/Company → Invoice (Hub 5)
  - Person → Driver (Hub 3)
  - Company → LegalEntity (Hub 6)
- Multi-category support (company has multiple category labels)

**Why:**
- Graph traversal queries:
  - "Show all people at Sun-Glo"
  - "Find all customers who are also vendors"
  - "Map G's business network"
  - "Show all communication with Shannon"
  - "Find vendors servicing Unit #6520"
- Relationship pattern detection:
  - Vendor concentration (one vendor services 80% of fleet)
  - Customer dependency (one customer = 40% of revenue)
  - Network effects (Shannon referred 3 other customers)

**Node Properties (Minimal):**
```cypher
(:Person {
    person_id: "person_shannon",
    first_name: "Shannon",
    last_name: "Martinez",
    categories: ["customer-contact"],
    active_status: true
})

(:Company {
    company_id: "company_sunglo",
    company_name: "Sun-Glo Corporation",
    categories: ["customer", "shipper", "receiver"],
    active_status: true
})
```

---

### PostgreSQL (Factual Memory)

**Stores:**
- **Complete person profiles** (all 39 properties)
- **Complete company profiles** (all 44 properties)
- **Communication log entries** (all 20 properties)
- **Contract records** (all 15 properties)
- **Business card scans metadata** (all 10 properties)

**Why:**
- Structured queries:
  - "List all contacts with birthdays this month"
  - "Companies with credit rating below B"
  - "Communication history for Sun-Glo (last 90 days)"
  - "All active employees sorted by hire date"
  - "Contracts expiring in next 60 days"
- Aggregations:
  - Count people by category
  - Average payment behavior score by industry
  - Communication frequency by company
- Filtering:
  - WHERE credit_rating = 'A'
  - WHERE payment_terms = 'net-30'
  - WHERE categories CONTAINS 'customer'
  - WHERE relationship_strength = 'strong'

**Schema Example (PostgreSQL):**
```sql
CREATE TABLE people (
    person_id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    preferred_name VARCHAR(100),
    email VARCHAR(255),
    phone_mobile VARCHAR(20),
    phone_work VARCHAR(20),
    birthday DATE,
    location_city VARCHAR(100),
    location_state VARCHAR(50),
    location_country VARCHAR(50) DEFAULT 'USA',
    timezone VARCHAR(50),
    preferred_contact_method VARCHAR(20),
    categories TEXT[],  -- Array of categories
    relationship_to_g VARCHAR(50),
    active_status BOOLEAN DEFAULT TRUE,
    employer_company_id UUID,
    employer_company_name VARCHAR(255),
    job_title VARCHAR(100),
    role VARCHAR(100),
    start_date_at_company DATE,
    end_date_at_company DATE,
    employment_status VARCHAR(20),
    direct_manager_id UUID,
    communication_style TEXT,
    preferences JSONB,  -- Structured preferences
    important_dates JSONB,  -- Array of date objects
    life_events JSONB,  -- Array of event objects
    last_contact_date DATE,
    contact_frequency VARCHAR(20),
    relationship_strength VARCHAR(20),
    vip_status BOOLEAN DEFAULT FALSE,
    referral_source VARCHAR(100),
    notes TEXT,
    tags TEXT[],
    social_profiles JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    valid_from TIMESTAMP DEFAULT NOW(),
    valid_to TIMESTAMP
);

CREATE INDEX idx_people_categories ON people USING GIN(categories);
CREATE INDEX idx_people_employer ON people(employer_company_id);
CREATE INDEX idx_people_relationship_to_g ON people(relationship_to_g);
CREATE INDEX idx_people_active ON people(active_status);
CREATE INDEX idx_people_birthday_month ON people(EXTRACT(MONTH FROM birthday));

CREATE TABLE companies (
    company_id UUID PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    dba_name VARCHAR(255),
    industry VARCHAR(100),
    website VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    country VARCHAR(50) DEFAULT 'USA',
    categories TEXT[],
    date_founded DATE,
    company_size VARCHAR(20),
    ownership_type VARCHAR(50),
    tax_id_last_4 VARCHAR(4),
    active_status BOOLEAN DEFAULT TRUE,
    credit_rating VARCHAR(10),
    payment_terms VARCHAR(50),
    credit_limit NUMERIC(12, 2),
    current_ar_balance NUMERIC(12, 2) DEFAULT 0,
    payment_behavior_score INTEGER,
    preferred_vendor BOOLEAN DEFAULT FALSE,
    approved_vendor BOOLEAN DEFAULT FALSE,
    performance_rating INTEGER,
    insurance_required BOOLEAN DEFAULT FALSE,
    broker_authority VARCHAR(50),
    carrier_authority VARCHAR(50),
    shipper_status BOOLEAN DEFAULT FALSE,
    receiver_status BOOLEAN DEFAULT FALSE,
    factoring_company_id UUID,
    primary_contact_person_id UUID,
    account_manager_person_id UUID,
    relationship_since DATE,
    relationship_strength VARCHAR(20),
    relationship_type VARCHAR(50),
    annual_volume_estimate NUMERIC(12, 2),
    last_transaction_date DATE,
    communication_frequency VARCHAR(20),
    acquisition_source VARCHAR(100),
    nps_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_companies_categories ON companies USING GIN(categories);
CREATE INDEX idx_companies_credit_rating ON companies(credit_rating);
CREATE INDEX idx_companies_active ON companies(active_status);
CREATE INDEX idx_companies_relationship_strength ON companies(relationship_strength);
```

---

### Qdrant (Semantic Memory)

**Stores:**
- **Communication log embeddings** (email summaries, meeting notes)
- **Company notes/descriptions embeddings**
- **Person preferences/notes embeddings**
- **Contract document embeddings** (full PDF text)
- **Business card scans** (OCR + image embeddings)

**Why:**
- Semantic search:
  - "Find customers similar to Sun-Glo" (industry, size, shipping patterns)
  - "Search communications mentioning pricing issues"
  - "Find vendors with capabilities: emergency brake service"
  - "Search contracts with auto-renewal clauses"
  - "Find people with expertise in fleet management"
- Document retrieval:
  - Original contracts for legal review
  - Business card images for reference
  - Full email context (if needed)
- Similarity queries:
  - "Group customers by communication patterns"
  - "Find vendors with similar service offerings"

**Vector Fields:**
```python
{
    "id": "person_shannon",
    "vector": [0.234, 0.567, ...],  # 1536-dim OpenAI embedding
    "payload": {
        "person_id": "person_shannon",
        "type": "person",
        "first_name": "Shannon",
        "last_name": "Martinez",
        "employer": "Sun-Glo Corporation",
        "categories": ["customer-contact"],
        "description": "Logistics Coordinator at Sun-Glo. Prefers email, books loads on Fridays. Strong relationship since 2019. Typical Chicago to Dallas routes, 40k lbs general freight.",
        "full_profile_text": "...complete profile for embedding..."
    }
}

{
    "id": "comm_001",
    "vector": [0.123, 0.456, ...],
    "payload": {
        "communication_id": "comm_001",
        "type": "communication",
        "person_id": "person_shannon",
        "company_id": "company_sunglo",
        "subject": "Weekly load request - Chicago to Dallas",
        "summary": "Shannon requesting Friday pickup...",
        "full_text": "...complete communication text for embedding..."
    }
}
```

---

### Redis (Working Memory)

**Stores:**
- Recent contacts (last 7 days) - fast access for "Who did we talk to today?"
- Active customer list (for dispatch/sales dashboards)
- Preferred vendor list (for quick maintenance lookups)
- Birthday/anniversary alerts (next 30 days)
- Contracts expiring soon (next 60 days)
- Communication follow-up queue

**Why:**
- Fast dashboard access (<100ms):
  - "Who did we communicate with today?"
  - "Upcoming birthdays this week?"
  - "Preferred vendors for brake service?"
  - "Active customers for sales dashboard"
  - "Contracts expiring in 60 days?"
- Real-time alerts:
  - Birthday reminders
  - Contract renewal notifications
  - Follow-up task alerts
- Cache expiration:
  - Recent contacts: 7-day TTL
  - Birthday alerts: 30-day rolling window
  - Preferred vendors: 24-hour TTL (refresh daily)

**Redis Keys:**
```python
# Recent contacts (last 7 days)
ZADD contacts:recent 1730854800 "person_shannon"  # Score = last contact timestamp
ZADD contacts:recent 1730768400 "person_travis"

# Active customers (for dashboard)
SADD customers:active "company_sunglo"
SADD customers:active "company_xyz"

# Preferred vendors by service type
SADD vendors:preferred:brake_service "company_bosch"
SADD vendors:preferred:tire_service "company_bosch"
SADD vendors:preferred:pm_maintenance "company_bosch"

# Birthday alerts (next 30 days)
ZADD birthdays:upcoming 1733961600 "person_shannon"  # Score = birthday timestamp

# Contract expirations (next 60 days)
ZADD contracts:expiring 1735257600 "contract_sunglo_001"

# Communication follow-up queue
ZADD followups:pending 1730937600 "comm_001"  # Score = followup_date timestamp
```

---

### Graphiti (Temporal Memory)

**Stores:**
- **Relationship evolution** (customer since 2019, became vendor in 2021)
- **Communication pattern tracking** (frequency, sentiment trends over time)
- **Person employment history** (Shannon moved from Company A to Sun-Glo in 2020)
- **Company category changes** (became vendor AND customer)
- **Relationship strength evolution** (weak → moderate → strong)
- **Credit rating changes** (upgraded from B to A)
- **Contract lifecycle** (signed → renewed → terminated)

**Why:**
- Temporal queries:
  - "When did Sun-Glo become a customer?"
  - "How has communication frequency changed over time?"
  - "Track Shannon's employment history"
  - "When did Origin become both vendor AND customer to OpenHaul?"
  - "Show relationship strength evolution for Sun-Glo"
- Pattern detection:
  - Customer communication drops 50% before churning
  - VIP customers communicate 3x more frequently
  - Vendors with performance_rating < 3 don't renew contracts
- Forecasting:
  - Predict churn risk based on communication patterns
  - Estimate relationship strength trajectory
  - Project contract renewal likelihood

**Graphiti Episode Example:**
```python
Episode(
    name="Sun-Glo Relationship Evolution - 2019 to Present",
    episode_type="relationship_history",
    content="Sun-Glo Corporation became a customer in March 2019 after meeting Shannon at MATS trade show. Initial relationship was transactional (weak strength) with monthly communication. By Q4 2019, communication increased to weekly and relationship strength upgraded to moderate. In 2020, annual volume grew from $200k to $500k, relationship strength upgraded to strong. Shannon has been primary contact throughout. Payment behavior excellent (95 score), always pays within 20 days despite net-30 terms. Currently strategic partnership with NPS score of 85.",
    source_description="Communication logs, invoice records, and relationship tracking data for Sun-Glo Corporation 2019-2025",
    created_at="2025-11-04T12:00:00Z",
    valid_at="2025-11-04T12:00:00Z",
    entities=[
        Entity(name="Sun-Glo Corporation", entity_type="company"),
        Entity(name="Shannon Martinez", entity_type="person")
    ],
    edges=[
        Edge(
            source_entity="Sun-Glo Corporation",
            target_entity="Shannon Martinez",
            edge_name="PRIMARY_CONTACT",
            fact="Shannon has been primary contact for Sun-Glo since March 2019, maintains weekly communication"
        ),
        Edge(
            source_entity="Sun-Glo Corporation",
            target_entity="OpenHaul",
            edge_name="CUSTOMER_RELATIONSHIP_EVOLUTION",
            fact="Relationship strength evolved from weak (2019-Q2) to moderate (2019-Q4) to strong (2020-Q1), currently strategic partnership"
        )
    ]
)
```

---

## Primary Keys & Cross-Database Identity

**Person uses UUID:**

```python
# Neo4j
(:Person {
    person_id: "person_shannon",
    first_name: "Shannon",
    last_name: "Martinez",
    categories: ["customer-contact"]
})

# PostgreSQL
SELECT * FROM people WHERE person_id = 'person_shannon'
SELECT * FROM people WHERE employer_company_id = 'company_sunglo'

# Qdrant
search(
    query="logistics coordinator with experience in Chicago to Dallas routes",
    filter={"person_id": "person_shannon"}
)

# Redis
ZADD contacts:recent 1730854800 "person_shannon"
GET person:detail:person_shannon

# Graphiti
Person(
    person_id="person_shannon",
    name="Shannon Martinez",
    employer="Sun-Glo Corporation"
)
```

**Company uses UUID:**

```python
# Neo4j
(:Company {
    company_id: "company_sunglo",
    company_name: "Sun-Glo Corporation",
    categories: ["customer", "shipper", "receiver"]
})

# PostgreSQL
SELECT * FROM companies WHERE company_id = 'company_sunglo'
SELECT * FROM companies WHERE 'customer' = ANY(categories)

# Qdrant
search(
    query="manufacturing companies shipping 40k lbs freight",
    filter={"company_id": "company_sunglo"}
)

# Redis
SADD customers:active "company_sunglo"
GET company:detail:company_sunglo

# Graphiti
Company(
    company_id="company_sunglo",
    name="Sun-Glo Corporation",
    categories=["customer", "shipper", "receiver"]
)
```

---

## Bi-Temporal Tracking Pattern

**Person employment changes (Shannon scenario):**

```cypher
// Original employment (ended)
(:Person {
    person_id: "person_shannon",
    employer_company_id: "company_abc_logistics",
    start_date_at_company: "2017-01-15",
    end_date_at_company: "2020-02-28",
    valid_from: "2017-01-15T00:00:00Z",
    valid_to: "2020-02-28T23:59:59Z"  // Invalidated
})

// New employment (current)
(:Person {
    person_id: "person_shannon",
    employer_company_id: "company_sunglo",
    start_date_at_company: "2020-03-01",
    end_date_at_company: null,  // Still current
    valid_from: "2020-03-01T00:00:00Z",
    valid_to: null  // Still current
})

// Relationship link
(shannon_v2)-[:SUPERSEDES]->(shannon_v1)

// Query: "Where did Shannon work in January 2020?"
// Returns: company_abc_logistics

// Query: "Where does Shannon work now?"
// Returns: company_sunglo
```

**Company category evolution (Origin example):**

```cypher
// Origin initially just a carrier (2015)
(:Company {
    company_id: "company_origin",
    categories: ["carrier"],
    valid_from: "2015-01-01T00:00:00Z",
    valid_to: "2020-06-01T00:00:00Z"  // When became vendor too
})

// Origin became carrier + vendor (2020)
(:Company {
    company_id: "company_origin",
    categories: ["carrier", "vendor"],  # Multi-category!
    valid_from: "2020-06-01T00:00:00Z",
    valid_to: "2021-09-01T00:00:00Z"  // When became customer too
})

// Origin now carrier + vendor + customer (2021-present)
(:Company {
    company_id: "company_origin",
    categories: ["carrier", "vendor", "customer"],  # All three!
    valid_from: "2021-09-01T00:00:00Z",
    valid_to: null  // Current
})

// Query: "What was Origin's relationship to OpenHaul in 2019?"
// Returns: ["carrier"]

// Query: "What is Origin's relationship to OpenHaul now?"
// Returns: ["carrier", "vendor", "customer"]
```

**Relationship strength evolution:**

```cypher
// Sun-Glo relationship timeline
(:Company {company_id: "company_sunglo"})-[:RELATIONSHIP_STRENGTH_HISTORY {
    "2019-03": "weak",      // New customer
    "2019-10": "moderate",  // Regular business
    "2020-03": "strong",    // High volume, consistent
    "2025-01": "strategic"  // Partnership level
}]

// Enable temporal queries:
// "When did Sun-Glo become a strong relationship?"
// Returns: March 2020
```

---

## Document Types & Extraction Patterns

Hub 4 requires **7 document types** matching Hub 3/Hub 5 baseline standard.

### 1. Business Card (Scan/Photo)

**Document:** `shannon-martinez-sun-glo-card.jpg`
**Type:** Business Card
**Format:** Image (JPEG, PNG)

**Extraction Pattern (OCR + Structured):**
```python
{
    "card_type": "physical",
    "person": {
        "first_name": "Shannon",
        "last_name": "Martinez",
        "job_title": "Logistics Coordinator",
        "email": "shannon@sunglo.com",
        "phone_mobile": "312-555-0199",
        "phone_work": "312-555-0100"
    },
    "company": {
        "company_name": "Sun-Glo Corporation",
        "address": "1234 Industrial Blvd, Chicago, IL 60601",
        "phone": "312-555-0100",
        "website": "https://sunglo.com"
    },
    "source": "trade_show",
    "source_detail": "Mid-America Trucking Show 2019 - Louisville, KY",
    "date_received": "2019-02-15",
    "followup_needed": true,
    "notes": "Interested in regular Chicago-Dallas lanes"
}
```

---

### 2. Vendor Contract (Service Agreement)

**Document:** `bosch-service-agreement-2020.pdf`
**Type:** Vendor Contract
**Company:** Bosch Service Center

**Extraction Pattern:**
```python
{
    "contract_type": "vendor_agreement",
    "company_name": "Bosch Automotive Service Solutions",
    "company_id": "company_bosch",  # Match from Hub 4
    "contract_number": "VEND-2020-003",
    "parties": [
        {"name": "Origin Transport LLC", "role": "customer"},
        {"name": "Bosch Automotive Service Solutions", "role": "vendor"}
    ],
    "start_date": "2020-06-01",
    "end_date": null,  # Indefinite
    "auto_renewal": false,
    "notice_period_days": 30,
    "key_terms": {
        "services_provided": "Fleet maintenance, tire service, preventive maintenance, emergency repairs",
        "payment_terms": "net-15",
        "rate_structure": "Posted service rates with 10% fleet discount",
        "emergency_service": "Same-day emergency repair service available",
        "warranty": "90 days on parts, 60 days on labor",
        "insurance_requirements": "General liability $1M, workers comp",
        "termination_clause": "Either party may terminate with 30 days written notice"
    },
    "annual_value_estimate": 85000.00,
    "primary_contact": {
        "name": "Mike Johnson",
        "title": "Service Manager",
        "email": "mjohnson@boschservice.com",
        "phone": "702-555-0234"
    }
}
```

---

### 3. Customer Agreement (Service Contract)

**Document:** `sun-glo-service-agreement-2019.pdf`
**Type:** Customer Contract
**Customer:** Sun-Glo Corporation

**Extraction Pattern:**
```python
{
    "contract_type": "customer_contract",
    "company_name": "Sun-Glo Corporation",
    "company_id": "company_sunglo",
    "contract_number": "CUST-2019-001",
    "parties": [
        {"name": "OpenHaul LLC", "role": "broker"},
        {"name": "Sun-Glo Corporation", "role": "customer"}
    ],
    "start_date": "2019-03-01",
    "end_date": "2026-02-28",
    "term_length_months": 84,  # 7 years
    "auto_renewal": true,
    "renewal_terms": "60_day_notice",
    "notice_period_days": 60,
    "key_terms": {
        "service_level": "Standard freight brokerage services",
        "payment_terms": "net-30",
        "rate_structure": "Per-load negotiated rates",
        "volume_commitment": "Minimum 100 loads per year",
        "insurance_requirements": "$1M cargo insurance, $1M general liability",
        "dispute_resolution": "Binding arbitration in Nevada",
        "liability_limits": "Limited to freight charges",
        "termination_clause": "60 days written notice required"
    },
    "annual_value_estimate": 500000.00,
    "primary_contact": {
        "name": "Shannon Martinez",
        "title": "Logistics Coordinator",
        "person_id": "person_shannon"
    }
}
```

---

### 4. Credit Application

**Document:** `credit-application-sun-glo-2019.pdf`
**Type:** Credit Application
**Customer:** Sun-Glo Corporation

**Extraction Pattern:**
```python
{
    "document_type": "credit_application",
    "company_name": "Sun-Glo Corporation",
    "company_id": "company_sunglo",
    "application_date": "2019-02-20",
    "approved_date": "2019-03-01",
    "credit_limit_requested": 50000.00,
    "credit_limit_approved": 50000.00,
    "payment_terms_requested": "net-30",
    "payment_terms_approved": "net-30",
    "financial_information": {
        "years_in_business": 24,
        "annual_revenue": 25000000.00,
        "dun_bradstreet_number": "12-345-6789",
        "credit_rating": "A"
    },
    "trade_references": [
        {"company": "ABC Logistics", "years": 5, "payment_terms": "net-30"},
        {"company": "XYZ Transport", "years": 3, "payment_terms": "net-15"}
    ],
    "bank_reference": {
        "bank_name": "First National Bank of Chicago",
        "account_type": "business_checking",
        "years": 10
    },
    "application_status": "approved",
    "notes": "Strong credit history, excellent payment references"
}
```

---

### 5. Email Communication (Highlights)

**Document:** `email-shannon-2025-11-01.eml`
**Type:** Email Communication
**From:** Shannon Martinez (Sun-Glo)
**To:** G (OpenHaul)

**Extraction Pattern (Highlights Only - NOT Full Email):**
```python
{
    "communication_type": "email",
    "direction": "inbound",
    "person_id": "person_shannon",
    "company_id": "company_sunglo",
    "from_email": "shannon@sunglo.com",
    "to_email": "g@openhaul.com",
    "date": "2025-11-01",
    "time": "14:30:00",
    "subject": "Weekly load request - Chicago to Dallas",
    "summary": "Shannon requesting Friday pickup for 40,000 lbs general freight. Standard Chicago to Dallas route. Rate discussion - Shannon initially requested $2,300, holding at $2,500. Needs carrier confirmation by Wednesday.",
    "key_points": [
        "40,000 lbs general freight",
        "Chicago pickup Friday morning",
        "Dallas delivery Monday",
        "Rate agreed: $2,500",
        "Carrier confirmation needed by Wed"
    ],
    "action_items": [
        {
            "item": "Book carrier by Wednesday",
            "assigned_to": "person_g",
            "due_date": "2025-11-06"
        },
        {
            "item": "Send rate confirmation to Shannon",
            "assigned_to": "person_g",
            "due_date": "2025-11-01"
        }
    ],
    "sentiment": "positive",
    "sentiment_score": 80,
    "related_entities": {
        "load_number": "OH-321678"
    },
    "next_followup_date": "2025-11-06",
    "full_text_archived": false  # Just highlights, not full email
}
```

**Note:** Full email text can be archived in Qdrant for semantic search, but PostgreSQL stores only highlights to reduce storage and improve query performance.

---

### 6. NDA / Confidentiality Agreement

**Document:** `nda-xyz-manufacturing-2025.pdf`
**Type:** Non-Disclosure Agreement
**Company:** XYZ Manufacturing Inc (Prospect)

**Extraction Pattern:**
```python
{
    "contract_type": "NDA",
    "company_name": "XYZ Manufacturing Inc",
    "company_id": "company_prospect_xyz",
    "contract_number": "NDA-2025-012",
    "parties": [
        {"name": "OpenHaul LLC", "role": "disclosing_party"},
        {"name": "XYZ Manufacturing Inc", "role": "receiving_party"}
    ],
    "nda_type": "mutual",  # or "one-way"
    "start_date": "2025-09-15",
    "end_date": "2027-09-14",
    "term_length_months": 24,
    "key_terms": {
        "purpose": "Explore potential freight services partnership",
        "confidential_information_definition": "Pricing, shipping volumes, operational details, business strategies",
        "exclusions": "Publicly available information, independently developed information",
        "return_of_materials": "Required upon termination or request",
        "termination": "2 years from effective date or upon written request",
        "governing_law": "State of Nevada"
    },
    "status": "active",
    "notes": "Signed during initial exploratory meeting. Prospect status - not yet customer."
}
```

---

### 7. Contact Import Batch (Initial Data Load)

**Document:** `contact-batch-import-2025-11-01.csv`
**Type:** Bulk Contact Import
**Format:** CSV/Spreadsheet

**Extraction Pattern (Field Mapping):**
```python
{
    "import_type": "contact_batch",
    "import_date": "2025-11-01",
    "source": "initial_download",
    "total_records": 150,
    "field_mapping": {
        "first_name": "First Name",
        "last_name": "Last Name",
        "email": "Email",
        "phone_mobile": "Mobile Phone",
        "phone_work": "Work Phone",
        "company_name": "Company",
        "job_title": "Title",
        "categories": "Contact Type",  # Map values: "Customer" → ["customer-contact"], etc.
        "address_line1": "Street Address",
        "city": "City",
        "state": "State",
        "zip": "ZIP Code",
        "notes": "Notes"
    },
    "category_mapping": {
        "Customer": ["customer-contact"],
        "Vendor": ["vendor-contact"],
        "Carrier": ["carrier"],
        "Employee": ["employee"],
        "Partner": ["partner"]
    },
    "validation_rules": {
        "email_required": true,
        "phone_required": false,
        "deduplicate_by": "email"
    },
    "import_stats": {
        "records_imported": 145,
        "records_skipped": 5,
        "duplicates_found": 3,
        "errors": 2
    }
}
```

**Example CSV Row:**
```csv
First Name,Last Name,Email,Mobile Phone,Company,Title,Contact Type,City,State
Shannon,Martinez,shannon@sunglo.com,312-555-0199,Sun-Glo Corporation,Logistics Coordinator,Customer,Chicago,IL
Mike,Johnson,mjohnson@boschservice.com,702-555-0234,Bosch Service Center,Service Manager,Vendor,Las Vegas,NV
```

---

## Real-World Example: Sun-Glo Corporation

This example shows ONE customer relationship (Sun-Glo + Shannon) flowing through the complete contact system across all 5 databases.

**Customer:** Sun-Glo Corporation
**Primary Contact:** Shannon Martinez
**Relationship:** Customer of OpenHaul since March 2019

### Step 1: Initial Contact (Trade Show - Feb 2019)

**Business Card Received:**
```python
BusinessCard(
    card_id="card_shannon_001",
    person_id="person_shannon",  # Created from card
    company_id="company_sunglo",  # Created from card
    date_received="2019-02-15",
    source="trade_show",
    source_detail="Mid-America Trucking Show 2019 - Louisville, KY",
    document_path="qdrant://business-cards/shannon-martinez-sun-glo-2019.jpg",
    card_type="physical",
    followup_needed=True,
    followup_date="2019-02-20",
    notes="Met at booth #412. Interested in Chicago-Dallas lanes."
)
```

**Person Record Created:**
```python
Person(
    person_id="person_shannon",
    first_name="Shannon",
    last_name="Martinez",
    email="shannon@sunglo.com",
    phone_mobile="312-555-0199",
    phone_work="312-555-0100",
    categories=["prospect"],  # Not yet customer
    relationship_to_g="prospect",
    employer_company_id="company_sunglo",
    job_title="Logistics Coordinator",
    relationship_strength="weak",  # New contact
    referral_source="trade_show",
    created_at="2019-02-15T16:30:00Z"
)
```

**Company Record Created:**
```python
Company(
    company_id="company_sunglo",
    company_name="Sun-Glo Corporation",
    industry="Manufacturing",
    categories=["prospect"],  # Not yet customer
    relationship_since="2019-02-15",
    relationship_strength="weak",
    acquisition_source="trade_show",
    created_at="2019-02-15T16:30:00Z"
)
```

**Stored Across Databases:**
- **Neo4j:** `(Shannon:Person)-[:WORKS_FOR]->(SunGlo:Company)`, `(G)-[:MET_AT_TRADE_SHOW]->(Shannon)`
- **PostgreSQL:** Person + Company + BusinessCard records
- **Qdrant:** Business card image + OCR text embedded
- **Redis:** `SADD prospects:new "company_sunglo"`
- **Graphiti:** Episode: "Met Shannon Martinez from Sun-Glo at MATS 2019"

### Step 2: Follow-Up Call (Feb 2019)

**Communication Log:**
```python
CommunicationLog(
    communication_id="comm_sunglo_001",
    person_id="person_shannon",
    company_id="company_sunglo",
    communication_type="phone",
    date="2019-02-20",
    time="10:00:00",
    duration_minutes=15,
    direction="outbound",
    initiated_by_person_id="person_g",
    subject="Follow-up from MATS trade show",
    summary="G called Shannon to follow up on trade show meeting. Shannon confirmed interest in Chicago-Dallas lanes. Ships 2-3 loads per week, typically 40k lbs general freight. Current carrier mix of 3 carriers, looking for reliable 4th option. Rate expectations $2,200-$2,500 depending on season.",
    key_points=[
        "2-3 loads per week",
        "Chicago to Dallas primary lane",
        "40k lbs general freight typical",
        "Rate range $2,200-$2,500",
        "Looking for reliable carrier"
    ],
    decisions_made=[
        "Send service overview and rate sheet",
        "Shannon to send credit application"
    ],
    action_items=[
        {"item": "Send service overview", "assigned_to": "person_g", "due_date": "2019-02-21"},
        {"item": "Send credit application", "assigned_to": "person_shannon", "due_date": "2019-02-25"}
    ],
    sentiment="positive",
    sentiment_score=85,
    next_followup_date="2019-02-25"
)
```

**Stored Across Databases:**
- **Neo4j:** `(Comm)-[:WITH_PERSON]->(Shannon)`, `(Comm)-[:INITIATED_BY]->(G)`
- **PostgreSQL:** CommunicationLog record
- **Qdrant:** Call summary embedded for semantic search
- **Redis:** `ZADD followups:pending 1551081600 "comm_sunglo_001"`
- **Graphiti:** Episode: "Initial follow-up call with Shannon - positive interest"

### Step 3: Credit Application & Contract (Mar 2019)

**Credit Application Received:**
```python
# Credit application processed (see document example above)
# Company updated with credit info

Company.credit_rating = "A"
Company.payment_terms = "net-30"
Company.credit_limit = 50000.00
Company.approved_vendor = True  # Passed credit check
```

**Contract Signed:**
```python
Contract(
    contract_id="contract_sunglo_001",
    company_id="company_sunglo",
    contract_type="customer_contract",
    start_date="2019-03-01",
    status="active",
    annual_value=500000.00
    # See full contract example above
)
```

**Status Updated:**
```python
# Person updated
Person.categories = ["customer-contact"]  # Changed from "prospect"
Person.relationship_to_g = "customer_contact"
Person.relationship_strength = "moderate"  # Upgraded from "weak"

# Company updated
Company.categories = ["customer", "shipper", "receiver"]  # Changed from "prospect"
Company.relationship_strength = "moderate"
Company.primary_contact_person_id = "person_shannon"
Company.account_manager_person_id = "person_g"
```

**Stored Across Databases:**
- **Neo4j:** Updated relationship strength, `(Contract)-[:WITH_COMPANY]->(SunGlo)`
- **PostgreSQL:** Contract record + Person/Company status updates
- **Qdrant:** Contract PDF embedded
- **Redis:** `SMOVE prospects:new customers:active "company_sunglo"`
- **Graphiti:** Episode: "Sun-Glo became customer - signed 7-year contract"

### Step 4: Regular Business (2019-2020)

**Weekly Load Booking Communications:**
```python
# Example: One of 100+ communications over 18 months
CommunicationLog(
    communication_id="comm_sunglo_045",
    person_id="person_shannon",
    company_id="company_sunglo",
    communication_type="email",
    date="2019-10-18",
    subject="Weekly load request - Chicago to Dallas",
    summary="Standard weekly load request. 40k lbs, Friday pickup, Monday delivery. Rate $2,400.",
    sentiment="positive",
    related_entities={"load_number": "OH-123456"}
)
```

**Relationship Evolution:**
```python
# After 6 months of consistent business (Oct 2019)
Company.relationship_strength = "strong"  # Upgraded from "moderate"
Company.annual_volume_estimate = 500000.00  # Updated based on actual volume
Company.communication_frequency = "weekly"
Person.last_contact_date = "2019-10-18"
Person.contact_frequency = "weekly"
```

**Stored Across Databases:**
- **Neo4j:** Relationship strength updated
- **PostgreSQL:** 100+ CommunicationLog records
- **Qdrant:** Email summaries embedded
- **Redis:** `ZADD contacts:recent 1571356800 "person_shannon"` (weekly updates)
- **Graphiti:** Episode: "Sun-Glo relationship strength upgraded to strong after 6 months of consistent weekly business"

### Step 5: Current State (Nov 2025)

**Person Profile (Shannon):**
```python
Person(
    person_id="person_shannon",
    first_name="Shannon",
    last_name="Martinez",
    email="shannon@sunglo.com",
    categories=["customer-contact", "VIP"],  # Added VIP status
    relationship_to_g="customer_contact",
    employer_company_id="company_sunglo",
    job_title="Logistics Coordinator",
    start_date_at_company="2019-03-01",  # Been with Sun-Glo entire time
    relationship_strength="strong",
    vip_status=True,  # High-value relationship
    communication_style="Prefers email, responds within 24 hours. Books loads on Fridays for Monday pickups.",
    preferences={
        "communication": {
            "preferred_method": "email",
            "preferred_time": "afternoon"
        },
        "operational": {
            "typical_ship_day": "Friday",
            "preferred_carriers": ["Origin Transport"],
            "typical_shipment_size": "40,000 lbs"
        }
    },
    last_contact_date="2025-11-01",
    contact_frequency="weekly",
    tags=["decision_maker", "booking_contact", "strategic"]
)
```

**Company Profile (Sun-Glo):**
```python
Company(
    company_id="company_sunglo",
    company_name="Sun-Glo Corporation",
    categories=["customer", "shipper", "receiver"],
    credit_rating="A",
    payment_terms="net-30",
    current_ar_balance=2525.00,  # Current outstanding
    payment_behavior_score=95,  # Excellent history
    relationship_since="2019-03-01",
    relationship_strength="strong",
    relationship_type="partnership",
    annual_volume_estimate=500000.00,
    last_transaction_date="2025-11-03",
    communication_frequency="weekly",
    nps_score=85,  # Promoter
    primary_contact_person_id="person_shannon",
    account_manager_person_id="person_g"
)
```

**Complete Relationship Summary (Across All 5 Databases):**

| Database | What's Stored | Query Example |
|----------|---------------|---------------|
| **Neo4j** | Person → Company → Contract relationships | "Show all people at Sun-Glo", "Map communication network around Shannon" |
| **PostgreSQL** | Complete profiles + 300+ communication logs | "Sun-Glo payment history", "Shannon contact frequency over time" |
| **Qdrant** | Business card + 300 email summaries + contract PDF | "Find customers similar to Sun-Glo", "Search communications about rate discussions" |
| **Redis** | Recent contact (last week), active customer flag | "Who at Sun-Glo did we talk to this week?", "Is Sun-Glo active customer?" |
| **Graphiti** | 6-year relationship evolution | "When did Sun-Glo become strong relationship?", "Track Shannon's tenure at Sun-Glo" |

**Cross-Hub Links:**

- **Hub 2 (OpenHaul):** 300+ loads booked for Sun-Glo, Shannon as contact
- **Hub 5 (Financials):** 300+ invoices billed to Sun-Glo, excellent payment history (95 score)
- **Hub 1 (G):** Goal: "Grow Sun-Glo to $1M annual" (currently $500k)

---

## Query Pattern Examples

### 1. Customer Relationship Scoring

**Calculate relationship score based on multiple factors:**

```cypher
// Neo4j - Relationship scoring algorithm
MATCH (c:Company {categories: ["customer"]})
OPTIONAL MATCH (c)<-[:WITH_COMPANY]-(comm:CommunicationLog)
WHERE comm.date >= date() - duration({months: 6})
OPTIONAL MATCH (c)<-[:RECEIVED_FROM]-(rev:Revenue)
WHERE rev.revenue_date >= date() - duration({months: 12})
OPTIONAL MATCH (c)<-[:BILLED_TO]-(inv:Invoice)
WHERE inv.payment_status = 'paid' AND inv.payment_date <= inv.due_date
WITH c,
     count(DISTINCT comm) as communication_count,
     sum(rev.amount) as annual_revenue,
     count(DISTINCT inv) as paid_invoices,
     c.payment_behavior_score as payment_score,
     c.relationship_strength as rel_strength
WITH c,
     communication_count,
     annual_revenue,
     paid_invoices,
     payment_score,
     CASE rel_strength
         WHEN 'strategic' THEN 100
         WHEN 'strong' THEN 75
         WHEN 'moderate' THEN 50
         WHEN 'weak' THEN 25
         ELSE 0
     END as relationship_score
RETURN
    c.company_name as customer,
    communication_count,
    annual_revenue,
    payment_score,
    relationship_score,
    (communication_count * 2) + (annual_revenue / 10000) + payment_score + relationship_score as total_score
ORDER BY total_score DESC
LIMIT 20
```

```sql
-- PostgreSQL - Customer health dashboard
WITH customer_metrics AS (
    SELECT
        c.company_id,
        c.company_name,
        c.relationship_strength,
        c.payment_behavior_score,
        c.annual_volume_estimate,
        COUNT(DISTINCT comm.communication_id) FILTER (WHERE comm.date >= CURRENT_DATE - INTERVAL '6 months') as recent_communications,
        MAX(comm.date) as last_communication,
        EXTRACT(DAYS FROM (CURRENT_DATE - MAX(comm.date))) as days_since_contact,
        c.nps_score
    FROM
        companies c
        LEFT JOIN communication_log comm ON comm.company_id = c.company_id
    WHERE
        'customer' = ANY(c.categories)
        AND c.active_status = TRUE
    GROUP BY c.company_id, c.company_name, c.relationship_strength, c.payment_behavior_score,
             c.annual_volume_estimate, c.nps_score
)
SELECT
    company_name,
    relationship_strength,
    payment_behavior_score,
    annual_volume_estimate,
    recent_communications,
    days_since_contact,
    nps_score,
    CASE
        WHEN days_since_contact > 90 THEN 'At Risk - No Recent Contact'
        WHEN payment_behavior_score < 70 THEN 'At Risk - Payment Issues'
        WHEN recent_communications < 5 THEN 'At Risk - Low Engagement'
        WHEN nps_score < 0 THEN 'At Risk - Detractor'
        WHEN relationship_strength = 'strategic' AND nps_score > 50 THEN 'Healthy - Strategic'
        WHEN relationship_strength = 'strong' THEN 'Healthy - Strong'
        ELSE 'Moderate'
    END as health_status
FROM customer_metrics
ORDER BY
    CASE health_status
        WHEN 'At Risk - No Recent Contact' THEN 1
        WHEN 'At Risk - Payment Issues' THEN 2
        WHEN 'At Risk - Low Engagement' THEN 3
        WHEN 'At Risk - Detractor' THEN 4
        ELSE 5
    END,
    annual_volume_estimate DESC;
```

### 2. Vendor Concentration Analysis

```cypher
// Neo4j - Vendor dependency risk
MATCH (exp:Expense)-[:PAID_TO]->(v:Company)
WHERE exp.company_assignment = "Origin"
  AND exp.expense_date >= date() - duration({months: 12})
WITH sum(exp.amount) as total_expenses
MATCH (exp2:Expense)-[:PAID_TO]->(v2:Company)
WHERE exp2.company_assignment = "Origin"
  AND exp2.expense_date >= date() - duration({months: 12})
WITH v2,
     sum(exp2.amount) as vendor_spend,
     total_expenses,
     count(exp2) as transaction_count
WITH v2, vendor_spend, total_expenses, transaction_count,
     round((vendor_spend / total_expenses) * 100, 2) as concentration_percent
WHERE concentration_percent > 15  // Flag vendors with >15% concentration
RETURN
    v2.company_name as vendor,
    vendor_spend,
    concentration_percent,
    transaction_count,
    CASE
        WHEN concentration_percent > 30 THEN 'CRITICAL CONCENTRATION RISK'
        WHEN concentration_percent > 20 THEN 'HIGH CONCENTRATION RISK'
        ELSE 'MODERATE CONCENTRATION RISK'
    END as risk_level
ORDER BY concentration_percent DESC
```

### 3. Birthday & Anniversary Tracking

```sql
-- PostgreSQL - Upcoming birthdays and work anniversaries
WITH upcoming_dates AS (
    SELECT
        person_id,
        first_name || ' ' || last_name as full_name,
        employer_company_name,
        job_title,
        'birthday' as event_type,
        birthday as original_date,
        DATE(EXTRACT(YEAR FROM CURRENT_DATE) || '-' ||
             EXTRACT(MONTH FROM birthday) || '-' ||
             EXTRACT(DAY FROM birthday)) as this_year_date
    FROM people
    WHERE birthday IS NOT NULL
      AND active_status = TRUE

    UNION ALL

    SELECT
        person_id,
        first_name || ' ' || last_name as full_name,
        employer_company_name,
        job_title,
        'work_anniversary' as event_type,
        start_date_at_company as original_date,
        DATE(EXTRACT(YEAR FROM CURRENT_DATE) || '-' ||
             EXTRACT(MONTH FROM start_date_at_company) || '-' ||
             EXTRACT(DAY FROM start_date_at_company)) as this_year_date
    FROM people
    WHERE start_date_at_company IS NOT NULL
      AND employment_status = 'active'
      AND active_status = TRUE
)
SELECT
    full_name,
    employer_company_name,
    job_title,
    event_type,
    this_year_date,
    this_year_date - CURRENT_DATE as days_until,
    CASE event_type
        WHEN 'work_anniversary' THEN EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM original_date)
        ELSE NULL
    END as years
FROM upcoming_dates
WHERE this_year_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY this_year_date ASC;
```

### 4. Multi-Category Entity Discovery

```cypher
// Neo4j - Find companies with multiple categories
MATCH (c:Company)
WHERE size(c.categories) > 1
WITH c, c.categories as cats
RETURN
    c.company_name as company,
    cats as categories,
    size(cats) as category_count,
    CASE
        WHEN 'customer' IN cats AND 'vendor' IN cats THEN 'Customer + Vendor'
        WHEN 'carrier' IN cats AND 'customer' IN cats THEN 'Carrier + Customer'
        WHEN 'customer' IN cats AND 'vendor' IN cats AND 'carrier' IN cats THEN 'Full Multi-Relationship'
        ELSE 'Other Multi-Category'
    END as relationship_type
ORDER BY category_count DESC, c.company_name
```

```sql
-- PostgreSQL - Multi-category companies with financial summary
SELECT
    c.company_name,
    c.categories,
    array_length(c.categories, 1) as category_count,
    c.relationship_since,
    c.relationship_strength,
    COALESCE(SUM(r.amount) FILTER (WHERE r.company_assignment = 'OpenHaul'), 0) as revenue_from_us,
    COALESCE(SUM(e.amount) FILTER (WHERE e.company_assignment = 'OpenHaul'), 0) as expenses_to_them,
    COALESCE(SUM(r.amount), 0) - COALESCE(SUM(e.amount), 0) as net_position
FROM
    companies c
    LEFT JOIN revenue r ON r.customer_id = c.company_id
        AND r.revenue_date >= CURRENT_DATE - INTERVAL '12 months'
    LEFT JOIN expenses e ON e.vendor_id = c.company_id
        AND e.expense_date >= CURRENT_DATE - INTERVAL '12 months'
WHERE
    array_length(c.categories, 1) > 1
    AND c.active_status = TRUE
GROUP BY c.company_id, c.company_name, c.categories, c.relationship_since, c.relationship_strength
ORDER BY array_length(c.categories, 1) DESC, net_position DESC;
```

### 5. Communication Sentiment Trending

```sql
-- PostgreSQL - Communication sentiment over time
WITH monthly_sentiment AS (
    SELECT
        c.company_id,
        c.company_name,
        DATE_TRUNC('month', comm.date) as month,
        AVG(comm.sentiment_score) as avg_sentiment,
        COUNT(*) as communication_count
    FROM
        communication_log comm
        JOIN companies c ON c.company_id = comm.company_id
    WHERE
        comm.sentiment_score IS NOT NULL
        AND comm.date >= CURRENT_DATE - INTERVAL '12 months'
        AND 'customer' = ANY(c.categories)
    GROUP BY c.company_id, c.company_name, DATE_TRUNC('month', comm.date)
),
sentiment_trend AS (
    SELECT
        company_name,
        month,
        avg_sentiment,
        communication_count,
        LAG(avg_sentiment) OVER (PARTITION BY company_name ORDER BY month) as prev_month_sentiment,
        avg_sentiment - LAG(avg_sentiment) OVER (PARTITION BY company_name ORDER BY month) as sentiment_change
    FROM monthly_sentiment
)
SELECT
    company_name,
    month,
    ROUND(avg_sentiment::NUMERIC, 2) as avg_sentiment,
    communication_count,
    ROUND(sentiment_change::NUMERIC, 2) as sentiment_change,
    CASE
        WHEN sentiment_change < -20 THEN 'ALERT: Sharp Decline'
        WHEN sentiment_change < -10 THEN 'Warning: Declining'
        WHEN sentiment_change > 10 THEN 'Positive: Improving'
        ELSE 'Stable'
    END as trend_alert
FROM sentiment_trend
WHERE month >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY company_name, month DESC;
```

### 6. Contact Dormancy Detection

```sql
-- PostgreSQL - Contacts with no recent communication
WITH last_contact AS (
    SELECT
        p.person_id,
        p.first_name || ' ' || p.last_name as full_name,
        p.employer_company_name,
        p.categories,
        p.relationship_strength,
        MAX(comm.date) as last_contact_date,
        EXTRACT(DAYS FROM (CURRENT_DATE - MAX(comm.date))) as days_since_contact
    FROM
        people p
        LEFT JOIN communication_log comm ON comm.person_id = p.person_id
    WHERE
        p.active_status = TRUE
        AND ('customer-contact' = ANY(p.categories) OR 'VIP' = ANY(p.categories))
    GROUP BY p.person_id, p.first_name, p.last_name, p.employer_company_name,
             p.categories, p.relationship_strength
)
SELECT
    full_name,
    employer_company_name,
    categories,
    relationship_strength,
    last_contact_date,
    days_since_contact,
    CASE
        WHEN days_since_contact > 180 THEN 'CRITICAL: 6+ Months No Contact'
        WHEN days_since_contact > 90 THEN 'HIGH RISK: 3+ Months No Contact'
        WHEN days_since_contact > 60 THEN 'MODERATE RISK: 2+ Months No Contact'
        ELSE 'Recent Contact'
    END as dormancy_risk
FROM last_contact
WHERE days_since_contact > 60
  OR last_contact_date IS NULL
ORDER BY
    CASE
        WHEN last_contact_date IS NULL THEN 1
        ELSE 2
    END,
    days_since_contact DESC;
```

### 7. Account Manager Workload Balancing

```cypher
// Neo4j - Account manager customer distribution
MATCH (manager:Person)-[:ACCOUNT_MANAGER_FOR]->(customer:Company)
WHERE 'customer' IN customer.categories
WITH manager, customer
OPTIONAL MATCH (customer)<-[:RECEIVED_FROM]-(rev:Revenue)
WHERE rev.revenue_date >= date() - duration({months: 12})
WITH manager,
     count(DISTINCT customer) as customer_count,
     sum(rev.amount) as total_annual_revenue,
     collect({name: customer.company_name, revenue: sum(rev.amount)}) as customers
RETURN
    manager.first_name + ' ' + manager.last_name as account_manager,
    customer_count,
    total_annual_revenue,
    round(total_annual_revenue / customer_count, 2) as avg_revenue_per_customer,
    customers
ORDER BY customer_count DESC
```

### 8. Contract Expiration & Renewal Pipeline

```sql
-- PostgreSQL - Contract renewal pipeline
WITH contract_pipeline AS (
    SELECT
        cont.contract_id,
        c.company_name,
        c.categories,
        cont.contract_type,
        cont.end_date,
        cont.annual_value,
        cont.auto_renewal,
        cont.notice_period_days,
        EXTRACT(DAYS FROM (cont.end_date - CURRENT_DATE)) as days_until_expiration,
        CASE
            WHEN cont.auto_renewal = TRUE THEN cont.end_date - (cont.notice_period_days || ' days')::INTERVAL
            ELSE cont.end_date - INTERVAL '90 days'
        END as action_required_by
    FROM
        contracts cont
        JOIN companies c ON c.company_id = cont.company_id
    WHERE
        cont.status = 'active'
        AND cont.end_date IS NOT NULL
        AND cont.end_date >= CURRENT_DATE
        AND cont.end_date <= CURRENT_DATE + INTERVAL '180 days'
)
SELECT
    company_name,
    categories,
    contract_type,
    end_date,
    annual_value,
    auto_renewal,
    days_until_expiration,
    action_required_by,
    CASE
        WHEN CURRENT_DATE >= action_required_by THEN 'URGENT: Action Required Now'
        WHEN action_required_by - CURRENT_DATE <= INTERVAL '30 days' THEN 'HIGH PRIORITY: Action Required Soon'
        WHEN action_required_by - CURRENT_DATE <= INTERVAL '60 days' THEN 'MEDIUM PRIORITY'
        ELSE 'LOW PRIORITY'
    END as priority
FROM contract_pipeline
ORDER BY
    CASE
        WHEN CURRENT_DATE >= action_required_by THEN 1
        WHEN action_required_by - CURRENT_DATE <= INTERVAL '30 days' THEN 2
        WHEN action_required_by - CURRENT_DATE <= INTERVAL '60 days' THEN 3
        ELSE 4
    END,
    annual_value DESC;
```

### 9. Network Effect Analysis (Referral Tracking)

```cypher
// Neo4j - Referral network visualization
MATCH path = (referrer:Person)-[:REFERRED]->(referee:Person)-[:WORKS_FOR]->(c:Company)
WHERE 'customer' IN c.categories
WITH referrer, collect({referee: referee.first_name + ' ' + referee.last_name,
                        company: c.company_name}) as referrals,
     count(DISTINCT c) as companies_referred
RETURN
    referrer.first_name + ' ' + referrer.last_name as referrer_name,
    companies_referred,
    referrals
ORDER BY companies_referred DESC
LIMIT 20
```

### 10. Employee Communication Pattern Analysis

```sql
-- PostgreSQL - Communication patterns by employee category
WITH employee_communication AS (
    SELECT
        p.person_id,
        p.first_name || ' ' || p.last_name as employee_name,
        p.job_title,
        COUNT(comm.communication_id) as total_communications,
        COUNT(comm.communication_id) FILTER (WHERE comm.communication_type = 'email') as emails,
        COUNT(comm.communication_id) FILTER (WHERE comm.communication_type = 'phone') as calls,
        COUNT(comm.communication_id) FILTER (WHERE comm.communication_type = 'meeting') as meetings,
        AVG(comm.sentiment_score) FILTER (WHERE comm.sentiment_score IS NOT NULL) as avg_sentiment,
        COUNT(DISTINCT comm.company_id) as unique_companies
    FROM
        people p
        LEFT JOIN communication_log comm ON comm.person_id = p.person_id
            AND comm.date >= CURRENT_DATE - INTERVAL '6 months'
    WHERE
        'employee' = ANY(p.categories)
        AND p.active_status = TRUE
    GROUP BY p.person_id, p.first_name, p.last_name, p.job_title
)
SELECT
    employee_name,
    job_title,
    total_communications,
    emails,
    calls,
    meetings,
    ROUND(avg_sentiment::NUMERIC, 2) as avg_sentiment_score,
    unique_companies as companies_contacted,
    ROUND((total_communications::NUMERIC / NULLIF(unique_companies, 0)), 2) as communications_per_company
FROM employee_communication
WHERE total_communications > 0
ORDER BY total_communications DESC;
```

---

## Next Steps

1. ✅ **Complete Entity Definitions** - 120+ properties across 5 entities
2. ✅ **Category Integration** - User-provided + extended categories
3. ✅ **Preferences JSON Structure** - Standard schema defined
4. ✅ **7 Document Types** - Extraction patterns documented
5. ✅ **Real-World Example** - Sun-Glo + Shannon complete lifecycle
6. ✅ **Database Distribution** - All 5 databases mapped
7. ✅ **Query Patterns** - 10+ advanced examples
8. ✅ **Cross-Hub Integration** - Complete links to Hubs 1, 2, 3, 5, 6
9. ✅ **Bi-Temporal Tracking** - Employment, category, relationship strength evolution
10. 🔲 **Remaining:** Contact information import strategy refinement, sentiment analysis algorithm details

---

**Completion Status:** ✅ 95% Complete (Categories integrated, 7 documents, 120+ properties, real-world example complete, 10+ query patterns)

**Match to Hub 3/Hub 5 Baseline:**
- ✅ **Entities Defined:** 5 core entities with complete property lists (120+ properties total)
- ✅ **Category System:** Multi-category support fully documented
- ✅ **Relationships Documented:** 25+ relationship types with properties
- ✅ **Database Distribution:** Clear mapping for all 5 databases
- ✅ **Document Examples:** 7 document types with extraction patterns
- ✅ **Cross-Hub Links:** Complete integration with Hubs 1, 2, 3, 5, 6
- ✅ **Temporal Tracking:** Bi-temporal patterns documented (employment changes, category evolution, relationship strength)
- ✅ **Primary Keys:** UUID strategy defined and exemplified across all databases
- ✅ **Real-World Example:** Complete Sun-Glo + Shannon relationship flow across all 5 databases
- ✅ **Query Patterns:** 10+ advanced query examples (relationship scoring, vendor risk, birthday tracking, sentiment analysis, dormancy detection)
- ✅ **Preferences Schema:** Complete JSON structure for Person and Company preferences
- 🔲 **Remaining:** Minor details on sentiment analysis algorithms, email import automation

**This matches Hub 3/Hub 5 baseline detail level.** Ready for Phase 2 deep dive on remaining hubs (Hub 2, Hub 6, Hub 1).

---

**Baseline Established:** November 4, 2025
**Schema Version:** v2.0 (Baseline Complete)
**Category Integration:** ✅ Complete (User-provided + extended)
