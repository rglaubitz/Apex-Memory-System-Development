# Google Drive Integration - Production Deployment Checklist

**Component:** Google Drive Integration
**Version:** 1.0
**Date:** November 7, 2025

---

## Pre-Deployment Checklist (14 items)

Complete all items before deploying to production:

### Google Cloud Setup (4 items)

- [ ] **1. Service Account Created**
  - Navigate to Google Cloud Console
  - Create service account: `apex-google-drive-monitor`
  - Grant appropriate permissions
  - **Verification:** Service account visible in IAM & Admin → Service Accounts

- [ ] **2. Service Account Key Downloaded**
  - Generate JSON key for service account
  - Download and save as `google-drive-service-account.json`
  - Add to `.env` as `GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY` (single-line JSON)
  - **Verification:** Key file downloaded, `.env` variable set

- [ ] **3. Drive Folder Shared**
  - Share target Google Drive folder with service account email
  - Permission level: `Viewer` (read-only) or `Editor` (archive capability)
  - Note folder ID from URL
  - **Verification:** Service account has access, folder ID recorded

- [ ] **4. API Enabled**
  - Enable Google Drive API in Google Cloud Console
  - Navigate to APIs & Services → Library
  - Search "Google Drive API" → Enable
  - **Verification:** API appears in Enabled APIs list

### Database Setup (2 items)

- [ ] **5. PostgreSQL Tables Created**
  - Create `google_drive_processed_files` table
  - Create `google_drive_dead_letter_queue` table
  - Tables created automatically on first run (idempotent)
  - **Verification:** Run `\dt` in psql, both tables exist

- [ ] **6. Database Indexes Verified**
  - Verify 3 indexes on `google_drive_processed_files`
  - Verify 3 indexes on `google_drive_dead_letter_queue`
  - **Verification:** Run `\di` in psql, 6 total indexes exist
  - **SQL Command:**
    ```sql
    SELECT tablename, indexname FROM pg_indexes
    WHERE tablename IN ('google_drive_processed_files', 'google_drive_dead_letter_queue');
    ```

### Temporal Configuration (2 items)

- [ ] **7. Temporal Schedule Created**
  - Create schedule for `GoogleDriveMonitorWorkflow`
  - Interval: Every 15 minutes
  - Schedule ID: `monitor-google-drive-schedule`
  - **Verification:** Run `temporal schedule list`, schedule appears
  - **Command:**
    ```bash
    python scripts/temporal/create_monitor_schedule.py
    ```

- [ ] **8. Task Queue Configured**
  - Worker configured with `apex-ingestion-queue` task queue
  - Schedule targets same task queue
  - **Verification:** Check worker logs for "task_queue=apex-ingestion-queue"

### Worker Deployment (2 items)

- [ ] **9. Worker Running**
  - Deploy worker using systemd, Docker, or Kubernetes
  - Worker includes all Google Drive workflows/activities
  - **Verification:** Worker process running, no errors in logs
  - **Commands:**
    - Systemd: `sudo systemctl status apex-temporal-worker`
    - Docker: `docker ps | grep apex-temporal-worker`
    - Kubernetes: `kubectl get pods -n apex-memory`

- [ ] **10. Worker Health Verified**
  - Worker connects to Temporal successfully
  - All workflows and activities registered
  - **Verification:** Check Temporal UI → Workers → Verify worker appears
  - **Temporal UI:** http://localhost:8233

### Monitoring & Alerting (3 items)

- [ ] **11. Prometheus Scraping Configured**
  - Prometheus scraping `/metrics` endpoint (port 8000)
  - Scrape interval: 15 seconds
  - **Verification:** Check Prometheus targets page (Status → Targets)
  - **Prometheus URL:** http://localhost:9090/targets

- [ ] **12. Alert Rules Loaded**
  - Copy `monitoring/alerts/google_drive_monitoring_rules.yml` to Prometheus
  - Reload Prometheus configuration
  - **Verification:** 12 Google Drive alerts appear in Prometheus
  - **Command:**
    ```bash
    curl http://localhost:9090/api/v1/rules | grep google_drive
    ```

- [ ] **13. Grafana Dashboard Created** (Optional)
  - Import Temporal ingestion dashboard
  - Includes Google Drive metrics panels
  - **Verification:** Dashboard visible in Grafana UI
  - **Grafana URL:** http://localhost:3001

### Verification (1 item)

- [ ] **14. End-to-End Test Passed**
  - Place test PDF file in monitored Google Drive folder
  - Wait for next scheduled run (up to 15 minutes) OR trigger manually
  - Verify file processed: Check `google_drive_processed_files` table
  - Verify ingestion: Check Temporal UI for `DocumentIngestionWorkflow`
  - Verify metrics: Check Prometheus for `google_drive_files_processed_total`
  - **SQL Command:**
    ```sql
    SELECT * FROM google_drive_processed_files ORDER BY processed_at DESC LIMIT 1;
    ```
  - **Temporal Command:**
    ```bash
    temporal schedule trigger --schedule-id monitor-google-drive-schedule
    ```

---

