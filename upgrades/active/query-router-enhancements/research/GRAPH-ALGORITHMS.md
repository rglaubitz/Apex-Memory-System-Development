# Graph Algorithms - Technical Reference

**Document:** Centrality Metrics, Shortest Paths, and Graph Analytics
**Audience:** Developers implementing graph analytics features
**Sources:** NetworkX, Neo4j Graph Algorithms, graph theory research

---

## Overview

**Graph algorithms** enable advanced analytics on knowledge graphs by measuring entity importance, finding connections, and extracting meaningful subgraphs.

**Key Capabilities:**
- **Centrality Metrics:** Identify most important entities (PageRank, betweenness, degree)
- **Shortest Paths:** Find optimal connections between entities
- **Subgraph Extraction:** Extract relevant portions of the graph
- **Community Detection:** Cluster densely connected entities (see GRAPHITI-COMMUNITY-DETECTION.md)

**Use Cases:**
- "Which equipment is most critical in the knowledge graph?"
- "What is the shortest path between CAT loaders and shipment delays?"
- "Extract all entities related to heavy equipment maintenance"

---

## Centrality Metrics

### 1. PageRank

**Concept:** Measures entity importance based on incoming relationships (inspired by Google's algorithm)

**Interpretation:**
- High PageRank → Entity referenced by many other important entities
- Low PageRank → Entity isolated or referenced by unimportant entities

**Formula:**
```
PR(A) = (1-d) + d * Σ(PR(Ti) / C(Ti))

Where:
- PR(A) = PageRank of entity A
- d = damping factor (0.85 default)
- Ti = entities linking to A
- C(Ti) = outgoing link count from Ti
```

**Implementation (NetworkX):**
```python
import networkx as nx

async def calculate_pagerank(
    entity_type: Optional[str] = None,
    damping: float = 0.85
) -> Dict[str, float]:
    """Calculate PageRank centrality for entities."""
    # 1. Fetch graph from Neo4j
    query = """
    MATCH (e1:Entity)-[r]->(e2:Entity)
    """

    if entity_type:
        query += " WHERE e1.entity_type = $entity_type"

    query += """
    RETURN e1.uuid as source, e2.uuid as target, e1.name as source_name
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        entity_type=entity_type if entity_type else None
    )

    # 2. Build NetworkX graph
    G = nx.DiGraph()  # Directed graph (relationships have direction)

    entity_names = {}  # Map UUID -> name

    for record in results:
        source = record["source"]
        target = record["target"]
        source_name = record.get("source_name", source)

        G.add_edge(source, target)
        entity_names[source] = source_name

    # 3. Calculate PageRank
    pagerank_scores = nx.pagerank(G, alpha=damping)

    # 4. Format results with entity names
    results_formatted = {}
    for uuid, score in pagerank_scores.items():
        entity_name = entity_names.get(uuid, uuid)
        results_formatted[entity_name] = score

    # 5. Sort by importance
    sorted_results = dict(
        sorted(results_formatted.items(), key=lambda x: x[1], reverse=True)
    )

    return sorted_results
```

**Example Output:**
```python
{
    "CAT 950 Loader": 0.0452,  # Most important
    "Equipment Maintenance": 0.0398,
    "Heavy Equipment Community": 0.0287,
    "John Deere Tractor": 0.0143,
    ...
}
```

---

### 2. Betweenness Centrality

**Concept:** Measures how often an entity lies on the shortest path between other entities

**Interpretation:**
- High betweenness → Entity is a "bridge" connecting different parts of graph
- Low betweenness → Entity is peripheral or redundant

**Use Case:** "Which entities are critical connectors in the knowledge graph?"

**Implementation:**
```python
async def calculate_betweenness_centrality(
    entity_type: Optional[str] = None,
    normalized: bool = True
) -> Dict[str, float]:
    """Calculate betweenness centrality."""
    # 1. Fetch graph
    query = """
    MATCH (e1:Entity)-[r]-(e2:Entity)
    """

    if entity_type:
        query += " WHERE e1.entity_type = $entity_type"

    query += """
    RETURN DISTINCT e1.uuid as source, e2.uuid as target, e1.name as source_name
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        entity_type=entity_type if entity_type else None
    )

    # 2. Build undirected graph (betweenness ignores direction)
    G = nx.Graph()
    entity_names = {}

    for record in results:
        source = record["source"]
        target = record["target"]
        source_name = record.get("source_name", source)

        G.add_edge(source, target)
        entity_names[source] = source_name

    # 3. Calculate betweenness
    betweenness_scores = nx.betweenness_centrality(G, normalized=normalized)

    # 4. Format results
    results_formatted = {
        entity_names.get(uuid, uuid): score
        for uuid, score in betweenness_scores.items()
    }

    # 5. Sort by importance
    sorted_results = dict(
        sorted(results_formatted.items(), key=lambda x: x[1], reverse=True)
    )

    return sorted_results
```

**Example Output:**
```python
{
    "Equipment Maintenance": 0.342,  # Critical bridge entity
    "CAT 950 Loader": 0.198,
    "Shipment Delays": 0.157,
    ...
}
```

---

### 3. Degree Centrality

**Concept:** Measures number of direct connections an entity has

**Types:**
- **In-Degree:** Incoming relationships (entity is referenced by others)
- **Out-Degree:** Outgoing relationships (entity references others)
- **Total Degree:** Sum of in-degree + out-degree

**Implementation:**
```python
async def calculate_degree_centrality(
    entity_type: Optional[str] = None,
    direction: str = "total"  # "in" | "out" | "total"
) -> Dict[str, int]:
    """Calculate degree centrality."""
    # 1. Fetch graph
    if direction == "in":
        query = """
        MATCH (e1:Entity)<-[r]-(e2:Entity)
        """
    elif direction == "out":
        query = """
        MATCH (e1:Entity)-[r]->(e2:Entity)
        """
    else:  # total
        query = """
        MATCH (e1:Entity)-[r]-(e2:Entity)
        """

    if entity_type:
        query += " WHERE e1.entity_type = $entity_type"

    query += """
    RETURN e1.uuid as entity_id, e1.name as entity_name, count(r) as degree
    ORDER BY degree DESC
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        entity_type=entity_type if entity_type else None
    )

    # 2. Format results
    degree_scores = {
        record["entity_name"]: record["degree"]
        for record in results
    }

    return degree_scores
```

---

## Shortest Path Algorithms

### 1. Single Shortest Path

**Purpose:** Find the shortest path between two specific entities

**Algorithm:** Dijkstra's algorithm (Neo4j `shortestPath`)

**Implementation:**
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ShortestPath:
    source: str
    target: str
    nodes: List[str]  # Entity UUIDs along path
    relationships: List[str]  # Relationship types along path
    length: int  # Number of hops

async def find_shortest_path(
    from_uuid: str,
    to_uuid: str,
    max_hops: int = 10,
    relationship_types: Optional[List[str]] = None
) -> Optional[ShortestPath]:
    """Find shortest path between two entities."""
    # Build query
    rel_filter = ""
    if relationship_types:
        rel_types_str = "|".join(relationship_types)
        rel_filter = f":{rel_types_str}"

    query = f"""
    MATCH (start:Entity {{uuid: $from_uuid}})
    MATCH (end:Entity {{uuid: $to_uuid}})
    MATCH path = shortestPath((start)-[{rel_filter}*1..$max_hops]-(end))
    RETURN
        nodes(path) as nodes_list,
        relationships(path) as rels_list,
        length(path) as path_length
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        from_uuid=from_uuid,
        to_uuid=to_uuid,
        max_hops=max_hops
    )

    if not results:
        return None  # No path found

    record = results[0]

    # Extract node UUIDs
    nodes = [node["uuid"] for node in record["nodes_list"]]

    # Extract relationship types
    relationships = [rel.type for rel in record["rels_list"]]

    return ShortestPath(
        source=from_uuid,
        target=to_uuid,
        nodes=nodes,
        relationships=relationships,
        length=record["path_length"]
    )
```

**Example Output:**
```python
ShortestPath(
    source="e-001",  # CAT 950 Loader
    target="e-042",  # Shipment Delays
    nodes=["e-001", "e-015", "e-023", "e-042"],
    relationships=["USED_IN", "CAUSED", "RESULTED_IN"],
    length=3  # 3 hops
)
```

---

### 2. All Shortest Paths

**Purpose:** Find all shortest paths (useful when multiple paths exist with same length)

**Implementation:**
```python
async def find_all_shortest_paths(
    from_uuid: str,
    to_uuid: str,
    max_hops: int = 10
) -> List[ShortestPath]:
    """Find all shortest paths between two entities."""
    query = """
    MATCH (start:Entity {uuid: $from_uuid})
    MATCH (end:Entity {uuid: $to_uuid})
    MATCH paths = allShortestPaths((start)-[*1..$max_hops]-(end))
    RETURN
        [n IN nodes(paths) | n.uuid] as nodes_list,
        [r IN relationships(paths) | type(r)] as rels_list,
        length(paths) as path_length
    LIMIT 10  # Prevent explosion of results
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        from_uuid=from_uuid,
        to_uuid=to_uuid,
        max_hops=max_hops
    )

    paths = []
    for record in results:
        paths.append(ShortestPath(
            source=from_uuid,
            target=to_uuid,
            nodes=record["nodes_list"],
            relationships=record["rels_list"],
            length=record["path_length"]
        ))

    return paths
