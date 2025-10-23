# Vercel AI SDK Overview - Unified AI Interface

**Purpose:** Introduction to Vercel AI SDK for building AI applications
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Documentation)

**Primary Sources:**
- Vercel AI SDK Docs: https://ai-sdk.dev/docs
- Vercel Blog - AI SDK 5: https://vercel.com/blog/ai-sdk-5
- NPM Package: https://www.npmjs.com/package/ai (2M+ weekly downloads)

**Related Documentation:**
- For useChat hook details → see `usechat-hook.md`
- For streaming UI patterns → see `streaming-ui-patterns.md`
- For tool visualization → see `tool-visualization.md`

---

## What is AI-Native UI?

**Definition:** Interfaces designed **for streaming, progressive responses** from LLMs, not traditional request/response patterns.

**Key Characteristics:**
- Render content **as it's generated** (word-by-word)
- Show **tool use in real-time** (searching, analyzing, querying)
- Provide **immediate feedback** at every step
- **Interruptible** - users can stop long responses

---

## Why Vercel AI SDK?

**Leading open-source toolkit** for building AI applications in TypeScript/JavaScript (2M+ weekly downloads).

**Key Benefits:**
1. **Unified API** across 20+ AI providers (OpenAI, Anthropic, Google, Cohere, Mistral)
2. **Framework hooks** (React, Svelte, Vue) for streaming chat interfaces
3. **Automatic state management** for conversations, streaming, and errors
4. **Provider-agnostic** - switch between models without code changes

---

## Core Concepts

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

## AI SDK Architecture

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
- `useChat()` - Full conversation management (most common)
- `useCompletion()` - Single-turn completions
- `useObject()` - Streaming structured data
- `useAssistant()` - OpenAI Assistants API integration

---

## Supported Providers

**AI SDK supports 20+ providers via unified interface:**

- **Anthropic** - Claude (Sonnet, Opus, Haiku)
- **OpenAI** - GPT-4, GPT-3.5
- **Google** - Gemini Pro, Gemini Ultra
- **Mistral** - Mistral Large, Medium, Small
- **Cohere** - Command R+, Command R
- **Azure OpenAI** - Enterprise GPT-4
- **AWS Bedrock** - Claude, Llama, Titan
- **Hugging Face** - Open source models
- **Groq** - Fast inference

**Switching providers is trivial:**
```typescript
// Anthropic
import { anthropic } from '@ai-sdk/anthropic';
const model = anthropic('claude-sonnet-4-5');

// OpenAI
import { openai } from '@ai-sdk/openai';
const model = openai('gpt-4-turbo');

// Google
import { google } from '@ai-sdk/google';
const model = google('gemini-1.5-pro');
```

---

## Installation

```bash
# Core SDK
npm install ai

# Provider SDKs (install as needed)
npm install @ai-sdk/anthropic
npm install @ai-sdk/openai
npm install @ai-sdk/google
```

**TypeScript Configuration:**
```json
{
  "compilerOptions": {
    "types": ["@ai-sdk/react"]
  }
}
```

---

## For Apex Memory System

**We'll use Vercel AI SDK patterns to:**

1. **Build conversation interfaces** with Claude (Anthropic provider)
2. **Stream responses progressively** for perceived performance
3. **Visualize tool calls** in real-time (search_apex_documents, query_apex_graph)
4. **Provide immediate feedback** as Claude analyzes the knowledge base
5. **Switch providers** easily if needed (e.g., test with GPT-4, deploy with Claude)

**Stack Convergence:**
- ✅ Already using React 18.3.1 + TypeScript 5.7.2
- ✅ Already using Vite 6.0.6
- ✅ Already using Framer Motion 12.x (animations)
- ✅ Add Vercel AI SDK for streaming chat

---

## References

**Official Documentation:**
- AI SDK Docs: https://ai-sdk.dev/docs
- AI SDK UI Reference: https://ai-sdk.dev/docs/reference/ai-sdk-ui
- GitHub Repository: https://github.com/vercel/ai (13k+ stars)

**Blog Posts & Tutorials:**
- Vercel Blog - AI SDK 5: https://vercel.com/blog/ai-sdk-5
- LogRocket: Unified AI Interfaces: https://blog.logrocket.com/unified-ai-interfaces-vercel-sdk/

**Related Documentation:**
- useChat hook details → `usechat-hook.md`
- Streaming UI patterns → `streaming-ui-patterns.md`
- Tool visualization → `tool-visualization.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Documentation)
