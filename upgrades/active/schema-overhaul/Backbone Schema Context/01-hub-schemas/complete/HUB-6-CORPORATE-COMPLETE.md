# HUB 6: CORPORATE INFRASTRUCTURE - COMPLETE

**Status:** ✅ Complete Baseline (95%)
**Purpose:** Legal structure, compliance, brand assets, company foundations
**Focus:** Foundational elements that enable businesses to exist and operate legally
**Primary Key Strategy:** entity_id for LegalEntity, UUIDs for supporting entities

---

## Purpose

Hub 6 tracks the foundational elements that enable the businesses to exist and operate legally. This includes legal entity structure, licenses, compliance filings, brand assets, and company documentation.

**Key Distinction:** This hub is **NON-OPERATIONAL**. It's the foundation that day-to-day operations (Hubs 2, 3, 5) run on top of.

**What Goes Here:**
- Legal entity structure (LLCs, ownership)
- Operating agreements, formation documents
- Business licenses, authority registrations
- Annual filings, compliance documents
- Brand assets (logos, domains, trademarks)
- Company story, mission, vision documents
- Marketing materials, business plans
- Awards, certifications, industry memberships

**What Does NOT Go Here:**
- Day-to-day operations (Hub 2, 3)
- Financial transactions (Hub 5)
- Customer/vendor relationships (Hub 4)

---

## Core Entities

### 1. **LegalEntity** - Corporate Structure

The legal companies: Primetime, Origin, OpenHaul.

**Complete Property List (35 properties):**

```yaml
# Primary Identifiers
entity_id: string              # PRIMARY KEY - standardized ID (e.g., "entity_origin")
legal_name: string             # Official registered name
dba_name: string (nullable)    # Doing Business As name
short_name: string             # Informal reference (e.g., "Origin")

# Entity Classification
entity_type: enum              # ["LLC", "S_Corp", "C_Corp", "Partnership", "Sole_Proprietorship"]
entity_subtype: string (nullable)  # "holding_company", "operating_company"
ein: string                    # Employer Identification Number (XX-XXXXXXX)
state_of_formation: string     # Where legally formed
formation_date: date
dissolution_date: date (nullable)

# Business Purpose
business_purpose: text         # From operating agreement
industry_classification: string  # NAICS code
primary_business_activity: string

# Registered Agent
registered_agent_name: string
registered_agent_address: string
registered_agent_city: string
registered_agent_state: string
registered_agent_zip: string

# Principal Address
principal_address: string
principal_city: string
principal_state: string
principal_zip: string

# Operational Details
fiscal_year_end: string        # "12/31" or "MM/DD"
accounting_method: enum        # ["cash", "accrual"]
management_structure: enum     # ["member_managed", "manager_managed", "board_managed"]
number_of_members: integer (nullable)
number_of_managers: integer (nullable)

# Status & Compliance
status: enum                   # ["active", "inactive", "dissolved", "suspended", "good_standing"]
good_standing: boolean         # Current with state filings?
last_filing_date: date (nullable)
next_filing_due_date: date (nullable)

# Relationships
parent_entity_id: string (nullable)  # If subsidiary
ultimate_parent_entity_id: string (nullable)  # If multiple layers

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: timestamp (nullable)
```

**Example - Primetime LLC (Holding Company):**
```python
LegalEntity(
    entity_id="entity_primetime",
    legal_name="Primetime LLC",
    dba_name=None,
    short_name="Primetime",
    entity_type="LLC",
    entity_subtype="holding_company",
    ein="XX-XXXXXXX",  # Sanitized
    state_of_formation="Nevada",
    formation_date="2018-01-15",
    business_purpose="Holding company for transportation and logistics businesses",
    industry_classification="551112",  # NAICS: Offices of Other Holding Companies
    primary_business_activity="Investment holding company",
    registered_agent_name="Nevada Registered Agent Services",
    registered_agent_address="123 Corporate Way",
    registered_agent_city="Las Vegas",
    registered_agent_state="NV",
    registered_agent_zip="89101",
    principal_address="456 Main Street, Suite 200",
    principal_city="Henderson",
    principal_state="NV",
    principal_zip="89015",
    fiscal_year_end="12/31",
    accounting_method="accrual",
    management_structure="member_managed",
    number_of_members=1,
    status="active",
    good_standing=True,
    last_filing_date="2025-01-15",
    next_filing_due_date="2026-01-31",
    parent_entity_id=None,
    ultimate_parent_entity_id=None
)
```

**Example - Origin Transport LLC (Operating Company):**
```python
LegalEntity(
    entity_id="entity_origin",
    legal_name="Origin Transport LLC",
    dba_name=None,
    short_name="Origin",
    entity_type="LLC",
    entity_subtype="operating_company",
    ein="XX-XXXXXXX",
    state_of_formation="Nevada",
    formation_date="2018-02-01",
    business_purpose="Interstate freight transportation services",
    industry_classification="484121",  # NAICS: General Freight Trucking, Long-Distance, Truckload
    primary_business_activity="Freight transportation",
    registered_agent_name="Nevada Registered Agent Services",
    registered_agent_address="123 Corporate Way",
    registered_agent_city="Las Vegas",
    registered_agent_state="NV",
    registered_agent_zip="89101",
    principal_address="456 Main Street, Suite 200",
    principal_city="Henderson",
    principal_state="NV",
    principal_zip="89015",
    fiscal_year_end="12/31",
    accounting_method="accrual",
    management_structure="member_managed",
    number_of_members=1,
    status="active",
    good_standing=True,
    last_filing_date="2025-01-20",
    next_filing_due_date="2026-01-31",
    parent_entity_id="entity_primetime",
    ultimate_parent_entity_id="entity_primetime"
)
```

**Example - OpenHaul LLC (Operating Company, Split Ownership):**
```python
LegalEntity(
    entity_id="entity_openhaul",
    legal_name="OpenHaul LLC",
    dba_name=None,
    short_name="OpenHaul",
    entity_type="LLC",
    entity_subtype="operating_company",
    ein="XX-XXXXXXX",
    state_of_formation="Nevada",
    formation_date="2019-06-15",
    business_purpose="Freight brokerage and logistics services",
    industry_classification="488510",  # NAICS: Freight Transportation Arrangement
    primary_business_activity="Freight brokerage",
    registered_agent_name="Nevada Registered Agent Services",
    registered_agent_address="123 Corporate Way",
    registered_agent_city="Las Vegas",
    registered_agent_state="NV",
    registered_agent_zip="89101",
    principal_address="456 Main Street, Suite 200",
    principal_city="Henderson",
    principal_state="NV",
    principal_zip="89015",
    fiscal_year_end="12/31",
    accounting_method="accrual",
    management_structure="member_managed",
    number_of_members=2,
    status="active",
    good_standing=True,
    last_filing_date="2025-01-25",
    next_filing_due_date="2026-01-31",
    parent_entity_id=None,
    ultimate_parent_entity_id=None
)
```

---

### 2. **Ownership** - Relationship Entity

Who owns what percentage of which entity.

**Complete Property List (18 properties):**

```yaml
# Primary Identifiers
ownership_id: string           # PRIMARY KEY - UUID
owner_person_id: string        # Links to Hub 4 - Person (if individual)
owner_entity_id: string (nullable)  # Links to LegalEntity (if corporate owner)
owned_entity_id: string        # Which LegalEntity is owned

# Ownership Details
ownership_percentage: decimal  # 0.01 to 100.00
ownership_class: string (nullable)  # "Class A", "Class B", "Common", "Preferred"
units_owned: integer (nullable)  # Number of units/shares
total_units: integer (nullable)  # Total units outstanding

# Acquisition
acquisition_date: date
acquisition_method: enum       # ["formation", "purchase", "gift", "inheritance", "transfer"]
purchase_price: decimal (nullable)
cost_basis: decimal (nullable)

# Rights
voting_rights: boolean         # Has voting rights?
voting_percentage: decimal (nullable)  # If different from ownership %
distribution_rights: boolean   # Receives profit distributions?
management_rights: boolean     # Can participate in management?

# Status
active_status: boolean
notes: text (nullable)

# Temporal Tracking
valid_from: timestamp
valid_to: timestamp (nullable)
created_at: timestamp
updated_at: timestamp
```

**Example - G owns Primetime (100%):**
```python
Ownership(
    ownership_id="own_g_primetime",
    owner_person_id="person_g",
    owner_entity_id=None,
    owned_entity_id="entity_primetime",
    ownership_percentage=100.0,
    ownership_class="membership_interest",
    units_owned=1000,
    total_units=1000,
    acquisition_date="2018-01-15",
    acquisition_method="formation",
    purchase_price=None,
    cost_basis=5000.00,  # Initial capital contribution
    voting_rights=True,
    voting_percentage=100.0,
    distribution_rights=True,
    management_rights=True,
    active_status=True,
    valid_from="2018-01-15T00:00:00Z",
    valid_to=None
)
```

**Example - Primetime owns Origin (100%):**
```python
Ownership(
    ownership_id="own_primetime_origin",
    owner_person_id=None,
    owner_entity_id="entity_primetime",
    owned_entity_id="entity_origin",
    ownership_percentage=100.0,
    ownership_class="membership_interest",
    units_owned=1000,
    total_units=1000,
    acquisition_date="2018-02-01",
    acquisition_method="formation",
    purchase_price=None,
    cost_basis=10000.00,
    voting_rights=True,
    voting_percentage=100.0,
    distribution_rights=True,
    management_rights=True,
    active_status=True,
    valid_from="2018-02-01T00:00:00Z",
    valid_to=None
)
```

