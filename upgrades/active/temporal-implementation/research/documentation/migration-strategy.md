# Temporal Migration Strategy

**Last Updated:** 2025-10-17  
**Timeline:** 4-6 weeks  
**Risk Level:** Medium (gradual rollout mitigates)

## Migration Approach: Blue-Green with Gradual Rollout

### Phase 1: Parallel Execution (Week 1-2) - Validation

**Goal:** Validate Temporal + Saga integration without production impact

**Implementation:**
```python
# Execute both paths, compare results
@workflow.defn
class ValidationWorkflow:
    @workflow.run
    async def run(self, doc_id: str):
        temporal_result, legacy_result = await asyncio.gather(
            execute_temporal_path(doc_id),
            execute_legacy_path(doc_id),
            return_exceptions=True
        )
        
        # Log discrepancies
        if temporal_result != legacy_result:
            log_mismatch(doc_id, temporal_result, legacy_result)
        
        return legacy_result  # Use legacy (safe)
```

**Success Criteria:**
- [ ] <1% result discrepancies
- [ ] Temporal latency < 2× legacy latency
- [ ] Zero data loss
- [ ] All 121 Saga tests still passing

### Phase 2: 10% Traffic (Week 3) - Limited Rollout

**Feature Flag:**
```python
TEMPORAL_ROLLOUT_PERCENTAGE = int(os.getenv("TEMPORAL_ROLLOUT", "10"))

@workflow.defn  
class RolloutWorkflow:
    @workflow.run
    async def run(self, doc_id: str):
        # Deterministic routing (same doc_id always goes same path)
        use_temporal = hash(doc_id) % 100 < TEMPORAL_ROLLOUT_PERCENTAGE
        
        if use_temporal:
            return await execute_temporal_path(doc_id)
        return await execute_legacy_path(doc_id)
```

**Monitoring:**
- Temporal UI: Monitor 10% traffic workflows
- Compare error rates: Temporal vs Legacy
- Track latency P50, P90, P99

**Rollback Trigger:**
- Error rate > 2× legacy
- P99 latency > 5× legacy
- Data consistency issues

### Phase 3: 50% Traffic (Week 4) - Scaled Validation

**Increase:** `TEMPORAL_ROLLOUT=50`

**Monitoring:**
- Database load (4 databases)
- Circuit breaker states
- DLQ entry rate
- Temporal Server resource usage

### Phase 4: 100% Traffic (Week 5) - Full Migration

**Increase:** `TEMPORAL_ROLLOUT=100`

**Post-Migration:**
- Keep legacy code for 2 weeks (safety)
- Remove legacy path after validation
- Update documentation

## Worker Versioning Strategy

### Pinned vs Auto-Upgrade Workflows

```python
from temporalio.common import VersioningBehavior
from temporalio.worker import Worker, WorkerDeploymentConfig

# Version 1.0 deployment
worker_v1 = Worker(
    client,
    task_queue="ingestion-queue",
    workflows=[IngestionWorkflow],
    deployment_config=WorkerDeploymentConfig(
        version=WorkerDeploymentVersion(
            deployment_name="ingestion-service",
            build_id="v1.0.0"
        ),
        use_worker_versioning=True,
        default_versioning_behavior=VersioningBehavior.PINNED
    )
)

# Version 2.0 deployment (new build)
worker_v2 = Worker(
    client,
    task_queue="ingestion-queue",
    workflows=[IngestionWorkflowV2],  # Updated workflow
    deployment_config=WorkerDeploymentConfig(
        version=WorkerDeploymentVersion(
            deployment_name="ingestion-service",
            build_id="v2.0.0"
        ),
        use_worker_versioning=True
    )
)
```

**Deployment Commands:**
```bash
# Set v2.0 as ramping version (5% traffic)
temporal worker deployment set-ramping-version \
  --deployment-name ingestion-service \
  --build-id v2.0.0 \
  --percentage 5

# Increase ramp
temporal worker deployment set-ramping-version \
  --deployment-name ingestion-service \
  --build-id v2.0.0 \
  --percentage 50

# Promote to current (100% traffic)
temporal worker deployment set-current-version \
  --deployment-name ingestion-service \
  --build-id v2.0.0

# Rollback instantly
temporal worker deployment set-current-version \
  --deployment-name ingestion-service \
  --build-id v1.0.0
```

## Rollback Procedures

### Instant Rollback (< 5 minutes)

```bash
# Option 1: Environment variable
export TEMPORAL_ROLLOUT=0  # Route all to legacy
kubectl rollout restart deployment/workers  # Restart workers

# Option 2: Worker versioning
temporal worker deployment set-current-version \
  --deployment-name ingestion-service \
  --build-id v1.0.0  # Previous stable version

# Option 3: Docker Compose
docker-compose -f docker/temporal-compose.yml down
# Remove Temporal, traffic falls back to legacy
```

### Graceful Rollback (< 30 minutes)

```bash
# 1. Stop new workflows
temporal workflow terminate --query "WorkflowType='IngestionWorkflow'"

# 2. Let running workflows complete (or cancel)
temporal workflow list --query "WorkflowType='IngestionWorkflow' AND ExecutionStatus='Running'"

# 3. Reduce traffic gradually
export TEMPORAL_ROLLOUT=50
export TEMPORAL_ROLLOUT=10
export TEMPORAL_ROLLOUT=0

# 4. Shut down Temporal
docker-compose -f docker/temporal-compose.yml down
```

## Testing Strategy

### Pre-Migration Tests

```python
# Test 1: Temporal + Saga integration
@pytest.mark.integration
async def test_temporal_saga_integration():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        result = await env.client.execute_workflow(
            IngestionWorkflow.run,
            "test-doc-123",
            task_queue="test-queue"
        )
        assert result["status"] == "success"

# Test 2: Error handling
@pytest.mark.integration  
async def test_saga_rollback_via_temporal():
    # Inject failure, verify rollback + DLQ
    ...

# Test 3: Load testing
@pytest.mark.load
async def test_concurrent_workflows():
    # 100 concurrent workflows
    tasks = [
        env.client.start_workflow(IngestionWorkflow.run, f"doc-{i}")
        for i in range(100)
    ]
    await asyncio.gather(*tasks)
```

### Migration Validation Tests

```bash
# Run full test suite before migration
pytest tests/ -v --cov=apex_memory --cov-report=html

# Expected: 121/121 Saga tests + 50+ Temporal tests passing
```

## Related Documentation

- [Temporal Overview](temporal-io-overview.md)
- [Integration Patterns](integration-patterns.md)
- [Deployment Guide](deployment-guide.md)