## Post-Deployment Monitoring (First 24 Hours)

After deployment, monitor these endpoints:

1. **Grafana Dashboard** - http://localhost:3001/d/temporal-ingestion
   - Check Google Drive metrics panels
   - Verify files_detected and files_processed increasing

2. **Prometheus Alerts** - http://localhost:9090/alerts
   - Ensure no critical alerts firing
   - Check for warning alerts (expected during ramp-up)

3. **Temporal UI** - http://localhost:8233
   - Monitor `GoogleDriveMonitorWorkflow` executions
   - Check for failed workflows (should be 0)

4. **Dead Letter Queue** - SQL query
   ```sql
   SELECT COUNT(*) FROM google_drive_dead_letter_queue WHERE reprocessed = FALSE;
   ```
   - Expected: 0 permanently failed files

5. **Worker Logs**
   - Systemd: `sudo journalctl -u apex-temporal-worker -f`
   - Docker: `docker logs -f apex-temporal-worker`
   - Kubernetes: `kubectl logs -f -n apex-memory deployment/apex-temporal-worker`

---

## Critical Metrics to Watch

### Success Metrics (First 24 hours)

| Metric | Expected Value | Action if Outside Range |
|--------|----------------|------------------------|
| `google_drive_monitor_polls_total` | Increasing every 15 min | Check worker and schedule |
| `google_drive_files_processed_total` | ≥ 0 (depends on files) | N/A - depends on folder activity |
| `google_drive_files_failed_total` | 0-5% of processed | Check DLQ and troubleshooting runbook |
| `google_drive_poll_duration_seconds` | < 5 seconds | Check Google Drive API rate limits |
| Dead Letter Queue size | 0 | Investigate permanent failures |

### Alert Thresholds

| Alert | Severity | Threshold | Action |
|-------|----------|-----------|--------|
| WorkflowDown | Critical | No polls for 30 minutes | Check worker, restart if needed |
| WorkflowFailing | Critical | 100% failure rate for 10 min | Check logs, investigate errors |
| HighFailureRate | Critical | >50% failure rate for 15 min | Check Google Drive permissions, API limits |
| ModerateFailureRate | Warning | >20% failure rate for 15 min | Monitor, may indicate transient issues |
| DLQGrowing | Warning | >10 files in DLQ | Review DLQ, reprocess if possible |

---

## Rollback Procedures

If issues occur, follow these rollback steps:

### 1. Pause Monitoring (Immediate)

```bash
# Pause schedule to stop new workflow runs
temporal schedule toggle --schedule-id monitor-google-drive-schedule --pause

# Verify paused
temporal schedule describe --schedule-id monitor-google-drive-schedule
```

### 2. Stop Worker (If Needed)

```bash
# Systemd
sudo systemctl stop apex-temporal-worker

# Docker
docker stop apex-temporal-worker

# Kubernetes
kubectl scale deployment apex-temporal-worker --replicas=0 -n apex-memory
```

### 3. Investigate Issues

- Check worker logs for errors
- Check Temporal UI for failed workflows
- Query Dead Letter Queue for permanently failed files
- Review `TROUBLESHOOTING-RUNBOOK.md` for common issues

### 4. Resume or Rollback

**Resume (if issue resolved):**
```bash
# Unpause schedule
temporal schedule toggle --schedule-id monitor-google-drive-schedule --unpause

# Restart worker (if stopped)
sudo systemctl start apex-temporal-worker  # Systemd
docker start apex-temporal-worker          # Docker
kubectl scale deployment apex-temporal-worker --replicas=2 -n apex-memory  # Kubernetes
```

**Rollback (if cannot resolve):**
```bash
# Delete schedule
temporal schedule delete --schedule-id monitor-google-drive-schedule

# Stop and disable worker
sudo systemctl stop apex-temporal-worker
sudo systemctl disable apex-temporal-worker
```

---

## Sign-Off

**Deployment Checklist Status:**

- [ ] All 14 pre-deployment items completed
- [ ] End-to-end test passed
- [ ] Monitoring configured and verified
- [ ] Team trained on troubleshooting runbook
- [ ] Rollback procedures tested

**Approved By:**

- [ ] **Tech Lead:** _________________ Date: _________
- [ ] **DevOps:** _________________ Date: _________
- [ ] **SRE/Operations:** _________________ Date: _________

**Deployment Date:** _________
**Deployed By:** _________

---

## Reference Documentation

- **Deployment Guide:** `deployment/components/google-drive-integration/DEPLOYMENT-GUIDE.md`
- **Troubleshooting Runbook:** `upgrades/active/temporal-implementation/google-drive-integration/TROUBLESHOOTING-RUNBOOK.md`
- **Architecture Diagrams:** `upgrades/active/temporal-implementation/google-drive-integration/ARCHITECTURE-DIAGRAMS.md`
- **Test Validation Report:** `upgrades/active/temporal-implementation/google-drive-integration/WEEK4-DAY3-COMPLETE.md`

---

**Checklist Version:** 1.0
**Last Updated:** November 7, 2025
**Component:** Google Drive Integration