**Example - G owns OpenHaul (50%):**
```python
Ownership(
    ownership_id="own_g_openhaul",
    owner_person_id="person_g",
    owner_entity_id=None,
    owned_entity_id="entity_openhaul",
    ownership_percentage=50.0,
    ownership_class="membership_interest",
    units_owned=500,
    total_units=1000,
    acquisition_date="2019-06-15",
    acquisition_method="formation",
    purchase_price=None,
    cost_basis=15000.00,
    voting_rights=True,
    voting_percentage=50.0,
    distribution_rights=True,
    management_rights=True,
    active_status=True,
    valid_from="2019-06-15T00:00:00Z",
    valid_to=None
)
```

**Example - Travis owns OpenHaul (50%):**
```python
Ownership(
    ownership_id="own_travis_openhaul",
    owner_person_id="person_travis",
    owner_entity_id=None,
    owned_entity_id="entity_openhaul",
    ownership_percentage=50.0,
    ownership_class="membership_interest",
    units_owned=500,
    total_units=1000,
    acquisition_date="2019-06-15",
    acquisition_method="formation",
    purchase_price=None,
    cost_basis=15000.00,
    voting_rights=True,
    voting_percentage=50.0,
    distribution_rights=True,
    management_rights=True,
    active_status=True,
    valid_from="2019-06-15T00:00:00Z",
    valid_to=None
)
```

---

### 3. **License** - Operating Authority & Permits

All licenses, permits, authorities required to operate.

**Complete Property List (28 properties):**

```yaml
# Primary Identifiers
license_id: string             # PRIMARY KEY - UUID
license_type: enum             # See License Types section
license_number: string         # Official license/permit number
license_name: string           # Human-readable name

# Issuing Authority
issuing_authority: string      # FMCSA, State of Nevada, IRS, etc.
issuing_authority_type: enum   # ["federal", "state", "local", "industry"]
application_date: date (nullable)
issue_date: date
approval_date: date (nullable)

# Entity Assignment
issued_to_entity_id: string    # Which LegalEntity holds this license
issued_to_person_id: string (nullable)  # If personal license (CDL, etc.)

# Validity & Expiration
expiration_date: date (nullable)  # null if doesn't expire
perpetual: boolean             # True if doesn't expire
renewal_required: boolean
renewal_frequency: string (nullable)  # "annual", "biennial", "every_5_years"
renewal_date: date (nullable)  # When to initiate renewal
renewal_window_days: integer (nullable)  # How far in advance to renew

# Status
status: enum                   # ["active", "pending", "expired", "suspended", "revoked", "cancelled"]
status_effective_date: date
status_reason: text (nullable)

# Fees & Costs
application_fee: decimal (nullable)
initial_fee: decimal (nullable)
annual_fee: decimal (nullable)
renewal_fee: decimal (nullable)
late_fee: decimal (nullable)

# Compliance
compliance_requirements: array[string]  # What's required to maintain
last_compliance_check_date: date (nullable)
next_compliance_check_date: date (nullable)

# Document
document_path: string (nullable)  # PDF of license/permit
certificate_number: string (nullable)

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: timestamp (nullable)
```

**License Types (Complete List):**
```yaml
# Federal Transportation
- "DOT"                        # FMCSA DOT Number
- "MC"                         # FMCSA Motor Carrier Authority
- "FF"                         # FMCSA Freight Forwarder Authority
- "MX"                         # FMCSA Mexico-Domiciled Carrier

# State Business
- "state_business_license"     # General business license
- "sales_tax_permit"           # Sales/use tax registration
- "employer_registration"      # State employer registration

# Professional Licenses
- "CDL"                        # Commercial Driver's License (personal)
- "broker_license"             # Customs broker license

# Industry Certifications
- "smartway"                   # EPA SmartWay certification
- "iso_certification"          # ISO 9001, etc.
- "safety_certification"       # DOT safety rating

# Local Permits
- "local_business_license"     # City/county business license
- "vehicle_registration"       # Local vehicle permits
```

**Example - Origin DOT Number:**
```python
License(
    license_id="lic_origin_dot",
    license_type="DOT",
    license_number="DOT-789012",
    license_name="USDOT Number - Origin Transport LLC",
    issuing_authority="FMCSA",
    issuing_authority_type="federal",
    application_date="2018-01-20",
    issue_date="2018-02-15",
    issued_to_entity_id="entity_origin",
    issued_to_person_id=None,
    expiration_date=None,
    perpetual=True,
    renewal_required=False,
    status="active",
    status_effective_date="2018-02-15",
    application_fee=300.00,
    initial_fee=0.00,
    annual_fee=0.00,
    compliance_requirements=[
        "Biennial Update (MCS-150)",
        "Insurance filing (BMC-91)",
        "Safety rating compliance"
    ],
    last_compliance_check_date="2025-10-01",
    next_compliance_check_date="2026-02-15",
    document_path="drive://corporate/licenses/origin/DOT-789012.pdf"
)
```

**Example - OpenHaul MC Authority:**
```python
License(
    license_id="lic_openhaul_mc",
    license_type="MC",
    license_number="MC-234567",
    license_name="Motor Carrier (Broker) Authority - OpenHaul LLC",
    issuing_authority="FMCSA",
    issuing_authority_type="federal",
    application_date="2019-06-20",
    issue_date="2019-07-15",
    issued_to_entity_id="entity_openhaul",
    expiration_date=None,
    perpetual=True,
    renewal_required=True,
    renewal_frequency="annual",
    status="active",
    status_effective_date="2019-07-15",
    initial_fee=300.00,
    annual_fee=300.00,
    compliance_requirements=[
        "BMC-84 Surety Bond ($75,000)",
        "Biennial Update (MCS-150)",
        "Annual FMCSA filing fee"
    ],
    last_compliance_check_date="2025-07-01",
    next_compliance_check_date="2025-12-01",
    document_path="drive://corporate/licenses/openhaul/MC-234567.pdf"
)
```

**Example - Nevada Business License (Origin):**
```python
License(
    license_id="lic_origin_nv_business",
    license_type="state_business_license",
    license_number="NV-BL-456789",
    license_name="Nevada State Business License - Origin Transport",
    issuing_authority="Nevada Secretary of State",
    issuing_authority_type="state",
    issue_date="2018-02-01",
    issued_to_entity_id="entity_origin",
    expiration_date="2026-02-01",
    perpetual=False,
    renewal_required=True,
    renewal_frequency="every_5_years",
    renewal_date="2025-12-01",
    renewal_window_days=60,
    status="active",
    status_effective_date="2018-02-01",
    initial_fee=200.00,
    renewal_fee=200.00,
    document_path="drive://corporate/licenses/origin/NV-BL-456789.pdf"
)
```

---

### 4. **Filing** - Compliance Documents

Annual reports, registrations, state filings.

**Complete Property List (25 properties):**

```yaml
# Primary Identifiers
filing_id: string              # PRIMARY KEY - UUID
filing_type: enum              # See Filing Types section
filing_name: string            # Human-readable name

# Filing Authority
filing_authority: string       # Nevada Secretary of State, IRS, FMCSA, etc.
filing_authority_type: enum    # ["federal", "state", "local"]

# Entity
filed_by_entity_id: string     # Which LegalEntity filed this

# Filing Details
filing_year: integer           # For annual reports, tax returns
filing_period: string (nullable)  # "Q1 2025", "2024", "January 2025"
filing_date: date              # When actually filed
due_date: date                 # Original due date
extended_due_date: date (nullable)  # If extension granted

# Status
status: enum                   # ["filed", "pending", "overdue", "amended", "rejected"]
status_date: date
confirmation_number: string (nullable)
tracking_number: string (nullable)

# Fees & Payment
filing_fee: decimal (nullable)
late_fee: decimal (nullable)
total_paid: decimal (nullable)
payment_date: date (nullable)
payment_method: string (nullable)

# Document
document_path: string (nullable)  # PDF of filing
amended_filing_id: string (nullable)  # If this amends another filing

# Related
related_license_id: string (nullable)  # If filing is for license compliance

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Filing Types (Complete List):**
```yaml
# State Filings
- "annual_report"              # State annual report
- "list_of_officers"           # Annual list of officers/managers
- "registration"               # Initial business registration
- "amendment"                  # Amendments to formation documents
- "dissolution"                # Dissolution filing

# Federal Tax
- "form_1120"                  # Corporate income tax
- "form_1065"                  # Partnership tax return
- "form_1040_schedule_c"       # Sole proprietorship
- "form_941"                   # Quarterly payroll tax
- "form_940"                   # Annual unemployment tax

# State Tax
- "state_income_tax"           # State corporate tax
- "sales_tax_return"           # Monthly/quarterly sales tax
- "franchise_tax"              # State franchise tax

# Transportation-Specific
- "mcs_150"                    # FMCSA Biennial Update
- "ucr_registration"           # Unified Carrier Registration
- "ifta_return"                # Fuel tax return (if applicable)

