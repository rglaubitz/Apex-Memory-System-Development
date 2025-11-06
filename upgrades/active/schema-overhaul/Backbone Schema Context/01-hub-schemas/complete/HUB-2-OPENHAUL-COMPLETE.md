# HUB 2: OPENHAUL (BROKERAGE OPERATIONS) - COMPLETE

**Status:** ✅ Complete Baseline (95%)
**Purpose:** Freight brokerage operations - booking, execution, carrier management
**Company:** OpenHaul LLC
**Primary Key Strategy:** load_number (e.g., "OH-321678")

---

## Purpose

Hub 2 tracks all OpenHaul brokerage operations - the "front-end" of the business. This includes customer sales orders, load bookings, carrier assignments, pickup/delivery execution, and document management.

**Key Distinction:** This hub focuses on **OPERATIONAL** work (booking, execution). The **FINANCIAL** side (invoices, payments) lives in Hub 5 (Financials).

**Relationship to Origin:** Origin Transport trucks are treated as "just another carrier" for OpenHaul loads. Normal load payments flow through Hub 5. Intercompany transfers (credit lines, bill coverage) are also tracked in Hub 5.

---

## Core Entities

### 1. **Load** - The Central Entity ⭐

The primary operational entity representing a freight movement. Everything links back to the load number.

**Complete Property List (42 properties):**

```yaml
# Primary Identifiers
load_number: string            # PRIMARY KEY - format: "OH-321678"
customer_reference: string     # Customer's order/PO number

# Parties
customer_id: string            # Who bought this shipment (Hub 4 link)
carrier_id: string             # Who hauls it (could be Origin or external)
broker_id: string (nullable)   # If brokered out to another broker
shipper_id: string             # Originating company (Hub 4)
consignee_id: string           # Receiving company (Hub 4)

# Locations
pickup_location_id: string     # Where freight originates
delivery_location_id: string   # Where freight is delivered

# Dates & Times
pickup_date: date
pickup_time_window_start: time (nullable)
pickup_time_window_end: time (nullable)
pickup_appointment_required: boolean
delivery_date: date
delivery_time_window_start: time (nullable)
delivery_time_window_end: time (nullable)
delivery_appointment_required: boolean

# Equipment & Freight
equipment_type: enum           # See Equipment Types section
weight_lbs: integer
piece_count: integer
commodity_description: string
commodity_class: string (nullable)  # NMFC freight class
temperature_range: string (nullable)  # For reefer loads
special_requirements: array[string]  # ["liftgate", "team_driver", "hazmat"]

# Operational Status
status: enum                   # See Load Status Lifecycle section
current_location_gps: {lat, lon, address} (nullable)
eta_delivery: timestamp (nullable)
last_status_update: timestamp

# Financial (values only - full tracking in Hub 5)
customer_rate: decimal         # What OpenHaul charges customer
carrier_rate: decimal          # What OpenHaul pays carrier
margin: decimal                # customer_rate - carrier_rate
accessorial_charges: array[object]  # See Accessorial Charges section

# Documents
sales_order_id: string (nullable)
rate_con_id: string (nullable)
bol_id: string (nullable)
pod_id: string (nullable)

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
booked_date: timestamp
completed_date: timestamp (nullable)
valid_from: timestamp
valid_to: timestamp (nullable)
```

**Example Load (OH-321678 - Sun-Glo to Dallas):**
```python
Load(
    load_number="OH-321678",
    customer_reference="SG-PO-2025-1045",
    customer_id="company_sunglo",
    carrier_id="carr_origin",
    shipper_id="company_sunglo",
    consignee_id="company_midwest_warehouse",
    pickup_location_id="loc_sunglo_chicago",
    delivery_location_id="loc_midwest_dallas",
    pickup_date="2025-11-05",
    pickup_appointment_required=True,
    pickup_time_window_start="08:00",
    pickup_time_window_end="17:00",
    delivery_date="2025-11-07",
    delivery_appointment_required=False,
    equipment_type="dry_van_53",
    weight_lbs=40000,
    piece_count=18,
    commodity_description="Pet Food - Dry Kibble (palletized)",
    commodity_class="50",
    special_requirements=["appointment_required"],
    status="delivered",
    customer_rate=2500.00,
    carrier_rate=2000.00,
    margin=500.00,
    accessorial_charges=[
        {"type": "detention_pickup", "amount": 75.00},
        {"type": "lumper_fee", "amount": 150.00}
    ],
    booked_date="2025-11-03T14:30:00Z",
    completed_date="2025-11-07T15:45:00Z"
)
```

---

### 2. **Carrier** - Trucking Companies & Drivers

Companies or owner-operators who haul freight for OpenHaul.

**Complete Property List (38 properties):**

```yaml
# Primary Identifiers
carrier_id: string             # PRIMARY KEY - UUID or standardized ID
carrier_name: string
carrier_legal_name: string (nullable)
dba_name: string (nullable)

# Authority & Compliance
carrier_type: enum             # ["asset_based", "owner_operator", "broker", "freight_forwarder"]
mc_number: string              # FMCSA Motor Carrier number
dot_number: string             # FMCSA DOT number
scac_code: string (nullable)   # Standard Carrier Alpha Code
authority_status: enum         # ["active", "inactive", "out_of_service"]
authority_expiry_date: date (nullable)

# Insurance
insurance_provider: string
insurance_policy_number: string
insurance_expiry_date: date
liability_coverage_amount: decimal
cargo_coverage_amount: decimal
insurance_cert_on_file: boolean

# Contact Information (links to Hub 4)
primary_contact_person_id: string
phone: string
email: string
address: string
city: string
state: string
zip: string

# Operational Preferences
preferred_lanes: array[string]  # ["IL-TX", "TX-CA", "midwest_regional"]
equipment_types_available: array[enum]
average_transit_time_days: decimal (nullable)
max_weight_capacity: integer (nullable)

# Performance Metrics
rating: decimal                # 1.0 to 5.0 (calculated from performance)
total_loads_hauled: integer
on_time_percentage: decimal
claims_count: integer
claims_total_amount: decimal

# Status & Activation
active_status: boolean
onboarding_date: date
last_load_date: date (nullable)
notes: text (nullable)

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: timestamp (nullable)
```

**Example - Origin Transport as Carrier:**
```python
Carrier(
    carrier_id="carr_origin",
    carrier_name="Origin Transport LLC",
    carrier_legal_name="Origin Transport LLC",
    carrier_type="asset_based",
    mc_number="MC-123456",
    dot_number="DOT-789012",
    scac_code="ORGN",
    authority_status="active",
    insurance_provider="Progressive Commercial",
    insurance_expiry_date="2026-03-15",
    liability_coverage_amount=1000000.00,
    cargo_coverage_amount=100000.00,
    insurance_cert_on_file=True,
    primary_contact_person_id="person_g",
    phone="312-555-0100",
    email="dispatch@origintransport.com",
    preferred_lanes=["IL-TX", "TX-CA", "midwest_regional"],
    equipment_types_available=["dry_van_53", "reefer_53"],
    rating=5.0,
    total_loads_hauled=342,
    on_time_percentage=98.5,
    claims_count=0,
    active_status=True,
    onboarding_date="2019-01-15",
    notes="Internal carrier - Primetime-owned. 18-truck fleet."
)
```

