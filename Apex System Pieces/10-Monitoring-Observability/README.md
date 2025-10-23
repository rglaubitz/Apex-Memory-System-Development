# 10 - Monitoring & Observability

## 🎯 Purpose

Provides complete system visibility through Prometheus metrics, Grafana dashboards, and health checks. Enables proactive issue detection and performance optimization.

## 🛠 Technical Stack

- **Prometheus 2.x:** Metrics collection and storage
- **Grafana Latest:** Visualization dashboards
- **prometheus_client (Python):** Metrics instrumentation
- **Custom Metrics:** 40+ application-specific metrics

## 📂 Key Files

### Metrics Instrumentation
**apex-memory-system/src/apex_memory/monitoring/metrics.py** (~500 lines)

**Metric Categories (40+ total):**

1. **Query Metrics (10 metrics)**
   - `apex_queries_total` - Counter by query_type, status
   - `apex_query_duration_seconds` - Histogram
   - `apex_query_errors_total` - Counter
   - `apex_query_result_size` - Histogram

2. **Cache Metrics (5 metrics)**
   - `apex_cache_operations_total` - Counter (hit/miss/error)
   - `apex_cache_hit_rate` - Gauge (0.0-1.0)
   - `apex_cache_size_bytes` - Gauge
   - `apex_cache_evictions_total` - Counter

3. **Database Metrics (8 metrics)**
   - `apex_db_connections_active` - Gauge by database
   - `apex_db_query_duration_seconds` - Histogram
   - `apex_db_errors_total` - Counter
   - `apex_db_connection_pool_usage` - Gauge

4. **Ingestion Metrics (7 metrics)**
   - `apex_documents_ingested_total` - Counter
   - `apex_ingestion_duration_seconds` - Histogram
   - `apex_chunks_created_total` - Counter
   - `apex_entities_extracted_total` - Counter

5. **Temporal Metrics (10 metrics)**
   - `apex_temporal_workflow_executions_total` - Counter
   - `apex_temporal_workflow_duration_seconds` - Histogram
   - `apex_temporal_activity_executions_total` - Counter
   - `apex_temporal_activity_duration_seconds` - Histogram

### Dashboards
**apex-memory-system/monitoring/dashboards/**

1. **temporal-ingestion.json** (33 panels)
   - Workflow execution rates
   - Activity latencies
   - Error rates by type
   - Data quality metrics

2. **query-performance.json** (16 panels)
   - Query latency P50/P90/P99
   - Cache hit rates
   - Database utilization
   - Intent classification accuracy

### Alerts
**apex-memory-system/monitoring/alerts/rules.yml**

**12 Alert Rules:**
1. High error rate (>5%)
2. Cache hit rate drop (<70%)
3. Query latency P99 >2s
4. Database connection exhaustion (>90%)
5. Workflow failure rate (>10%)
6. Worker offline
7. Disk space low (<10GB)
8. Memory usage high (>80%)
9. Silent failure detection (zero chunks/entities)

### Infrastructure
**apex-memory-system/docker/docker-compose.yml**

```yaml
prometheus:
  image: prom/prometheus:latest
  ports: ["9090:9090"]
  volumes:
    - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    - ../monitoring/alerts:/etc/prometheus/alerts

grafana:
  image: grafana/grafana:latest
  ports: ["3001:3000"]
  volumes:
    - ../monitoring/dashboards:/etc/grafana/provisioning/dashboards
    - ../monitoring/grafana-provisioning/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
```

## Access Points

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001 (admin/apexmemory2024)
- **API Metrics:** http://localhost:8000/metrics
- **Worker Metrics:** http://localhost:9091/metrics

## Example Metrics

```python
# From apex_memory/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Track query execution
queries_total.labels(query_type="semantic", status="success").inc()
query_duration_seconds.labels(query_type="semantic", database="qdrant").observe(0.85)

# Track cache operations
cache_operations_total.labels(operation="get", status="hit").inc()
cache_hit_rate.set(0.95)

# Track database health
db_connections_active.labels(database="neo4j").set(12)
db_connection_pool_usage.labels(database="postgres").set(0.60)
```

---

**Previous Component:** [09-Cache-Layer](../09-Cache-Layer/README.md)
**Next Component:** [11-Configuration-Management](../11-Configuration-Management/README.md)
