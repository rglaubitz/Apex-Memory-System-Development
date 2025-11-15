# Phase 4: Agent↔Agent Communication - Implementation Plan

**Phase:** Conversational Memory Integration - Phase 4
**Status:** 📝 Planning
**Timeline:** Week 5-6 (2 weeks)
**Prerequisites:** Phase 1 (Multi-Agent Namespacing) + Phase 3 (Memory Quality) Complete
**Last Updated:** 2025-11-15

---

## Executive Summary

**Phase 4 enables direct agent-to-agent communication** through NATS messaging, logging all interactions to PostgreSQL, and enriching the knowledge graph with agent collaboration patterns.

**What This Unlocks:**
- Oscar (Fleet Manager) can ask Sarah (CFO) about maintenance budgets
- Maya (Sales) can query Oscar about truck availability for quotes
- All agent interactions logged and searchable
- Knowledge graph enriched from agent collaborations
- Foundation for autonomous multi-agent workflows

**Timeline:** 2 weeks (10 working days)
**Test Target:** 15 tests (all passing)
**Performance Target:** <20ms agent messaging latency (P95)

---

## Architecture Overview

### Current State (After Phase 1 + 3)
- ✅ Multi-agent namespacing (Oscar, Sarah, Maya, System)
- ✅ Agent-specific Qdrant collections
- ✅ Agent-specific Redis caching
- ✅ Memory quality & importance management
- ❌ No agent↔agent communication
- ❌ Agents can't collaborate directly

### Target State (After Phase 4)
- ✅ NATS pub/sub for agent↔agent messaging
- ✅ Request-reply pattern for synchronous queries
- ✅ All agent interactions logged to PostgreSQL
- ✅ Knowledge graph enriched from collaborations
- ✅ <20ms messaging latency (P95)

---

## Phase 4 Data Flow

```
Agent Oscar (Fleet Manager)
    ↓
"What's our Q4 maintenance budget?"
    ↓
NATS Publish
    Topic: "agent.sarah.query"
    Payload: {
        from: "oscar",
        to: "sarah",
        query: "Q4 maintenance budget",
        conversation_id: "12345",
        request_id: "uuid-...",
        timestamp: "2025-11-15T10:30:00Z"
    }
    Latency: <5ms
    ↓
Agent Sarah (CFO) Subscriber
    ↓
Process Query
    1. Fetch context from Redis
    2. Query financial data (Qdrant: sarah_financial_knowledge)
    3. Generate response (Claude API)
    Latency: 500-1500ms
    ↓
NATS Reply
    Topic: "agent.oscar.response"
    Payload: {
        from: "sarah",
        to: "oscar",
        response: "Q4 maintenance budget is $125,000 across 45 vehicles",
        confidence: 0.95,
        sources: ["invoice-2024-Q4-001", "budget-2024"],
        request_id: "uuid-...",
        timestamp: "2025-11-15T10:30:01.2Z"
    }
    Latency: <10ms
    ↓
Agent Oscar Receives Response
    Total: ~1.5s end-to-end
    ↓
PostgreSQL Write (Background)
    Table: agent_interactions
    Fields: {
        id: uuid,
        conversation_id: "12345",
        from_agent: "oscar",
        to_agent: "sarah",
        interaction_type: "query",
        query_text: "What's our Q4 maintenance budget?",
        response_text: "Q4 maintenance budget is $125,000...",
        metadata: {...},
        created_at: timestamp,
        processed_at: timestamp,
        latency_ms: 1500
    }
    ↓
Temporal Queue
    Workflow: AgentInteractionIngestionWorkflow
    Activities:
        1. Extract entities from interaction
        2. Create Graphiti episode
        3. Update agent collaboration graph
        4. Calculate importance score
    Background processing: 10-20s
```

---

## Implementation Tasks

### Task 4.1: NATS Integration (Days 1-3)

**Goal:** Set up NATS messaging infrastructure for agent-to-agent communication

#### Subtask 4.1.1: Install NATS Server (Day 1 - Morning)

