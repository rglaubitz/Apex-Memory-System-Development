# Task 2.5.4: ConversationHub Streaming Integration

**Phase:** 2.5 - Claude Agents SDK Integration
**Status:** ⬜ Not Started
**Estimated Duration:** 4 hours (Day 5)
**Assigned To:** (filled during execution)

---

## Overview

Update ConversationHub component to use useApexChat hook with streaming responses, integrate ArtifactSidebar, and add ToolUseIndicator component for live tool execution visualization.

---

## Dependencies

**Required Before Starting:**
- Task 2.5.2: Frontend Streaming Hook (requires useApexChat)
- Task 2.5.3: Artifacts Sidebar Component (requires ArtifactSidebar)
- Task 2.4: Frontend Chat Interface (requires ConversationHub base)

**Enables After Completion:**
- Task 2.5.5: Testing and Documentation

---

## Success Criteria

✅ ConversationHub uses useApexChat hook instead of axios
✅ Messages stream progressively in UI
✅ ToolUseIndicator shows live tool execution
✅ ArtifactSidebar wired to show tool results
✅ Tool executions trigger artifact display
✅ Smooth transitions between states
✅ Backward compatible with existing conversation list

---

## Research References

**Technical Documentation:**
- research/documentation/streaming-ui-patterns.md (Lines: 1-100)
  - Key concepts: Progressive rendering, loading indicators, real-time updates

- research/documentation/tool-visualization.md (Lines: 1-80)
  - Key concepts: Tool execution states, live indicators, artifact patterns

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2812-2875)
  - Complete ConversationHub update with streaming and artifacts

---

## Test Specifications

**Integration Tests:** (part of 15 integration tests)
- TESTING.md: Lines 1413-1489
- File: `tests/integration/test_streaming_flow.py`

**Tests validated by this task:**
- Stream chat basic
- Stream with tool use
- Artifacts display on tool execution
- Tool indicators show correct status

**Total Tests:** Part of 15 integration tests

---

## Implementation Steps

### Subtask 2.5.4.1: Integrate useApexChat Hook

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ConversationHub.tsx` (replace axios with useApexChat)

**Steps:**
1. Import useApexChat hook
2. Replace axios-based message sending with useApexChat
3. Remove manual state management for messages (useApexChat handles it)
4. Keep conversation list logic (separate from streaming)
5. Update state to use currentConversationId
6. Destructure messages, input, handleInputChange, handleSubmit, isLoading, toolExecutions from hook
7. Remove old sendMessage function
8. Update form to use handleSubmit from hook

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2817-2834 for complete code
import { useState } from 'react';
import { useApexChat } from '../hooks/useApexChat';
import { ArtifactSidebar } from './ArtifactSidebar';
import { ToolUseIndicator } from './ToolUseIndicator';

export function ConversationHub() {
  const [currentConversationId, setCurrentConversationId] = useState<string>('');
  const [isArtifactsOpen, setIsArtifactsOpen] = useState(false);
  const [artifacts, setArtifacts] = useState([]);

  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    toolExecutions,
  } = useApexChat(currentConversationId);

  // Keep existing conversation list logic
  // ...
}
```

**Validation:**
```bash
# Test in browser
# 1. Select a conversation
# 2. Type a message
# 3. Verify streaming response (not instant full message)
# 4. Check Network tab for EventSource connection
```

**Expected Result:**
- Messages stream progressively (not instant)
- Input handled by useApexChat hook
- Form submission triggers streaming
- Loading state shows during streaming

---

### Subtask 2.5.4.2: Add Tool Use Indicators

**Duration:** 1.5 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/components/ToolUseIndicator.tsx`

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ConversationHub.tsx` (add ToolUseIndicator)

**Steps:**
1. Create ToolUseIndicator component
2. Accept executions prop (ToolExecution[])
3. Render loading spinner for each executing tool
4. Show tool_name and status
5. Add smooth fade-in animation
6. Integrate into ConversationHub message list
7. Display ToolUseIndicator when toolExecutions.length > 0
8. Position below latest message

**Code Example:**
```typescript
// ToolUseIndicator.tsx
interface ToolUseIndicatorProps {
  executions: ToolExecution[];
}

export function ToolUseIndicator({ executions }: ToolUseIndicatorProps) {
  if (executions.length === 0) return null;

  return (
    <div className="animate-fade-in p-4 bg-blue-50 rounded-lg">
      {executions.map((exec, idx) => (
        <div key={idx} className="flex items-center gap-2 text-sm text-gray-700">
          <div className="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
          <span>Using tool: <strong>{exec.tool_name}</strong></span>
          <span className="text-gray-400">({exec.status})</span>
        </div>
      ))}
    </div>
  );
}

// In ConversationHub.tsx
{toolExecutions.length > 0 && (
  <ToolUseIndicator executions={toolExecutions} />
)}
```

