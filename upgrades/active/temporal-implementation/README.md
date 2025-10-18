# Temporal Workflow Orchestration - Upgrade Plan

**Status:** 🔬 Research Complete (Phase 1 RDF Done)
**Priority:** High
**Timeline:** 6-8 weeks
**Research Progress:** 100% ✅ (Phase 1 RDF complete - 2025-10-17)

## Overview

Implement Temporal.io workflow orchestration to replace saga-based orchestration with durable, scalable workflow management for ingestion and query processing.

## Current State

**Architecture:** Custom saga pattern with manual compensation
- Ingestion uses in-memory saga coordinator
- No workflow history or replay capabilities
- Limited failure recovery and retry logic
- Manual state management across services

**Limitations:**
- ❌ No visibility into workflow execution state
- ❌ Manual compensation logic for each operation
- ❌ No automatic retry with exponential backoff
- ❌ Limited distributed tracing
- ❌ Cannot pause/resume long-running workflows

## Target State

**Architecture:** Temporal.io workflow orchestration
- Durable workflows with automatic state management
- Built-in retry, timeout, and compensation
- Distributed tracing and observability
- Workflow versioning and migration

**Expected Improvements:**
- ✅ 99.9% workflow reliability (Temporal SLA)
- ✅ Automatic retries with exponential backoff
- ✅ Complete workflow visibility and debugging
- ✅ Pause/resume/cancel long-running operations
- ✅ Zero code compensation logic (built-in)

## Research Foundation

**✅ Phase 1 RDF Complete (2025-10-17)**

**📂 All Research Artifacts:** [research/README.md](research/README.md)

**Comprehensive Research Documentation:**
- [Temporal.io Overview](research/documentation/temporal-io-overview.md) - Core concepts, architecture, benefits
- [Python SDK Guide](research/documentation/python-sdk-guide.md) - Detailed SDK usage, patterns, best practices
- [Deployment Guide](research/documentation/deployment-guide.md) - Docker Compose, Kubernetes, production setup
- [Integration Patterns](research/documentation/integration-patterns.md) - Hybrid architecture with Enhanced Saga
- [Migration Strategy](research/documentation/migration-strategy.md) - Gradual rollout, versioning, rollback
- [Monitoring & Observability](research/documentation/monitoring-observability.md) - Prometheus, Grafana, OpenTelemetry

**Code Examples:**
- [Hello World Workflow](research/examples/hello-world-workflow.py) - Basic workflow example
- [Ingestion Workflow](research/examples/ingestion-workflow-example.py) - Production pattern with Enhanced Saga
- [Testing Examples](research/examples/testing-example.py) - Unit and integration tests

**Architecture Decision:**
- [ADR-003: Temporal Orchestration](research/architecture-decisions/ADR-003-temporal-orchestration.md) - Complete decision rationale

