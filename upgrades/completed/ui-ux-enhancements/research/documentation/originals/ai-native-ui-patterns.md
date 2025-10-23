# AI-Native UI Patterns - Vercel AI SDK & Streaming Interfaces

**Primary Sources:**
- Vercel AI SDK Docs: https://ai-sdk.dev/docs
- useChat Hook Reference: https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat
- Vercel Blog: AI SDK 5 Announcement: https://vercel.com/blog/ai-sdk-5
- LogRocket: Unified AI Interfaces with Vercel SDK: https://blog.logrocket.com/unified-ai-interfaces-vercel-sdk/

**Date Accessed:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Documentation) + Tier 4 (Technical Blog Posts)

---

## Executive Summary

**What is AI-Native UI?**
Interfaces designed **for streaming, progressive responses** from LLMs, not traditional request/response patterns. AI-native UIs render content **as it's generated**, show **tool use in real-time**, and provide **immediate feedback** at every step.

**Vercel AI SDK:**
The leading open-source toolkit for building AI applications in TypeScript/JavaScript (2M+ weekly downloads). Provides:
- **Unified API** across 20+ AI providers (OpenAI, Anthropic, Google, etc.)
- **Framework hooks** (React, Svelte, Vue) for streaming chat interfaces
- **Automatic state management** for conversations, streaming, and error handling

**For Apex Memory System:**
We'll use Vercel AI SDK patterns to build conversation interfaces with Claude that **stream responses progressively**, **visualize tool calls** (search_apex_documents, query_apex_graph), and provide **real-time feedback** as Claude analyzes the knowledge base.

---

## Part 1: Core Concepts

### 1. Streaming vs. Request/Response

**Traditional (Request/Response):**
```
User: "Show me CAT equipment"
  ↓
[Loading spinner for 3-5 seconds]
  ↓
Full response appears at once
```

**AI-Native (Streaming):**
```
User: "Show me CAT equipment"
  ↓
"Searching..." (0.1s)
  ↓
"I found 45 documents about CAT equipment..." (0.5s - word by word)
  ↓
"Let me analyze the relationships..." (1.0s)
  ↓
[Result rendering progressively]
```

**Why Streaming Matters:**
- **Perceived performance** - User sees progress immediately (<200ms)
- **Engagement** - Users stay on page longer with real-time updates
- **Transparency** - Shows what AI is doing (searching, analyzing, synthesizing)
- **Interruptibility** - Users can stop long responses early

### 2. Message-Based Architecture

**UIMessage Type:**
```typescript
interface UIMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string | MessagePart[];  // Text or multi-modal parts
  createdAt?: Date;
  metadata?: Record<string, any>;
}

interface MessagePart {
  type: 'text' | 'tool-call' | 'tool-result' | 'image';
  // ... type-specific properties
}
```

**Conversation State:**
```typescript
const [messages, setMessages] = useState<UIMessage[]>([
  { id: '1', role: 'user', content: 'Show me CAT equipment' },
  { id: '2', role: 'assistant', content: 'Searching documents...' },
  { id: '3', role: 'tool', content: 'Found 45 documents', metadata: { tool: 'search_apex_documents' } },
  { id: '4', role: 'assistant', content: 'I found 45 documents about CAT equipment...' }
]);
```

### 3. Status-Based UI Rendering

```typescript
type ChatStatus = 'ready' | 'submitted' | 'streaming' | 'error';

function ConversationUI({ status }) {
  return (
    <>
      {status === 'submitted' && <LoadingIndicator />}
      {status === 'streaming' && <TypingIndicator />}
      {status === 'error' && <ErrorMessage />}
      {status === 'ready' && <ReadyPrompt />}
    </>
  );
}
```

---

## Part 2: Vercel AI SDK Architecture

### AI SDK Core (Backend)

**Purpose:** Unified interface for calling LLMs from any provider

```typescript
import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

const { text } = await generateText({
  model: anthropic('claude-sonnet-4-5'),
  messages: [
    { role: 'user', content: 'Explain quantum computing' }
  ]
});
```