```

---

## Subgraph Extraction

### 1. Entity-Centered Subgraph

**Purpose:** Extract all entities within N hops of a seed entity

**Implementation:**
```python
@dataclass
class Subgraph:
    nodes: List[Dict]  # Entities
    edges: List[Dict]  # Relationships
    center_node: str   # Seed entity UUID

async def extract_subgraph(
    center_uuid: str,
    max_depth: int = 2,
    max_nodes: int = 100
) -> Subgraph:
    """Extract subgraph centered on entity."""
    query = """
    MATCH path = (center:Entity {uuid: $center_uuid})-[*1..$max_depth]-(related:Entity)
    WITH center, related, relationships(path) as rels

    // Limit to prevent explosion
    WITH center, collect(DISTINCT related)[0..$max_nodes] as related_nodes,
         collect(DISTINCT rels) as all_rels

    UNWIND related_nodes as related
    OPTIONAL MATCH (center)-[r]-(related)

    RETURN
        collect(DISTINCT {
            uuid: related.uuid,
            name: related.name,
            type: related.entity_type,
            summary: related.summary
        }) as nodes,
        collect(DISTINCT {
            source: startNode(r).uuid,
            target: endNode(r).uuid,
            type: type(r)
        }) as edges
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        center_uuid=center_uuid,
        max_depth=max_depth,
        max_nodes=max_nodes
    )

    if not results:
        return Subgraph(nodes=[], edges=[], center_node=center_uuid)

    record = results[0]

    return Subgraph(
        nodes=record["nodes"],
        edges=record["edges"],
        center_node=center_uuid
    )
```

---

### 2. Type-Filtered Subgraph

**Purpose:** Extract subgraph containing only specific entity types

**Implementation:**
```python
async def extract_typed_subgraph(
    entity_types: List[str],
    max_nodes: int = 100
) -> Subgraph:
    """Extract subgraph containing only specified entity types."""
    query = """
    MATCH (e1:Entity)-[r]-(e2:Entity)
    WHERE e1.entity_type IN $entity_types AND e2.entity_type IN $entity_types
    WITH e1, e2, r
    LIMIT $max_nodes

    RETURN
        collect(DISTINCT {
            uuid: e1.uuid,
            name: e1.name,
            type: e1.entity_type,
            summary: e1.summary
        }) + collect(DISTINCT {
            uuid: e2.uuid,
            name: e2.name,
            type: e2.entity_type,
            summary: e2.summary
        }) as nodes,
        collect({
            source: startNode(r).uuid,
            target: endNode(r).uuid,
            type: type(r)
        }) as edges
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        entity_types=entity_types,
        max_nodes=max_nodes
    )

    if not results:
        return Subgraph(nodes=[], edges=[], center_node="")

    record = results[0]

    return Subgraph(
        nodes=record["nodes"],
        edges=record["edges"],
        center_node=""  # No single center
    )