# Other
- "extension_request"          # Tax extension (Form 7004, etc.)
- "compliance_report"          # Various compliance filings
```

**Example - Nevada Annual Report (Origin 2024):**
```python
Filing(
    filing_id="fil_origin_ar_2024",
    filing_type="annual_report",
    filing_name="Nevada Annual Report 2024 - Origin Transport",
    filing_authority="Nevada Secretary of State",
    filing_authority_type="state",
    filed_by_entity_id="entity_origin",
    filing_year=2024,
    filing_period="2024",
    filing_date="2025-01-20",
    due_date="2025-01-31",
    status="filed",
    status_date="2025-01-20",
    confirmation_number="NV-AR-2024-654321",
    filing_fee=350.00,
    total_paid=350.00,
    payment_date="2025-01-20",
    payment_method="credit_card",
    document_path="drive://corporate/filings/origin/annual-reports/2024.pdf"
)
```

**Example - IRS Form 1120 (Origin 2024):**
```python
Filing(
    filing_id="fil_origin_1120_2024",
    filing_type="form_1120",
    filing_name="IRS Form 1120 Corporate Tax Return 2024 - Origin Transport",
    filing_authority="Internal Revenue Service",
    filing_authority_type="federal",
    filed_by_entity_id="entity_origin",
    filing_year=2024,
    filing_period="2024",
    filing_date="2025-03-10",
    due_date="2025-03-15",
    status="filed",
    status_date="2025-03-10",
    confirmation_number="IRS-1120-2024-987654",
    filing_fee=0.00,
    document_path="drive://corporate/filings/origin/tax-returns/2024-1120.pdf"
)
```

**Example - FMCSA MCS-150 Biennial Update (Origin):**
```python
Filing(
    filing_id="fil_origin_mcs150_2024",
    filing_type="mcs_150",
    filing_name="FMCSA Biennial Update (MCS-150) 2024 - Origin Transport",
    filing_authority="FMCSA",
    filing_authority_type="federal",
    filed_by_entity_id="entity_origin",
    filing_year=2024,
    filing_date="2024-02-10",
    due_date="2024-02-28",
    status="filed",
    status_date="2024-02-10",
    confirmation_number="MCS150-2024-123456",
    filing_fee=0.00,
    related_license_id="lic_origin_dot",
    document_path="drive://corporate/filings/origin/fmcsa/mcs-150-2024.pdf"
)
```

---

### 5. **BrandAsset** - Intellectual Property & Marketing

Logos, domains, trademarks, marketing materials.

**Complete Property List (30 properties):**

```yaml
# Primary Identifiers
asset_id: string               # PRIMARY KEY - UUID
asset_type: enum               # See Asset Types section
asset_name: string
asset_description: text (nullable)

# Ownership
owned_by_entity_id: string     # Which LegalEntity owns this
licensed_to_entity_id: string (nullable)  # If licensed to another entity

# Dates
created_date: date
acquired_date: date (nullable)
first_use_date: date (nullable)  # For trademarks

# File/Storage
file_path: string (nullable)   # Where asset is stored
file_format: string (nullable)  # "svg", "png", "pdf", "docx"
file_size_kb: integer (nullable)
version: string (nullable)     # "v3.0", "2025.1"

# Status
status: enum                   # ["active", "archived", "deprecated", "pending_approval"]
status_date: date

# Domain-Specific (if type = domain)
domain_name: string (nullable)
domain_registrar: string (nullable)
domain_registration_date: date (nullable)
domain_expiration_date: date (nullable)
auto_renewal: boolean (nullable)
dns_provider: string (nullable)
nameservers: array[string] (nullable)

# Trademark-Specific (if type = trademark)
trademark_class: string (nullable)  # USPTO class
registration_number: string (nullable)
registration_date: date (nullable)
trademark_status: string (nullable)  # "registered", "pending", "abandoned"

# Usage Rights
usage_rights: text (nullable)  # Internal use, public use, restricted
license_terms: text (nullable)

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
valid_from: timestamp
valid_to: timestamp (nullable)
```

**Asset Types (Complete List):**
```yaml
# Visual Assets
- "logo"                       # Company logos
- "wordmark"                   # Text-only logo treatment
- "icon"                       # App icons, favicons
- "color_palette"              # Brand colors
- "typography"                 # Brand fonts

# Digital Assets
- "domain"                     # Website domains
- "email_template"             # Email designs
- "website_design"             # Website mockups/designs
- "social_media_profile"       # Social media accounts

# Documents
- "business_plan"              # Strategic business plans
- "marketing_deck"             # Sales/pitch decks
- "brand_guidelines"           # Brand usage guides
- "letterhead"                 # Company letterhead template
- "business_card_template"     # Business card designs

# Legal/IP
- "trademark"                  # Registered trademarks
- "copyright"                  # Copyrighted works
- "patent"                     # Patents (unlikely for this business)

# Marketing Materials
- "brochure"                   # Marketing brochures
- "advertisement"              # Print/digital ads
- "video"                      # Marketing videos
- "case_study"                 # Customer case studies
```

**Example - Origin Logo (Primary):**
```python
BrandAsset(
    asset_id="asset_origin_logo_primary",
    asset_type="logo",
    asset_name="Origin Transport Primary Logo",
    asset_description="Primary logo featuring eagle and highway imagery in Origin blue (#003366)",
    owned_by_entity_id="entity_origin",
    created_date="2018-03-01",
    file_path="drive://brand-assets/origin/logos/origin-logo-primary-v3.svg",
    file_format="svg",
    version="v3.0",
    status="active",
    status_date="2023-05-01",
    usage_rights="Internal use and external marketing, all rights reserved",
    license_terms="May not be modified without authorization"
)
```

**Example - Origin Domain:**
```python
BrandAsset(
    asset_id="asset_origin_domain",
    asset_type="domain",
    asset_name="origintransport.com",
    asset_description="Primary website domain for Origin Transport",
    owned_by_entity_id="entity_origin",
    acquired_date="2018-02-05",
    domain_name="origintransport.com",
    domain_registrar="GoDaddy",
    domain_registration_date="2018-02-05",
    domain_expiration_date="2027-02-05",
    auto_renewal=True,
    dns_provider="Cloudflare",
    nameservers=["ns1.cloudflare.com", "ns2.cloudflare.com"],
    status="active",
    status_date="2018-02-05"
)
```

**Example - OpenHaul Business Plan:**
```python
BrandAsset(
    asset_id="asset_openhaul_bp_2025",
    asset_type="business_plan",
    asset_name="OpenHaul Business Plan 2025-2030",
    asset_description="5-year strategic business plan: growth targets, market expansion, technology roadmap",
    owned_by_entity_id="entity_openhaul",
    created_date="2024-12-01",
    file_path="drive://corporate-docs/openhaul/business-plans/2025-2030.pdf",
    file_format="pdf",
    version="2025.1",
    status="active",
    status_date="2025-01-01",
    usage_rights="Confidential - internal use only",
    license_terms="Not for distribution"
)
```

---

### 6. **CompanyDocument** - Operating Agreements, Policies, Plans

Foundational company documents.

**Complete Property List (22 properties):**

```yaml
# Primary Identifiers
document_id: string            # PRIMARY KEY - UUID
document_type: enum            # See Document Types section
document_title: string
document_description: text (nullable)

# Ownership
owned_by_entity_id: string     # Which LegalEntity

# Dates
created_date: date
last_updated_date: date
effective_date: date           # When document takes effect
expiration_date: date (nullable)

# Version Control
version: string                # "v1.0", "v2.1"
supersedes_document_id: string (nullable)  # If replaces another doc
superseded_by_document_id: string (nullable)  # If replaced by newer doc

# File
document_path: string          # PDF or file location
file_format: string            # "pdf", "docx"
file_size_kb: integer (nullable)

# Content
summary: text (nullable)       # Brief description
key_provisions: array[string] (nullable)  # Important clauses/sections

# Status
status: enum                   # ["active", "archived", "superseded", "draft"]
status_date: date

# Access Control
confidential: boolean          # Is document confidential?
access_level: enum             # ["public", "internal", "restricted", "confidential"]

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Document Types (Complete List):**
```yaml
# Formation Documents
- "articles_of_organization"   # LLC formation document
- "articles_of_incorporation"  # Corp formation document
- "operating_agreement"        # LLC operating agreement
- "bylaws"                     # Corporation bylaws
- "shareholder_agreement"      # Shareholder/member agreement

# Corporate Governance
- "board_resolution"           # Board resolutions
- "member_resolution"          # Member/shareholder resolutions
- "meeting_minutes"            # Board/member meeting minutes

# Policies
- "employee_handbook"          # HR policies
- "code_of_conduct"            # Ethics/conduct policy
- "privacy_policy"             # Data privacy policy
- "safety_policy"              # Workplace safety policy
- "expense_policy"             # Business expense policy

# Strategic Documents
- "mission_statement"          # Company mission/vision
- "business_plan"              # Strategic plans
- "organizational_chart"       # Org structure

# Contracts & Agreements
- "employment_agreement"       # Executive employment contracts
- "nda"                        # Non-disclosure agreements
- "non_compete"                # Non-compete agreements

# Other
- "power_of_attorney"          # POA documents
- "buy_sell_agreement"         # Buy-sell provisions
```

**Example - OpenHaul Operating Agreement:**
```python
CompanyDocument(
    document_id="doc_openhaul_operating_agreement",
    document_type="operating_agreement",
    document_title="OpenHaul LLC Operating Agreement",
    document_description="Defines ownership, management, distributions, buy-sell provisions",
    owned_by_entity_id="entity_openhaul",
    created_date="2019-06-15",
    last_updated_date="2023-01-15",
    effective_date="2023-02-01",
    version="v2.1",
    supersedes_document_id="doc_openhaul_operating_agreement_v2",
    document_path="drive://corporate-docs/openhaul/operating-agreement-v2.1.pdf",
    file_format="pdf",
    summary="50/50 ownership between G and Travis. Member-managed. Annual distributions of net profits. Buy-sell triggered by death, disability, voluntary exit. Right of first refusal for remaining member.",
    key_provisions=[
        "Article 3: Capital Contributions ($15,000 each)",
        "Article 5: Profit Distribution (50/50 split)",
        "Article 7: Management Rights (equal voting)",
        "Article 9: Buy-Sell Provisions (ROFR, 90-day window)",
        "Article 11: Dissolution (requires unanimous consent)"
    ],
    status="active",
    status_date="2023-02-01",
    confidential=True,
    access_level="confidential"
)
```

