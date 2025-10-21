# Graphiti Community Detection - Technical Reference

**Document:** Official API Documentation and Implementation Guide
**Audience:** Developers implementing community detection features
**Sources:** graphiti-core 0.23.0+ documentation, Neo4j community algorithms

---

## Overview

**Community detection** is a graph algorithm that identifies groups of densely connected entities (nodes) in a knowledge graph. Graphiti provides built-in support for detecting and managing communities using Neo4j's graph algorithms.

**Key Capabilities:**
- Automatic community detection using Louvain algorithm
- Community summaries via LLM integration
- Hierarchical community structure
- Temporal community evolution tracking

---

## Graphiti Community API

### Core Methods

**1. Detect Communities**

```python
from graphiti_core import Graphiti

graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Detect communities in the graph
communities = await graphiti.get_all_communities(group_id="default")

# Returns list of Community objects:
# [
#   {
#     "community_id": "c-001",
#     "name": "Heavy Equipment",
#     "member_count": 12,
#     "members": ["e-uuid-1", "e-uuid-2", ...],
#     "summary": "Community focused on CAT loaders and excavators"
#   }
# ]
```

**2. Get Community Members**

```python
# Fetch entities in a specific community
query = """
MATCH (c:Community {uuid: $community_id})-[:HAS_MEMBER]->(e:Entity)
RETURN e.uuid as entity_id, e.name as entity_name, e.summary as entity_summary
"""

results, _, _ = await graphiti.client.driver.execute_query(
    query,
    community_id="c-001"
)

members = [
    {
        "entity_id": r["entity_id"],
        "name": r["entity_name"],
        "summary": r["entity_summary"]
    }
    for r in results
]
```

**3. Update Community Summaries**

```python
# Graphiti can auto-generate summaries when communities are updated
await graphiti.add_episode(
    name="Document ingestion",
    content="CAT 950 loader used for heavy construction",
    update_communities=True  # ✅ Enable community updates
)

# Community summary auto-generated via LLM
```

---

## Community Detection Algorithm

### Louvain Algorithm (Default)

**How it works:**
1. **Initialization:** Each node starts in its own community
2. **Modularity Optimization:** Iteratively move nodes to maximize modularity
3. **Community Aggregation:** Merge communities into meta-nodes
4. **Repeat:** Until modularity cannot be improved

**Modularity Formula:**
```
Q = (1/2m) * Σ[Aᵢⱼ - (kᵢ*kⱼ)/(2m)] * δ(cᵢ, cⱼ)

Where:
- Aᵢⱼ = adjacency matrix (1 if edge exists, 0 otherwise)
- kᵢ, kⱼ = degree of nodes i and j
- m = total number of edges
- δ(cᵢ, cⱼ) = 1 if nodes in same community, 0 otherwise
```

**Advantages:**
- Fast: O(n log n) time complexity
- Hierarchical: Produces multi-level community structure
- Proven: Used in social network analysis, biology, citation networks

---

## Configuration Options

### Minimum Community Size

**Problem:** Small communities (1-2 members) not useful

**Solution:**
```python
class CommunityManager:
    def __init__(
        self,
        graphiti_service,
        min_community_size: int = 3  # Filter out small communities
    ):
        self.min_community_size = min_community_size

    async def detect_communities(self):
        all_communities = await self.graphiti.get_all_communities()

        # Filter by size
        filtered = [
            c for c in all_communities
            if c.member_count >= self.min_community_size
        ]

        return filtered
```

**Recommended Values:**
- Development: `min_community_size=2` (see all communities)
- Production: `min_community_size=5` (meaningful communities only)

---

### Hierarchical Communities

**Concept:** Communities can be nested (meta-communities)

**Example:**
```
Heavy Equipment Community
├── CAT Equipment Sub-Community
│   ├── CAT 950 Loaders
│   └── CAT Excavators
└── John Deere Equipment Sub-Community
    ├── JD Tractors
    └── JD Harvesters
```

