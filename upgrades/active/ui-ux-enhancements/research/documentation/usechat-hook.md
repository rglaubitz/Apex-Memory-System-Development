# useChat Hook - Complete API Reference

**Purpose:** Comprehensive guide to Vercel AI SDK's useChat hook
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Documentation)

**Primary Source:** https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat

**Related Documentation:**
- For SDK overview → see `vercel-ai-sdk-overview.md`
- For UI patterns → see `streaming-ui-patterns.md`
- For tool integration → see `tool-visualization.md`

---

## Overview

**useChat** is the primary React hook for building streaming chat interfaces with AI models. It provides:

- **Automatic state management** for messages and conversation
- **Streaming support** with progressive rendering
- **Tool execution** via onToolCall callback
- **Error handling** with retry capabilities
- **Form integration** with handleSubmit
- **Optimistic UI** for instant responsiveness

---

## Basic Usage

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

---

## Configuration Options

```typescript
useChat({
  // API Endpoint
  api: '/api/apex/conversation',

  // Request Configuration
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-User-ID': userId
  },
  credentials: 'include',  // For cookies
  body: {
    // Additional data sent with every request
    userId: 'user-123',
    sessionId: 'session-456'
  },

  // Initial State
  id: 'conv-uuid',
  initialMessages: existingConversation,

  // Callbacks
  onFinish: (message, options) => {
    // Message complete
    console.log('Final message:', message);
    saveConversation(messages);
  },

  onError: (error) => {
    // Handle errors
    console.error('Error:', error);
    showErrorNotification(error.message);
  },

  onToolCall: async (toolCall) => {
    // Execute tool
    console.log('Tool called:', toolCall.name, toolCall.arguments);
    const result = await executeApexTool(toolCall);
    return result;
  },

  onResponse: (response) => {
    // Raw response received
    console.log('Response status:', response.status);
  },

  // Auto-send Configuration
  sendAutomaticallyWhen: ({ messages }) => {
    // Auto-send when tool results are added
    return messages[messages.length - 1].role === 'tool';
  },

  // Experimental Features
  streamProtocol: 'data',  // or 'text'
  maxSteps: 5,             // Maximum automatic tool execution rounds
});
```

---

## Status Management

### Status Flow

```
ready → submitted → streaming → ready
  ↓                    ↓
  └─── error ──────────┘
```

### UI Patterns by Status

```tsx
import { useChat } from '@ai-sdk/react';

function ChatInterface() {
  const { status, error, stop, clearError } = useChat({ api: '/api/chat' });

  return (
    <div>
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
    </div>
  );
}
```

---

## Message Management

### Sending Messages

```typescript
// Method 1: Form submission (most common)
<form onSubmit={handleSubmit}>
  <input value={input} onChange={(e) => setInput(e.target.value)} />
  <button type="submit">Send</button>
</form>

// Method 2: Programmatic sending
sendMessage("Show me all CAT equipment");

// Method 3: With custom options
sendMessage("Search documents", {
  data: { filters: { file_type: 'pdf' } },
  options: { headers: { 'X-Priority': 'high' } }
});
```

### Manipulating Messages

```typescript
// Replace entire conversation
setMessages([
  { id: '1', role: 'user', content: 'Hello' },
  { id: '2', role: 'assistant', content: 'Hi there!' }
]);

// Append message
setMessages([...messages, newMessage]);

// Remove last message
setMessages(messages.slice(0, -1));

// Clear conversation
setMessages([]);
```

### Regenerating Responses

```typescript
// Regenerate last assistant message
regenerate();

// Regenerate with custom options
regenerate({
  options: { headers: { 'X-Model': 'claude-opus-4' } }
});
```

---

## Tool Execution

### Automatic Tool Execution