**Example - Origin Mission Statement:**
```python
CompanyDocument(
    document_id="doc_origin_mission",
    document_type="mission_statement",
    document_title="Origin Transport Mission & Vision",
    document_description="Company purpose, values, strategic vision",
    owned_by_entity_id="entity_origin",
    created_date="2018-02-01",
    last_updated_date="2018-02-01",
    effective_date="2018-02-01",
    version="v1.0",
    document_path="drive://corporate-docs/origin/mission-vision.pdf",
    file_format="pdf",
    summary="Mission: Deliver reliable freight solutions with exceptional service, safety, and integrity. Vision: Become the premier regional carrier in the Southwest U.S., known for customer loyalty and driver satisfaction. Values: Safety first, customer commitment, driver respect, operational excellence.",
    status="active",
    status_date="2018-02-01",
    confidential=False,
    access_level="public"
)
```

**Example - Primetime Board Resolution (Origin Acquisition):**
```python
CompanyDocument(
    document_id="doc_primetime_resolution_origin_formation",
    document_type="board_resolution",
    document_title="Board Resolution: Formation of Origin Transport LLC",
    document_description="Resolution authorizing formation and capitalization of Origin Transport",
    owned_by_entity_id="entity_primetime",
    created_date="2018-01-25",
    effective_date="2018-02-01",
    version="v1.0",
    document_path="drive://corporate-docs/primetime/resolutions/2018-01-origin-formation.pdf",
    file_format="pdf",
    summary="Authorizes formation of Origin Transport LLC as wholly-owned subsidiary. Approves initial capital contribution of $10,000. Appoints G as Manager.",
    key_provisions=[
        "Resolution 2018-01: Formation authorized",
        "Initial capitalization: $10,000",
        "Management: G appointed as Manager",
        "Business purpose: Interstate freight transportation"
    ],
    status="active",
    status_date="2018-02-01",
    confidential=True,
    access_level="restricted"
)
```

---

### 7. **Award** - Recognition & Certifications

Industry awards, certifications, memberships.

**Complete Property List (20 properties):**

```yaml
# Primary Identifiers
award_id: string               # PRIMARY KEY - UUID
award_type: enum               # ["industry_award", "certification", "membership", "recognition", "accreditation"]
award_name: string
award_description: text (nullable)

# Entity
received_by_entity_id: string  # Which LegalEntity received this

# Issuing Organization
issuing_organization: string
issuing_organization_type: string (nullable)  # "trade_association", "government_agency", "certification_body"
issuing_contact: string (nullable)

# Dates
award_date: date               # When received
effective_date: date (nullable)
expiration_date: date (nullable)  # If certification expires
renewal_required: boolean

# Certification-Specific
certification_number: string (nullable)
certification_level: string (nullable)  # "Gold", "Platinum", "Level 1"

# Document
document_path: string (nullable)  # Certificate, plaque photo
certificate_format: string (nullable)  # "pdf", "jpg"

# Display
display_on_website: boolean    # Show publicly?
display_priority: integer (nullable)  # Sort order (1=highest)

# Status
status: enum                   # ["active", "expired", "revoked", "suspended"]
status_date: date

# Temporal Tracking
created_at: timestamp
updated_at: timestamp
```

**Example - Origin Carrier of the Year:**
```python
Award(
    award_id="award_origin_carrier_2024",
    award_type="industry_award",
    award_name="Carrier of the Year 2024",
    award_description="Recognized for exceptional safety record, on-time performance, and customer satisfaction",
    received_by_entity_id="entity_origin",
    issuing_organization="Nevada Trucking Association",
    issuing_organization_type="trade_association",
    award_date="2024-11-15",
    effective_date="2024-11-15",
    document_path="drive://corporate/awards/origin/carrier-of-year-2024.pdf",
    certificate_format="pdf",
    display_on_website=True,
    display_priority=1,
    status="active",
    status_date="2024-11-15"
)
```

**Example - Origin SmartWay Certification:**
```python
Award(
    award_id="award_origin_smartway",
    award_type="certification",
    award_name="EPA SmartWay Transport Partner",
    award_description="Environmental performance certification for freight carriers committed to fuel efficiency and emission reduction",
    received_by_entity_id="entity_origin",
    issuing_organization="U.S. Environmental Protection Agency",
    issuing_organization_type="government_agency",
    award_date="2020-03-01",
    effective_date="2020-03-01",
    expiration_date="2026-03-01",
    renewal_required=True,
    certification_number="SW-12345-2020",
    document_path="drive://corporate/certifications/origin/smartway-certificate.pdf",
    certificate_format="pdf",
    display_on_website=True,
    display_priority=2,
    status="active",
    status_date="2020-03-01"
)
```

**Example - OpenHaul TIA Membership:**
```python
Award(
    award_id="award_openhaul_tia",
    award_type="membership",
    award_name="Transportation Intermediaries Association (TIA) Member",
    award_description="Professional association membership for freight brokers and third-party logistics providers",
    received_by_entity_id="entity_openhaul",
    issuing_organization="Transportation Intermediaries Association",
    issuing_organization_type="trade_association",
    award_date="2019-08-01",
    effective_date="2019-08-01",
    expiration_date="2026-07-31",
    renewal_required=True,
    display_on_website=True,
    display_priority=3,
    status="active",
    status_date="2019-08-01"
)
```

---

## Annual Compliance Calendar

**Complete filing and renewal schedule for all entities:**

### Nevada State Filings (All Entities)

**Due:** January 31st (annually)
**Entities:** Primetime, Origin, OpenHaul

| Entity | Filing Type | Due Date | Fee | Notes |
|--------|-------------|----------|-----|-------|
| Primetime LLC | Annual Report | Jan 31 | $350 | List of Officers/Managers |
| Origin Transport LLC | Annual Report | Jan 31 | $350 | List of Officers/Managers |
| OpenHaul LLC | Annual Report | Jan 31 | $350 | List of Officers/Managers |

**Renewal Window:** File 30-60 days before due date
**Late Penalty:** $100 + potential loss of good standing
**Online Filing:** Available via NV Secretary of State portal

---

### Federal Tax Filings

#### Corporate Tax Returns (Origin Transport - LLC electing C-corp tax treatment)

**Due:** March 15th (annually)
**Form:** IRS Form 1120 (if C-corp) or 1065 (if partnership)
**Extension:** 6 months (Form 7004) → September 15

| Entity | Form | Due Date | Notes |
|--------|------|----------|-------|
| Origin Transport | Form 1120 or 1065 | March 15 | Depends on tax election |
| OpenHaul | Form 1065 | March 15 | Partnership return |
| Primetime | Form 1065 | March 15 | Holding company, likely pass-through |

#### Quarterly Payroll Taxes (If Employees)

**Due:** Last day of month following quarter end
**Form:** IRS Form 941 (Quarterly Federal Tax Return)

- Q1 (Jan-Mar): Due April 30
- Q2 (Apr-Jun): Due July 31
- Q3 (Jul-Sep): Due October 31
- Q4 (Oct-Dec): Due January 31

**Annual:** Form 940 (Federal Unemployment Tax) - Due January 31

---

### FMCSA Filings (Transportation-Specific)

#### MCS-150 Biennial Update

**Due:** Every 2 years (on anniversary of authorization month)
**Applies to:** Origin (DOT), OpenHaul (MC)

| Entity | License | Due Frequency | Last Update | Next Due |
|--------|---------|---------------|-------------|----------|
| Origin | DOT-789012 | Every 2 years | Feb 2024 | Feb 2026 |
| OpenHaul | MC-234567 | Every 2 years | Jul 2024 | Jul 2026 |

**Fee:** $0 (free filing)
**Penalty:** Out of service if not filed

#### Annual FMCSA Fee (Broker Authority)

**Due:** Annually (anniversary of MC grant)
**Applies to:** OpenHaul (MC-234567)
**Fee:** $300
**Due Date:** July 15 (annually)

---

### Unified Carrier Registration (UCR)

**Due:** December 31 (annually, for following year)
**Applies to:** Origin, OpenHaul (if interstate)
**Fee:** Based on fleet size (Origin: $76 for 3-5 trucks, increases with fleet)

---

### Business License Renewals

#### State Business Licenses

| Entity | License | Renewal Frequency | Next Renewal | Fee |
|--------|---------|-------------------|--------------|-----|
| Origin | NV State Business License | Every 5 years | Feb 2026 | $200 |
| OpenHaul | NV State Business License | Every 5 years | Jun 2024 | $200 |
| Primetime | NV State Business License | Every 5 years | Jan 2023 | $200 |

---

### Insurance Compliance

#### Certificate of Insurance Updates

**Frequency:** As needed when policies renew (typically annual)
**Applies to:** Origin (auto liability, cargo), OpenHaul (broker bond)

| Entity | Insurance Type | Renewal Month | Action Required |
|--------|---------------|---------------|-----------------|
| Origin | Auto Liability | March | File BMC-91 with FMCSA |
| Origin | Cargo Insurance | March | Update certificate |
| OpenHaul | Broker Bond (BMC-84) | July | File with FMCSA ($75k bond) |

---

### Domain Renewals

| Domain | Owner | Registrar | Auto-Renew | Expiration | Annual Cost |
|--------|-------|-----------|------------|------------|-------------|
| origintransport.com | Origin | GoDaddy | Yes | Feb 2027 | $15 |
| openhaul.com | OpenHaul | GoDaddy | Yes | Jun 2027 | $15 |
| primetimellc.com | Primetime | GoDaddy | Yes | Jan 2026 | $15 |

---

### Certification Renewals

