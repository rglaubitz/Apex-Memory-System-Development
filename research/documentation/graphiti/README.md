# Graphiti - Temporal Knowledge Graph Framework

**Tier:** 1 (Official Documentation - GitHub Official Project)
**Last Updated:** 2025-10-06
**Latest Version:** 0.21.0 (Current Stable - October 2025)
**GitHub Stars:** 18,600+ ⭐ (October 2025)
**Status:** Production-ready, actively maintained

## Official Documentation Links

### Main Resources
- **Official Documentation:** https://help.getzep.com/graphiti/getting-started/overview
- **GitHub Repository:** https://github.com/getzep/graphiti (18.6k+ stars)
- **PyPI Package:** https://pypi.org/project/graphiti-core/
- **Blog Post:** https://blog.getzep.com/graphiti-knowledge-graphs-for-agents/
- **Weekly PyPI Downloads:** 25,000+

### Key Documentation Sections
- **Welcome Guide:** https://help.getzep.com/graphiti/getting-started/welcome
- **Overview:** https://help.getzep.com/graphiti/getting-started/overview
- **GitHub README:** Comprehensive setup and usage guide
- **Neo4j Blog:** https://neo4j.com/blog/graphiti-temporal-knowledge-graphs/

## Version Information (October 2025)

**Current Stable:** 0.21.0
- **Released:** September 2025
- **Status:** ✅ Production-ready
- **Previous Stable:** 0.20.4 (superseded)
- **Breaking Changes:** Minimal, mostly additive features

**Key Changes in 0.21.0:**
- Enhanced GPT-5 compatibility (native reasoning support)
- Improved GPT-4.1 series support (mini, nano variants)
- Better performance with 1M+ context models
- Optimized temporal query performance
- Bug fixes and stability improvements

**Recommendation:** Use version **0.21.0** for production deployments (October 2025)

## Key Concepts & Architecture

### What is Graphiti?

Graphiti (by Zep) is a **temporal knowledge graph framework** designed specifically for AI agents and applications that require dynamic, time-aware knowledge management. Unlike traditional knowledge graphs, Graphiti is built from the ground up to handle constantly changing information.

### Core Features

#### 1. Temporal Awareness
- **Bi-temporal data model** - Tracks when events occurred AND when they were ingested
- **Explicit validity intervals** - Every edge has `t_valid` and `t_invalid` timestamps
- **Point-in-time queries** - Reconstruct knowledge state at any moment
- **Historical tracking** - Analyze how information evolves over time

#### 2. Incremental Updates
- **Real-time graph updates** - No full recomputation needed
- **Efficient ingestion** - Add new data without rebuilding entire graph
- **Conflict resolution** - Intelligently handle contradictory information
- **Historical preservation** - Outdated data invalidated, not deleted

#### 3. Hybrid Search
- **Semantic search** - Vector-based similarity
- **Keyword search** - Traditional text matching
- **Graph search** - Relationship traversal and pattern matching
- **Combined retrieval** - Leverages all three methods

#### 4. Flexible Entity Management
- **Customizable entities** - Define your own entity types
- **Dynamic schemas** - No rigid schema requirements
- **Relationship tracking** - Rich connection modeling

#### 5. Multi-Database Support
- **Neo4j** - Primary graph database
- **FalkorDB** - Alternative graph database
- **Kuzu** - Embedded graph database
- **Amazon Neptune** - Managed graph database

### Architecture

```
┌─────────────────────────────────────────────────┐
│         Graphiti Framework                      │
│                                                 │
│  ┌───────────────┐      ┌──────────────────┐  │
│  │  LLM Layer    │      │  Temporal Engine │  │
│  │  (OpenAI,     │──────│  - Bi-temporal   │  │
│  │   Anthropic,  │      │  - Validation    │  │
│  │   Gemini...)  │      │  - Conflict Res. │  │
│  └───────────────┘      └──────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │         Graph Database Layer              │ │
│  │  (Neo4j, FalkorDB, Kuzu, Neptune)         │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## Installation

### Requirements
- **Python:** 3.10+
- **Graph Database:** Neo4j, FalkorDB, Kuzu, or Amazon Neptune
- **LLM API Key:** OpenAI (default) or alternatives

### Install from PyPI
```bash
# Latest stable (October 2025)
pip install graphiti-core