```typescript
useChat({
  api: '/api/apex/conversation',
  onToolCall: async (toolCall) => {
    // This runs automatically when Claude calls a tool
    console.log('Executing:', toolCall.name);

    switch (toolCall.name) {
      case 'search_apex_documents':
        return await fetch('/api/v1/query', {
          method: 'POST',
          body: JSON.stringify(toolCall.arguments)
        }).then(r => r.json());

      case 'query_apex_graph':
        return await fetch('/api/v1/graph/query', {
          method: 'POST',
          body: JSON.stringify(toolCall.arguments)
        }).then(r => r.json());

      default:
        throw new Error(`Unknown tool: ${toolCall.name}`);
    }
  }
});
```

### Manual Tool Results

```typescript
// For custom control, use addToolResult
addToolResult({
  toolCallId: 'toolu_123',
  result: {
    documents: [...],
    total: 45
  }
});
```

---

## Error Handling

### Handling Errors

```typescript
useChat({
  api: '/api/chat',
  onError: (error) => {
    if (error.message.includes('rate limit')) {
      showRateLimitWarning();
      // Retry after delay
      setTimeout(() => regenerate(), 60000);
    } else if (error.message.includes('token limit')) {
      showTokenLimitError();
      // Suggest clearing conversation
    } else {
      showGenericError(error.message);
    }
  }
});
```

### Retry on Error

```typescript
const { error, regenerate, clearError } = useChat({ api: '/api/chat' });

if (error) {
  return (
    <div>
      <p>Error: {error.message}</p>
      <button onClick={() => { clearError(); regenerate(); }}>
        Retry
      </button>
    </div>
  );
}
```

---

## Complete Example

```tsx
import { useChat } from '@ai-sdk/react';
import { Send, StopCircle } from 'lucide-react';

export function ApexConversation() {
  const {
    messages,
    input,
    status,
    error,
    handleSubmit,
    setInput,
    stop,
    clearError,
    regenerate
  } = useChat({
    api: '/api/apex/conversation',
    id: 'apex-chat',
    initialMessages: [],

    onToolCall: async (toolCall) => {
      // Show tool indicator in UI
      showToolIndicator(toolCall);

      // Execute tool
      const result = await executeApexTool(toolCall);
      return result;
    },

    onFinish: (message) => {
      // Save conversation to local storage
      localStorage.setItem('apex-conversation', JSON.stringify(messages));
    },

    onError: (error) => {
      console.error('Chat error:', error);
      showErrorToast(error.message);
    }
  });

  return (
    <div className="flex flex-col h-screen">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[70%] rounded-lg p-3 ${
              message.role === 'user'
                ? 'bg-purple-600 text-white'
                : 'bg-white/10 text-white'
            }`}>
              {message.content}
            </div>
          </div>
        ))}

        {status === 'streaming' && (
          <div className="flex items-center gap-2 text-white/60">
            <div className="typing-indicator" />
            <span>Claude is typing...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            <p className="text-red-400">{error.message}</p>
            <button
              onClick={() => { clearError(); regenerate(); }}
              className="mt-2 text-sm text-red-400 hover:text-red-300"
            >
              Retry
            </button>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-white/10">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your knowledge base..."
            disabled={status === 'streaming'}
            className="flex-1 bg-white/10 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          {status === 'streaming' ? (
            <button
              type="button"
              onClick={stop}
              className="p-2 bg-red-500 rounded-lg hover:bg-red-600"
            >
              <StopCircle className="w-5 h-5" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim() || status !== 'ready'}
              className="p-2 bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              <Send className="w-5 h-5" />
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
```

---

## References

**Official Documentation:**
- useChat Reference: https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat
- AI SDK UI Overview: https://ai-sdk.dev/docs/ai-sdk-ui
- Examples: https://github.com/vercel/ai/tree/main/examples

**Related Documentation:**
- SDK overview → `vercel-ai-sdk-overview.md`
- Streaming patterns → `streaming-ui-patterns.md`
- Tool integration → `tool-visualization.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Documentation)
