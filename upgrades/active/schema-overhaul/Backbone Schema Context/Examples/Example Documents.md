# APEX MEMORY - EXAMPLE DOCUMENTS
**Supporting Document for Schema v2.0**  
**Date:** November 1, 2025

---

## DOCUMENT 1: Fleetone Fuel Invoice

**Filename:** `EFS_Statement_2025-10-30.pdf`  
**Source:** Weekly email every Friday  
**Storage:** `/Fuel-Invoices/2025/EFS_Statement_2025-10-30.pdf`

### Header Information
```
Statement Date: 10/30/2025
Statement Period: 10/24/2025 - 10/30/2025
Customer Number: 3770001904412
Statement Number: 91812235
Customer: Origin Transport
Address: 6030 S YELLOWSTONE HWY, IDAHO FALLS, ID 83402
```

### Summary Section
```
Fuel Type    Count    Volume      Net Total
Diesel       84       9,610.74    $32,127.12
Reefer       33       561.75      $1,900.39
DEF          45       434.62      $1,857.50

Total Statement: $40,622.15
```

### Transaction Detail Example
```
DATE       CATEGORY    CARD   UNIT              LOCATION NAME           ST   QTY      GROSS PPG   TOTAL AMT
10/24/25   Diesel      00445  N-Robert          PILOT 353               KY   44.110   3.699       144.62
                              McCullough
10/24/25   DEF         00445  N-Robert          PILOT 353               KY   5.350    4.399       24.03
                              McCullough
10/24/25   Diesel      00726  N-Raven           PILOT 1175              AZ   99.330   3.999       346.87
                              Stoddard
10/24/25   Reefer      00726  N-Raven           PILOT 1175              AZ   24.470   3.999       85.45
                              Stoddard
```

### Key Extraction Points
```yaml
Transaction Date: 10/24/25
Fuel Type: Diesel, DEF, Reefer
Card Last 5: 00445, 00726
Driver Name: "N-Robert McCullough", "N-Raven Stoddard"
Location: PILOT 353, PILOT 1175
State: KY, AZ
Gallons: 44.110, 5.350, 99.330, 24.470
Price Per Gallon: 3.699, 4.399, 3.999
Total Amount: 144.62, 24.03, 346.87, 85.45

Matching Challenge:
  - Unit number NOT explicitly listed
  - Must derive from driver name + Samsara assignment
  - Driver "N-Robert McCullough" → Query Samsara → Find assigned unit
  - Verify with transaction location matching truck GPS
```

---

## DOCUMENT 2: Maintenance Receipt

**Filename:** `6520-repair-invoice-2025-10-15.pdf`  
**Source:** Service shop email/paper receipt  
**Storage:** `/Trucks/Unit-6520/Maintenance/2025-10-15-repair-invoice.pdf`

### Example Content
```
PHOENIX TRUCK REPAIR
789 Service Road
Phoenix, AZ 85001
(602) 555-0700

INVOICE #: PTR-2025-10487
Date: October 15, 2025

Vehicle Information:
  Unit #: 6520
  VIN: 1XKYDP9X3NJ124351
  Make: Kenworth
  Model: T680
  Odometer: 127,540 miles

Service Performed:
  - Oil change (15W-40)
  - Oil filter replacement
  - Air filter replacement
  - Coolant system flush
  - DOT inspection

Parts:
  Oil (12 gal)                 $84.00
  Oil filter                   $28.50
  Air filter                   $42.00
  Coolant (3 gal)              $36.00
                        TOTAL: $190.50

Labor:
  4.5 hours @ $125/hr         $562.50

TOTAL DUE:                    $753.00

Payment Method: Fleet Credit Card
Paid in Full: 10/15/2025

Next Service Due: 142,540 miles (15,000 mile interval)
```

### Key Extraction Points
```yaml
Unit Number: "6520" (FOUND - primary identifier)
VIN: "1XKYDP9X3NJ124351" (secondary identifier)
Service Date: "October 15, 2025"
Odometer: 127,540
Service Type: ["preventive", "oil_change", "inspection"]
Description: "Oil change, filters, coolant flush, DOT inspection"
Vendor: "Phoenix Truck Repair"
Cost Parts: $190.50
Cost Labor: $562.50
Total Cost: $753.00
Invoice Number: "PTR-2025-10487"
Next Service Due: 142,540 miles
```

---

## DOCUMENT 3: Purchase Agreement

