# Grafana Cloud Pro Setup Guide

**Date:** 2025-11-15
**Time:** 30-40 minutes
**Cost:** $19/month (Pro tier - 10,000 metrics)

---

## Why Grafana Cloud?

Your Apex Memory System has **27 Temporal metrics** already instrumented and needs:
- **Prometheus storage** - Remote write endpoint for metrics
- **Grafana dashboards** - Visualization (33-panel Temporal Ingestion dashboard ready)
- **Alerting** - 12 critical alerts configured
- **Long-term retention** - 13 months metric retention (vs 15 days local)

**What's already built:**
- ✅ 27 Temporal metrics in `apex_memory/monitoring/metrics.py`
- ✅ 33-panel Grafana dashboard JSON (`monitoring/dashboards/temporal-ingestion.json`)
- ✅ 12 Prometheus alert rules (`monitoring/alerts/rules.yml`)

**You need Grafana Cloud to view and alert on these metrics in production.**

---

## Step 1: Create Account (10 minutes)

### 1.1 Sign Up

Go to: **https://grafana.com/auth/sign-up**

**Account Details:**
- Use your primary email (same as GCP/Temporal if possible)
- Choose "Grafana Cloud" (not self-hosted)
- Select "Pro" plan ($19/month)
- Verify email address

**Plan Comparison:**
- ❌ Free: 10k series limit, 14-day retention (not enough for production)
- ✅ **Pro: 10k series, 13-month retention** ← Choose this
- ❌ Advanced: 100k series, $299/month (overkill for start)

### 1.2 Create Stack

After signup, create your first stack:
- **Stack name:** `apex-memory-prod` (or `apex-memory-dev`)
- **Region:** `us-east-1` (closest to Temporal Cloud us-east4)
- **Plan:** Pro ($19/month)

This creates:
- Grafana instance: `https://apex-memory-prod.grafana.net`
- Prometheus instance: `https://prometheus-prod-xx-xxx.grafana.net`
- Loki instance: (logs, optional)

---

## Step 2: Setup Prometheus Remote Write (10 minutes)

### 2.1 Get Prometheus Credentials

In Grafana Cloud console:

1. Navigate to: **Connections → Add new connection**
2. Search for: "Prometheus"
3. Click: "Prometheus (metrics)"
4. Click: "Create a new API token"
   - Name: `apex-memory-metrics`
   - Role: `MetricsPublisher`
5. **Copy these three values:**

```bash
# Remote Write URL
GRAFANA_PROMETHEUS_URL=https://prometheus-prod-xx-xxx-xx.grafana.net/api/prom/push

# Instance ID (username)
GRAFANA_PROMETHEUS_USER=123456

# API Token (password)
GRAFANA_PROMETHEUS_TOKEN=glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ CRITICAL:** Copy the token immediately - you won't see it again!

### 2.2 Test Remote Write

```bash
# Test Prometheus remote write
curl -u "123456:glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -X POST \
  -H "Content-Type: application/x-protobuf" \
  -H "Content-Encoding: snappy" \
  --data-binary @/dev/null \
  https://prometheus-prod-xx-xxx-xx.grafana.net/api/prom/push

# Expected: Empty response (HTTP 200)
```

---

## Step 3: Configure Application Metrics (10 minutes)

### 3.1 Update .env File

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Add Grafana Cloud configuration
cat >> .env << 'EOF'

# =============================================================================
# Grafana Cloud Configuration
# =============================================================================
# Prometheus Remote Write
GRAFANA_PROMETHEUS_URL=https://prometheus-prod-xx-xxx-xx.grafana.net/api/prom/push
GRAFANA_PROMETHEUS_USER=123456
GRAFANA_PROMETHEUS_TOKEN=glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Grafana Instance
GRAFANA_URL=https://apex-memory-prod.grafana.net

# Metrics Configuration
METRICS_ENABLED=true
METRICS_PUSH_INTERVAL=15  # seconds (how often to push metrics)
EOF

echo "✅ Grafana Cloud configuration added to .env"
```

**Replace the placeholder values** with your actual credentials.

### 3.2 Verify Metrics Configuration

Your application already has metrics configured in:
- **Metrics definition:** `src/apex_memory/monitoring/metrics.py` (27 metrics)
- **Prometheus config:** `monitoring/prometheus/prometheus.yml`
- **Dashboard JSON:** `monitoring/dashboards/temporal-ingestion.json` (33 panels)
- **Alert rules:** `monitoring/alerts/rules.yml` (12 alerts)

**No code changes needed!** Just configure the remote write endpoint.

---

## Step 4: Import Dashboard (5 minutes)

### 4.1 Upload Temporal Ingestion Dashboard

In Grafana Cloud:

1. Navigate to: **Dashboards → Import**
2. Click: "Upload JSON file"
3. Select: `/Users/richardglaubitz/Projects/apex-memory-system/monitoring/dashboards/temporal-ingestion.json`
4. Click: "Import"

**Your 33-panel dashboard is now live!**

Dashboard includes:
- Workflow metrics (success rate, duration, P95)
- Activity metrics (5 activities instrumented)
- Data quality metrics (chunks, entities, embeddings)
- Infrastructure metrics (memory, CPU, database connections)
- Business metrics (documents processed, cost per document)
- Log stream (workflow events)

### 4.2 Verify Dashboard

Navigate to the imported dashboard:
- URL: `https://apex-memory-prod.grafana.net/d/temporal-ingestion`
- Should show: 33 panels (most empty until workflows run)

---

## Step 5: Configure Alerts (5 minutes)

### 5.1 Upload Alert Rules

