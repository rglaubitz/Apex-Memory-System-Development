"""Hello World - Retry Policy Demonstration.

This example demonstrates how GreetingWorkflow handles retries when activities fail.
Shows retry policy configuration: initial_interval=1s, max_attempts=3.

Prerequisites:
    1. Temporal Server running:
       cd docker && docker-compose -f temporal-compose.yml up -d

    2. Worker running:
       python -m apex_memory.temporal.workers.dev_worker

Usage:
    python examples/section-5/hello-world-with-retry.py

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
from temporalio.client import Client

from apex_memory.config import TemporalConfig


async def main():
    """Execute workflow demonstrating retry policy."""
    config = TemporalConfig.from_env()

    print(f"Connecting to Temporal Server at {config.server_url}...")

    client = await Client.connect(
        config.server_url,
        namespace=config.namespace,
    )

    print("Executing GreetingWorkflow (with retry policy)...")
    print("\nRetry Policy Configuration:")
    print("  - Initial interval: 1 second")
    print("  - Maximum interval: 10 seconds")
    print("  - Maximum attempts: 3")
    print("\nNote: If activity fails, it will retry automatically.\n")

    # Execute workflow with retry policy (configured in workflow definition)
    result = await client.execute_workflow(
        "GreetingWorkflow",
        "Retry Demo",
        id="hello-world-retry-example",
        task_queue=config.task_queue,
    )

    print(f"\nResult: {result}")
    print("\n✅ Success! Workflow completed (with retry policy active).")
    print("\nTo see retries in action:")
    print("  1. Modify greet_activity to raise exception occasionally")
    print("  2. Re-run this example")
    print("  3. Check Temporal UI for retry attempts")
    print(f"\n🔗 Temporal UI: http://localhost:8088/namespaces/{config.namespace}/workflows")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
