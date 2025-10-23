# Claude Quick Reference - UI/UX Enhancements

**Fast lookup for patterns, commands, and key findings from Phase 1 research.**

---

## 🔑 Key Research Findings

### No Separate "Agents SDK"
- **Finding:** No separate "Agents SDK" exists for Claude
- **Reality:** Agentic capabilities = Tool Use API + Streaming + Application Orchestration
- **Impact:** Simpler architecture, more control over implementation
- **Deep Dive:** `tool-use-api.md` + `streaming-api.md`

### Perfect Stack Convergence
- **All patterns use:** React 18, TypeScript, Tailwind CSS, Radix UI, Vite
- **Current Apex stack:** ✅ MATCHES PERFECTLY
- **Result:** Zero additional learning curve, gradual adoption possible
- **Deep Dive:** `vercel-ai-sdk-overview.md` + `shadcn-installation.md`

### Artifacts Sidebar Pattern
- **Desktop:** Side-by-side layout (conversation 60% / artifact 40%)
- **Mobile:** Full-screen modal with smooth transitions
- **Component:** Shadcn/ui Sheet (built on existing Radix UI Dialog)
- **Deep Dive:** `artifacts-layout.md` + `sheet-component.md`

### Streaming Chat Best Practice
- **Hook:** Vercel AI SDK `useChat` (2M+ weekly downloads)
- **Protocol:** Server-Sent Events (SSE)
- **State:** Automatic message history + status management
- **Deep Dive:** `usechat-hook.md` + `streaming-ui-patterns.md`

---

## 📂 File Locations

### ⭐ Navigation Hub
```
research/documentation/
├── INDEX.md                            # ⭐ START HERE - Decision trees for all chunks
└── WORKFLOW-GUIDE.md                   # ⭐ How to use chunks during development
```

### Research Documentation (Phase 1 - Chunked into 16 focused files)

**Claude Tool Use & Streaming (4 chunks):**
```
research/documentation/
├── tool-use-api.md                     # ~80 lines - Core tool calling patterns
├── streaming-api.md                    # ~120 lines - SSE streaming protocol
├── apex-tool-definitions.md            # ~230 lines - Apex-specific tools
└── tool-orchestration.md               # ~200 lines - Multi-step workflows
```

**Artifacts UI Pattern (4 chunks):**
```
research/documentation/
├── artifacts-layout.md                 # ~140 lines - Side-by-side layout
├── sheet-component.md                  # ~150 lines - Shadcn/ui Sheet
├── artifact-types.md                   # ~180 lines - Code/charts/documents
└── apex-artifacts-integration.md       # ~200 lines - Apex artifact patterns
```

**AI-Native UI Patterns (4 chunks):**
```
research/documentation/
├── vercel-ai-sdk-overview.md           # ~120 lines - What is Vercel AI SDK?
├── usechat-hook.md                     # ~200 lines - Complete useChat API
├── streaming-ui-patterns.md            # ~140 lines - Progressive rendering
└── tool-visualization.md               # ~170 lines - Showing tool calls
```

**Shadcn/ui Integration (4 chunks):**
```
research/documentation/
├── shadcn-installation.md              # ~150 lines - Getting started
├── component-catalog.md                # ~210 lines - 20 components
├── customization-guide.md              # ~80 lines - Theming & styling
└── apex-integration-strategy.md        # ~80 lines - Integration approach
```

### Planning Documents (Phase 2 - In Progress)
```
upgrades/active/ui-ux-enhancements/
├── README.md                           # Project overview + status dashboard
├── PLANNING.md                         # 6-week plan (needs Phase 2.5 addition)
├── IMPLEMENTATION.md                   # ⏳ PENDING - 2,000+ line guide
├── TESTING.md                          # ⏳ PENDING - 50-77 test specs
├── TROUBLESHOOTING.md                  # ⏳ PENDING - Common issues
└── RESEARCH-REFERENCES.md              # ⏳ PENDING - Complete bibliography
```

### Example Components
```
examples/
├── conversation-interface/
│   └── ConversationHub.tsx             # Current: 416 lines (needs Vercel AI SDK)
├── authentication/
│   └── Login.tsx                       # 371 lines (reference implementation)
└── gamification/
    └── AchievementBadge.tsx            # 127 lines (reference implementation)
```

