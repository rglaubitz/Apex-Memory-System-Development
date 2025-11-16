# Graphiti Integration - Deployment Guide

**Feature:** LLM-Powered Entity Extraction
**Status:** ✅ Production Ready (Implemented Nov 6, 2025)
**Impact:** Critical - Replaces 60% regex extraction with 90%+ LLM accuracy
**Deployment Week:** Week 2 (Dockerization & Configuration)

---

## Overview

Graphiti Integration provides LLM-powered entity extraction using Zep's Graphiti temporal knowledge graph library. This upgrade replaces regex-based entity extraction with AI-powered extraction, achieving 90%+ accuracy across all 46 entity types.

**What It Does:**
- Automatic entity extraction using GPT-5 or Claude
- Relationship inference between entities
- Bi-temporal knowledge graph tracking
- Hybrid search (semantic + BM25 + graph traversal)
- Point-in-time queries with temporal reasoning

**Why It's Important:**
- 50% accuracy improvement over regex patterns (60% → 90%+)
- Extracts all 46 entity types across 6 rigid hubs
- Domain-specific extraction context (logistics, personal, manufacturing)
- Automatic entity deduplication and relationship detection

**Dependencies:**
- Neo4j (already deployed in Phase 2)
- OpenAI API key OR Anthropic API key (for LLM extraction)
- Python package: `graphiti-core` (already in requirements.txt)

**References:**
- Implementation: `apex-memory-system/src/apex_memory/services/graphiti_service.py` (1,194 lines)
- Completion Docs: `upgrades/completed/graphiti-json-integration/COMPLETION-SUMMARY.md`
- Tests: `apex-memory-system/tests/unit/test_graphiti_extraction_activity.py`

---

## Prerequisites

### GCP Services
**None required** - Uses existing Neo4j database

### External Services
- **OpenAI API** (already configured) OR **Anthropic API** (already configured)
- Uses existing API keys for LLM-powered extraction

### Environment Variables
Already configured in `.env.example` (lines 129-135):
```bash
GRAPHITI_ENABLED=true
GRAPHITI_NEO4J_URI=${NEO4J_URI}
GRAPHITI_NEO4J_USER=${NEO4J_USER}
GRAPHITI_NEO4J_PASSWORD=${NEO4J_PASSWORD}
```

### Cost Estimate
**~$10-30/month** - LLM usage for entity extraction
- Uses OpenAI GPT-5 by default (`llm_model="gpt-5"`)
- Configurable to use Anthropic Claude or other providers
- Cost scales with document volume

---

## Setup Instructions

### Step 1: Verify Neo4j Deployment

Graphiti uses the existing Neo4j database deployed in Phase 2.

**Verification:**
```bash
# Check Neo4j is accessible
curl -u neo4j:apexmemory2024 http://localhost:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"RETURN 1"}]}'

# Should return: {"results":[{"columns":["1"],"data":[{"row":[1]}]}],...}
```

**If Neo4j is not accessible:** Refer to Phase 2 deployment steps in `deployment/production/GCP-DEPLOYMENT-GUIDE.md`

---

### Step 2: Verify API Keys

Graphiti requires an LLM API key for entity extraction.

**Check existing configuration:**
```bash
# Check OpenAI key is set
echo $OPENAI_API_KEY

# OR check Anthropic key is set
echo $ANTHROPIC_API_KEY
```

**If not set:** Add to Cloud Run environment variables in Step 4 below.

---

### Step 3: Enable Graphiti in Configuration

**Local Development (.env):**
```bash
# Add to apex-memory-system/.env
GRAPHITI_ENABLED=true
GRAPHITI_NEO4J_URI=bolt://localhost:7687
GRAPHITI_NEO4J_USER=neo4j
GRAPHITI_NEO4J_PASSWORD=apexmemory2024
```

**Production (Cloud Run environment variables):**
These will be set in Step 4.

---

### Step 4: Update Cloud Run Configuration

Add Graphiti environment variables to Cloud Run service.

**Command:**
```bash
# Set project and region
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Update Cloud Run service
gcloud run services update apex-api \
  --region=$REGION \
  --update-env-vars="GRAPHITI_ENABLED=true" \
  --update-env-vars="GRAPHITI_NEO4J_URI=bolt://NEO4J_INTERNAL_IP:7687" \
  --update-env-vars="GRAPHITI_NEO4J_USER=neo4j" \
  --set-secrets="GRAPHITI_NEO4J_PASSWORD=neo4j-password:latest"

# Note: NEO4J_INTERNAL_IP should be replaced with actual Neo4j internal IP
# Get Neo4j IP from Phase 2 deployment
```