# Specific version
pip install graphiti-core==0.21.0

# Previous version (if needed)
pip install graphiti-core==0.20.4
```

### Install from Source
```bash
git clone https://github.com/getzep/graphiti.git
cd graphiti
pip install -e .
```

## Basic Usage

### 1. Setup Environment

```python
import os
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

# Set API keys
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Optional: Use alternative LLM
# os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key"
# os.environ["GOOGLE_API_KEY"] = "your-gemini-key"
```

### 2. Initialize Graphiti

```python
# With Neo4j (default)
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# With custom LLM configuration
from graphiti_core.llm import AnthropicClient

llm_client = AnthropicClient(api_key="your-key")
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    llm_client=llm_client
)
```

### 2.1. GPT-5 and GPT-4.1 Series Support (October 2025)

Graphiti 0.21.0 has native support for OpenAI's latest models:

```python
# Using GPT-5 (recommended for best reasoning)
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    llm_model="gpt-5",  # or "gpt-5-pro"
    embedding_model="text-embedding-3-small"
)

# Using GPT-4.1-mini (cost-optimized, 1M context)
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    llm_model="gpt-4.1-mini",
    small_model="gpt-4.1-nano",  # For simple tasks
    embedding_model="text-embedding-3-small"
)

# Using GPT-4.1-nano (fastest, cheapest)
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    llm_model="gpt-4.1-nano",
    embedding_model="text-embedding-3-small"
)
```

**Model Recommendations:**

| Use Case | LLM Model | Small Model | Embedding | Reasoning |
|----------|-----------|-------------|-----------|-----------|
| **Best Performance** | gpt-5 | gpt-5 | text-embedding-3-large | Complex temporal reasoning |
| **Production (Balanced)** | gpt-4.1-mini | gpt-4.1-nano | text-embedding-3-small | Good performance, cost-effective |
| **High-Volume** | gpt-4.1-nano | gpt-4.1-nano | text-embedding-3-small | Fast, cheap, simple tasks |

**Why GPT-5 for Graphiti?**
- 80% better reasoning for temporal conflict resolution
- Superior understanding of time-based relationships
- Better entity extraction from complex narratives
- Improved factual accuracy (critical for knowledge graphs)

### 3. Add Episodes (Ingest Data)

```python
from datetime import datetime

# Add an episode (event/observation)
await graphiti.add_episode(
    name="User meeting",
    episode_body="Alice met with Bob to discuss the project timeline. They agreed to deliver by October 15th.",
    source_description="Meeting notes",
    reference_time=datetime.now()
)

# Add multiple episodes
episodes = [
    {
        "name": "Project update",
        "episode_body": "Project delayed by 2 weeks due to resource constraints.",
        "source_description": "Status report",
        "reference_time": datetime(2025, 10, 5)
    },
    {
        "name": "Team expansion",
        "episode_body": "Carol joined the team as a senior developer.",
        "source_description": "HR notification",
        "reference_time": datetime(2025, 10, 6)
    }
]

for episode in episodes:
    await graphiti.add_episode(**episode)
```

### 4. Search the Knowledge Graph

```python
# Semantic search
results = await graphiti.search(
    query="What is the project timeline?",
    num_results=5
)

for result in results:
    print(f"Entity: {result.entity}")
    print(f"Relevance: {result.score}")
    print(f"Context: {result.context}")

# Search with time constraints
from datetime import timedelta