**Docker Compose:**
```yaml
# Add to docker-compose.yml
  nats:
    image: nats:2.10-alpine
    container_name: apex-nats
    ports:
      - "4222:4222"  # Client connections
      - "8222:8222"  # HTTP monitoring
      - "6222:6222"  # Cluster routing
    command:
      - "--jetstream"
      - "--store_dir=/data"
      - "--http_port=8222"
    volumes:
      - nats_data:/data
    networks:
      - apex-network
    healthcheck:
      test: ["CMD", "nats", "server", "check"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  nats_data:
    driver: local
```

**Test Installation:**
```bash
# Start NATS
docker-compose up -d nats

# Verify health
curl http://localhost:8222/healthz
# Expected: {"status":"ok"}

# Test pub/sub
docker exec apex-nats nats pub test.subject "Hello NATS"
docker exec apex-nats nats sub test.subject
```

**Success Criteria:**
- NATS server running and healthy
- Can pub/sub messages via CLI
- Monitoring dashboard accessible at http://localhost:8222

---

#### Subtask 4.1.2: Python NATS Client Integration (Day 1 - Afternoon)

**Install Dependencies:**
```bash
# Add to requirements.txt
nats-py==2.7.0
```

**Create NATS Service:**
`apex_memory/services/nats_service.py`

```python
"""
NATS Service for Agent↔Agent Communication.

Provides pub/sub and request-reply patterns for inter-agent messaging.
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg

from apex_memory.config.settings import settings

logger = logging.getLogger(__name__)


class NATSService:
    """NATS client for agent communication."""

    def __init__(self):
        self.nc: Optional[NATS] = None
        self.subscriptions: Dict[str, int] = {}  # topic -> subscription_id

    async def connect(self):
        """Connect to NATS server."""
        if self.nc and self.nc.is_connected:
            logger.info("Already connected to NATS")
            return

        self.nc = NATS()
        await self.nc.connect(servers=[settings.nats_url])
        logger.info(f"Connected to NATS at {settings.nats_url}")

    async def disconnect(self):
        """Disconnect from NATS server."""
        if self.nc:
            await self.nc.drain()
            logger.info("Disconnected from NATS")

    async def publish(
        self,
        subject: str,
        message: Dict[str, Any],
        timeout: float = 2.0
    ):
        """
        Publish a message to a subject.

        Args:
            subject: NATS subject (e.g., "agent.sarah.query")
            message: Message payload (will be JSON serialized)
            timeout: Publish timeout in seconds

        Example:
            await nats.publish("agent.sarah.query", {
                "from": "oscar",
                "to": "sarah",
                "query": "Q4 maintenance budget",
                "request_id": "uuid-..."
            })
        """
        if not self.nc or not self.nc.is_connected:
            await self.connect()

        payload = json.dumps(message).encode()
        await self.nc.publish(subject, payload)
        logger.debug(f"Published to {subject}: {message}")

    async def subscribe(
        self,
        subject: str,
        callback: Callable[[Dict[str, Any]], None],
        queue: Optional[str] = None
    ):
        """
        Subscribe to a subject.

        Args:
            subject: NATS subject to subscribe to
            callback: Async function to handle messages
            queue: Optional queue group name for load balancing

        Example:
            async def handle_query(msg):
                print(f"Received: {msg}")

            await nats.subscribe("agent.sarah.query", handle_query)
        """
        if not self.nc or not self.nc.is_connected:
            await self.connect()

        async def message_handler(msg: Msg):
            """Wrapper to deserialize and call callback."""
            try:
                payload = json.loads(msg.data.decode())
                await callback(payload)
            except Exception as e:
                logger.error(f"Error handling message from {subject}: {e}")

        sub_id = await self.nc.subscribe(subject, cb=message_handler, queue=queue)
        self.subscriptions[subject] = sub_id
        logger.info(f"Subscribed to {subject} (queue: {queue})")

    async def request(
        self,
        subject: str,
        message: Dict[str, Any],
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """
        Send a request and wait for response (request-reply pattern).

        Args:
            subject: NATS subject to send request to
            message: Request payload
            timeout: Response timeout in seconds

        Returns:
            Response payload (deserialized JSON)

        Example:
            response = await nats.request("agent.sarah.query", {
                "from": "oscar",
                "query": "Q4 maintenance budget"
            })
        """
        if not self.nc or not self.nc.is_connected:
            await self.connect()

        payload = json.dumps(message).encode()
        msg = await self.nc.request(subject, payload, timeout=timeout)

        response = json.loads(msg.data.decode())
        logger.debug(f"Request to {subject}: {message} → Response: {response}")
        return response

    async def unsubscribe(self, subject: str):
        """Unsubscribe from a subject."""
        if subject in self.subscriptions:
            sub_id = self.subscriptions[subject]
            await self.nc.unsubscribe(sub_id)
            del self.subscriptions[subject]
            logger.info(f"Unsubscribed from {subject}")

    def is_connected(self) -> bool:
        """Check if connected to NATS."""
        return self.nc is not None and self.nc.is_connected


# Singleton instance
nats_service = NATSService()
```

