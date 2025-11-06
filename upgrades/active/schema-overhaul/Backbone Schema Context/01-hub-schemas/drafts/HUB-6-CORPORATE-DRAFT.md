# HUB 6: CORPORATE INFRASTRUCTURE

**Status:** 📝 Draft - Rough Structure
**Purpose:** Legal structure, compliance, brand assets, company foundations
**Focus:** Everything that makes up the companies that doesn't contribute to day-to-day operations
**Primary Key Strategy:** entity_id for LegalEntity, UUIDs for supporting entities

---

## Purpose

Hub 6 tracks the foundational elements that enable the businesses to exist and operate legally. This includes legal entity structure, licenses, compliance filings, brand assets, and company documentation.

**Key Distinction:** This hub is NON-OPERATIONAL. It's the foundation that day-to-day operations (Hubs 2, 3, 5) run on top of.

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

**Core Properties:**
- **entity_id** (PRIMARY KEY - standardized ID)
- legal_name (official registered name)
- dba_name (doing business as, if applicable)
- entity_type (LLC, S-Corp, C-Corp, Partnership, Sole Proprietorship)
- ein (Employer Identification Number)
- state_of_formation
- formation_date
- business_purpose (from operating agreement)
- registered_agent_name, registered_agent_address
- status (active, dissolved, suspended)

**Operating Details:**
- fiscal_year_end
- accounting_method (cash, accrual)
- number_of_members/shareholders
- management_structure (member-managed, manager-managed)

**Temporal:**
- created_at, updated_at, valid_from, valid_to

**Examples:**
```python
# Holding Company
LegalEntity(
    entity_id="entity_primetime",
    legal_name="Primetime LLC",
    entity_type="LLC",
    ein="XX-XXXXXXX",
    state_of_formation="Nevada",
    formation_date="2018-01-15",
    business_purpose="Holding company for transportation and logistics businesses",
    status="active",
    management_structure="member-managed"
)

# Operating Company - Origin
LegalEntity(
    entity_id="entity_origin",
    legal_name="Origin Transport LLC",
    entity_type="LLC",
    ein="XX-XXXXXXX",
    state_of_formation="Nevada",
    formation_date="2018-02-01",
    business_purpose="Interstate freight transportation services",
    status="active",
    parent_entity_id="entity_primetime"  # Owned by Primetime
)

# Operating Company - OpenHaul
LegalEntity(
    entity_id="entity_openhaul",
    legal_name="OpenHaul LLC",
    entity_type="LLC",
    ein="XX-XXXXXXX",
    state_of_formation="Nevada",
    formation_date="2019-06-15",
    business_purpose="Freight brokerage and logistics services",
    status="active"
)
```

---

### 2. **Ownership** - Relationship Entity
Who owns what percentage of which entity.

**Core Properties:**
- ownership_id (UUID)
- owner_person_id (links to Hub 4 - Person)
- owned_entity_id (which LegalEntity)
- ownership_percentage
- ownership_class (if multiple classes of shares/units)
- acquisition_date
- cost_basis (what they paid for ownership)
- voting_rights (boolean or percentage)
- active_status

**Temporal Tracking:**
- valid_from, valid_to (ownership can change over time)

**Examples:**
```cypher
// Primetime ownership structure
(G:Person)-[:OWNS {
    percentage: 100,
    acquisition_date: "2018-01-15",
    valid_from: "2018-01-15",
    valid_to: null
}]->(Primetime:LegalEntity)

// Origin ownership (via Primetime)
(Primetime:LegalEntity)-[:OWNS {
    percentage: 100,
    acquisition_date: "2018-02-01"
}]->(Origin:LegalEntity)

// OpenHaul ownership (split)
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)
(Travis:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)
```

---

### 3. **License** - Operating Authority & Permits
All licenses, permits, authorities required to operate.

**Core Properties:**
- **license_id** (PRIMARY KEY - UUID)
- license_type (DOT, MC, state_business_license, CDL, etc.)
- license_number
- issuing_authority (FMCSA, State of Nevada, etc.)
- issued_to_entity_id (which LegalEntity)
- issue_date, expiration_date
- status (active, expired, suspended, revoked)
- renewal_required (boolean)
- renewal_date (when to renew)
- document_path (PDF of license/permit)

**Cost:**
- annual_fee, renewal_fee

