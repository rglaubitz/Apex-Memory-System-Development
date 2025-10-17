# ADR-003: Temporal.io Workflow Orchestration

**Status:** Accepted  
**Date:** 2025-10-17  
**Deciders:** Apex Architecture Team  
**Context:** Phase 1 RDF - Temporal Implementation

## Context

Apex Memory System currently handles single-document ingestion well via the Enhanced Saga pattern (121/121 tests passing, 88-96% coverage). However, we need to integrate 9+ external data sources with different ingestion patterns:

**Data Sources:**
- P0 (Critical): FrontApp (webhook, 1,000/day), Turvo (webhook, 500/day), LLMs (API)
- P1 (High): Samsara (stream, 1,000/min), Banks/Plaid (poll, 200/day)
- P2 (Standard): Sonar (webhook, 300/day), Carrier EDI (batch, 50/day), CRM (poll, 100/day), Financial (poll, 50/day)

**Current Challenges:**
1. No unified orchestration layer for multi-source ingestion
2. Manual retry/error handling for each source
3. Limited visibility into long-running processes
4. Difficulty coordinating compensation across sources
5. State management for polling/streaming workflows

## Decision Drivers

1. **Durable Execution:** Workflows must survive crashes, restarts, infrastructure failures
2. **Observability:** Complete visibility into workflow state and history
3. **Simplified Development:** Reduce boilerplate for retries, state, error handling
4. **Production-Proven:** Battle-tested at scale (Uber, Netflix, Stripe)
5. **Preserve Investments:** Keep Enhanced Saga for database writes (121/121 tests)

## Options Considered

### Option 1: Custom Orchestration (Status Quo + Extensions)

**Pros:**
- Full control over implementation
- No new dependencies
- Use existing infrastructure

**Cons:**
- High development cost (3,000+ lines estimated)
- Complex state management across 9 sources
- Limited visibility (logs/metrics only)
- Difficult to debug long-running workflows
- Manual versioning/migration

**Research Support:** N/A (custom solution)

### Option 2: Apache Airflow

**Pros:**
- Proven for data pipelines
- Python-native DAG definitions
- Built-in scheduler

**Cons:**
- DAG-centric (not code-centric workflows)
- Limited durable execution (external state needed)
- Complex local development setup
- No automatic retry/versioning
- Heavy infrastructure (scheduler, executor, database)

**Research Support:**
- Tier 1: https://airflow.apache.org/docs/
- Used for batch ETL, not real-time orchestration

### Option 3: Celery

**Pros:**
- Python-native task queue
- Simple task definitions
- Wide adoption