**Configuration:**
`apex_memory/config/settings.py`

```python
class Settings(BaseSettings):
    # Existing settings...

    # NATS Configuration
    nats_url: str = Field(
        default="nats://localhost:4222",
        env="NATS_URL",
        description="NATS server URL"
    )

    nats_enable_agent_communication: bool = Field(
        default=False,
        env="NATS_ENABLE_AGENT_COMMUNICATION",
        description="Enable NATS-based agent communication"
    )
```

**Test:**
```python
# tests/unit/test_nats_service.py

import pytest
from apex_memory.services.nats_service import NATSService


@pytest.mark.asyncio
async def test_nats_connect():
    """Test NATS connection."""
    nats = NATSService()
    await nats.connect()

    assert nats.is_connected()

    await nats.disconnect()


@pytest.mark.asyncio
async def test_nats_pub_sub():
    """Test publish and subscribe."""
    nats = NATSService()
    await nats.connect()

    received_messages = []

    async def handle_message(msg):
        received_messages.append(msg)

    # Subscribe
    await nats.subscribe("test.subject", handle_message)

    # Publish
    await nats.publish("test.subject", {"content": "Hello NATS"})

    # Wait for message delivery
    await asyncio.sleep(0.1)

    assert len(received_messages) == 1
    assert received_messages[0]["content"] == "Hello NATS"

    await nats.disconnect()


@pytest.mark.asyncio
async def test_nats_request_reply():
    """Test request-reply pattern."""
    nats = NATSService()
    await nats.connect()

    # Set up responder
    async def handle_request(msg):
        # Reply handled automatically by NATS
        return {"response": f"Processed: {msg['query']}"}

    await nats.subscribe("test.request", handle_request)

    # Send request
    response = await nats.request("test.request", {"query": "test"})

    assert "response" in response
    assert "Processed: test" in response["response"]

    await nats.disconnect()
```

**Success Criteria:**
- NATS service connects successfully
- Pub/sub pattern working
- Request-reply pattern working
- All 3 unit tests passing

---

#### Subtask 4.1.3: Agent Communication Patterns (Days 2-3)

**Create Agent Interaction Models:**
`apex_memory/models/agent_interaction.py`

```python
"""Agent interaction data models."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class InteractionType(str, Enum):
    """Types of agent interactions."""
    QUERY = "query"  # Agent asks another agent a question
    NOTIFICATION = "notification"  # Agent notifies another agent
    COMMAND = "command"  # Agent commands another agent to perform action
    RESPONSE = "response"  # Response to a query/command


class AgentInteraction(BaseModel):
    """Agent-to-agent interaction record."""

    id: UUID = Field(default_factory=uuid4)
    conversation_id: Optional[UUID] = None  # Link to parent conversation
    from_agent: str  # Agent ID sending message
    to_agent: str  # Agent ID receiving message
    interaction_type: InteractionType
    query_text: Optional[str] = None
    response_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    request_id: UUID = Field(default_factory=uuid4)  # For request-reply tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    latency_ms: Optional[int] = None  # Round-trip latency
    confidence: Optional[float] = None  # Response confidence score
    sources: list[str] = Field(default_factory=list)  # Source documents/facts


class AgentMessage(BaseModel):
    """Message payload for NATS."""

    from_agent: str
    to_agent: str
    message_type: InteractionType
    content: str
    conversation_id: Optional[UUID] = None
    request_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

**Create Agent Communication Manager:**
`apex_memory/services/agent_communication.py`

```python
"""
Agent Communication Manager.

Handles agent-to-agent messaging via NATS with logging and tracking.
"""

