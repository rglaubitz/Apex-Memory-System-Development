# TROUBLESHOOTING.md - UI/UX Enhancements Common Issues & Solutions

**Project:** Apex Memory System - UI/UX Enhancements
**Purpose:** Comprehensive troubleshooting guide for all phases
**Last Updated:** 2025-10-21

---

## Quick Reference

**Common Issues by Symptom:**

| Symptom | Phase | Jump To |
|---------|-------|---------|
| "401 Unauthorized" errors | Phase 1 | [Authentication Issues](#phase-1-authentication-issues) |
| JWT token expired | Phase 1 | [Token Expiration](#issue-11-jwt-token-expired) |
| Cannot register duplicate email | Phase 1 | [Registration Errors](#issue-12-duplicate-email-registration) |
| Conversation not loading | Phase 2 | [Conversation Issues](#phase-2-conversation-issues) |
| LLM responses slow/timeout | Phase 2 | [LLM Performance](#issue-23-slow-llm-responses) |
| Citations not showing | Phase 2 | [Citation Problems](#issue-24-citations-not-displaying) |
| Streaming connection drops | Phase 2.5 | [Streaming Issues](#phase-25-streaming-issues) |
| Tools not executing | Phase 2.5 | [Tool Execution](#issue-251-tools-not-executing) |
| Artifacts sidebar empty | Phase 2.5 | [Artifacts Problems](#issue-253-artifacts-sidebar-empty) |
| UI looks "busy" not minimal | Phase 3 | [Design System](#phase-3-design-system-issues) |
| Gamification too flashy | Phase 3 | [Gamification Issues](#issue-31-gamification-too-flashy) |
| Cache not working | Phase 4 | [Caching Issues](#phase-4-caching-issues) |
| Tests failing | All | [Testing Issues](#testing-issues) |

---

## Phase 1: Authentication Issues

### Issue 1.1: JWT Token Expired

**Symptom:**
```
401 Unauthorized
{"detail": "Could not validate credentials"}
```

**Cause:** Access token has expired (default: 30 minutes)

**Solution:**

1. **Check token expiration:**
```python
from jose import jwt
from apex_memory.config import settings

token = "your-token-here"
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
print(f"Expires at: {payload['exp']}")

import datetime
exp_time = datetime.datetime.fromtimestamp(payload['exp'])
print(f"Expired: {exp_time < datetime.datetime.utcnow()}")
```

2. **Implement token refresh:**
```typescript
// Frontend: src/contexts/AuthContext.tsx
useEffect(() => {
  const refreshToken = async () => {
    try {
      const response = await axios.post('/api/v1/auth/refresh', null, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setToken(response.data.access_token);
      localStorage.setItem('auth_token', response.data.access_token);
    } catch (error) {
      // Token refresh failed, logout user
      logout();
    }
  };

  // Refresh token 5 minutes before expiration
  const interval = setInterval(refreshToken, 25 * 60 * 1000); // 25 minutes
  return () => clearInterval(interval);
}, [token]);
```

3. **Increase token lifetime (if needed):**
```python
# apex_memory/config.py
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increase from 30 to 60 minutes
```

**Prevention:**
- Implement automatic token refresh 5 minutes before expiration
- Store refresh tokens for longer sessions
- Show "session expiring" warning to users

---

### Issue 1.2: Duplicate Email Registration

**Symptom:**
```
400 Bad Request
{"detail": "Email already registered"}
```

**Cause:** User trying to register with email that already exists

**Solution:**

1. **Check if email exists before registration:**
```python
# Backend: services/auth_service.py
def is_email_available(self, email: str) -> bool:
    """Check if email is available."""
    existing_user = self.db.query(UserDB).filter(
        UserDB.email == email
    ).first()
    return existing_user is None
```

2. **Frontend validation:**
```typescript
// Check email availability before form submission
const checkEmailAvailability = async (email: string) => {
  try {
    const response = await axios.get(`/api/v1/auth/check-email?email=${email}`);
    return response.data.available;
  } catch (error) {
    return false;
  }
};

// In registration form
const handleEmailBlur = async (e: React.FocusEvent<HTMLInputElement>) => {
  const email = e.target.value;
  const available = await checkEmailAvailability(email);

  if (!available) {
    setEmailError('This email is already registered');
  }
};
```

3. **Better error messages:**
```python
# Backend: api/auth.py
if existing_user:
    raise HTTPException(
        status_code=400,
        detail="This email is already registered. Try logging in or use password reset."
    )
```

**Prevention:**
- Real-time email availability checking during registration
- Clear error messages with actionable next steps
- Suggest "Login" or "Password Reset" options

---

### Issue 1.3: Password Hashing Too Slow

**Symptom:**
- Registration/login takes 5+ seconds
- High CPU usage during auth operations

**Cause:** Bcrypt work factor too high

**Solution:**

1. **Check current work factor:**
```python
# apex_memory/services/auth_service.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Default bcrypt rounds is 12, which is good for production
# If too slow, reduce to 10 (not recommended for production)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=10  # Reduce for development only
)
```

2. **Use environment-specific configuration:**
```python
# config.py
import os

# Use lower rounds in development, higher in production
BCRYPT_ROUNDS = 10 if os.getenv("ENV") == "development" else 12
```

3. **Async password hashing (for high load):**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def hash_password_async(password: str) -> str:
    """Hash password asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        pwd_context.hash,
        password
    )
```

**Prevention:**
- Use appropriate bcrypt rounds (10-12 is standard)
- Consider async hashing for high-traffic scenarios
- Monitor auth endpoint performance

---

### Issue 1.4: CORS Errors in Frontend

**Symptom:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/auth/login'
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Cause:** Backend not configured to allow frontend origin

**Solution:**

1. **Configure CORS in FastAPI:**
```python
# apex_memory/main.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://your-production-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **For development (allow all origins):**
```python
# Development only - NOT for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **Check preflight requests:**
```bash
# Test CORS with curl
curl -X OPTIONS http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

**Prevention:**
- Configure CORS during initial setup
- Use environment variables for allowed origins
- Test with frontend before deploying

---

### Issue 1.5: Protected Routes Not Working

**Symptom:**
- User logged in but still redirected to login page
- Protected routes accessible without authentication

**Cause:** Protected route component not checking auth status correctly

**Solution:**

1. **Check ProtectedRoute implementation:**
```typescript
// frontend/src/components/ProtectedRoute.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function ProtectedRoute({ requireAdmin = false }: { requireAdmin?: boolean }) {
  const { isAuthenticated, isLoading, user } = useAuth();

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div>Loading...</div>
      </div>
    );
  }

  // Not authenticated - redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Admin required but user is not admin
  if (requireAdmin && user?.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
```

2. **Verify auth context loads token on mount:**
```typescript
// AuthContext.tsx
useEffect(() => {
  const loadToken = async () => {
    const storedToken = localStorage.getItem('auth_token');

    if (storedToken) {
      setToken(storedToken);

      try {
        // Verify token is still valid
        const response = await axios.get('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${storedToken}` }
        });
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (error) {
        // Token invalid, clear it
        localStorage.removeItem('auth_token');
        setToken(null);
        setIsAuthenticated(false);
      }
    }

    setIsLoading(false);
  };

  loadToken();
}, []);
```

3. **Debug auth state:**
```typescript
// Add to component for debugging
const { isAuthenticated, isLoading, user, token } = useAuth();

console.log('Auth State:', {
  isAuthenticated,
  isLoading,
  user,
  hasToken: !!token
});
```

**Prevention:**
- Always wait for `isLoading` to be false before checking auth
- Verify token on app mount
- Clear invalid tokens from localStorage

---

## Phase 2: Conversation Issues

### Issue 2.1: Conversations Not Loading

**Symptom:**
- Blank screen or spinner never completes
- Console error: "Failed to load conversations"

**Cause:** Backend endpoint error or frontend not handling response

**Solution:**

1. **Check backend endpoint:**
```bash
# Test endpoint directly
curl -X GET "http://localhost:8000/api/v1/conversations/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

2. **Debug frontend request:**
```typescript
// Add error logging to ConversationHub.tsx
const loadConversations = async () => {
  try {
    console.log('Loading conversations...');
    console.log('Token:', token);

    const response = await axios.get('/api/v1/conversations/', {
      headers: { Authorization: `Bearer ${token}` },
    });

    console.log('Response:', response.data);
    setConversations(response.data);
  } catch (error) {
    console.error('Failed to load conversations:', error);
    console.error('Error details:', error.response?.data);

    // Show error to user
    setError('Failed to load conversations. Please try again.');
  }
};
```

3. **Check database connection:**
```python
# Backend: Check if database is accessible
from apex_memory.database import SessionLocal

def test_db_connection():
    try:
        db = SessionLocal()
        # Try a simple query
        from apex_memory.models.conversation import ConversationDB
        count = db.query(ConversationDB).count()
        print(f"Database accessible. Conversations: {count}")
        db.close()
    except Exception as e:
        print(f"Database error: {e}")

test_db_connection()
```

**Prevention:**
- Add error boundaries in React components
- Implement retry logic for failed requests
- Show user-friendly error messages

---

### Issue 2.2: Message Not Sending

**Symptom:**
- User types message and clicks send, but nothing happens
- Loading state never completes

**Cause:** LLM API error, network timeout, or missing conversation context

**Solution:**

1. **Check Anthropic API key:**
```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Test API key works
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

2. **Add timeout handling:**
```python
# Backend: services/conversation_service.py
from httpx import Timeout

self.anthropic = Anthropic(
    api_key=settings.ANTHROPIC_API_KEY,
    timeout=Timeout(60.0, connect=10.0)  # 60s total, 10s connect
)
```

3. **Frontend timeout:**
```typescript
// Add timeout to axios request
const sendMessage = async (content: string) => {
  try {
    const response = await axios.post(
      `/api/v1/conversations/${conversationId}/messages`,
      { content },
      {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 60000  // 60 second timeout
      }
    );
    // ... handle response
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      setError('Request timed out. Please try again.');
    } else {
      setError('Failed to send message.');
    }
  }
};
```

4. **Check LLM service logs:**
```python
# Add logging to conversation service
import logging

logger = logging.getLogger(__name__)

async def process_message(self, conversation_uuid: UUID, user_uuid: UUID, message_content: str):
    logger.info(f"Processing message for conversation {conversation_uuid}")

    try:
        # ... existing code
        response = self.anthropic.messages.create(...)
        logger.info(f"LLM response received: {len(response.content[0].text)} chars")
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise
```

**Prevention:**
- Set appropriate timeouts (30-60 seconds for LLM)
- Show progress indicators during long operations
- Implement request cancellation on unmount

---

### Issue 2.3: Slow LLM Responses

**Symptom:**
- Messages take 10+ seconds to receive response
- User sees loading spinner for extended time

**Cause:** Large context window, inefficient query routing, or API rate limiting

**Solution:**

1. **Optimize context retrieval:**
```python
# Limit context size
async def _retrieve_context(self, query: str) -> List[dict]:
    results = await self.query_router.route_query(query)

    # Only return top 3 results instead of 5
    context = []
    for result in results[:3]:  # Reduced from 5
        context.append({
            "title": result.get("title", "Unknown"),
            "content": result.get("content", "")[:500],  # Limit content length
            "score": result.get("score", 0.0),
            "uuid": result.get("uuid"),
        })

    return context
```

2. **Reduce max_tokens:**
```python
# Generate shorter responses
response = self.anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,  # Reduced from 4096
    system=system_prompt,
    messages=messages,
)
```

3. **Implement streaming (Phase 2.5):**
```python
# Use streaming for faster perceived performance
response = await self.anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=messages,
    stream=True,  # Enable streaming
)

async for event in response:
    # Send partial responses to frontend
    yield event
```

4. **Monitor API performance:**
```python
import time

start = time.time()
response = self.anthropic.messages.create(...)
duration = time.time() - start

logger.info(f"LLM request took {duration:.2f} seconds")

# Alert if taking too long
if duration > 10:
    logger.warning(f"Slow LLM response: {duration:.2f}s")
```

**Prevention:**
- Use streaming for real-time responses
- Limit context to top 3-5 results
- Cache frequently asked questions
- Monitor and alert on slow responses

---

### Issue 2.4: Citations Not Displaying

**Symptom:**
- AI responds but no citations shown
- Citations object is empty or null

**Cause:** Context retrieval failing or citation extraction not working

**Solution:**

1. **Debug context retrieval:**
```python
async def _retrieve_context(self, query: str) -> List[dict]:
    results = await self.query_router.route_query(query)

    # Log what we got
    logger.info(f"Retrieved {len(results)} context results for query: {query}")
    for i, result in enumerate(results[:5]):
        logger.info(f"Result {i}: {result.get('title', 'No title')} (score: {result.get('score', 0)})")

    # ... rest of method
```

2. **Check citation generation:**
```python
async def _generate_response(self, query: str, context: List[dict], history: List[dict]):
    # ... existing code

    # Ensure citations are created when context exists
    citations = []
    for ctx in context:
        if ctx.get("uuid"):  # Make sure UUID exists
            citations.append(
                Citation(
                    document_uuid=ctx["uuid"],
                    document_title=ctx.get("title", "Unknown"),
                    relevant_excerpt=ctx.get("content", "")[:200],
                    confidence_score=ctx.get("score", 0.0),
                )
            )

    logger.info(f"Generated {len(citations)} citations")
    return ai_response, citations
```

3. **Frontend display check:**
```typescript
// Ensure citations are displayed when present
{message.citations && message.citations.length > 0 && (
  <div className="mt-3 pt-3 border-t border-gray-300">
    <div className="text-sm font-medium mb-2">
      Sources: ({message.citations.length})
    </div>
    {message.citations.map((citation, idx) => (
      <div key={citation.document_uuid} className="text-sm bg-white bg-opacity-50 rounded p-2 mb-2">
        <div className="font-medium">
          [{idx + 1}] {citation.document_title}
        </div>
        <div className="text-xs mt-1 text-gray-600">
          {citation.relevant_excerpt}
        </div>
        <div className="text-xs mt-1 text-gray-400">
          Confidence: {(citation.confidence_score * 100).toFixed(1)}%
        </div>
      </div>
    ))}
  </div>
)}
```

4. **Verify query router returns results:**
```python
# Test query router directly
from apex_memory.query_router.router import QueryRouter

router = QueryRouter()
results = await router.route_query("test query about ACME")

print(f"Found {len(results)} results")
for result in results:
    print(f"- {result['title']}: {result.get('uuid', 'NO UUID')}")
```

**Prevention:**
- Log context retrieval at each step
- Ensure document UUIDs are present in query results
- Test with sample queries that should return results
- Add fallback UI when no citations available

---

### Issue 2.5: Conversation History Not Persisting

**Symptom:**
- User sends messages but on refresh, conversation is empty
- Messages disappear after page reload

**Cause:** Messages not being saved to database or incorrect user UUID

**Solution:**

1. **Verify messages are saved:**
```python
async def process_message(self, conversation_uuid: UUID, user_uuid: UUID, message_content: str):
    # Save user message
    user_message = MessageDB(
        conversation_uuid=conversation_uuid,
        role="user",
        content=message_content,
    )
    self.db.add(user_message)
    self.db.commit()

    # Verify it was saved
    saved_msg = self.db.query(MessageDB).filter(
        MessageDB.uuid == user_message.uuid
    ).first()

    if not saved_msg:
        logger.error("Failed to save user message!")
        raise Exception("Message not saved")

    logger.info(f"User message saved: {user_message.uuid}")

    # ... rest of method
```

2. **Check conversation UUID is correct:**
```typescript
// Frontend: Ensure conversation UUID is passed correctly
const sendMessage = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!currentConversation?.uuid) {
    console.error('No conversation selected!');
    setError('Please select a conversation first');
    return;
  }

  console.log('Sending message to conversation:', currentConversation.uuid);

  // ... rest of method
};
```

3. **Test database persistence:**
```bash
# Check messages in database
psql -U apex -d apex_memory -c "SELECT uuid, conversation_uuid, role, substring(content, 1, 50) FROM messages ORDER BY created_at DESC LIMIT 10;"
```

4. **Verify conversation retrieval includes messages:**
```python
def get_conversation(self, conversation_uuid: UUID, user_uuid: UUID):
    # ... existing code

    # Load messages with explicit query
    messages = (
        self.db.query(MessageDB)
        .filter(MessageDB.conversation_uuid == conversation_uuid)
        .order_by(MessageDB.created_at.asc())  # Chronological order
        .all()
    )

    logger.info(f"Loaded {len(messages)} messages for conversation {conversation_uuid}")

    # ... rest of method
```

**Prevention:**
- Always commit after database changes
- Verify saves with immediate read-back
- Test conversation persistence with page refreshes

---

## Phase 2.5: Streaming Issues

### Issue 2.5.1: Tools Not Executing

**Symptom:**
- Claude uses tool_use blocks but tool never executes
- Artifacts sidebar remains empty

**Cause:** Tool execution not triggered or tool executor failing

**Solution:**

1. **Check tool definitions match Claude's usage:**
```python
# Verify tool names match exactly
APEX_TOOLS = [
    {
        "name": "search_knowledge_graph",  # Must match exactly in executor
        # ...
    }
]

# In ToolExecutor
async def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
    logger.info(f"Executing tool: {tool_name}")
    logger.info(f"Tool input: {tool_input}")

    if tool_name == "search_knowledge_graph":  # Exact match required
        # ...
    else:
        logger.error(f"Unknown tool: {tool_name}")
        return {"error": f"Unknown tool: {tool_name}"}
```

2. **Debug streaming flow:**
```python
async def stream_chat_response(messages: list[dict], user: User):
    # ... existing code

    async for event in response:
        logger.info(f"Stream event type: {event.type}")

        if event.type == "content_block_stop":
            if event.content_block.type == "tool_use":
                tool_name = event.content_block.name
                tool_input = event.content_block.input

                logger.info(f"Tool use detected: {tool_name}")
                logger.info(f"Tool input: {tool_input}")

                # Execute tool
                result = await tool_executor.execute_tool(tool_name, tool_input)
                logger.info(f"Tool result: {result}")

                yield f'data: {{"type": "tool_result", "tool_name": "{tool_name}", "result": {json.dumps(result)}}}\n\n'
```

3. **Verify tool executor dependencies:**
```python
class ToolExecutor:
    def __init__(self):
        # Verify services are initialized
        self.query_router = QueryRouter()
        self.graph_service = GraphService()

        logger.info("ToolExecutor initialized")
        logger.info(f"Query router: {self.query_router}")
        logger.info(f"Graph service: {self.graph_service}")
```

4. **Test tools individually:**
```python
# Test script: test_tools.py
import asyncio
from apex_memory.api.chat_stream import ToolExecutor

async def test_tools():
    executor = ToolExecutor()

    # Test search
    result = await executor.execute_tool(
        "search_knowledge_graph",
        {"query": "ACME Corporation", "limit": 5}
    )
    print(f"Search result: {result}")

    # Test relationships
    result = await executor.execute_tool(
        "get_entity_relationships",
        {"entity_name": "ACME Corporation", "max_depth": 2}
    )
    print(f"Relationships result: {result}")

asyncio.run(test_tools())
```

**Prevention:**
- Log every tool execution attempt
- Test tools individually before integration
- Verify tool names match exactly

---

### Issue 2.5.2: Streaming Connection Drops

**Symptom:**
- Stream starts but stops mid-response
- Error: "Connection closed"

**Cause:** Timeout, proxy issues, or server-sent events not configured

**Solution:**

1. **Increase streaming timeout:**
```python
# Backend: main.py
from fastapi import FastAPI
from starlette.middleware.timeout import TimeoutMiddleware

app = FastAPI()

# Add timeout middleware with longer timeout for streaming
app.add_middleware(TimeoutMiddleware, timeout=120)  # 2 minutes
```

2. **Configure SSE properly:**
```python
@router.post("/stream")
async def stream_chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """Stream chat responses."""
    return StreamingResponse(
        stream_chat_response(request.messages, current_user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
```

3. **Frontend reconnection:**
```typescript
// Implement automatic reconnection
import { useChat } from 'ai/react';

export function useApexChat(conversationId: string) {
  const { messages, input, handleInputChange, handleSubmit, error } = useChat({
    api: '/api/v1/chat/stream',
    onError: (error) => {
      console.error('Streaming error:', error);

      // Retry connection
      if (error.message.includes('Connection closed')) {
        console.log('Attempting to reconnect...');
        setTimeout(() => handleSubmit(), 2000);  // Retry after 2s
      }
    },
  });

  return { messages, input, handleInputChange, handleSubmit };
}
```

4. **Check proxy configuration (if using nginx):**
```nginx
# nginx.conf
location /api/v1/chat/stream {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 300s;  # 5 minutes
}
```

**Prevention:**
- Use appropriate timeouts for streaming (2-5 minutes)
- Disable buffering for SSE endpoints
- Implement reconnection logic in frontend

---

### Issue 2.5.3: Artifacts Sidebar Empty

**Symptom:**
- Tools execute successfully but artifacts sidebar shows no data
- Tool results not being captured

**Cause:** Frontend not processing tool results or state not updating

**Solution:**

1. **Verify tool results are emitted:**
```python
# Backend: Ensure tool results are sent
async for event in response:
    if event.type == "content_block_stop":
        if event.content_block.type == "tool_use":
            result = await tool_executor.execute_tool(tool_name, tool_input)

            # Make sure result is JSON serializable
            import json
            try:
                json_result = json.dumps(result)
                yield f'data: {{"type": "tool_result", "tool_name": "{tool_name}", "result": {json_result}}}\n\n'
            except TypeError as e:
                logger.error(f"Tool result not JSON serializable: {e}")
                yield f'data: {{"type": "tool_error", "tool_name": "{tool_name}", "error": "Result not serializable"}}\n\n'
```

2. **Frontend state management:**
```typescript
// Update useApexChat to capture tool results
export function useApexChat(conversationId: string) {
  const [toolExecutions, setToolExecutions] = useState<ToolExecution[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/v1/chat/stream',
    experimental_onFunctionCall: async ({ name, arguments: args }) => {
      // Track tool execution
      setToolExecutions(prev => [
        ...prev,
        { tool_name: name, status: 'executing', args }
      ]);
    },
  });

  // Process streaming events for tool results
  useEffect(() => {
    const eventSource = new EventSource('/api/v1/chat/stream');

    eventSource.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'tool_result') {
        // Add to artifacts
        setArtifacts(prev => [
          ...prev,
          {
            type: getArtifactType(data.tool_name),
            title: getArtifactTitle(data.tool_name),
            data: data.result
          }
        ]);

        // Update tool execution status
        setToolExecutions(prev =>
          prev.map(t =>
            t.tool_name === data.tool_name
              ? { ...t, status: 'completed', result: data.result }
              : t
          )
        );
      }
    });

    return () => eventSource.close();
  }, []);

  return { messages, input, handleInputChange, handleSubmit, toolExecutions, artifacts };
}
```

3. **Debug artifact state:**
```typescript
// Add logging to ArtifactSidebar
export function ArtifactSidebar({ isOpen, onClose, artifacts }: ArtifactSidebarProps) {
  console.log('ArtifactSidebar rendered with artifacts:', artifacts);

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-[600px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Tool Artifacts ({artifacts.length})</SheetTitle>
        </SheetHeader>

        {artifacts.length === 0 ? (
          <div className="mt-6 text-center text-gray-500">
            No artifacts yet. Tools will appear here when executed.
          </div>
        ) : (
          <div className="mt-6 space-y-6">
            {artifacts.map((artifact, idx) => (
              // ... render artifacts
            ))}
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
```

**Prevention:**
- Log every tool result received
- Verify state updates with React DevTools
- Test with manual tool execution

---

## Phase 3: Design System Issues

### Issue 3.1: Gamification Too Flashy

**Symptom:**
- Achievement popups appearing
- Colorful emoji badges showing
- UI feels "busy" not minimal

**Cause:** Not following Apple minimalist design principles

**Solution:**

1. **Remove all popups/toasts:**
```typescript
// BAD - Don't do this
const showAchievementToast = (achievement: Achievement) => {
  toast.success(`🎉 Achievement unlocked: ${achievement.title}!`, {
    duration: 5000,
    icon: achievement.icon
  });
};

// GOOD - Profile only display
const ProfileAchievements = ({ achievements }) => (
  <div className="max-w-2xl mx-auto p-8">
    {achievements.map(achievement => (
      <div className={achievement.earned ? 'bg-gray-50' : 'opacity-50'}>
        <div className="text-3xl text-gray-900">{achievement.icon}</div>
        <div className="font-semibold">{achievement.title}</div>
      </div>
    ))}
  </div>
);
```

2. **Replace emoji badges with monochrome icons:**
```typescript
// BAD
const badges = {
  beginner: '🔍',
  explorer: '🤿',
  expert: '🕵️'
};

// GOOD
const badges = {
  beginner: '⬡',  // Hollow hexagon
  explorer: '⬢',  // Filled hexagon
  expert: '⬣'     // Bold hexagon
};
```

3. **Use text-only streaks:**
```typescript
// BAD
<div className="text-4xl">🔥 {streak} day streak!</div>

// GOOD
<div className="text-center">
  <div className="text-6xl font-semibold text-gray-900">{streak}</div>
  <div className="mt-2 text-sm text-gray-500">day streak</div>
</div>
```

4. **Remove leaderboards from default view:**
```typescript
// BAD - Leaderboard on dashboard
<Dashboard>
  <Leaderboard users={topUsers} />
</Dashboard>

// GOOD - Hidden behind menu
<Menu>
  <MenuItem onClick={() => navigate('/profile')}>
    Profile
  </MenuItem>
  {/* No leaderboard */}
</Menu>
```

**Prevention:**
- Follow design system constants (design-system.ts)
- Review all gamification features against Apple aesthetic
- Remove all popups, toasts, and colorful badges

---

### Issue 3.2: Spacing Not Generous Enough

**Symptom:**
- UI feels cramped
- Components too close together

**Cause:** Not using 2-3x typical spacing

**Solution:**

1. **Use design system spacing:**
```typescript
// design-system.ts spacing values
export const spacing = {
  xs: 8,
  sm: 16,
  md: 24,
  lg: 32,
  xl: 48,
  xxl: 64,
};

// BAD - Typical spacing
<div className="p-4 space-y-2">

// GOOD - Generous spacing (2-3x)
<div className="p-8 space-y-6">  // or p-12, space-y-8
```

2. **Component-level spacing audit:**
```typescript
// Dashboard - Should use generous spacing
export function Dashboard({ metrics }: DashboardProps) {
  return (
    <div className="max-w-2xl mx-auto p-16">  {/* Generous padding */}
      <div className="text-center">
        <div className="text-6xl font-semibold text-gray-900 mb-4">
          {/* Large text */}
        </div>
        <div className="text-2xl font-medium text-gray-700 mb-2">
          {/* Medium text */}
        </div>
      </div>

      {/* Generous spacing between sections */}
      <div className="flex justify-center gap-2 mt-12">
        {/* Pagination */}
      </div>
    </div>
  );
}
```

3. **Line height check:**
```typescript
// Ensure generous line heights
export const typography = {
  sizes: {
    display: { size: 32, weight: 600, lineHeight: 1.2 },
    headline: { size: 24, weight: 600, lineHeight: 1.3 },
    body: { size: 16, weight: 400, lineHeight: 1.6 },  // Generous
    caption: { size: 14, weight: 400, lineHeight: 1.5 },
  },
};
```

**Prevention:**
- Use spacing scale consistently (xs, sm, md, lg, xl, xxl)
- Aim for 2-3x typical spacing
- Review with Apple products as reference

---

### Issue 3.3: Animations Too Flashy

**Symptom:**
- Bounce, scale, or rotate animations present
- Transitions feel busy

**Cause:** Using non-subtle animation types

**Solution:**

1. **Remove bounce/scale animations:**
```css
/* BAD */
.achievement-unlock {
  animation: bounce 0.5s ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* GOOD - Fade only */
.achievement-unlock {
  animation: fadeIn 300ms cubic-bezier(0.4, 0.0, 0.2, 1);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

2. **Use design system animation:**
```typescript
export const animation = {
  duration: {
    fast: 200,
    normal: 300,
  },
  easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
};

// Apply to components
<div
  className="transition-opacity duration-300"
  style={{ transitionTimingFunction: animation.easing }}
>
```

3. **Limit to fade and slide only:**
```typescript
// GOOD animations
const transitions = {
  fade: 'transition-opacity duration-300',
  slide: 'transition-transform duration-300',
};

// Apply
<div className={transitions.fade}>  // Fade in/out only
<div className={transitions.slide}> // Slide up/down only
```

**Prevention:**
- Only use fade and slide transitions
- Duration: 200-300ms only
- Use cubic-bezier(0.4, 0.0, 0.2, 1) easing

---

### Issue 3.4: Dashboard Too Prominent

**Symptom:**
- Dashboard is default landing page
- Multiple metrics visible at once

**Cause:** Not following "hidden dashboard" pattern

**Solution:**

1. **Make conversation default landing:**
```typescript
// App.tsx
<BrowserRouter>
  <Routes>
    <Route element={<ProtectedRoute />}>
      <Route path="/" element={<ConversationHub />} />  {/* Default */}
      <Route path="/dashboard" element={<Dashboard />} />  {/* Hidden */}
      <Route path="/vault" element={<DocumentBrowser />} />
    </Route>
  </Routes>
</BrowserRouter>
```

2. **Single metric display:**
```typescript
// Dashboard.tsx - Show one metric at a time
export function Dashboard({ metrics }: DashboardProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const currentMetric = metrics[currentIndex];  // Single metric only

  return (
    <div className="max-w-2xl mx-auto p-16">
      {/* Single metric display */}
      <div className="text-center">
        <div className="text-6xl font-semibold text-gray-900 mb-4">
          {currentMetric.value}
        </div>
        <div className="text-2xl font-medium text-gray-700 mb-2">
          {currentMetric.label}
        </div>
      </div>

      {/* Pagination for other metrics */}
      <div className="flex justify-center gap-2 mt-12">
        {metrics.map((_, idx) => (
          <button
            onClick={() => setCurrentIndex(idx)}
            className={`w-2 h-2 rounded-full ${
              idx === currentIndex ? 'bg-gray-900 w-6' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
```

3. **Access via menu only:**
```typescript
// AppLayout.tsx
<nav>
  <NavItem to="/" icon={<MessageIcon />} />        {/* Conversation */}
  <NavItem to="/vault" icon={<FolderIcon />} />   {/* Documents */}
  <NavItem to="/dashboard" icon={<ChartIcon />} /> {/* Dashboard - not default */}
</nav>
```

**Prevention:**
- Conversation is always default landing
- Dashboard accessible via menu
- One metric at a time with pagination

---

## Phase 4: Caching Issues

### Issue 4.1: Cache Not Returning Results

**Symptom:**
- Query executed multiple times despite caching
- Cache always returns None

**Cause:** Redis not running or incorrect cache key generation

**Solution:**

1. **Verify Redis is running:**
```bash
# Check Redis status
redis-cli ping
# Should return: PONG

# If not running, start Redis
redis-server

# Or via Docker
docker run -d -p 6379:6379 redis:latest
```

2. **Test cache connection:**
```python
from apex_memory.cache.query_cache import QueryCache

cache = QueryCache()

# Test set/get
cache.set("test_key", {"data": "test"})
result = cache.get("test_key")

print(f"Cache test: {result}")
# Should print: Cache test: {'data': 'test'}
```

3. **Debug cache key generation:**
```python
class QueryCache:
    def _generate_key(self, query: str, filters: dict = None) -> str:
        key_data = {"query": query, "filters": filters or {}}
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        final_key = f"query:{key_hash}"

        logger.info(f"Generated cache key: {final_key} for query: {query}")
        return final_key

    def get(self, query: str, filters: dict = None) -> Optional[Any]:
        key = self._generate_key(query, filters)
        logger.info(f"Getting from cache: {key}")

        cached = self.redis.get(key)

        if cached:
            logger.info(f"Cache hit for: {key}")
            return json.loads(cached)
        else:
            logger.info(f"Cache miss for: {key}")
            return None
```

4. **Check Redis memory:**
```bash
# Check Redis memory usage
redis-cli INFO memory

# Check number of keys
redis-cli DBSIZE

# View all keys (development only)
redis-cli KEYS "query:*"
```

**Prevention:**
- Ensure Redis starts with application
- Monitor cache hit rate
- Set appropriate TTL values

---

### Issue 4.2: Cache Not Invalidating

**Symptom:**
- Stale data returned from cache
- Updates not reflected in responses

**Cause:** Cache not invalidated when data changes

**Solution:**

1. **Invalidate on document ingestion:**
```python
# After ingesting new documents
from apex_memory.cache.query_cache import QueryCache

async def ingest_document(document: Document):
    # ... ingestion logic

    # Invalidate all query caches
    cache = QueryCache()
    # Clear all query keys
    cache.redis.delete(*cache.redis.keys("query:*"))

    logger.info("Cache invalidated after document ingestion")
```

2. **Selective invalidation:**
```python
# Only invalidate related queries
def invalidate_entity_queries(entity_name: str):
    cache = QueryCache()

    # Find all cache keys related to this entity
    pattern = f"query:*{entity_name}*"
    keys = cache.redis.keys(pattern)

    if keys:
        cache.redis.delete(*keys)
        logger.info(f"Invalidated {len(keys)} cache entries for entity: {entity_name}")
```

3. **Time-based expiration:**
```python
# Set shorter TTL for frequently updated data
cache.set(
    query,
    result,
    ttl=300  # 5 minutes instead of default 1 hour
)
```

4. **Cache warming after invalidation:**
```python
# Warm cache with common queries after invalidation
async def warm_cache():
    common_queries = [
        "recent documents",
        "top entities",
        "trending topics"
    ]

    for query in common_queries:
        result = await query_router.route_query(query)
        cache.set(query, result)
        logger.info(f"Cache warmed for query: {query}")
```

**Prevention:**
- Invalidate cache on data updates
- Use appropriate TTL values
- Monitor stale data complaints

---

## Testing Issues

### Issue T.1: Tests Failing After Code Changes

**Symptom:**
- Tests that passed before now fail
- Error: "AssertionError" or "AttributeError"

**Cause:** Code changes not reflected in tests or missing mocks

**Solution:**

1. **Update mocks to match new code:**
```python
# If you changed a function signature, update mock
# OLD
@patch('apex_memory.services.conversation_service.ConversationService.process_message')

# NEW (if you added parameters)
@patch('apex_memory.services.conversation_service.ConversationService.process_message')
async def test_process_message(mock_process):
    mock_process.return_value = Mock(
        uuid="test-uuid",
        role="assistant",
        content="Response",
        citations=[],  # Added citations
        created_at=datetime.utcnow()
    )
```

2. **Run tests with verbose output:**
```bash
pytest tests/unit/test_conversation.py::test_create_conversation -vv
```

3. **Check for import errors:**
```python
# If you moved/renamed a module, update imports
# OLD
from apex_memory.services.conversation import ConversationService

# NEW
from apex_memory.services.conversation_service import ConversationService
```

4. **Clear pytest cache:**
```bash
# Sometimes old cache causes issues
pytest --cache-clear
rm -rf .pytest_cache
```

**Prevention:**
- Run tests after every code change
- Update tests when changing interfaces
- Use CI to catch breaking changes

---

### Issue T.2: Frontend Tests Timing Out

**Symptom:**
```
Timeout - Async callback was not invoked within the 5000 ms timeout
```

**Cause:** Async operations not completing or mocks not resolving

**Solution:**

1. **Increase timeout:**
```typescript
await waitFor(() => {
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
}, { timeout: 10000 });  // Increase to 10 seconds
```

2. **Mock async functions properly:**
```typescript
// Mock axios to resolve immediately
jest.mock('axios');
import axios from 'axios';
const mockedAxios = axios as jest.Mocked<typeof axios>;

// BAD - Missing resolution
mockedAxios.get.mockImplementation(() => {
  return new Promise(() => {});  // Never resolves!
});

// GOOD - Resolves immediately
mockedAxios.get.mockResolvedValue({
  data: { conversations: [] }
});
```

3. **Use fake timers for long delays:**
```typescript
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});

test('handles delayed response', async () => {
  // ... test code

  // Fast-forward time
  jest.advanceTimersByTime(5000);

  await waitFor(() => {
    expect(screen.getByText('Loaded')).toBeInTheDocument();
  });
});
```

**Prevention:**
- Always mock async operations
- Use waitFor with appropriate timeouts
- Check that mocks resolve/reject properly

---

## Performance Issues

### Issue P.1: Application Slow to Load

**Symptom:**
- Frontend takes 5+ seconds to load
- Large JavaScript bundle size

**Cause:** Bundle not optimized or too many dependencies

**Solution:**

1. **Analyze bundle size:**
```bash
cd frontend
npm run build -- --analyze

# Check bundle sizes
du -h dist/assets/*.js
```

2. **Lazy load routes:**
```typescript
// App.tsx - Use lazy loading
import { lazy, Suspense } from 'react';

const ConversationHub = lazy(() => import('./components/ConversationHub'));
const Dashboard = lazy(() => import('./components/Dashboard'));
const DocumentBrowser = lazy(() => import('./components/DocumentBrowser'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ConversationHub />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/vault" element={<DocumentBrowser />} />
        </Routes>
      </BrowserRouter>
    </Suspense>
  );
}
```

3. **Optimize dependencies:**
```bash
# Remove unused dependencies
npm uninstall <unused-package>

# Use production build
npm run build
npm run preview
```

4. **Enable compression:**
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import compression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
  ],
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // Remove console.log in production
      },
    },
  },
});
```

**Prevention:**
- Lazy load routes and heavy components
- Regularly audit bundle size
- Remove unused dependencies

---

## Getting Help

### When to Escalate

**Contact maintainers if:**
- Issue persists after trying all solutions
- Data corruption or loss occurs
- Security vulnerability discovered
- Performance degradation >50%

### Debug Information to Provide

**Always include:**
1. **Error message** (full stack trace)
2. **Steps to reproduce**
3. **Environment** (OS, Python/Node version, browser)
4. **Logs** (backend logs, browser console)
5. **What you've tried** (solutions attempted)

### Log Collection

```bash
# Backend logs
tail -f apex-memory-system/logs/app.log

# Frontend console (in browser DevTools)
# Copy console output

# Database logs
tail -f /var/log/postgresql/postgresql-14-main.log

# Redis logs
redis-cli MONITOR
```

---

## Preventive Maintenance

### Weekly Checks

- [ ] Review error logs for patterns
- [ ] Check cache hit rate (target: >70%)
- [ ] Monitor API response times (target: P90 <1s)
- [ ] Verify all tests passing
- [ ] Check database query performance

### Monthly Audits

- [ ] Review bundle size
- [ ] Update dependencies
- [ ] Run security audit (`npm audit`, `safety check`)
- [ ] Benchmark performance
- [ ] Review user feedback for issues

---

**Last Updated:** 2025-10-21
**Status:** ✅ Complete - Comprehensive troubleshooting guide
**Next:** RESEARCH-REFERENCES.md or begin implementation