### Handoffs
```
handoffs/
└── HANDOFF-PHASE1-RESEARCH.md          # ✅ Complete session summary
```

---

## 🛠️ Common Code Templates

### 1. Tool Definition (Claude Tool Use API)

```typescript
// Define Apex Memory System tools
const apexTools = [
  {
    name: "search_apex_documents",
    description: "Search the Apex knowledge base for documents matching query",
    input_schema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Natural language search query"
        },
        filters: {
          type: "object",
          properties: {
            date_range: { type: "string" },
            entity_types: { type: "array", items: { type: "string" } }
          }
        }
      },
      required: ["query"]
    },
    execute: async ({ query, filters }) => {
      const response = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, filters })
      });
      return await response.json();
    }
  },
  {
    name: "get_entity_timeline",
    description: "Get temporal timeline of entity appearances across documents",
    input_schema: {
      type: "object",
      properties: {
        entity_id: { type: "string", description: "Entity UUID" }
      },
      required: ["entity_id"]
    },
    execute: async ({ entity_id }) => {
      const response = await fetch(`http://localhost:8000/api/v1/entities/${entity_id}/timeline`);
      return await response.json();
    }
  }
];
```

### 2. Streaming Chat Hook (Vercel AI SDK)

```typescript
import { useChat } from '@ai-sdk/react';
import { useState } from 'react';

export function ConversationHub() {
  const [showArtifact, setShowArtifact] = useState(false);
  const [currentArtifact, setCurrentArtifact] = useState(null);

  const {
    messages,      // UIMessage[] - Full conversation history
    input,         // string - Current input value
    status,        // 'ready' | 'submitted' | 'streaming' | 'error'
    sendMessage,   // (message: string) => void
    handleSubmit,  // Form submission handler
    stop,          // () => void - Stop streaming
    reload,        // () => void - Retry last message
  } = useChat({
    api: '/api/apex/conversation',
    initialMessages: [],

    onToolCall: async ({ toolCallId, toolName, args }) => {
      console.log(`Tool called: ${toolName}`, args);
      // Show tool use indicator in UI
      return await apexTools.find(t => t.name === toolName)?.execute(args);
    },

    onFinish: (message) => {
      // Save conversation to Apex memory
      saveConversation(messages);

      // Check for artifacts in response
      const artifact = extractArtifact(message.content);
      if (artifact) {
        setCurrentArtifact(artifact);
        setShowArtifact(true);
      }
    },

    onError: (error) => {
      console.error('Chat error:', error);
      toast.error('Failed to send message');
    }
  });

  return (
    <div className="flex h-screen">
      <main className="flex-1 min-w-0">
        <MessageList messages={messages} />
        <InputArea
          value={input}
          onSubmit={handleSubmit}
          isStreaming={status === 'streaming'}
          onStop={stop}
        />
      </main>

      {showArtifact && (
        <ArtifactSidebar
          artifact={currentArtifact}
          onClose={() => setShowArtifact(false)}
        />
      )}
    </div>
  );
}
```

### 3. Artifacts Sidebar (Shadcn/ui Sheet)

```tsx
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Download, Copy, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ArtifactSidebarProps {
  artifact: {
    type: 'code' | 'document' | 'chart' | 'table';
    content: string;
    title?: string;
    language?: string;
  };
  onClose: () => void;
}