---

### 3. **Location** - Pickup & Delivery Points

Shipper and receiver facilities.

**Complete Property List (28 properties):**

```yaml
# Primary Identifiers
location_id: string            # PRIMARY KEY - UUID
location_name: string
location_code: string (nullable)  # Internal shorthand (e.g., "SG-CHI")

# Location Type
location_type: enum            # ["shipper", "receiver", "both", "warehouse", "distribution_center"]
company_id: string             # Links to Company in Hub 4

# Address
address_line1: string
address_line2: string (nullable)
city: string
state: string
zip: string
country: string                # Default: "USA"
gps_coordinates: {latitude, longitude}

# Contact Information (links to Hub 4)
primary_contact_person_id: string (nullable)
phone: string
email: string (nullable)

# Operating Details
operating_hours: string        # "Mon-Fri 8am-5pm"
timezone: string               # "America/Chicago"
appointment_required: boolean
appointment_scheduling_phone: string (nullable)
appointment_scheduling_email: string (nullable)

# Facility Details
dock_count: integer (nullable)
dock_type: enum (nullable)     # ["inside", "outside", "both"]
forklift_available: boolean
lumper_required: boolean
lumper_typical_fee: decimal (nullable)

# Restrictions
restrictions: array[string]    # ["no_reefers", "no_teams", "53_max_length", "no_hazmat"]
detention_free_hours: integer  # Hours before detention charged
detention_rate_per_hour: decimal

# Additional Info
notes: text (nullable)
last_used_date: date (nullable)

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Example - Sun-Glo Chicago Warehouse:**
```python
Location(
    location_id="loc_sunglo_chicago",
    location_name="Sun-Glo Corporation - Chicago Warehouse",
    location_code="SG-CHI",
    location_type="shipper",
    company_id="company_sunglo",
    address_line1="4500 Industrial Boulevard",
    city="Chicago",
    state="IL",
    zip="60601",
    country="USA",
    gps_coordinates={"latitude": 41.8781, "longitude": -87.6298},
    primary_contact_person_id="person_shannon",
    phone="312-555-0199",
    email="shipping@sunglo.com",
    operating_hours="Mon-Fri 8am-5pm",
    timezone="America/Chicago",
    appointment_required=True,
    appointment_scheduling_phone="312-555-0199",
    dock_count=8,
    dock_type="inside",
    forklift_available=True,
    lumper_required=False,
    detention_free_hours=2,
    detention_rate_per_hour=75.00,
    restrictions=["no_weekend_deliveries"],
    notes="Shannon prefers Friday pickups. 8-dock facility with inside loading."
)
```

---

### 4. **SalesOrder** - Customer Purchase Order (Document Entity)

Customer's purchase order or shipping request document.

**Complete Property List (15 properties):**

```yaml
# Primary Identifiers
sales_order_id: string         # PRIMARY KEY - UUID
load_number: string            # FOREIGN KEY to Load

# Order Details
customer_id: string            # Links to Hub 4
order_number: string           # Customer's PO/SO number
order_date: date

# Document Management
document_path: string          # Google Drive or local path
document_type: enum            # ["email", "pdf", "fax", "portal_download"]
extracted_data: object         # JSON - key fields extracted from document

# Status
processing_status: enum        # ["pending", "processed", "load_created", "error"]
error_message: string (nullable)

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
processed_at: timestamp (nullable)
```

**Example - Sun-Glo Sales Order:**
```python
SalesOrder(
    sales_order_id="so_sunglo_1045",
    load_number="OH-321678",
    customer_id="company_sunglo",
    order_number="SG-PO-2025-1045",
    order_date="2025-11-01",
    document_path="drive://openhaul/sales_orders/2025-11/SG-PO-2025-1045.pdf",
    document_type="email",
    extracted_data={
        "pickup_date": "2025-11-05",
        "delivery_date": "2025-11-07",
        "pickup_location": "4500 Industrial Blvd, Chicago, IL 60601",
        "delivery_location": "2300 Distribution Way, Dallas, TX 75201",
        "weight": "40,000 lbs",
        "pieces": "18 pallets",
        "commodity": "Pet Food - Dry Kibble",
        "rate": "$2,500.00",
        "equipment": "53' Dry Van"
    },
    processing_status="load_created",
    processed_at="2025-11-03T14:30:00Z"
)
```

---

### 5. **RateConfirmation** - Carrier Agreement (Document Entity)

Binding agreement with carrier on rate and terms.

**Complete Property List (18 properties):**

```yaml
# Primary Identifiers
rate_con_id: string            # PRIMARY KEY - UUID
load_number: string            # FOREIGN KEY to Load

# Parties
carrier_id: string             # Links to Carrier entity
broker_id: string              # OpenHaul broker ID (person from Hub 4)

# Agreement Details
rate_con_number: string        # Sequential number (e.g., "RC-2025-001234")
rate_con_date: date
agreed_rate: decimal
payment_terms: string          # "Quick pay - 3 days" or "Net 30"
payment_method: enum           # ["check", "ach", "factoring", "comchek"]

# Terms & Conditions
terms_text: text               # Full T&C text
detention_rate: decimal (nullable)
lumper_reimbursement: boolean

# Document Management
document_path: string          # Signed PDF location
signed: boolean
signature_date: date (nullable)

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Example - Origin Transport Rate Confirmation:**
```python
RateConfirmation(
    rate_con_id="ratecon_oh321678",
    load_number="OH-321678",
    carrier_id="carr_origin",
    broker_id="person_g",
    rate_con_number="RC-2025-003456",
    rate_con_date="2025-11-03",
    agreed_rate=2000.00,
    payment_terms="Net 15",
    payment_method="ach",
    detention_rate=75.00,
    lumper_reimbursement=True,
    document_path="drive://openhaul/rate_cons/2025-11/RC-2025-003456.pdf",
    signed=True,
    signature_date="2025-11-03"
)
```

---

### 6. **BOL** - Bill of Lading (Document Entity)

Proof of pickup and freight details.

**Complete Property List (22 properties):**