**Implementation:**
```python
class CommunityManager:
    def __init__(
        self,
        enable_hierarchical: bool = False  # Disabled by default (complex)
    ):
        self.enable_hierarchical = enable_hierarchical

    async def build_community_hierarchy(self, communities):
        """Group communities by entity type or domain."""
        if not self.enable_hierarchical:
            return {}

        hierarchy = {}
        for community in communities:
            # Extract primary entity type from summary
            primary_type = self._extract_primary_type(community.summary)

            if primary_type not in hierarchy:
                hierarchy[primary_type] = []

            hierarchy[primary_type].append(community.id)

        return hierarchy

    def _extract_primary_type(self, summary: str) -> str:
        """Extract entity type from LLM-generated summary."""
        # Example: "Equipment community with CAT loaders" -> "Equipment"
        if "equipment" in summary.lower():
            return "Equipment"
        elif "vehicle" in summary.lower():
            return "Vehicle"
        elif "shipment" in summary.lower():
            return "Shipment"
        else:
            return "General"
```

---

## LLM-Powered Community Summaries

### GPT-5 Integration

**Purpose:** Generate human-readable summaries describing what communities are about

**Example Input:**
```python
members = [
    {"name": "CAT 950 Loader", "type": "Equipment", "summary": "Heavy loader for construction"},
    {"name": "CAT 966 Loader", "type": "Equipment", "summary": "Medium loader for mining"},
    {"name": "CAT Excavator 320", "type": "Equipment", "summary": "Excavator for digging"}
]

prompt = f"""Analyze this community of entities and generate a concise summary.

Community Members ({len(members)} entities):
{', '.join([m['name'] for m in members[:20]])}  # Truncate to 20 for token efficiency

Entity Types: {set([m['type'] for m in members])}

Generate a 2-3 sentence summary describing:
1. What this community represents
2. Common characteristics across members
3. Primary domain or use case

Summary:"""
```

**Example Output:**
```
"This community represents heavy construction equipment manufactured by Caterpillar (CAT).
The entities are primarily loaders and excavators used in mining and construction operations.
Common characteristics include diesel engines, hydraulic systems, and high load capacity."
```

**API Call:**
```python
from openai import AsyncOpenAI

openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = await openai.chat.completions.create(
    model="gpt-5",  # Latest model for best summaries
    messages=[
        {"role": "system", "content": "You are a knowledge graph analyst."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3,  # Lower for consistency
    max_tokens=150
)

summary = response.choices[0].message.content
```

---

## Performance Considerations

### Community Detection Latency

**Baseline Performance (Neo4j Louvain):**
- Small graphs (<1k nodes): <100ms
- Medium graphs (1k-10k nodes): 100-500ms
- Large graphs (>10k nodes): 500-2000ms

**Optimization Strategies:**

**1. Caching:**
```python
from datetime import datetime, timedelta

class CommunityManager:
    def __init__(self):
        self.community_cache = {}
        self.cache_ttl = 3600  # 1 hour

    async def detect_communities(self, force_refresh: bool = False):
        cache_key = "all_communities"

        # Check cache
        if not force_refresh and cache_key in self.community_cache:
            cached_entry = self.community_cache[cache_key]
            if datetime.now() - cached_entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached_entry["communities"]

        # Fetch from Graphiti
        communities = await self.graphiti.get_all_communities()

        # Update cache
        self.community_cache[cache_key] = {
            "communities": communities,
            "timestamp": datetime.now()
        }

        return communities
```

**2. Incremental Updates:**
```python
# Instead of re-detecting all communities every query...
# Only update when new entities added:

await graphiti.add_episode(
    content="New document content",
    update_communities=True  # Only update when content changes
)
```

**3. Batch Summary Generation:**
```python
async def generate_all_summaries(self, communities):
    """Generate summaries for all communities in parallel."""
    from asyncio import Semaphore

    semaphore = Semaphore(5)  # Limit to 5 concurrent GPT-5 calls

    async def generate_with_limit(community):
        async with semaphore:
            return await self.generate_community_summary(community)

    # Run in parallel
    summaries = await asyncio.gather(*[
        generate_with_limit(c) for c in communities
    ])

    return summaries
```

---

## Common Issues and Solutions

### Issue 1: Community Detection Disabled

