# Streaming UI Patterns - Progressive Rendering

**Purpose:** UI patterns for rendering streaming AI responses
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 1 + Tier 2 (Official docs + verified examples)

**Related Documentation:**
- For SDK overview → see `vercel-ai-sdk-overview.md`
- For useChat hook → see `usechat-hook.md`
- For tool visualization → see `tool-visualization.md`

---

## Overview

Streaming UI patterns create **engaging, transparent interfaces** that show AI progress in real-time rather than blocking with loading spinners.

**Key Principles:**
1. **Immediate feedback** - Show progress within 200ms
2. **Word-by-word rendering** - Text appears as it streams
3. **Visual indicators** - Typing animations, progress bars
4. **Interruptibility** - Stop button always available
5. **Error recovery** - Graceful degradation with retry

---

## Pattern 1: Progressive Text Rendering

### Word-by-Word Streaming

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
        <span className="cursor animate-pulse">▊</span>
      )}
    </div>
  );
}
```

### Chunked Response Rendering

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

## Pattern 2: Typing Indicators

### Animated Dots

```tsx
import { motion } from 'framer-motion';

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

### Progress Bar

```tsx
function StreamingProgressBar({ progress }: { progress: number }) {
  return (
    <div className="w-full bg-white/10 rounded-full h-1 overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ ease: 'linear' }}
        className="h-full bg-purple-500"
      />
    </div>
  );
}
```

---

## Pattern 3: Status Transitions

### Smooth State Changes

```tsx
import { AnimatePresence, motion } from 'framer-motion';

function StatusIndicator({ status }) {
  return (
    <AnimatePresence mode="wait">
      {status === 'submitted' && (
        <motion.div
          key="submitted"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="flex items-center gap-2"
        >
          <Spinner />
          <span>Sending...</span>
        </motion.div>
      )}

      {status === 'streaming' && (
        <motion.div
          key="streaming"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="flex items-center gap-2"
        >
          <TypingIndicator />
          <button onClick={stop}>Stop</button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

---

## Pattern 4: Auto-Scroll

### Smart Scroll Behavior

```tsx
function MessageList({ messages, status }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Auto-scroll when new content arrives
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, autoScroll]);

  // Detect manual scroll
  const handleScroll = () => {
    if (!scrollRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;

    setAutoScroll(isAtBottom);
  };

  return (
    <div
      ref={scrollRef}
      onScroll={handleScroll}
      className="overflow-y-auto"
    >
      {messages.map((m) => (
        <Message key={m.id} message={m} />
      ))}

      {status === 'streaming' && <TypingIndicator />}
    </div>
  );
}
```

---

## Pattern 5: Markdown Streaming

### Progressive Markdown Rendering

```tsx
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

function StreamingMarkdown({ content }) {
  return (
    <ReactMarkdown
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter language={match[1]} {...props}>
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
```

---

## Performance Optimization

### Debounced Updates

```typescript
import { useMemo, useState } from 'react';
import { debounce } from 'lodash';

function useStreamingContent(content: string) {
  const [displayContent, setDisplayContent] = useState('');

  const debouncedUpdate = useMemo(
    () => debounce((newContent: string) => {
      setDisplayContent(newContent);
    }, 50),  // Update UI every 50ms max
    []
  );

  useEffect(() => {
    debouncedUpdate(content);
  }, [content, debouncedUpdate]);

  return displayContent;
}
```

### Virtualized Messages

```tsx
import { Virtuoso } from 'react-virtuoso';

function VirtualizedMessageList({ messages }) {
  return (
    <Virtuoso
      data={messages}
      itemContent={(index, message) => (
        <Message message={message} />
      )}
      followOutput="smooth"
    />
  );
}
```

---

## Accessibility

### Screen Reader Announcements

```tsx
import { useAnnouncer } from '@react-aria/live-announcer';

function StreamingChat() {
  const announce = useAnnouncer();
  const { messages, status } = useChat({ api: '/api/chat' });

  useEffect(() => {
    if (status === 'streaming') {
      announce('New message streaming');
    } else if (status === 'ready') {
      announce('Message complete');
    }
  }, [status, announce]);

  return <MessageList messages={messages} />;
}
```

### Keyboard Controls

```tsx
useEffect(() => {
  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Escape' && status === 'streaming') {
      stop();
      announce('Streaming stopped');
    }
  }

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [status, stop]);
```

---

## References

**Official Documentation:**
- Vercel AI SDK: https://ai-sdk.dev/docs
- React Markdown: https://github.com/remarkjs/react-markdown
- Framer Motion: https://www.framer.com/motion/

**Related Documentation:**
- SDK overview → `vercel-ai-sdk-overview.md`
- useChat hook → `usechat-hook.md`
- Tool visualization → `tool-visualization.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 + Tier 2 (Official + Verified Examples)