```yaml
# Primary Identifiers
bol_id: string                 # PRIMARY KEY - UUID
load_number: string            # FOREIGN KEY to Load

# BOL Details
bol_number: string             # Sequential or carrier-generated
pickup_date: date
pickup_time: time (nullable)
pickup_location_id: string

# Freight Details
piece_count: integer
weight_lbs: integer
pallet_count: integer (nullable)
commodity_description: string
freight_class: string (nullable)

# Signatures & Verification
pickup_signature: string (nullable)  # Signature data or "signed"
shipper_name: string
shipper_signature_time: timestamp (nullable)
driver_name: string
driver_signature: string (nullable)

# Condition & Notes
freight_condition: enum        # ["good", "damaged", "shortage", "overage"]
condition_notes: text (nullable)
special_instructions: text (nullable)

# Document Management
document_path: string          # PDF location
ocr_extracted: boolean         # OCR processing complete?
extracted_data: object         # JSON - OCR results

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Example - Load OH-321678 BOL:**
```python
BOL(
    bol_id="bol_oh321678",
    load_number="OH-321678",
    bol_number="OH-BOL-321678",
    pickup_date="2025-11-05",
    pickup_time="10:15",
    pickup_location_id="loc_sunglo_chicago",
    piece_count=18,
    weight_lbs=40000,
    pallet_count=18,
    commodity_description="Pet Food - Dry Kibble (palletized)",
    freight_class="50",
    pickup_signature="signed",
    shipper_name="Shannon Martinez",
    shipper_signature_time="2025-11-05T10:15:00Z",
    driver_name="Robert McCullough",
    driver_signature="signed",
    freight_condition="good",
    condition_notes="All 18 pallets loaded, shrink-wrapped, no visible damage",
    document_path="drive://openhaul/bols/2025-11/OH-BOL-321678.pdf",
    ocr_extracted=True,
    extracted_data={
        "pieces": 18,
        "weight": 40000,
        "shipper": "Sun-Glo Corporation",
        "consignee": "Midwest Warehouse Solutions"
    }
)
```

---

### 7. **POD** - Proof of Delivery (Document Entity)

Proof of delivery and receiver sign-off.

**Complete Property List (20 properties):**

```yaml
# Primary Identifiers
pod_id: string                 # PRIMARY KEY - UUID
load_number: string            # FOREIGN KEY to Load

# Delivery Details
delivery_date: date
delivery_time: time (nullable)
delivery_location_id: string

# Receiver Verification
receiver_name: string
receiver_signature: string (nullable)
receiver_signature_time: timestamp (nullable)
receiver_company: string (nullable)

# Freight Verification
piece_count_delivered: integer
freight_condition: enum        # ["good", "damaged", "shortage", "overage"]
delivery_notes: text (nullable)
driver_name: string

# Exceptions
exception_type: enum (nullable)  # ["shortage", "damage", "refused", "none"]
exception_details: text (nullable)

# Document Management
document_path: string          # PDF location
ocr_extracted: boolean
extracted_data: object         # JSON - OCR results

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Example - Load OH-321678 POD:**
```python
POD(
    pod_id="pod_oh321678",
    load_number="OH-321678",
    delivery_date="2025-11-07",
    delivery_time="15:45",
    delivery_location_id="loc_midwest_dallas",
    receiver_name="Carlos Rodriguez",
    receiver_signature="signed",
    receiver_signature_time="2025-11-07T15:45:00Z",
    receiver_company="Midwest Warehouse Solutions",
    piece_count_delivered=18,
    freight_condition="good",
    delivery_notes="All 18 pallets delivered intact. No damage.",
    driver_name="Robert McCullough",
    exception_type="none",
    document_path="drive://openhaul/pods/2025-11/OH-POD-321678.pdf",
    ocr_extracted=True,
    extracted_data={
        "delivery_date": "2025-11-07",
        "pieces_delivered": 18,
        "receiver": "Carlos Rodriguez",
        "condition": "good"
    }
)
```

---

### 8. **Factor** - Factoring Company

Quick-pay financing service for carrier payments.

**Complete Property List (18 properties):**

```yaml
# Primary Identifiers
factor_id: string              # PRIMARY KEY - UUID
factor_name: string
factor_legal_name: string (nullable)

# Contact Information
primary_contact_person_id: string (nullable)  # Links to Hub 4
phone: string
email: string
address: string
city: string
state: string
zip: string

# Terms
fee_percentage: decimal        # e.g., 3.5%
advance_percentage: decimal    # e.g., 95%
payment_terms: string          # "Same-day funding" or "24-hour"
noa_required: boolean          # Notice of Assignment required?

# Status
active_status: boolean
total_loads_factored: integer (nullable)

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Example - Triumph Factoring:**
```python
Factor(
    factor_id="factor_triumph",
    factor_name="Triumph Business Capital",
    factor_legal_name="Triumph Business Capital, LLC",
    primary_contact_person_id="person_triumph_rep",
    phone="800-555-0150",
    email="funding@triumphcapital.com",
    address="123 Financial Plaza",
    city="Dallas",
    state="TX",
    zip="75201",
    fee_percentage=3.5,
    advance_percentage=95.0,
    payment_terms="Same-day funding upon POD receipt",
    noa_required=True,
    active_status=True,
    total_loads_factored=156
)
```

---

## Equipment Types (Complete List)

**Dry Vans:**
- `dry_van_53` - 53-foot dry van (most common)
- `dry_van_48` - 48-foot dry van
- `dry_van_28` - 28-foot pup trailer

**Refrigerated:**
- `reefer_53` - 53-foot refrigerated trailer
- `reefer_48` - 48-foot refrigerated trailer

**Flatbeds:**
- `flatbed_48` - 48-foot flatbed
- `flatbed_53` - 53-foot flatbed
- `step_deck` - Step deck / drop deck trailer

**Specialized:**
- `conestoga` - Curtain-side flatbed
- `power_only` - Power unit only (customer provides trailer)
- `hot_shot` - Expedited flatbed (pickup truck + trailer)
- `van_ltl` - Less-than-truckload van
- `box_truck` - Straight truck / box truck

---

## Load Status Lifecycle (Complete)

**Status Flow:**
```
pending → booked → dispatched → pickup_scheduled →
en_route_to_pickup → at_pickup → loading →
picked_up → in_transit → en_route_to_delivery →
at_delivery → unloading → delivered →
pod_received → invoiced → completed

# Alternative paths:
→ cancelled (any stage)
→ on_hold (any stage before picked_up)
```

**Status Definitions:**

- `pending` - Customer inquiry, not yet booked
- `booked` - Customer committed, no carrier assigned
- `dispatched` - Carrier assigned, rate confirmed
- `pickup_scheduled` - Pickup appointment set
- `en_route_to_pickup` - Truck heading to shipper
- `at_pickup` - Truck arrived at shipper
- `loading` - Freight being loaded
- `picked_up` - BOL signed, freight on truck
- `in_transit` - En route to delivery location
- `en_route_to_delivery` - Within 50 miles of delivery
- `at_delivery` - Truck arrived at receiver
- `unloading` - Freight being unloaded
- `delivered` - POD signed, freight delivered
- `pod_received` - POD document received by OpenHaul
- `invoiced` - Customer invoiced (Hub 5)
- `completed` - Payment received, load closed
- `cancelled` - Load cancelled before pickup
- `on_hold` - Temporarily paused (customer request, carrier issue, etc.)

---

## Accessorial Charges (Common Types)

**Detention:**
```python
{
    "type": "detention_pickup",
    "amount": 75.00,
    "hours": 2,
    "note": "Detained 2 hours at shipper beyond free time"
}
```

**Lumper Fees:**
```python
{
    "type": "lumper_fee",
    "amount": 150.00,
    "location": "delivery",
    "note": "Lumper service at receiver"
}
```

**Layover:**
```python
{
    "type": "layover",
    "amount": 200.00,
    "reason": "Weather delay - driver safety"
}
```

**TONU (Truck Ordered Not Used):**
```python
{
    "type": "tonu",
    "amount": 500.00,
    "reason": "Customer cancelled after truck dispatched"
}
```

**Other Common Types:**
- `detention_delivery` - Detention at receiver
- `reweigh_fee` - Truck had to reweigh at scale
- `pallet_exchange` - Pallet exchange service
- `driver_assist` - Driver helped load/unload
- `hazmat_fee` - Hazardous materials surcharge
- `fuel_surcharge` - Fuel price adjustment
- `tarping_fee` - Flatbed load tarping
- `overnight_fee` - Driver overnight stay
- `scale_ticket` - Certified weight ticket

---

## Document Types & Extraction Patterns

### Document Type 1: Sales Order (Customer PO)

**Source:** Email (PDF attachment or forwarded body)
**Example:** Sun-Glo sends "SG-PO-2025-1045.pdf" via email

**Key Fields to Extract:**
```yaml
# Customer Info
customer_name: "Sun-Glo Corporation"
customer_contact: "Shannon Martinez"
order_number: "SG-PO-2025-1045"
order_date: "2025-11-01"