```

---

## Performance Optimization

### 1. Cypher Query Optimization

**Problem:** Large graph traversals are expensive

**Solution 1: Limit Max Hops**
```cypher
// Inefficient (unbounded depth)
MATCH path = (e1)-[*]-(e2)
RETURN path

// Efficient (bounded depth)
MATCH path = (e1)-[*1..3]-(e2)  // Max 3 hops
RETURN path
```

**Solution 2: Early Termination**
```cypher
// Stop at first N results
MATCH path = (e1)-[*1..5]-(e2)
RETURN path
LIMIT 100  // Stop after 100 paths
```

**Solution 3: Index Usage**
```cypher
// Create indexes for fast lookup
CREATE INDEX entity_uuid FOR (e:Entity) ON (e.uuid);
CREATE INDEX entity_type FOR (e:Entity) ON (e.entity_type);

// Use indexed properties in WHERE clauses
MATCH (e:Entity {uuid: $uuid})  // Uses index ✅
```

---

### 2. NetworkX Optimization

**Problem:** Converting large Neo4j graphs to NetworkX is slow

**Solution: Paginated Conversion**
```python
async def build_networkx_graph_paginated(
    entity_type: Optional[str] = None,
    page_size: int = 1000
) -> nx.Graph:
    """Build NetworkX graph with pagination."""
    G = nx.Graph()

    skip = 0
    while True:
        query = """
        MATCH (e1:Entity)-[r]-(e2:Entity)
        """

        if entity_type:
            query += " WHERE e1.entity_type = $entity_type"

        query += """
        RETURN e1.uuid as source, e2.uuid as target
        SKIP $skip
        LIMIT $page_size
        """

        results, _, _ = await graphiti.client.driver.execute_query(
            query,
            entity_type=entity_type if entity_type else None,
            skip=skip,
            page_size=page_size
        )

        if not results:
            break  # No more results

        # Add edges to graph
        for record in results:
            G.add_edge(record["source"], record["target"])

        skip += page_size

        # Progress logging
        logger.info(f"Loaded {skip} edges into NetworkX graph")

    return G
