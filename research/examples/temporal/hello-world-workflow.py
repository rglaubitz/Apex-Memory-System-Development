"""Hello World Temporal Workflow Example.

Demonstrates:
- Basic workflow definition
- Activity definition
- Worker setup
- Client execution

Usage:
    python hello_world_workflow.py
"""

import asyncio
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


@activity.defn
async def say_hello(name: str) -> str:
    """Simple activity that returns a greeting.
    
    Activities are the basic unit of work in Temporal.
    They should be idempotent and can be retried.
    """
    activity.logger.info(f"Saying hello to {name}")
    return f"Hello, {name}!"


@workflow.defn
class HelloWorldWorkflow:
    """Basic workflow that executes a single activity.
    
    Workflows orchestrate activities and maintain state.
    They must be deterministic for replay.
    """
    
    @workflow.run
    async def run(self, name: str) -> str:
        """Workflow entry point.
        
        Args:
            name: Name to greet
            
        Returns:
            Greeting message
        """
        workflow.logger.info(f"Starting HelloWorld workflow for {name}")
        
        # Execute activity with timeout
        greeting = await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        workflow.logger.info(f"Workflow complete: {greeting}")
        return greeting


async def main():
    """Main function to run the hello world example."""
    # Connect to Temporal Server
    client = await Client.connect("localhost:7233")
    
    # Start worker
    print("Starting worker...")
    async with Worker(
        client,
        task_queue="hello-queue",
        workflows=[HelloWorldWorkflow],
        activities=[say_hello]
    ):
        print("Worker started. Executing workflow...")
        
        # Execute workflow
        result = await client.execute_workflow(
            HelloWorldWorkflow.run,
            "World",
            id="hello-workflow-1",
            task_queue="hello-queue"
        )
        
        print(f"Result: {result}")
        print("\n✅ Workflow completed successfully!")
        print("View in Temporal UI: http://localhost:8088")


if __name__ == "__main__":
    asyncio.run(main())