**Validation:**
```bash
# Test tool indicator
# 1. Send message that triggers tool use ("Search for ACME")
# 2. Verify indicator appears below messages
# 3. Verify spinner animation
# 4. Verify indicator disappears when tool completes
```

**Expected Result:**
- Indicator shows when tools are executing
- Spinner animation smooth
- Tool name displayed clearly
- Indicator fades out when complete

---

### Subtask 2.5.4.3: Wire Artifacts Sidebar

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ConversationHub.tsx` (add artifact logic)

**Steps:**
1. Add useEffect to watch toolExecutions
2. When tool execution completes, parse result and create Artifact
3. Map tool_name to artifact type
4. Add artifact to artifacts state
5. Open artifacts sidebar (setIsArtifactsOpen(true))
6. Render ArtifactSidebar component in ConversationHub
7. Add button to toggle artifacts sidebar

**Code Example:**
```typescript
// In ConversationHub
import { useEffect } from 'react';

useEffect(() => {
  // Watch for completed tool executions
  const completed = toolExecutions.filter(exec => exec.status === 'completed' && exec.result);
  if (completed.length > 0) {
    const newArtifacts = completed.map(exec => ({
      type: mapToolToArtifactType(exec.tool_name),
      title: formatToolTitle(exec.tool_name),
      data: exec.result,
    }));
    setArtifacts(prev => [...prev, ...newArtifacts]);
    setIsArtifactsOpen(true);
  }
}, [toolExecutions]);

function mapToolToArtifactType(toolName: string) {
  const mapping = {
    'search_knowledge_graph': 'search_results',
    'get_entity_relationships': 'relationships',
    'get_temporal_timeline': 'timeline',
    'find_similar_documents': 'similar_docs',
    'get_graph_statistics': 'statistics',
  };
  return mapping[toolName] || 'search_results';
}

// Render artifacts sidebar
<ArtifactSidebar
  isOpen={isArtifactsOpen}
  onClose={() => setIsArtifactsOpen(false)}
  artifacts={artifacts}
/>
```

**Validation:**
```bash
# Test artifacts sidebar
# 1. Send message that triggers tool ("Show me relationships for ACME")
# 2. Verify sidebar opens automatically
# 3. Verify artifact rendered with correct visualization
# 4. Verify multiple artifacts stack vertically
# 5. Test close button
```

**Expected Result:**
- Sidebar opens automatically on tool completion
- Correct visualization component used for each tool type
- Multiple artifacts display correctly
- Close button functional

---

### Subtask 2.5.4.4: Polish UX and Transitions

**Duration:** 0.5 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ConversationHub.tsx` (add animations)

**Steps:**
1. Add fade-in animation for new messages
2. Add smooth scroll to bottom when streaming
3. Add subtle pulse for ToolUseIndicator
4. Ensure Sheet slide animation smooth (Sheet default)
5. Test loading states (disable input while streaming)
6. Add empty state when no artifacts

**Code Example:**
```typescript
// Add Tailwind animations
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

// In component
<div className="animate-fade-in">
  {/* New messages */}
</div>

// Disable input while loading
<input
  value={input}
  onChange={handleInputChange}
  disabled={isLoading}
  className={isLoading ? 'opacity-50 cursor-not-allowed' : ''}
/>
```

**Validation:**
```bash
# Visual testing
# 1. Verify messages fade in
# 2. Check smooth scroll during streaming
# 3. Test input disabled state (grayed out during loading)
# 4. Verify all transitions <300ms (Apple standard)
```

**Expected Result:**
- All animations subtle and smooth
- Loading states clear (input disabled, spinner visible)
- No jarring transitions
- Follows Apple minimalist aesthetic

---

## Troubleshooting

**Common Issues:**

**Issue 1: Messages not streaming progressively**
- See TROUBLESHOOTING.md:Lines 1250-1275
- Solution: Verify useApexChat hook connected, check EventSource in Network tab, ensure backend streaming correctly

**Issue 2: Artifacts not opening**
- See TROUBLESHOOTING.md:Lines 1300-1325
- Solution: Check useEffect dependencies include toolExecutions, verify tool result format matches Artifact interface

**Issue 3: Tool indicators not showing**
- See TROUBLESHOOTING.md:Lines 1350-1375
- Solution: Verify toolExecutions state updating, check ToolUseIndicator conditional rendering

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 2.5.4.1: Integrate useApexChat Hook
- [ ] Subtask 2.5.4.2: Add Tool Use Indicators
- [ ] Subtask 2.5.4.3: Wire Artifacts Sidebar
- [ ] Subtask 2.5.4.4: Polish UX and Transitions

**Tests:** Part of 15 integration tests

**Last Updated:** 2025-10-21
