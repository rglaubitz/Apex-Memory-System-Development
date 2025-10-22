#!/usr/bin/env python3
"""
Feature Flag Setup Script

Creates and manages feature flags for Phase 4 deployment.
Use this to set up flags before gradual rollout.
"""

import os
import asyncio
from dotenv import load_dotenv
import redis.asyncio as redis
from apex_memory.query_router.feature_flags import FeatureFlagManager

load_dotenv()


async def setup_feature_flags():
    """Set up feature flags for Phase 4 deployment."""

    # Connect to Redis
    redis_client = await redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    # Create feature flag manager
    flag_manager = FeatureFlagManager(
        redis_client=redis_client,
        cache_ttl=30,
        default_fail_mode="closed"  # Fail-safe: disable on error
    )

    await flag_manager.initialize()

    print("✅ Feature flag manager initialized\n")

    # Create Phase 4 feature flag
    print("Creating Phase 4 feature flag...")
    await flag_manager.create_flag(
        flag_name="phase4_online_learning",
        description="Enable Phase 4 online learning router with real-time adaptation",
        default_enabled=False,
        rollout_percentage=0  # Start at 0%
    )

    print("✓ Created flag: phase4_online_learning")
    print("  - Rollout: 0% (disabled for all users)")
    print("  - Default: False (fail-safe)\n")

    # Add internal team to whitelist
    print("Adding internal team to whitelist...")
    internal_users = [
        "admin_user",
        "dev_user_1",
        "dev_user_2",
        "qa_tester"
    ]

    for user_id in internal_users:
        await flag_manager.add_to_whitelist("phase4_online_learning", user_id)
        print(f"  ✓ Whitelisted: {user_id}")

    print("\n✅ Internal team will always have Phase 4 enabled (for testing)\n")

    # Verify flag created
    flag_state = await flag_manager.get_flag("phase4_online_learning")
    print(f"📋 Flag state:")
    print(f"   - Name: {flag_state.name}")
    print(f"   - Enabled: {flag_state.enabled}")
    print(f"   - Rollout: {flag_state.rollout_percentage}%")
    print(f"   - Whitelist: {len(flag_state.whitelist)} users")
    print(f"   - Created: {flag_state.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Test flag evaluation
    print("🧪 Testing flag evaluation...")

    # Test whitelisted user (should be enabled)
    eval1 = await flag_manager.is_enabled("phase4_online_learning", "admin_user")
    print(f"   admin_user: {'✓ ENABLED' if eval1.enabled else '✗ DISABLED'} (reason: {eval1.reason})")

    # Test regular user (should be disabled at 0%)
    eval2 = await flag_manager.is_enabled("phase4_online_learning", "regular_user_123")
    print(f"   regular_user_123: {'✓ ENABLED' if eval2.enabled else '✗ DISABLED'} (reason: {eval2.reason})\n")

    print("✅ Feature flag setup complete!")
    print("\nNext steps:")
    print("   1. Test with internal team (whitelisted)")
    print("   2. Increase rollout to 5% (use gradual_rollout_script.py)")
    print("   3. Monitor metrics for 2-3 days")
    print("   4. Continue gradual rollout: 25% → 50% → 100%")

    await redis_client.aclose()


async def list_all_flags():
    """List all existing feature flags."""

    redis_client = await redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    flag_manager = FeatureFlagManager(redis_client)
    await flag_manager.initialize()

    flags = await flag_manager.list_flags()

    print(f"\n📋 All Feature Flags ({len(flags)} total):\n")

    for flag in flags:
        status = "🟢 ACTIVE" if flag.rollout_percentage > 0 else "⚪ INACTIVE"
        print(f"{status} {flag.name}")
        print(f"   Rollout: {flag.rollout_percentage}%")
        print(f"   Whitelist: {len(flag.whitelist)} users")
        print(f"   Description: {flag.description}")
        print()

    await redis_client.aclose()


async def cleanup_old_flags():
    """Clean up flags that have been at 100% for >4 weeks."""

    redis_client = await redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    flag_manager = FeatureFlagManager(redis_client)
    await flag_manager.initialize()

    flags = await flag_manager.list_flags()

    print("\n🧹 Checking for flags ready for cleanup...\n")

    from datetime import datetime, timedelta

    for flag in flags:
        if flag.rollout_percentage == 100:
            age = datetime.utcnow() - flag.updated_at
            if age > timedelta(weeks=4):
                print(f"⚠️  Flag '{flag.name}' has been at 100% for {age.days} days")
                print(f"   Consider making permanent and deleting flag")
                print(f"   Command: await flag_manager.delete_flag('{flag.name}')\n")

    await redis_client.aclose()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            asyncio.run(list_all_flags())
        elif sys.argv[1] == "cleanup":
            asyncio.run(cleanup_old_flags())
        else:
            print("Usage:")
            print("  python feature_flag_setup.py        # Set up Phase 4 flag")
            print("  python feature_flag_setup.py list   # List all flags")
            print("  python feature_flag_setup.py cleanup # Check for old flags")
    else:
        asyncio.run(setup_feature_flags())
