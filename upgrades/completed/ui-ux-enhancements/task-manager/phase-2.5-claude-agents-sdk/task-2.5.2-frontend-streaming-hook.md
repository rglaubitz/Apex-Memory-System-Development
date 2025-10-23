# Task 2.5.2: Frontend Streaming Hook

**Phase:** 2.5 - Claude Agents SDK Integration
**Status:** ⬜ Not Started
**Estimated Duration:** 4 hours (Day 3)
**Assigned To:** (filled during execution)

---

## Overview

Create useApexChat custom React hook using Vercel AI SDK's useChat hook with tool execution tracking and EventSource handling for real-time streaming responses.

---

## Dependencies

**Required Before Starting:**
- Task 2.5.1: Backend Streaming with Tool Use (requires /api/v1/chat/stream endpoint)
- Task 2.4: Frontend Chat Interface (requires ConversationHub structure)

**Enables After Completion:**
- Task 2.5.3: Artifacts Sidebar Component
- Task 2.5.4: ConversationHub Streaming Integration

---

## Success Criteria

✅ useApexChat hook functional with TypeScript types
✅ Tool execution tracking state maintained
✅ EventSource handles streaming events
✅ Hook exposes messages, input, submit, loading, toolExecutions
✅ onFinish callback clears tool execution state
✅ experimental_onFunctionCall handles tool events

---

## Research References

**Technical Documentation:**
- research/documentation/vercel-ai-sdk-overview.md (Lines: 1-100)
  - Key concepts: useChat hook, streaming, function calling

- research/documentation/usechat-hook.md (Lines: 1-150)
  - Key concepts: Hook API, onFinish, experimental_onFunctionCall

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2621-2672)
  - Complete useApexChat hook implementation

---

## Test Specifications

**Frontend Hook Tests:** (5 tests, part of 10 frontend tests)
- TESTING.md: Lines 1491-1534
- File: `frontend/src/__tests__/hooks/useApexChat.test.ts`

**Tests to pass:**
1. Hook initializes with empty messages
2. Hook tracks tool executions
3. onFinish clears tool executions
4. experimental_onFunctionCall updates state
5. Hook handles streaming errors

**Total Tests:** 5 (part of 10 total frontend tests)

---

## Implementation Steps

### Subtask 2.5.2.1: Create useApexChat Hook Structure

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/hooks/useApexChat.ts`

**Steps:**
1. Install Vercel AI SDK dependencies: `npm install ai @ai-sdk/anthropic`
2. Create TypeScript interface for ToolExecution (tool_name, status, result)
3. Import useChat from 'ai/react'
4. Create useApexChat function with conversationId parameter
5. Initialize toolExecutions state with useState
6. Configure useChat hook with api endpoint, body, callbacks
7. Return object with messages, input, handleInputChange, handleSubmit, isLoading, toolExecutions

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2625-2668 for complete code
import { useChat } from 'ai/react';
import { useState } from 'react';

interface ToolExecution {
  tool_name: string;
  status: 'pending' | 'executing' | 'completed';
  result?: any;
}

export function useApexChat(conversationId: string) {
  const [toolExecutions, setToolExecutions] = useState<ToolExecution[]>([]);

  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/v1/chat/stream',
    body: {
      conversation_uuid: conversationId,
    },
    // ... callbacks
  });

  return {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    toolExecutions,
  };
}
```

**Validation:**
```bash
# Check TypeScript compilation
cd frontend
npm run type-check

# Test import
npm run dev
# Open browser console, check for errors
```

**Expected Result:**
- Hook compiles without TypeScript errors
- useChat imported successfully
- State management functional

---

### Subtask 2.5.2.2: Implement Tool Execution Tracking

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/hooks/useApexChat.ts` (add callbacks)

**Steps:**
1. Add onFinish callback to useChat config
2. In onFinish: Clear toolExecutions state (setToolExecutions([]))
3. Add experimental_onFunctionCall callback
4. In experimental_onFunctionCall: Update toolExecutions state
5. Push new ToolExecution with status 'executing'
6. Handle async tool result updates from server

**Code Example:**
```typescript
const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
  api: '/api/v1/chat/stream',
  body: {
    conversation_uuid: conversationId,
  },
  onFinish: () => {
    setToolExecutions([]);
  },
  experimental_onFunctionCall: async ({ name, arguments: args }) => {
    // Track tool execution
    setToolExecutions(prev => [
      ...prev,
      { tool_name: name, status: 'executing' }
    ]);
    // Tool result handled by server streaming
  },
});
```

**Validation:**
```typescript
// Test in component
const { toolExecutions } = useApexChat('test-id');
console.log('Tool executions:', toolExecutions);
// Should be empty array initially
```

**Expected Result:**
- onFinish callback clears tool execution state
- experimental_onFunctionCall adds tool to tracking
- Tool status updates reflected in UI

---

### Subtask 2.5.2.3: Add EventSource Handling

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/hooks/useApexChat.ts` (add useEffect for EventSource)

**Steps:**
1. Add useEffect hook for EventSource setup (optional - useChat handles this)
2. Verify useChat handles SSE streaming automatically
3. Add error handling for streaming failures
4. Test reconnection behavior
5. Add cleanup on unmount

**Code Example:**
```typescript
// Note: Vercel AI SDK's useChat handles EventSource internally
// This step is primarily validation and error handling

export function useApexChat(conversationId: string) {
  // ... existing code

  // Optional: Add custom error handling
  const handleError = (error: Error) => {
    console.error('Streaming error:', error);
    setToolExecutions([]);
  };

  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/v1/chat/stream',
    body: {
      conversation_uuid: conversationId,
    },
    onError: handleError,
    // ... other callbacks
  });

  return { messages, input, handleInputChange, handleSubmit, isLoading, toolExecutions };
}
```

**Validation:**
```bash
# Test streaming in browser
# 1. Open Network tab in DevTools
# 2. Send a message
# 3. Verify EventSource connection
# 4. Check for "text/event-stream" content type
```

**Expected Result:**
- useChat handles SSE automatically
- Error states managed gracefully
- Cleanup on unmount prevents memory leaks

---

## Troubleshooting

**Common Issues:**

**Issue 1: useChat hook not streaming**
- See TROUBLESHOOTING.md:Lines 950-975
- Solution: Verify backend returns text/event-stream, check CORS headers, ensure body includes conversation_uuid

**Issue 2: Tool executions not updating**
- See TROUBLESHOOTING.md:Lines 1000-1025
- Solution: Verify experimental_onFunctionCall fires, check tool event format from backend

**Issue 3: TypeScript errors with useChat**
- See TROUBLESHOOTING.md:Lines 1050-1075
- Solution: Update ai package (npm install ai@latest), check @types packages

---

## Progress Tracking

**Subtasks:** 0/3 complete (0%)

- [ ] Subtask 2.5.2.1: Create useApexChat Hook Structure
- [ ] Subtask 2.5.2.2: Implement Tool Execution Tracking
- [ ] Subtask 2.5.2.3: Add EventSource Handling

**Tests:** 0/5 passing (0%)

**Last Updated:** 2025-10-21
