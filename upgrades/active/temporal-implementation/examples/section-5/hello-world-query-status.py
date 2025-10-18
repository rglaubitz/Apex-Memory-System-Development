"""Hello World - Query Workflow Status.

This example demonstrates how to query workflow status and fetch results
after workflow execution completes.

Prerequisites:
    1. Temporal Server running:
       cd docker && docker-compose -f temporal-compose.yml up -d

    2. Worker running:
       python -m apex_memory.temporal.workers.dev_worker

Usage:
    python examples/section-5/hello-world-query-status.py

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
from temporalio.client import Client, WorkflowHandle

from apex_memory.config import TemporalConfig


async def main():
    """Execute workflow and query its status."""
    config = TemporalConfig.from_env()

    print(f"Connecting to Temporal Server at {config.server_url}...")

    client = await Client.connect(
        config.server_url,
        namespace=config.namespace,
    )

    workflow_id = "hello-world-query-status-example"

    print(f"Executing GreetingWorkflow (ID: {workflow_id})...")

    # Start workflow (non-blocking)
    handle = await client.start_workflow(
        "GreetingWorkflow",
        "Status Query Demo",
        id=workflow_id,
        task_queue=config.task_queue,
    )

    print(f"\n✅ Workflow started!")
    print(f"   Workflow ID: {handle.id}")
    print(f"   Run ID: {handle.result_run_id}")

    # Query workflow status
    print("\n📊 Querying workflow status...")

    # Wait for workflow to complete
    result = await handle.result()

    print(f"\n✅ Workflow completed!")
    print(f"   Status: Completed")
    print(f"   Result: {result}")

    # Fetch workflow description for detailed status
    description = await handle.describe()

    print(f"\n📋 Workflow Details:")
    print(f"   Status: {description.status}")
    print(f"   Start Time: {description.start_time}")
    print(f"   Close Time: {description.close_time}")
    print(f"   Execution Time: {description.close_time - description.start_time}")

    # Fetch workflow history
    print(f"\n📜 Fetching workflow history...")
    history = handle.fetch_history()
    events = [event async for event in history]

    print(f"   Total events: {len(events)}")
    print(f"   Event types:")
    for i, event in enumerate(events[:5], 1):  # Show first 5 events
        print(f"      {i}. {event.event_type}")

    if len(events) > 5:
        print(f"      ... and {len(events) - 5} more events")

    print(f"\n🔗 View full details in Temporal UI:")
    print(f"   http://localhost:8088/namespaces/{config.namespace}/workflows/{workflow_id}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