```

---

### 3. Caching Centrality Metrics

**Problem:** Centrality calculations are expensive (O(n²) to O(n³))

**Solution:**
```python
class GraphAnalytics:
    def __init__(self, cache_ttl: int = 3600):
        self.centrality_cache = {}
        self.cache_ttl = cache_ttl

    async def calculate_centrality(
        self,
        metric: str = "pagerank",  # "pagerank" | "betweenness" | "degree"
        entity_type: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, float]:
        """Calculate centrality with caching."""
        cache_key = f"{metric}:{entity_type or 'all'}"

        # Check cache
        if not force_refresh and cache_key in self.centrality_cache:
            cached = self.centrality_cache[cache_key]
            if datetime.now() - cached["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached["scores"]

        # Calculate centrality
        if metric == "pagerank":
            scores = await calculate_pagerank(entity_type)
        elif metric == "betweenness":
            scores = await calculate_betweenness_centrality(entity_type)
        else:  # degree
            scores = await calculate_degree_centrality(entity_type)

        # Cache result
        self.centrality_cache[cache_key] = {
            "scores": scores,
            "timestamp": datetime.now()
        }

        return scores
```

**Performance Impact:**
- Without cache: 500-2000ms centrality calculation
- With cache: <10ms cache hit
- **Speedup:** 50-200x ✅

---

## Advanced Algorithms

### 1. Graph Diameter

**Purpose:** Maximum shortest path length in graph (measures graph "size")

**Implementation:**
```python
async def calculate_graph_diameter(entity_type: Optional[str] = None) -> int:
    """Calculate graph diameter."""
    # Build NetworkX graph
    G = await build_networkx_graph_paginated(entity_type)

    # Calculate diameter (expensive for large graphs)
    if nx.is_connected(G):
        diameter = nx.diameter(G)
    else:
        # For disconnected graphs, find largest component
        largest_cc = max(nx.connected_components(G), key=len)
        subgraph = G.subgraph(largest_cc)
        diameter = nx.diameter(subgraph)

    return diameter
```

---

### 2. Connected Components

**Purpose:** Identify disconnected clusters in graph

**Implementation:**
```python
async def find_connected_components(
    entity_type: Optional[str] = None
) -> List[List[str]]:
    """Find connected components (disconnected clusters)."""
    # Build NetworkX graph
    G = await build_networkx_graph_paginated(entity_type)

    # Find connected components
    components = list(nx.connected_components(G))

    # Sort by size (largest first)
    components.sort(key=len, reverse=True)

    return [list(component) for component in components]
```

**Example Output:**
```python
[
    ["e-001", "e-002", "e-003", ...],  # Large connected component (95% of graph)
    ["e-500", "e-501"],                 # Small isolated cluster
    ["e-800"]                           # Isolated entity
]
```

---

### 3. Graph Density

**Purpose:** Measure how connected the graph is

**Formula:**
```
Density = (2 * E) / (N * (N - 1))

Where:
- E = number of edges
- N = number of nodes
```

**Interpretation:**
- Density = 1.0 → Fully connected (every entity connected to every other)
- Density = 0.0 → No connections
- Typical knowledge graphs: 0.01-0.1 (sparse)

**Implementation:**
```python
async def calculate_graph_density(entity_type: Optional[str] = None) -> float:
    """Calculate graph density."""
    # Count nodes and edges
    query = """
    MATCH (e:Entity)
    """

    if entity_type:
        query += " WHERE e.entity_type = $entity_type"

    query += """
    WITH count(e) as node_count
    MATCH ()-[r]->()
    """

    if entity_type:
        query += " WHERE startNode(r).entity_type = $entity_type"

    query += """
    RETURN node_count, count(r) as edge_count
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        entity_type=entity_type if entity_type else None
    )

    record = results[0]
    N = record["node_count"]
    E = record["edge_count"]

    if N <= 1:
        return 0.0

    density = (2 * E) / (N * (N - 1))

    return density
```

---

## Example Integration

### Complete Graph Analytics Manager

```python
from typing import List, Dict, Optional
import networkx as nx
from datetime import datetime, timedelta

class GraphAnalyticsManager:
    """Production-ready graph analytics."""

    def __init__(self, graphiti_service):
        self.graphiti = graphiti_service
        self.centrality_cache = {}
        self.cache_ttl = 3600

    async def calculate_centrality(
        self,
        metric: str = "pagerank",
        entity_type: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, float]:
        """Calculate centrality metrics with caching."""
        cache_key = f"{metric}:{entity_type or 'all'}"

        # Check cache
        if not force_refresh and cache_key in self.centrality_cache:
            cached = self.centrality_cache[cache_key]
            if datetime.now() - cached["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached["scores"]

        # Calculate
        if metric == "pagerank":
            scores = await self._calculate_pagerank(entity_type)
        elif metric == "betweenness":
            scores = await self._calculate_betweenness(entity_type)
        else:
            scores = await self._calculate_degree(entity_type)

        # Cache
        self.centrality_cache[cache_key] = {
            "scores": scores,
            "timestamp": datetime.now()
        }

        return scores

    async def find_shortest_path(
        self,
        from_uuid: str,
        to_uuid: str,
        max_hops: int = 10
    ) -> Optional[ShortestPath]:
        """Find shortest path between two entities."""
        query = """
        MATCH (start:Entity {uuid: $from_uuid})
        MATCH (end:Entity {uuid: $to_uuid})
        MATCH path = shortestPath((start)-[*1..$max_hops]-(end))
        RETURN
            [n IN nodes(path) | n.uuid] as nodes_list,
            [r IN relationships(path) | type(r)] as rels_list,
            length(path) as path_length
        """

        results, _, _ = await self.graphiti.client.driver.execute_query(
            query,
            from_uuid=from_uuid,
            to_uuid=to_uuid,
            max_hops=max_hops
        )

        if not results:
            return None

        record = results[0]

        return ShortestPath(
            source=from_uuid,
            target=to_uuid,
            nodes=record["nodes_list"],
            relationships=record["rels_list"],
            length=record["path_length"]
        )

    async def extract_subgraph(
        self,
        center_uuid: str,
        max_depth: int = 2,
        max_nodes: int = 100
    ) -> Subgraph:
        """Extract entity-centered subgraph."""
        query = """
        MATCH path = (center:Entity {uuid: $center_uuid})-[*1..$max_depth]-(related:Entity)
        WITH collect(DISTINCT related)[0..$max_nodes] as related_nodes, center

        UNWIND related_nodes as related
        OPTIONAL MATCH (center)-[r]-(related)

        RETURN
            collect(DISTINCT {
                uuid: related.uuid,
                name: related.name,
                type: related.entity_type
            }) as nodes,
            collect(DISTINCT {
                source: startNode(r).uuid,
                target: endNode(r).uuid,
                type: type(r)
            }) as edges
        """

        results, _, _ = await self.graphiti.client.driver.execute_query(
            query,
            center_uuid=center_uuid,
            max_depth=max_depth,
            max_nodes=max_nodes
        )

        if not results:
            return Subgraph(nodes=[], edges=[], center_node=center_uuid)

        record = results[0]

        return Subgraph(
            nodes=record["nodes"],
            edges=record["edges"],
            center_node=center_uuid
        )

    async def _calculate_pagerank(self, entity_type: Optional[str]) -> Dict[str, float]:
        """Calculate PageRank."""
        query = """
        MATCH (e1:Entity)-[r]->(e2:Entity)
        """

        if entity_type:
            query += " WHERE e1.entity_type = $entity_type"

        query += """
        RETURN e1.uuid as source, e2.uuid as target, e1.name as source_name
        """

        results, _, _ = await self.graphiti.client.driver.execute_query(
            query,
            entity_type=entity_type if entity_type else None
        )

        # Build NetworkX graph
        G = nx.DiGraph()
        entity_names = {}

        for record in results:
            source = record["source"]
            target = record["target"]
            source_name = record.get("source_name", source)

            G.add_edge(source, target)
            entity_names[source] = source_name

        # Calculate PageRank
        pagerank_scores = nx.pagerank(G)

        # Format
        results_formatted = {
            entity_names.get(uuid, uuid): score
            for uuid, score in pagerank_scores.items()
        }

        return dict(sorted(results_formatted.items(), key=lambda x: x[1], reverse=True))

    async def _calculate_betweenness(self, entity_type: Optional[str]) -> Dict[str, float]:
        """Calculate betweenness centrality."""
        query = """
        MATCH (e1:Entity)-[r]-(e2:Entity)
        """

        if entity_type:
            query += " WHERE e1.entity_type = $entity_type"

        query += """
        RETURN DISTINCT e1.uuid as source, e2.uuid as target, e1.name as source_name
        """

        results, _, _ = await self.graphiti.client.driver.execute_query(
            query,
            entity_type=entity_type if entity_type else None
        )

        # Build undirected graph
        G = nx.Graph()
        entity_names = {}

        for record in results:
            source = record["source"]
            target = record["target"]
            source_name = record.get("source_name", source)

            G.add_edge(source, target)
            entity_names[source] = source_name

        # Calculate betweenness
        betweenness_scores = nx.betweenness_centrality(G)

        # Format
        results_formatted = {
            entity_names.get(uuid, uuid): score
            for uuid, score in betweenness_scores.items()
        }

        return dict(sorted(results_formatted.items(), key=lambda x: x[1], reverse=True))

    async def _calculate_degree(self, entity_type: Optional[str]) -> Dict[str, int]:
        """Calculate degree centrality."""
        query = """
        MATCH (e1:Entity)-[r]-(e2:Entity)
        """

        if entity_type:
            query += " WHERE e1.entity_type = $entity_type"

        query += """
        RETURN e1.uuid as entity_id, e1.name as entity_name, count(r) as degree
        ORDER BY degree DESC
        """

        results, _, _ = await self.graphiti.client.driver.execute_query(
            query,
            entity_type=entity_type if entity_type else None
        )

        return {
            record["entity_name"]: record["degree"]
            for record in results
        }
```

---

## References

**Official Documentation:**
- NetworkX Algorithms: https://networkx.org/documentation/stable/reference/algorithms/
- Neo4j Graph Algorithms: https://neo4j.com/docs/graph-data-science/current/algorithms/
- Graph Theory: https://en.wikipedia.org/wiki/Graph_theory

**Research Papers:**
- "The PageRank Citation Ranking" (Page et al., 1999)
- "A Set of Measures of Centrality Based on Betweenness" (Freeman, 1977)

**Code Examples:**
- NetworkX Centrality: https://networkx.org/documentation/stable/reference/algorithms/centrality.html
- Neo4j Shortest Path: https://neo4j.com/docs/cypher-manual/current/clauses/match/#shortest-path

---

**End of Technical Reference**

**Status:** Complete graph algorithms implementation guide
**Next:** Apply these algorithms in query-router-enhancements implementation
