# Workflow Guide - Using Chunked Documentation During Development

**Purpose:** Structured workflow for using chunked research docs throughout the project
**Created:** 2025-10-21
**Goal:** Ensure research gets used, not forgotten

---

## The Problem This Solves

**Without chunking:**
- Claude reads 3,700-line file → uses ~15,000 tokens
- Loses context of earlier sections
- Hal lucinates patterns from incomplete recall
- You read 900-line file → overwhelming, skipped

**With chunking:**
- Claude reads 150-line file → uses ~600 tokens
- Focused context, accurate recall
- No hallucination (complete section in memory)
- You read 150 lines → manageable, actually used

---

## Workflow Overview

```
Planning → Research → Implementation → Review
   ↓          ↓            ↓             ↓
  ADR     Read chunks   Apply patterns  Validate
```

---

## Phase 1: Planning (Before Writing Code)

### Step 1: Identify Feature Requirements

**User/Claude:** Determine what needs to be built
- "Add streaming chat interface"
- "Implement artifacts sidebar"
- "Add tool call visualization"

### Step 2: Find Relevant Documentation

**Use INDEX.md decision trees:**

**Example:**
```
Feature: Streaming chat interface
  ↓
INDEX.md says: "Need streaming chat interface?"
  → Read vercel-ai-sdk-overview.md
  → Read usechat-hook.md
  → Read streaming-ui-patterns.md
```

**Claude command:**
```
"I need to implement [feature]. Check INDEX.md and tell me which chunks to read."
```

### Step 3: Read Identified Chunks

**DO:**
- Read all 3-4 relevant chunks (450-600 lines total)
- Take notes on key patterns
- Identify code templates

**DON'T:**
- Try to read all 16 chunks
- Read original 3,700-line files

**Why it works:** 450 lines is manageable, gives complete context for the feature.

### Step 4: Document Architectural Decisions

**Create ADR before implementing:**

```
research/architecture-decisions/ADR-004-claude-agents-integration.md

## Context
We need streaming conversation with tool use.

## Research Support (WITH CITATIONS)
- Tool use patterns: tool-use-api.md
- Streaming implementation: streaming-api.md
- useChat hook: usechat-hook.md

## Decision
Use Vercel AI SDK's useChat hook for conversation management.

## Rationale
[... from research ...]
```

**Key:** Link to specific chunks, not vague "research shows..."

---

## Phase 2: Implementation (While Writing Code)

### Step 1: Keep Chunks Open

**Before starting:**
```
# In your editor/browser, open:
- Index.md (navigation)
- Relevant chunks (2-3 files)
- CLAUDE-QUICK-REFERENCE.md (code templates)
```

### Step 2: Reference Chunks During Development

**Pattern: Look → Implement → Verify**

**Example workflow:**
```
Task: Implement tool visualization

1. Open tool-visualization.md
2. Find "Tool Call Indicators" section
3. Copy code template
4. Adapt to Apex context
5. Verify against chunk's best practices
```

### Step 3: Use CLAUDE-QUICK-REFERENCE for Speed

**When you need:**
- Quick code template → CLAUDE-QUICK-REFERENCE.md
- Deep understanding → Specific chunk file

**Example:**
```
Need: Tool definition template
  ↓
CLAUDE-QUICK-REFERENCE.md → "Tool Definition Pattern" section
  → Copy template, fill in Apex-specific details
```

### Step 4: Ask Claude to Reference Chunks

**Bad prompt:**
```
"Implement streaming chat"
```

**Good prompt:**
```
"Implement streaming chat. First, read usechat-hook.md
and streaming-ui-patterns.md, then apply those patterns to Apex."
```

**Why it works:** Forces Claude to read current research, not hallucinate.

---

## Phase 3: Review (After Writing Code)

### Step 1: Self-Review Against Chunks

**Checklist approach:**
```
✓ Read artifacts-layout.md
  ✓ Side-by-side layout (60/40)? → Yes
  ✓ Responsive behavior? → Yes
  ✓ Keyboard shortcuts? → Missing!
  → Go back, add Escape key handler
```

### Step 2: Validate Implementation

**Ask Claude:**
```
"Review my ArtifactsSidebar component against artifacts-layout.md
and sheet-component.md. Are there any missing best practices?"
```

**Claude will:**
1. Read both chunks (~300 lines)
2. Compare against your code
3. Identify gaps (accessibility, error handling, etc.)

### Step 3: Document Deviations