**Verify deployment:**
```bash
gcloud run services describe apex-api --region=$REGION --format="value(status.url)"
# Visit URL/docs to verify API is running
```

---

### Step 5: Configure LLM Provider (Optional)

By default, Graphiti uses OpenAI GPT-5. To use a different provider:

**Option A: Use Anthropic Claude**
```bash
# Update Cloud Run service
gcloud run services update apex-api \
  --region=$REGION \
  --update-env-vars="GRAPHITI_LLM_PROVIDER=anthropic"

# Ensure ANTHROPIC_API_KEY is set (already configured in Phase 1)
```

**Option B: Use Custom Model**
Edit `apex-memory-system/src/apex_memory/services/graphiti_service.py`:
```python
# Line 89-91
llm_model: str = "gpt-5",  # Change to "claude-3-5-sonnet-20241022" for Claude
small_model: str = "gpt-5-mini",  # Or "claude-3-haiku-20240307" for Claude
```

**Redeploy after changes:**
```bash
# Rebuild and push Docker image
docker build -t gcr.io/$PROJECT_ID/apex-api:latest .
docker push gcr.io/$PROJECT_ID/apex-api:latest

# Deploy new image
gcloud run deploy apex-api \
  --image=gcr.io/$PROJECT_ID/apex-api:latest \
  --region=$REGION
```

---

### Step 6: Enable Unified Schemas Feature Flag

Graphiti Integration uses unified entity schemas. Enable the feature flag:

**Cloud Run Update:**
```bash
gcloud run services update apex-api \
  --region=$REGION \
  --update-env-vars="USE_UNIFIED_SCHEMAS=true"
```

**Verification:**
```bash
# Check environment variables
gcloud run services describe apex-api \
  --region=$REGION \
  --format="value(spec.template.spec.containers[0].env)"
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GRAPHITI_ENABLED` | Yes | `false` | Enable Graphiti integration |
| `GRAPHITI_NEO4J_URI` | Yes | `${NEO4J_URI}` | Neo4j connection URI |
| `GRAPHITI_NEO4J_USER` | Yes | `${NEO4J_USER}` | Neo4j username |
| `GRAPHITI_NEO4J_PASSWORD` | Yes | (secret) | Neo4j password (from Secret Manager) |
| `USE_UNIFIED_SCHEMAS` | Yes | `false` | Enable unified entity schemas |
| `GRAPHITI_LLM_PROVIDER` | No | `openai` | LLM provider (openai, anthropic) |

### Feature Flags

**Unified Schemas:** `USE_UNIFIED_SCHEMAS=true`
- Enables all 46 entity types across 6 rigid hubs
- Auto-configures Graphiti with three-tier property system
- Filters to `llm_extractable=True` fields only

---

## Deployment

### Production Deployment Checklist

- [ ] Neo4j deployed and accessible (Phase 2)
- [ ] OpenAI or Anthropic API key configured (Phase 1)
- [ ] Environment variables set on Cloud Run
- [ ] `GRAPHITI_ENABLED=true` set
- [ ] `USE_UNIFIED_SCHEMAS=true` set
- [ ] Cloud Run service redeployed with new configuration
- [ ] Verification tests passing (see below)

### Deployment Commands Summary

```bash
# 1. Verify Neo4j
curl -u neo4j:PASSWORD http://NEO4J_IP:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"RETURN 1"}]}'

# 2. Update Cloud Run environment
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="GRAPHITI_ENABLED=true,USE_UNIFIED_SCHEMAS=true,GRAPHITI_NEO4J_URI=bolt://NEO4J_IP:7687,GRAPHITI_NEO4J_USER=neo4j" \
  --set-secrets="GRAPHITI_NEO4J_PASSWORD=neo4j-password:latest"

# 3. Verify deployment
gcloud run services describe apex-api --region=us-central1
```

---

## Verification

### Test 1: Entity Extraction Endpoint

