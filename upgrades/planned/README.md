# Planned Upgrades

This directory contains early-stage planning for future upgrades that are in the research and ideation phase.

## Overview

Planned upgrades represent identified improvement opportunities that have not yet entered active development. Each planned upgrade includes initial goals, priority assessment, research direction, and comprehensive planning documentation.

**Current Status:** 3 planned upgrades (1 high priority, 2 medium priority)

## Planned Upgrades Index

| Upgrade | Priority | Status | Research Progress | Timeline | Directory |
|---------|----------|--------|-------------------|----------|-----------|
| **Security Layer** | High | 📝 Research | 0% | Before Production | [security-layer/](security-layer/) |
| **Fine-Tuned Embeddings** | High | 📝 Planning | 30% | 1 week | [fine-tuned-embeddings/](fine-tuned-embeddings/) |
| **API Connections & External Integrations** | Medium | 📝 Planning | 20% | 4-6 weeks | [api-connections/](api-connections/) |

---

## Upgrade Stages

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Planned   │────▶│   Active     │────▶│   Testing    │────▶│  Completed   │
│  (Ideas)    │     │ (Executing)  │     │ (Validating) │     │  (Archived)  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │                    │
       ▼                    ▼                     ▼                    ▼
planned/            upgrades/[name]/      upgrades/[name]/      completed/
```

### Planned Phase Criteria

An upgrade is in `planned/` when:
- ✅ Problem or opportunity identified
- ✅ High-level goals defined
- ✅ Priority assigned
- ❌ Comprehensive research NOT yet complete (or in progress)
- ❌ Review Board approval NOT yet obtained
- ❌ Implementation NOT yet started

### Graduation to Active

An upgrade moves from `planned/` to active (`upgrades/[name]/`) when:
1. ✅ Research phase completed (Tier 1-3 sources documented)
2. ✅ Comprehensive IMPROVEMENT-PLAN.md created
3. ✅ Review Board (Phase 3.5) approves the plan
4. ✅ Implementation timeline established
5. ✅ Moved to `upgrades/[name]/` directory

---

## Planned Upgrades Details

### 1. Security Layer Implementation

**Priority:** High (Must-Have Before Production)
**Status:** 📝 Research Phase
**Timeline:** 4 weeks (2 phases)
**Research Progress:** 0%

**Problem Statement:**

The Apex Memory System has ZERO security implementation:
- ❌ No authentication (anyone can access API)
- ❌ No authorization (no user permissions/roles)
- ❌ No rate limiting (vulnerable to abuse/DoS)
- ❌ No encryption (data in plaintext)
- ❌ No audit logging (no tracking)
- ❌ No multi-tenancy (cannot isolate data)

**Goals:**

**Phase 1: Core Security (Must-Have):**
- OAuth2 authentication with JWT tokens
- Redis-based rate limiting (per-user, per-IP)
- TLS/HTTPS encryption
- Audit logging to PostgreSQL

**Phase 2: Advanced Security (Nice-to-Have):**
- Role-Based Access Control (RBAC)
- Data encryption at rest (AES-256-GCM)
- API key management

**Expected Gains:**
- ✅ Complete authentication and authorization
- ✅ DoS protection (100 req/hour/IP rate limit)
- ✅ HTTPS encryption (TLS 1.3)
- ✅ Audit logging (all requests tracked)
- ✅ 80% compliance readiness (SOC 2, GDPR basics)

**Research Needed:**
- OAuth2/OIDC providers (Auth0 vs Keycloak)
- FastAPI security patterns
- Redis rate limiting algorithms
- Encryption key management

**Next Steps:**
1. Compare Auth0 vs Keycloak (cost, features, self-hosted)
2. Design authentication middleware
3. Define rate limit thresholds
4. Create comprehensive security plan

📂 **[Full Planning](security-layer/)**

---

### 2. Fine-Tuned Embeddings for Logistics

**Priority:** High
**Status:** 📝 Planning Phase
**Timeline:** 1 week
**Research Progress:** 30%

**Problem Statement:**

Generic OpenAI embeddings don't capture domain-specific semantics:
- ❌ Poor understanding of freight/logistics terminology
- ❌ Graph routes collapse on ambiguous queries (43.8% medium tier accuracy)
- ❌ Semantic gap between route definitions and training queries
- ❌ Ultra-low learned thresholds cause false positives
- ❌ Cannot fine-tune OpenAI embeddings (API limitation)

**Goals:**

Fine-tune domain-specific embedding model for freight logistics:
- Fine-tune BAAI/bge-base-en-v1.5 on logistics-specific queries
- Use M4 Neural Engine for fast training (5-10 min)
- Specialize for OpenHaul and Origin Transport business domains
- Close semantic gap at embedding level
- Improve graph route classification accuracy

**Expected Gains:**
- Medium tier: 67.8% → 85%+ (+17 points)
- Hard tier: 60.0% → 75%+ (+15 points)
- Graph intent: 66.0% → 80%+ (+14 points)
- Overall: 77.9% → 85-90% (+7-12 points)

**M4 Advantage:**
- Only way to fine-tune embeddings (OpenAI doesn't offer this)
- 16-core Neural Engine (38 TOPS)
- Fast iteration cycles (10 minutes per training run)
- Local training (no data leaving machine)

**Research Needed:**
- Sentence Transformers fine-tuning best practices
- Training data augmentation strategies
- Evaluation metrics for embedding quality
- Deployment patterns for custom embeddings

**Next Steps:**
1. Review Sentence Transformers documentation
2. Create training dataset from logistics queries
3. Implement training script with M4 optimizations
4. Validate on test suite (250+ queries)

📂 **[Full Planning](fine-tuned-embeddings/)**

---

### 3. API Connections & External Integrations

**Priority:** Medium
**Status:** 📝 Planning Phase (FrontApp specification complete)
**Timeline:** 4-6 weeks (4 phases)
**Research Progress:** 20%

**Problem Statement:**

Current system is standalone with no external integrations:
- ❌ No FrontApp conversation history ingestion
- ❌ No CRM contact/account sync
- ❌ No analytics platform integration
- ❌ Manual data entry required
- ❌ No real-time updates from external systems

**Goals:**

Build robust API integration layer to connect with external platforms:
- OAuth 2.0 authentication with external platforms
- Webhook receivers for real-time updates
- Scheduled sync jobs for batch imports
- Bi-directional data synchronization
- Rate limiting and retry logic

**Key Integrations:**

**Priority 1: FrontApp**
- Conversation history import
- Real-time message sync via webhooks
- Contact metadata extraction
- Expected volume: ~1000 conversations/day, ~5000 messages/day

**Priority 2: CRM Systems (Salesforce/HubSpot)**
- Account/contact sync
- Deal pipeline tracking
- Activity history
- Custom field mapping

**Priority 3: Analytics Platforms (Google Analytics/Mixpanel)**
- Event stream ingestion
- User session data
- Conversion funnel metrics
- Cohort analysis data

**Expected Gains:**
- ✅ Automatic ingestion from 5+ external platforms
- ✅ Real-time updates via webhooks (<30 second latency)
- ✅ 99.9% sync reliability
- ✅ Zero manual data entry
- ✅ Complete conversation context for support queries

**Implementation Phases:**
1. **Week 1-2:** Integration framework (OAuth2 layer, webhook infrastructure, sync scheduler)
2. **Week 3-4:** FrontApp integration (OAuth connection, conversation sync, webhook handler)
3. **Week 5-6:** CRM integration (Salesforce/HubSpot sync, data mapping)
4. **Week 7-8:** Monitoring and admin interface (dashboard, sync logs, retry management)

**Research Foundation:**
- [FrontApp API Documentation](https://dev.frontapp.com/) - Complete API reference
- [OAuth 2.0 Best Practices](https://oauth.net/2/) - Authentication standards
- [Webhook Security](https://webhook.site/docs) - Signature validation patterns

**FrontApp Specification:**
- Complete OAuth 2.0 flow implementation
- Webhook handler with HMAC signature validation
- Sync manager with pagination and rate limiting (5 req/sec)
- Entity extraction and sentiment analysis
- Real-time conversation updates

**Next Steps:**
1. Review FrontApp API documentation in detail
2. Design OAuth authentication flow
3. Prototype webhook receiver and signature validation
4. Implement POC for single conversation sync

📂 **[Full Planning](api-connections/)** | 📄 **[FrontApp Integration Spec](api-connections/INTEGRATIONS.md)**

---

## Research Phase Workflow

### 1. Problem Validation
- Confirm problem exists and is significant
- Assess impact vs effort
- Verify alignment with project goals
- Document current state limitations

### 2. Research Gathering
- Find Tier 1 sources (official documentation)
- Locate Tier 2 examples (1.5k+ star repos)
- Document Tier 3+ supporting materials
- Store in `research/documentation/[topic]/`
- Track sources in `research/references.md`

### 3. Solution Exploration
- Evaluate alternative approaches
- Identify proven patterns from research
- Document trade-offs and costs
- Estimate complexity and timeline
- Create architecture diagrams

### 4. Plan Creation
- Create comprehensive IMPROVEMENT-PLAN.md
- Define phased implementation approach
- Establish success metrics and benchmarks
- Identify risks and mitigation strategies
- Include code examples from research

### 5. Review Board Submission (Phase 3.5)
- Submit to C-suite executive review
- **CIO**: Validates research quality and source hierarchy
- **CTO**: Validates technical approach and architecture
- **COO**: Validates execution feasibility and timelines
- All 3 must approve before implementation begins

### 6. Graduation to Active
- Move from `planned/` to `upgrades/[name]/`
- Begin Phase 4 (Implementation)
- Track progress with TodoWrite
- Update status in main README

---

## Adding New Planned Upgrades

### 1. Identify Opportunity

**Questions to Answer:**
- What problem does this solve?
- What value does it provide?
- Is it aligned with project goals?
- What is the priority relative to other work?

### 2. Create Directory Structure

```bash
mkdir upgrades/planned/[upgrade-name]
cd upgrades/planned/[upgrade-name]
```

### 3. Create Initial README

```markdown
# [Upgrade Name]