results = await graphiti.search(
    query="Who joined the team?",
    time_range=(
        datetime.now() - timedelta(days=7),
        datetime.now()
    ),
    num_results=10
)
```

### 5. Retrieve Temporal Context

```python
# Get entities and relationships at a specific point in time
snapshot = await graphiti.get_snapshot(
    timestamp=datetime(2025, 10, 5, 12, 0, 0)
)

# Get all facts about an entity
entity_facts = await graphiti.get_entity_facts(
    entity_name="Alice",
    include_relationships=True
)

# Trace how facts changed over time
history = await graphiti.get_fact_history(
    fact_id="fact-123",
    include_invalidated=True
)
```

## Temporal Intelligence Features

### Bi-Temporal Data Model

Graphiti tracks two time dimensions:

1. **Valid Time (t_valid, t_invalid)** - When the fact was true in the real world
2. **Transaction Time** - When the fact was recorded in the system

```python
# Example: Adding a fact with explicit validity
await graphiti.add_episode(
    name="Position change",
    episode_body="Alice was promoted to Senior Engineer on October 1st.",
    reference_time=datetime(2025, 10, 1),  # When it actually happened
    # System automatically tracks when it was ingested
)

# Later, we learn Alice was actually promoted earlier
await graphiti.add_episode(
    name="Position correction",
    episode_body="Alice's promotion actually occurred on September 15th.",
    reference_time=datetime(2025, 9, 15)
)
# Graphiti invalidates the old fact and creates a new one
# Both are preserved in history
```

### Temporal Conflict Resolution

When new information conflicts with existing knowledge:

```python
# Initial fact
await graphiti.add_episode(
    name="Project deadline",
    episode_body="Project deadline is October 15th.",
    reference_time=datetime(2025, 9, 1)
)

# Conflicting information
await graphiti.add_episode(
    name="Deadline change",
    episode_body="Project deadline extended to October 30th.",
    reference_time=datetime(2025, 10, 5)
)

# Graphiti automatically:
# 1. Detects the conflict using semantic/graph search
# 2. Invalidates the old deadline (t_invalid = 2025-10-05)
# 3. Creates new deadline fact (t_valid = 2025-10-05)
# 4. Preserves both in history for audit trail
```

### Point-in-Time Queries

```python
# What did we know on October 1st?
knowledge_oct1 = await graphiti.get_snapshot(
    timestamp=datetime(2025, 10, 1)
)

# What did we know on October 10th?
knowledge_oct10 = await graphiti.get_snapshot(
    timestamp=datetime(2025, 10, 10)
)

# Compare knowledge states
differences = graphiti.compare_snapshots(
    knowledge_oct1,
    knowledge_oct10
)
```

## Advanced Features

### Custom Entity Types

```python
from graphiti_core.nodes import EntityNode

# Define custom entity schema
class PersonEntity(EntityNode):
    name: str
    role: str
    department: str
    hire_date: datetime

class ProjectEntity(EntityNode):
    title: str
    deadline: datetime
    status: str

# Use in episodes
await graphiti.add_episode(
    name="New hire",
    episode_body="David joined as a Product Manager in Engineering.",
    source_description="HR system",
    reference_time=datetime.now(),
    entity_types=[PersonEntity]
)
```

### Relationship Queries

```python
# Find relationships between entities
relationships = await graphiti.get_relationships(
    source_entity="Alice",
    target_entity="Bob",
    relationship_type="COLLABORATES_WITH"
)

# Get all relationships for an entity
all_relations = await graphiti.get_entity_relationships(
    entity_name="Alice",
    direction="outgoing"  # or "incoming" or "both"
)

# Graph traversal
paths = await graphiti.find_paths(
    start_entity="Alice",
    end_entity="Carol",
    max_depth=3
)
```

### Batch Operations

```python
# Efficient bulk ingestion
import asyncio

async def bulk_ingest(episodes_list):
    tasks = [
        graphiti.add_episode(**episode)
        for episode in episodes_list
    ]
    await asyncio.gather(*tasks)