```bash
# Get Cloud Run URL
export API_URL=$(gcloud run services describe apex-api --region=us-central1 --format="value(status.url)")

# Test document ingestion with entity extraction
curl -X POST "$API_URL/api/v1/ingest/document" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "ACME Corporation placed a purchase order for 500 units from Bosch Automotive on January 15, 2025. The shipment will be delivered to the Dallas distribution center via FreightCo Logistics.",
    "source": "test",
    "metadata": {"test": "graphiti_extraction"}
  }'

# Expected: Success response with document_id
# Entities should be extracted: ACME Corporation, Bosch Automotive, FreightCo Logistics, Dallas, etc.
```

### Test 2: Verify Entities in Neo4j

```bash
# Connect to Neo4j
export NEO4J_IP=your-neo4j-ip
export NEO4J_PASSWORD=apexmemory2024

# Query extracted entities (via Cypher)
curl -u neo4j:$NEO4J_PASSWORD http://$NEO4J_IP:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [{
      "statement": "MATCH (n) WHERE n.name CONTAINS '\''ACME'\'' RETURN n LIMIT 5"
    }]
  }'

# Should return ACME Corporation entity with properties
```

### Test 3: Check Graphiti Service Initialization

```bash
# Check Cloud Run logs for Graphiti initialization
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=apex-api AND textPayload=~\"Graphiti\"" \
  --limit=10 \
  --format=json

# Look for: "GraphitiService initialized" or similar
```

### Test 4: Verify Extraction Accuracy

```bash
# Ingest test document with known entities
curl -X POST "$API_URL/api/v1/ingest/document" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "John Smith, CEO of TechCorp Inc., announced a strategic partnership with GlobalLogistics on March 20, 2025. The agreement includes a $5M investment in warehouse automation systems deployed across 12 facilities in California.",
    "source": "test_accuracy"
  }'

# Query for all entities
curl -u neo4j:$NEO4J_PASSWORD http://$NEO4J_IP:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [{
      "statement": "MATCH (n) WHERE n.source = '\''test_accuracy'\'' RETURN n.name, labels(n)"
    }]
  }'

# Expected entities:
# - John Smith (Person)
# - TechCorp Inc. (Organization)
# - GlobalLogistics (Organization)
# - California (Location)
# - March 20, 2025 (TemporalFact)
# - $5M (Monetary)
# - 12 facilities (Quantity)
```

### Test 5: Performance Check

```bash
# Check extraction latency (should be <5s for small documents)
time curl -X POST "$API_URL/api/v1/ingest/document" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document with minimal content.", "source": "perf_test"}'

# Acceptable: <5s total time
# If slower, check LLM API latency and network
```

---

## Troubleshooting

### Issue 1: Graphiti Initialization Fails

**Symptoms:**
- Cloud Run logs show: "Failed to initialize GraphitiService"
- Entity extraction returns errors

**Solution:**
```bash
# 1. Check Neo4j connectivity
gcloud compute ssh apex-worker-vm --command "
  curl -u neo4j:PASSWORD http://NEO4J_INTERNAL_IP:7474
"

# 2. Verify environment variables
gcloud run services describe apex-api --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | grep GRAPHITI

# 3. Check Secret Manager secret exists
gcloud secrets versions access latest --secret="neo4j-password"

# 4. Review Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=apex-api" \
  --limit=50 \
  --format=json | jq -r '.[] | .textPayload' | grep -i graphiti
```

### Issue 2: No Entities Extracted

**Symptoms:**
- Documents ingest successfully
- No entities appear in Neo4j

**Solution:**
```bash
# 1. Check feature flag
gcloud run services describe apex-api --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | grep USE_UNIFIED_SCHEMAS

# Should show: USE_UNIFIED_SCHEMAS=true

# 2. Verify LLM API key is set
gcloud run services describe apex-api --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | grep OPENAI_API_KEY

# 3. Check Graphiti activity logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"extract_entities_activity\"" \
  --limit=20

# 4. Test LLM directly
curl -X POST "$API_URL/api/v1/test/llm" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test LLM extraction"}'
```

### Issue 3: High LLM Costs

**Symptoms:**
- OpenAI or Anthropic bills higher than expected
- Multiple extractions per document

**Solution:**
```bash
# 1. Switch to cheaper model
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="GRAPHITI_LLM_MODEL=gpt-5-mini"  # Cheaper model

# 2. Enable caching (if available)
# Check if Graphiti has built-in caching for repeated extractions

# 3. Monitor usage
# OpenAI: https://platform.openai.com/usage
# Anthropic: https://console.anthropic.com/settings/usage

# 4. Set monthly budget alerts
# Configure in OpenAI/Anthropic console
```

### Issue 4: Extraction Accuracy Below 90%