export function ArtifactSidebar({ artifact, onClose }: ArtifactSidebarProps) {
  const handleExport = () => {
    const blob = new Blob([artifact.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title || 'artifact'}.${artifact.language || 'txt'}`;
    a.click();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    toast.success('Copied to clipboard');
  };

  return (
    <Sheet open={true} onOpenChange={onClose}>
      <SheetContent
        side="right"
        className="w-[600px] sm:w-[540px] sm:max-w-[40vw]"
      >
        <SheetHeader>
          <div className="flex items-center justify-between">
            <SheetTitle>
              {artifact.title || `${artifact.type} Artifact`}
            </SheetTitle>
            <div className="flex gap-2">
              <Button variant="ghost" size="icon" onClick={handleCopy}>
                <Copy className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" onClick={handleExport}>
                <Download className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </SheetHeader>

        <div className="mt-6 h-[calc(100vh-8rem)] overflow-auto">
          {artifact.type === 'code' && (
            <CodeBlock
              code={artifact.content}
              language={artifact.language}
            />
          )}
          {artifact.type === 'document' && (
            <MarkdownRenderer content={artifact.content} />
          )}
          {artifact.type === 'chart' && (
            <ChartViewer data={JSON.parse(artifact.content)} />
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
```

### 4. Tool Use Indicator Component

```tsx
import { motion } from "framer-motion";
import { Loader2, Search, Database, Timeline } from "lucide-react";

interface ToolUseIndicatorProps {
  toolName: string;
  status: 'thinking' | 'executing' | 'complete';
  args?: Record<string, any>;
}

const TOOL_ICONS = {
  search_apex_documents: Search,
  get_entity_timeline: Timeline,
  query_database: Database,
};

export function ToolUseIndicator({ toolName, status, args }: ToolUseIndicatorProps) {
  const Icon = TOOL_ICONS[toolName] || Database;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="flex items-center gap-3 p-4 rounded-lg bg-purple-500/10 border border-purple-500/20"
    >
      <div className="relative">
        {status === 'executing' ? (
          <Loader2 className="h-5 w-5 animate-spin text-purple-400" />
        ) : (
          <Icon className="h-5 w-5 text-purple-400" />
        )}
      </div>

      <div className="flex-1">
        <div className="text-sm font-medium text-white">
          {toolName.replace(/_/g, ' ')}
        </div>
        {args && (
          <div className="text-xs text-white/60 mt-1">
            {Object.entries(args).map(([key, value]) => (
              <span key={key} className="mr-3">
                {key}: {String(value)}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="text-xs text-white/40">
        {status === 'thinking' && 'Planning...'}
        {status === 'executing' && 'Executing...'}
        {status === 'complete' && '✓ Done'}
      </div>
    </motion.div>
  );
}
```

### 5. Progressive Streaming Response

```tsx
import { motion } from "framer-motion";
import { useState, useEffect } from "react";

interface StreamingResponseProps {
  content: string;
  isStreaming: boolean;
}

export function StreamingResponse({ content, isStreaming }: StreamingResponseProps) {
  const [displayedContent, setDisplayedContent] = useState('');

  useEffect(() => {
    setDisplayedContent(content);
  }, [content]);

  return (
    <div className="prose prose-invert max-w-none">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <ReactMarkdown
          components={{
            code: ({ node, inline, className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <CodeBlock language={match[1]} code={String(children)} />
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {displayedContent}
        </ReactMarkdown>
      </motion.div>

      {isStreaming && (
        <motion.span
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          className="inline-block w-2 h-4 ml-1 bg-purple-400 rounded-sm"
        />
      )}
    </div>
  );
}
```

---

## 📦 Shadcn/ui Installation

### Initialize Shadcn/ui
```bash
cd apex-memory-system/ui
npx shadcn@latest init
```

**Config selections:**
- ✅ TypeScript
- ✅ Tailwind CSS (already configured)
- ✅ Use CSS variables for colors
- ✅ Import alias: `@/components`

### Add Required Components
```bash
# Core components for Artifacts
npx shadcn@latest add sheet dialog button

# Forms and inputs
npx shadcn@latest add input textarea label

# Feedback and status
npx shadcn@latest add toast progress badge

# Navigation
npx shadcn@latest add tabs command

# Data display
npx shadcn@latest add table card separator
```

### Custom Variant Example
```tsx
// /components/ui/button.tsx (modify after installation)
const buttonVariants = cva(
  "inline-flex items-center justify-center...",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        // APEX CUSTOM VARIANTS
        apex: "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600",
        apexGlass: "backdrop-blur-xl bg-white/10 border border-white/10 hover:bg-white/20"
      }
    }
  }
);
```

---

## 🧪 Testing Commands

### Run All Tests (Future)
```bash
cd apex-memory-system/ui
npm run test              # All tests
npm run test:unit         # Unit tests only
npm run test:integration  # Integration tests
npm run test:e2e          # End-to-end tests
```

### Component Development
```bash
npm run dev              # Start dev server (http://localhost:5173)
npm run storybook        # Component playground (future)
```

---

## 🎯 Critical Integration Points

### Apex API Endpoints (Existing)
```
POST   /api/v1/query                    # Universal query endpoint
GET    /api/v1/entities/:id/timeline    # Entity temporal timeline
POST   /api/v1/documents/ingest         # Document ingestion
GET    /api/v1/conversations/:id        # Conversation history
POST   /api/v1/conversations             # Create conversation
```

### New Endpoints Needed (Phase 2.5)
```
POST   /api/apex/conversation            # Streaming chat with tool use
GET    /api/apex/tools                   # Available tools list
POST   /api/apex/artifacts/:id           # Save artifact
GET    /api/apex/artifacts/:id           # Retrieve artifact
```

---

## 📊 Phase Progress Tracking

### ✅ Phase 1: Research (COMPLETE + CHUNKED)
- **Original:** 4 large files (~15,000 lines total)
- **Chunked:** 16 focused files (~150 lines average)
- **Navigation:** INDEX.md + WORKFLOW-GUIDE.md
- **Benefit:** Read 150 lines (focused) vs. 3,700 lines (overwhelmed)

### 🚀 Phase 2: Planning Updates (IN PROGRESS)
- [ ] Update PLANNING.md (add Phase 2.5)
- [ ] Create IMPLEMENTATION.md (2,000+ lines)
- [ ] Create TESTING.md (50-77 tests)
- [ ] Create TROUBLESHOOTING.md
- [ ] Create RESEARCH-REFERENCES.md

### ⏳ Phase 3: ADRs (PENDING)
- [ ] ADR-004: Claude Agents Integration
- [ ] ADR-005: Artifacts Sidebar Pattern
- [ ] ADR-006: Shadcn/ui Component Library

### ⏳ Phase 4: Example Components (PENDING)
- [ ] Update ConversationHub.tsx (Vercel AI SDK)
- [ ] Create ArtifactSidebar.tsx
- [ ] Create ToolUseIndicator.tsx
- [ ] Create StreamingResponse.tsx

---

## 🔗 Quick Links

**Research Documentation:**
- [Claude Tool Use & Streaming](research/documentation/claude-tool-use-and-streaming.md)
- [Artifacts Sidebar Pattern](research/documentation/claude-artifacts-ui-pattern.md)
- [AI-Native UI Patterns](research/documentation/ai-native-ui-patterns.md)
- [Shadcn/ui Integration](research/documentation/shadcn-ui-integration.md)

**Planning:**
- [Project README](README.md)
- [Planning Document](PLANNING.md)
- [Phase 1 Handoff](handoffs/HANDOFF-PHASE1-RESEARCH.md)

**Examples:**
- [Current ConversationHub](examples/conversation-interface/ConversationHub.tsx)
- [Login Component](examples/authentication/Login.tsx)

---

## 💡 Key Architectural Decisions

### 1. No Separate SDK Needed
**Decision:** Use Claude's native Tool Use API + Streaming
**Rationale:** Official "Agents SDK" doesn't exist; pattern is simpler than expected
**Impact:** Less complexity, more control, faster implementation

### 2. Gradual Shadcn/ui Adoption
**Decision:** Copy-paste components as needed (not all at once)
**Rationale:** Minimize breaking changes, ship incrementally
**Impact:** Low risk, faster iteration, full customization

### 3. Side-by-Side Artifacts Layout
**Decision:** Use Shadcn/ui Sheet for desktop, full-screen for mobile
**Rationale:** Matches user's vision from Claude Desktop, built on existing Radix UI
**Impact:** Familiar UX, accessible, responsive

### 4. Vercel AI SDK for Streaming
**Decision:** Use `useChat` hook instead of custom SSE implementation
**Rationale:** 2M+ weekly downloads, provider-agnostic, battle-tested
**Impact:** Faster development, better DX, community support

---

## 📝 Start Command (Resume Next Session)

```bash
# Navigate to UI/UX enhancements directory
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/ui-ux-enhancements

# Read latest handoff
cat handoffs/HANDOFF-PHASE1-RESEARCH.md

# Begin Phase 2: Planning Updates
# Start with: Update PLANNING.md to add Phase 2.5 (Agents SDK Integration)
```

---

**Last Updated:** 2025-10-21 (Pre-compact checkpoint)
**Next Milestone:** Planning documents complete (5 files)
**Timeline:** Phase 2 = 2-3 hours