**Priority:** [High/Medium/Low]
**Status:** 📝 Research Phase
**Timeline:** TBD
**Research Progress:** 0%

## Problem Statement
[What problem are we solving?]

## Goals
- Goal 1
- Goal 2

## Expected Gains
- Metric 1: X% improvement
- Metric 2: Y reduction

## Research Needed
- Topic 1 (Tier 1 sources)
- Topic 2 (Tier 2 examples)

## Next Steps
1. Research phase
2. POC development
3. Plan creation
```

### 4. Gather Research

Follow research-first principles:
- Official documentation (Tier 1)
- Verified examples (Tier 2, 1.5k+ stars)
- Technical standards (Tier 3)
- Document in `research/documentation/[topic]/`

### 5. Create Comprehensive Plan

When research is complete:
- Create detailed IMPROVEMENT-PLAN.md
- Define phased implementation
- Include code examples
- Cite research sources
- Establish success criteria

### 6. Add to Planned Index

Update this README with new entry in index table and details section.

---

## Priority Guidelines

### High Priority
- Critical bugs or security issues
- Blocks other important work
- Required before production launch
- High user impact
- Quick wins with major benefits
- Research complete and ready for implementation

### Medium Priority
- Significant improvements
- Moderate user impact
- Good ROI but not urgent
- Foundational for future work
- Research in progress

### Low Priority
- Nice-to-have features
- Limited immediate impact
- Experimental or exploratory
- Future-looking capabilities
- Research not yet started

---

## Success Criteria for Graduation

An upgrade is ready to graduate from `planned/` to active when:

### Research Complete
- ✅ Tier 1 sources documented (official docs)
- ✅ Tier 2 examples identified (1.5k+ stars)
- ✅ Alternative approaches evaluated
- ✅ Sources cited in `research/references.md`

### Plan Complete
- ✅ Comprehensive IMPROVEMENT-PLAN.md created
- ✅ Phased implementation defined (week-by-week)
- ✅ Success metrics established
- ✅ Code examples included
- ✅ Risks and mitigation identified

### Review Board Approved
- ✅ CIO approved (research quality)
- ✅ CTO approved (technical architecture)
- ✅ COO approved (execution feasibility)

### Ready for Implementation
- ✅ Timeline established
- ✅ Dependencies identified
- ✅ Team capacity confirmed
- ✅ Migration path from `planned/` to `upgrades/[name]/`

---

## Benefits of Planned Directory

**Organized Ideation:**
- Capture ideas before they're forgotten
- Structure early thinking
- Prioritize competing opportunities
- Track research progress transparently

**Research Tracking:**
- Document what's been explored
- Track source quality (Tier 1-5 hierarchy)
- Avoid duplicate research work
- Build institutional knowledge

**Transparent Roadmap:**
- Stakeholders see future direction
- Contributors know what's coming
- Clear priorities established
- Research-first compliance enforced

**Quality Gate:**
- Research phase validates approach
- Review Board prevents premature implementation
- Phased plans reduce risk
- Success criteria defined upfront

**Graduation Path:**
- Smooth transition to active development
- Quality gate enforcement (Phase 3.5 Review Board)
- Research-first principles maintained
- Complete documentation handoff

---

## Cross-References

**Active Upgrades:**
- [Temporal Workflow Orchestration](../active/temporal-implementation/) - Active implementation (6-8 weeks, 4 phases)

**Completed Upgrades:**
- [Query Router Improvement Plan](../completed/query-router/) - ✅ Oct 2025
- [Documentation System](../completed/documentation-system/) - ✅ Oct 2025
- [Cross-Reference System](../completed/cross-reference-system/) - ✅ Oct 2025

**Related Documentation:**
- [Main Upgrades README](../) - Complete upgrade lifecycle
- [Research Directory](../../research/) - Documentation and examples
- [Review Board Agents](../../.claude/agents/) - C-suite validation (CIO, CTO, COO)
- [Architecture Analysis 2025](../../ARCHITECTURE-ANALYSIS-2025.md) - Current architecture research

**Research Links:**
- [Temporal.io Docs](https://docs.temporal.io/) - Workflow orchestration
- [FrontApp API](https://dev.frontapp.com/) - External integrations
- [OAuth 2.0 Spec](https://oauth.net/2/) - Authentication standards

---

## Metrics

**Current Pipeline Status:**
- ✅ Completed: 3 upgrades (Query Router, Documentation System, Cross-Reference System)
- 🚀 Active: 1 upgrade (Temporal Workflow Orchestration - 6-8 weeks)
- 📝 Planned: 3 upgrades (Security Layer, Fine-Tuned Embeddings, API Connections)
- **Total**: 7 upgrades in pipeline

**Research Progress:**
- Security Layer: 0% (needs OAuth2/OIDC research)
- Fine-Tuned Embeddings: 30% (training script planning)
- API Connections: 20% (FrontApp spec complete)

**Readiness for Graduation:**
- Fine-Tuned Embeddings: ⏳ Needs Sentence Transformers research
- API Connections: ⏳ Needs OAuth flow design
- Security Layer: ⏳ Needs provider comparison (Auth0 vs Keycloak)

---

**Last Updated:** 2025-10-16
**Planned Upgrades:** 3 (2 high priority, 1 medium priority)
**Total Pipeline:** 3 planned + 1 active + 3 completed = 7 upgrades
**Next Graduation:** Fine-Tuned Embeddings (needs research phase)