**Key Functions:**
- `generateText()` - Single completion (non-streaming)
- `streamText()` - Streaming text generation
- `generateObject()` - Structured data with schema validation
- `streamObject()` - Streaming structured data

### AI SDK UI (Frontend)

**Purpose:** React hooks for managing conversation state and streaming

```typescript
import { useChat } from '@ai-sdk/react';

function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit, status } = useChat({
    api: '/api/chat',
    onFinish: (message) => console.log('Complete:', message),
    onError: (error) => console.error('Error:', error)
  });

  return (
    <div>
      {messages.map((m) => (
        <div key={m.id} className={m.role}>
          {m.content}
        </div>
      ))}

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          disabled={status === 'streaming'}
        />
        <button disabled={status === 'streaming'}>Send</button>
      </form>
    </div>
  );
}
```

**Available Hooks:**
- `useChat()` - Full conversation management
- `useCompletion()` - Single-turn completions
- `useObject()` - Streaming structured data
- `useAssistant()` - OpenAI Assistants API integration

---

## Part 3: useChat Hook Deep Dive

### Basic Usage

```typescript
import { useChat } from '@ai-sdk/react';

const {
  messages,      // UIMessage[] - Full conversation history
  input,         // string - Current input value
  status,        // ChatStatus - Current state
  error,         // Error | undefined

  // Methods
  sendMessage,   // (message, options?) => void
  setInput,      // (input: string) => void
  handleSubmit,  // (e: FormEvent) => void
  regenerate,    // (options?) => void
  stop,          // () => void
  clearError,    // () => void

  // Advanced
  addToolResult, // (toolCallId, result) => void
  setMessages,   // (messages) => void
  resumeStream   // () => void
} = useChat({
  api: '/api/chat',
  id: 'conversation-123',
  initialMessages: [],
  onFinish: (message) => {},
  onError: (error) => {},
  onToolCall: (toolCall) => {}
});
```

### Configuration Options

```typescript
useChat({
  // Endpoint
  api: '/api/apex/conversation',

  // Headers
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-User-ID': userId
  },

  // Credentials
  credentials: 'include',  // For cookies

  // Initial state
  id: 'conv-uuid',
  initialMessages: existingConversation,

  // Callbacks
  onFinish: (message) => {
    // Message complete
    saveConversation(message);
  },

  onError: (error) => {
    // Handle errors
    showErrorNotification(error.message);
  },

  onToolCall: async (toolCall) => {
    // Execute tool
    const result = await executeApexTool(toolCall);
    return result;
  },

  // Auto-send
  sendAutomaticallyWhen: ({ messages }) => {
    // Auto-send when tool results are added
    return messages[messages.length - 1].role === 'tool';
  }
});
```

### Status Flow

```
ready → submitted → streaming → ready
  ↓                    ↓
  └─── error ──────────┘
```

**UI Patterns by Status:**

```tsx
{status === 'ready' && (
  <button type="submit">Send Message</button>
)}

{status === 'submitted' && (
  <div className="flex items-center gap-2">
    <Spinner />
    <span>Sending...</span>
  </div>
)}

{status === 'streaming' && (
  <div className="flex items-center gap-2">
    <div className="typing-indicator" />
    <span>Claude is typing...</span>
    <button onClick={stop}>Stop</button>
  </div>
)}

{status === 'error' && error && (
  <div className="error-banner">
    <AlertCircle />
    <span>{error.message}</span>
    <button onClick={clearError}>Dismiss</button>
  </div>
)}
```

---

## Part 4: Streaming Patterns

### Pattern 1: Progressive Text Rendering

```tsx
function StreamingMessage({ message }) {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    // Simulate streaming (in real use, comes from useChat)
    let index = 0;
    const interval = setInterval(() => {
      if (index < message.content.length) {
        setDisplayedText(message.content.slice(0, index + 1));
        index++;
      } else {
        clearInterval(interval);
      }
    }, 20);  // 20ms per character

    return () => clearInterval(interval);
  }, [message.content]);

  return (
    <div className="message assistant">
      {displayedText}
      {displayedText.length < message.content.length && (
        <span className="cursor">▊</span>
      )}
    </div>
  );
}
```

### Pattern 2: Typing Indicator