**Symptoms:**
- Entities missed or incorrectly classified
- Wrong relationships inferred

**Solution:**
```bash
# 1. Enable domain configuration (if available)
# Edit apex-memory-system/src/apex_memory/config/domain_config.py
# Add domain-specific glossary and examples

# 2. Verify unified schemas are active
curl -X GET "$API_URL/api/v1/config" | jq '.graphiti'

# 3. Test with domain-specific examples
curl -X POST "$API_URL/api/v1/ingest/document" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your domain-specific test content",
    "domain": "logistics"  # or "personal", "manufacturing"
  }'

# 4. Review extraction logs for specific failures
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"GraphitiService\"" \
  --limit=100 | grep -i "error\|warning"
```

---

## Rollback

### Disable Graphiti Extraction

If issues arise, disable Graphiti and fall back to regex extraction:

```bash
# 1. Disable feature flag
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="GRAPHITI_ENABLED=false"

# 2. Verify rollback
curl -X POST "$API_URL/api/v1/ingest/document" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document", "source": "rollback_test"}'

# 3. Check logs for regex extraction (not Graphiti)
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"EntityExtractor\"" \
  --limit=10

# Should show regex-based extraction, not Graphiti
```

### Complete Rollback

```bash
# Remove all Graphiti environment variables
gcloud run services update apex-api \
  --region=us-central1 \
  --remove-env-vars="GRAPHITI_ENABLED,USE_UNIFIED_SCHEMAS,GRAPHITI_NEO4J_URI,GRAPHITI_NEO4J_USER" \
  --remove-secrets="GRAPHITI_NEO4J_PASSWORD"

# Verify
gcloud run services describe apex-api --region=us-central1
```

---

## Monitoring

### Key Metrics

**Extraction Accuracy:**
```cypher
// Query Neo4j for entity counts by source
MATCH (n)
WHERE n.created_at > datetime() - duration('P1D')
RETURN labels(n)[0] as entity_type, count(*) as count
ORDER BY count DESC
```

**Extraction Latency:**
```bash
# Check Cloud Run metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies" AND resource.label.service_name="apex-api"' \
  --format=json
```

**LLM API Usage:**
- OpenAI: https://platform.openai.com/usage
- Anthropic: https://console.anthropic.com/settings/usage

### Alerts

**Set up Cloud Monitoring alerts:**
```bash
# Alert on high extraction latency (>10s P95)
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="Graphiti Extraction Latency High" \
  --condition-display-name="Latency > 10s" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=60s

# Alert on extraction failures (error rate >5%)
# (Configure via Cloud Console Monitoring)
```

---

## Performance Optimization

### Reduce LLM Costs

1. **Use smaller model for simple documents:**
   ```python
   # In graphiti_service.py
   small_model: str = "gpt-5-mini"  # Already configured
   ```

2. **Batch extraction:** Process multiple documents in single LLM call (if supported by Graphiti)

3. **Cache results:** Enable Graphiti's built-in caching for repeated content

### Improve Accuracy

1. **Domain configuration:** Add business-specific terminology
2. **Few-shot examples:** Provide 3-5 examples per entity type
3. **Validation rules:** Add post-extraction validation (5-10 critical rules)

---

## Cost Breakdown

**Monthly Estimate: $10-30**

- **LLM API calls:** $8-25/month
  - Assumption: 500 documents/month, 2KB avg size
  - GPT-5: ~$0.015 per document = $7.50/month
  - Claude Sonnet: ~$0.05 per document = $25/month

- **Neo4j storage:** $0/month (uses existing database)

- **Cloud Run compute:** $0/month (negligible overhead)

**Cost optimization:** Use GPT-5 Mini for $0.002 per document = $1/month

---

## References

- **Implementation:** `apex-memory-system/src/apex_memory/services/graphiti_service.py`
- **Completion Summary:** `upgrades/completed/graphiti-json-integration/COMPLETION-SUMMARY.md`
- **Architecture:** `upgrades/completed/graphiti-json-integration/OPTION-D-PLUS-ARCHITECTURE.md`
- **Tests:** `apex-memory-system/tests/unit/test_graphiti_extraction_activity.py`
- **Graphiti Documentation:** https://docs.getzep.com/graphiti/

---

**Deployment Status:** ✅ Ready for Production
**Last Updated:** 2025-11-15
**Next Step:** Proceed to Structured Data Ingestion deployment