import logging
from typing import Optional, Callable
from uuid import UUID
from datetime import datetime

from apex_memory.models.agent_interaction import (
    AgentInteraction,
    AgentMessage,
    InteractionType
)
from apex_memory.services.nats_service import nats_service
from apex_memory.database import get_db_session

logger = logging.getLogger(__name__)


class AgentCommunicationManager:
    """Manages agent-to-agent communication."""

    def __init__(self):
        self.nats = nats_service
        self.agent_handlers: dict[str, Callable] = {}

    async def initialize(self):
        """Initialize NATS connection and subscriptions."""
        await self.nats.connect()
        logger.info("Agent communication manager initialized")

    async def send_query(
        self,
        from_agent: str,
        to_agent: str,
        query: str,
        conversation_id: Optional[UUID] = None,
        timeout: float = 5.0
    ) -> dict:
        """
        Send a query from one agent to another (synchronous request-reply).

        Args:
            from_agent: Sending agent ID
            to_agent: Receiving agent ID
            query: Query text
            conversation_id: Optional conversation context
            timeout: Response timeout

        Returns:
            Response from target agent

        Example:
            response = await comm.send_query(
                from_agent="oscar",
                to_agent="sarah",
                query="What's our Q4 maintenance budget?"
            )
        """
        start_time = datetime.utcnow()

        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=InteractionType.QUERY,
            content=query,
            conversation_id=conversation_id
        )

        # NATS subject: agent.{to_agent}.query
        subject = f"agent.{to_agent}.query"

        try:
            # Send request via NATS
            response = await self.nats.request(
                subject=subject,
                message=message.model_dump(mode='json'),
                timeout=timeout
            )

            # Calculate latency
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log interaction to PostgreSQL
            await self._log_interaction(
                from_agent=from_agent,
                to_agent=to_agent,
                interaction_type=InteractionType.QUERY,
                query_text=query,
                response_text=response.get("content"),
                conversation_id=conversation_id,
                request_id=message.request_id,
                latency_ms=latency_ms,
                confidence=response.get("confidence"),
                sources=response.get("sources", [])
            )

            return response

        except Exception as e:
            logger.error(f"Error sending query from {from_agent} to {to_agent}: {e}")
            raise

    async def send_notification(
        self,
        from_agent: str,
        to_agent: str,
        notification: str,
        conversation_id: Optional[UUID] = None
    ):
        """
        Send a notification from one agent to another (fire-and-forget).

        Example:
            await comm.send_notification(
                from_agent="maya",
                to_agent="oscar",
                notification="New quote request for 3 trucks in LA region"
            )
        """
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=InteractionType.NOTIFICATION,
            content=notification,
            conversation_id=conversation_id
        )

        subject = f"agent.{to_agent}.notification"

        await self.nats.publish(subject, message.model_dump(mode='json'))

        # Log interaction
        await self._log_interaction(
            from_agent=from_agent,
            to_agent=to_agent,
            interaction_type=InteractionType.NOTIFICATION,
            query_text=notification,
            conversation_id=conversation_id,
            request_id=message.request_id
        )

    async def register_agent_handler(
        self,
        agent_id: str,
        handler: Callable
    ):
        """
        Register a handler function for an agent.

        The handler receives AgentMessage and returns a response.

        Example:
            async def sarah_handler(message: AgentMessage) -> dict:
                # Process query
                return {
                    "content": "Q4 maintenance budget is $125,000",
                    "confidence": 0.95,
                    "sources": ["budget-2024"]
                }

            await comm.register_agent_handler("sarah", sarah_handler)
        """
        self.agent_handlers[agent_id] = handler

        # Subscribe to agent's query subject
        query_subject = f"agent.{agent_id}.query"
        await self.nats.subscribe(query_subject, handler)

        # Subscribe to agent's notification subject
        notif_subject = f"agent.{agent_id}.notification"
        await self.nats.subscribe(notif_subject, handler)

        logger.info(f"Registered handler for agent: {agent_id}")

    async def _log_interaction(
        self,
        from_agent: str,
        to_agent: str,
        interaction_type: InteractionType,
        query_text: Optional[str] = None,
        response_text: Optional[str] = None,
        conversation_id: Optional[UUID] = None,
        request_id: Optional[UUID] = None,
        latency_ms: Optional[int] = None,
        confidence: Optional[float] = None,
        sources: list[str] = None
    ):
        """Log interaction to PostgreSQL."""
        interaction = AgentInteraction(
            conversation_id=conversation_id,
            from_agent=from_agent,
            to_agent=to_agent,
            interaction_type=interaction_type,
            query_text=query_text,
            response_text=response_text,
            request_id=request_id,
            latency_ms=latency_ms,
            confidence=confidence,
            sources=sources or [],
            created_at=datetime.utcnow(),
            processed_at=datetime.utcnow() if response_text else None
        )

        # Write to database
        async with get_db_session() as session:
            session.add(interaction)
            await session.commit()

        logger.info(f"Logged {interaction_type} interaction: {from_agent} → {to_agent}")