**If you deviate from research:**
```
// src/components/ArtifactsSidebar.tsx

/**
 * RESEARCH NOTE: artifacts-layout.md recommends 60/40 split,
 * but we use 70/30 for Apex because [reason].
 *
 * See: artifacts-layout.md, line 45-50
 */
```

**Why:** Future you (or other devs) understand the decision.

---

## Common Workflows

### Workflow A: New Component from Scratch

```
1. Check INDEX.md for relevant chunks
   Example: "Implementing artifacts sidebar"
   → artifacts-layout.md, sheet-component.md

2. Read chunks (300 lines total)
   Take notes on key patterns

3. Create ADR documenting approach
   Link to specific chunks

4. Copy code template from CLAUDE-QUICK-REFERENCE.md
   Or from chunk directly

5. Implement component
   Reference chunk during dev

6. Self-review against chunk checklist
   Ensure no missing best practices

7. Ask Claude to validate
   "Compare my code against [chunk]"
```

**Estimated time:** 2-3 hours (vs. 5-6 hours without research)

### Workflow B: Debugging Existing Code

```
1. Identify problem area
   Example: "Streaming responses not rendering"

2. Find debugging chunk
   INDEX.md → "Problem with streaming?"
   → streaming-ui-patterns.md

3. Read relevant section (50-100 lines)
   Example: "Progressive Text Rendering"

4. Compare code against pattern
   Find discrepancy

5. Apply fix from chunk
   Test

6. Document fix
   Reference chunk in code comment
```

**Estimated time:** 30-60 minutes (vs. 2-3 hours trial/error)

### Workflow C: Adding New Feature

```
1. User requests: "Add command palette"

2. Check if research exists
   INDEX.md → component-catalog.md mentions Command

3. Read relevant chunk section (20-30 lines)
   component-catalog.md: "Command" section

4. If sufficient: implement directly
   If insufficient: research + document + implement

5. Reference chunk in PR description
   "Implemented Command palette per component-catalog.md"
```

**Estimated time:** 1-2 hours (vs. 3-4 hours researching from scratch)

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Skipping Research

**Problem:**
```
User: "Add streaming chat"
Dev: [Implements without reading chunks]
Result: Missing best practices, reinvents wheel, bugs
```

**Solution:**
```
User: "Add streaming chat"
Dev: "Let me read usechat-hook.md first" → [Reads 150 lines] → Implements correctly
```

### ❌ Anti-Pattern 2: Reading Everything

**Problem:**
```
Dev: [Reads all 16 chunks before starting]
Result: Overwhelmed, forgets 80%, doesn't start
```

**Solution:**
```
Dev: Uses INDEX.md to identify 2-3 relevant chunks → Reads 300 lines → Starts immediately
```

### ❌ Anti-Pattern 3: Not Referencing Chunks

**Problem:**
```
Claude: "I'll implement streaming chat" [Hallucinates patterns]
Result: Code doesn't match research, bugs
```

**Solution:**
```
You: "Read usechat-hook.md, then implement streaming chat using those exact patterns"
Claude: [Reads 150 lines] → [Implements correctly]
```

### ❌ Anti-Pattern 4: Forgetting to Document

**Problem:**
```
Dev implements feature, doesn't link to research
3 months later: Why did we do it this way?
```

**Solution:**
```
Dev implements feature, adds comment:
// Implemented per streaming-ui-patterns.md (progressive rendering)
```

---

## Integration with CLAUDE.md

**Add this to your CLAUDE.md project instructions:**

```markdown
## Research-First Development

Before implementing ANY UI feature:

1. Check `research/documentation/INDEX.md`
2. Read 2-3 relevant chunks (~300 lines)
3. Create ADR if architectural decision
4. Implement using patterns from chunks
5. Reference chunks in code comments
```

**This ensures every Claude session follows the workflow.**

---

## Measuring Success

**Good signs you're using chunks effectively:**

✅ Code comments reference specific chunks
✅ PRs mention which chunks were followed
✅ ADRs cite chunk files
✅ Implementation time decreases (research reuse)
✅ Fewer bugs from missing best practices
✅ Consistent patterns across codebase

**Bad signs you're not using chunks:**

❌ No chunk references in code/PRs
❌ Reimplementing patterns from scratch
❌ Claude hallucinating instead of reading chunks
❌ You saying "I forgot we had research on that"
❌ Inconsistent implementations

---

## Tips for Claude

**When working with me (Claude), use these prompts:**

### Prompt Template 1: Implementation