**Problem:**
```python
# graphiti_service.py:146
update_communities=False  # Disabled
```

**Root Cause:** graphiti-core 0.22.0 has a bug with `semaphore_gather` unpacking

**Solution 1: Upgrade to graphiti-core 0.23.0+**
```bash
pip install --upgrade graphiti-core
python -c "import graphiti_core; print(graphiti_core.__version__)"
# Expected: 0.23.0 or higher
```

**Solution 2: Custom Community Detection (NetworkX fallback)**
```python
import networkx as nx
import networkx.algorithms.community as nx_comm

async def detect_communities_custom(self):
    """Fallback community detection using NetworkX."""
    # Get all relationships from Neo4j
    query = """
    MATCH (e1:Entity)-[r]->(e2:Entity)
    RETURN e1.uuid as source, e2.uuid as target
    """

    records, _, _ = await self.graphiti.client.driver.execute_query(query)

    # Build NetworkX graph
    G = nx.Graph()
    for record in records:
        G.add_edge(record["source"], record["target"])

    # Louvain algorithm
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

### Issue 2: Empty Community List

**Problem:**
```python
communities = await community_manager.detect_communities()
print(len(communities))  # Output: 0 (expected: >0)
```

**Diagnosis:**
```cypher
// Check if communities exist in Neo4j
MATCH (c:Community {group_id: "default"})
RETURN count(c) as community_count;

// If 0, communities haven't been created yet
```

**Solution:**
```python
# Trigger community detection manually
await graphiti.add_episode(
    name="Community initialization",
    content="Sample document to trigger community creation",
    update_communities=True  # Force community update
)

# Verify communities created
communities = await graphiti.get_all_communities()
print(f"Detected {len(communities)} communities")
```

---

## Neo4j Cypher Queries

### Query 1: List All Communities

```cypher
MATCH (c:Community {group_id: "default"})
RETURN c.uuid as community_id, c.name as name, c.summary as summary
ORDER BY c.member_count DESC;
```

### Query 2: Get Community Members

```cypher
MATCH (c:Community {uuid: $community_id})-[:HAS_MEMBER]->(e:Entity)
RETURN e.uuid, e.name, e.entity_type, e.summary
ORDER BY e.created_at DESC;
```

### Query 3: Community Size Distribution

```cypher
MATCH (c:Community {group_id: "default"})
WITH c, size((c)-[:HAS_MEMBER]->()) as member_count
RETURN member_count, count(c) as num_communities
ORDER BY member_count DESC;
```

### Query 4: Find Communities for Specific Entity Type

```cypher
MATCH (c:Community)-[:HAS_MEMBER]->(e:Entity {entity_type: "Equipment"})
WITH c, count(e) as equipment_count
WHERE equipment_count >= 5
RETURN c.uuid, c.name, equipment_count
ORDER BY equipment_count DESC;
```

---

## Best Practices

### 1. Community Size Tuning

**Guideline:** Adjust `min_community_size` based on graph size

| Graph Size | Min Community Size | Rationale |
|------------|-------------------|-----------|
| <100 entities | 2 | Allow small communities |
| 100-1k entities | 3-5 | Balance granularity |
| 1k-10k entities | 5-10 | Avoid noise |
| >10k entities | 10-20 | Focus on major clusters |

### 2. Summary Quality

**DO:**
- ✅ Truncate member lists to 20 entities (avoid token waste)
- ✅ Include entity types in prompt for context
- ✅ Use low temperature (0.3) for consistency
- ✅ Cache summaries (communities change infrequently)

**DON'T:**
- ❌ Pass all members to LLM (expensive, unnecessary)
- ❌ Use high temperature (>0.7) - creates variable summaries
- ❌ Regenerate summaries every query (waste)

### 3. Cache Strategy

**When to cache:**
- Community detection results (TTL: 1 hour)
- Community summaries (TTL: 24 hours)

**When to invalidate:**
- After `add_episode()` with `update_communities=True`
- After manual community creation/deletion
- After graph schema changes

### 4. Incremental Updates

**Efficient:**
```python
# Only update communities when content changes
await graphiti.add_episode(
    content=new_document,
    update_communities=True  # ✅ Graphiti handles incremental update
)
```

**Inefficient:**
```python
# DON'T re-detect all communities from scratch every time
communities = await custom_louvain_detection()  # ❌ Expensive
```

---

## Example Integration

### Full Community Manager Implementation

```python
from graphiti_core import Graphiti
from openai import AsyncOpenAI
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Community:
    id: str
    name: str
    members: List[str]
    member_count: int
    summary: Optional[str] = None