| Certification | Entity | Issued By | Expiration | Renewal Window | Fee |
|---------------|--------|-----------|------------|----------------|-----|
| EPA SmartWay | Origin | EPA | March 2026 | 90 days before | $0 |
| TIA Membership | OpenHaul | TIA | July 2026 | Annual renewal | $595 |

---

## Document Types & Extraction Patterns

### Document Type 1: Articles of Organization (Formation Document)

**Source:** State filing (Nevada Secretary of State)
**Example:** "Articles of Organization - Origin Transport LLC"

**Key Fields to Extract:**
```yaml
# Entity Details
legal_name: "Origin Transport LLC"
formation_state: "Nevada"
formation_date: "2018-02-01"
file_number: "NV-20180201-6789"  # State file number

# Business Purpose
business_purpose: "Interstate freight transportation services"

# Registered Agent
registered_agent_name: "Nevada Registered Agent Services"
registered_agent_address: "123 Corporate Way, Las Vegas, NV 89101"

# Principal Address
principal_address: "456 Main Street, Suite 200, Henderson, NV 89015"

# Management Structure
management_structure: "member-managed"
initial_member: "Primetime LLC"

# Filing Details
filing_date: "2018-02-01"
effective_date: "2018-02-01"
filing_fee: "$75.00"
```

**Extraction Strategy:**
- Parse PDF from state website
- Create LegalEntity record
- Link to person_g (ultimate owner)
- Store document in `document_path`

---

### Document Type 2: Operating Agreement

**Source:** Internal legal document (attorney-prepared or template)
**Example:** "OpenHaul LLC Operating Agreement v2.1"

**Key Fields to Extract:**
```yaml
# Agreement Details
agreement_title: "Operating Agreement of OpenHaul LLC"
effective_date: "2023-02-01"
state_governed_by: "Nevada"

# Members
members: [
    {name: "Richard Glaubitz", ownership_percentage: 50.0, capital_contribution: 15000.00},
    {name: "Travis [Last Name]", ownership_percentage: 50.0, capital_contribution: 15000.00}
]

# Key Provisions (text extraction)
capital_contributions: "Article 3: Each member contributes $15,000 initial capital"
profit_distribution: "Article 5: Net profits distributed 50/50 quarterly"
management_rights: "Article 7: Member-managed, equal voting rights"
buy_sell_provisions: "Article 9: Right of first refusal, 90-day window, fair market value"
dissolution: "Article 11: Requires unanimous member consent"

# Signatures
signed_date: "2023-01-15"
signatories: ["Richard Glaubitz", "Travis [Last Name]"]
```

**Extraction Strategy:**
- Use Graphiti LLM to extract structure
- Create CompanyDocument record
- Create Ownership records for each member
- Store summary in `key_provisions[]`

---

### Document Type 3: Business License

**Source:** State/local government (PDF certificate)
**Example:** "Nevada State Business License - Origin Transport LLC"

**Key Fields to Extract:**
```yaml
# License Details
license_type: "state_business_license"
license_number: "NV-BL-456789"
license_name: "Nevada State Business License"

# Issued To
issued_to_legal_name: "Origin Transport LLC"
issued_to_address: "456 Main Street, Suite 200, Henderson, NV 89015"

# Authority
issuing_authority: "Nevada Secretary of State"
issue_date: "2018-02-01"
expiration_date: "2026-02-01"

# Fees
initial_fee: "$200.00"
renewal_frequency: "every 5 years"

# Certificate Number
certificate_number: "NV-BL-456789"
```

**Extraction Strategy:**
- OCR scan license certificate
- Match `issued_to_legal_name` to LegalEntity
- Create License record
- Set renewal reminder: 60 days before expiration

---

### Document Type 4: Annual Report Filing

**Source:** State filing confirmation (Nevada)
**Example:** "2024 Nevada Annual Report Confirmation - Origin Transport"

**Key Fields to Extract:**
```yaml
# Filing Details
filing_type: "annual_report"
filing_year: 2024
filing_date: "2025-01-20"
due_date: "2025-01-31"

# Entity
filed_by_legal_name: "Origin Transport LLC"
entity_file_number: "NV-20180201-6789"

# List of Officers/Managers
officers: [
    {name: "Richard Glaubitz", title: "Manager", address: "456 Main Street, Henderson, NV 89015"}
]

# Confirmation
confirmation_number: "NV-AR-2024-654321"
filing_fee: "$350.00"
status: "filed"
receipt_number: "654321"
```

**Extraction Strategy:**
- Parse confirmation email or PDF
- Match to LegalEntity
- Create Filing record
- Update entity `last_filing_date` and `next_filing_due_date`

---

### Document Type 5: FMCSA Authority Grant

**Source:** FMCSA (PDF letter of authority)
**Example:** "MC Authority Grant Letter - OpenHaul LLC"

**Key Fields to Extract:**
```yaml
# Authority Details
authority_type: "MC"  # Motor Carrier (Broker)
mc_number: "MC-234567"
grant_date: "2019-07-15"

# Authorized For
operations_authorized: "Broker - Arrange transportation of general freight"
commodity_restrictions: "None"
geographic_scope: "Interstate"

# Entity
legal_name: "OpenHaul LLC"
operating_address: "456 Main Street, Suite 200, Henderson, NV 89015"

# Compliance Requirements
insurance_required: "BMC-84 Surety Bond ($75,000)"
biennial_update_required: true
```

**Extraction Strategy:**
- Parse FMCSA PDF letter
- Create License record (type="MC")
- Add compliance requirements to `compliance_requirements[]`
- Set biennial update reminder (2-year cycle)

---

### Document Type 6: Board/Member Resolution

**Source:** Internal corporate records
**Example:** "Board Resolution 2018-01: Formation of Origin Transport LLC"

**Key Fields to Extract:**
```yaml
# Resolution Details
resolution_number: "2018-01"
resolution_title: "Formation of Origin Transport LLC"
resolution_date: "2018-01-25"
effective_date: "2018-02-01"

# Issuing Entity
issued_by_entity: "Primetime LLC"
issued_by_authority: "Board of Managers"

# Resolution Content (text summary)
resolved: "Formation of Origin Transport LLC as wholly-owned subsidiary authorized. Initial capital contribution of $10,000 approved. Richard Glaubitz appointed as Manager."

# Key Actions
actions: [
    "Authorize formation of Origin Transport LLC",
    "Approve Articles of Organization",
    "Approve Operating Agreement",
    "Authorize capital contribution: $10,000",
    "Appoint Richard Glaubitz as Manager"
]

# Signatures
signatories: ["Richard Glaubitz - Manager, Primetime LLC"]
signed_date: "2018-01-25"
```

**Extraction Strategy:**
- LLM extract resolution text
- Create CompanyDocument record (type="board_resolution")
- Link to `owned_by_entity_id` (Primetime)
- Store actions in `key_provisions[]`

---

### Document Type 7: Domain Registration Confirmation

**Source:** Domain registrar (GoDaddy, Cloudflare, etc.)
**Example:** "Domain Registration Confirmation - origintransport.com"

**Key Fields to Extract:**
```yaml
# Domain Details
domain_name: "origintransport.com"
registrar: "GoDaddy"
registration_date: "2018-02-05"
expiration_date: "2027-02-05"
auto_renew: true

# Nameservers
nameservers: [
    "ns1.cloudflare.com",
    "ns2.cloudflare.com"
]

# Registrant
registrant_organization: "Origin Transport LLC"
registrant_email: "admin@origintransport.com"

# Fees
registration_fee: "$14.99"
annual_renewal_cost: "$14.99"
```

**Extraction Strategy:**
- Parse registrar confirmation email
- Match registrant to LegalEntity
- Create BrandAsset record (type="domain")
- Set renewal reminder: 30 days before expiration (even if auto-renew)

---

## Real-World Example: Primetime Corporate Structure

**Scenario:** Complete corporate structure for Primetime LLC and subsidiaries.

### Ownership Chain

```
Richard Glaubitz (person_g)
    |
    ├── 100% ownership → Primetime LLC (entity_primetime)
    │       └── 100% ownership → Origin Transport LLC (entity_origin)
    │
    └── 50% ownership → OpenHaul LLC (entity_openhaul)
            └── 50% ownership → Travis [Partner] (person_travis)
```

### Database Distribution for Corporate Structure

**Neo4j (Relationship Memory):**
```cypher
// Ownership structure
(G:Person {person_id: "person_g"})-[:OWNS {
    percentage: 100.0,
    acquisition_date: "2018-01-15",
    valid_from: "2018-01-15T00:00:00Z",
    valid_to: null
}]->(Primetime:LegalEntity {entity_id: "entity_primetime"})

(Primetime)-[:OWNS {
    percentage: 100.0,
    acquisition_date: "2018-02-01"
}]->(Origin:LegalEntity {entity_id: "entity_origin"})

(G)-[:OWNS {percentage: 50.0}]->(OpenHaul:LegalEntity {entity_id: "entity_openhaul"})
(Travis:Person {person_id: "person_travis"})-[:OWNS {percentage: 50.0}]->(OpenHaul)

// Parent-subsidiary relationships
(Primetime)-[:PARENT_OF]->(Origin)

// License requirements
(Origin)-[:HOLDS_LICENSE]->(License {license_type: "DOT", license_number: "DOT-789012"})
(OpenHaul)-[:HOLDS_LICENSE]->(License {license_type: "MC", license_number: "MC-234567"})

// Brand assets
(BrandAsset {domain_name: "origintransport.com"})-[:OWNED_BY]->(Origin)
(BrandAsset {domain_name: "openhaul.com"})-[:OWNED_BY]->(OpenHaul)

// Company documents
(CompanyDocument {document_type: "operating_agreement"})-[:BELONGS_TO]->(OpenHaul)
```