**Compliance:**
- compliance_requirements [] (what's required to maintain)
- last_compliance_check_date

**Examples:**
```python
# DOT Number - Origin
License(
    license_type="DOT",
    license_number="DOT-789012",
    issuing_authority="FMCSA",
    issued_to_entity_id="entity_origin",
    issue_date="2018-02-15",
    expiration_date=null,  # DOT numbers don't expire
    status="active",
    annual_fee=0
)

# MC Authority - OpenHaul
License(
    license_type="MC",
    license_number="MC-123456",
    issuing_authority="FMCSA",
    issued_to_entity_id="entity_openhaul",
    issue_date="2019-07-01",
    expiration_date=null,  # MC authority doesn't expire
    status="active",
    annual_fee=300  # FMCSA annual fee
)

# Nevada Business License - Origin
License(
    license_type="state_business_license",
    license_number="NV-BL-456789",
    issuing_authority="Nevada Secretary of State",
    issued_to_entity_id="entity_origin",
    issue_date="2018-02-01",
    expiration_date="2026-02-01",  # Renews every few years
    status="active",
    renewal_required=True,
    renewal_date="2025-12-01",  # Renew 2 months early
    annual_fee=200
)
```

---

### 4. **Filing** - Compliance Documents
Annual reports, registrations, state filings.

**Core Properties:**
- **filing_id** (PRIMARY KEY - UUID)
- filing_type (annual_report, registration, amendment, dissolution, etc.)
- filing_authority (Nevada Secretary of State, IRS, etc.)
- filed_by_entity_id (which LegalEntity)
- filing_date
- filing_year (for annual reports)
- status (filed, pending, overdue)
- document_path (PDF of filing)
- confirmation_number

**Cost:**
- filing_fee

**Temporal:**
- due_date, filed_date

**Examples:**
```python
# Annual Report - Nevada
Filing(
    filing_type="annual_report",
    filing_authority="Nevada Secretary of State",
    filed_by_entity_id="entity_origin",
    filing_date="2025-01-15",
    filing_year=2024,
    due_date="2025-01-31",
    status="filed",
    filing_fee=350,
    confirmation_number="NV-AR-2024-123456"
)

# IRS Form 1120 - Corporate Tax Return
Filing(
    filing_type="tax_return",
    filing_authority="IRS",
    filed_by_entity_id="entity_origin",
    filing_date="2025-03-15",
    filing_year=2024,
    due_date="2025-03-15",  # March 15 for corporations
    status="filed"
)
```

---

### 5. **BrandAsset** - Intellectual Property & Marketing
Logos, domains, trademarks, marketing materials.

**Core Properties:**
- **asset_id** (PRIMARY KEY - UUID)
- asset_type (logo, domain, trademark, slogan, business_plan, marketing_deck, etc.)
- asset_name
- owned_by_entity_id (which LegalEntity)
- description
- created_date, acquired_date
- registration_number (if registered trademark/copyright)
- file_path (where asset is stored)
- version (for versioned assets like logos)
- status (active, archived, deprecated)

**Domain-Specific:**
- domain_name (if type = domain)
- domain_registrar
- domain_expiration_date
- auto_renewal (boolean)

**Trademark-Specific:**
- trademark_class (if registered)
- registration_date

**Examples:**
```python
# Logo
BrandAsset(
    asset_type="logo",
    asset_name="Origin Transport Primary Logo",
    owned_by_entity_id="entity_origin",
    description="Primary logo with eagle and road imagery",
    created_date="2018-02-15",
    version="v3.0",
    file_path="/brand-assets/origin/logos/origin-logo-v3.svg",
    status="active"
)

# Domain
BrandAsset(
    asset_type="domain",
    asset_name="origintransport.com",
    owned_by_entity_id="entity_origin",
    domain_name="origintransport.com",
    domain_registrar="GoDaddy",
    domain_expiration_date="2027-02-15",
    auto_renewal=True,
    status="active"
)

# Business Plan
BrandAsset(
    asset_type="business_plan",
    asset_name="Origin Transport Business Plan 2025-2030",
    owned_by_entity_id="entity_origin",
    description="5-year strategic business plan",
    created_date="2024-12-01",
    version="2025.1",
    file_path="/corporate-docs/origin/business-plans/2025-2030.pdf",
    status="active"
)
```

---

### 6. **CompanyDocument** - Operating Agreements, Policies, Plans
Foundational company documents.

**Core Properties:**
- **document_id** (PRIMARY KEY - UUID)
- document_type (operating_agreement, bylaws, shareholder_agreement, employee_handbook, mission_statement, business_plan, etc.)
- document_title
- owned_by_entity_id (which LegalEntity)
- created_date, last_updated_date
- version
- effective_date
- document_path (PDF or file location)
- status (active, archived, superseded)

**Content:**
- summary (brief description)
- key_provisions [] (important clauses/sections)

**Examples:**
```python
# Operating Agreement
CompanyDocument(
    document_type="operating_agreement",
    document_title="OpenHaul LLC Operating Agreement",
    owned_by_entity_id="entity_openhaul",
    created_date="2019-06-15",
    last_updated_date="2023-01-10",
    version="v2.1",
    effective_date="2023-01-15",
    document_path="/corporate-docs/openhaul/operating-agreement-v2.1.pdf",
    status="active",
    summary="Defines ownership structure (50/50 G and Travis), management rights, profit distribution, buy-sell provisions"
)

# Mission Statement
CompanyDocument(
    document_type="mission_statement",
    document_title="Origin Transport Mission & Vision",
    owned_by_entity_id="entity_origin",
    created_date="2018-02-01",
    version="v1.0",
    document_path="/corporate-docs/origin/mission-vision.pdf",
    status="active",
    summary="Company mission: Reliable freight solutions with exceptional service. Vision: Become premier regional carrier in Southwest."
)
```

---

### 7. **Award** (Optional) - Recognition & Certifications
Industry awards, certifications, memberships.

**Core Properties:**
- award_id (UUID)
- award_type (industry_award, certification, membership, recognition)
- award_name
- received_by_entity_id
- issuing_organization
- award_date
- expiration_date (if applicable - e.g., certifications)
- description
- document_path (certificate, plaque photo)

**Examples:**
```python
# Industry Award
Award(
    award_type="industry_award",
    award_name="Carrier of the Year 2024",
    received_by_entity_id="entity_origin",
    issuing_organization="Nevada Trucking Association",
    award_date="2024-11-15",
    description="Recognized for safety record and on-time performance"
)

# Certification
Award(
    award_type="certification",
    award_name="SmartWay Transport Partner",
    received_by_entity_id="entity_origin",
    issuing_organization="EPA",
    award_date="2020-03-01",
    expiration_date="2026-03-01",  # Must renew
    description="Environmental performance certification for freight carriers"
)
```

---

## Primary Relationships

### Ownership Structure
```cypher
// Personal ownership
(G:Person)-[:OWNS {percentage: 100}]->(Primetime:LegalEntity)
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)
(Travis:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)

// Corporate ownership
(Primetime:LegalEntity)-[:OWNS {percentage: 100}]->(Origin:LegalEntity)

// Parent-subsidiary
(Primetime:LegalEntity)-[:PARENT_OF]->(Origin:LegalEntity)
```

### License & Compliance
```cypher
// License issued to entity
(License)-[:ISSUED_TO]->(LegalEntity)
(License)-[:REQUIRED_FOR]->(BusinessActivity)

// Filing by entity
(Filing)-[:FILED_BY]->(LegalEntity)
(Filing)-[:REQUIRED_FOR_COMPLIANCE]->(License)
```

### Brand & Documents
```cypher
// Assets owned by entity
(BrandAsset)-[:OWNED_BY]->(LegalEntity)
(CompanyDocument)-[:BELONGS_TO]->(LegalEntity)

// Document versions
(CompanyDocument {version: "v2.0"})-[:SUPERSEDES]->(CompanyDocument {version: "v1.0"})
```

---

## Cross-Hub Relationships

### Hub 6 → Hub 1 (G)
```cypher
// G owns entities
(G:Person)-[:OWNS]->(LegalEntity)

// Projects target corporate structure
(Project {name: "Corporate Restructuring"})-[:TARGETS]->(LegalEntity)
```

### Hub 6 → Hub 4 (Contacts)
```cypher
// Entities are also companies
(LegalEntity {entity_id: "entity_origin"})-[:COMPANY_RECORD]->(Company {company_id: "company_origin"})

// Ownership links to people
(Person)-[:OWNS]->(LegalEntity)
```

### Hub 6 → Hub 5 (Financials)
```cypher
// Expenses assigned to entities
(Expense)-[:ASSIGNED_TO]->(LegalEntity)

// Revenue earned by entities
(Revenue)-[:EARNED_BY]->(LegalEntity)

// Intercompany transfers
(IntercompanyTransfer)-[:FROM]->(LegalEntity)
(IntercompanyTransfer)-[:TO]->(LegalEntity)
```

### Hub 6 → Hub 2 (OpenHaul)
```cypher
// Loads require operating authority
(Load)-[:REQUIRES_LICENSE]->(License {license_type: "MC"})

// Company books loads
(LegalEntity {entity_id: "entity_openhaul"})-[:BOOKS]->(Load)
```

### Hub 6 → Hub 3 (Origin)
```cypher
// Entity owns fleet
(LegalEntity {entity_id: "entity_origin"})-[:OWNS_FLEET]->(Fleet)
(LegalEntity)-[:OWNS]->(Tractor)

// Trucks require DOT authority
(Tractor)-[:OPERATED_UNDER]->(License {license_type: "DOT"})
```

---

## Database Distribution

### Neo4j (Relationship Memory)
**Stores:**
- LegalEntity nodes
- Ownership relationships (person → entity, entity → entity)
- License → entity relationships
- Brand/document ownership

**Why:** Graph traversal - "Show ownership chain for Origin", "What licenses does OpenHaul need?", "Map corporate structure"

---

### PostgreSQL (Factual Memory)
**Stores:**
- Complete entity details (EIN, formation dates, addresses)
- License details (numbers, dates, fees)
- Filing records (dates, confirmation numbers, fees)
- Brand asset metadata
- Document metadata

**Why:** Structured queries - "List all licenses expiring in next 90 days", "Annual filing history for Origin", "All domains owned by entities"

---

### Qdrant (Semantic Memory)
**Stores:**
- Company document embeddings (operating agreements, business plans, mission statements)
- Brand asset descriptions
- Filing document embeddings

**Why:** Semantic search - "Find company documents mentioning profit distribution", "Search for similar brand assets"

---

### Redis (Working Memory)
**Stores:**
- Upcoming license renewals (next 90 days)
- Recent filings (last 30 days)
- Active entity status (for quick validation)

**Why:** Fast access for compliance checks - "Are all licenses current?", "What filings are due this month?"

---

### Graphiti (Temporal Memory)
**Stores:**
- Ownership changes over time (Travis acquired 50% in 2019)
- License status history
- Document version history
- Entity status changes

**Why:** Temporal queries - "When did ownership structure change?", "Track license compliance history", "Document revision timeline"

---

## Primary Keys & Cross-Database Identity

**LegalEntity:**
```python
# Neo4j
(:LegalEntity {entity_id: "entity_origin", legal_name: "Origin Transport LLC"})

# PostgreSQL
SELECT * FROM legal_entities WHERE entity_id = 'entity_origin'

# Qdrant
filter={"entity_id": "entity_origin"}

# Graphiti
LegalEntity(entity_id="entity_origin", legal_name="Origin Transport LLC", ...)
```

**Link to Hub 4:**
```cypher
// Entity has corresponding Company record
(LegalEntity {entity_id: "entity_origin"})-[:COMPANY_RECORD]->(Company {company_id: "company_origin"})
```

---

## TODO - Information Needed

### Missing Details
- [ ] **Entity Structure:** Exact ownership percentages, formation dates, EINs (sanitized)
- [ ] **License Inventory:** Complete list of all licenses, permits, authorities currently held
- [ ] **Filing Schedule:** Annual filing requirements by entity (Nevada, IRS, FMCSA, etc.)
- [ ] **Domain Inventory:** All domains owned (origin domains, openhaul domains, related)
- [ ] **Brand Assets:** Inventory of logos, marketing materials, versions

### Document Examples
- [ ] Sample operating agreement (sanitized)
- [ ] Sample annual report filing
- [ ] Sample business license
- [ ] Sample logo files (for schema examples)
- [ ] Sample business plan (for document structure)

### Compliance Details
- [ ] **Annual Filing Calendar:** When are filings due for each entity?
- [ ] **License Renewal Schedule:** When do licenses expire/renew?
- [ ] **Compliance Requirements:** What's required to maintain each license?
- [ ] **Insurance Requirements:** Any insurance tied to licenses? (Or in Hub 3?)

### Integration Questions
- [ ] Should Hub 3 truck insurance link to Hub 6 compliance requirements?
- [ ] Should Hub 5 license fees create automatic Expense records?
- [ ] How to track multi-entity assets (e.g., Primetime owns Origin which uses assets)?

---

## Next Steps

1. **Review this draft** - Does corporate infrastructure focus make sense?
2. **Gather entity documents** - Operating agreements, licenses (sanitized)
3. **Create license inventory** - All current licenses and authorities
4. **Map ownership structure** - Exact percentages and dates
5. **Document filing calendar** - Annual compliance requirements
6. **Deep dive** - Expand to full detail matching Hub 3 baseline

---

**Draft Created:** November 3, 2025
**Schema Version:** v2.0 (Draft)
**Completion Status:** ~30% (structure defined, inventory needed)
