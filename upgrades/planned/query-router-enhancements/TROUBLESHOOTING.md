# Query Router Advanced Features - Troubleshooting Guide

**Document:** Common Issues and Solutions
**Audience:** Developers encountering implementation problems

---

## Quick Diagnosis

**Common Symptoms:**

1. **Community detection returns empty list** → graphiti-core bug or Neo4j connection issue
2. **Query explanations are generic/low-quality** → Claude prompt needs tuning
3. **Pattern prediction accuracy <85%** → Insufficient historical data or incorrect time window
4. **Performance degradation (>2s for communities)** → Cache disabled or large community count
5. **Tests failing after upgrade** → Import errors or missing dependencies

---

## Issue 1: Community Detection Not Working

### Symptom

```python
communities = await community_manager.detect_communities()
print(len(communities))  # Output: 0 (expected: >0)
```

### Root Causes

**Cause 1.1: graphiti-core 0.22.0 Bug**

**Problem:** Community detection disabled due to `semaphore_gather` unpacking issue in graphiti-core 0.22.0

**Solution:**

```bash
# Upgrade to graphiti-core 0.23.0+
pip install --upgrade graphiti-core

# Verify version
python -c "import graphiti_core; print(graphiti_core.__version__)"

# Expected: 0.23.0 or higher
```

**If upgrade doesn't work:**

Implement custom community detection using NetworkX:

```python
# community_manager.py
import networkx as nx

async def detect_communities_custom(self):
    """Custom community detection using NetworkX Louvain algorithm."""

    # Get all entities and relationships from Neo4j
    query = """
    MATCH (e1:Entity)-[r]->(e2:Entity)
    RETURN e1.uuid as source, e2.uuid as target, type(r) as rel_type
    """

    records, _, _ = await self.graphiti.client.driver.execute_query(query)

    # Build NetworkX graph
    G = nx.Graph()
    for record in records:
        G.add_edge(record['source'], record['target'])

    # Louvain community detection
    import networkx.algorithms.community as nx_comm
    communities_raw = nx_comm.louvain_communities(G)

    # Convert to Community objects
    communities = []
    for i, comm_nodes in enumerate(communities_raw):
        if len(comm_nodes) >= self.min_community_size:
            community = Community(
                id=f"custom-comm-{i}",
                name=f"Community {i+1}",
                members=list(comm_nodes),
                member_count=len(comm_nodes)
            )
            communities.append(community)

    return communities
```

---

**Cause 1.2: Neo4j Connection Issue**

**Problem:** GraphitiService cannot connect to Neo4j

**Solution:**

```bash
# Verify Neo4j running
docker ps | grep neo4j

# Expected: neo4j container running on port 7687

# Test connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'apexmemory2024'))
driver.verify_connectivity()
print('✅ Neo4j connection OK')
"
```

---

**Cause 1.3: `update_communities=False` in GraphitiService**

**Problem:** Community updates disabled

**Solution:**

```python
# graphiti_service.py:146
# Change from:
update_communities=False  # Disabled

# To:
update_communities=True  # ✅ ENABLED
```

---

**Cause 1.4: No Communities Exist Yet**

**Problem:** Communities haven't been created (first-time setup)

**Solution:**

```bash
# Trigger community detection manually
python -c "
import asyncio
from apex_memory.services.graphiti_service import GraphitiService

async def create_communities():
    service = GraphitiService(
        neo4j_uri='bolt://localhost:7687',
        neo4j_user='neo4j',
        neo4j_password='apexmemory2024'
    )

    # Add test episodes to trigger community creation
    await service.add_document_episode(
        document_uuid='test-001',
        document_title='Test Document',
        document_content='CAT 950 Loader used for construction work',
        document_type='test',
        update_communities=True  # Force community update
    )

    print('✅ Community detection triggered')
    await service.close()

asyncio.run(create_communities())
"
```

---

## Issue 2: Query Explanations Are Generic/Low-Quality

### Symptom

```json
{
  "explanation": {
    "why_these_results": "Results were returned based on query analysis.",
    "confidence": 0.0,
    "alternative_queries": []
  }
}
```

### Root Causes

**Cause 2.1: Claude API Error**

**Problem:** Anthropic API key invalid or rate limit exceeded

**Solution:**

```bash
# Verify API key
export ANTHROPIC_API_KEY=sk-ant-...
python -c "
from anthropic import AsyncAnthropic
client = AsyncAnthropic()
print('✅ API key valid')
"

# Check rate limits
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"

# If rate limited, wait or upgrade plan
```

---

**Cause 2.2: Prompt Needs Tuning**

**Problem:** Claude prompt doesn't provide enough context

**Solution:**

Enhance prompt in `query_explainer.py`:

