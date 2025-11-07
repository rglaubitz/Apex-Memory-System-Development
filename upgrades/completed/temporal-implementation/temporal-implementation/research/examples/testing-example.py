"""Temporal Testing Examples.

Demonstrates:
- Unit testing activities
- Unit testing workflows
- Integration testing with time-skipping
- Mocking activities
"""

import pytest
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.testing import WorkflowEnvironment, ActivityEnvironment
from temporalio.worker import Worker
from temporalio.common import RetryPolicy


# Example activity
@activity.defn
async def process_data(data: str) -> str:
    """Process data (activity to test)."""
    return f"Processed: {data}"


# Example workflow
@workflow.defn
class DataWorkflow:
    """Workflow to test."""
    
    @workflow.run
    async def run(self, data: str) -> str:
        result = await workflow.execute_activity(
            process_data,
            data,
            start_to_close_timeout=timedelta(seconds=10)
        )
        return result


# ============================================================================
# Unit Testing Activities
# ============================================================================

@pytest.mark.asyncio
async def test_activity_unit():
    """Test activity in isolation."""
    activity_env = ActivityEnvironment()
    
    result = await activity_env.run(process_data, "test-data")
    
    assert result == "Processed: test-data"


# ============================================================================
# Unit Testing Workflows
# ============================================================================

@pytest.mark.asyncio
async def test_workflow_unit():
    """Test workflow with time-skipping."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DataWorkflow],
            activities=[process_data]
        ):
            result = await env.client.execute_workflow(
                DataWorkflow.run,
                "test-data",
                id="test-workflow",
                task_queue="test-queue"
            )
            
            assert result == "Processed: test-data"


# ============================================================================
# Mocking Activities
# ============================================================================

@pytest.mark.asyncio
async def test_workflow_with_mocked_activity():
    """Test workflow with mocked activity."""
    
    # Mock activity
    @activity.defn
    async def mock_process_data(data: str) -> str:
        return f"Mocked: {data}"
    
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DataWorkflow],
            activities=[mock_process_data]  # Use mock instead of real
        ):
            result = await env.client.execute_workflow(
                DataWorkflow.run,
                "test-data",
                id="test-workflow-mocked",
                task_queue="test-queue"
            )
            
            assert result == "Mocked: test-data"


# ============================================================================
# Testing Error Scenarios
# ============================================================================

@pytest.mark.asyncio
async def test_activity_retry():
    """Test activity retry behavior."""
    
    attempt_count = 0
    
    @activity.defn
    async def failing_activity() -> str:
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count < 3:
            raise Exception(f"Attempt {attempt_count} failed")
        
        return "Success on attempt 3"
    
    @workflow.defn
    class RetryWorkflow:
        @workflow.run
        async def run(self) -> str:
            return await workflow.execute_activity(
                failing_activity,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=5,
                    initial_interval=timedelta(milliseconds=100)
                )
            )
    
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[RetryWorkflow],
            activities=[failing_activity]
        ):
            result = await env.client.execute_workflow(
                RetryWorkflow.run,
                id="test-retry",
                task_queue="test-queue"
            )
            
            assert result == "Success on attempt 3"
            assert attempt_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