# Pickup Details
pickup_location: "4500 Industrial Blvd, Chicago, IL 60601"
pickup_date: "2025-11-05"
pickup_time_window: "8am-5pm"
pickup_contact: "Shannon Martinez"
pickup_phone: "312-555-0199"

# Delivery Details
delivery_location: "2300 Distribution Way, Dallas, TX 75201"
delivery_date: "2025-11-07"
delivery_time_window: "flexible"
delivery_contact: "Carlos Rodriguez"
delivery_phone: "214-555-0288"

# Freight Details
equipment_type: "53' Dry Van"
weight: "40,000 lbs"
pieces: "18 pallets"
commodity: "Pet Food - Dry Kibble"

# Rate
rate: "$2,500.00"
payment_terms: "Net 30"

# Special Instructions
instructions: "Appointment required at pickup. Shannon prefers Friday pickups."
```

**Extraction Strategy:**
- Use Graphiti LLM extraction for PDF → structured data
- Cross-reference customer_name with Hub 4 (Contacts) → get customer_id
- Create Location entities if new addresses
- Create Load entity with status = "booked"
- Link SalesOrder document → Load

---

### Document Type 2: Rate Confirmation (Carrier Agreement)

**Source:** Email (PDF attachment) or TMS-generated
**Example:** OpenHaul sends "RC-2025-003456.pdf" to Origin Transport

**Key Fields to Extract:**
```yaml
# Load Reference
load_number: "OH-321678"
rate_con_number: "RC-2025-003456"
date: "2025-11-03"

# Carrier Info
carrier_name: "Origin Transport LLC"
carrier_mc: "MC-123456"
carrier_contact: "G (Richard Glaubitz)"
carrier_phone: "312-555-0100"

# Rate & Terms
rate: "$2,000.00"
payment_terms: "Net 15"
detention_rate: "$75.00/hour after 2 free hours"
lumper_reimbursement: "Yes"

# Load Details (repeat from sales order)
pickup_date: "2025-11-05"
pickup_location: "Sun-Glo Chicago Warehouse"
delivery_date: "2025-11-07"
delivery_location: "Midwest Warehouse, Dallas TX"

# Signatures
broker_signature: "signed"
carrier_signature: "signed"
signed_date: "2025-11-03"
```

**Extraction Strategy:**
- Match load_number to existing Load entity
- Match carrier_name to Carrier entity (or create if new)
- Store signed PDF in document_path
- Update Load entity: status = "dispatched", carrier_id = matched carrier

---

### Document Type 3: Bill of Lading (BOL)

**Source:** Email (scanned PDF from driver) or fax
**Example:** Driver sends BOL photo after pickup

**Key Fields to Extract:**
```yaml
# Load Reference
load_number: "OH-321678"
bol_number: "OH-BOL-321678"

# Pickup Details
pickup_date: "2025-11-05"
pickup_time: "10:15 AM"
shipper_name: "Sun-Glo Corporation"
shipper_address: "4500 Industrial Blvd, Chicago, IL 60601"

# Freight Details
pieces: 18
weight: "40,000 lbs"
pallets: 18
commodity: "Pet Food - Dry Kibble (palletized)"

# Signatures
shipper_signature: "Shannon Martinez"
driver_name: "Robert McCullough"
driver_signature: "signed"

# Condition
condition: "good"
condition_notes: "All 18 pallets loaded, shrink-wrapped, no visible damage"
```

**Extraction Strategy:**
- OCR scan BOL PDF for text extraction
- Match load_number to Load entity
- Create BOL document entity
- Update Load entity: status = "picked_up"
- Store BOL PDF in document_path

---

### Document Type 4: Proof of Delivery (POD)

**Source:** Email (scanned PDF from driver) or fax
**Example:** Driver sends POD photo after delivery

**Key Fields to Extract:**
```yaml
# Load Reference
load_number: "OH-321678"

# Delivery Details
delivery_date: "2025-11-07"
delivery_time: "3:45 PM"
receiver_name: "Carlos Rodriguez"
receiver_company: "Midwest Warehouse Solutions"
receiver_address: "2300 Distribution Way, Dallas, TX 75201"

# Freight Verification
pieces_delivered: 18
condition: "good"
delivery_notes: "All 18 pallets delivered intact. No damage."

# Signatures
receiver_signature: "Carlos Rodriguez"
driver_name: "Robert McCullough"

# Exceptions
exceptions: "None"
```

**Extraction Strategy:**
- OCR scan POD PDF
- Match load_number to Load entity
- Create POD document entity
- Update Load entity: status = "delivered"
- Trigger invoicing workflow (Hub 5)
- Store POD PDF in document_path

---

### Document Type 5: Lumper Receipt

**Source:** Email (photo from driver) or fax
**Example:** Driver pays lumper $150 at receiver, sends receipt

**Key Fields to Extract:**
```yaml
# Load Reference
load_number: "OH-321678"

# Lumper Info
lumper_company: "Midwest Unloading Services"
location: "Midwest Warehouse, Dallas TX"
date: "2025-11-07"
amount: "$150.00"
payment_method: "ComCheck"

# Receipt Details
receipt_number: "LMP-2025-9876"
service_description: "Unload 18 pallets pet food"
```

**Extraction Strategy:**
- OCR receipt image
- Match load_number to Load entity
- Add to Load.accessorial_charges[] array
- Create Expense in Hub 5 (reimbursable to carrier)

---

### Document Type 6: Detention Notice

**Source:** Email from carrier or driver
**Example:** Carrier emails "Truck detained 2 hours at shipper"

**Key Fields to Extract:**
```yaml
# Load Reference
load_number: "OH-321678"

# Detention Details
location: "pickup"
location_name: "Sun-Glo Chicago Warehouse"
arrival_time: "8:00 AM"
free_time_end: "10:00 AM"
departure_time: "12:15 PM"
detention_hours: 2
detention_rate: "$75.00/hour"
detention_total: "$150.00"

# Justification
reason: "Warehouse staff delayed loading due to forklift breakdown"
```

**Extraction Strategy:**
- Parse email body or PDF attachment
- Match load_number to Load entity
- Add to Load.accessorial_charges[] array
- Flag for review (some detention may be disputed)

---

### Document Type 7: Notice of Assignment (NOA)

**Source:** TMS-generated or manual email to factor
**Example:** OpenHaul sends NOA to Triumph Business Capital

**Key Fields to Extract:**
```yaml
# Load Reference
load_number: "OH-321678"
invoice_number: "INV-2025-005678"  # Hub 5 link