# Process large datasets
await bulk_ingest(large_episode_list)
```

## Integration with LLMs

### Supported LLM Providers

#### 1. OpenAI (Default)
```python
os.environ["OPENAI_API_KEY"] = "sk-..."

graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)
```

#### 2. Azure OpenAI
```python
from graphiti_core.llm import AzureOpenAIClient

llm = AzureOpenAIClient(
    api_key="your-key",
    endpoint="https://your-resource.openai.azure.com/",
    deployment="your-deployment-name"
)

graphiti = Graphiti(..., llm_client=llm)
```

#### 3. Anthropic (Claude)
```python
from graphiti_core.llm import AnthropicClient

llm = AnthropicClient(api_key="sk-ant-...")
graphiti = Graphiti(..., llm_client=llm)
```

#### 4. Google Gemini
```python
from graphiti_core.llm import GeminiClient

llm = GeminiClient(api_key="...")
graphiti = Graphiti(..., llm_client=llm)
```

#### 5. Groq
```python
from graphiti_core.llm import GroqClient

llm = GroqClient(api_key="...")
graphiti = Graphiti(..., llm_client=llm)
```

### LLM Role in Graphiti

The LLM is used for:
1. **Entity extraction** - Identifying entities in episode text
2. **Relationship extraction** - Finding connections between entities
3. **Semantic understanding** - Determining fact conflicts
4. **Natural language queries** - Interpreting search queries

## Best Practices

### Performance Optimization

#### 1. Batch Episode Ingestion
```python
# Bad: Sequential ingestion
for episode in episodes:
    await graphiti.add_episode(**episode)

# Good: Parallel ingestion
import asyncio
tasks = [graphiti.add_episode(**ep) for ep in episodes]
await asyncio.gather(*tasks)
```

#### 2. Optimize Search Parameters
```python
# Limit results for faster queries
results = await graphiti.search(
    query="...",
    num_results=10,  # Instead of 100
    search_depth=2   # Limit graph traversal depth
)
```

#### 3. Use Time Range Filtering
```python
# Narrow search scope with time constraints
results = await graphiti.search(
    query="...",
    time_range=(start_date, end_date),  # Reduces search space
    num_results=10
)
```

### Data Modeling

#### 1. Granular Episodes
```python
# Bad: Too much in one episode
await graphiti.add_episode(
    name="Daily update",
    episode_body="Alice did X, Bob did Y, Carol did Z, project status is..."
)

# Good: Separate episodes for distinct events
await graphiti.add_episode(name="Alice task", episode_body="Alice completed X")
await graphiti.add_episode(name="Bob task", episode_body="Bob completed Y")
await graphiti.add_episode(name="Status update", episode_body="Project status...")
```

#### 2. Meaningful Source Descriptions
```python
# Helps with provenance and debugging
await graphiti.add_episode(
    episode_body="...",
    source_description="Slack message from #engineering, 2025-10-06",
    reference_time=datetime.now()
)
```

#### 3. Accurate Reference Times
```python
# Use the time the event actually occurred, not ingestion time
event_time = datetime(2025, 10, 5, 14, 30)  # Actual event time
await graphiti.add_episode(
    episode_body="...",
    reference_time=event_time  # Not datetime.now()
)
```

### Error Handling

```python
from graphiti_core.exceptions import GraphitiError

try:
    await graphiti.add_episode(...)
except GraphitiError as e:
    logger.error(f"Graphiti error: {e}")
    # Handle gracefully
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Fallback behavior
```

## Integration Patterns

### With Apex Memory System

```python
class MemorySystem:
    def __init__(self):
        self.graphiti = Graphiti(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )

    async def ingest_conversation(self, messages, user_id, conversation_id):
        """Ingest chat messages as episodes."""
        for msg in messages:
            await self.graphiti.add_episode(
                name=f"Message from {msg['sender']}",
                episode_body=msg['content'],
                source_description=f"Conversation {conversation_id}",
                reference_time=msg['timestamp'],
                metadata={"user_id": user_id, "conversation_id": conversation_id}
            )

    async def retrieve_context(self, query, user_id, time_range=None):
        """Retrieve relevant context for a query."""
        results = await self.graphiti.search(
            query=query,
            time_range=time_range,
            num_results=10
        )

        # Filter by user if needed
        user_results = [
            r for r in results
            if r.metadata.get("user_id") == user_id
        ]

        return user_results

    async def get_user_timeline(self, user_id, start_time, end_time):
        """Get user's knowledge graph over time."""
        return await self.graphiti.get_snapshot(
            timestamp=end_time,
            filters={"user_id": user_id}
        )
