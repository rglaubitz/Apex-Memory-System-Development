#!/usr/bin/env python3
"""
Query Router Configuration - Phases 1+2+3

Complete router with Agentic Evolution (baseline before Phase 4):
- Phase 1: Semantic classification, rewriting, analytics
- Phase 2: Adaptive routing, GraphRAG, caching, fusion
- Phase 3: Complexity analysis, multi-router, self-correction, query improvement

This is the BASELINE configuration before enabling Phase 4.
Use this to establish performance metrics before gradual rollout.
"""

import os
from dotenv import load_dotenv
from apex_memory.query_router.router import QueryRouter

load_dotenv()

async def create_phase3_router():
    """Create query router with Phases 1+2+3 (baseline)."""

    # Initialize connections
    from neo4j import AsyncGraphDatabase
    import asyncpg
    from qdrant_client import QdrantClient
    import redis.asyncio as redis

    neo4j_driver = AsyncGraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
    )

    postgres_conn = await asyncpg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB")
    )

    qdrant_client = QdrantClient(
        host=os.getenv("QDRANT_HOST"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )

    redis_client = await redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    router = QueryRouter(
        # Database connections
        neo4j_driver=neo4j_driver,
        postgres_conn=postgres_conn,
        qdrant_client=qdrant_client,
        redis_host=os.getenv("REDIS_HOST"),

        # Phase 1: Foundation (ENABLED)
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        postgres_dsn=os.getenv("POSTGRES_DSN"),
        enable_semantic_classification=True,
        enable_query_rewriting=True,
        enable_analytics=True,

        # Phase 2: Intelligent Routing (ENABLED)
        neo4j_uri=os.getenv("NEO4J_URI"),
        neo4j_user=os.getenv("NEO4J_USER"),
        neo4j_password=os.getenv("NEO4J_PASSWORD"),
        redis_client=redis_client,
        enable_adaptive_routing=True,
        enable_graphrag=True,
        enable_semantic_cache=True,
        enable_result_fusion=True,
        bandit_alpha=0.5,
        cache_similarity_threshold=0.95,

        # Phase 3: Agentic Evolution (ENABLED)
        enable_complexity_analysis=True,
        enable_multi_router=True,
        enable_self_correction=True,
        enable_query_improvement=True,
        max_correction_retries=2,

        # Phase 4: DISABLED (baseline)
        enable_feature_flags=False,
        enable_online_learning=False
    )

    await router.initialize()

    print("✅ Phase 1+2+3 router initialized (BASELINE)")
    print("   Phase 1: ✓ Semantic classification, rewriting, analytics")
    print("   Phase 2: ✓ Adaptive routing, GraphRAG, caching, fusion")
    print("   Phase 3: ✓ Complexity analysis, multi-router, self-correction")
    print("   Phase 4: ✗ Feature flags and online learning DISABLED")
    print("\n   This is your BASELINE for Phase 4 comparison.")

    return router


async def collect_baseline_metrics(router):
    """Collect baseline metrics for Phase 4 comparison."""

    print("\n📊 Collecting baseline metrics...")
    print("   Run queries for 2-3 days to establish baseline.\n")

    # Sample queries
    test_queries = [
        "find all invoices from ACME Corp",
        "show relationships between companies",
        "temporal analysis of contracts last quarter",
        "similar documents to contract ABC123"
    ]

    metrics = {
        "latency_p50": [],
        "latency_p90": [],
        "latency_p99": [],
        "cache_hits": 0,
        "total_queries": 0
    }

    for query in test_queries:
        result = await router.query(query)
        latency = result.get('latency_ms', 0)
        metrics["latency_p50"].append(latency)
        metrics["total_queries"] += 1

        if result.get('cached'):
            metrics["cache_hits"] += 1

    # Calculate metrics
    import statistics
    if metrics["latency_p50"]:
        p50 = statistics.median(metrics["latency_p50"])
        p90 = statistics.quantiles(metrics["latency_p50"], n=10)[8]
        p99 = max(metrics["latency_p50"])

        print(f"   Latency P50: {p50:.0f}ms")
        print(f"   Latency P90: {p90:.0f}ms")
        print(f"   Latency P99: {p99:.0f}ms")

    cache_hit_rate = metrics["cache_hits"] / metrics["total_queries"] if metrics["total_queries"] > 0 else 0
    print(f"   Cache hit rate: {cache_hit_rate:.1%}")

    print("\n   💾 Save these metrics for Phase 4 comparison!")

    return metrics


if __name__ == "__main__":
    import asyncio

    async def main():
        router = await create_phase3_router()
        baseline_metrics = await collect_baseline_metrics(router)

        print("\n✅ Baseline established. Ready for Phase 4 deployment.")
        print("   Next: Enable Phase 4 with feature flags at 0%")

    asyncio.run(main())