# Factor Info
factor_name: "Triumph Business Capital"
factor_email: "funding@triumphcapital.com"

# Assignment Details
customer_name: "Sun-Glo Corporation"
invoice_amount: "$2,500.00"
invoice_date: "2025-11-07"
payment_terms: "Net 30"

# Notification
sent_date: "2025-11-07"
customer_notified: true
```

**Extraction Strategy:**
- Match load_number to Load entity
- Match invoice_number to Invoice in Hub 5
- Link to Factor entity
- Record NOA sent (for factoring tracking)

---

## Real-World Example: Load OH-321678 (Complete Lifecycle)

**Scenario:** Sun-Glo Corporation ships 18 pallets of pet food from Chicago to Dallas via OpenHaul, hauled by Origin Transport Unit #6520.

### Complete Entity Set

**Load Entity:**
```python
Load(
    load_number="OH-321678",
    customer_reference="SG-PO-2025-1045",
    customer_id="company_sunglo",
    carrier_id="carr_origin",
    shipper_id="company_sunglo",
    consignee_id="company_midwest_warehouse",
    pickup_location_id="loc_sunglo_chicago",
    delivery_location_id="loc_midwest_dallas",
    pickup_date="2025-11-05",
    pickup_appointment_required=True,
    delivery_date="2025-11-07",
    equipment_type="dry_van_53",
    weight_lbs=40000,
    piece_count=18,
    commodity_description="Pet Food - Dry Kibble (palletized)",
    status="completed",
    customer_rate=2500.00,
    carrier_rate=2000.00,
    margin=500.00,
    accessorial_charges=[
        {"type": "detention_pickup", "amount": 75.00},
        {"type": "lumper_fee", "amount": 150.00}
    ]
)
```

**Database Distribution for OH-321678:**

**Neo4j (Relationship Memory):**
```cypher
// Core load relationships
(:Load {load_number: "OH-321678"})-[:BOOKED_FOR]->(:Company {company_id: "company_sunglo"})
(:Load)-[:HAULED_BY]->(:Carrier {carrier_id: "carr_origin"})
(:Load)-[:ASSIGNED_UNIT {unit_number: "6520"}]->(:Tractor {unit_number: "6520"})  // Hub 3 link
(:Load)-[:PICKS_UP_AT]->(:Location {location_id: "loc_sunglo_chicago"})
(:Load)-[:DELIVERS_TO]->(:Location {location_id: "loc_midwest_dallas"})

// Document relationships
(:SalesOrder {sales_order_id: "so_sunglo_1045"})-[:FOR_LOAD]->(:Load)
(:RateConfirmation {rate_con_id: "ratecon_oh321678"})-[:FOR_LOAD]->(:Load)
(:BOL {bol_id: "bol_oh321678"})-[:FOR_LOAD]->(:Load)
(:POD {pod_id: "pod_oh321678"})-[:FOR_LOAD]->(:Load)

// Financial links (Hub 5)
(:Load)-[:GENERATES]->(:Revenue {amount: 2500.00, source: "sun_glo"})
(:Load)-[:INCURS]->(:Expense {amount: 2000.00, category: "carrier_payment"})
(:Load)-[:CUSTOMER_INVOICE]->(:Invoice {invoice_id: "inv_sunglo_321678"})
```

**PostgreSQL (Factual Memory):**
```sql
-- loads table
SELECT * FROM loads WHERE load_number = 'OH-321678';
-- Returns: all 42 load properties

-- carriers table
SELECT * FROM carriers WHERE carrier_id = 'carr_origin';
-- Returns: Origin Transport complete profile

-- locations table
SELECT * FROM locations WHERE location_id IN ('loc_sunglo_chicago', 'loc_midwest_dallas');
-- Returns: both pickup and delivery location details

-- documents table
SELECT * FROM sales_orders WHERE load_number = 'OH-321678';
SELECT * FROM rate_confirmations WHERE load_number = 'OH-321678';
SELECT * FROM bols WHERE load_number = 'OH-321678';
SELECT * FROM pods WHERE load_number = 'OH-321678';
```

**Qdrant (Semantic Memory):**
```python
# Document embeddings for OH-321678
collection: "openhaul_documents"
points: [
    {
        "id": "so_sunglo_1045",
        "vector": [...],  # Embedding of sales order PDF
        "payload": {
            "document_type": "sales_order",
            "load_number": "OH-321678",
            "customer": "Sun-Glo Corporation",
            "text": "Full OCR text of sales order..."
        }
    },
    {
        "id": "ratecon_oh321678",
        "vector": [...],
        "payload": {
            "document_type": "rate_confirmation",
            "load_number": "OH-321678",
            "carrier": "Origin Transport LLC"
        }
    },
    {
        "id": "bol_oh321678",
        "vector": [...],
        "payload": {
            "document_type": "bol",
            "load_number": "OH-321678",
            "shipper": "Sun-Glo Corporation",
            "condition": "good"
        }
    },
    {
        "id": "pod_oh321678",
        "vector": [...],
        "payload": {
            "document_type": "pod",
            "load_number": "OH-321678",
            "receiver": "Midwest Warehouse Solutions",
            "condition": "good"
        }
    }
]
```

**Redis (Working Memory):**
```redis
# Active load tracking (while in-transit)
SET load:OH-321678:status "in_transit"
SET load:OH-321678:current_location "I-55 near Springfield, IL"
SET load:OH-321678:eta "2025-11-07T15:00:00Z"
SET load:OH-321678:last_update "2025-11-06T14:23:00Z"
EXPIRE load:OH-321678:* 86400  # 24-hour TTL

# After delivery, keys expire (data persists in PostgreSQL/Neo4j)
```

**Graphiti (Temporal Memory):**
```python
# Load lifecycle temporal tracking
Load_OH321678_Lifecycle = [
    {"status": "booked", "timestamp": "2025-11-03T14:30:00Z", "changed_by": "person_g"},
    {"status": "dispatched", "timestamp": "2025-11-03T15:00:00Z", "changed_by": "person_g"},
    {"status": "pickup_scheduled", "timestamp": "2025-11-04T10:00:00Z", "changed_by": "person_shannon"},
    {"status": "en_route_to_pickup", "timestamp": "2025-11-05T07:30:00Z", "driver": "Robert McCullough"},
    {"status": "at_pickup", "timestamp": "2025-11-05T08:00:00Z"},
    {"status": "loading", "timestamp": "2025-11-05T09:00:00Z"},
    {"status": "picked_up", "timestamp": "2025-11-05T10:15:00Z"},  # BOL signed
    {"status": "in_transit", "timestamp": "2025-11-05T10:30:00Z"},
    {"status": "at_delivery", "timestamp": "2025-11-07T15:00:00Z"},
    {"status": "delivered", "timestamp": "2025-11-07T15:45:00Z"},  # POD signed
    {"status": "pod_received", "timestamp": "2025-11-07T16:30:00Z"},
    {"status": "invoiced", "timestamp": "2025-11-07T17:00:00Z"},
    {"status": "completed", "timestamp": "2025-12-05T10:00:00Z"}  # Payment received
]