```tsx
function TypingIndicator() {
  return (
    <div className="flex gap-1 p-4">
      <motion.div
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1, repeat: Infinity, delay: 0 }}
        className="w-2 h-2 bg-purple-500 rounded-full"
      />
      <motion.div
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
        className="w-2 h-2 bg-purple-500 rounded-full"
      />
      <motion.div
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
        className="w-2 h-2 bg-purple-500 rounded-full"
      />
      <span className="ml-2 text-sm text-white/60">Claude is typing...</span>
    </div>
  );
}
```

### Pattern 3: Tool Call Visualization

```tsx
function ToolCallIndicator({ toolCall }) {
  const icons = {
    search_apex_documents: <Search />,
    query_apex_graph: <Network />,
    get_apex_temporal_data: <Clock />
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-2 p-3 bg-white/5 rounded-lg border border-white/10"
    >
      {icons[toolCall.name] || <Tool />}
      <div className="flex-1">
        <p className="text-sm font-medium">Calling {toolCall.name}</p>
        <p className="text-xs text-white/60">
          {JSON.stringify(toolCall.arguments, null, 2)}
        </p>
      </div>
      <Spinner className="w-4 h-4" />
    </motion.div>
  );
}
```

### Pattern 4: Chunked Response Rendering

```tsx
function ChunkedMessage({ message }) {
  const chunks = useMemo(() => {
    // Split message into logical chunks (paragraphs, code blocks)
    return message.content.split(/\n\n+/);
  }, [message.content]);

  return (
    <div className="message-chunks">
      {chunks.map((chunk, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="chunk"
        >
          <ReactMarkdown>{chunk}</ReactMarkdown>
        </motion.div>
      ))}
    </div>
  );
}
```

---

## Part 5: Tool Use Integration

### Backend Route (Next.js API Route)

```typescript
// /app/api/apex/conversation/route.ts
import { streamText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: anthropic('claude-sonnet-4-5'),
    messages,
    tools: {
      search_apex_documents: {
        description: 'Search the Apex knowledge base for documents',
        parameters: z.object({
          query: z.string(),
          filters: z.object({
            file_type: z.enum(['pdf', 'docx', 'pptx']).optional()
          }).optional()
        }),
        execute: async ({ query, filters }) => {
          // Call Apex API
          const response = await fetch('http://localhost:8000/api/v1/query', {
            method: 'POST',
            body: JSON.stringify({ query, filters })
          });
          return await response.json();
        }
      },

      query_apex_graph: {
        description: 'Execute Cypher query on Neo4j knowledge graph',
        parameters: z.object({
          cypher: z.string(),
          parameters: z.record(z.any()).optional()
        }),
        execute: async ({ cypher, parameters }) => {
          const response = await fetch('http://localhost:8000/api/v1/graph/query', {
            method: 'POST',
            body: JSON.stringify({ cypher, parameters })
          });
          return await response.json();
        }
      }
    }
  });

  return result.toDataStreamResponse();
}
```

### Frontend Hook Usage

```tsx
function ApexConversation() {
  const { messages, input, handleInputChange, handleSubmit, status } = useChat({
    api: '/api/apex/conversation',
    onToolCall: async (toolCall) => {
      console.log('Tool called:', toolCall.name, toolCall.arguments);

      // Optionally show UI indicator
      showToolIndicator(toolCall);
    },
    onFinish: (message) => {
      console.log('Response complete:', message);

      // Save conversation
      saveConversation(messages);
    }
  });

  return (
    <div className="conversation">
      {messages.map((m) => (
        <Message key={m.id} message={m} />
      ))}

      {status === 'streaming' && <TypingIndicator />}

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Ask about your knowledge base..."
          disabled={status === 'streaming'}
        />
        <button type="submit" disabled={status === 'streaming'}>
          Send
        </button>
      </form>
    </div>
  );
}
```

---

## Part 6: Advanced Patterns

### Pattern 1: Message Branching

```tsx
function RegenerateButton({ messageId }) {
  const { regenerate } = useChat();

  return (
    <button
      onClick={() => regenerate({ messageId })}
      className="regenerate-btn"
    >
      <RefreshCw size={16} />
      Regenerate Response
    </button>
  );
}
```

