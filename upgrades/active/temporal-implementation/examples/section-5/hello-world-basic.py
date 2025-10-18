"""Hello World - Basic Example.

This example demonstrates minimal workflow execution with GreetingWorkflow.
Shows the simplest possible Temporal workflow execution.

Prerequisites:
    1. Temporal Server running:
       cd docker && docker-compose -f temporal-compose.yml up -d

    2. Worker running:
       python -m apex_memory.temporal.workers.dev_worker

Usage:
    python examples/section-5/hello-world-basic.py

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
from temporalio.client import Client

from apex_memory.config import TemporalConfig


async def main():
    """Execute basic Hello World workflow."""
    # Load configuration from environment
    config = TemporalConfig.from_env()

    print(f"Connecting to Temporal Server at {config.server_url}...")

    # Connect to Temporal Server
    client = await Client.connect(
        config.server_url,
        namespace=config.namespace,
    )

    print("Executing GreetingWorkflow...")

    # Execute workflow
    result = await client.execute_workflow(
        "GreetingWorkflow",
        "World",
        id="hello-world-basic-example",
        task_queue=config.task_queue,
    )

    print(f"\nResult: {result}")
    print("\n✅ Success! Basic workflow execution complete.")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
