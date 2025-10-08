#!/usr/bin/env python3
"""
Gradual Rollout Script

Automates Phase 4 gradual rollout with safety checks.
Increases rollout percentage in safe increments with monitoring.

Timeline:
  Day 1:  5% (internal team)
  Day 4: 25% (early adopters)
  Day 8: 50% (majority)
  Day 14: 100% (everyone)
"""

import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import redis.asyncio as redis
from apex_memory.query_router.feature_flags import FeatureFlagManager

load_dotenv()


class GradualRollout:
    """Automated gradual rollout manager."""

    def __init__(self, flag_manager, flag_name="phase4_online_learning"):
        self.flag_manager = flag_manager
        self.flag_name = flag_name

        # Rollout stages
        self.stages = [
            {"percentage": 5, "wait_days": 3, "name": "Canary"},
            {"percentage": 25, "wait_days": 4, "name": "Early Adopters"},
            {"percentage": 50, "wait_days": 6, "name": "Majority"},
            {"percentage": 100, "wait_days": 0, "name": "Full Rollout"}
        ]

        # Safety thresholds
        self.max_error_rate = 0.05  # 5%
        self.max_latency_increase = 0.20  # 20%
        self.min_avg_reward = 0.40  # Below this triggers rollback

    async def get_current_metrics(self):
        """Get current system metrics (mock - implement with your monitoring)."""

        # TODO: Implement actual metric collection from Prometheus/Grafana
        return {
            "error_rate": 0.01,  # 1%
            "latency_p99": 950,  # ms
            "avg_reward": 0.65,
            "cache_hit_rate": 0.92
        }

    async def check_safety(self, baseline_metrics):
        """Check if it's safe to proceed to next stage."""

        current = await self.get_current_metrics()

        # Check error rate
        if current["error_rate"] > self.max_error_rate:
            return False, f"Error rate too high: {current['error_rate']:.1%}"

        # Check latency increase
        if baseline_metrics:
            latency_increase = (current["latency_p99"] - baseline_metrics["latency_p99"]) / baseline_metrics["latency_p99"]
            if latency_increase > self.max_latency_increase:
                return False, f"Latency increased {latency_increase:.1%}"

        # Check avg reward (if online learning active)
        if current.get("avg_reward", 1.0) < self.min_avg_reward:
            return False, f"Avg reward too low: {current['avg_reward']:.2f}"

        return True, "All metrics healthy"

    async def rollout_to_percentage(self, percentage, dry_run=False):
        """Roll out to a specific percentage."""

        print(f"\n📈 Rolling out to {percentage}%...")

        if dry_run:
            print("   [DRY RUN] Would set rollout to {percentage}%")
            return

        await self.flag_manager.set_rollout_percentage(self.flag_name, percentage)

        # Verify
        flag_state = await self.flag_manager.get_flag(self.flag_name)
        actual_pct = flag_state.rollout_percentage

        if actual_pct == percentage:
            print(f"   ✓ Rollout set to {actual_pct}%")
        else:
            print(f"   ⚠️  Expected {percentage}%, got {actual_pct}%")

        return actual_pct

    async def run(self, dry_run=False, interactive=True):
        """Run automated gradual rollout."""

        print("🚀 Starting Gradual Rollout for Phase 4\n")

        if dry_run:
            print("⚠️  DRY RUN MODE - No changes will be made\n")

        # Get baseline metrics
        print("📊 Collecting baseline metrics...")
        baseline_metrics = await self.get_current_metrics()
        print(f"   - Error rate: {baseline_metrics['error_rate']:.1%}")
        print(f"   - Latency P99: {baseline_metrics['latency_p99']}ms")
        print(f"   - Cache hit rate: {baseline_metrics['cache_hit_rate']:.1%}\n")

        # Get current state
        current_state = await self.flag_manager.get_flag(self.flag_name)
        current_pct = current_state.rollout_percentage

        print(f"📍 Current rollout: {current_pct}%\n")

        # Find next stage
        next_stage = None
        for stage in self.stages:
            if stage["percentage"] > current_pct:
                next_stage = stage
                break

        if not next_stage:
            print("✅ Already at 100% rollout!")
            return

        # Execute next stage
        print(f"🎯 Next Stage: {next_stage['name']} ({next_stage['percentage']}%)\n")

        if interactive:
            response = input(f"Proceed to {next_stage['percentage']}%? [y/N]: ")
            if response.lower() != 'y':
                print("   Cancelled by user")
                return

        # Safety check
        is_safe, reason = await self.check_safety(baseline_metrics)
        if not is_safe:
            print(f"⚠️  Safety check failed: {reason}")
            print(f"   Rollout aborted. Fix issues and try again.")
            return

        print(f"✓ Safety check passed: {reason}")

        # Roll out
        await self.rollout_to_percentage(next_stage["percentage"], dry_run=dry_run)

        # Monitor period
        wait_days = next_stage["wait_days"]
        if wait_days > 0:
            print(f"\n⏱️  Monitor for {wait_days} days before next stage")
            print(f"   Next rollout eligible: {(datetime.now() + timedelta(days=wait_days)).strftime('%Y-%m-%d')}")

        # Show what's next
        next_index = self.stages.index(next_stage) + 1
        if next_index < len(self.stages):
            next_next = self.stages[next_index]
            print(f"\n📍 After monitoring, next stage: {next_next['name']} ({next_next['percentage']}%)")
        else:
            print(f"\n🎉 This is the final stage! Monitor at 100% for 2-4 weeks, then cleanup.")

        print(f"\n✅ Rollout to {next_stage['percentage']}% complete!")