**Filename:** `6520-purchase-agreement.pdf`  
**Source:** Dealer/seller  
**Storage:** `/Trucks/Unit-6520/Purchase/purchase-agreement.pdf`

### Example Content
```
VEHICLE PURCHASE AGREEMENT

Seller: Heavy Duty Truck Sales LLC
Buyer: Origin Transport LLC
Date: June 15, 2023

Vehicle Description:
  Year: 2023
  Make: Kenworth
  Model: T680
  VIN: 1XKYDP9X3NJ124351
  Odometer: 8,450 miles
  Color: White
  Engine: PACCAR MX-13, 455HP
  Transmission: Eaton Fuller 10-speed
  
Purchase Price: $165,000.00

Payment Terms:
  Down Payment: $35,000.00
  Financed Amount: $130,000.00
  Lender: Commercial Capital Bank
  Interest Rate: 6.5% APR
  Term: 60 months
  Monthly Payment: $2,537.00
  First Payment Due: July 15, 2023

Signatures:
[Buyer Signature]
[Seller Signature]
```

### Key Extraction Points
```yaml
VIN: "1XKYDP9X3NJ124351" (PRIMARY identifier)
Make: "Kenworth"
Model: "T680"
Year: 2023
Purchase Date: June 15, 2023
Purchase Price: $165,000.00
Financing Status: "financed"
Lender Name: "Commercial Capital Bank"
Loan Amount: $130,000.00
Interest Rate: 6.5%
Monthly Payment: $2,537.00
Engine: "PACCAR MX-13, 455HP"
Transmission: "Eaton Fuller 10-speed"

Note: Unit number "6520" may be assigned later by owner
```

---

## DOCUMENT 4: Insurance Policy

**Filename:** `6520-insurance-policy-2025.pdf`  
**Source:** Insurance company  
**Storage:** `/Trucks/Unit-6520/Insurance/policy-2025.pdf`

### Example Content
```
COMMERCIAL AUTO INSURANCE POLICY

Policy Holder: Origin Transport LLC
Policy Number: CA-2025-847392
Effective Date: January 1, 2025
Expiration Date: January 1, 2026

Coverage Details:
  Liability: $1,000,000 per occurrence
  Physical Damage: Actual Cash Value
  Comprehensive Deductible: $1,000
  Collision Deductible: $2,500
  Cargo: $100,000

Covered Vehicles:
  Vehicle #1:
    Unit #: 6520
    VIN: 1XKYDP9X3NJ124351
    Year: 2023
    Make: Kenworth
    Model: T680
    Stated Value: $145,000
    
Premium Schedule:
  Annual Premium: $14,400.00
  Monthly Premium: $1,200.00
  Payment Method: Automatic Withdrawal

Agent: Southwest Insurance Services
Phone: (702) 555-0800
Policy Type: Commercial Trucking
```

### Key Extraction Points
```yaml
Unit Number: "6520" (FOUND)
VIN: "1XKYDP9X3NJ124351"
Policy Number: "CA-2025-847392"
Insurance Provider: "Southwest Insurance Services"
Coverage Type: ["liability", "physical_damage", "comprehensive", "collision", "cargo"]
Coverage Amount: $1,000,000 (liability)
Deductible: $1,000 (comprehensive), $2,500 (collision)
Monthly Premium: $1,200.00
Annual Premium: $14,400.00
Policy Start: January 1, 2025
Policy Expiry: January 1, 2026
Stated Value: $145,000
```

---

## DOCUMENT 5: Spec Sheet

**Filename:** `kenworth-t680-specs.pdf`  
**Source:** Manufacturer  
**Storage:** `/Trucks/Unit-6520/Specs/kenworth-t680-specs.pdf`

### Example Content
```
KENWORTH T680 SPECIFICATIONS

Model Year: 2023
VIN: 1XKYDP9X3NJ124351

ENGINE
  Make: PACCAR
  Model: MX-13
  Displacement: 12.9L
  Horsepower: 455 HP @ 1,600 RPM
  Torque: 1,650 lb-ft @ 1,100 RPM
  Emissions: EPA 2021 Compliant

TRANSMISSION
  Make: Eaton Fuller
  Model: Advantage 10-Speed
  Type: Automated Manual
  
AXLES
  Front: 12,000 lb capacity
  Rear: Tandem, 40,000 lb capacity
  Ratio: 3.42

SUSPENSION
  Front: Hendrickson HAS-40
  Rear: Hendrickson PRIMAAX EX

FUEL SYSTEM
  Tank 1: 100 gallons (driver side)
  Tank 2: 100 gallons (passenger side)
  Total Capacity: 200 gallons
  DEF Tank: 22 gallons

DIMENSIONS
  Wheelbase: 244"
  GVWR: 80,000 lbs
  GAWR Front: 12,000 lbs
  GAWR Rear: 40,000 lbs

BRAKES
  Service: Air disc
  ABS: Standard
  
ELECTRICAL
  Batteries: Dual 12V
  Alternator: 160 amp
```