# Enables temporal queries:
# "What was the status of OH-321678 on November 6th at 2pm?" → "in_transit"
# "How long from pickup to delivery?" → 2 days, 5.5 hours
# "When did customer pay?" → December 5 (28 days after invoice)
```

---

## Advanced Query Patterns

### Query 1: Find All Loads for Customer in Date Range

```cypher
// Neo4j - Relationship traversal
MATCH (c:Company {company_id: "company_sunglo"})<-[:BOOKED_FOR]-(l:Load)
WHERE l.pickup_date >= date("2025-11-01")
  AND l.pickup_date <= date("2025-11-30")
RETURN l.load_number, l.pickup_date, l.status, l.customer_rate
ORDER BY l.pickup_date DESC
```

```sql
-- PostgreSQL - Factual query
SELECT
    load_number,
    pickup_date,
    delivery_date,
    status,
    customer_rate,
    carrier_rate,
    margin
FROM loads
WHERE customer_id = 'company_sunglo'
  AND pickup_date BETWEEN '2025-11-01' AND '2025-11-30'
ORDER BY pickup_date DESC;
```

---

### Query 2: Carrier Performance Report (On-Time %)

```sql
-- PostgreSQL - Performance metrics
SELECT
    c.carrier_name,
    COUNT(*) as total_loads,
    SUM(CASE WHEN l.delivery_date <= l.scheduled_delivery_date THEN 1 ELSE 0 END) as on_time_loads,
    ROUND(
        (SUM(CASE WHEN l.delivery_date <= l.scheduled_delivery_date THEN 1 ELSE 0 END)::decimal / COUNT(*)) * 100,
        2
    ) as on_time_percentage
FROM loads l
JOIN carriers c ON l.carrier_id = c.carrier_id
WHERE l.status = 'completed'
  AND l.pickup_date >= '2025-01-01'
GROUP BY c.carrier_name
ORDER BY on_time_percentage DESC;
```

---

### Query 3: Find Loads with Similar Freight (Semantic Search)

```python
# Qdrant - Semantic search
query_text = "18 pallets of pet food, 40,000 lbs"
results = qdrant_client.search(
    collection_name="openhaul_documents",
    query_vector=embed(query_text),
    limit=10,
    filter={
        "must": [
            {"key": "document_type", "match": {"value": "sales_order"}}
        ]
    }
)
# Returns: Similar loads by semantic similarity (not exact keyword match)
```

---

### Query 4: Lane Analysis (Most Profitable Routes)

```sql
-- PostgreSQL - Lane profitability
WITH lane_stats AS (
    SELECT
        CONCAT(pl.state, '-', dl.state) as lane,
        COUNT(*) as load_count,
        AVG(l.margin) as avg_margin,
        AVG(l.customer_rate) as avg_customer_rate,
        AVG(l.carrier_rate) as avg_carrier_rate
    FROM loads l
    JOIN locations pl ON l.pickup_location_id = pl.location_id
    JOIN locations dl ON l.delivery_location_id = dl.location_id
    WHERE l.status = 'completed'
      AND l.pickup_date >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY CONCAT(pl.state, '-', dl.state)
    HAVING COUNT(*) >= 5  -- Minimum 5 loads for statistical significance
)
SELECT
    lane,
    load_count,
    ROUND(avg_margin, 2) as avg_margin,
    ROUND(avg_customer_rate, 2) as avg_customer_rate,
    ROUND(avg_carrier_rate, 2) as avg_carrier_rate,
    ROUND((avg_margin / avg_customer_rate) * 100, 2) as margin_percentage
FROM lane_stats
ORDER BY avg_margin DESC
LIMIT 10;
```

---

### Query 5: Origin-as-Carrier Performance

```cypher
// Neo4j - Find all loads hauled by Origin trucks
MATCH (l:Load)-[:HAULED_BY]->(c:Carrier {carrier_id: "carr_origin"})
MATCH (l)-[:ASSIGNED_UNIT]->(t:Tractor)
WHERE l.pickup_date >= date("2025-01-01")
RETURN
    t.unit_number as truck,
    COUNT(l) as loads_hauled,
    AVG(l.carrier_rate) as avg_revenue_per_load,
    SUM(l.carrier_rate) as total_revenue
ORDER BY loads_hauled DESC
```

---

### Query 6: Detention Analysis (Most Common Locations)

```sql
-- PostgreSQL - Detention hotspots
WITH detention_data AS (
    SELECT
        l.load_number,
        loc.location_name,
        loc.city,
        loc.state,
        jsonb_array_elements(l.accessorial_charges) as charge
    FROM loads l
    JOIN locations loc ON l.pickup_location_id = loc.location_id OR l.delivery_location_id = loc.location_id
    WHERE l.status = 'completed'
      AND l.accessorial_charges IS NOT NULL
)
SELECT
    location_name,
    city,
    state,
    COUNT(*) as detention_count,
    ROUND(AVG((charge->>'amount')::decimal), 2) as avg_detention_cost
FROM detention_data
WHERE charge->>'type' IN ('detention_pickup', 'detention_delivery')
GROUP BY location_name, city, state
HAVING COUNT(*) >= 3
ORDER BY detention_count DESC
LIMIT 10;
```

---

### Query 7: Load Document Completeness Check

```cypher
// Neo4j - Find loads missing documents
MATCH (l:Load)
WHERE l.status IN ['delivered', 'invoiced', 'completed']
  AND l.pickup_date >= date("2025-11-01")
OPTIONAL MATCH (so:SalesOrder)-[:FOR_LOAD]->(l)
OPTIONAL MATCH (rc:RateConfirmation)-[:FOR_LOAD]->(l)
OPTIONAL MATCH (bol:BOL)-[:FOR_LOAD]->(l)
OPTIONAL MATCH (pod:POD)-[:FOR_LOAD]->(l)
WITH l,
     CASE WHEN so IS NOT NULL THEN 1 ELSE 0 END as has_so,
     CASE WHEN rc IS NOT NULL THEN 1 ELSE 0 END as has_rc,
     CASE WHEN bol IS NOT NULL THEN 1 ELSE 0 END as has_bol,
     CASE WHEN pod IS NOT NULL THEN 1 ELSE 0 END as has_pod
WHERE has_so + has_rc + has_bol + has_pod < 4
RETURN
    l.load_number,
    l.status,
    has_so as has_sales_order,
    has_rc as has_rate_con,
    has_bol as has_bol,
    has_pod as has_pod
ORDER BY l.pickup_date DESC
```

---

### Query 8: Customer Payment Behavior Analysis

```cypher
// Neo4j + Hub 5 integration
MATCH (c:Company)<-[:BOOKED_FOR]-(l:Load)-[:CUSTOMER_INVOICE]->(inv:Invoice)
WHERE l.status = 'completed'
  AND inv.paid_date IS NOT NULL
WITH c,
     COUNT(l) as total_loads,
     AVG(duration.between(inv.invoice_date, inv.paid_date).days) as avg_payment_days,
     SUM(CASE WHEN duration.between(inv.invoice_date, inv.paid_date).days <= 30 THEN 1 ELSE 0 END) as on_time_payments
RETURN
    c.company_name,
    total_loads,
    avg_payment_days,
    ROUND((on_time_payments * 1.0 / total_loads) * 100, 2) as on_time_percentage