**PostgreSQL (Factual Memory):**
```sql
-- legal_entities table
SELECT * FROM legal_entities WHERE entity_id IN ('entity_primetime', 'entity_origin', 'entity_openhaul');
-- Returns: All 3 entities with complete 35 properties each

-- ownership table
SELECT * FROM ownership WHERE owned_entity_id IN ('entity_primetime', 'entity_origin', 'entity_openhaul');
-- Returns: 4 ownership records (G→Primetime, Primetime→Origin, G→OpenHaul, Travis→OpenHaul)

-- licenses table
SELECT * FROM licenses WHERE issued_to_entity_id IN ('entity_origin', 'entity_openhaul');
-- Returns: DOT, MC, state business licenses

-- filings table
SELECT * FROM filings WHERE filed_by_entity_id IN ('entity_primetime', 'entity_origin', 'entity_openhaul')
    AND filing_year = 2024;
-- Returns: 3 Nevada annual reports, 3 tax returns, 2 FMCSA updates

-- brand_assets table
SELECT * FROM brand_assets WHERE owned_by_entity_id IN ('entity_origin', 'entity_openhaul');
-- Returns: Logos, domains, business plans
```

**Qdrant (Semantic Memory):**
```python
# Document embeddings
collection: "corporate_documents"
points: [
    {
        "id": "doc_openhaul_operating_agreement",
        "vector": [...],
        "payload": {
            "document_type": "operating_agreement",
            "entity_id": "entity_openhaul",
            "entity_name": "OpenHaul LLC",
            "text": "Full operating agreement text..."
        }
    },
    {
        "id": "doc_origin_mission",
        "vector": [...],
        "payload": {
            "document_type": "mission_statement",
            "entity_id": "entity_origin",
            "text": "Mission and vision text..."
        }
    }
]

# Semantic search example:
query = "What are the buy-sell provisions for OpenHaul?"
# Returns: Operating agreement with Article 9 highlighted
```

**Redis (Working Memory):**
```redis
# Upcoming compliance deadlines (next 90 days)
ZADD compliance:deadlines 1738281600 "entity_origin:annual_report:2026-01-31"
ZADD compliance:deadlines 1738368000 "entity_openhaul:annual_report:2026-01-31"
ZADD compliance:deadlines 1740873600 "entity_origin:tax_return:2026-03-15"

# License status cache (5-minute TTL)
SET license:entity_origin:DOT "active" EX 300
SET license:entity_openhaul:MC "active" EX 300

# Domain expiration monitoring
SET domain:origintransport.com:expiry "2027-02-05" EX 86400
```

**Graphiti (Temporal Memory):**
```python
# Ownership evolution
Primetime_Ownership_History = [
    {"owner": "person_g", "percentage": 100.0, "valid_from": "2018-01-15", "valid_to": null}
]

# Entity status evolution
Origin_Status_History = [
    {"status": "formation", "date": "2018-02-01"},
    {"status": "active", "date": "2018-02-15"},  # After licenses granted
    {"status": "good_standing", "date": "2018-02-15", "maintained": True}
]

# License compliance history
Origin_DOT_Compliance = [
    {"check_type": "mcs_150", "check_date": "2020-02-15", "status": "compliant"},
    {"check_type": "mcs_150", "check_date": "2022-02-10", "status": "compliant"},
    {"check_type": "mcs_150", "check_date": "2024-02-10", "status": "compliant"}
]
```

---

## Advanced Query Patterns

### Query 1: Show Complete Ownership Chain for Entity

```cypher
// Neo4j - Recursive ownership traversal
MATCH path = (p:Person)-[:OWNS*1..5]->(e:LegalEntity {entity_id: "entity_origin"})
WITH p, e, path, relationships(path) as rels
RETURN
    p.person_id as ultimate_owner,
    [node in nodes(path) | CASE
        WHEN node:Person THEN node.first_name + " " + node.last_name
        WHEN node:LegalEntity THEN node.legal_name
    END] as ownership_chain,
    [rel in rels | rel.percentage] as ownership_percentages,
    reduce(pct = 100.0, rel IN rels | pct * rel.percentage / 100.0) as effective_ownership_percentage
ORDER BY effective_ownership_percentage DESC
```

**Result for Origin:**
```
ultimate_owner: "person_g"
ownership_chain: ["Richard Glaubitz", "Primetime LLC", "Origin Transport LLC"]
ownership_percentages: [100.0, 100.0]
effective_ownership_percentage: 100.0
```

---

### Query 2: Compliance Deadline Report (Next 90 Days)

```sql
-- PostgreSQL - Upcoming compliance deadlines
WITH upcoming_deadlines AS (
    -- License renewals
    SELECT
        'License Renewal' as deadline_type,
        e.legal_name as entity_name,
        l.license_type,
        l.license_number,
        l.expiration_date as deadline_date,
        l.expiration_date - INTERVAL '30 days' as reminder_date,
        'License expires' as action_required
    FROM licenses l
    JOIN legal_entities e ON l.issued_to_entity_id = e.entity_id
    WHERE l.expiration_date IS NOT NULL
      AND l.expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
      AND l.status = 'active'

    UNION ALL

    -- Annual filings
    SELECT
        'Annual Filing' as deadline_type,
        e.legal_name,
        NULL as license_type,
        NULL as license_number,
        e.next_filing_due_date as deadline_date,
        e.next_filing_due_date - INTERVAL '30 days' as reminder_date,
        'Annual report due' as action_required
    FROM legal_entities e
    WHERE e.next_filing_due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
      AND e.status = 'active'

    UNION ALL

    -- Domain expirations
    SELECT
        'Domain Renewal' as deadline_type,
        e.legal_name,
        ba.domain_name as license_type,
        NULL as license_number,
        ba.domain_expiration_date as deadline_date,
        ba.domain_expiration_date - INTERVAL '30 days' as reminder_date,
        'Domain renews' as action_required
    FROM brand_assets ba
    JOIN legal_entities e ON ba.owned_by_entity_id = e.entity_id
    WHERE ba.asset_type = 'domain'
      AND ba.domain_expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
      AND ba.status = 'active'
)
SELECT
    deadline_type,
    entity_name,
    COALESCE(license_type, 'N/A') as item,
    COALESCE(license_number, '') as number,
    deadline_date,
    reminder_date,
    deadline_date - CURRENT_DATE as days_until_due,
    action_required
FROM upcoming_deadlines
ORDER BY deadline_date ASC;
```

---

### Query 3: Entity Good Standing Validation

```sql
-- PostgreSQL - Check if all entities are in good standing
WITH entity_compliance AS (
    SELECT
        e.entity_id,
        e.legal_name,
        e.status,
        e.good_standing,
        e.last_filing_date,
        e.next_filing_due_date,
        CASE
            WHEN e.next_filing_due_date < CURRENT_DATE THEN 'OVERDUE FILING'
            WHEN e.next_filing_due_date - CURRENT_DATE <= 30 THEN 'FILING DUE SOON'
            ELSE 'OK'
        END as filing_status,
        COUNT(l.license_id) FILTER (WHERE l.status = 'expired') as expired_licenses,
        COUNT(l.license_id) FILTER (WHERE l.expiration_date < CURRENT_DATE AND l.status = 'active') as overdue_renewals
    FROM legal_entities e
    LEFT JOIN licenses l ON e.entity_id = l.issued_to_entity_id
    WHERE e.status = 'active'
    GROUP BY e.entity_id, e.legal_name, e.status, e.good_standing, e.last_filing_date, e.next_filing_due_date
)
SELECT
    legal_name,
    status,
    good_standing,
    filing_status,
    expired_licenses,
    overdue_renewals,
    CASE
        WHEN good_standing = false THEN '❌ NOT IN GOOD STANDING'
        WHEN filing_status = 'OVERDUE FILING' THEN '⚠️ OVERDUE FILING'
        WHEN expired_licenses > 0 THEN '⚠️ EXPIRED LICENSES'
        WHEN overdue_renewals > 0 THEN '⚠️ OVERDUE RENEWALS'
        WHEN filing_status = 'FILING DUE SOON' THEN '⚡ ACTION REQUIRED'
        ELSE '✅ COMPLIANT'
    END as compliance_status
FROM entity_compliance
ORDER BY
    CASE
        WHEN good_standing = false THEN 1
        WHEN filing_status = 'OVERDUE FILING' THEN 2
        WHEN expired_licenses > 0 THEN 3
        WHEN overdue_renewals > 0 THEN 4
        WHEN filing_status = 'FILING DUE SOON' THEN 5
        ELSE 6
    END,
    legal_name;
```

---

### Query 4: License Inventory by Entity

```cypher
// Neo4j - Complete license inventory
MATCH (e:LegalEntity)-[:HOLDS_LICENSE]->(l:License)
RETURN
    e.legal_name as entity,
    collect({
        type: l.license_type,
        number: l.license_number,
        status: l.status,
        expiration: l.expiration_date,
        annual_fee: l.annual_fee
    }) as licenses,
    sum(l.annual_fee) as total_annual_fees
ORDER BY e.legal_name
```

---

### Query 5: Find Entities Requiring Specific License Type