### Key Extraction Points
```yaml
VIN: "1XKYDP9X3NJ124351"
Make: "Kenworth"
Model: "T680"
Year: 2023
Engine Type: "PACCAR MX-13, 12.9L, 455HP"
Transmission Type: "Eaton Fuller Advantage 10-Speed"
Axle Configuration: "6x4 (Tandem)"
Fuel Capacity: 200 gallons
Weight Rating: 80,000 lbs GVWR
```

---

## DOCUMENT 6: Samsara API Response

**Source:** Real-time API call  
**Endpoint:** `/fleet/vehicles/{id}`

### Example JSON Response
```json
{
  "vehicle": {
    "id": "281489456700747",
    "name": "6520",
    "vin": "1XKYDP9X3NJ124351",
    "make": "Kenworth",
    "model": "T680",
    "year": 2023,
    "licensePlate": "NV-82749",
    "status": "active",
    "odometer": 127893,
    "engineHours": 4832,
    "location": {
      "latitude": 36.1699,
      "longitude": -115.1398,
      "address": "Las Vegas, NV 89101",
      "timestamp": "2025-11-01T10:30:00Z"
    },
    "driver": {
      "id": "driver_robert_mccullough",
      "name": "Robert McCullough"
    },
    "lastUpdated": "2025-11-01T10:30:00Z"
  }
}
```

### Key Data Points
```yaml
Unit Number: "6520" (from name field)
VIN: "1XKYDP9X3NJ124351"
Make: "Kenworth"
Model: "T680"
Year: 2023
Status: "active"
Current Miles: 127,893
Engine Hours: 4,832
Location GPS: {latitude: 36.1699, longitude: -115.1398}
Location Address: "Las Vegas, NV 89101"
Current Driver ID: "driver_robert_mccullough"
Current Driver Name: "Robert McCullough"
Last Updated: "2025-11-01T10:30:00Z"
```

---

## DOCUMENT 7: Loan Payoff Statement

**Filename:** `6520-loan-payoff-2025-09.pdf`  
**Source:** Lender  
**Storage:** `/Trucks/Unit-6520/Purchase/loan-payoff-2025-09.pdf`

### Example Content
```
LOAN PAYOFF STATEMENT

Lender: Commercial Capital Bank
Account Number: 847362-9284
Date: September 1, 2025

Borrower: Origin Transport LLC
Collateral: 2023 Kenworth T680
VIN: 1XKYDP9X3NJ124351

Original Loan Amount: $130,000.00
Interest Rate: 6.5% APR
Original Term: 60 months
Origination Date: July 15, 2023

Payment History:
  Total Payments Made: 26
  Amount Paid to Date: $65,962.00

Current Balance:
  Principal Balance: $58,742.00
  Accrued Interest: $315.00
  Payoff Amount: $59,057.00
  
Payoff Good Through: September 30, 2025
Daily Interest Accrual: $10.48

Paid in Full: September 15, 2025
Final Payment: $59,057.00
Title Released: September 20, 2025
```

### Key Extraction Points
```yaml
VIN: "1XKYDP9X3NJ124351"
Lender: "Commercial Capital Bank"
Original Loan: $130,000.00
Interest Rate: 6.5%
Loan Start: July 15, 2023
Payoff Date: September 15, 2025
Final Payment: $59,057.00
Status: "Paid in Full"

Update Required:
  - Tractor.financing_status: "financed" → "owned"
  - Tractor.loan_balance: $58,742 → $0
  - Tractor.valid_to: September 15, 2025 (for financed state)
  - Tractor.valid_from: September 15, 2025 (for owned state)
```

---

**END OF EXAMPLE DOCUMENTS** ✅

**Note:** These examples show the REAL data formats that Graphiti will need to parse and extract from. Each document type has specific patterns and identifiers that the system should look for.