ORDER BY total_loads DESC
```

---

### Query 9: Carrier Preferred Lanes (Recommendation Engine)

```cypher
// Neo4j - Find carriers who frequently haul similar lanes
MATCH (l:Load)-[:HAULED_BY]->(c:Carrier)
MATCH (l)-[:PICKS_UP_AT]->(pl:Location)
MATCH (l)-[:DELIVERS_TO]->(dl:Location)
WHERE pl.state = 'IL' AND dl.state = 'TX'  // Looking for IL → TX carriers
  AND l.status = 'completed'
  AND l.pickup_date >= date() - duration({months: 6})
WITH c, COUNT(l) as lane_frequency
WHERE lane_frequency >= 3  // At least 3 loads on this lane
RETURN
    c.carrier_name,
    c.rating,
    lane_frequency,
    c.phone,
    c.email
ORDER BY lane_frequency DESC, c.rating DESC
LIMIT 5
```

---

### Query 10: Load Lifecycle Duration Analysis

```python
# Graphiti - Temporal analysis
query = """
For loads completed in the last 3 months, what is the average time spent in each status?
"""

# Returns:
# booked → dispatched: avg 2.5 hours
# dispatched → picked_up: avg 1.8 days
# picked_up → delivered: avg 2.1 days
# delivered → invoiced: avg 4.5 hours
# invoiced → completed: avg 28 days (payment cycle)
```

---

## Cross-Hub Integration Patterns

### Hub 2 → Hub 3 (Origin Transport)

**When Origin Truck Hauls OpenHaul Load:**

```cypher
// Neo4j - Complete integration
(:Load {load_number: "OH-321678"})-[:HAULED_BY]->(:Carrier {carrier_id: "carr_origin"})
(:Load)-[:ASSIGNED_UNIT {unit_number: "6520"}]->(:Tractor {unit_number: "6520"})

// Track in both directions
(:Tractor {unit_number: "6520"})-[:HAULS]->(:Load {load_number: "OH-321678"})

// Enables queries:
// "What loads did Unit #6520 haul this month?"
// "Which Origin trucks are available for OpenHaul loads?"
```

**Fuel & Maintenance Attribution:**
```cypher
// When Origin truck hauls OpenHaul load, attribute costs
(:Load {load_number: "OH-321678"})-[:ASSIGNED_UNIT]->(:Tractor {unit_number: "6520"})
(:Tractor)-[:CONSUMES]->(:FuelTransaction {transaction_date: "2025-11-06"})
(:Tractor)-[:INCURS]->(:MaintenanceRecord {service_date: "2025-11-10"})

// Enables cost allocation:
// "What were the fuel costs for OH-321678?" (via Unit #6520 fuel during load dates)
// "Maintenance costs attributable to OpenHaul loads this quarter?"
```

---

### Hub 2 → Hub 4 (Contacts)

**Customer Relationships:**
```cypher
// Load links to customer company
(:Load {load_number: "OH-321678"})-[:BOOKED_FOR]->(:Company {company_id: "company_sunglo"})

// Location links to contacts
(:Location {location_id: "loc_sunglo_chicago"})-[:PRIMARY_CONTACT]->(:Person {person_id: "person_shannon"})

// Enables queries:
// "Who's the contact for Sun-Glo shipments?"
// "All loads for Shannon's locations?"
```

**Carrier Relationships:**
```cypher
// Carrier managed by contact person
(:Carrier {carrier_id: "carr_abc"})-[:MANAGED_BY]->(:Person {person_id: "person_john_driver"})
(:Carrier)-[:COMPANY_ENTITY]->(:Company {company_id: "company_abc_trucking"})

// Track communication
(:Person {person_id: "person_john_driver"})-[:SENT]->(:CommunicationLog {
    date: "2025-11-03",
    subject: "Rate confirmation for OH-321678",
    sentiment_score: 85
})
```

---

### Hub 2 → Hub 5 (Financials)

**Revenue Generation:**
```cypher
// Load creates customer invoice
(:Load {load_number: "OH-321678"})-[:GENERATES]->(:Revenue {
    amount: 2500.00,
    source: "sun_glo_payment",
    revenue_date: "2025-12-05"
})

// Invoice linkage
(:Load)-[:CUSTOMER_INVOICE]->(:Invoice {
    invoice_id: "inv_sunglo_321678",
    invoice_date: "2025-11-07",
    amount: 2500.00,
    due_date: "2025-12-07",
    paid_date: "2025-12-05",
    payment_terms: "net_30"
})
```

**Expense Creation (Carrier Payment):**
```cypher
// Load incurs carrier payment expense
(:Load {load_number: "OH-321678"})-[:INCURS]->(:Expense {
    amount: 2000.00,
    category: "carrier_payment",
    expense_date: "2025-11-10",
    payee: "Origin Transport LLC"
})

// Carrier invoice
(:Load)-[:CARRIER_INVOICE]->(:Invoice {
    invoice_id: "inv_carrier_321678",
    amount: 2000.00,
    paid_date: "2025-11-10"
})
```

**Accessorial Charges:**
```cypher
// Detention as reimbursable expense
(:Load {load_number: "OH-321678"})-[:INCURS]->(:Expense {
    category: "detention",
    amount: 75.00,
    reimbursable: true,
    payee: "Origin Transport LLC"
})

// Lumper fee reimbursement
(:Load)-[:INCURS]->(:Expense {
    category: "lumper_fee",
    amount: 150.00,
    reimbursable: true,
    payee: "Origin Transport LLC"
})
```

**Factoring Integration:**
```cypher
// Customer invoice factored
(:Invoice {invoice_id: "inv_sunglo_321678"})-[:FACTORED_BY]->(:Factor {factor_id: "factor_triumph"})

// Factoring fee as expense
(:Factor)-[:CHARGES_FEE]->(:Expense {
    category: "factoring_fee",
    amount: 87.50,  // 3.5% of $2,500
    expense_date: "2025-11-08"
})

// Factor payment (quick pay)
(:Factor)-[:PAID]->(:Payment {
    amount: 2375.00,  // 95% advance
    payment_date: "2025-11-08"
})
```

---

### Hub 2 → Hub 6 (Corporate)

**Company Ownership:**
```cypher
// OpenHaul owns loads
(:Company {company_name: "OpenHaul LLC"})-[:OWNS]->(:Load {load_number: "OH-321678"})

// Broker authority
(:Load)-[:REQUIRES]->(:License {
    license_type: "broker_authority",
    license_number: "MC-234567",
    issued_to: "OpenHaul LLC",
    expiry_date: "2026-12-31"
})
```

**Insurance Requirements:**
```cypher
// Load requires insurance
(:Load {load_number: "OH-321678"})-[:COVERED_BY]->(:Insurance {
    policy_type: "cargo",
    coverage_amount: 100000.00,
    policy_holder: "OpenHaul LLC"
})
```

---

## Bi-Temporal Tracking Patterns

### Example 1: Load Status Evolution

**Track both "when it happened" (valid_time) and "when we learned it" (transaction_time):**

```cypher
// Historical status records
(:Load {load_number: "OH-321678"})-[:HAD_STATUS {
    status: "booked",
    valid_from: "2025-11-03T14:30:00Z",
    valid_to: "2025-11-03T15:00:00Z",
    transaction_time: "2025-11-03T14:30:00Z"
}]