# Singleton instance
agent_comm = AgentCommunicationManager()
```

**Success Criteria:**
- Agent communication manager working
- Can send queries between agents
- Can send notifications
- All interactions logged to PostgreSQL

---

### Task 4.2: Database Schema + API (Days 4-5)

#### Subtask 4.2.1: Create agent_interactions Table (Day 4 - Morning)

**Alembic Migration:**
`alembic/versions/xxxx_add_agent_interactions_table.py`

```python
"""Add agent_interactions table.

Revision ID: xxxx
Revises: previous_revision
Create Date: 2025-11-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


def upgrade():
    op.create_table(
        'agent_interactions',
        sa.Column('id', UUID(), primary_key=True),
        sa.Column('conversation_id', UUID(), nullable=True),
        sa.Column('from_agent', sa.String(50), nullable=False),
        sa.Column('to_agent', sa.String(50), nullable=False),
        sa.Column('interaction_type', sa.String(20), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=True),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('metadata', JSONB(), default={}),
        sa.Column('request_id', UUID(), nullable=False, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('sources', sa.ARRAY(sa.String()), default=[]),
    )

    # Indices
    op.create_index('ix_agent_interactions_from_agent', 'agent_interactions', ['from_agent'])
    op.create_index('ix_agent_interactions_to_agent', 'agent_interactions', ['to_agent'])
    op.create_index('ix_agent_interactions_conversation_id', 'agent_interactions', ['conversation_id'])
    op.create_index('ix_agent_interactions_created_at', 'agent_interactions', ['created_at'])
    op.create_index('ix_agent_interactions_request_id', 'agent_interactions', ['request_id'], unique=True)

    # Foreign key to conversations table (if exists)
    op.create_foreign_key(
        'fk_agent_interactions_conversation_id',
        'agent_interactions', 'conversations',
        ['conversation_id'], ['uuid'],
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_table('agent_interactions')
```

**Run Migration:**
```bash
alembic upgrade head
```

**Verify:**
```sql
\d agent_interactions

-- Expected columns:
-- id, conversation_id, from_agent, to_agent, interaction_type,
-- query_text, response_text, metadata, request_id, created_at,
-- processed_at, latency_ms, confidence, sources
```

**Success Criteria:**
- agent_interactions table created
- All indices created
- Foreign key constraint to conversations table
- Migration reversible (downgrade works)

---

#### Subtask 4.2.2: Create Agent Interactions API (Day 4 - Afternoon + Day 5)

**API Endpoints:**
`apex_memory/api/agent_interactions.py`

```python
"""
Agent Interactions API.