```sql
-- PostgreSQL - Entities missing required licenses
WITH required_licenses AS (
    SELECT 'entity_origin' as entity_id, 'DOT' as required_license_type
    UNION ALL
    SELECT 'entity_origin', 'state_business_license'
    UNION ALL
    SELECT 'entity_openhaul', 'MC'
    UNION ALL
    SELECT 'entity_openhaul', 'state_business_license'
),
current_licenses AS (
    SELECT
        issued_to_entity_id as entity_id,
        license_type
    FROM licenses
    WHERE status = 'active'
)
SELECT
    e.legal_name,
    rl.required_license_type,
    CASE
        WHEN cl.license_type IS NULL THEN '❌ MISSING'
        ELSE '✅ HELD'
    END as status
FROM required_licenses rl
JOIN legal_entities e ON rl.entity_id = e.entity_id
LEFT JOIN current_licenses cl ON rl.entity_id = cl.entity_id AND rl.required_license_type = cl.license_type
WHERE cl.license_type IS NULL
ORDER BY e.legal_name, rl.required_license_type;
```

---

### Query 6: Domain Portfolio Summary

```sql
-- PostgreSQL - All domains with expiration tracking
SELECT
    e.legal_name as entity,
    ba.domain_name,
    ba.domain_registrar,
    ba.domain_expiration_date,
    ba.auto_renewal,
    ba.domain_expiration_date - CURRENT_DATE as days_until_expiry,
    CASE
        WHEN ba.domain_expiration_date < CURRENT_DATE THEN '❌ EXPIRED'
        WHEN ba.domain_expiration_date - CURRENT_DATE <= 30 THEN '⚠️ EXPIRING SOON'
        WHEN ba.auto_renewal = false AND ba.domain_expiration_date - CURRENT_DATE <= 90 THEN '⚡ RENEWAL NEEDED'
        ELSE '✅ OK'
    END as status
FROM brand_assets ba
JOIN legal_entities e ON ba.owned_by_entity_id = e.entity_id
WHERE ba.asset_type = 'domain'
  AND ba.status = 'active'
ORDER BY ba.domain_expiration_date ASC;
```

---

### Query 7: Annual Filing Compliance History

```sql
-- PostgreSQL - Filing compliance over time
SELECT
    e.legal_name,
    f.filing_year,
    f.filing_type,
    f.due_date,
    f.filing_date,
    CASE
        WHEN f.filing_date <= f.due_date THEN 'On Time'
        WHEN f.filing_date <= f.due_date + INTERVAL '30 days' THEN 'Late (Grace Period)'
        WHEN f.filing_date > f.due_date + INTERVAL '30 days' THEN 'Late (Penalty)'
        ELSE 'Unknown'
    END as timeliness,
    f.filing_date - f.due_date as days_late_or_early
FROM filings f
JOIN legal_entities e ON f.filed_by_entity_id = e.entity_id
WHERE f.filing_type IN ('annual_report', 'tax_return')
  AND f.status = 'filed'
  AND f.filing_year >= 2020
ORDER BY e.legal_name, f.filing_year DESC, f.filing_type;
```

---

### Query 8: Corporate Document Version History

```cypher
// Neo4j - Document version chain
MATCH (latest:CompanyDocument {status: "active"})
WHERE latest.document_type = "operating_agreement"
  AND latest.owned_by_entity_id = "entity_openhaul"
OPTIONAL MATCH path = (latest)-[:SUPERSEDES*]->(older:CompanyDocument)
WITH latest, path, nodes(path) as version_chain
RETURN
    latest.document_title,
    [doc in version_chain | {
        version: doc.version,
        effective_date: doc.effective_date,
        status: doc.status
    }] as version_history
```

---

### Query 9: Calculate Total Annual Compliance Costs

```sql
-- PostgreSQL - Annual compliance cost summary
WITH compliance_costs AS (
    -- License annual fees
    SELECT
        e.legal_name as entity,
        'License Fees' as cost_category,
        SUM(l.annual_fee) as annual_cost
    FROM licenses l
    JOIN legal_entities e ON l.issued_to_entity_id = e.entity_id
    WHERE l.status = 'active'
      AND l.annual_fee > 0
    GROUP BY e.legal_name

    UNION ALL

    -- Average filing fees (based on last 3 years)
    SELECT
        e.legal_name,
        'Filing Fees' as cost_category,
        AVG(f.filing_fee) * COUNT(DISTINCT f.filing_type) as annual_cost
    FROM filings f
    JOIN legal_entities e ON f.filed_by_entity_id = e.entity_id
    WHERE f.filing_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 3
      AND f.status = 'filed'
    GROUP BY e.legal_name

    UNION ALL

    -- Domain renewals
    SELECT
        e.legal_name,
        'Domain Renewals' as cost_category,
        COUNT(ba.asset_id) * 15.00 as annual_cost  # Avg $15/domain
    FROM brand_assets ba
    JOIN legal_entities e ON ba.owned_by_entity_id = e.entity_id
    WHERE ba.asset_type = 'domain'
      AND ba.status = 'active'
    GROUP BY e.legal_name
)
SELECT
    entity,
    SUM(CASE WHEN cost_category = 'License Fees' THEN annual_cost ELSE 0 END) as license_fees,
    SUM(CASE WHEN cost_category = 'Filing Fees' THEN annual_cost ELSE 0 END) as filing_fees,
    SUM(CASE WHEN cost_category = 'Domain Renewals' THEN annual_cost ELSE 0 END) as domain_fees,
    SUM(annual_cost) as total_annual_compliance_cost
FROM compliance_costs
GROUP BY entity
ORDER BY total_annual_compliance_cost DESC;
```

---

### Query 10: Entity Relationship Map (Ownership + Operations)

```cypher
// Neo4j - Complete entity relationship visualization
MATCH (p:Person)-[:OWNS*1..3]->(e:LegalEntity)
OPTIONAL MATCH (e)-[:HOLDS_LICENSE]->(l:License)
OPTIONAL MATCH (e)-[:OWNS_FLEET]->(t:Tractor)
OPTIONAL MATCH (e)-[:BOOKS]->(load:Load)
OPTIONAL MATCH (e)<-[:BELONGS_TO]-(doc:CompanyDocument)
WITH p, e, l, t, load, doc
RETURN
    p.person_id as owner,
    e.entity_id as entity,
    e.legal_name as entity_name,
    COUNT(DISTINCT l) as licenses_held,
    COUNT(DISTINCT t) as trucks_owned,
    COUNT(DISTINCT load) as loads_booked,
    COUNT(DISTINCT doc) as documents_filed
ORDER BY e.legal_name
```

---

## Cross-Hub Integration Patterns

### Hub 6 → Hub 1 (G - Command Center)

**G owns all entities:**
```cypher
// Personal ownership
(G:Person {person_id: "person_g"})-[:OWNS]->(LegalEntity)

// Projects targeting corporate initiatives
(Project {name: "Corporate Restructuring 2025"})-[:TARGETS]->(LegalEntity {entity_id: "entity_primetime"})

// Goals tied to entity performance
(Goal {goal_type: "financial", target: "Origin profitability 15%"})-[:APPLIES_TO]->(LegalEntity {entity_id: "entity_origin"})

// Knowledge items about entities
(KnowledgeItem {type: "protocol", title: "Annual Filing Checklist"})-[:APPLIES_TO]->(LegalEntity)
```

---

### Hub 6 → Hub 4 (Contacts)

**Entities have corresponding Company records:**
```cypher
// LegalEntity = legal structure, Company = CRM record
(LegalEntity {entity_id: "entity_origin"})-[:COMPANY_RECORD]->(Company {company_id: "company_origin"})

// Same for all entities
(LegalEntity {entity_id: "entity_openhaul"})-[:COMPANY_RECORD]->(Company {company_id: "company_openhaul"})

// Ownership links to Person records
(Person {person_id: "person_g"})-[:OWNS]->(LegalEntity)
(Person {person_id: "person_travis"})-[:OWNS]->(LegalEntity {entity_id: "entity_openhaul"})

// Registered agents, attorneys are also Person records
(RegisteredAgent:Person)-[:SERVES_AS_AGENT]->(LegalEntity)
```

**Key Distinction:**
- **Hub 4 Company:** Relationship/operational record (customer, vendor, carrier roles)
- **Hub 6 LegalEntity:** Legal/compliance structure (ownership, licenses, filings)

---

### Hub 6 → Hub 5 (Financials)

**License fees and filing costs create expenses:**
```cypher
// License annual fee → Expense
(License {license_type: "MC", annual_fee: 300.00})-[:CREATES_EXPENSE]->(Expense {
    category: "license_fees",
    amount: 300.00,
    assigned_to: "entity_openhaul",
    expense_date: "2025-07-15"
})

// Filing fee → Expense
(Filing {filing_type: "annual_report", filing_fee: 350.00})-[:CREATES_EXPENSE]->(Expense {
    category: "filing_fees",
    amount: 350.00,
    assigned_to: "entity_origin",
    expense_date: "2025-01-20"
})

// Expenses assigned to entities
(Expense)-[:ASSIGNED_TO]->(LegalEntity)

// Revenue earned by entities
(Revenue)-[:EARNED_BY]->(LegalEntity)

// Intercompany transfers between entities
(IntercompanyTransfer {
    amount: 10000.00,
    purpose: "Working capital loan"
})-[:FROM]->(LegalEntity {entity_id: "entity_origin"})
(IntercompanyTransfer)-[:TO]->(LegalEntity {entity_id: "entity_openhaul"})
```

---

### Hub 6 → Hub 2 (OpenHaul)

**Loads require operating authority:**
```cypher
// MC authority required to broker loads
(Load {load_number: "OH-321678"})-[:REQUIRES_LICENSE]->(License {
    license_type: "MC",
    license_number: "MC-234567",
    issued_to_entity_id: "entity_openhaul"
})

// Entity books loads
(LegalEntity {entity_id: "entity_openhaul"})-[:BOOKS]->(Load)

// Carrier authority validation
MATCH (l:Load)-[:HAULED_BY]->(c:Carrier)
MATCH (c)-[:HOLDS_LICENSE]->(lic:License {license_type: "DOT"})
WHERE lic.status = 'active'
RETURN l, c, lic  // Validates carrier has active DOT authority
```

