# examples: Example Documents and Entity Connections

**Purpose:** Example documents and entity relationship visualizations for understanding the 6-hub schema.

---

## Documents in This Folder

### 1. [Schema Primary Context.md](Schema%20Primary%20Context.md)

**What it is:** Original primary context document explaining the schema foundation.

**When to read:** For historical context and foundational understanding.

**Contains:**
- Original schema concepts
- Initial entity definitions
- Early relationship patterns
- Design rationale

**Note:** Historical reference - see [../01-hub-schemas/](../01-hub-schemas/) for current complete schemas.

---

### 2. [example entity connections.md](example%20entity%20connections.md)

**What it is:** Visual examples of entity relationships across hubs.

**When to read:** When you need to understand how entities connect.

**Contains:**
- Entity relationship diagrams
- Cross-hub connection examples
- Real-world use cases
- Relationship patterns

**Example Scenarios:**
- How a Load connects to Carrier, Customer, Driver, Tractor
- How a Project drives Loads and measures Goals
- How Expenses link to LegalEntity and source_load_number

---

### 3. Example Documents/ (Folder)

**What it is:** Sample documents showing real-world data examples.

**Contents:** (if any exist in the folder)

**Use Cases:**
- Understanding data formats
- Sample data for testing
- Real-world examples for validation

---

### 4. Examples/ (Folder)

**What it is:** Additional example files and reference materials.

**Contents:** (if any exist in the folder)

**Use Cases:**
- Reference implementations
- Code samples
- Additional visualizations

---

## How to Use These Examples

### Understanding Entity Relationships

1. **Read:** [example entity connections.md](example%20entity%20connections.md)
2. **Visualize:** See how entities connect across hubs
3. **Reference:** Use patterns in your implementation

---

### Learning from Real Data

1. **Explore:** Example Documents/ folder
2. **Understand:** Data formats and structures
3. **Apply:** Patterns to your own data

---

## Quick Reference: Common Patterns

### Pattern 1: Load → Multi-Hub Connections

**Entities Involved:**
- Load (Hub 2: OpenHaul)
- Carrier (Hub 2: OpenHaul)
- Customer (Hub 4: Contacts)
- Shipper (Hub 4: Contacts)
- Tractor (Hub 3: Origin)
- Driver (Hub 3: Origin)

**Relationships:**
```cypher
// Load connects to multiple hubs
(Load)-[:HAULED_BY]->(Carrier)
(Load)-[:FOR_CUSTOMER]->(Company:Customer)
(Load)-[:SHIPPED_BY]->(Company:Shipper)
(Load)-[:ASSIGNED_UNIT]->(Tractor)
(Tractor)-[:ASSIGNED_TO]->(Driver)
```

---

### Pattern 2: Project Impact Tracking

**Entities Involved:**
- Project (Hub 1: G)
- Goal (Hub 1: G)
- Load (Hub 2: OpenHaul)
- Revenue (Hub 5: Financials)
- Expense (Hub 5: Financials)

**Relationships:**
```cypher
// Project drives business outcomes
(Project)-[:DRIVES]->(Load)
(Project)-[:AIMS_FOR]->(Goal)
(Goal)-[:MEASURED_BY]->(Revenue)
(Goal)-[:MEASURED_BY]->(Expense)
(Load)-[:GENERATED_REVENUE]->(Revenue)
(Load)-[:INCURRED_EXPENSE]->(Expense)
```

---

### Pattern 3: Intercompany Transactions

**Entities Involved:**
- Expense (Hub 5: Financials)
- LegalEntity (Hub 6: Corporate)
- Load (Hub 2: OpenHaul)

**Relationships:**
```cypher
// OpenHaul pays Origin for hauling
(Expense)-[:PAID_BY]->(LegalEntity:OpenHaul)
(Expense)-[:PAID_TO]->(LegalEntity:Origin)
(Expense)-[:FOR_SOURCE]->(Load)
```

**Key:** Expense.notes contains "Related party transaction" flag

---

## Additional Resources

**For complete entity definitions:**
- See [../01-hub-schemas/complete/](../01-hub-schemas/complete/)

**For relationship validation:**
- See [../02-phase3-validation/PHASE-3-INTEGRATION-PATTERN-VALIDATION.md](../02-phase3-validation/PHASE-3-INTEGRATION-PATTERN-VALIDATION.md)

**For implementation patterns:**
- See [../03-implementation/6-HUB-SCHEMA-CROSS-REFERENCE.md](../03-implementation/6-HUB-SCHEMA-CROSS-REFERENCE.md)

---

## Contributing Examples

If you create useful examples:

1. **Document** the use case clearly
2. **Show** entity relationships
3. **Provide** Neo4j queries or SQL examples
4. **Explain** the business logic
5. **Add** to this folder with descriptive names

**Example naming:**
- `example-load-with-intercompany-carrier.md`
- `example-project-goal-revenue-tracking.md`
- `example-driver-tractor-assignment-history.md`