**Cons:**
- No durable state (tasks don't survive crashes)
- No workflow visibility (log-based debugging only)
- Manual state management required
- No compensation/saga pattern support
- Limited observability

**Research Support:**
- Tier 1: https://docs.celeryq.dev/
- Good for fire-and-forget tasks, not workflows

### Option 4: AWS Step Functions

**Pros:**
- Fully managed (no infrastructure)
- Durable execution
- Built-in retry/error handling

**Cons:**
- Vendor lock-in (AWS only)
- JSON/ASL instead of Python code
- No local development (cloud-only)
- Limited debugging capabilities
- Expensive at scale

**Research Support:**
- Tier 1: https://docs.aws.amazon.com/step-functions/
- Good for AWS-native stacks, not polycloud

### Option 5: Temporal.io (SELECTED)

**Pros:**
- Durable execution (automatic state persistence)
- Code-as-workflows (native Python)
- Complete observability (Temporal UI)
- Automatic retry/versioning
- Production-proven (Uber, Netflix, Stripe)
- Self-hosted or cloud
- Local development friendly

**Cons:**
- New dependency (Temporal Server)
- Learning curve for team
- ~80ms latency overhead per workflow

**Research Support:**
- **Tier 1 (Official Documentation):**
  - Temporal Docs: https://docs.temporal.io
  - Python SDK: https://docs.temporal.io/develop/python
  - Worker Versioning: https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning

- **Tier 2 (Verified Examples):**
  - Temporal Python Samples: https://github.com/temporalio/samples-python
  - Production Case Studies: Uber (100,000+ workflows/sec), Netflix (scheduling), Stripe (payments)

- **Tier 3 (Technical Standards):**
  - Saga Pattern: Microsoft Azure Architecture Guide
  - Workflow Orchestration Patterns: Enterprise Integration Patterns

## Decision

**We will adopt Temporal.io for workflow orchestration while preserving Enhanced Saga for database writes.**

### Hybrid Architecture

```
Temporal.io → Orchestration (9+ sources, retries, state, observability)
   ↓
Enhanced Saga → Database Writes (4 DBs atomically, circuit breakers, DLQ)
```

**Rationale:**
1. **Clear Separation:** Temporal = "what/when", Enhanced Saga = "how" (multi-DB consistency)
2. **Leverage Strengths:** Temporal for workflows, Saga for data integrity
3. **Preserve Investments:** 121/121 Saga tests remain, no rewrite needed
4. **70% Code Reduction:** 3,000 → 1,000 lines (Temporal handles retries, state, error handling)
5. **Production-Ready:** Temporal's observability + Saga's battle-tested writes

## Consequences

### Positive

1. **Complete Workflow Visibility:** Temporal UI shows ALL workflows in real-time
2. **Automatic Reliability:** Retries, state persistence, compensation built-in
3. **Simplified Development:** Developers write business logic, not infrastructure
4. **Safe Deployments:** Worker versioning enables gradual rollout (10% → 50% → 100%)
5. **Local Development:** Temporal CLI (`temporal server start-dev`) = 1 command
6. **Proven at Scale:** Uber, Netflix, Stripe production deployments

### Negative

1. **New Dependency:** Temporal Server (PostgreSQL for persistence)
2. **Latency Overhead:** ~80ms per workflow (mitigated: use local activities for fast ops)
3. **Learning Curve:** Team must learn Temporal concepts (1-2 weeks)
4. **Infrastructure Complexity:** Docker Compose for local, Kubernetes for production

### Mitigation Strategies

1. **Gradual Adoption:**
   - Week 1-2: Parallel execution (both paths)
   - Week 3-4: 10% → 50% traffic
   - Week 5-6: 100% migration

2. **Rollback Plan:**
   - Keep legacy code for 2 weeks post-migration
   - Feature flags for instant traffic switch
   - Enhanced Saga remains unchanged (fallback path)

3. **Team Training:**
   - Temporal 101 course (free, 2 hours)
   - Code examples in `research/examples/temporal/`
   - Pair programming for first workflows

4. **Performance Optimization:**
   - Use local activities for <10ms operations
   - Batch operations where possible
   - Direct Saga calls for <100ms latency requirements

## Implementation Plan

### Phase 1: Infrastructure Setup (Week 1-2)
- Deploy Temporal Server (Docker Compose)
- Install temporalio Python SDK (1.11.0+)
- Create worker infrastructure
- "Hello World" workflow validation

### Phase 2: Ingestion Migration (Week 3-4)
- Convert ingestion pipeline to Temporal workflow
- Delegate database writes to Enhanced Saga (unchanged)
- Gradual rollout: 10% → 50% → 100%

### Phase 3: Multi-Source Integration (Week 5-6)
- Implement 9 source workflows (webhook, poll, stream, batch patterns)
- Priority-based execution (P0 → P1 → P2)

### Phase 4: Monitoring (Week 7-8)
- Temporal UI integration
- Prometheus metrics export
- OpenTelemetry tracing
- Grafana dashboards

**Total Timeline:** 6-8 weeks

## Related Documentation

- [Temporal.io Overview](../documentation/temporal/temporal-io-overview.md)
- [Python SDK Guide](../documentation/temporal/python-sdk-guide.md)
- [Integration Patterns](../documentation/temporal/integration-patterns.md)
- [Migration Strategy](../documentation/temporal/migration-strategy.md)
- [Deployment Guide](../documentation/temporal/deployment-guide.md)

## References

1. Temporal Documentation: https://docs.temporal.io
2. Temporal Python SDK: https://docs.temporal.io/develop/python
3. Worker Versioning: https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning
4. Temporal Samples: https://github.com/temporalio/samples-python
5. Microsoft Saga Pattern: https://docs.microsoft.com/azure/architecture/reference-architectures/saga
6. Enhanced Saga Implementation: `upgrades/completed/saga-pattern-enhancement/README.md`