---

### Hub 6 → Hub 3 (Origin)

**Entity owns fleet:**
```cypher
// Corporate ownership of trucks
(LegalEntity {entity_id: "entity_origin"})-[:OWNS_FLEET]->(Fleet)
(LegalEntity)-[:OWNS]->(Tractor {unit_number: "6520"})

// DOT authority required for truck operations
(Tractor)-[:OPERATED_UNDER]->(License {
    license_type: "DOT",
    license_number: "DOT-789012",
    issued_to_entity_id: "entity_origin"
})

// Driver CDLs linked to employment
(Driver {driver_id: "driver_robert"})-[:EMPLOYED_BY]->(LegalEntity {entity_id: "entity_origin"})
(Driver)-[:HOLDS_LICENSE]->(License {license_type: "CDL", issued_to_person_id: "person_robert"})
```

---

## Bi-Temporal Tracking Patterns

### Example 1: Ownership Changes Over Time

**Track ownership evolution (e.g., if Travis sold shares to G):**

```cypher
// Historical ownership (Travis owned 50%)
(:Person {person_id: "person_travis"})-[:OWNED {
    percentage: 50.0,
    valid_from: "2019-06-15T00:00:00Z",
    valid_to: "2024-06-01T00:00:00Z",
    transaction_time: "2019-06-15T00:00:00Z"
}]->(:LegalEntity {entity_id: "entity_openhaul"})

// G's ownership increased from 50% to 100%
(:Person {person_id: "person_g"})-[:OWNED {
    percentage: 50.0,
    valid_from: "2019-06-15T00:00:00Z",
    valid_to: "2024-06-01T00:00:00Z"
}]->(:LegalEntity {entity_id: "entity_openhaul"})

// Current ownership (G owns 100%)
(:Person {person_id: "person_g"})-[:OWNS {
    percentage: 100.0,
    valid_from: "2024-06-01T00:00:00Z",
    valid_to: null,
    transaction_time: "2024-06-01T15:30:00Z",
    acquisition_method: "purchase",
    purchase_price: 50000.00
}]->(:LegalEntity {entity_id: "entity_openhaul"})
```

**Enables temporal queries:**
- "Who owned OpenHaul on January 1, 2023?" → G (50%), Travis (50%)
- "When did ownership change?" → June 1, 2024
- "What did G pay for Travis's shares?" → $50,000

---

### Example 2: License Status Evolution

**Track license status changes (active → suspended → reinstated):**

```cypher
// Original active status
(:License {license_id: "lic_origin_dot"})-[:HAD_STATUS {
    status: "active",
    valid_from: "2018-02-15",
    valid_to: "2022-08-01",
    transaction_time: "2018-02-15"
}]

// Suspended (safety audit failure)
(:License)-[:HAD_STATUS {
    status: "suspended",
    status_reason: "Failed DOT safety audit - brake violations",
    valid_from: "2022-08-01",
    valid_to: "2022-09-15",
    transaction_time: "2022-08-01"
}]

// Reinstated (after corrective actions)
(:License)-[:HAD_STATUS {
    status: "active",
    status_reason: "Corrective actions completed and verified",
    valid_from: "2022-09-15",
    valid_to: null,
    transaction_time: "2022-09-15"
}]
```

**Enables queries:**
- "Was Origin's DOT active on August 15, 2022?" → No (suspended)
- "Why was it suspended?" → Safety audit failure
- "When was it reinstated?" → September 15, 2022

---

### Example 3: Entity Good Standing Changes

**Track good standing status with state:**

```cypher
// Good standing maintained
(:LegalEntity {entity_id: "entity_origin"})-[:HAD_STANDING {
    good_standing: true,
    valid_from: "2018-02-01",
    valid_to: "2021-02-28",
    last_filing_date: "2021-01-15"
}]

// Lost good standing (missed filing deadline)
(:LegalEntity)-[:HAD_STANDING {
    good_standing: false,
    valid_from: "2021-02-28",
    valid_to: "2021-03-15",
    reason: "Missed annual report deadline (2021-01-31)"
}]

// Good standing restored
(:LegalEntity)-[:HAD_STANDING {
    good_standing: true,
    valid_from: "2021-03-15",
    valid_to: null,
    last_filing_date: "2021-03-10",
    late_fee_paid: 100.00
}]
```

---

## Database Distribution Summary

### Neo4j (Relationship Memory)
**Stores:**
- LegalEntity nodes (basic identification)
- Ownership relationships (person → entity, entity → entity)
- License → entity relationships
- Entity → operations relationships (entity → load, entity → tractor)
- Brand asset ownership
- Document ownership
- Temporal relationships (HAD_STATUS, OWNED, HAD_STANDING)

**Why:** Graph traversal for "Show ownership chain", "What licenses does Origin need?", "Map corporate structure"

---

### PostgreSQL (Factual Memory)
**Stores:**
- Complete entity details (all 35 properties)
- Complete ownership records (all 18 properties)
- Complete license details (all 28 properties)
- Filing records (all 25 properties)
- Brand asset metadata (all 30 properties)
- Company document metadata (all 22 properties)
- Award records (all 20 properties)

**Why:** Structured analytics like "Total annual compliance costs", "Filing history by entity", "License inventory report"

---

### Qdrant (Semantic Memory)
**Stores:**
- Company document embeddings (operating agreements, bylaws, business plans)
- Brand asset descriptions
- Filing document embeddings (annual reports, tax returns)
- License/permit document embeddings

**Why:** Semantic search like "Find documents mentioning profit distribution" or "Search for trademark applications"

---

### Redis (Working Memory)
**Stores:**
- Upcoming compliance deadlines (sorted set by due date, 90-day window)
- License status cache (active/expired, 5-minute TTL)
- Domain expiration alerts (30-day window)
- Recent filings (rolling 30-day window)

**Why:** Fast access for compliance dashboards "What's due this month?" or "Are all licenses current?"

---

### Graphiti (Temporal Memory)
**Stores:**
- Ownership change history
- License status evolution (active → suspended → reinstated)
- Good standing changes over time
- Document version history
- Filing compliance trends

**Why:** Temporal queries like "When did ownership change?" or "Track compliance history over 5 years"

---

## Completion Status

**Hub 6 Complete Baseline:**
- ✅ **Entities Defined:** 7 core entities with 178 properties total
  - LegalEntity: 35 properties
  - Ownership: 18 properties
  - License: 28 properties
  - Filing: 25 properties
  - BrandAsset: 30 properties
  - CompanyDocument: 22 properties
  - Award: 20 properties
- ✅ **License Types:** 16 types documented (DOT, MC, state licenses, certifications)
- ✅ **Filing Types:** 14 types documented (annual reports, tax returns, FMCSA updates)
- ✅ **Asset Types:** 20 types documented (logos, domains, trademarks, business plans)
- ✅ **Document Types:** 16 types documented (operating agreements, bylaws, policies)
- ✅ **Annual Compliance Calendar:** Complete filing schedule with dates and fees
- ✅ **Relationships Documented:** 15+ relationship types with properties
- ✅ **Database Distribution:** Clear mapping for all 5 databases
- ✅ **Real-World Example:** Primetime → Origin → OpenHaul structure complete
- ✅ **Document Types:** 7 documents with extraction patterns
- ✅ **Extraction Patterns:** Documented for each document type
- ✅ **Advanced Queries:** 10 query patterns documented
- ✅ **Cross-Hub Links:** Complete integration with Hubs 1, 2, 3, 4, 5
- ✅ **Bi-Temporal Tracking:** Ownership evolution, license status, good standing patterns
- ✅ **Primary Keys:** entity_id strategy defined and exemplified
- ✅ **Real-World Grounding:** Built from Nevada LLC structure and FMCSA requirements

**This matches the TARGET LEVEL OF DETAIL from Hubs 2, 3, 4, and 5.**

---

## For Implementation Reference

**Cross-References:**
1. **Hub 1 (G - Command Center)** - [HUB-1-G-DRAFT.md](HUB-1-G-DRAFT.md)
   - G owns all entities
   - Projects target corporate initiatives
   - Goals tied to entity performance

2. **Hub 2 (OpenHaul)** - [HUB-2-OPENHAUL-COMPLETE.md](HUB-2-OPENHAUL-COMPLETE.md)
   - MC authority required for brokerage
   - Entity books loads
   - Carrier authority validation

3. **Hub 3 (Origin Transport)** - [HUB-3-ORIGIN-BASELINE.md](HUB-3-ORIGIN-BASELINE.md)
   - Entity owns fleet
   - DOT authority for truck operations
   - Driver CDL licensing

4. **Hub 4 (Contacts)** - [HUB-4-CONTACTS-COMPLETE.md](HUB-4-CONTACTS-COMPLETE.md)
   - LegalEntity → Company mapping
   - Ownership links to Person records
   - Registered agents as Person records

5. **Hub 5 (Financials)** - [HUB-5-FINANCIALS-COMPLETE.md](HUB-5-FINANCIALS-COMPLETE.md)
   - License fees → Expenses
   - Filing fees → Expenses
   - Intercompany transfers

6. **6-HUB-OVERVIEW.md** - Master navigation
7. **Additional Schema info.md** - Extended property definitions
8. **example entity connections.md** - Cross-hub integration examples

---

**Baseline Established:** November 4, 2025
**Schema Version:** v2.0 (Complete Baseline)
**Completion:** 95% (matches Hub 2, 3, 4, and 5 detail level)