async def emergency_rollback(flag_manager, flag_name="phase4_online_learning"):
    """Emergency rollback to 0%."""

    print("\n🚨 EMERGENCY ROLLBACK\n")

    await flag_manager.set_rollout_percentage(flag_name, 0)

    flag_state = await flag_manager.get_flag(flag_name)
    print(f"   ✓ Rolled back to {flag_state.rollout_percentage}%")
    print(f"   Phase 4 disabled for all users (except whitelist)")

    print("\n✅ Emergency rollback complete")
    print("   Investigate issues, fix, then retry rollout")


async def get_rollout_status(flag_manager, flag_name="phase4_online_learning"):
    """Get current rollout status."""

    flag_state = await flag_manager.get_flag(flag_name)

    print(f"\n📊 Rollout Status: {flag_name}\n")
    print(f"   Percentage: {flag_state.rollout_percentage}%")
    print(f"   Enabled globally: {flag_state.enabled}")
    print(f"   Whitelist: {len(flag_state.whitelist)} users")
    print(f"   Blacklist: {len(flag_state.blacklist)} users")
    print(f"   Last updated: {flag_state.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # Estimate users affected
    if flag_state.rollout_percentage > 0:
        # Mock user count
        total_users = 1000
        affected = int(total_users * flag_state.rollout_percentage / 100) + len(flag_state.whitelist)
        print(f"\n   📈 Estimated users with Phase 4: {affected}/{total_users}")


async def main():
    """Main entry point."""

    import sys

    # Connect to Redis
    redis_client = await redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    flag_manager = FeatureFlagManager(redis_client)
    await flag_manager.initialize()

    # Parse command
    command = sys.argv[1] if len(sys.argv) > 1 else "rollout"

    if command == "rollout":
        # Run gradual rollout
        dry_run = "--dry-run" in sys.argv
        interactive = "--non-interactive" not in sys.argv

        rollout = GradualRollout(flag_manager)
        await rollout.run(dry_run=dry_run, interactive=interactive)

    elif command == "status":
        # Show status
        await get_rollout_status(flag_manager)

    elif command == "rollback":
        # Emergency rollback
        await emergency_rollback(flag_manager)

    else:
        print("Usage:")
        print("  python gradual_rollout_script.py rollout [--dry-run] [--non-interactive]")
        print("  python gradual_rollout_script.py status")
        print("  python gradual_rollout_script.py rollback")

    await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
