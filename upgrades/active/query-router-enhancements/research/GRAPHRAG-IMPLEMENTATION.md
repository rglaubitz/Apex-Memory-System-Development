# GraphRAG Implementation - Technical Reference

**Document:** Graph Retrieval-Augmented Generation Patterns
**Audience:** Developers implementing GraphRAG features
**Sources:** Microsoft GraphRAG, Neo4j RAG patterns, LangChain graph integrations

---

## Overview

**GraphRAG** combines graph-based knowledge retrieval with LLM-powered generation to answer complex queries that require multi-hop reasoning across connected entities.

**Key Differences from Standard RAG:**

| Standard RAG | GraphRAG |
|-------------|----------|
| Retrieves isolated documents | Retrieves connected entity subgraphs |
| No relationship context | Preserves relationship semantics |
| Single-hop retrieval | Multi-hop graph traversal |
| Flat vector search | Hybrid graph + vector search |
| Limited reasoning | Community-aware reasoning |

**Use Cases:**
- "What patterns exist across all equipment maintenance issues?"
- "How are CAT loaders related to shipment delays?"
- "What communities of entities are involved in this query?"

---

## GraphRAG Architecture

### High-Level Flow

```
User Query
    ↓
1. Intent Classification (graph/temporal/semantic/hybrid)
    ↓
2. Community Detection (identify relevant entity clusters)
    ↓
3. Multi-Hop Retrieval (traverse graph from seed entities)
    ↓
4. Subgraph Extraction (build connected context)
    ↓
5. Community Summaries (aggregate LLM-generated insights)
    ↓
6. Context Construction (format for LLM)
    ↓
7. LLM Generation (Claude 3.5 Sonnet)
    ↓
Final Answer
```

---

## Core Components

### 1. Community-Based Retrieval

**Concept:** Use communities as contextual clusters for better retrieval

**Traditional Retrieval:**
```python
# Problem: Retrieves isolated entities, misses broader context
entities = await vector_search(query_embedding, top_k=10)
# Returns: [Entity1, Entity5, Entity8, ...] (disconnected)
```

**Community-Based Retrieval:**
```python
# Solution: Retrieve entire communities, preserving context
async def community_based_retrieval(query: str) -> List[Community]:
    # 1. Embed query
    query_embedding = await embedder.embed(query)

    # 2. Find seed entities via vector search
    seed_entities = await vector_search(query_embedding, top_k=5)

    # 3. Identify communities containing seed entities
    communities = []
    for entity in seed_entities:
        entity_communities = await get_entity_communities(entity.uuid)
        communities.extend(entity_communities)

    # 4. Deduplicate and rank communities
    ranked_communities = rank_by_relevance(communities, query)

    return ranked_communities[:3]  # Top 3 communities
```

**Benefits:**
- ✅ Retrieves connected entity clusters (not isolated nodes)
- ✅ Preserves relationship context
- ✅ Reduces hallucination (LLM sees complete context)

---

### 2. Multi-Hop Graph Traversal

**Purpose:** Navigate relationships to build comprehensive context

**Example Query:** "What patterns exist across all equipment maintenance issues?"

**Single-Hop (Insufficient):**
```cypher
// Returns: Equipment entities only (missing maintenance relationships)
MATCH (e:Entity {entity_type: "Equipment"})
RETURN e
LIMIT 10
```

**Multi-Hop (Comprehensive):**
```cypher
// Returns: Equipment + Maintenance + Issues + Patterns
MATCH path = (e:Entity {entity_type: "Equipment"})-[*1..3]-(related)
WHERE related.entity_type IN ["Maintenance", "Issue", "Pattern"]
RETURN path
LIMIT 50
```

**Implementation:**
```python
async def multi_hop_retrieval(
    seed_entities: List[str],
    max_hops: int = 3,
    max_nodes: int = 50
) -> Dict:
    """Traverse graph from seed entities."""
    query = """
    MATCH path = (seed:Entity)-[*1..$max_hops]-(related:Entity)
    WHERE seed.uuid IN $seed_uuids
    WITH path, relationships(path) as rels, nodes(path) as nodes_list
    RETURN
        nodes_list,
        rels,
        [n IN nodes_list | n.uuid] as node_ids,
        [r IN rels | type(r)] as rel_types
    LIMIT $max_nodes
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        seed_uuids=seed_entities,
        max_hops=max_hops,
        max_nodes=max_nodes
    )

    # Build subgraph
    subgraph = {
        "nodes": [],
        "edges": []
    }

    for record in results:
        nodes_list = record["nodes_list"]
        rels = record["rels"]

        for node in nodes_list:
            subgraph["nodes"].append({
                "uuid": node["uuid"],
                "name": node.get("name", "Unknown"),
                "type": node.get("entity_type", "Unknown"),
                "summary": node.get("summary", "")
            })

        for rel in rels:
            subgraph["edges"].append({
                "source": rel.start_node["uuid"],
                "target": rel.end_node["uuid"],
                "type": rel.type,
                "summary": rel.get("summary", "")
            })

    return subgraph
```

