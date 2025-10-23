# Task 2.4: Frontend Chat Interface

**Phase:** 2 - AI Conversation Hub
**Status:** ⬜ Not Started
**Estimated Duration:** 6 hours
**Assigned To:** (filled during execution)

---

## Overview

Build React chat interface with conversation sidebar, message display with citations, real-time message sending, and auto-scroll to latest message.

---

## Dependencies

**Required Before Starting:**
- Task 2.3: Conversation API Endpoints (requires API)
- Task 1.2: Frontend Authentication UI (requires AuthContext)

**Enables After Completion:**
- Task 2.5: Voice Input and Testing

---

## Success Criteria

✅ ConversationHub component renders with sidebar and chat area
✅ Conversations list loads and displays
✅ "New Conversation" button creates conversation
✅ Messages display with correct styling (user vs. assistant)
✅ Citations displayed below assistant messages
✅ Input field sends messages and shows loading state
✅ Auto-scroll to bottom when new messages arrive
✅ Responsive layout works on mobile and desktop

---

## Research References

**Technical Documentation:**
- research/documentation/react/hooks-patterns.md (Lines: 1-100)
  - Key concepts: useState, useEffect, useRef for auto-scroll

- research/documentation/react/api-integration.md (Lines: 1-80)
  - Key concepts: Axios with auth headers, loading states

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 1928-2146)
  - Complete ConversationHub component
  - Styling and layout examples

---

## Test Specifications

**Frontend Component Tests:** (5 tests)
- TESTING.md: Lines 801-900
- File: `frontend/src/__tests__/components/ConversationHub.test.tsx`

**Tests to pass:**
1. ConversationHub renders empty state
2. Load conversations on mount
3. Create new conversation
4. Send message updates conversation
5. Citations display correctly

**Total Tests:** 5

---

## Implementation Steps

### Subtask 2.4.1: ConversationHub Component Structure

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/components/ConversationHub.tsx`

**Steps:**
1. Create TypeScript interfaces (Message, Citation, Conversation)
2. Set up component state (conversations, currentConversation, inputMessage, isLoading)
3. Create refs (messagesEndRef for auto-scroll)
4. Implement loadConversations function (GET /api/v1/conversations)
5. Implement createNewConversation function (POST /api/v1/conversations)
6. Add useEffect to load conversations on mount
7. Add useEffect to auto-scroll on message changes

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 1932-2011 for complete code
```

**Validation:**
```bash
# Start frontend
cd frontend
npm run dev

# Test in browser
# 1. Navigate to /conversations
# 2. Verify sidebar shows conversations
# 3. Click "New Conversation" button
# 4. Verify new conversation created
```

**Expected Result:**
- Component renders with sidebar and main area
- Conversations load on mount
- New conversation button functional
- State updates correctly

---

### Subtask 2.4.2: Message Display and Citations

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ConversationHub.tsx` (add message rendering)

**Steps:**
1. Implement message list rendering (map over currentConversation.messages)
2. Add conditional styling (user messages right-aligned blue, assistant left-aligned gray)
3. Render citations below assistant messages
4. Format citations with numbered references
5. Show document title and relevant excerpt
6. Add spacing and styling for readability

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2068-2112 for complete code
```

**Validation:**
```bash
# Test message display
# 1. Send a message in existing conversation
# 2. Verify user message appears right-aligned in blue
# 3. Verify assistant response appears left-aligned in gray
# 4. Verify citations show below assistant message
# 5. Verify excerpts truncated appropriately
```

**Expected Result:**
- Messages display with correct alignment
- User and assistant messages visually distinct
- Citations formatted as numbered list
- Excerpts show context from knowledge graph

---

### Subtask 2.4.3: Message Input and Sending

**Duration:** 1.5 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ConversationHub.tsx` (add sendMessage function)

**Steps:**
1. Implement sendMessage function (POST /api/v1/conversations/{uuid}/messages)
2. Add form submit handler
3. Update currentConversation with response
4. Clear input field after send
5. Show loading state during API call
6. Disable input while loading
7. Handle errors gracefully

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2010-2030, 2115-2133 for complete code
```

**Validation:**
```bash
# Test message sending
# 1. Type message in input field
# 2. Press Enter or click Send
# 3. Verify input shows "Sending..." state
# 4. Verify input disabled during send
# 5. Verify message appears in conversation
# 6. Verify input cleared after send
```

**Expected Result:**
- Enter key sends message
- Loading state shows during API call
- Input field disabled while loading
- Conversation updates with new messages
- Input clears after successful send

---

### Subtask 2.4.4: Layout and Styling

**Duration:** 0.5 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ConversationHub.tsx` (add layout CSS)

**Steps:**
1. Implement sidebar layout (fixed 256px width)
2. Add scrollable conversation list
3. Add scrollable message area
4. Add fixed input area at bottom
5. Style "New Conversation" button
6. Add hover effects and transitions
7. Ensure responsive design

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2032-2143 for complete code
```

**Validation:**
```bash
# Test layout
# 1. Resize browser window
# 2. Verify sidebar stays fixed width
# 3. Verify message area scrolls independently
# 4. Verify input stays at bottom
# 5. Test on mobile viewport (< 768px)
```

**Expected Result:**
- Sidebar fixed at 256px width
- Message area scrolls independently
- Input area fixed at bottom
- Layout responsive on mobile
- Smooth transitions and hover effects

---

## Troubleshooting

**Common Issues:**

**Issue 1: Messages not auto-scrolling**
- See TROUBLESHOOTING.md:Lines 550-575
- Solution: Verify messagesEndRef.current exists, use scrollIntoView with smooth behavior

**Issue 2: Citations not rendering**
- See TROUBLESHOOTING.md:Lines 600-625
- Solution: Check citations is array, handle null/undefined gracefully

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 2.4.1: ConversationHub Component Structure
- [ ] Subtask 2.4.2: Message Display and Citations
- [ ] Subtask 2.4.3: Message Input and Sending
- [ ] Subtask 2.4.4: Layout and Styling

**Tests:** 0/5 passing (0%)

**Last Updated:** 2025-10-21
