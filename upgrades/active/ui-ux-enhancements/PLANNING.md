# UI/UX Enhancements - Implementation Planning

**Upgrade:** UI/UX Enhancements
**Duration:** 7 weeks (5 implementation phases + 2 polish)
**Start Date:** TBD
**Target Completion:** TBD
**Status:** 📝 Planning Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Timeline Overview](#timeline-overview)
3. [Phase 1: Authentication Foundation (Week 1)](#phase-1-authentication-foundation-week-1)
4. [Phase 2: AI Conversation Hub (Week 2)](#phase-2-ai-conversation-hub-week-2)
5. [Phase 2.5: Claude Agents SDK Integration (Week 3)](#phase-25-claude-agents-sdk-integration-week-3)
6. [Phase 3: Engagement Layer (Weeks 4-5)](#phase-3-engagement-layer-weeks-4-5)
7. [Phase 4: Collaboration & Polish (Weeks 6-7)](#phase-4-collaboration--polish-weeks-6-7)
8. [Dependencies & Prerequisites](#dependencies--prerequisites)
9. [Risk Mitigation](#risk-mitigation)
10. [Success Criteria](#success-criteria)
11. [Resource Requirements](#resource-requirements)

---

## Executive Summary

### Current State

**Implementation Level:** 85% complete

**Existing Features:**
- ✅ Document upload portal (drag & drop, progress tracking)
- ✅ Knowledge graph visualization (force-directed, interactive)
- ✅ Advanced search and filtering
- ✅ Document management (CRUD operations)
- ✅ Cache monitoring dashboard
- ✅ Mobile-responsive design
- ✅ Beautiful animations (Framer Motion)

**Critical Gaps:**
- ❌ User authentication (BLOCKER for production)
- ❌ AI conversation interface (CRITICAL for adoption)

### Enhancement Goals

**Transform the UI from:**
- "Basic document upload portal"
- 5-minute average session
- Limited engagement

**Into:**
- "Addictive knowledge platform employees use daily"
- 15+ minute average session
- High engagement with discovery, collaboration, personalization

### Implementation Approach

**7 Weeks, 5 Phases:**

| Phase | Timeline | Focus | Priority | Tests |
|-------|----------|-------|----------|-------|
| 1 | Week 1 | Authentication Foundation | BLOCKER | 12 |
| 2 | Week 2 | AI Conversation Hub | CRITICAL | 15 |
| 2.5 | Week 3 | Claude Agents SDK Integration | CRITICAL | 20 |
| 3 | Weeks 4-5 | Engagement Layer (Gamification, Personalization) | HIGH | 35 |
| 4 | Weeks 6-7 | Collaboration & Polish | MEDIUM | 23 |

**Total:** 105 new tests, 7-week timeline

---

## Timeline Overview

### Week-by-Week Breakdown

```
Week 1: Authentication Foundation (BLOCKER)
├── Day 1-2: FastAPI JWT backend
├── Day 3-4: Login/Logout UI + Protected Routes
└── Day 5: Role-based access + Testing

Week 2: AI Conversation Hub (CRITICAL)
├── Day 1-2: Chat UI component
├── Day 3: Natural language processing integration
├── Day 4: Conversation history + Citations
└── Day 5: Voice input + Testing

Week 3: Claude Agents SDK Integration (CRITICAL)
├── Day 1-2: Vercel AI SDK integration (useChat hook + streaming)
├── Day 3: Claude tool use implementation (knowledge graph queries)
├── Day 4: Artifacts sidebar (Sheet component + visualizations)
└── Day 5: Tool visualization + Testing

Weeks 4-5: Engagement Layer (HIGH)
├── Week 4:
│   ├── Day 1-2: Gamification system (achievements, streaks)
│   ├── Day 3-4: Smart recommendations engine
│   └── Day 5: Personalized dashboard
└── Week 5:
    ├── Day 1-2: AI-generated briefings
    ├── Day 3-4: Analytics and tracking
    └── Day 5: Testing and polish

Weeks 6-7: Collaboration & Polish (MEDIUM)
├── Week 6:
│   ├── Day 1-2: Document sharing + Annotations
│   ├── Day 3-4: Team activity feed
│   └── Day 5: Collaborative graph exploration
└── Week 7:
    ├── Day 1-2: Advanced visualizations (3D, timeline, heatmaps)
    ├── Day 3: Performance optimization
    ├── Day 4: Accessibility audit (WCAG 2.1 AA)
    └── Day 5: Final testing and documentation
```

---

## Phase 1: Authentication Foundation (Week 1)

**Priority:** 🔴 BLOCKER for production deployment

**Goal:** Secure the system with user management and authentication

### Why This Matters

**Without authentication:**
- All API endpoints are public
- No user tracking or personalization
- Cannot deploy to production
- No access control for sensitive data

**With authentication:**
- ✅ Production-ready security
- ✅ Foundation for personalization
- ✅ User activity tracking
- ✅ Role-based access control

### Deliverables

#### Backend (FastAPI + JWT)

**1.1 Authentication API Endpoints**

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
```

**Implementation:**
- `apex-memory-system/src/apex_memory/api/auth.py` (new)
- `apex-memory-system/src/apex_memory/models/user.py` (new)
- `apex-memory-system/src/apex_memory/services/auth_service.py` (new)

**Technologies:**
- FastAPI Security (OAuth2PasswordBearer)
- python-jose (JWT tokens)
- passlib (password hashing with bcrypt)
- SQLAlchemy (user database models)

**1.2 User Database Schema**

```sql
CREATE TABLE users (
    uuid UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user', -- 'admin' | 'user'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    preferences JSONB DEFAULT '{}'
);

CREATE TABLE api_keys (
    uuid UUID PRIMARY KEY,
    user_uuid UUID REFERENCES users(uuid),
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    last_used TIMESTAMP
);
```

**1.3 Protected Route Middleware**

```python
# apex-memory-system/src/apex_memory/api/dependencies.py

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT token and return current user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid: str = payload.get("sub")
        if user_uuid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.uuid == user_uuid).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

#### Frontend (React + TypeScript)

**1.4 Authentication Components**

**Components to create:**
- `Login.tsx` - Login form with email/password
- `Register.tsx` - User registration form
- `AuthProvider.tsx` - React context for auth state
- `ProtectedRoute.tsx` - Route guard component
- `UserMenu.tsx` - User profile dropdown
- `ApiKeyManager.tsx` - API key management UI

**Location:** `apex-memory-system/src/apex_memory/frontend/src/components/auth/`

**1.5 Authentication State Management**

```typescript
// src/lib/auth.ts

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  refreshToken: () => Promise<void>;
}

export function useAuth(): AuthState {
  // Implementation using Zustand or React Context
}
```

**1.6 Protected Routes**

```typescript
// src/App.tsx (updated)

<Router>
  <Routes>
    {/* Public routes */}
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />

    {/* Protected routes */}
    <Route element={<ProtectedRoute />}>
      <Route path="/" element={<Dashboard />} />
      <Route path="/vault" element={<DocumentBrowser />} />
      <Route path="/graph" element={<GraphExplorer />} />
      <Route path="/import" element={<UploadZone />} />
    </Route>

    {/* Admin-only routes */}
    <Route element={<ProtectedRoute requireAdmin />}>
      <Route path="/admin" element={<AdminPanel />} />
    </Route>
  </Routes>
</Router>
```

### Technical Tasks

**Day 1: Backend Foundation**
1. Create user database schema (PostgreSQL)
2. Implement User and ApiKey models (SQLAlchemy)
3. Add password hashing utilities (passlib + bcrypt)
4. Create JWT token generation/validation functions

**Day 2: Authentication API**
5. Implement `/auth/register` endpoint
6. Implement `/auth/login` endpoint (return JWT)
7. Implement `/auth/logout` endpoint (blacklist token)
8. Implement `/auth/refresh` endpoint (refresh expired tokens)
9. Implement `/auth/me` endpoint (get current user)

**Day 3: Frontend Auth Components**
10. Create AuthProvider context
11. Create Login.tsx component
12. Create Register.tsx component
13. Create UserMenu.tsx component
14. Implement token storage (localStorage + secure cookies)

**Day 4: Protected Routes**
15. Create ProtectedRoute.tsx component
16. Update App.tsx with route guards
17. Add authentication interceptor to Axios client
18. Handle token refresh on 401 responses
19. Add "unauthorized" error handling

**Day 5: Testing & Polish**
20. Write 12 authentication tests (see TESTING.md)
21. Test login/logout flows
22. Test protected route access
23. Test token refresh
24. Add loading states and error messages
25. Update API documentation

### Testing Checklist

**Backend Tests (6 tests):**
- ✅ User registration with valid data
- ✅ User login with correct credentials
- ✅ User login with incorrect credentials (fail)
- ✅ Access protected endpoint with valid token
- ✅ Access protected endpoint with expired token (fail)
- ✅ Token refresh flow

**Frontend Tests (6 tests):**
- ✅ Login form validation
- ✅ Successful login redirects to dashboard
- ✅ Failed login shows error message
- ✅ Protected route redirects to login when unauthenticated
- ✅ Logout clears user state
- ✅ Token refresh on page reload

### Success Criteria

**Phase 1 Complete When:**
- ✅ All 12 tests passing
- ✅ Users can register and login
- ✅ JWT tokens are generated and validated
- ✅ Protected routes require authentication
- ✅ Admin routes require admin role
- ✅ Token refresh works automatically
- ✅ Logout clears session properly
- ✅ API endpoints are protected

---

## Phase 2: AI Conversation Hub (Week 2)

**Priority:** 🟠 CRITICAL for user adoption

**Goal:** Create "ChatGPT for your knowledge graph" experience

### Why This Matters

**User Problem:**
- Current UI is "upload and forget"
- No easy way to query knowledge base in natural language
- Users must manually search and filter
- No conversational exploration

**Solution:**
- Natural language chat interface
- Memory-grounded responses (cite source documents)
- Follow-up questions with context
- Voice input option

**Impact:**
- 3-5x increase in daily active users
- 15+ minute average session duration
- "Addictive" user experience

### Deliverables

#### Backend API

**2.1 Conversation API Endpoints**

```
POST /api/v1/conversation/query
GET  /api/v1/conversation/history
POST /api/v1/conversation/export
DELETE /api/v1/conversation/{conversation_uuid}
```

**Implementation:**
- `apex-memory-system/src/apex_memory/api/conversation.py` (new)
- `apex-memory-system/src/apex_memory/models/conversation.py` (new)
- `apex-memory-system/src/apex_memory/services/conversation_service.py` (new)

**2.2 Conversation Database Schema**

```sql
CREATE TABLE conversations (
    uuid UUID PRIMARY KEY,
    user_uuid UUID REFERENCES users(uuid),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP
);

CREATE TABLE messages (
    uuid UUID PRIMARY KEY,
    conversation_uuid UUID REFERENCES conversations(uuid) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    citations JSONB, -- Array of document UUIDs referenced
    created_at TIMESTAMP DEFAULT NOW()
);
```

**2.3 Natural Language Processing Integration**

```python
# apex-memory-system/src/apex_memory/services/conversation_service.py

async def process_user_query(
    query: str,
    conversation_uuid: Optional[UUID],
    user_uuid: UUID
) -> ConversationResponse:
    """
    Process user query with memory-grounded response.

    Steps:
    1. Retrieve conversation history (if exists)
    2. Query multi-database system (Neo4j, Qdrant, PostgreSQL)
    3. Construct LLM prompt with:
       - Conversation history
       - Retrieved context (top 10 documents/entities)
       - User query
    4. Generate response with Claude 3.5 Sonnet
    5. Extract citations from response
    6. Store message in database
    7. Return response with citations
    """
```

**2.4 Citation Extraction**

```python
class Citation(BaseModel):
    document_uuid: UUID
    document_title: str
    relevant_excerpt: str
    confidence_score: float

async def extract_citations(
    response: str,
    context_documents: List[Document]
) -> List[Citation]:
    """Extract document citations from LLM response."""
```

#### Frontend Components

**2.5 Conversation Interface Components**

**Components to create:**
- `ConversationHub.tsx` - Main chat interface (full-screen)
- `MessageList.tsx` - Scrollable conversation history
- `MessageBubble.tsx` - Individual message with role styling
- `ChatInput.tsx` - Text input with voice option
- `CitationPanel.tsx` - Side panel showing source documents
- `ConversationSidebar.tsx` - List of past conversations
- `ExportConversationDialog.tsx` - Export as PDF/Markdown

**Location:** `apex-memory-system/src/apex_memory/frontend/src/components/conversation/`

**2.6 Conversation UI Layout**

```
┌─────────────────────────────────────────────────────────────┐
│ Header: "Conversation with Knowledge Graph"     [Export] [X]│
├──────────────┬──────────────────────────────────┬───────────┤
│              │                                  │           │
│ Conversation │   Message History                │ Citations │
│ Sidebar      │                                  │  Panel    │
│              │   User: "Show me CAT loaders"    │           │
│ [+ New Chat] │   ────────────────────────────── │ Document: │
│              │   Assistant: "Here are 5 CAT    │ "CAT 950  │
│ Previous:    │   loaders found in the          │  Loader   │
│ - CAT...     │   knowledge graph..."           │  Manual"  │
│ - Hydraulic  │   • CAT 950 Wheel Loader        │           │
│ - Maint...   │   • CAT 962M Wheel Loader       │ [View]    │
│              │   [Citations: 3 documents]       │           │
│              │   ────────────────────────────── │ Document: │
│              │                                  │ "Equip-   │
│              │   User: "What maintenance is    │  ment DB" │
│              │         required?"              │           │
│              │   ────────────────────────────── │ [View]    │
│              │                                  │           │
│              │   [Assistant is typing...]       │           │
│              │                                  │           │
├──────────────┴──────────────────────────────────┴───────────┤
│ Chat Input: "Type your message..."         [🎤] [Send]     │
└─────────────────────────────────────────────────────────────┘
```

**2.7 Voice Input Integration**

```typescript
// src/lib/speech-recognition.ts

export function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');

  const startListening = () => {
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0])
        .map((result) => result.transcript)
        .join('');

      setTranscript(transcript);
    };

    recognition.start();
    setIsListening(true);
  };

  return { isListening, transcript, startListening, stopListening };
}
```

### Technical Tasks

**Day 1: Backend Foundation**
1. Create conversation/message database schema
2. Implement Conversation and Message models
3. Create conversation service scaffolding
4. Add conversation API routes

**Day 2: LLM Integration**
5. Implement query processing with Claude API
6. Add context retrieval from multi-database system
7. Implement citation extraction logic
8. Add conversation history management

**Day 3: Frontend Chat UI**
9. Create ConversationHub.tsx component
10. Create MessageList.tsx and MessageBubble.tsx
11. Create ChatInput.tsx with send functionality
12. Add real-time message streaming (SSE)
13. Create typing indicator animation

**Day 4: Citations & History**
14. Create CitationPanel.tsx component
15. Add citation click-through to documents
16. Create ConversationSidebar.tsx
17. Implement conversation persistence
18. Add export functionality (PDF/Markdown)

**Day 5: Voice & Testing**
19. Implement voice input (Web Speech API)
20. Add voice input UI toggle
21. Write 15 conversation tests (see TESTING.md)
22. Test conversation flow end-to-end
23. Add loading states and error handling
24. Polish UI animations and transitions
25. Update documentation

### Testing Checklist

**Backend Tests (8 tests):**
- ✅ Create new conversation
- ✅ Send message to conversation
- ✅ Retrieve conversation history
- ✅ Extract citations from response
- ✅ Query retrieves relevant context
- ✅ Follow-up question uses conversation history
- ✅ Export conversation
- ✅ Delete conversation

**Frontend Tests (7 tests):**
- ✅ Send message displays in chat
- ✅ Receive assistant response
- ✅ Citations display in side panel
- ✅ Click citation opens document
- ✅ Voice input captures speech
- ✅ Conversation history loads on page reload
- ✅ Export conversation downloads file

### Success Criteria

**Phase 2 Complete When:**
- ✅ All 15 tests passing
- ✅ Users can ask natural language questions
- ✅ Assistant responses cite source documents
- ✅ Citations link to actual documents
- ✅ Conversation history persists
- ✅ Voice input works in supported browsers
- ✅ Export to PDF/Markdown works
- ✅ UI is polished and responsive

---

## Phase 2.5: Claude Agents SDK Integration (Week 3)

**Priority:** 🟠 CRITICAL for modern AI experience

**Goal:** Transform basic chat into AI-native interface with streaming, tool use, and artifacts

### Why This Matters

**Current State (Post-Phase 2):**
- Basic conversation interface functional
- Standard request/response pattern
- Citations in text format
- No visibility into Claude's reasoning
- No visual artifacts for code/data

**Problems:**
- Users don't see "what Claude is doing"
- No modern streaming experience (ChatGPT-like)
- Tool calls are invisible to users
- No artifacts sidebar for visualizations
- Feels like "old-style chatbot"

**Solution (Phase 2.5):**
- **Vercel AI SDK** for modern streaming (useChat hook)
- **Claude tool use** for knowledge graph queries
- **Artifacts sidebar** for visualizing results (Sheet component from Shadcn/ui)
- **Tool visualization** showing Claude's reasoning steps

**Impact:**
- Modern "ChatGPT for your knowledge graph" experience
- Visual transparency (see Claude query the knowledge graph)
- Rich artifact display (code, charts, documents in sidebar)
- 10-20% higher user satisfaction vs. basic chat

### Research Foundation

This phase implements patterns from our comprehensive research:

**Documentation References:**
- Vercel AI SDK: `research/documentation/vercel-ai-sdk-overview.md`
- useChat hook: `research/documentation/usechat-hook.md`
- Claude tool use: `research/documentation/tool-use-api.md` + `apex-tool-definitions.md`
- Artifacts layout: `research/documentation/artifacts-layout.md`
- Sheet component: `research/documentation/sheet-component.md`
- Tool visualization: `research/documentation/tool-visualization.md`
- Streaming patterns: `research/documentation/streaming-ui-patterns.md`

**Key Insight from Research:**
> There is NO separate "Claude Agents SDK" - agentic workflows are built by combining:
> 1. Tool use (Claude decides when to use tools)
> 2. Streaming (progressive response rendering)
> 3. Orchestration (multi-step workflows in application layer)

### Deliverables

#### 2.5.1 Vercel AI SDK Integration

**Replace basic fetch with useChat hook:**

```typescript
// Before (Phase 2):
const response = await fetch('/api/v1/conversation/query', {
  method: 'POST',
  body: JSON.stringify({ query, conversation_uuid })
});

// After (Phase 2.5):
import { useChat } from 'ai/react';

const {
  messages,
  input,
  handleSubmit,
  isLoading,
  stop
} = useChat({
  api: '/api/apex/conversation',
  onToolCall: async (toolCall) => {
    // Execute Apex tools (search, query graph, etc.)
    return await executeApexTool(toolCall);
  },
  onFinish: (message) => {
    // Save conversation
    saveConversation(messages);
  }
});
```

**Implementation:**
- `apex-memory-system/src/apex_memory/frontend/src/hooks/useApexChat.ts` (new)
- Update `ConversationHub.tsx` to use useChat
- Add streaming message rendering
- Add "Stop generation" button

**Key Features:**
- Progressive text streaming (word-by-word)
- Automatic message state management
- Built-in error handling and retry
- Tool execution integration
- Status tracking (idle → loading → streaming → error)

#### 2.5.2 Claude Tool Use Implementation

**Define 5 Apex-specific tools:**

```typescript
// apex-memory-system/src/apex_memory/api/tools.ts (new)

export const apexTools = [
  {
    name: "search_apex_documents",
    description: "Search the Apex knowledge base for documents",
    input_schema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" },
        filters: {
          type: "object",
          properties: {
            document_type: { type: "string", enum: ["pdf", "docx", "txt"] },
            date_range: { type: "object" }
          }
        }
      },
      required: ["query"]
    }
  },
  {
    name: "query_knowledge_graph",
    description: "Query the Neo4j knowledge graph for entities and relationships",
    input_schema: {
      type: "object",
      properties: {
        entity_name: { type: "string" },
        relationship_type: { type: "string" },
        depth: { type: "number", minimum: 1, maximum: 3 }
      },
      required: ["entity_name"]
    }
  },
  {
    name: "get_entity_timeline",
    description: "Get temporal history of an entity from Graphiti",
    input_schema: {
      type: "object",
      properties: {
        entity_uuid: { type: "string" },
        time_range: { type: "string", enum: ["1d", "7d", "30d", "all"] }
      },
      required: ["entity_uuid"]
    }
  },
  {
    name: "semantic_search",
    description: "Semantic vector search across documents using Qdrant",
    input_schema: {
      type: "object",
      properties: {
        query: { type: "string" },
        limit: { type: "number", default: 10 },
        min_score: { type: "number", default: 0.7 }
      },
      required: ["query"]
    }
  },
  {
    name: "get_graph_stats",
    description: "Get statistics about the knowledge graph",
    input_schema: {
      type: "object",
      properties: {
        stat_type: { type: "string", enum: ["node_count", "relationship_count", "communities", "centrality"] }
      },
      required: ["stat_type"]
    }
  }
];
```

**Tool Execution Router:**

```python
# apex-memory-system/src/apex_memory/api/tool_executor.py (new)

async def execute_tool(
    tool_name: str,
    tool_input: dict,
    user_uuid: UUID
) -> dict:
    """
    Execute Apex tool and return result.

    Routes to appropriate service:
    - search_apex_documents → PostgreSQL + Qdrant
    - query_knowledge_graph → Neo4j
    - get_entity_timeline → Graphiti
    - semantic_search → Qdrant
    - get_graph_stats → Neo4j
    """
    if tool_name == "search_apex_documents":
        return await search_service.search_documents(**tool_input)

    elif tool_name == "query_knowledge_graph":
        return await graph_service.query_graph(**tool_input)

    elif tool_name == "get_entity_timeline":
        return await graphiti_service.get_timeline(**tool_input)

    elif tool_name == "semantic_search":
        return await qdrant_service.semantic_search(**tool_input)

    elif tool_name == "get_graph_stats":
        return await graph_service.get_stats(**tool_input)

    else:
        raise ValueError(f"Unknown tool: {tool_name}")
```

#### 2.5.3 Artifacts Sidebar (Sheet Component)

**Implement side-by-side layout:**

```
┌─────────────────────────────────────────────────────────────┐
│ Conversation with Apex Knowledge Graph              [Export]│
├──────────────────────────────┬──────────────────────────────┤
│                              │                              │
│ Conversation Area (60%)      │ Artifacts Sidebar (40%)      │
│                              │                              │
│ User: "Show me CAT loaders"  │ ┌──────────────────────────┐│
│ ─────────────────────────    │ │ 📊 Query Results         ││
│ Assistant: "I'll search the  │ │                          ││
│ knowledge graph..."          │ │ [Tool: query_kg]         ││
│                              │ │                          ││
│ [Tool: query_knowledge_graph]│ │ Found 5 CAT loaders:     ││
│ ✓ Complete                   │ │                          ││
│                              │ │ • CAT 950 Wheel Loader   ││
│ Here are 5 CAT loaders:      │ │   └─ 3 relationships     ││
│ • CAT 950 Wheel Loader       │ │                          ││
│ • CAT 962M Wheel Loader      │ │ • CAT 962M Wheel Loader  ││
│ ...                          │ │   └─ 2 relationships     ││
│                              │ │                          ││
│ [View in sidebar →]          │ │ [View Full Graph]        ││
│                              │ └──────────────────────────┘│
│                              │                              │
│ Chat Input: "Type here..."   │                              │
└──────────────────────────────┴──────────────────────────────┘
```

**Implementation:**

```typescript
// apex-memory-system/src/apex_memory/frontend/src/components/conversation/ConversationHub.tsx

import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';

export function ConversationHub() {
  const [showArtifacts, setShowArtifacts] = useState(false);
  const [currentArtifact, setCurrentArtifact] = useState<Artifact | null>(null);

  return (
    <div className="flex h-screen">
      {/* Main conversation area */}
      <main className="flex-1 flex flex-col min-w-0">
        <ConversationArea
          onArtifactGenerated={(artifact) => {
            setCurrentArtifact(artifact);
            setShowArtifacts(true);
          }}
        />
      </main>

      {/* Artifacts sidebar (Sheet component) */}
      <Sheet open={showArtifacts} onOpenChange={setShowArtifacts}>
        <SheetContent
          side="right"
          className="w-2/5 sm:max-w-2xl"
        >
          <SheetHeader>
            <SheetTitle>Artifacts</SheetTitle>
          </SheetHeader>
          <ArtifactViewer artifact={currentArtifact} />
        </SheetContent>
      </Sheet>
    </div>
  );
}
```

**Artifact Types:**
- **Code** - Cypher queries, Python code
- **Charts** - Knowledge graph visualizations (force-directed, bar charts)
- **Documents** - Structured data displays (entity timelines, document lists)
- **Data Tables** - Query results in table format

**Components:**
- `ArtifactsSidebar.tsx` - Sheet-based sidebar container
- `ArtifactViewer.tsx` - Router for artifact types
- `CodeArtifact.tsx` - Syntax-highlighted code display
- `ChartArtifact.tsx` - Recharts visualizations
- `DocumentArtifact.tsx` - Structured document display
- `TableArtifact.tsx` - Data table with sorting/filtering

#### 2.5.4 Tool Visualization

**Show Claude's reasoning process:**

```typescript
// Tool call indicator in conversation

┌────────────────────────────────────────────┐
│ 🔧 Using tool: query_knowledge_graph      │
│                                            │
│ Parameters:                                │
│ • entity_name: "CAT Equipment"            │
│ • depth: 2                                │
│                                            │
│ [Executing...] ████████░░ 80%             │
└────────────────────────────────────────────┘

// After completion:
┌────────────────────────────────────────────┐
│ ✅ Tool completed: query_knowledge_graph   │
│                                            │
│ Found 5 entities, 12 relationships        │
│ Execution time: 1.2s                      │
│                                            │
│ [View Results in Sidebar →]               │
└────────────────────────────────────────────┘
```

**Implementation:**
- `ToolUseIndicator.tsx` - Collapsible tool call display
- `ToolStatusBadge.tsx` - Status indicator (pending, running, complete, error)
- `ToolParameters.tsx` - Display tool input parameters
- `ToolResults.tsx` - Summary of tool results

**UI Patterns:**
- Expand/collapse tool details
- Progress animation during execution
- Error handling with retry option
- Link to artifact sidebar when results available

### Technical Tasks

**Day 1: Vercel AI SDK Backend**
1. Install Vercel AI SDK (`npm install ai`)
2. Create `/api/apex/conversation` endpoint (streaming support)
3. Implement Claude API streaming with Server-Sent Events
4. Add tool definitions to API request
5. Test streaming response in Postman

**Day 2: Vercel AI SDK Frontend**
6. Install `ai/react` package
7. Create `useApexChat` hook wrapping useChat
8. Update ConversationHub.tsx to use useApexChat
9. Add progressive message rendering
10. Add "Stop generation" button
11. Test streaming in UI

**Day 3: Claude Tool Use**
12. Define 5 Apex tools (search, query graph, timeline, semantic search, stats)
13. Create tool execution router
14. Implement tool execution for each tool type
15. Add tool result formatting
16. Test tool execution from conversation

**Day 4: Artifacts Sidebar**
17. Install Shadcn/ui Sheet component (`npx shadcn@latest add sheet`)
18. Create ArtifactsSidebar.tsx with Sheet component
19. Create ArtifactViewer.tsx (router for artifact types)
20. Implement CodeArtifact.tsx (syntax highlighting)
21. Implement ChartArtifact.tsx (Recharts integration)
22. Add artifact generation from tool results
23. Test sidebar open/close animation

**Day 5: Tool Visualization & Testing**
24. Create ToolUseIndicator.tsx component
25. Add tool status tracking
26. Create ToolParameters.tsx display
27. Add tool result summary
28. Write 20 Phase 2.5 tests (see TESTING.md)
29. Test complete flow: query → tool use → artifact display
30. Polish animations and transitions
31. Update documentation

### Testing Checklist

**Backend Tests (8 tests):**
- ✅ Streaming endpoint sends SSE events
- ✅ Tool definitions included in Claude API request
- ✅ Tool execution router calls correct service
- ✅ search_apex_documents returns valid results
- ✅ query_knowledge_graph returns graph data
- ✅ get_entity_timeline returns temporal data
- ✅ Tool errors handled gracefully
- ✅ Streaming continues after tool execution

**Frontend Tests (12 tests):**
- ✅ useApexChat hook streams messages progressively
- ✅ Stop button halts streaming
- ✅ Tool call displays in conversation
- ✅ Tool parameters visible
- ✅ Tool status updates (pending → running → complete)
- ✅ Tool results summary displays
- ✅ Artifacts sidebar opens with Sheet animation
- ✅ CodeArtifact renders with syntax highlighting
- ✅ ChartArtifact renders Recharts visualization
- ✅ Sidebar closes with Escape key
- ✅ Conversation continues after tool use
- ✅ Error handling displays user-friendly message

### Success Criteria

**Phase 2.5 Complete When:**
- ✅ All 20 tests passing
- ✅ Vercel AI SDK useChat hook functional
- ✅ Messages stream progressively (word-by-word)
- ✅ Claude tool use working (all 5 tools)
- ✅ Tool calls visible in conversation
- ✅ Artifacts sidebar opens with Sheet animation
- ✅ Code artifacts render with syntax highlighting
- ✅ Chart artifacts display visualizations
- ✅ Tool visualization shows reasoning process
- ✅ Escape key closes sidebar
- ✅ UI polished and responsive
- ✅ Feels like "ChatGPT for knowledge graph"

### Dependencies Added

**npm packages:**
```json
{
  "dependencies": {
    "ai": "^3.0.0",
    "react-syntax-highlighter": "^15.5.0",
    "recharts": "^2.10.4"
  }
}
```

**Shadcn/ui components:**
```bash
npx shadcn@latest add sheet
npx shadcn@latest add badge
npx shadcn@latest add progress
```

---

## Phase 3: Engagement Layer (Weeks 4-5)

**Priority:** 🟡 HIGH for user retention

**Goal:** Make the UI "addictive" and "employees would use at all times"

### Why This Matters

**User Behavior Problem:**
- Users upload documents and don't return
- No incentive to explore knowledge graph
- No personalization or recommendations
- System doesn't "pull" users back

**Solution:**
- Gamification (achievements, streaks, leaderboards)
- Smart recommendations ("You might be interested in...")
- Personalized dashboard
- AI-generated daily briefings

**Impact:**
- 80%+ daily active users
- Users check system daily for insights
- Increased knowledge discovery
- "I can't imagine working without this tool"

### Deliverables

#### Week 3: Gamification & Recommendations

**3.1 Gamification System**

**Achievement Types:**

| Achievement | Trigger | Badge |
|-------------|---------|-------|
| Knowledge Explorer | Explore 10 documents | 🔍 Bronze Explorer |
| Deep Diver | View 5+ graph hops | 🤿 Deep Diver |
| Pattern Detective | Discover 3+ patterns | 🕵️ Detective |
| Conversation Master | 50+ conversation messages | 💬 Master Chatter |
| Team Player | Share 10+ documents | 🤝 Team Player |
| Streak Keeper | 7-day streak | 🔥 Week Warrior |
| Super Streaker | 30-day streak | 🏆 Month Master |

**Database Schema:**

```sql
CREATE TABLE user_achievements (
    uuid UUID PRIMARY KEY,
    user_uuid UUID REFERENCES users(uuid),
    achievement_type VARCHAR(100) NOT NULL,
    achieved_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB -- Additional context (e.g., streak count)
);

CREATE TABLE user_activity (
    uuid UUID PRIMARY KEY,
    user_uuid UUID REFERENCES users(uuid),
    activity_type VARCHAR(100) NOT NULL, -- 'document_view' | 'graph_explore' | 'message_sent'
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_streaks (
    user_uuid UUID PRIMARY KEY REFERENCES users(uuid),
    current_streak_days INT DEFAULT 0,
    longest_streak_days INT DEFAULT 0,
    last_activity_date DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Frontend Components:**
- `AchievementBadge.tsx` - Badge UI with animations
- `AchievementToast.tsx` - "You earned a badge!" notification
- `StreakCounter.tsx` - Current streak display
- `Leaderboard.tsx` - Team leaderboard (optional)
- `AchievementsPanel.tsx` - Full achievement gallery

**3.2 Smart Recommendations Engine**

**Recommendation Types:**

1. **"You might be interested in..."** - Content-based filtering
   - Based on recently viewed documents
   - Based on search history
   - Based on graph exploration patterns

2. **"New connections discovered"** - Graph-based recommendations
   - New relationships added since last visit
   - Trending entities in your teams

3. **"Trending topics"** - Collaborative filtering
   - Popular documents in your team
   - Most explored graph nodes this week

**Implementation:**

```python
# apex-memory-system/src/apex_memory/services/recommendation_service.py

async def generate_recommendations(
    user_uuid: UUID,
    limit: int = 10
) -> List[Recommendation]:
    """
    Generate personalized recommendations.

    Steps:
    1. Retrieve user activity history (last 30 days)
    2. Extract user interests (document types, entities, topics)
    3. Query similar documents (Qdrant semantic search)
    4. Query related entities (Neo4j graph traversal)
    5. Rank recommendations by relevance
    6. Return top N recommendations
    """

class Recommendation(BaseModel):
    type: str  # 'document' | 'entity' | 'pattern'
    uuid: UUID
    title: str
    reason: str  # Why recommended
    confidence_score: float
```

**Frontend Components:**
- `RecommendationCard.tsx` - Single recommendation UI
- `RecommendationFeed.tsx` - Scrollable feed
- `TrendingTopics.tsx` - Sidebar widget

**3.3 Personalized Dashboard**

**Dashboard Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│ Good morning, [User]! Here's what's new in your knowledge   │
│ base...                                                       │
├───────────────────┬──────────────────────┬───────────────────┤
│                   │                      │                   │
│ Your Stats        │ Recent Activity      │ Recommendations   │
│                   │                      │                   │
│ 🔥 7-day streak   │ • Viewed "CAT 950"  │ You might be      │
│ 🏆 5 achievements │ • Searched "hydraul" │ interested in:    │
│ 📊 127 docs       │ • Exported graph    │                   │
│    explored       │                      │ • "Maintenance    │
│                   │ [View All]           │    Schedules"     │
│ [View Profile]    │                      │ • "Equipment DB"  │
│                   │                      │                   │
│                   │                      │ [More]            │
├───────────────────┴──────────────────────┴───────────────────┤
│ AI-Generated Daily Briefing                                  │
│ ────────────────────────────────────────────────────────────│
│ "Based on your recent activity, here are key insights:      │
│                                                              │
│ 1. New maintenance patterns detected for CAT equipment      │
│ 2. 3 colleagues also exploring hydraulic systems            │
│ 3. 12 new documents added to your favorite topics"          │
│                                                              │
│ [Read Full Briefing]                                         │
└──────────────────────────────────────────────────────────────┘
```

**Components:**
- `PersonalDashboard.tsx` - Main dashboard layout
- `UserStatsWidget.tsx` - Achievements, streaks, stats
- `RecentActivityWidget.tsx` - Timeline of recent actions
- `AIBriefingWidget.tsx` - Daily AI-generated summary
- `QuickActionsWidget.tsx` - Favorite queries, saved filters

#### Week 4: AI Briefings & Analytics

**3.4 AI-Generated Daily Briefings**

**Briefing Content:**

1. **New Documents** - Documents added since last login
2. **Trending Topics** - Popular topics in your team
3. **Pattern Detection** - New patterns discovered
4. **Activity Summary** - Your knowledge graph growth
5. **Recommendations** - Top 3 documents to explore

**Implementation:**

```python
# apex-memory-system/src/apex_memory/services/briefing_service.py

async def generate_daily_briefing(
    user_uuid: UUID
) -> DailyBriefing:
    """
    Generate AI-powered daily briefing.

    Steps:
    1. Retrieve user activity since last login
    2. Query new documents in user's topics
    3. Detect patterns in recent data
    4. Generate natural language summary with Claude
    5. Return structured briefing
    """

class DailyBriefing(BaseModel):
    summary: str  # 2-3 sentence overview
    new_documents: List[Document]
    trending_topics: List[Topic]
    patterns_detected: List[Pattern]
    recommendations: List[Recommendation]
    generated_at: datetime
```

**Frontend Components:**
- `DailyBriefing.tsx` - Full briefing page
- `BriefingCard.tsx` - Collapsed briefing card
- `BriefingNotification.tsx` - "New briefing available"

**3.5 User Analytics & Tracking**

**Tracked Metrics:**

- Documents viewed
- Graph nodes explored
- Messages sent (conversation)
- Searches performed
- Time spent in system
- Knowledge graph growth (personal)

**Implementation:**

```typescript
// src/lib/analytics.ts

export function trackActivity(
  activityType: string,
  metadata?: Record<string, any>
) {
  api.post('/api/v1/analytics/track', {
    activity_type: activityType,
    metadata,
    timestamp: new Date().toISOString()
  });
}

// Usage:
trackActivity('document_view', { document_uuid: '...' });
trackActivity('graph_explore', { depth: 3, node_count: 42 });
trackActivity('message_sent', { conversation_uuid: '...' });
```

### Technical Tasks

**Week 3: Gamification & Recommendations**

**Day 1: Gamification Backend**
1. Create achievement database schema
2. Implement achievement tracking service
3. Create streak tracking logic
4. Add activity logging system

**Day 2: Gamification Frontend**
5. Create AchievementBadge.tsx component
6. Create StreakCounter.tsx component
7. Add achievement toast notifications
8. Create AchievementsPanel.tsx (full gallery)

**Day 3: Recommendations Backend**
9. Implement recommendation service
10. Add content-based filtering logic
11. Add collaborative filtering logic
12. Create recommendation API endpoints

**Day 4: Recommendations Frontend**
13. Create RecommendationCard.tsx
14. Create RecommendationFeed.tsx
15. Add "You might be interested in..." section
16. Create TrendingTopics.tsx sidebar

**Day 5: Testing Week 3**
17. Write 12 gamification tests
18. Write 8 recommendation tests
19. Test achievement triggering
20. Test streak counting accuracy
21. Polish animations and UI

**Week 4: Briefings & Dashboard**

**Day 1: AI Briefings Backend**
22. Implement briefing generation service
23. Add pattern detection integration
24. Create briefing API endpoints
25. Schedule daily briefing generation (cron job)

**Day 2: AI Briefings Frontend**
26. Create DailyBriefing.tsx page
27. Create BriefingCard.tsx widget
28. Add briefing notifications
29. Create "Read Full Briefing" modal

**Day 3: Personalized Dashboard**
30. Create PersonalDashboard.tsx layout
31. Create UserStatsWidget.tsx
32. Create RecentActivityWidget.tsx
33. Create QuickActionsWidget.tsx
34. Add widget customization (drag & drop)

**Day 4: Analytics & Tracking**
35. Implement analytics tracking service
36. Add frontend tracking calls
37. Create analytics dashboard (admin only)
38. Add privacy controls (opt-out)

**Day 5: Testing Week 4**
39. Write 10 briefing tests
40. Write 5 dashboard tests
41. Test analytics tracking accuracy
42. End-to-end testing of engagement features
43. Performance testing (dashboard load time)
44. Polish and bug fixes

### Testing Checklist

**Gamification Tests (12 tests):**
- ✅ Achievement unlocked when criteria met
- ✅ Achievement toast displays correctly
- ✅ Streak increments daily
- ✅ Streak resets after missed day
- ✅ Leaderboard displays top users
- ✅ Activity tracking records events
- (+ 6 more, see TESTING.md)

**Recommendations Tests (8 tests):**
- ✅ Content-based recommendations generated
- ✅ Collaborative filtering works
- ✅ Recommendations update with user activity
- ✅ "You might be interested in" displays
- ✅ Trending topics accurate
- (+ 3 more, see TESTING.md)

**Briefings Tests (10 tests):**
- ✅ Daily briefing generated
- ✅ Briefing includes new documents
- ✅ Briefing includes patterns
- ✅ Briefing notification appears
- ✅ Briefing exports to PDF
- (+ 5 more, see TESTING.md)

**Dashboard Tests (5 tests):**
- ✅ Dashboard loads user stats
- ✅ Widgets customizable
- ✅ Recent activity displays
- ✅ Quick actions work
- ✅ Dashboard responsive on mobile

### Success Criteria

**Phase 3 Complete When:**
- ✅ All 35 tests passing (12 + 8 + 10 + 5)
- ✅ Achievements unlock and display
- ✅ Streaks track accurately
- ✅ Recommendations personalized per user
- ✅ Daily briefing generates automatically
- ✅ Personalized dashboard customizable
- ✅ Analytics tracking working
- ✅ UI is polished and engaging
- ✅ Users report system as "addictive"

---

## Phase 4: Collaboration & Polish (Weeks 5-6)

**Priority:** 🟢 MEDIUM for team adoption

**Goal:** Enable team knowledge sharing and finalize production-ready UI

### Why This Matters

**Team Collaboration Problem:**
- Knowledge silos (users work in isolation)
- No way to share discoveries
- No visibility into team activity
- No collaborative exploration

**Solution:**
- Document sharing with annotations
- Team activity feed
- Collaborative graph sessions
- Advanced visualizations (3D, timeline, heatmaps)

**Impact:**
- Team collaboration around shared knowledge
- Faster knowledge discovery through social learning
- Increased engagement through social features

### Deliverables

#### Week 5: Collaboration Features

**4.1 Document Sharing & Annotations**

**Sharing Features:**
- Share document with specific users
- Share document with teams
- Public sharing (generate link)
- Annotations on shared documents

**Database Schema:**

```sql
CREATE TABLE document_shares (
    uuid UUID PRIMARY KEY,
    document_uuid UUID NOT NULL,
    shared_by UUID REFERENCES users(uuid),
    shared_with UUID REFERENCES users(uuid), -- NULL for public share
    share_link_token VARCHAR(255) UNIQUE, -- For public shares
    can_annotate BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE TABLE document_annotations (
    uuid UUID PRIMARY KEY,
    document_uuid UUID NOT NULL,
    user_uuid UUID REFERENCES users(uuid),
    annotation_type VARCHAR(50), -- 'highlight' | 'comment' | 'tag'
    content TEXT,
    position JSONB, -- {page: 1, x: 100, y: 200}
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Frontend Components:**
- `ShareDialog.tsx` - Share document modal
- `AnnotationToolbar.tsx` - Annotation tools
- `AnnotationMarker.tsx` - Visual annotation display
- `ShareLinkGenerator.tsx` - Generate public share links

**4.2 Team Activity Feed**

**Activity Types:**
- Document uploaded
- Document shared
- Graph explored
- Pattern discovered
- Achievement unlocked
- Conversation started

**Frontend Components:**
- `ActivityFeed.tsx` - Scrollable team activity timeline
- `ActivityCard.tsx` - Single activity item
- `ActivityFilter.tsx` - Filter by user/type

**Layout:**

```
┌──────────────────────────────────────────┐
│ Team Activity                     [Filter]│
├──────────────────────────────────────────┤
│                                          │
│ 🔍 Alice explored "CAT Equipment"       │
│    2 hours ago                           │
│                                          │
│ 📄 Bob uploaded "Maintenance Schedule"  │
│    3 hours ago                           │
│                                          │
│ 🏆 Charlie unlocked "Deep Diver"        │
│    5 hours ago                           │
│                                          │
│ 💬 Alice started conversation           │
│    "How do we track maintenance?"        │
│    1 day ago                             │
│                                          │
│ [Load More]                              │
└──────────────────────────────────────────┘
```

**4.3 Collaborative Graph Exploration**

**Features:**
- Multiple users view same graph simultaneously
- Real-time cursor positions ("Alice is viewing...")
- Shared annotations on graph nodes
- Live chat during exploration

**Implementation:**
- WebSocket connection for real-time updates
- Shared graph state (Zustand + WebSocket sync)
- Cursor tracking and display

**Frontend Components:**
- `CollaborativeGraph.tsx` - Multi-user graph viewer
- `UserCursor.tsx` - Remote user cursor display
- `CollaborativeChatPanel.tsx` - Live chat sidebar

#### Week 6: Advanced Visualizations & Polish

**4.4 Advanced Visualizations**

**3D Knowledge Graph:**
- React Force Graph 3D
- VR/AR mode (optional)
- Immersive graph exploration

**Timeline View:**
- Temporal patterns visualization
- Document upload timeline
- Entity creation timeline
- Filter by date range

**Heatmaps:**
- Activity heatmap (time of day, day of week)
- Topic popularity heatmap
- User engagement heatmap

**Frontend Components:**
- `Graph3D.tsx` - 3D force-directed graph
- `TimelineView.tsx` - Temporal visualization
- `ActivityHeatmap.tsx` - Heatmap component
- `VisualizationSwitcher.tsx` - Toggle between views

**4.5 Theme Switcher**

**Themes:**
- Dark mode (default)
- Light mode
- High contrast mode (accessibility)
- Custom themes (future)

**Implementation:**
- TailwindCSS dark mode classes
- Theme context provider
- Persistent theme preference

**4.6 Performance Optimization**

**Optimizations:**
- Code splitting (React.lazy)
- Virtual scrolling for large lists
- Image lazy loading
- Service worker for offline support
- Bundle size analysis and reduction

**4.7 Accessibility Audit**

**WCAG 2.1 AA Compliance:**
- Keyboard navigation for all features
- Screen reader support (ARIA labels)
- Color contrast ratios >4.5:1
- Focus indicators visible
- Skip links for navigation
- Alt text for images
- Form labels and error messages

**Tools:**
- axe DevTools
- Lighthouse accessibility audits
- Manual testing with screen readers (NVDA, JAWS)

### Technical Tasks

**Week 5: Collaboration**

**Day 1: Sharing Backend**
1. Create sharing database schema
2. Implement sharing service
3. Add sharing API endpoints
4. Implement share link generation

**Day 2: Sharing Frontend**
5. Create ShareDialog.tsx component
6. Add sharing UI to document cards
7. Implement public share link viewer
8. Add annotation toolbar

**Day 3: Team Activity Feed**
9. Create activity feed backend service
10. Add activity tracking for team events
11. Create ActivityFeed.tsx component
12. Add activity filtering

**Day 4: Collaborative Graph**
13. Set up WebSocket server for real-time sync
14. Create CollaborativeGraph.tsx
15. Add user cursor tracking
16. Implement live chat panel

**Day 5: Testing Week 5**
17. Write 12 collaboration tests
18. Test sharing flows
19. Test real-time graph sync
20. Test activity feed accuracy
21. Bug fixes and polish

**Week 6: Visualizations & Polish**

**Day 1: Advanced Visualizations**
22. Add react-force-graph-3d dependency
23. Create Graph3D.tsx component
24. Create TimelineView.tsx component
25. Create ActivityHeatmap.tsx component
26. Add visualization switcher UI

**Day 2: Theme & Polish**
27. Implement theme switcher
28. Add dark/light mode styles
29. Create high contrast theme
30. Polish animations and transitions
31. Add loading skeletons

**Day 3: Performance Optimization**
32. Implement code splitting
33. Add virtual scrolling for document lists
34. Optimize bundle size (tree shaking)
35. Add service worker (offline support)
36. Run Lighthouse performance audits
37. Fix performance bottlenecks

**Day 4: Accessibility Audit**
38. Run axe DevTools on all pages
39. Fix accessibility issues
40. Add ARIA labels to interactive elements
41. Test keyboard navigation
42. Test with screen reader (NVDA)
43. Ensure color contrast compliance

**Day 5: Final Testing & Documentation**
44. Write 11 final tests (see TESTING.md)
45. End-to-end regression testing
46. User acceptance testing (UAT)
47. Update all documentation
48. Create deployment guide
49. Prepare release notes

### Testing Checklist

**Collaboration Tests (12 tests):**
- ✅ Share document with user
- ✅ Share document via public link
- ✅ Add annotation to shared document
- ✅ Activity feed displays team events
- ✅ Collaborative graph syncs in real-time
- ✅ User cursors display correctly
- (+ 6 more, see TESTING.md)

**Visualization Tests (6 tests):**
- ✅ 3D graph renders correctly
- ✅ Timeline view displays documents
- ✅ Heatmap shows activity patterns
- ✅ Visualization switcher works
- ✅ Theme switcher changes colors
- ✅ All visualizations responsive

**Performance Tests (3 tests):**
- ✅ Dashboard loads in <2s
- ✅ Graph renders 100 nodes in <500ms
- ✅ Lighthouse score >90

**Accessibility Tests (2 tests):**
- ✅ WCAG 2.1 AA compliance (axe)
- ✅ Keyboard navigation works

### Success Criteria

**Phase 4 Complete When:**
- ✅ All 23 tests passing (12 + 6 + 3 + 2)
- ✅ Document sharing works
- ✅ Team activity feed accurate
- ✅ Collaborative graph real-time sync works
- ✅ 3D graph, timeline, heatmaps functional
- ✅ Theme switcher works
- ✅ Performance: Lighthouse >90
- ✅ Accessibility: WCAG 2.1 AA compliant
- ✅ All documentation complete
- ✅ **READY FOR PRODUCTION DEPLOYMENT**

---

## Dependencies & Prerequisites

### External Dependencies

**New npm packages to add:**

```json
{
  "dependencies": {
    "react-router-dom": "^6.21.3",
    "react-force-graph-3d": "^1.43.0",
    "zustand": "^4.5.0",
    "react-hook-form": "^7.49.3",
    "zod": "^3.22.4",
    "@tanstack/react-query": "^5.17.19",
    "socket.io-client": "^4.6.1",
    "recharts": "^2.10.4",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "@playwright/test": "^1.41.1",
    "@axe-core/react": "^4.8.4",
    "vitest": "^1.2.0"
  }
}
```

**Python packages to add:**

```txt
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
itsdangerous==2.1.2
websockets==12.0
```

### Prerequisites

**Before starting Phase 1:**
- ✅ Current UI (85% complete) tested and working
- ✅ Backend API accessible at `/api/v1/*`
- ✅ PostgreSQL database available
- ✅ Claude API key configured
- ✅ Frontend dev environment set up (Node.js 18+, npm 9+)

**Before starting Phase 2:**
- ✅ Phase 1 complete (authentication working)
- ✅ User database schema created
- ✅ Protected routes functional
- ✅ Claude API integration tested

**Before starting Phase 3:**
- ✅ Phase 2 complete (conversation working)
- ✅ Conversation database schema created
- ✅ User activity tracking functional

**Before starting Phase 4:**
- ✅ Phase 3 complete (engagement features working)
- ✅ Achievement system functional
- ✅ Recommendations generating correctly
- ✅ Dashboard displaying user stats

---

## Risk Mitigation

### Technical Risks

**Risk 1: Claude API Rate Limits**

**Impact:** Conversation interface and daily briefings depend on Claude API

**Mitigation:**
- Implement caching for common queries
- Add rate limiting on frontend
- Queue requests during high load
- Fallback to cached responses if rate limit hit

**Risk 2: Real-time Collaboration Complexity**

**Impact:** WebSocket implementation for collaborative graph may be complex

**Mitigation:**
- Start with simple cursor tracking
- Use Socket.IO (battle-tested library)
- Phase approach: cursor → chat → graph sync
- Fallback to polling if WebSocket fails

**Risk 3: Performance Degradation with Large Graphs**

**Impact:** 3D graph may be slow with 1000+ nodes

**Mitigation:**
- Implement node clustering (group distant nodes)
- Add level-of-detail (LOD) rendering
- Limit graph depth to 3 hops
- Pagination for large result sets

**Risk 4: Authentication Security**

**Impact:** Security vulnerabilities in auth implementation

**Mitigation:**
- Use proven libraries (FastAPI Security, python-jose)
- Follow OWASP best practices
- Security audit before production
- Implement rate limiting on auth endpoints
- Use HTTPS only in production

### Schedule Risks

**Risk 1: Scope Creep**

**Impact:** Feature additions delay timeline

**Mitigation:**
- Strict phase gates (no starting Phase N+1 until Phase N complete)
- "Nice-to-have" features deferred to post-launch
- Weekly progress review
- Re-prioritize if behind schedule

**Risk 2: Testing Takes Longer Than Expected**

**Impact:** Testing phase extends timeline

**Mitigation:**
- Test-driven development (write tests first)
- Automated testing (CI/CD)
- Parallel testing (developers test while implementing)
- Budget extra time in Week 6 for final testing

---

## Success Criteria

### Phase-Level Success Criteria

**Phase 1 (Week 1) - Authentication:**
- ✅ 12/12 tests passing
- ✅ Users can register, login, logout
- ✅ Protected routes functional
- ✅ Admin access control working

**Phase 2 (Week 2) - Conversation:**
- ✅ 15/15 tests passing
- ✅ Natural language queries work
- ✅ Responses cite source documents
- ✅ Voice input functional

**Phase 3 (Weeks 3-4) - Engagement:**
- ✅ 35/35 tests passing
- ✅ Achievements unlock automatically
- ✅ Recommendations personalized
- ✅ Daily briefings generate
- ✅ Dashboard customizable

**Phase 4 (Weeks 5-6) - Collaboration & Polish:**
- ✅ 23/23 tests passing
- ✅ Document sharing works
- ✅ Collaborative graph real-time sync
- ✅ Performance: Lighthouse >90
- ✅ Accessibility: WCAG 2.1 AA

### Overall Success Criteria

**Functional Requirements:**
- ✅ 85/85 total tests passing
- ✅ All features implemented as designed
- ✅ Zero critical bugs
- ✅ Mobile-responsive on all devices

**Performance Requirements:**
- ✅ Dashboard loads in <2s
- ✅ Graph renders in <500ms (100 nodes)
- ✅ UI interaction latency <200ms
- ✅ Lighthouse score >90

**Quality Requirements:**
- ✅ WCAG 2.1 AA compliant
- ✅ Code coverage >80%
- ✅ Zero accessibility violations (axe)
- ✅ Cross-browser compatible (Chrome, Firefox, Safari, Edge)

**User Adoption Metrics (Post-Launch):**
- ✅ 80%+ daily active users (if deployed company-wide)
- ✅ 15+ minute average session duration
- ✅ 70%+ users try conversation interface (Week 1)
- ✅ 8/10+ user satisfaction rating

---

## Resource Requirements

### Development Team

**Minimum:**
- 1 Full-stack developer (React + Python)
- Part-time UX designer (for design review)

**Ideal:**
- 1 Frontend developer (React/TypeScript)
- 1 Backend developer (Python/FastAPI)
- 1 UX designer
- 1 QA engineer (testing)

### Infrastructure

**Development:**
- Local development environment (Node.js 18+, Python 3.11+)
- PostgreSQL database (localhost or dev server)
- Claude API key (development tier)

**Staging:**
- Staging server (Docker Compose)
- PostgreSQL database (staging)
- Redis (staging)
- Claude API key (production tier)

**Production:**
- Production servers (Docker + Kubernetes)
- PostgreSQL database (production, replicated)
- Redis (production, clustered)
- Claude API key (production tier with higher rate limits)

### Budget Estimates

**Claude API Costs (monthly):**
- Development: ~$50/month (10k requests)
- Production: ~$500/month (100k requests, depends on usage)

**Infrastructure:**
- Development: $0 (local)
- Staging: ~$50/month (small VPS)
- Production: ~$200/month (larger instances + database)

**Total 6-Week Project Budget:**
- Development labor: (varies by team)
- API costs: ~$300 (6 weeks × $50/week)
- Infrastructure: ~$300 (staging + production setup)
- **Total non-labor costs: ~$600**

---

## Next Steps

**Ready to start implementation?**

1. ✅ **Confirm team availability** (developers, designer, QA)
2. ✅ **Set start date** (calendar Week 1 begins)
3. ✅ **Read IMPLEMENTATION.md** (step-by-step guide)
4. ✅ **Set up development environment** (dependencies, local databases)
5. ✅ **Kick off Phase 1: Authentication** (Day 1 tasks)

**Questions before starting?**

- Review [RESEARCH-REFERENCES.md](RESEARCH-REFERENCES.md) for technical details
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review [examples/](examples/) for code samples

---

**Timeline Summary:**

| Week | Phase | Focus | Tests |
|------|-------|-------|-------|
| 1 | Phase 1 | Authentication Foundation | 12 |
| 2 | Phase 2 | AI Conversation Hub | 15 |
| 3 | Phase 2.5 | Claude Agents SDK Integration | 20 |
| 4-5 | Phase 3 | Engagement Layer | 35 |
| 6-7 | Phase 4 | Collaboration & Polish | 23 |

**Total:** 105 tests, 7 weeks, production-ready AI-native UI

---

**Let's build something incredible.** 🚀

---

**Last Updated:** 2025-10-21
**Version:** 2.0.0 (added Phase 2.5: Claude Agents SDK Integration)
**Maintainer:** Claude Code