---

### 3. Community Summaries as Context

**Problem:** Passing 100+ entities to LLM exceeds context window

**Solution:** Use pre-generated community summaries instead of raw entities

**Example:**
```python
async def build_graphrag_context(
    query: str,
    communities: List[Community]
) -> str:
    """Build LLM context from community summaries."""
    context_parts = []

    # Add query
    context_parts.append(f"User Query: {query}\n")

    # Add community summaries (compact representation)
    context_parts.append("Relevant Knowledge Communities:\n")
    for i, community in enumerate(communities[:5], 1):
        context_parts.append(
            f"{i}. {community.name} ({community.member_count} entities)\n"
            f"   Summary: {community.summary}\n"
        )

    # Add sample entities from top community
    top_community = communities[0]
    members = await get_community_members(top_community.id)

    context_parts.append(f"\nKey Entities from '{top_community.name}':\n")
    for member in members[:10]:  # Top 10 entities
        context_parts.append(
            f"- {member['name']} ({member['type']}): {member['summary']}\n"
        )

    return "".join(context_parts)
```

**Context Size Comparison:**

| Approach | Entities | Tokens | Context Window Usage |
|----------|----------|--------|---------------------|
| Raw entities | 100 | ~8,000 | 40% |
| Community summaries | 5 | ~500 | 2.5% |
| **Hybrid** (summaries + top entities) | 5 + 10 | **~1,200** | **6%** ✅ |

---

## GraphRAG Query Patterns

### Pattern 1: Community-Enhanced Search

**Query:** "Find all equipment issues"

**Standard Search:**
```python
# Returns: Isolated equipment entities
results = await qdrant_search(query="equipment issues", limit=10)
```

**GraphRAG Search:**
```python
async def graphrag_search(query: str) -> Dict:
    # 1. Identify relevant communities
    communities = await community_based_retrieval(query)

    # 2. Multi-hop retrieval from community members
    seed_entities = []
    for community in communities[:3]:
        members = await get_community_members(community.id)
        seed_entities.extend([m["uuid"] for m in members[:5]])

    subgraph = await multi_hop_retrieval(seed_entities, max_hops=2)

    # 3. Build context from communities + subgraph
    context = await build_graphrag_context(query, communities)
    context += format_subgraph_as_text(subgraph)

    # 4. LLM generation
    answer = await generate_with_claude(query, context)

    return {
        "answer": answer,
        "communities": communities,
        "subgraph": subgraph,
        "confidence": calculate_confidence(communities, subgraph)
    }
```

---

### Pattern 2: Temporal GraphRAG

**Query:** "How has equipment maintenance changed over the last 6 months?"

**Implementation:**
```python
async def temporal_graphrag_search(query: str, lookback_months: int = 6) -> Dict:
    # 1. Parse temporal intent
    time_filter = {
        "start_date": datetime.now() - timedelta(days=30 * lookback_months),
        "end_date": datetime.now()
    }

    # 2. Community retrieval with temporal filtering
    communities = await community_based_retrieval(query)

    # 3. Graphiti temporal search
    temporal_results = await graphiti.search(
        query=query,
        center_node_uuid=None,
        num_results=20
    )

    # Filter by time window
    filtered_results = [
        r for r in temporal_results
        if time_filter["start_date"] <= r.created_at <= time_filter["end_date"]
    ]

    # 4. Detect temporal patterns
    patterns = await detect_temporal_patterns(filtered_results, time_filter)

    # 5. Build context with temporal information
    context = f"""Time Range: {time_filter['start_date']} to {time_filter['end_date']}

Communities:
{format_communities(communities)}

Temporal Patterns Detected:
{format_patterns(patterns)}

Entities and Relationships:
{format_temporal_results(filtered_results)}
"""

    # 6. LLM generation
    answer = await generate_with_claude(query, context)

    return {
        "answer": answer,
        "communities": communities,
        "patterns": patterns,
        "time_range": time_filter
    }
```

