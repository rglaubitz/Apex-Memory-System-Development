# 06 - Data Models

## 🎯 Purpose

Provides type-safe Pydantic models for all data structures: documents, users, conversations, entities, and API requests/responses. Ensures data validation, serialization, and consistency across the system.

## 🛠 Technical Stack

- **Pydantic 2.x:** Data validation and serialization
- **Python Type Hints:** Static typing
- **UUID:** Unique identifiers for all entities
- **Datetime:** Timezone-aware timestamps

## 📂 Key Files (9 Models)

### Core Data Models

**1. document.py** (14,188 bytes)
```python
class Document(BaseModel):
    """Document with chunks and metadata."""
    uuid: UUID
    title: str
    source: str
    chunks: List[Chunk]
    entities: List[Entity]
    created_at: datetime
    updated_at: datetime
```

**2. structured_data.py** (3,725 bytes)
```python
class StructuredData(BaseModel):
    """JSON/API data with JSONB storage."""
    uuid: UUID
    source: str
    data_type: StructuredDataType  # INVOICE, ORDER, etc.
    content: dict  # JSONB field
```

**3. user.py** (3,896 bytes)
```python
class User(BaseModel):
    """User authentication and profile."""
    uuid: UUID
    email: EmailStr
    hashed_password: str
    full_name: str
    is_active: bool = True
```

**4. conversation.py** (8,163 bytes)
```python
class Conversation(BaseModel):
    """AI conversation with messages."""
    uuid: UUID
    user_id: UUID
    title: str
    messages: List[Message]
    created_at: datetime
```

**5. briefing.py** (3,111 bytes)
```python
class Briefing(BaseModel):
    """Daily AI briefing."""
    uuid: UUID
    user_id: UUID
    date: date
    sections: List[BriefingSection]
```

**6. achievement.py** (4,671 bytes)
```python
class Achievement(BaseModel):
    """User achievement tracking."""
    uuid: UUID
    user_id: UUID
    achievement_type: str  # first_query, 10_queries, etc.
    unlocked_at: datetime
```

**7. user_metric.py** (5,254 bytes)
```python
class UserMetric(BaseModel):
    """User activity metrics."""
    user_id: UUID
    total_queries: int
    total_conversations: int
    avg_query_latency_ms: float
```

**8. conversation_share.py** (1,637 bytes)
```python
class ConversationShare(BaseModel):
    """Shareable conversation link."""
    share_id: UUID
    conversation_id: UUID
    expires_at: Optional[datetime]
```

**9. graphiti_entities.py** (13,021 bytes)
```python
class GraphitiEntity(BaseModel):
    """Temporal entity version."""
    name: str
    entity_type: str
    valid_from: datetime
    valid_to: Optional[datetime]
    transaction_time: datetime
```

## Example Usage

```python
from apex_memory.models import Document, Chunk, Entity

# Create document
doc = Document(
    uuid=uuid4(),
    title="Q4 Financial Report",
    source="local_upload",
    chunks=[
        Chunk(text="Revenue increased 20%...", chunk_index=0)
    ],
    entities=[
        Entity(name="ACME Corp", entity_type="Organization")
    ],
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# Automatic validation
print(doc.model_dump_json())  # Serialize to JSON
```

---

**Previous Component:** [05-Core-Services](../05-Core-Services/README.md)
**Next Component:** [07-Database-Writers](../07-Database-Writers/README.md)