```python
# BEFORE (generic):
prompt = f"Explain why these results were returned for: {query}"

# AFTER (detailed):
prompt = f"""You are a knowledge graph query explainer helping users understand search results.

User Query: "{query}"

System Analysis:
- Intent: {intent} (confidence: {confidence:.0%})
- Databases Queried: {', '.join(databases)}
- Result Count: {len(results)}
- Sample Results:
  {self._format_sample_results(results[:5])}

Your task:
1. Explain in 2-3 sentences WHY these specific results were chosen
2. List 3-5 reasoning steps the system used (be specific)
3. Suggest 3 alternative queries that might also be helpful

Be concrete and specific. Reference actual entity names from results.

Format as JSON:
{{
  "why_these_results": "...",
  "reasoning_steps": ["step 1", "step 2", ...],
  "alternative_queries": ["query 1", "query 2", "query 3"]
}}"""
```

---

**Cause 2.3: Temperature Too High**

**Problem:** Claude responses too creative/variable

**Solution:**

```python
# query_explainer.py
response = await self.anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",
    temperature=0.3,  # CHANGE: 0.7 → 0.3 (more deterministic)
    max_tokens=500
)
```

---

## Issue 3: Pattern Prediction Accuracy <85%

### Symptom

```python
patterns = await temporal_analytics.predict_patterns(...)
accuracy = calculate_accuracy(patterns)
print(accuracy)  # Output: 0.67 (expected: >0.85)
```

### Root Causes

**Cause 3.1: Insufficient Historical Data**

**Problem:** Not enough data points for reliable pattern prediction

**Solution:**

```python
# temporal_analytics.py - Add data validation

async def predict_patterns(self, entity_type, property_name, lookback_days=90):
    # Fetch historical data
    data_points = await self._fetch_historical_data(entity_type, property_name, lookback_days)

    # Validate minimum data points
    MIN_DATA_POINTS = 30
    if len(data_points) < MIN_DATA_POINTS:
        logger.warning(
            f"Insufficient data for pattern prediction: "
            f"{len(data_points)} points (minimum: {MIN_DATA_POINTS})"
        )
        return []  # Return empty - don't make unreliable predictions

    # Continue with pattern analysis...
```

---

**Cause 3.2: Incorrect Time Window**

**Problem:** Time window too short/long for meaningful patterns

**Solution:**

```python
# Adjust lookback window based on entity type
OPTIMAL_WINDOWS = {
    "Equipment": 90,  # 3 months for equipment patterns
    "Vehicle": 180,   # 6 months for vehicle patterns
    "Shipment": 30    # 1 month for shipment patterns
}

lookback_days = OPTIMAL_WINDOWS.get(entity_type, 90)  # Default 90 days
```

---

**Cause 3.3: Seasonal Patterns Not Detected**

**Problem:** Scikit-learn model doesn't account for seasonality

**Solution:**

```python
# Use seasonal decomposition
from statsmodels.tsa.seasonal import seasonal_decompose

async def predict_patterns(self, entity_type, property_name, lookback_days=90):
    data_points = await self._fetch_historical_data(...)

    # Seasonal decomposition
    decomposition = seasonal_decompose(
        data_points,
        model='additive',
        period=30  # Monthly seasonality
    )

    # Detect seasonal patterns
    if decomposition.seasonal.std() > decomposition.resid.std():
        pattern = Pattern(
            pattern="Seasonal pattern detected with 30-day cycle",
            confidence=0.85,
            type="seasonal"
        )
        return [pattern]
```

---

## Issue 4: Performance Degradation (>2s for Communities)

### Symptom

```bash
# Community query latency
pytest tests/performance/test_community_performance.py -v

# Output: Community detection: 3200ms (expected: <2000ms)
```

### Root Causes

**Cause 4.1: Cache Disabled**

**Problem:** Community summaries re-generated every query

**Solution:**

Enable caching in `community_manager.py`:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CommunityManager:
    def __init__(self, ...):
        self.summary_cache = {}  # Cache summaries
        self.cache_ttl = 3600  # 1 hour

    async def generate_community_summary(self, community_id, members):
        # Check cache
        if community_id in self.summary_cache:
            cached_entry = self.summary_cache[community_id]
            if datetime.now() - cached_entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                logger.info(f"Using cached summary for {community_id}")
                return cached_entry['summary']

        # Generate summary
        summary = await self._generate_summary_llm(community_id, members)

        # Cache result
        self.summary_cache[community_id] = {
            'summary': summary,
            'timestamp': datetime.now()
        }

        return summary
```

---

**Cause 4.2: Too Many Communities**

**Problem:** 100+ communities being processed every query

**Solution:**

Increase minimum community size:

```python
# router.py
community_manager = CommunityManager(
    min_community_size=5  # CHANGE: 3 → 5 (reduce community count)
)
```

---

**Cause 4.3: GPT-5 API Latency**

**Problem:** GPT-5 summary generation slow (>1s per summary)

**Solution:**

Batch summary generation with async:

```python
async def generate_all_summaries(self, communities):
    # Generate summaries in parallel (max 5 concurrent)
    from asyncio import Semaphore

    semaphore = Semaphore(5)  # Limit concurrent API calls

    async def generate_with_limit(community):
        async with semaphore:
            return await self.generate_community_summary(community.id, ...)

    # Run in parallel
    summaries = await asyncio.gather(*[
        generate_with_limit(c) for c in communities
    ])

    return summaries