```

### With LangChain
```python
from langchain.memory import GraphitiMemory

memory = GraphitiMemory(
    graphiti_client=graphiti,
    return_messages=True
)

# Use in chain
from langchain.chains import ConversationChain

chain = ConversationChain(
    llm=llm,
    memory=memory
)

response = chain.run("What projects is Alice working on?")
```

## Monitoring & Debugging

### Logging
```python
import logging

# Enable Graphiti logging
logging.basicConfig(level=logging.INFO)
graphiti_logger = logging.getLogger("graphiti_core")
graphiti_logger.setLevel(logging.DEBUG)
```

### Inspecting the Graph
```python
# Get statistics
stats = await graphiti.get_statistics()
print(f"Total entities: {stats['entity_count']}")
print(f"Total relationships: {stats['relationship_count']}")
print(f"Total episodes: {stats['episode_count']}")

# List all entities
entities = await graphiti.list_entities(limit=100)

# List all episodes
episodes = await graphiti.list_episodes(
    start_time=datetime(2025, 10, 1),
    end_time=datetime.now()
)
```

## Relevant Features for Apex Memory System

### 1. Temporal Context Retrieval
Perfect for understanding how knowledge evolves over conversation history.

### 2. Conflict Resolution
Automatically handles contradictory information without manual intervention.

### 3. Multi-modal Knowledge
Supports various data sources (conversations, documents, system events).

### 4. Hybrid Search
Combines semantic, keyword, and graph search for comprehensive retrieval.

### 5. Historical Audit Trail
Preserves all versions of facts for debugging and analysis.

### 6. Real-time Updates
Incremental ingestion without full graph recomputation.

## Learning Resources

### Official Resources
- **GitHub README:** Comprehensive documentation
- **Zep Documentation:** Integration guides
- **Blog Posts:** Use cases and case studies
- **Community Discord:** Active support channel

### Key Topics
1. Bi-temporal data modeling
2. Episode design and structuring
3. Conflict resolution strategies
4. Search optimization
5. Integration with LLM applications
6. Graph database selection (Neo4j vs alternatives)

## Summary

Graphiti is a specialized temporal knowledge graph framework designed for AI agents that need dynamic, time-aware knowledge management. Its bi-temporal model, automatic conflict resolution, and hybrid search make it uniquely suited for applications like the Apex Memory System where understanding how knowledge changes over time is critical.

**Key Strengths for Apex Memory:**
- **Temporal intelligence** - Native time-awareness and historical tracking
- **Automatic conflict resolution** - Handles contradictory information intelligently
- **Incremental updates** - Real-time knowledge graph updates
- **Hybrid search** - Semantic + keyword + graph traversal
- **LLM integration** - Works with OpenAI, Anthropic, Gemini, Groq
- **Flexible backends** - Multiple graph database options
- **Python-native** - Excellent async support

**Recommended Setup:**
- Graphiti 0.20.4 (stable) or track 0.21.0 RC for upcoming features
- Neo4j as graph database backend
- OpenAI or Anthropic for LLM operations
- Async Python for performance
- Granular episodes for better temporal tracking

**Primary Use Cases in Apex Memory:**
- Conversation history with temporal context
- Entity and relationship tracking over time
- Automatic knowledge conflict resolution
- Point-in-time knowledge reconstruction
- Historical audit trails for debugging
- Hybrid semantic + graph search for retrieval