class CommunityManager:
    """Production-ready community detection manager."""

    def __init__(
        self,
        graphiti_service: Graphiti,
        openai_client: AsyncOpenAI,
        min_community_size: int = 5,
        enable_hierarchical: bool = False,
        cache_ttl: int = 3600
    ):
        self.graphiti = graphiti_service
        self.openai = openai_client
        self.min_community_size = min_community_size
        self.enable_hierarchical = enable_hierarchical
        self.cache_ttl = cache_ttl

        # Caches
        self.community_cache = {}
        self.summary_cache = {}

    async def detect_communities(
        self,
        group_id: str = "default",
        force_refresh: bool = False
    ) -> List[Community]:
        """Detect communities with caching."""
        cache_key = f"communities_{group_id}"

        # Check cache
        if not force_refresh and cache_key in self.community_cache:
            cached = self.community_cache[cache_key]
            if datetime.now() - cached["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached["communities"]

        # Fetch from Graphiti
        all_communities = await self.graphiti.get_all_communities(group_id=group_id)

        # Filter by size
        filtered = [
            Community(
                id=c.uuid,
                name=c.name,
                members=await self._get_community_members(c.uuid),
                member_count=c.member_count,
                summary=c.summary
            )
            for c in all_communities
            if c.member_count >= self.min_community_size
        ]

        # Cache result
        self.community_cache[cache_key] = {
            "communities": filtered,
            "timestamp": datetime.now()
        }

        return filtered

    async def generate_community_summary(
        self,
        community_id: str,
        members: List[Dict]
    ) -> str:
        """Generate LLM-powered community summary."""
        # Check cache
        if community_id in self.summary_cache:
            cached = self.summary_cache[community_id]
            if datetime.now() - cached["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached["summary"]

        # Prepare prompt
        member_names = [m["name"] for m in members[:20]]  # Truncate to 20
        entity_types = set([m.get("entity_type", "Unknown") for m in members])

        prompt = f"""Analyze this community of entities and generate a concise summary.

Community ID: {community_id}
Members ({len(members)} entities): {", ".join(member_names)}
Entity Types: {", ".join(entity_types)}

Generate a 2-3 sentence summary describing what this community represents."""

        # Call GPT-5
        response = await self.openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a knowledge graph analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )

        summary = response.choices[0].message.content

        # Cache result
        self.summary_cache[community_id] = {
            "summary": summary,
            "timestamp": datetime.now()
        }

        return summary

    async def _get_community_members(self, community_id: str) -> List[str]:
        """Fetch community member UUIDs from Neo4j."""
        query = """
        MATCH (c:Community {uuid: $community_id})-[:HAS_MEMBER]->(e:Entity)
        RETURN e.uuid as member_id
        """

        records, _, _ = await self.graphiti.client.driver.execute_query(
            query,
            community_id=community_id
        )

        return [r["member_id"] for r in records]
```

---

## References

**Official Documentation:**
- Graphiti Community API: `graphiti-core` package documentation
- Neo4j Graph Algorithms: https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/
- Louvain Algorithm: https://en.wikipedia.org/wiki/Louvain_method

**Research Papers:**
- "Fast unfolding of communities in large networks" (Blondel et al., 2008)
- "Community detection in graphs" (Fortunato, 2010)

**Code Examples:**
- NetworkX Louvain: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain_communities.html
- Neo4j GDS Examples: https://github.com/neo4j/graph-data-science

---

**End of Technical Reference**

**Status:** Complete community detection API documentation
**Next:** See GRAPHRAG-IMPLEMENTATION.md for GraphRAG integration patterns