Endpoints for querying and managing agent-to-agent interactions.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apex_memory.models.agent_interaction import AgentInteraction, InteractionType
from apex_memory.database import get_db_session

router = APIRouter(prefix="/api/v1/agent-interactions", tags=["agent-interactions"])


@router.get("/", response_model=List[AgentInteraction])
async def list_interactions(
    from_agent: Optional[str] = Query(None, description="Filter by sending agent"),
    to_agent: Optional[str] = Query(None, description="Filter by receiving agent"),
    interaction_type: Optional[InteractionType] = Query(None),
    conversation_id: Optional[UUID] = Query(None),
    since: Optional[datetime] = Query(None, description="Filter by created_at >= since"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List agent interactions with filters.

    Example:
        GET /api/v1/agent-interactions?from_agent=oscar&to_agent=sarah&limit=10
    """
    query = db.query(AgentInteraction)

    if from_agent:
        query = query.filter(AgentInteraction.from_agent == from_agent)
    if to_agent:
        query = query.filter(AgentInteraction.to_agent == to_agent)
    if interaction_type:
        query = query.filter(AgentInteraction.interaction_type == interaction_type)
    if conversation_id:
        query = query.filter(AgentInteraction.conversation_id == conversation_id)
    if since:
        query = query.filter(AgentInteraction.created_at >= since)

    query = query.order_by(AgentInteraction.created_at.desc())
    query = query.limit(limit).offset(offset)

    interactions = await query.all()
    return interactions


@router.get("/{interaction_id}", response_model=AgentInteraction)
async def get_interaction(
    interaction_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific agent interaction by ID."""
    interaction = await db.get(AgentInteraction, interaction_id)

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    return interaction


@router.get("/stats/summary")
async def get_interaction_stats(
    since: Optional[datetime] = Query(None, description="Stats since this timestamp"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get summary statistics for agent interactions.

    Returns:
        {
            "total_interactions": 1250,
            "by_type": {"query": 800, "notification": 450},
            "by_agent": {"oscar": 500, "sarah": 400, "maya": 350},
            "avg_latency_ms": 1250,
            "p95_latency_ms": 2500
        }
    """
    query = db.query(AgentInteraction)

    if since:
        query = query.filter(AgentInteraction.created_at >= since)
    else:
        # Default to last 24 hours
        since = datetime.utcnow() - timedelta(hours=24)
        query = query.filter(AgentInteraction.created_at >= since)

    interactions = await query.all()

    # Calculate stats
    total = len(interactions)
    by_type = {}
    by_agent = {}
    latencies = [i.latency_ms for i in interactions if i.latency_ms is not None]

    for interaction in interactions:
        # By type
        itype = interaction.interaction_type.value
        by_type[itype] = by_type.get(itype, 0) + 1

        # By agent
        from_agent = interaction.from_agent
        by_agent[from_agent] = by_agent.get(from_agent, 0) + 1

    # Latency stats
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0

    return {
        "total_interactions": total,
        "by_type": by_type,
        "by_agent": by_agent,
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": p95_latency,
        "since": since.isoformat()
    }


@router.delete("/{interaction_id}")
async def delete_interaction(
    interaction_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete an agent interaction."""
    interaction = await db.get(AgentInteraction, interaction_id)

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    await db.delete(interaction)
    await db.commit()

    return {"status": "deleted", "interaction_id": str(interaction_id)}
```

**Mount API in main.py:**
```python
# main.py

from apex_memory.api import agent_interactions

app.include_router(agent_interactions.router)
```

**Test API:**
```bash
# List all interactions
curl http://localhost:8000/api/v1/agent-interactions

# Filter by agent
curl "http://localhost:8000/api/v1/agent-interactions?from_agent=oscar&to_agent=sarah"

# Get stats
curl http://localhost:8000/api/v1/agent-interactions/stats/summary
```

**Success Criteria:**
- All API endpoints working
- Can query interactions by agent, type, conversation
- Stats endpoint returns accurate metrics
- API documented in FastAPI Swagger UI

---

### Task 4.3: AgentInteractionService (Days 6-7)

**Create service:**
`apex_memory/services/agent_interaction_service.py`

```python
"""
Agent Interaction Service.

Manages agent-to-agent interactions with knowledge graph integration.
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from apex_memory.models.agent_interaction import AgentInteraction, InteractionType
from apex_memory.services.agent_communication import agent_comm
from apex_memory.services.conversation_entity_extractor import ConversationEntityExtractor
from apex_memory.database import get_db_session

logger = logging.getLogger(__name__)


class AgentInteractionService:
    """Service for managing agent interactions."""

    def __init__(self):
        self.comm = agent_comm
        self.entity_extractor = ConversationEntityExtractor()

    async def process_interaction(
        self,
        interaction_id: UUID
    ):
        """
        Process an agent interaction for knowledge graph ingestion.

        Extracts entities from the interaction and creates a Graphiti episode.

        Args:
            interaction_id: Interaction to process

        Steps:
            1. Fetch interaction from database
            2. Extract entities from query + response
            3. Create Graphiti episode
            4. Update interaction metadata
        """
        async with get_db_session() as session:
            interaction = await session.get(AgentInteraction, interaction_id)

            if not interaction:
                logger.error(f"Interaction {interaction_id} not found")
                return

            # Combine query and response for entity extraction
            text = f"{interaction.query_text or ''} {interaction.response_text or ''}"

            # Extract entities
            entities = await self.entity_extractor.extract_entities(
                text=text,
                conversation_id=interaction.conversation_id,
                agent_id=interaction.from_agent
            )

            logger.info(f"Extracted {len(entities)} entities from interaction {interaction_id}")

            # TODO: Create Graphiti episode (Task 4.4)

            # Update interaction metadata
            interaction.metadata["entities_extracted"] = len(entities)
            interaction.metadata["processed_at"] = datetime.utcnow().isoformat()

            await session.commit()

    async def get_agent_collaboration_stats(
        self,
        agent_id: str,
        days: int = 30
    ) -> dict:
        """
        Get collaboration statistics for an agent.

        Args:
            agent_id: Agent to analyze
            days: Number of days to look back

        Returns:
            {
                "total_interactions": 150,
                "queries_sent": 80,
                "queries_received": 70,
                "most_frequent_collaborator": "sarah",
                "avg_response_time_ms": 1250
            }
        """
        async with get_db_session() as session:
            # Fetch interactions
            since = datetime.utcnow() - timedelta(days=days)

            # Queries sent
            sent_query = session.query(AgentInteraction).filter(
                AgentInteraction.from_agent == agent_id,
                AgentInteraction.created_at >= since
            )
            sent = await sent_query.all()

            # Queries received
            received_query = session.query(AgentInteraction).filter(
                AgentInteraction.to_agent == agent_id,
                AgentInteraction.created_at >= since
            )
            received = await received_query.all()

            # Calculate stats
            total = len(sent) + len(received)
            queries_sent = len([i for i in sent if i.interaction_type == InteractionType.QUERY])
            queries_received = len([i for i in received if i.interaction_type == InteractionType.QUERY])

            # Most frequent collaborator
            collaborators = {}
            for interaction in sent + received:
                other_agent = interaction.to_agent if interaction.from_agent == agent_id else interaction.from_agent
                collaborators[other_agent] = collaborators.get(other_agent, 0) + 1

            most_frequent = max(collaborators.items(), key=lambda x: x[1])[0] if collaborators else None

            # Average response time
            latencies = [i.latency_ms for i in sent if i.latency_ms is not None]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0

            return {
                "agent_id": agent_id,
                "total_interactions": total,
                "queries_sent": queries_sent,
                "queries_received": queries_received,
                "most_frequent_collaborator": most_frequent,
                "avg_response_time_ms": round(avg_latency, 2),
                "days_analyzed": days
            }


# Singleton instance
agent_interaction_service = AgentInteractionService()
```

**Success Criteria:**
- Service can process interactions
- Entity extraction working
- Collaboration stats accurate

---

### Task 4.4: Knowledge Graph Integration (Days 8-9)

**Goal:** Create Graphiti episodes from agent interactions

**Implementation:** Integration with existing Graphiti service

```python
# In agent_interaction_service.py

from apex_memory.services.graphiti_service import graphiti_service

async def process_interaction(self, interaction_id: UUID):
    """Process interaction and create Graphiti episode."""
    # ... (existing code)

    # Create Graphiti episode
    episode = await graphiti_service.create_episode(
        name=f"Agent Interaction: {interaction.from_agent} → {interaction.to_agent}",
        content=f"Query: {interaction.query_text}\nResponse: {interaction.response_text}",
        source_description=f"Agent interaction between {interaction.from_agent} and {interaction.to_agent}",
        metadata={
            "interaction_id": str(interaction.id),
            "from_agent": interaction.from_agent,
            "to_agent": interaction.to_agent,
            "interaction_type": interaction.interaction_type.value
        }
    )

    logger.info(f"Created Graphiti episode for interaction {interaction_id}")
```

**Success Criteria:**
- Graphiti episodes created from interactions
- Knowledge graph enriched with agent collaboration patterns
- Can query "Oscar asked Sarah about budgets" in graph

---

### Task 4.5: Testing & Validation (Day 10)

**Test Plan:** 15 tests across integration and unit testing

```python
# tests/unit/test_nats_service.py (3 tests)
- test_nats_connect
- test_nats_pub_sub
- test_nats_request_reply

# tests/unit/test_agent_communication.py (4 tests)
- test_send_query
- test_send_notification
- test_register_handler
- test_log_interaction

# tests/unit/test_agent_interaction_service.py (3 tests)
- test_process_interaction
- test_get_collaboration_stats
- test_entity_extraction_from_interaction

# tests/integration/test_agent_to_agent_flow.py (5 tests)
- test_end_to_end_query_flow
- test_multiple_agent_collaboration
- test_interaction_logged_to_postgres
- test_graphiti_episode_created
- test_latency_within_target
```

**Success Criteria:**
- All 15 tests passing
- <20ms P95 latency for agent messaging
- 100% of interactions logged to PostgreSQL
- Knowledge graph enriched from interactions

---

## Success Metrics

### Functional Requirements
- ✅ NATS server running and healthy
- ✅ Agent-to-agent messaging working (pub/sub + request-reply)
- ✅ All interactions logged to agent_interactions table
- ✅ Knowledge graph enriched from agent collaborations
- ✅ API endpoints for querying interactions

### Performance Requirements
- ✅ <20ms agent messaging latency (P95)
- ✅ <5ms NATS publish latency
- ✅ <100ms PostgreSQL write latency
- ✅ Background Graphiti ingestion <20s

### Testing Requirements
- ✅ All 15 Phase 4 tests passing
- ✅ Integration tests validate end-to-end flow
- ✅ Load tests show 10,000 interactions/min capacity

---

## Rollback Plan

If Phase 4 causes issues:

**1. Disable NATS Communication**
```bash
# Set in .env
NATS_ENABLE_AGENT_COMMUNICATION=false

# Restart services
docker-compose restart apex-api
```

**2. Stop NATS Server**
```bash
docker-compose stop nats
```

**3. Rollback Database Migration**
```bash
alembic downgrade -1
```

**4. Verify System Health**
```bash
curl http://localhost:8000/health
# Should show system operational without NATS
```

---

## Next Steps

**After Phase 4 completion:**
- Move to Phase 5: Proactive Features
- Enable multi-agent autonomous workflows
- Implement context-triggered suggestions
- Deploy to production

---

**Last Updated:** 2025-11-15
**Status:** Planning Complete - Ready for Implementation
**Timeline:** 2 weeks (10 working days)
**Test Target:** 15 tests
