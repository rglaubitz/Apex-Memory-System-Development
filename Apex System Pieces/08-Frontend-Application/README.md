# 08 - Frontend Application (React SPA)

## 🎯 Purpose

Provides modern web interface for document upload, intelligent querying, streaming AI chat, and conversation management. Built with React 18, TypeScript, and Tailwind CSS.

## 🛠 Technical Stack

- **React 18.3:** UI framework
- **TypeScript 5:** Type safety
- **Vite 5:** Build tool (fast HMR)
- **Tailwind CSS:** Utility-first styling
- **shadcn/ui:** Component library
- **Vercel AI SDK:** Streaming chat
- **React Router 6:** Client-side routing
- **Axios:** HTTP client with interceptors

## 📂 Key Files

**Location:** `apex-memory-system/src/apex_memory/frontend/`

### Core Application
- `src/App.tsx` (14,380 bytes) - Main app with routing
- `src/main.tsx` (550 bytes) - React entry point
- `src/routes.tsx` (1,781 bytes) - Route definitions

### Components (27 total)
- `components/chat/ConversationsStreaming.tsx` - Streaming chat UI
- `components/chat/ArtifactSidebar.tsx` - 5 artifact types (table, markdown, JSON, graph, timeline)
- `components/auth/Login.tsx` - Authentication
- `components/auth/Register.tsx` - User registration
- `components/ui/*` - shadcn/ui components (button, sheet, dialog, etc.)

### Hooks (6 custom hooks)
- `hooks/useApexChat.ts` - Wraps Vercel AI SDK with SSE
- `hooks/useAuth.ts` - Authentication state
- `hooks/use-toast.ts` - Toast notifications

### Contexts
- `contexts/AuthContext.tsx` - Global auth state
- `contexts/ThemeContext.tsx` - Dark/light mode

### Pages (8 pages)
- `pages/ConversationsPage.tsx` - Chat interface
- `pages/LoginPage.tsx` - Authentication
- `pages/RegisterPage.tsx` - Registration
- `pages/DocumentsPage.tsx` - Document management
- `pages/ProfilePage.tsx` - User profile + achievements
- `pages/BriefingsPage.tsx` - Daily AI briefings

## Key Features

### 1. Streaming Chat with Claude
- Real-time SSE (Server-Sent Events)
- Progressive message rendering
- Tool execution indicators
- 5 artifact types in sidebar

### 2. Authentication
- JWT-based with auto-refresh
- Protected routes
- Role-based access control

### 3. Document Upload
- Drag-and-drop interface
- Multi-format support (PDF, DOCX, PPTX, HTML, MD, TXT)
- Progress indicators

### 4. Conversation Management
- Create/delete conversations
- History with search
- Message threading

## Development

```bash
cd apex-memory-system/src/apex_memory/frontend

# Install dependencies
npm install

# Development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

## Dependencies

**Key Libraries:**
```json
{
  "@ai-sdk/anthropic": "^2.0.35",
  "ai": "^5.0.76",
  "axios": "^1.7.9",
  "react": "^18.3.1",
  "react-router-dom": "^6.26.0",
  "tailwindcss": "^3.4.1",
  "framer-motion": "^12.23.22",
  "lucide-react": "^0.468.0"
}
```

---

**Previous Component:** [07-Database-Writers](../07-Database-Writers/README.md)
**Next Component:** [09-Cache-Layer](../09-Cache-Layer/README.md)
