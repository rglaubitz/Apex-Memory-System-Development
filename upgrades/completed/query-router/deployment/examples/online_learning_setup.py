#!/usr/bin/env python3
"""
Online Learning Setup Script

Initializes online learning router with Phase 2 contextual bandit warm start.
Verifies background task running and ready for feedback.
"""

import os
import asyncio
from dotenv import load_dotenv
from apex_memory.query_router.adaptive_weights import ContextualBandit
from apex_memory.query_router.online_learning import OnlineLearningRouter, UserFeedback

load_dotenv()


async def setup_online_learning():
    """Set up online learning router with warm start from Phase 2."""

    print("🧠 Setting up online learning router...\n")

    # Initialize Phase 2 contextual bandit (warm start)
    print("Step 1: Loading Phase 2 contextual bandit weights...")
    bandit = ContextualBandit(
        n_databases=4,         # neo4j, postgres, qdrant, graphiti
        embedding_dim=1536,    # OpenAI embedding dimension
        alpha=0.5,             # Exploration parameter
        postgres_dsn=os.getenv("POSTGRES_DSN")
    )

    await bandit.initialize()
    print("✓ Phase 2 weights loaded (warm start)\n")

    # Create online learning router
    print("Step 2: Creating online learning router...")
    online_router = OnlineLearningRouter(
        base_bandit=bandit,
        batch_size=100,        # Process 100 feedback items at a time
        learning_rate=0.01,    # Conservative learning rate
        reward_weights={
            'clicked': 0.4,
            'dwell_time': 0.3,
            'explicit_rating': 0.2,
            'latency': 0.1
        }
    )

    await online_router.initialize()
    print("✓ Online learning router initialized")
    print("✓ Background learning task started\n")

    # Verify background task running
    print("Step 3: Verifying background task...")
    assert online_router.learning_task is not None
    assert not online_router.learning_task.done()
    print("✓ Background task running\n")

    # Show initial stats
    stats = online_router.get_stats()
    print(f"📊 Initial Stats:")
    print(f"   - Feedback count: {stats['feedback_count']}")
    print(f"   - Batch updates: {stats['batch_update_count']}")
    print(f"   - Queue size: {stats['queue_size']}")
    print(f"   - Learning rate: {stats['learning_rate']}\n")

    # Per-database stats
    print(f"   Per-database (from Phase 2 warm start):")
    for db_name, db_stats in stats['databases'].items():
        print(f"   - {db_name}: {db_stats['n_pulls']} pulls, "
              f"avg reward {db_stats['avg_reward']:.3f}")

    print("\n✅ Online learning setup complete!")

    return online_router


async def test_feedback_flow(online_router):
    """Test feedback recording and processing."""

    print("\n🧪 Testing feedback flow...\n")

    # Simulate a query
    import numpy as np

    query = "find ACME Corp invoices"
    query_embedding = np.random.rand(1536)  # Mock embedding

    # Mock execute function
    async def mock_execute(databases):
        return {"results": [{"doc_id": "123"}], "latency_ms": 250}

    # Route query (stores context)
    result, query_id = await online_router.route(
        query=query,
        query_embedding=query_embedding,
        intent="semantic",
        execute_fn=mock_execute
    )

    print(f"   Query: {query}")
    print(f"   Query ID: {query_id}")
    print(f"   Databases: {result.get('databases', 'N/A')}")
    print()

    # Simulate user feedback
    feedback = UserFeedback(
        query_id=query_id,
        clicked=True,
        click_position=1,
        dwell_time_seconds=15,
        explicit_rating=4.5,
        result_count=1,
        latency_ms=250
    )

    await online_router.record_feedback(feedback)

    print(f"   ✓ Feedback recorded")
    print(f"     - Clicked: {feedback.clicked}")
    print(f"     - Dwell time: {feedback.dwell_time_seconds}s")
    print(f"     - Rating: {feedback.explicit_rating}/5.0")
    print()

    # Check stats updated
    stats = online_router.get_stats()
    print(f"   📊 Updated Stats:")
    print(f"     - Feedback count: {stats['feedback_count']}")
    print(f"     - Queue size: {stats['queue_size']}")
    print(f"     - Total reward: {stats['total_reward']:.3f}")
    print()

    print("   ✅ Feedback flow working correctly!")


async def monitor_learning(online_router, duration_seconds=30):
    """Monitor online learning for a period."""

    print(f"\n📊 Monitoring online learning for {duration_seconds} seconds...\n")

    import time

    start_time = time.time()
    last_stats = online_router.get_stats()

    while time.time() - start_time < duration_seconds:
        await asyncio.sleep(5)

        stats = online_router.get_stats()

        # Check if learning is happening
        new_batches = stats['batch_update_count'] - last_stats['batch_update_count']
        new_feedback = stats['feedback_count'] - last_stats['feedback_count']

        if new_batches > 0:
            print(f"   ✓ Processed {new_batches} batches ({new_feedback} feedback items)")

        last_stats = stats

    final_stats = online_router.get_stats()

    print(f"\n   Final Stats:")
    print(f"   - Total feedback: {final_stats['feedback_count']}")
    print(f"   - Total batches: {final_stats['batch_update_count']}")
    print(f"   - Avg reward: {final_stats['avg_reward']:.3f}")

    print("\n✅ Monitoring complete!")


async def adjust_learning_rate_example(online_router):
    """Example: Adjust learning rate based on performance."""

    print("\n⚙️  Learning Rate Adjustment Example\n")

    stats = online_router.get_stats()

    print(f"   Current learning rate: {stats['learning_rate']}")
    print(f"   Feedback count: {stats['feedback_count']}")

    # Example logic: Slow down learning after 1000 feedback items
    if stats['feedback_count'] > 1000:
        new_rate = 0.005  # Half the default
        online_router.adjust_learning_rate(new_rate)
        print(f"   ✓ Reduced learning rate to {new_rate} (more conservative)")
    else:
        print(f"   ℹ️  Learning rate OK (need more feedback to adjust)")


if __name__ == "__main__":

    async def main():
        # Set up online learning
        online_router = await setup_online_learning()

        # Test feedback flow
        await test_feedback_flow(online_router)

        # Example: Monitor learning
        # await monitor_learning(online_router, duration_seconds=30)

        # Example: Adjust learning rate
        await adjust_learning_rate_example(online_router)

        # Clean up
        await online_router.close()

        print("\n✅ Online learning setup and testing complete!")
        print("\nNext steps:")
        print("   1. Enable in production with feature flag at 0%")
        print("   2. Gradual rollout: 5% → 25% → 50% → 100%")
        print("   3. Monitor avg reward (target: 0.6+)")
        print("   4. Adjust learning rate if needed")

    asyncio.run(main())
