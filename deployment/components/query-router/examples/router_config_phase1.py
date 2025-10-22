#!/usr/bin/env python3
"""
Query Router Configuration - Phase 1 Only

Foundation features:
- Semantic intent classification (90%+ accuracy)
- Claude-powered query rewriting (+21-28 point relevance)
- Comprehensive analytics (Prometheus + Jaeger + PostgreSQL)

Use this configuration to test Phase 1 in isolation.
"""

import os
from dotenv import load_dotenv
from apex_memory.query_router.router import QueryRouter

# Load environment variables
load_dotenv()

async def create_phase1_router():
    """Create query router with Phase 1 features only."""

    # Initialize database connections (you'll need to set these up)
    from neo4j import AsyncGraphDatabase
    import asyncpg
    from qdrant_client import QdrantClient
    import redis.asyncio as redis

    # Neo4j
    neo4j_driver = AsyncGraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
    )

    # PostgreSQL
    postgres_conn = await asyncpg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB")
    )

    # Qdrant
    qdrant_client = QdrantClient(
        host=os.getenv("QDRANT_HOST"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )

    # Redis
    redis_client = await redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    # Create router with Phase 1 only
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

        # Phases 2-4: DISABLED
        enable_adaptive_routing=False,
        enable_graphrag=False,
        enable_semantic_cache=False,
        enable_result_fusion=False,
        enable_complexity_analysis=False,
        enable_multi_router=False,
        enable_self_correction=False,
        enable_query_improvement=False,
        enable_feature_flags=False,
        enable_online_learning=False
    )

    # Initialize async components
    await router.initialize()

    print("✅ Phase 1 router initialized")
    print("   - Semantic classification: ENABLED")
    print("   - Query rewriting: ENABLED")
    print("   - Analytics: ENABLED")
    print("   - Phases 2-4: DISABLED")

    return router


async def test_phase1_router(router):
    """Test Phase 1 features."""

    # Test query
    test_query = "find all invoices from ACME Corp in the last quarter"

    print(f"\n🔍 Testing query: {test_query}")

    # Execute query
    result = await router.query(test_query, limit=10)

    print(f"\n📊 Results:")
    print(f"   - Intent: {result.get('intent', 'N/A')}")
    print(f"   - Rewritten query: {result.get('rewritten_query', 'N/A')}")
    print(f"   - Results found: {len(result.get('results', []))}")
    print(f"   - Latency: {result.get('latency_ms', 0)}ms")

    # Check analytics
    if router.analytics:
        stats = await router.analytics.get_routing_stats(limit=10)
        print(f"\n📈 Analytics:")
        print(f"   - Total queries: {stats.get('total_queries', 0)}")
        print(f"   - Avg latency: {stats.get('avg_latency_ms', 0)}ms")


if __name__ == "__main__":
    import asyncio

    async def main():
        router = await create_phase1_router()
        await test_phase1_router(router)

    asyncio.run(main())
