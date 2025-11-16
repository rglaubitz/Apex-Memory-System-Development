# Deployment Integration Checklist Template

**Purpose:** Use this checklist when adding new features to ensure complete deployment documentation integration.

**Usage:** Copy this template for each new feature, fill in all sections, then integrate into main deployment docs.

---

## Feature Information

**Feature Name:** _______________________
**Status:** [ ] Planned | [ ] In Development | [ ] Complete | [ ] OPTIONAL | [ ] DEFERRED
**Impact:** [ ] Critical | [ ] High | [ ] Medium | [ ] Low
**Deployment Week:** Week ___ (e.g., Week 2, Week 3)
**Estimated Time:** ___ hours

---

## Step 1: Research & Analysis (Phase 1)

**Complete analysis in:** `deployment/FEATURE-ANALYSIS-WORKING-NOTES.md`

- [ ] **Identify Feature**: What does it do? Why is it needed?
- [ ] **Locate Implementation Files**: List all files (workflows, activities, APIs, models)
- [ ] **Database Changes**: Identify migrations, new tables, schema changes
- [ ] **Environment Variables**: List all required env vars with descriptions
- [ ] **Cost Impact**: Estimate monthly cost (low/high range)
- [ ] **Dependencies**: List all prerequisite features/services
- [ ] **APIs**: Identify all new endpoints
- [ ] **Workflows**: List Temporal workflows (if any)

**Research Output:**
- Feature summary table row
- Detailed analysis section (300-500 words)
- Database migration list
- Environment variables list
- Cost estimate justification

---

## Step 2: Component Documentation (Phase 2)

**Create deployment guide:** `deployment/components/[feature-name]/DEPLOYMENT-GUIDE.md`

### Required Sections

- [ ] **Overview**: Feature description, cost, impact, deployment week
- [ ] **Prerequisites**: What must be deployed first? (with cross-references)
- [ ] **Setup Instructions**: Step-by-step deployment (6-10 steps max)
- [ ] **Configuration**: Environment variables table (name, required, default, description)
- [ ] **Deployment Commands**: Bash commands with inline explanations
- [ ] **Verification**: Test commands (3-5 tests minimum)
- [ ] **Troubleshooting**: Common issues with solutions (3-4 issues)
- [ ] **Rollback**: How to disable/remove if needed
- [ ] **Cost Breakdown**: Monthly estimate with itemization
- [ ] **References**: Links to implementation files, tests, related docs

### Quality Checks

- [ ] All bash commands are copy-paste ready
- [ ] All placeholder values clearly marked (e.g., `<PROJECT_ID>`, `$VARIABLE`)
- [ ] Cross-references to other guides use relative paths
- [ ] Cost estimates match DEPLOYMENT-NEEDS.md
- [ ] Deployment week matches PRODUCTION-DEPLOYMENT-PLAN.md

**Guide Length:** 300-500 lines (reference existing guides for format)

---

## Step 3: Prerequisites Integration (Phase 3)

**Update:** `deployment/DEPLOYMENT-NEEDS.md`

### Section 2: API Keys (if applicable)

- [ ] Add row to API keys table:
  - Name
  - Cost (monthly)
  - Purpose
  - How to get
  - Prerequisites
  - Time to setup
  - Checkbox

### Section 3-5: Infrastructure (if applicable)

- [ ] Add GCS buckets (if storage feature)
- [ ] Add service accounts (if new permissions needed)
- [ ] Add NATS/other services (with OPTIONAL marker if needed)

### Cost Summary Table (lines 154-172)

- [ ] Update "API Keys" row if adding API costs
- [ ] Add new row for feature if separate infrastructure cost
- [ ] Recalculate "TOTAL" (Low + High)
- [ ] Update "First 90 Days" calculations

**Cost Update Formula:**
```
New Low Total = Old Low Total + Feature Low Cost
New High Total = Old High Total + Feature High Cost
New Out-of-Pocket (90 days) = New Total - GCP Services Cost
```

---

## Step 4: Workflow Integration (Phase 4)

### Update PRODUCTION-DEPLOYMENT-PLAN.md

**Location:** Week 2-3, after Step 44b (Google Drive Integration)

- [ ] Add new step (e.g., "44k. Enable [Feature Name]")
- [ ] Include:
  - Feature description (1 line)
  - Cost estimate
  - Prerequisites (with "already configured in Step X" reference)
  - Database migration commands (if applicable)
  - Environment variable setup commands
  - Workflow registration (if Temporal workflow)
  - Verification commands (2-3)
  - Reference to component guide

- [ ] Update "Feature Deployment Summary" table at end of section
- [ ] Update "Total Additional Cost" calculation
- [ ] Update "Total Additional Time" calculation

### Update GCP-DEPLOYMENT-GUIDE.md

**Location:** Phase 4.4, Cloud Run deployment command (line ~880-920)

- [ ] Add environment variables to `gcloud run deploy` command:
  ```bash
  --update-env-vars="FEATURE_ENV_VAR_1=value" \
  --update-env-vars="FEATURE_ENV_VAR_2=value"
  ```