---

### Pattern 3: Multi-Community Reasoning

**Query:** "What connections exist between heavy equipment and shipment delays?"

**Challenge:** Query spans multiple communities

**Implementation:**
```python
async def multi_community_reasoning(query: str) -> Dict:
    # 1. Identify multiple relevant communities
    all_communities = await detect_communities()

    # Rank by relevance to query
    query_embedding = await embedder.embed(query)
    ranked_communities = []

    for community in all_communities:
        # Calculate relevance score
        community_embedding = await embedder.embed(community.summary)
        similarity = cosine_similarity(query_embedding, community_embedding)

        ranked_communities.append({
            "community": community,
            "relevance": similarity
        })

    # Select top 3 communities
    top_communities = sorted(
        ranked_communities,
        key=lambda x: x["relevance"],
        reverse=True
    )[:3]

    # 2. Find cross-community connections
    query = """
    MATCH (c1:Community)-[:HAS_MEMBER]->(e1:Entity)
    MATCH (c2:Community)-[:HAS_MEMBER]->(e2:Entity)
    WHERE c1.uuid = $comm1_id AND c2.uuid = $comm2_id
    MATCH path = shortestPath((e1)-[*1..5]-(e2))
    RETURN path, length(path) as path_length
    ORDER BY path_length ASC
    LIMIT 10
    """

    cross_community_paths = []
    for i in range(len(top_communities)):
        for j in range(i + 1, len(top_communities)):
            comm1 = top_communities[i]["community"]
            comm2 = top_communities[j]["community"]

            results, _, _ = await graphiti.client.driver.execute_query(
                query,
                comm1_id=comm1.id,
                comm2_id=comm2.id
            )

            cross_community_paths.extend(results)

    # 3. Build context with cross-community insights
    context = f"""Query: {query}

Relevant Communities:
{format_communities([c["community"] for c in top_communities])}

Cross-Community Connections:
{format_paths(cross_community_paths)}
"""

    # 4. LLM reasoning
    answer = await generate_with_claude(query, context)

    return {
        "answer": answer,
        "communities": [c["community"] for c in top_communities],
        "cross_community_paths": cross_community_paths
    }
```

---

## LLM Context Construction

### Best Practices

**1. Structured Format:**
```python
def format_graphrag_context(
    query: str,
    communities: List[Community],
    subgraph: Dict,
    patterns: List[Pattern] = None
) -> str:
    """Format GraphRAG context for LLM."""
    sections = []

    # Section 1: Query
    sections.append(f"# User Query\n{query}\n")

    # Section 2: Communities (high-level overview)
    sections.append("# Relevant Knowledge Communities\n")
    for i, comm in enumerate(communities[:5], 1):
        sections.append(
            f"{i}. **{comm.name}** ({comm.member_count} entities)\n"
            f"   {comm.summary}\n"
        )

    # Section 3: Key Entities (specific examples)
    sections.append("\n# Key Entities\n")
    for node in subgraph["nodes"][:15]:
        sections.append(
            f"- **{node['name']}** ({node['type']}): {node['summary']}\n"
        )

    # Section 4: Relationships (connections)
    sections.append("\n# Key Relationships\n")
    for edge in subgraph["edges"][:10]:
        sections.append(
            f"- {edge['source']} --[{edge['type']}]-> {edge['target']}\n"
        )

    # Section 5: Patterns (if temporal query)
    if patterns:
        sections.append("\n# Detected Patterns\n")
        for pattern in patterns:
            sections.append(f"- {pattern.description} (confidence: {pattern.confidence:.0%})\n")

    return "\n".join(sections)
```

**2. Token Budgeting:**

| Component | Max Tokens | Rationale |
|-----------|-----------|-----------|
| Communities (5) | 500 | High-level overview |
| Entities (15) | 1,500 | Specific examples |
| Relationships (10) | 500 | Key connections |
| Patterns (5) | 500 | Temporal insights |
| **Total** | **3,000** | **15% of Claude 3.5 context** ✅ |

**3. Relevance Ranking:**
```python
def rank_entities_by_relevance(
    entities: List[Dict],
    query_embedding: List[float]
) -> List[Dict]:
    """Rank entities by semantic similarity to query."""
    ranked = []

    for entity in entities:
        # Calculate similarity
        entity_text = f"{entity['name']} {entity['summary']}"
        entity_embedding = embedder.embed_sync(entity_text)
        similarity = cosine_similarity(query_embedding, entity_embedding)

        ranked.append({
            "entity": entity,
            "relevance": similarity
        })

    # Sort by relevance
    ranked.sort(key=lambda x: x["relevance"], reverse=True)

    return [item["entity"] for item in ranked]
```