Your alert rules are defined in: `monitoring/alerts/rules.yml` (12 alerts)

**In Grafana Cloud:**

1. Navigate to: **Alerting → Alert rules**
2. Click: "New alert rule"
3. Copy-paste each rule from `rules.yml`

**Critical alerts configured:**
- Silent failure detection (zero chunks/entities)
- High error rate (>5%)
- Slow performance (P95 >5s)
- Database connection issues
- Memory pressure (>80%)
- Workflow timeout (>30 min)

### 5.2 Configure Notification Channels

**Setup email alerts:**

1. Navigate to: **Alerting → Contact points**
2. Click: "New contact point"
3. Name: `email-alerts`
4. Type: `Email`
5. Addresses: Your email
6. Save

**Link to alert rules:**
1. Navigate to: **Alerting → Notification policies**
2. Edit default policy
3. Add contact point: `email-alerts`
4. Save

---

## Step 6: Add Payment Method (5 minutes)

### 6.1 Add Credit Card

1. Navigate to: **Billing**
2. Click: "Add payment method"
3. Add credit card
4. Set billing email

### 6.2 Set Budget Alerts (Optional)

**Prevent unexpected charges:**

1. Navigate to: **Billing → Usage**
2. Set alert thresholds:
   - Alert at: $15 (75% of $19/month)
   - Alert at: $18 (95% of $19/month)

**Grafana Cloud Pro is fixed $19/month** (not usage-based), but alerts help if you accidentally upgrade.

---

## Step 7: Store Credentials (5 minutes)

### 7.1 Password Manager Format

**Copy to your password manager (Bitwarden, 1Password, etc.):**

```yaml
Title: Grafana Cloud - Apex Memory
Type: Secure Note
Category: Monitoring

Stack Details:
  Stack Name: apex-memory-prod
  Region: us-east-1
  Plan: Pro ($19/month)

Grafana Instance:
  URL: https://apex-memory-prod.grafana.net
  Username: [your-email]
  Password: [your-password]

Prometheus Remote Write:
  URL: https://prometheus-prod-xx-xxx-xx.grafana.net/api/prom/push
  User (Instance ID): 123456
  Token: glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  Created: 2025-11-15

Dashboard:
  URL: https://apex-memory-prod.grafana.net/d/temporal-ingestion
  Panels: 33 (workflow, activity, data quality, infrastructure, business, logs)

Alerts:
  Total: 12 critical alerts
  Contact: email-alerts
  Email: [your-email]

Cost: $19/month (fixed)
Metrics Limit: 10,000 series
Retention: 13 months

Notes:
  - 27 Temporal metrics already instrumented
  - Dashboard JSON imported from monitoring/dashboards/
  - Alert rules from monitoring/alerts/rules.yml
  - Metrics push every 15 seconds via remote write
```

---

## ✅ Grafana Cloud Setup Complete!

### What You've Accomplished

- ✅ Grafana Cloud account created (Pro plan, $19/month)
- ✅ Stack created (`apex-memory-prod`)
- ✅ Prometheus remote write configured
- ✅ 33-panel dashboard imported
- ✅ 12 alert rules configured
- ✅ Email notifications setup
- ✅ Payment method added
- ✅ .env file updated
- ✅ Credentials stored in password manager

### Dashboards Ready

**Temporal Ingestion Dashboard** (33 panels):
- **Workflow layer:** Success rate, duration, errors, retries
- **Activity layer:** 5 activities (parse, extract, embed, write, stage)
- **Data quality:** Chunks, entities, embeddings generated
- **Infrastructure:** Memory, CPU, connections, queues
- **Business:** Documents/hour, cost per document, throughput
- **Logs:** Real-time workflow event stream

**Access:** https://apex-memory-prod.grafana.net/d/temporal-ingestion

---

## 🎯 Next Steps

**Update Prerequisites Tracker:**
- Mark "Grafana Cloud Pro" as complete in `PREREQUISITES-COMPLETION-TRACKER.md`

**Continue Prerequisites:**
- Next: Store all credentials in password manager (15-20 minutes)
- Then: Enable 2FA on all accounts (30-40 minutes)
- Then: Final verification and you're done!

---

## 🧪 Optional: Test Metrics Flow

**After starting your application:**

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
source venv/bin/activate

# Start API server (metrics will start flowing)
python -m uvicorn apex_memory.main:app --reload --port 8000

# In another terminal, trigger a workflow
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"content": "Test document for metrics", "source": "test"}'

# Wait 15-30 seconds, then check Grafana dashboard
# Should see metrics appearing in the 33 panels
```

---

## Troubleshooting

### "Invalid credentials" Error

**Problem:** Prometheus remote write returns 401

**Solutions:**
1. Verify instance ID (username) is correct
2. Check API token copied completely (starts with `glc_`)
3. Regenerate token in Grafana Cloud console

### Dashboard Shows "No Data"

**Problem:** Dashboard panels empty

**Solutions:**
1. Wait 15-30 seconds after starting application
2. Check metrics push interval (default: 15 seconds)
3. Verify Prometheus remote write URL is correct
4. Check application logs for metric push errors

### Alerts Not Firing

**Problem:** No alert notifications received

**Solutions:**
1. Verify contact point configured (Alerting → Contact points)
2. Check notification policy linked to contact point
3. Trigger test alert: Alerting → Alert rules → Test
4. Check email spam folder

---

**Setup Complete!** 🎉

You now have production-grade monitoring with Grafana Cloud Pro. All 27 Temporal metrics will flow to your dashboard and trigger alerts when needed.

**Next:** Store all credentials in password manager, then enable 2FA.