(:Load)-[:HAD_STATUS {
    status: "dispatched",
    valid_from: "2025-11-03T15:00:00Z",
    valid_to: "2025-11-05T10:15:00Z",
    transaction_time: "2025-11-03T15:00:00Z"
}]

(:Load)-[:HAD_STATUS {
    status: "picked_up",
    valid_from: "2025-11-05T10:15:00Z",
    valid_to: "2025-11-07T15:45:00Z",
    transaction_time: "2025-11-05T10:30:00Z"  // We learned about pickup 15 min later
}]

// Current status
(:Load)-[:CURRENT_STATUS {
    status: "completed",
    valid_from: "2025-12-05T10:00:00Z",
    valid_to: null,  // Still current
    transaction_time: "2025-12-05T10:00:00Z"
}]
```

**Enables temporal queries:**
- "What was the status of OH-321678 on November 6th at 2pm?" → Query valid_from/valid_to
- "When did we learn the load was picked up?" → Query transaction_time
- "Show me the complete status history" → All HAD_STATUS relationships

---

### Example 2: Carrier Rate Changes

**Track rate evolution for same lane over time:**

```cypher
// Q1 2025 rate
(:Carrier {carrier_id: "carr_origin"})-[:HAD_RATE {
    lane: "IL-TX",
    equipment: "dry_van_53",
    rate: 1800.00,
    valid_from: "2025-01-01",
    valid_to: "2025-03-31",
    transaction_time: "2024-12-15"  // Negotiated in December
}]

// Q2 2025 rate (fuel surcharge increase)
(:Carrier)-[:HAD_RATE {
    lane: "IL-TX",
    equipment: "dry_van_53",
    rate: 2000.00,
    valid_from: "2025-04-01",
    valid_to: null,  // Current rate
    transaction_time: "2025-03-20"  // Negotiated in March
}]

// Enables queries:
// "What was Origin's IL-TX rate in February?" → $1,800
// "When did rates increase?" → April 1, 2025
// "What loads were affected by rate change?" → All loads after April 1
```

---

## Database Distribution Summary

### Neo4j (Relationship Memory)
**Stores:**
- Load nodes (basic identifying properties)
- Carrier nodes
- Location nodes
- Company nodes (from Hub 4)
- All relationships (load → customer, load → carrier, load → locations, load → documents)
- Cross-hub relationships (load → tractor, load → invoice)
- Temporal relationships (HAD_STATUS, HAD_RATE)

**Why:** Graph traversal for complex queries like "Show all loads for Sun-Glo shipped through Chicago to Texas carriers rated 4+ stars" requires multi-hop relationship navigation.

---

### PostgreSQL (Factual Memory)
**Stores:**
- Complete load details (all 42 properties)
- Complete carrier profiles (all 38 properties)
- Complete location details (all 28 properties)
- Document metadata (SalesOrder, RateConfirmation, BOL, POD - all fields)
- Factor details
- Structured accessorial charges

**Why:** Structured analytical queries like "Average margin by customer" or "Carrier performance metrics" require SQL aggregations and JOINs.

---

### Qdrant (Semantic Memory)
**Stores:**
- Document embeddings (PDFs of sales orders, rate cons, BOLs, PODs)
- Location notes/restrictions embeddings
- Carrier performance notes embeddings
- Load commodity descriptions

**Why:** Semantic search like "Find loads similar to this one" or "Search BOLs mentioning damage" requires vector similarity, not keyword matching.

---

### Redis (Working Memory)
**Stores:**
- Active loads (status = in-transit) with current location and ETA (60s TTL)
- Available carriers by lane (for quick dispatch matching)
- Recent load bookings (rolling 24-hour window)
- Real-time driver location (if tracking via Samsara)

**Why:** Real-time dispatch dashboard needs <100ms response times for "Which loads are in transit right now?" queries.

---

### Graphiti (Temporal Memory)
**Stores:**
- Load lifecycle complete (all status changes with timestamps)
- Carrier performance trends over time
- Customer shipping pattern evolution (frequency, volume, lanes)
- Margin changes by lane over time
- Relationship strength evolution (customer, carrier, location)

**Why:** Temporal queries like "How has carrier performance changed in Q4?" or "When did this customer start shipping more frequently?" require time-series pattern detection.

---

## Completion Status

**Hub 2 Complete Baseline:**
- ✅ **Entities Defined:** 8 core entities with 201 properties total
  - Load: 42 properties
  - Carrier: 38 properties
  - Location: 28 properties
  - SalesOrder: 15 properties
  - RateConfirmation: 18 properties
  - BOL: 22 properties
  - POD: 20 properties
  - Factor: 18 properties
- ✅ **Equipment Types:** 13 types documented
- ✅ **Load Statuses:** 18 lifecycle statuses documented
- ✅ **Accessorial Charges:** 12 common types documented
- ✅ **Relationships Documented:** 15+ relationship types with properties
- ✅ **Database Distribution:** Clear mapping for all 5 databases
- ✅ **Real-World Example:** Load OH-321678 (Sun-Glo to Dallas) complete lifecycle
- ✅ **Document Types:** 7 documents with extraction patterns
- ✅ **Extraction Patterns:** Documented for each document type
- ✅ **Advanced Queries:** 10 query patterns documented
- ✅ **Cross-Hub Links:** Complete integration with Hubs 3, 4, 5, 6
- ✅ **Bi-Temporal Tracking:** Status evolution and rate change patterns documented
- ✅ **Primary Keys:** load_number strategy defined and exemplified
- ✅ **Real-World Grounding:** Built from freight brokerage industry standards

**This matches the TARGET LEVEL OF DETAIL from Hub 3 and Hub 4.**

---

## For Implementation Reference

**Cross-References:**
1. **Hub 3 (Origin Transport)** - [HUB-3-ORIGIN-BASELINE.md](HUB-3-ORIGIN-BASELINE.md)
   - Origin trucks as carriers for OpenHaul loads
   - Unit assignment tracking
   - Fuel/maintenance cost attribution

2. **Hub 4 (Contacts)** - [HUB-4-CONTACTS-COMPLETE.md](HUB-4-CONTACTS-COMPLETE.md)
   - Customer relationships (companies)
   - Location contacts (people)
   - Carrier contacts
   - Communication tracking

3. **Hub 5 (Financials)** - [HUB-5-FINANCIALS-COMPLETE.md](HUB-5-FINANCIALS-COMPLETE.md)
   - Revenue from customer invoices
   - Expenses for carrier payments
   - Factoring integration
   - Accessorial charge billing

4. **Hub 6 (Corporate)** - [6-HUB-OVERVIEW.md](6-HUB-OVERVIEW.md)
   - OpenHaul LLC entity structure
   - Broker authority licenses
   - Insurance requirements

5. **Additional Schema Details** - [Additional Schema info.md](Additional%20Schema%20info.md)
   - Extended property definitions
   - Implementation notes

6. **Example Connections** - [example entity connections.md](example%20entity%20connections.md)
   - Complete relationship walkthrough
   - Cross-hub integration examples

---

**Baseline Established:** November 4, 2025
**Schema Version:** v2.0 (Complete Baseline)
**Completion:** 95% (matches Hub 3 and Hub 4 detail level)