**Official Documentation:**
- [Temporal.io Python SDK](https://docs.temporal.io/develop/python) - Official Python SDK docs
- [Temporal Architecture](https://docs.temporal.io/concepts) - Core concepts and architecture
- [Temporal Best Practices](https://docs.temporal.io/production-deployment) - Production deployment guide

**Key Findings from ARCHITECTURE-ANALYSIS-2025.md:**

### Workflow Orchestration Benefits
- **Durable Execution:** Workflow state persisted to database (survives crashes)
- **Automatic Retries:** Exponential backoff with jitter (no custom retry logic)
- **Compensation:** Built-in saga pattern support (automatic rollback)
- **Observability:** Complete workflow history and replay for debugging

### Production-Ready Features
- **High Availability:** Multi-datacenter replication support
- **Horizontal Scaling:** Worker pools scale independently
- **Version Migration:** Gradual workflow version rollout
- **Testing:** Deterministic workflow testing with time travel

## Implementation Plan

### Phase 1: Infrastructure Setup (Week 1-2)

**1.1 Temporal Server Deployment**
```yaml
# docker-compose.yml addition
temporal:
  image: temporalio/auto-setup:1.22.0
  ports:
    - "7233:7233"  # gRPC
    - "8088:8088"  # UI
  environment:
    - DB=postgresql
    - DB_PORT=5432
    - POSTGRES_USER=apex
    - POSTGRES_PWD=apexmemory2024
    - POSTGRES_SEEDS=postgres
```

**1.2 Python SDK Installation**
```bash
pip install temporalio==1.5.0
```

**1.3 Worker Infrastructure**
```python
# src/apex_memory/temporal/worker.py
from temporalio.client import Client
from temporalio.worker import Worker

async def run_worker():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="apex-ingestion",
        workflows=[IngestionWorkflow],
        activities=[parse_document, extract_entities, write_databases]
    )
    await worker.run()
```

### Phase 2: Ingestion Workflow Migration (Week 3-4)

**2.1 Define Ingestion Workflow**
```python
# src/apex_memory/temporal/workflows/ingestion.py
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class IngestionWorkflow:
    @workflow.run
    async def run(self, document_uuid: str) -> dict:
        # Step 1: Parse document (with automatic retry)
        parsed = await workflow.execute_activity(
            parse_document,
            document_uuid,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3
            )
        )

        # Step 2: Extract entities (parallel execution)
        entities = await workflow.execute_activity(
            extract_entities,
            parsed,
            start_to_close_timeout=timedelta(minutes=3)
        )

        # Step 3: Write to databases (with compensation)
        try:
            results = await workflow.execute_activity(
                write_databases,
                entities,
                start_to_close_timeout=timedelta(minutes=10)
            )
            return results
        except Exception:
            # Automatic compensation (saga rollback)
            await workflow.execute_activity(
                rollback_writes,
                entities,
                start_to_close_timeout=timedelta(minutes=5)
            )
            raise
```

**2.2 Convert Activities**
```python
# src/apex_memory/temporal/activities/ingestion.py
from temporalio import activity

@activity.defn
async def parse_document(document_uuid: str) -> dict:
    """Parse document activity (idempotent)."""
    parser = DocumentParser()
    result = await parser.parse(document_uuid)
    return result

@activity.defn
async def write_databases(entities: dict) -> dict:
    """Write to all databases (with idempotency keys)."""
    orchestrator = DatabaseOrchestrator()
    return await orchestrator.write_parallel(entities)
```

**2.3 Gradual Rollout**
- Week 3: Feature flag for Temporal ingestion (10% traffic)
- Week 4: Increase to 50% traffic
- End of Phase 2: 100% traffic on Temporal

### Phase 3: Query Workflow Migration (Week 5-6)

**3.1 Query Processing Workflow**
```python
@workflow.defn
class QueryWorkflow:
    @workflow.run
    async def run(self, query_text: str) -> dict:
        # Step 1: Classify intent
        intent = await workflow.execute_activity(
            classify_intent,
            query_text,
            start_to_close_timeout=timedelta(seconds=10)
        )

        # Step 2: Route to databases (parallel)
        results = await asyncio.gather(
            workflow.execute_activity(route_neo4j, query_text, intent),
            workflow.execute_activity(route_postgres, query_text, intent),
            workflow.execute_activity(route_qdrant, query_text, intent),
        )

        # Step 3: Aggregate and cache
        final = await workflow.execute_activity(
            aggregate_results,
            results,
            start_to_close_timeout=timedelta(seconds=5)
        )

        return final
```

**3.2 Long-Running Query Support**
```python
@workflow.defn
class ComplexQueryWorkflow:
    @workflow.run
    async def run(self, query_text: str) -> dict:
        # Support for queries >30s with cancellation
        with workflow.cancellation_scope() as cancel_scope:
            # User can cancel via Temporal UI
            results = await workflow.execute_activity(
                run_complex_analysis,
                query_text,
                start_to_close_timeout=timedelta(minutes=10),
                heartbeat_timeout=timedelta(seconds=30)
            )
        return results
```

### Phase 4: Monitoring & Observability (Week 7-8)

**4.1 Temporal UI Integration**
- Workflow execution history
- Real-time progress tracking
- Retry visualization
- Error debugging

**4.2 Metrics Export**
```python
# Export Temporal metrics to Prometheus
from temporalio.runtime import PrometheusConfig

runtime = Runtime(
    telemetry=TelemetryConfig(
        metrics=PrometheusConfig(bind_address="0.0.0.0:9090")
    )
)
```

**4.3 Distributed Tracing**
```python
# OpenTelemetry integration
from temporalio.contrib.opentelemetry import TracingInterceptor

interceptors = [TracingInterceptor()]
client = await Client.connect(
    "localhost:7233",
    interceptors=interceptors
)
```

## Success Criteria

### Performance Metrics
- ✅ Workflow reliability: ≥99.9%
- ✅ Average workflow duration: <5s (same as current)
- ✅ Worker CPU usage: <50%
- ✅ Workflow history retention: 30 days

### Operational Metrics
- ✅ Zero manual compensation code
- ✅ 100% workflow visibility in UI
- ✅ Automatic retry success rate: >95%
- ✅ Time to debug workflow failure: <5 minutes

### Migration Criteria
- ✅ All ingestion workflows on Temporal
- ✅ All query workflows on Temporal
- ✅ Legacy saga code removed
- ✅ Team trained on Temporal debugging

## Dependencies

**Infrastructure:**
- Temporal Server (1.22.0+)
- PostgreSQL (for Temporal persistence)
- Python 3.11+ with temporalio SDK

**Code Changes:**
- Refactor ingestion orchestrator → workflow + activities
- Refactor query router → workflow + activities
- Add feature flags for gradual rollout
- Update monitoring dashboards

## Risks & Mitigation

**Risk 1: Learning Curve**
- Mitigation: Start with simple workflows, iterate
- Training: Official Temporal tutorials + documentation

**Risk 2: Infrastructure Overhead**
- Mitigation: Use managed Temporal Cloud (optional)
- Fallback: Self-hosted with HA setup

**Risk 3: Migration Complexity**
- Mitigation: Gradual rollout with feature flags
- Rollback: Keep legacy saga code for 4 weeks

## Next Steps

**✅ Research Complete** → **✅ Execution Plan Ready** → Ready for Implementation

### 🚀 Start Here: Execution Roadmap

**📋 Follow the 17-section execution plan:** [EXECUTION-ROADMAP.md](EXECUTION-ROADMAP.md)

The implementation is broken into **17 numbered sections** aligned with the `/execute` command pattern:

**Section 1-6 (Phase 1): Infrastructure Setup** (Week 1-2)
- Section 1: Pre-Flight & Setup
- Section 2: Docker Compose Infrastructure
- Section 3: Python SDK & Configuration
- Section 4: Worker Infrastructure
- Section 5: Hello World Validation
- Section 6: Monitoring & Testing

**Section 7-10 (Phase 2): Ingestion Migration** (Week 3-4)
- Section 7: Ingestion Activities
- Section 8: Ingestion Workflow
- Section 9: Gradual Rollout
- Section 10: Ingestion Testing & Rollout

**Section 11-13 (Phase 3): Multi-Source Integration** (Week 5-6)
- Section 11: Webhook Workflows
- Section 12: Polling Workflows
- Section 13: Streaming & Batch Workflows

**Section 14-17 (Phase 4): Monitoring & Observability** (Week 7-8)
- Section 14: Temporal UI & Search
- Section 15: Prometheus & Grafana
- Section 16: OpenTelemetry & Documentation
- Section 17: Testing Strategy & Rollback

### Quick Start

1. **Review Research:** [research/README.md](research/README.md) - All research artifacts
2. **Study Decision:** [ADR-003](research/architecture-decisions/ADR-003-temporal-orchestration.md) - Decision rationale
3. **Read Implementation Guide:** [IMPLEMENTATION-GUIDE.md](IMPLEMENTATION-GUIDE.md) - Complete step-by-step guide
4. **Start Section 1:** Use `/execute` command to begin first section

### Additional Resources

- **Detailed Implementation:** [IMPLEMENTATION-GUIDE.md](IMPLEMENTATION-GUIDE.md) - Complete 3,110-line guide
- **Phase 1 Checklist:** [PHASE-1-CHECKLIST.md](PHASE-1-CHECKLIST.md) - Day-by-day Phase 1 tasks

## Cross-References

**Related Documentation:**
- [ARCHITECTURE-ANALYSIS-2025.md](../../ARCHITECTURE-ANALYSIS-2025.md) - Architecture research findings
- [Query Router README](../../query-router/README.md) - Query orchestration patterns
- [Completed Upgrades](../../completed/README.md) - Migration examples

**Research Links:**
- [Temporal Python Samples](https://github.com/temporalio/samples-python)
- [Temporal Best Practices](https://docs.temporal.io/production-deployment/best-practices)
- [Saga Pattern in Temporal](https://docs.temporal.io/workflows#saga-pattern)

---

**Last Updated:** 2025-10-10
**Owner:** Infrastructure Team
**Status:** Planning Complete → Ready for POC