- [ ] If OPTIONAL feature, add commented out:
  ```bash
  # OPTIONAL: Uncomment if deploying [Feature Name]
  #   --update-env-vars="FEATURE_ENV_VAR=value" \
  ```

**Additional Phases (if needed):**
- [ ] Phase 2 (Database Deployment): If new database/migration
- [ ] Phase 3 (Temporal Setup): If new Temporal workflows/schedules

---

## Step 5: Quality Assurance (Phase 5)

**Update:** `deployment/INTEGRATION-QA-SUMMARY.md`

- [ ] Add row to "Feature → Component Guide → Main Deployment Plans" table
- [ ] Add row to "Cost Consistency Check" table
- [ ] Validate all cross-references work
- [ ] Validate all bash commands are syntactically correct
- [ ] Validate cost consistency across all docs
- [ ] Validate terminology consistency

### Cross-Reference Validation

- [ ] Component guide exists at documented path
- [ ] Component guide referenced in DEPLOYMENT-NEEDS.md
- [ ] Component guide referenced in PRODUCTION-DEPLOYMENT-PLAN.md
- [ ] Component guide referenced in GCP-DEPLOYMENT-GUIDE.md (if applicable)
- [ ] All links use relative paths (e.g., `../components/feature/DEPLOYMENT-GUIDE.md`)

### Cost Validation

- [ ] DEPLOYMENT-NEEDS.md cost matches component guide
- [ ] PRODUCTION-DEPLOYMENT-PLAN.md summary matches component guide
- [ ] Cost breakdown itemized (not just total)

### Command Validation

- [ ] All `gcloud` commands use correct syntax
- [ ] All environment variables follow naming convention
- [ ] All placeholder values clearly marked
- [ ] All bash commands tested locally (if possible)

---

## Step 6: Documentation Review (Phase 6)

### Self-Review Checklist

- [ ] Read component guide end-to-end (catches copy-paste errors)
- [ ] Verify all cross-references clickable in markdown editor
- [ ] Check for consistent terminology (e.g., "GCS" vs "Google Cloud Storage")
- [ ] Verify deployment week consistent across all docs
- [ ] Verify cost estimates have justification
- [ ] Check for typos/grammar errors

### Integration Checklist

- [ ] Feature appears in `deployment/FEATURE-ANALYSIS-WORKING-NOTES.md`
- [ ] Feature has component guide in `deployment/components/[name]/`
- [ ] Feature referenced in `deployment/DEPLOYMENT-NEEDS.md` (if adds prerequisites)
- [ ] Feature step added to `deployment/PRODUCTION-DEPLOYMENT-PLAN.md`
- [ ] Feature env vars added to `deployment/production/GCP-DEPLOYMENT-GUIDE.md`
- [ ] Feature validated in `deployment/INTEGRATION-QA-SUMMARY.md`

---

## Common Pitfalls to Avoid

❌ **Don't:** Forget to update cost summary table in DEPLOYMENT-NEEDS.md
✅ **Do:** Recalculate totals whenever adding feature costs

❌ **Don't:** Use absolute paths for cross-references
✅ **Do:** Use relative paths (e.g., `../components/feature/DEPLOYMENT-GUIDE.md`)

❌ **Don't:** Mark feature as OPTIONAL without clear criteria
✅ **Do:** Define exactly when to deploy vs. skip (e.g., "only if API needs public access")

❌ **Don't:** Skip verification commands in component guide
✅ **Do:** Provide 3-5 concrete test commands with expected outputs

❌ **Don't:** Estimate costs without itemization
✅ **Do:** Break down costs by service (e.g., API calls, storage, compute)

❌ **Don't:** Forget to update "Total Additional Time" estimate
✅ **Do:** Add feature deployment time to summary calculations

❌ **Don't:** Use inconsistent environment variable names across docs
✅ **Do:** Use exact same variable names in all locations

❌ **Don't:** Reference undeployed dependencies
✅ **Do:** Ensure all dependencies deployed in earlier phases/steps

---

## Integration Timeline

**Estimated Total Time:** 2-4 hours per feature

- **Phase 1 (Research):** 30-60 min
- **Phase 2 (Component Guide):** 60-90 min
- **Phase 3 (Prerequisites):** 15-30 min
- **Phase 4 (Workflow):** 20-40 min
- **Phase 5 (QA):** 15-30 min
- **Phase 6 (Review):** 10-20 min

**Best Practice:** Complete all 6 phases in one session to maintain context and consistency.

---

## Example: Graphiti Integration Checklist

See `deployment/components/graphiti-integration/DEPLOYMENT-GUIDE.md` for a complete example of all checklist items properly executed.

**Key Success Factors:**
- Clear cost breakdown ($10-30/month with usage-based itemization)
- Comprehensive verification (5 test commands with expected outputs)
- Explicit prerequisites (OpenAI/Anthropic API key from Section 2)
- Cross-references to all deployment plans
- OPTIONAL vs. REQUIRED clearly marked

---

**Template Version:** 1.0
**Last Updated:** 2025-11-15
**Maintained By:** Deployment Documentation Team
