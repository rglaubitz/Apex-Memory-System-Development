# External Integration Specifications

This document provides detailed implementation specifications for each external platform integration.

## Table of Contents

- [FrontApp](#frontapp)
- [Salesforce](#salesforce)
- [HubSpot](#hubspot)
- [Google Analytics](#google-analytics)
- [Mixpanel](#mixpanel)

---

## FrontApp

**Priority:** High
**Use Case:** Ingest customer conversation history for context-aware support queries
**Status:** Planned

### Overview

FrontApp is a customer communication platform that consolidates emails, chats, and social messages. Integrating with FrontApp allows Apex to:

- Ingest conversation history for semantic search
- Extract customer interaction patterns
- Provide context-aware query responses
- Track support trends over time

### API Documentation

- **API Reference:** https://dev.frontapp.com/reference/introduction
- **Authentication:** OAuth 2.0
- **Rate Limits:** 300 requests/minute (5 req/sec)
- **Webhook Support:** Yes (real-time updates)

### Authentication Flow

**OAuth 2.0 Configuration:**

```python
# config/settings.py
FRONTAPP_CLIENT_ID = os.getenv("FRONTAPP_CLIENT_ID")
FRONTAPP_CLIENT_SECRET = os.getenv("FRONTAPP_CLIENT_SECRET")
FRONTAPP_REDIRECT_URI = "https://apex.example.com/integrations/frontapp/callback"

FRONTAPP_SCOPES = [
    "conversations:read",
    "messages:read",
    "contacts:read",
    "tags:read",
    "comments:read"
]
```

**OAuth Flow Implementation:**

```python
# src/apex_memory/integrations/frontapp/auth.py
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='frontapp',
    client_id=FRONTAPP_CLIENT_ID,
    client_secret=FRONTAPP_CLIENT_SECRET,
    authorize_url='https://app.frontapp.com/oauth/authorize',
    access_token_url='https://app.frontapp.com/oauth/token',
    api_base_url='https://api2.frontapp.com/',
    client_kwargs={'scope': ' '.join(FRONTAPP_SCOPES)}
)

@router.get("/integrations/frontapp/connect")
async def frontapp_connect(request: Request):
    """Initiate FrontApp OAuth flow."""
    redirect_uri = request.url_for('frontapp_callback')
    return await oauth.frontapp.authorize_redirect(request, redirect_uri)

@router.get("/integrations/frontapp/callback")
async def frontapp_callback(request: Request):
    """Handle OAuth callback and store tokens."""
    token = await oauth.frontapp.authorize_access_token(request)
    # Store token in database
    await store_integration_token("frontapp", token)
    return {"status": "connected"}
```

### Data Model

**Conversation Schema:**

```python
from pydantic import BaseModel
from datetime import datetime

class FrontConversation(BaseModel):
    conversation_id: str
    subject: str
    status: str  # archived, deleted, open, etc.
    assignee: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    messages: List[FrontMessage]

class FrontMessage(BaseModel):
    message_id: str
    conversation_id: str
    author: str
    body: str  # HTML content
    body_text: str  # Plain text
    created_at: datetime
    recipients: List[str]
    attachments: List[FrontAttachment]

class FrontAttachment(BaseModel):
    filename: str
    url: str
    content_type: str
    size: int
```

### API Endpoints

**1. List Conversations**

```python
GET https://api2.frontapp.com/conversations
Parameters:
  - q: Search query (optional)
  - page_token: Pagination token
  - limit: Results per page (default: 50, max: 100)

Response:
{
  "_pagination": {
    "next": "https://api2.frontapp.com/conversations?page_token=abc123"
  },
  "_results": [
    {
      "id": "cnv_123abc",
      "subject": "Support request",
      "status": "open",
      "assignee": {...},
      "tags": [...],
      "created_at": 1633027200,
      "updated_at": 1633113600
    }
  ]
}
```

**2. Get Conversation Messages**

```python
GET https://api2.frontapp.com/conversations/{conversation_id}/messages

Response:
{
  "_results": [
    {
      "id": "msg_456def",
      "type": "email",
      "body": "<html>Message body</html>",
      "text": "Message body",
      "author": {...},
      "recipients": [...],
      "created_at": 1633027200,
      "attachments": [...]
    }
  ]
}
```

### Implementation

**Sync Manager:**

```python
# src/apex_memory/integrations/frontapp/sync.py
from apex_memory.integrations.base import BaseSyncManager

class FrontAppSyncManager(BaseSyncManager):
    """Manage FrontApp data synchronization."""

    async def sync_conversations(
        self,
        since: Optional[datetime] = None,
        full_sync: bool = False
    ) -> dict:
        """Sync conversations from FrontApp."""

        # Get access token
        token = await self.get_access_token("frontapp")

        # Fetch conversations
        conversations = []
        page_token = None

        while True:
            response = await self._fetch_conversations(
                token, page_token, since
            )

            conversations.extend(response["_results"])

            # Check for next page
            if "_pagination" in response and "next" in response["_pagination"]:
                page_token = self._extract_page_token(
                    response["_pagination"]["next"]
                )
            else:
                break

            # Rate limit: 5 req/sec
            await asyncio.sleep(0.2)

        # Process conversations
        for conv in conversations:
            await self._process_conversation(conv)

        return {
            "conversations_synced": len(conversations),
            "status": "success"
        }

    async def _process_conversation(self, conv: dict):
        """Process and ingest a single conversation."""

        # Fetch messages
        messages = await self._fetch_messages(conv["id"])

        # Extract entities
        entities = {
            "conversation_id": conv["id"],
            "subject": conv["subject"],
            "participants": self._extract_participants(messages),
            "tags": conv.get("tags", []),
            "messages": []
        }

        # Process each message
        for msg in messages:
            entities["messages"].append({
                "message_id": msg["id"],
                "author": msg["author"]["email"],
                "content": msg["text"],
                "timestamp": datetime.fromtimestamp(msg["created_at"]),
                "sentiment": await self._analyze_sentiment(msg["text"])
            })

        # Ingest into Apex
        await self.ingestion_service.ingest_structured_data(
            source="frontapp",
            data_type="conversation",
            data=entities
        )
```

**Webhook Handler:**

```python
# src/apex_memory/api/webhooks/frontapp.py
import hmac
import hashlib

@router.post("/webhooks/frontapp")
async def frontapp_webhook(
    request: Request,
    x_front_signature: str = Header(...)
):
    """Handle FrontApp webhooks for real-time updates."""

    # Get webhook secret from settings
    webhook_secret = settings.frontapp_webhook_secret

    # Read request body
    body = await request.body()

    # Validate signature
    expected_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, x_front_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse webhook payload
    payload = await request.json()

    # Queue for processing (don't block webhook response)
    await queue_webhook_processing("frontapp", payload)

    return {"status": "received"}


async def process_frontapp_webhook(payload: dict):
    """Process FrontApp webhook event."""

    event_type = payload["type"]

    if event_type == "message":
        # New message in conversation
        conversation_id = payload["conversation"]["id"]
        await sync_manager.sync_conversation(conversation_id)

    elif event_type == "conversation":
        # Conversation updated (status, tags, etc.)
        conversation_id = payload["id"]
        await sync_manager.update_conversation_metadata(conversation_id)

    elif event_type == "comment":
        # Internal comment added
        conversation_id = payload["conversation"]["id"]
        await sync_manager.sync_conversation_comments(conversation_id)
```

### Webhook Events

FrontApp supports the following webhook events:

- `message`: New message in conversation
- `conversation`: Conversation created/updated
- `comment`: Internal comment added
- `tag`: Tag added/removed
- `assignment`: Conversation assigned/unassigned

**Webhook Configuration:**

```bash
# Configure webhook in FrontApp dashboard
URL: https://apex.example.com/webhooks/frontapp
Events: message, conversation, comment, tag
Secret: <generate-random-secret>
```

### Data Mapping

**FrontApp → Apex Entity Mapping:**

| FrontApp Field | Apex Entity | Notes |
|---------------|------------|-------|
| `conversation.id` | `Document.uuid` | Conversation as document |
| `conversation.subject` | `Document.title` | |
| `conversation.tags` | `Entity.tags` | Extracted as entities |
| `message.text` | `Chunk.content` | Each message = chunk |
| `author.email` | `Entity(type=person)` | Contact entity |
| `created_at` | `Document.created_at` | Bi-temporal tracking |

### Testing

**Mock API Responses:**

```python
# tests/integrations/frontapp/test_sync.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_sync_conversations():
    """Test FrontApp conversation sync."""

    mock_response = {
        "_results": [
            {
                "id": "cnv_123",
                "subject": "Test conversation",
                "status": "open",
                "created_at": 1633027200,
                "tags": []
            }
        ]
    }

    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )

        sync_manager = FrontAppSyncManager()
        result = await sync_manager.sync_conversations()

        assert result["conversations_synced"] == 1
        assert result["status"] == "success"
```

### Performance Considerations

**Rate Limiting:**
- FrontApp: 300 requests/minute (5 req/sec)
- Implementation: Add 200ms delay between requests
- Bulk operations: Use pagination (100 items/page)

**Data Volume Estimates:**
- Average conversation: 5-10 messages
- Average message size: 500 bytes
- 1000 conversations/day = ~5MB/day
- Monthly storage: ~150MB

**Sync Strategy:**
- **Initial sync:** Full history (batch overnight)
- **Incremental sync:** Every 15 minutes
- **Real-time updates:** Webhooks for immediate updates

### Error Handling

**Retry Logic:**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def _fetch_with_retry(self, url: str, token: str):
    """Fetch with automatic retry."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            if response.status == 429:  # Rate limit
                retry_after = int(response.headers.get("Retry-After", 60))
                await asyncio.sleep(retry_after)
                raise Exception("Rate limited")

            response.raise_for_status()
            return await response.json()
```

### Monitoring Metrics

**Key Metrics to Track:**

```python
# Prometheus metrics
frontapp_conversations_synced = Counter(
    'frontapp_conversations_synced_total',
    'Total FrontApp conversations synced'
)

frontapp_sync_duration = Histogram(
    'frontapp_sync_duration_seconds',
    'Time taken to sync FrontApp data'
)

frontapp_api_errors = Counter(
    'frontapp_api_errors_total',
    'Total FrontApp API errors',
    ['error_type']
)

frontapp_webhook_events = Counter(
    'frontapp_webhook_events_total',
    'Total webhook events received',
    ['event_type']
)
```

### Security Considerations

**Token Storage:**
- Store OAuth tokens encrypted in database
- Rotate tokens every 60 days
- Use separate service account (not personal)

**Webhook Validation:**
- Always validate HMAC signature
- Use constant-time comparison
- Log invalid signature attempts

**Data Privacy:**
- Respect conversation privacy settings
- PII detection and redaction
- Compliance with data retention policies

---

## Salesforce

**Priority:** Medium
**Status:** Future

(Detailed specification to be added)

---

## HubSpot

**Priority:** Medium
**Status:** Future

(Detailed specification to be added)

---

## Google Analytics

**Priority:** Low
**Status:** Future

(Detailed specification to be added)

---

## Mixpanel

**Priority:** Low
**Status:** Future

(Detailed specification to be added)

---

**Last Updated:** 2025-10-10
**Next Review:** After FrontApp implementation complete