```

---

## Issue 5: Tests Failing After Upgrade

### Symptom

```bash
pytest tests/unit/test_community_detection.py -v

# Output: ImportError: cannot import name 'CommunityManager'
```

### Root Causes

**Cause 5.1: Missing Dependencies**

**Problem:** NetworkX or scikit-learn not installed

**Solution:**

```bash
# Install missing dependencies
pip install networkx scikit-learn

# Verify installation
python -c "import networkx; import sklearn; print('✅ Dependencies installed')"
```

---

**Cause 5.2: Import Path Incorrect**

**Problem:** Module path changed during implementation

**Solution:**

Update imports:

```python
# BEFORE:
from apex_memory.query_router.community import CommunityManager

# AFTER:
from apex_memory.query_router.community_manager import CommunityManager
```

---

**Cause 5.3: Fixture Conflicts**

**Problem:** Test fixtures incompatible with new code

**Solution:**

Update test fixtures in `conftest.py`:

```python
# tests/conftest.py

@pytest.fixture
def mock_graphiti_service():
    """Mock GraphitiService with community detection support."""
    service = AsyncMock()

    # Add community detection methods
    service.get_all_communities = AsyncMock(return_value=[
        {'community_id': 'c-001', 'name': 'Test', 'member_count': 5}
    ])

    service.client.driver.execute_query = AsyncMock(return_value=(
        [{'uuid': 'e-001', 'name': 'Entity', 'type': 'Equipment'}],
        None,
        None
    ))

    return service
```

---

## Issue 6: Graph Analytics Not Finding Paths

### Symptom

```python
path = await graph_analytics.find_shortest_path(from_uuid="e-001", to_uuid="e-002")
print(path)  # Output: None (expected: ShortestPath object)
```

### Root Causes

**Cause 6.1: Entities Not Connected**

**Problem:** No relationship path exists between entities

**Solution:**

Verify entities are connected:

```cypher
// Check if path exists
MATCH path = shortestPath(
  (e1:Entity {uuid: "e-001"})-[*]-(e2:Entity {uuid: "e-002"})
)
RETURN length(path) as path_length

// If null, entities not connected
```

---

**Cause 6.2: Max Hops Too Low**

**Problem:** Path exists but exceeds max_hops limit

**Solution:**

```python
# Increase max_hops
path = await graph_analytics.find_shortest_path(
    from_uuid="e-001",
    to_uuid="e-002",
    max_hops=10  # CHANGE: 5 → 10
)
```

---

## Debugging Tools

### Tool 1: Enable Debug Logging

```python
# Set log level to DEBUG
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("apex_memory")
logger.setLevel(logging.DEBUG)
```

---

### Tool 2: Query Neo4j Directly

```cypher
// Check community count
MATCH (c:Community) RETURN count(c) as community_count;

// Check entities in communities
MATCH (c:Community)-[:HAS_MEMBER]->(e:Entity)
RETURN c.name, count(e) as member_count
ORDER BY member_count DESC;

// Check temporal data
MATCH (e:Entity)-[r:TEMPORAL_EDGE]->(state:EntityState)
RETURN e.name, state.valid_from, state.properties
ORDER BY state.valid_from DESC
LIMIT 10;
```

---

### Tool 3: Profile Performance

```python
import time

async def profile_query():
    timings = {}

    # Community detection
    start = time.time()
    communities = await community_manager.detect_communities()
    timings['community_detection'] = (time.time() - start) * 1000

    # Summary generation
    start = time.time()
    await community_manager.generate_all_summaries(communities)
    timings['summary_generation'] = (time.time() - start) * 1000

    # Query explanation
    start = time.time()
    explanation = await query_explainer.explain_results(...)
    timings['explanation'] = (time.time() - start) * 1000

    print("Performance Profile:")
    for operation, ms in timings.items():
        print(f"  {operation}: {ms:.0f}ms")
```

---

## Getting Help

**If issue persists:**

1. **Check logs:** `tail -f apex-memory-system/logs/apex.log`
2. **Run diagnostics:** `python scripts/diagnose_query_router.py`
3. **Review research docs:** `upgrades/active/query-router-enhancements/research/`
4. **Search existing issues:** GitHub Issues with label `query-router`
5. **Create new issue:** Include logs, error messages, reproduction steps

---

**End of Troubleshooting Guide**

**Status:** Common issues documented with solutions
**Next Step:** Begin implementation following IMPLEMENTATION.md
