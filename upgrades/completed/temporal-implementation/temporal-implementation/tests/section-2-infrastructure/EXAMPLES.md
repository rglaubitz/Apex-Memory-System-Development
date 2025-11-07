# Section 2: Infrastructure Examples

**Author:** Apex Infrastructure Team
**Created:** 2025-10-18
**Section:** 2 - Docker Compose Infrastructure

---

## Quick Start

### 1. Start Temporal Infrastructure

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
./scripts/temporal/start_temporal.sh
```

**Expected Output:**
```
======================================================================
Starting Temporal Infrastructure
======================================================================

✓ apex-network found

Starting Temporal services...
[+] Running 4/4
 ✔ Container temporal-postgres      Started
 ✔ Container temporal                Started
 ✔ Container temporal-ui             Started
 ✔ Container temporal-admin-tools    Started

======================================================================
Temporal Infrastructure Starting...
======================================================================

Services:
  - temporal-postgres (port 5433)
  - temporal (ports 7233, 8077)
  - temporal-ui (port 8088)
  - temporal-admin-tools

This will take ~30-60 seconds for all health checks to pass.
```

---

### 2. Check Health Status

Wait 30-60 seconds, then run:

```bash
./scripts/temporal/check_temporal_health.sh
```

**Expected Output (when healthy):**
```
======================================================================
Temporal Infrastructure Health Check
======================================================================

Checking containers...

✅ temporal-postgres - HEALTHY
✅ temporal - HEALTHY
✅ temporal-ui - HEALTHY
✅ temporal-admin-tools - RUNNING

Checking ports...

✅ PostgreSQL (port 5433) - ACCESSIBLE
✅ Temporal Server (gRPC) (port 7233) - ACCESSIBLE
✅ Temporal Metrics (Prometheus) (port 8077) - ACCESSIBLE
✅ Temporal UI (Web) (port 8088) - ACCESSIBLE

======================================================================
✅ All Temporal services are healthy!

Temporal UI: http://localhost:8088
Prometheus Metrics: http://localhost:8077/metrics

You can now proceed with Temporal workflow development.
======================================================================
```

---

### 3. Access Temporal UI

Open your browser:
```
http://localhost:8088
```

You should see the Temporal Web UI with:
- Workflows list (empty for now)
- Namespaces (default namespace visible)
- Search capabilities

---

### 4. Verify Prometheus Metrics

```bash
curl http://localhost:8077/metrics | head -20
```

**Expected Output:**
```
# HELP temporal_namespace_state Gauge of namespace state
# TYPE temporal_namespace_state gauge
temporal_namespace_state{namespace="default"} 1
...
```

---

### 5. Use Admin Tools (tctl)

```bash
docker exec -it temporal-admin-tools tctl namespace list
```

**Expected Output:**
```
Name: default
Id: 00000000-0000-0000-0000-000000000000
Status: Registered
```

---

### 6. Stop Temporal Infrastructure

```bash
./scripts/temporal/stop_temporal.sh
```

**Expected Output:**
```
======================================================================
Stopping Temporal Infrastructure
======================================================================

Stopping Temporal services...
[+] Running 4/4
 ✔ Container temporal-admin-tools    Removed
 ✔ Container temporal-ui             Removed
 ✔ Container temporal                Removed
 ✔ Container temporal-postgres       Removed

======================================================================
✅ Temporal Infrastructure Stopped
======================================================================
```

---

## Docker Compose Commands

### View Logs

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system/docker
docker-compose -f temporal-compose.yml logs -f
```

### View Specific Service Logs

```bash
docker-compose -f temporal-compose.yml logs -f temporal
docker-compose -f temporal-compose.yml logs -f temporal-ui
```

### Check Container Status

```bash
docker-compose -f temporal-compose.yml ps
```

### Restart Services

```bash
docker-compose -f temporal-compose.yml restart temporal
```

---

## Testing Infrastructure

### Run All Infrastructure Tests

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
python3 -m pytest /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/temporal-implementation/tests/section-2-infrastructure/test_temporal_docker.py -v
```

**Expected Output:**
```
test_temporal_compose_valid PASSED                    [ 10%]
test_temporal_postgres_starts PASSED                  [ 20%]
test_temporal_server_starts PASSED                    [ 30%]
test_temporal_ui_accessible PASSED                    [ 40%]
test_admin_tools_accessible PASSED                    [ 50%]
test_health_checks_pass PASSED                        [ 60%]
test_prometheus_metrics_available PASSED              [ 70%]
test_postgres_persistence PASSED                      [ 80%]
test_network_connectivity PASSED                      [ 90%]
test_dynamic_config_loaded PASSED                     [100%]

============================== 10 passed ==============================
```

### Run Individual Tests

```bash
# Test YAML validity
pytest test_temporal_docker.py::test_temporal_compose_valid -v

# Test health checks
pytest test_temporal_docker.py::test_health_checks_pass -v

# Test metrics
pytest test_temporal_docker.py::test_prometheus_metrics_available -v
```

---

## Troubleshooting

### Issue: Containers not starting

**Check logs:**
```bash
docker-compose -f docker/temporal-compose.yml logs
```

**Common causes:**
- Port conflicts (5433, 7233, 8077, 8088 already in use)
- apex-network doesn't exist (start Apex databases first)
- Docker daemon not running

---

### Issue: Health checks failing

**Wait longer:**
Health checks can take 30-60 seconds on first startup.

**Check individual service health:**
```bash
docker ps --filter "name=temporal" --format "table {{.Names}}\t{{.Status}}"
```

---

### Issue: Cannot access UI at localhost:8088

**Check if port is listening:**
```bash
lsof -i :8088
```

**Check temporal-ui logs:**
```bash
docker logs temporal-ui
```

---

### Issue: Metrics not available at localhost:8077

**Check temporal server logs:**
```bash
docker logs temporal
```

**Verify PROMETHEUS_ENDPOINT environment variable:**
```bash
docker exec temporal env | grep PROMETHEUS
```

---

## Next Steps

Once all services are healthy:

1. ✅ Proceed to **Section 3: Python SDK & Configuration**
2. Create `TemporalConfig` dataclass
3. Add `.env.temporal` for configuration
4. Test SDK connection to Temporal Server

---

**Files Created in Section 2:**
- `docker/temporal-compose.yml` - 4 services
- `docker/temporal-dynamicconfig/development.yaml` - Runtime config
- `scripts/temporal/start_temporal.sh` - Startup helper
- `scripts/temporal/stop_temporal.sh` - Shutdown helper
- `scripts/temporal/check_temporal_health.sh` - Health validator
- `tests/section-2-infrastructure/test_temporal_docker.py` - 10 tests

**Section 2 Complete! Ready for Section 3.**