### Pattern 2: Resume Interrupted Streams

```tsx
function ConversationWithRecovery() {
  const { messages, status, error, resumeStream, clearError } = useChat({
    api: '/api/chat',
    onError: (error) => {
      console.error('Stream interrupted:', error);
    }
  });

  if (error && status === 'error') {
    return (
      <div className="error-recovery">
        <p>Stream interrupted: {error.message}</p>
        <button onClick={resumeStream}>Resume Stream</button>
        <button onClick={clearError}>Start Fresh</button>
      </div>
    );
  }

  return <MessageList messages={messages} />;
}
```

### Pattern 3: Optimistic UI Updates

```tsx
function OptimisticMessage() {
  const { messages, setMessages, sendMessage } = useChat();

  const handleSend = async (content: string) => {
    // Optimistically add user message
    const optimisticMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      createdAt: new Date()
    };

    setMessages([...messages, optimisticMessage]);

    // Send to API (will replace optimistic message)
    await sendMessage(content);
  };

  return (
    <MessageInput onSend={handleSend} />
  );
}
```

### Pattern 4: Multi-Modal Messages

```tsx
function MultiModalInput() {
  const { sendMessage } = useChat();
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleImageUpload = async (file: File) => {
    const base64 = await fileToBase64(file);
    setImagePreview(base64);
  };

  const handleSubmit = () => {
    sendMessage({
      role: 'user',
      content: [
        { type: 'text', text: input },
        { type: 'image', image: imagePreview }
      ]
    });
  };

  return (
    <div className="multi-modal-input">
      <input type="file" accept="image/*" onChange={handleImageUpload} />
      {imagePreview && <img src={imagePreview} alt="Preview" />}
      <button onClick={handleSubmit}>Send</button>
    </div>
  );
}
```

---

## Part 7: Integration with Apex Memory System

### Apex-Specific Chat Hook

```typescript
// /hooks/useApexChat.ts
import { useChat } from '@ai-sdk/react';
import { useArtifactStore } from '@/stores/artifact';

export function useApexChat() {
  const { addArtifact } = useArtifactStore();

  return useChat({
    api: '/api/apex/conversation',

    headers: {
      'X-User-ID': localStorage.getItem('userId'),
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },

    onToolCall: async (toolCall) => {
      // Log tool calls for debugging
      console.log('[Apex Tool]', toolCall.name, toolCall.arguments);

      // Show tool indicator in UI
      const toolIndicatorId = showToolIndicator(toolCall);

      // Tool result will be handled by backend
      return () => {
        hideToolIndicator(toolIndicatorId);
      };
    },

    onFinish: (message) => {
      // Check if response contains artifact-worthy content
      if (message.metadata?.artifact) {
        addArtifact(message.metadata.artifact);
      }

      // Save conversation to backend
      saveConversation(message);

      // Track analytics
      trackMessageComplete(message);
    },

    onError: (error) => {
      // Show error notification
      showNotification({
        type: 'error',
        title: 'Conversation Error',
        message: error.message
      });

      // Log to monitoring
      logError('apex_conversation_error', error);
    }
  });
}
```

### Complete Apex Conversation Component