---

## Claude 3.5 Sonnet Integration

### Prompt Template

```python
GRAPHRAG_SYSTEM_PROMPT = """You are an expert knowledge graph analyst with access to a graph database containing entities and their relationships.

Your task is to answer the user's query using the provided knowledge graph context. The context includes:
1. **Communities:** High-level clusters of related entities
2. **Entities:** Specific nodes in the graph with descriptions
3. **Relationships:** Connections between entities
4. **Patterns:** Temporal or structural patterns detected in the graph

Guidelines:
- Base your answer ONLY on the provided context
- Reference specific entities and relationships when explaining
- Identify patterns and connections across communities
- If the context is insufficient, state what information is missing
- Provide confidence level (High/Medium/Low) based on context completeness

Format:
1. Direct answer (2-3 sentences)
2. Supporting evidence from graph (list key entities/relationships)
3. Cross-community insights (if applicable)
4. Confidence level and reasoning
"""

async def generate_with_claude(
    query: str,
    context: str
) -> Dict:
    """Generate answer using Claude 3.5 Sonnet."""
    from anthropic import AsyncAnthropic

    anthropic = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = await anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0.3,  # Lower for factual accuracy
        system=GRAPHRAG_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{context}\n\nQuery: {query}"
            }
        ]
    )

    answer_text = response.content[0].text

    # Parse response
    return {
        "answer": answer_text,
        "model": "claude-3-5-sonnet-20241022",
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }
```

---

## Performance Optimization

### 1. Community Caching

**Problem:** Community detection is expensive (500-2000ms)

**Solution:**
```python
class GraphRAGCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.community_ttl = 3600  # 1 hour

    async def get_cached_communities(self, group_id: str) -> Optional[List[Community]]:
        cache_key = f"graphrag:communities:{group_id}"
        cached = await self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        return None

    async def cache_communities(self, group_id: str, communities: List[Community]):
        cache_key = f"graphrag:communities:{group_id}"
        await self.redis.setex(
            cache_key,
            self.community_ttl,
            json.dumps([c.dict() for c in communities])
        )
```

**Performance Impact:**
- Without cache: 500-2000ms community detection
- With cache: <10ms cache hit
- **Speedup:** 50-200x ✅

---

### 2. Parallel Retrieval

**Problem:** Sequential retrieval is slow

**Solution:**
```python
async def parallel_graphrag_retrieval(query: str) -> Dict:
    """Retrieve all GraphRAG components in parallel."""
    import asyncio

    # Execute in parallel
    communities_task = detect_communities()
    embedding_task = embedder.embed(query)
    graphiti_search_task = graphiti.search(query, num_results=20)

    # Wait for all
    communities, query_embedding, graphiti_results = await asyncio.gather(
        communities_task,
        embedding_task,
        graphiti_search_task
    )

    # Continue with subgraph extraction
    seed_entities = extract_seed_entities(graphiti_results)
    subgraph = await multi_hop_retrieval(seed_entities)

    return {
        "communities": communities,
        "subgraph": subgraph,
        "graphiti_results": graphiti_results
    }
```

**Performance Impact:**
- Sequential: 500ms + 100ms + 300ms = 900ms
- Parallel: max(500ms, 100ms, 300ms) = 500ms
- **Speedup:** 1.8x ✅

---

### 3. Subgraph Size Limiting

**Problem:** Large subgraphs exceed LLM context window

**Solution:**
```python
async def extract_bounded_subgraph(
    seed_entities: List[str],
    max_nodes: int = 50,
    max_hops: int = 3
) -> Dict:
    """Extract subgraph with size bounds."""
    query = """
    MATCH path = (seed:Entity)-[*1..$max_hops]-(related:Entity)
    WHERE seed.uuid IN $seed_uuids
    WITH path, nodes(path) as nodes_list, relationships(path) as rels

    // Rank by centrality (more connected = more important)
    WITH nodes_list, rels,
         [n IN nodes_list | size((n)--())] as degrees

    // Take top N nodes by degree
    WITH nodes_list, rels, degrees
    ORDER BY degrees DESC
    LIMIT $max_nodes

    RETURN nodes_list, rels
    """

    results, _, _ = await graphiti.client.driver.execute_query(
        query,
        seed_uuids=seed_entities,
        max_hops=max_hops,
        max_nodes=max_nodes
    )

    return build_subgraph_from_results(results)
```