```
"Implement [feature]. First, check INDEX.md to find relevant
documentation chunks, read them, then implement using those
patterns. Reference the chunks in your code comments."
```

### Prompt Template 2: Review

```
"Review this [component] implementation against [chunk-name.md].
List any missing best practices or deviations from the documented pattern."
```

### Prompt Template 3: Debugging

```
"I'm having trouble with [problem]. Check INDEX.md for relevant
debugging guidance, read those chunks, and suggest fixes based
on the documented patterns."
```

### Prompt Template 4: Research Check

```
"Before we implement [feature], search INDEX.md to see if we
already have research on this. If yes, summarize key findings.
If no, should we research first?"
```

---

## Example: Full Feature Implementation

**Feature:** Implement artifacts sidebar

**Step-by-step workflow:**

### 1. Planning (5 minutes)

```
You: "We need artifacts sidebar. Check INDEX.md for guidance."
Claude: [Reads INDEX.md] "I found 4 relevant chunks:
  - artifacts-layout.md (layout patterns)
  - sheet-component.md (Shadcn/ui implementation)
  - artifact-types.md (rendering patterns)
  - apex-artifacts-integration.md (Apex-specific)
Should I read these?"
You: "Yes, read artifacts-layout.md and sheet-component.md first."
```

### 2. Research (10 minutes)

```
Claude: [Reads 290 lines total]
"Key findings:
- Use Shadcn/ui Sheet component
- 60/40 split (conversation/artifacts)
- Responsive: desktop side-by-side, mobile full-screen
- Accessibility: Escape key closes, focus management
- Animation: slide-in from right with spring transition"
```

### 3. ADR (10 minutes)

```
You: "Create ADR-005 documenting this decision."
Claude: [Creates ADR-005-artifacts-sidebar-pattern.md]
"Done. ADR cites artifacts-layout.md and sheet-component.md."
```

### 4. Implementation (60 minutes)

```
You: "Implement ArtifactsSidebar.tsx following those patterns."
Claude: [Implements using code templates from chunks]
[Adds comments referencing chunks]
```

### 5. Review (15 minutes)

```
You: "Review your implementation against the two chunks."
Claude: [Re-reads chunks, compares code]
"Found 2 gaps:
1. Missing Escape key handler (sheet-component.md line 120)
2. Missing screen reader announcement (sheet-component.md line 175)
Should I fix?"
You: "Yes."
Claude: [Adds both features]
```

**Total time:** ~100 minutes with research-backed, high-quality result
**vs.** ~240 minutes without research (trial/error, bugs, rework)

---

## Maintenance

**Updating chunks:**

```
When research changes:
1. Update specific chunk (not original 3,700-line file)
2. Update cross-references if needed
3. Update INDEX.md decision trees if new patterns
4. Notify team in Slack/PR
```

**Adding new chunks:**

```
When new research is added:
1. Create focused chunk file (~150 lines)
2. Add to INDEX.md with decision tree
3. Add cross-references to related chunks
4. Update CLAUDE-QUICK-REFERENCE.md if code template
```

---

## Summary: The Workflow in One Image

```
┌─────────────────────────────────────────────────────────┐
│  Feature Request: "Add artifacts sidebar"               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Check INDEX.md: Which chunks are relevant?             │
│  → artifacts-layout.md, sheet-component.md              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Read 2-3 chunks (~300 lines total)                     │
│  Take notes on key patterns                             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Create ADR documenting approach                        │
│  Cite specific chunks                                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Implement using chunk patterns                         │
│  Reference chunks in code comments                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Review implementation against chunks                   │
│  Fill any gaps from best practices                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  ✅ High-quality, research-backed implementation        │
│  ✅ In 1/2 the time (vs. no research)                   │
│  ✅ Documented decisions for future reference           │
└─────────────────────────────────────────────────────────┘
```

---

## Get Started

**Right now, you can:**

1. **Bookmark INDEX.md** - Your primary navigation hub
2. **Read this WORKFLOW-GUIDE.md** - You're doing it!
3. **Try the workflow** - Pick a small feature, follow the steps above
4. **Measure results** - Did it save time? Was code quality better?
5. **Iterate** - Adjust the workflow to fit your style

**Remember:** The goal isn't perfect workflow adherence - it's **making sure research actually gets used** instead of being forgotten.

---

**Last Updated:** 2025-10-21
**Success Metric:** Research used in 80%+ of implementations (vs. 20% without workflow)