```tsx
// /components/ApexConversation.tsx
import { useApexChat } from '@/hooks/useApexChat';
import { ApexMessage } from './ApexMessage';
import { ApexInput } from './ApexInput';
import { ToolCallIndicator } from './ToolCallIndicator';
import { TypingIndicator } from './TypingIndicator';

export function ApexConversation() {
  const {
    messages,
    input,
    status,
    error,
    handleInputChange,
    handleSubmit,
    stop,
    clearError,
    regenerate
  } = useApexChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen bg-black">
      {/* Header */}
      <header className="backdrop-blur-xl bg-black/80 border-b border-white/10 p-4">
        <h1 className="text-xl font-semibold">Apex Memory Assistant</h1>
        <p className="text-sm text-white/60">
          Ask questions about your knowledge base
        </p>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <WelcomeScreen />
        )}

        {messages.map((message) => (
          <ApexMessage
            key={message.id}
            message={message}
            onRegenerate={() => regenerate({ messageId: message.id })}
          />
        ))}

        {/* Tool Call Indicators */}
        {messages.filter(m => m.role === 'tool').map((toolMessage) => (
          <ToolCallIndicator
            key={toolMessage.id}
            toolCall={toolMessage.metadata?.toolCall}
          />
        ))}

        {/* Typing Indicator */}
        {status === 'streaming' && <TypingIndicator />}

        {/* Error Banner */}
        {status === 'error' && error && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <AlertCircle className="text-red-400" />
            <p className="text-red-400 flex-1">{error.message}</p>
            <button onClick={clearError} className="text-red-400 hover:text-red-300">
              <X size={20} />
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="backdrop-blur-xl bg-black/80 border-t border-white/10 p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <ApexInput
            value={input}
            onChange={handleInputChange}
            onSubmit={handleSubmit}
            disabled={status === 'streaming'}
            onStop={stop}
            isStreaming={status === 'streaming'}
          />
        </form>
      </div>
    </div>
  );
}
```

---

## Part 8: Performance Optimization

### 1. Message Virtualization

```tsx
import { Virtuoso } from 'react-virtuoso';

function VirtualizedMessages({ messages }) {
  return (
    <Virtuoso
      style={{ height: '100%' }}
      data={messages}
      itemContent={(index, message) => (
        <ApexMessage message={message} />
      )}
    />
  );
}
```

### 2. Debounced Input

```tsx
const debouncedInput = useMemo(
  () => debounce((value) => setInput(value), 300),
  []
);
```

### 3. Lazy Load Message Components

```tsx
const CodeBlock = lazy(() => import('./CodeBlock'));
const ChartVisualization = lazy(() => import('./ChartVisualization'));

function MessageContent({ content }) {
  return (
    <Suspense fallback={<Skeleton />}>
      {content.type === 'code' && <CodeBlock code={content.code} />}
      {content.type === 'chart' && <ChartVisualization data={content.data} />}
    </Suspense>
  );
}
```

---

## Part 9: Accessibility

### Keyboard Shortcuts

```tsx
useEffect(() => {
  function handleKeyDown(e: KeyboardEvent) {
    // Cmd/Ctrl + Enter to send
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      handleSubmit(e as any);
    }

    // Escape to stop streaming
    if (e.key === 'Escape' && status === 'streaming') {
      stop();
    }
  }

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [status]);
```

### Screen Reader Announcements

```tsx
import { useAnnouncer } from '@react-aria/live-announcer';

function MessageAnnouncer({ message }) {
  const announce = useAnnouncer();

  useEffect(() => {
    if (message.role === 'assistant') {
      announce(`Assistant: ${message.content}`);
    }
  }, [message]);

  return null;
}
```

### Focus Management

```tsx
const inputRef = useRef<HTMLInputElement>(null);

useEffect(() => {
  if (status === 'ready') {
    inputRef.current?.focus();
  }
}, [status]);
```

---

## References

**Official Documentation (Tier 1):**
- Vercel AI SDK: https://ai-sdk.dev/docs
- useChat Hook: https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat
- Streaming Guide: https://ai-sdk.dev/docs/foundations/streaming

**Technical Articles (Tier 4):**
- Vercel Blog - AI SDK 5: https://vercel.com/blog/ai-sdk-5
- LogRocket - Unified AI Interfaces: https://blog.logrocket.com/unified-ai-interfaces-vercel-sdk/
- Medium - Frontend AI Integration 2025: https://medium.com/@gopesh.jangid/frontend-ai-integration-in-2025

**SDKs & Libraries:**
- @ai-sdk/react: https://www.npmjs.com/package/@ai-sdk/react
- @ai-sdk/anthropic: https://www.npmjs.com/package/@ai-sdk/anthropic
- Zod (schema validation): https://zod.dev/

**Related Patterns:**
- React Suspense: https://react.dev/reference/react/Suspense
- React Virtualization: https://github.com/petyosi/react-virtuoso
- Debouncing: https://www.npmjs.com/package/use-debounce

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Docs) + Tier 4 (Technical Articles)