---

## Example Integration

### Complete GraphRAG Router

```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class GraphRAGResult:
    answer: str
    communities: List[Community]
    subgraph: Dict
    confidence: float
    patterns: Optional[List[Pattern]] = None

class GraphRAGRouter:
    """Production GraphRAG implementation."""

    def __init__(
        self,
        graphiti_service,
        community_manager,
        anthropic_client,
        cache: GraphRAGCache
    ):
        self.graphiti = graphiti_service
        self.communities = community_manager
        self.anthropic = anthropic_client
        self.cache = cache

    async def query(
        self,
        query: str,
        enable_temporal: bool = True,
        max_communities: int = 5,
        max_nodes: int = 50
    ) -> GraphRAGResult:
        """Execute GraphRAG query."""
        # 1. Community retrieval (with caching)
        cached_communities = await self.cache.get_cached_communities("default")

        if cached_communities:
            all_communities = cached_communities
        else:
            all_communities = await self.communities.detect_communities()
            await self.cache.cache_communities("default", all_communities)

        # Rank communities by relevance
        query_embedding = await embedder.embed(query)
        relevant_communities = await self._rank_communities(
            all_communities,
            query_embedding
        )

        # 2. Multi-hop retrieval
        seed_entities = []
        for community in relevant_communities[:max_communities]:
            members = await self.communities._get_community_members(community.id)
            seed_entities.extend(members[:5])

        subgraph = await multi_hop_retrieval(
            seed_entities,
            max_hops=3,
            max_nodes=max_nodes
        )

        # 3. Temporal pattern detection (if enabled)
        patterns = None
        if enable_temporal:
            patterns = await detect_temporal_patterns(subgraph)

        # 4. Build context
        context = format_graphrag_context(
            query,
            relevant_communities[:5],
            subgraph,
            patterns
        )

        # 5. LLM generation
        llm_result = await generate_with_claude(query, context)

        # 6. Calculate confidence
        confidence = self._calculate_confidence(
            relevant_communities,
            subgraph,
            patterns
        )

        return GraphRAGResult(
            answer=llm_result["answer"],
            communities=relevant_communities[:5],
            subgraph=subgraph,
            confidence=confidence,
            patterns=patterns
        )

    async def _rank_communities(
        self,
        communities: List[Community],
        query_embedding: List[float]
    ) -> List[Community]:
        """Rank communities by semantic similarity to query."""
        ranked = []

        for community in communities:
            summary_embedding = await embedder.embed(community.summary)
            similarity = cosine_similarity(query_embedding, summary_embedding)

            ranked.append({
                "community": community,
                "relevance": similarity
            })

        ranked.sort(key=lambda x: x["relevance"], reverse=True)
        return [item["community"] for item in ranked]

    def _calculate_confidence(
        self,
        communities: List[Community],
        subgraph: Dict,
        patterns: Optional[List[Pattern]]
    ) -> float:
        """Calculate confidence based on context quality."""
        score = 0.0

        # Community coverage (0-0.4)
        if len(communities) >= 3:
            score += 0.4
        elif len(communities) >= 1:
            score += 0.2

        # Subgraph size (0-0.4)
        if len(subgraph["nodes"]) >= 30:
            score += 0.4
        elif len(subgraph["nodes"]) >= 10:
            score += 0.2

        # Pattern detection (0-0.2)
        if patterns and len(patterns) > 0:
            score += 0.2

        return min(score, 1.0)
```

---

## References

**Official Documentation:**
- Microsoft GraphRAG: https://github.com/microsoft/graphrag
- Neo4j RAG Patterns: https://neo4j.com/docs/graph-data-science/current/machine-learning/rag/
- LangChain Graph Integrations: https://python.langchain.com/docs/modules/chains/popular/graph

**Research Papers:**
- "Graph Retrieval-Augmented Generation" (Microsoft Research, 2024)
- "Knowledge Graph RAG" (Neo4j Technical Blog, 2024)

**Code Examples:**
- LlamaIndex GraphRAG: https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/graph_stores
- Neo4j RAG Examples: https://github.com/neo4j/NaLLM

---

**End of Technical Reference**

**Status:** Complete GraphRAG implementation patterns
**Next:** See TEMPORAL-ANALYTICS.md for time-series analysis and pattern detection
