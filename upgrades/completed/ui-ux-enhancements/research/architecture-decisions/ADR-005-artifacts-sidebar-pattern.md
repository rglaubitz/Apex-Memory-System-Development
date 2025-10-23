# ADR-005: Artifacts Sidebar Pattern

**Status:** Accepted
**Date:** 2025-10-21
**Decision Makers:** Development Team
**Affected Components:** Frontend UI, ConversationHub, Tool Results Display

---

## Context

### Problem Statement

The Apex Memory System UI needs to display complex, structured information from tool executions and agent orchestration without cluttering the main conversation thread. Current implementation (Phase 2) embeds tool results as JSON blocks in the conversation, making it difficult to distinguish narrative from technical details.

**Requirements:**
- Display tool execution results (entities, relationships, patterns)
- Show agent reasoning steps transparently
- Keep main thread narrative-focused
- Provide easy access to technical details
- Support visual data exploration (graphs, tables)

---

## Decision

**We will implement a Claude.ai-inspired Artifacts Sidebar Pattern in Phase 3 (Week 6).**

### Design Overview

**Two-column layout:**
- **Left:** Main conversation thread (narrative responses only)
- **Right:** Artifacts sidebar (tool results, agent reasoning, visualizations)

**Sidebar features:**
- Collapsible tabs for different artifact types
- Syntax highlighting for JSON/code
- Interactive visualizations (entity graphs, time series)
- Copy-to-clipboard for technical details
- Artifact history (access previous tool results)

---

## Research Support

### Tier 1 Sources

**Claude.ai Artifacts Pattern**
- **Source:** https://www.anthropic.com/news/claude-3-5-sonnet (artifacts announcement)
- **Tier:** 1 (Official Anthropic Documentation)
- **Reference:** RESEARCH-REFERENCES.md (Phase 3 section)

**Key insights:**
- Sidebar pattern keeps conversation clean
- Users can explore technical details without disrupting chat flow
- Progressive disclosure (show summary, expand for details)

**Apple Human Interface Guidelines**
- **Source:** https://developer.apple.com/design/human-interface-guidelines/
- **Tier:** 1 (Official Apple Design Documentation)
- **Reference:** RESEARCH-REFERENCES.md (Phase 3 section)

**Relevant principles:**
- Visual hierarchy (primary vs. secondary content)
- Progressive disclosure (reveal details on demand)
- Consistent navigation patterns

### Tier 2 Sources

**Shadcn/ui Components**
- **Source:** https://ui.shadcn.com/
- **Tier:** 2 (Community Project - 40k+ stars)
- **Reference:** RESEARCH-REFERENCES.md (Phase 3 section)

**Components to use:**
- Sidebar / Sheet component
- Tabs for artifact types
- Collapsible sections
- Code blocks with syntax highlighting

---

## Alternatives Considered

### Alternative 1: Modal/Dialog for Tool Results

**Approach:** Show tool results in modal overlays

**Pros:**
- ✅ Maximizes screen space for conversation
- ✅ Focus on one artifact at a time

**Cons:**
- ❌ Breaks conversation flow (requires clicking to dismiss)
- ❌ Cannot reference chat and data simultaneously
- ❌ Poor multi-tasking (can't compare multiple tool results)

**Decision:** Rejected - Too disruptive to conversation flow

---

### Alternative 2: Inline Expandable Sections

**Approach:** Tool results embedded as expandable <details> blocks in chat

**Pros:**
- ✅ No additional UI components needed
- ✅ Results appear in conversation context

**Cons:**
- ❌ Chat thread becomes cluttered with technical details
- ❌ Poor visual hierarchy (hard to distinguish narrative from data)
- ❌ Cannot compare tool results across messages

**Decision:** Rejected - Violates narrative-first design principle

---

### Alternative 3: Bottom Sheet/Drawer

**Approach:** Sliding drawer from bottom of screen

**Pros:**
- ✅ Mobile-friendly pattern
- ✅ Familiar interaction model

**Cons:**
- ❌ Obscures conversation when open
- ❌ Poor for desktop (wasted horizontal space)
- ❌ Cannot view chat and data simultaneously

**Decision:** Rejected - Optimizing for desktop use case first

---

## Consequences

### Positive Consequences

**1. Clean Conversation Thread** ⭐ PRIMARY BENEFIT
- Narrative responses remain readable prose
- Technical details don't clutter main view
- Natural conversation flow preserved

**2. Enhanced Data Exploration**
- Interactive visualizations for entity graphs
- Syntax-highlighted JSON for technical users
- Easy copying of structured data

**3. Agent Reasoning Transparency**
- Sidebar shows agent planning steps
- Tool execution progress visible
- Users understand why agent made decisions

**4. Better Multi-Tasking**
- Reference conversation while exploring data
- Compare multiple tool results side-by-side
- Context switching without losing place

---

### Negative Consequences

**1. Screen Space Trade-off**
- Sidebar reduces conversation area width
- Less optimal for small screens (<1024px width)

**Mitigation:**
- Collapsible sidebar (toggle on/off)
- Responsive layout (sidebar moves to overlay on mobile)
- User preference persistence (remember collapsed state)

**2. Implementation Complexity**
- New component architecture needed
- State management for sidebar content
- Synchronization between chat and sidebar

**Mitigation:**
- Use proven Shadcn/ui Sidebar component
- Leverage existing React context for state
- Phase 3 dedicated week for implementation (Week 6)

**3. Learning Curve**
- Users must discover sidebar functionality
- New interaction pattern to learn

**Mitigation:**
- First-time user tooltip ("Technical details appear here")
- Automatic sidebar open on first tool execution
- Visual indicator when new artifact added

---

## Implementation Notes

### Component Architecture

```typescript
// src/components/ArtifactSidebar/ArtifactSidebar.tsx
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Artifact {
  id: string;
  type: "tool_result" | "agent_reasoning" | "visualization";
  timestamp: Date;
  data: any;
}

export const ArtifactSidebar: React.FC<{ artifacts: Artifact[] }> = ({ artifacts }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetContent side="right" className="w-[500px]">
        <Tabs defaultValue="tool_results">
          <TabsList>
            <TabsTrigger value="tool_results">Tool Results</TabsTrigger>
            <TabsTrigger value="agent_reasoning">Agent Reasoning</TabsTrigger>
            <TabsTrigger value="visualizations">Visualizations</TabsTrigger>
          </TabsList>

          <TabsContent value="tool_results">
            {artifacts
              .filter(a => a.type === "tool_result")
              .map(artifact => (
                <ArtifactCard key={artifact.id} artifact={artifact} />
              ))}
          </TabsContent>

          {/* ... other tabs */}
        </Tabs>
      </SheetContent>
    </Sheet>
  );
};
```

### Integration with ConversationHub

```typescript
// src/components/ConversationHub/ConversationHub.tsx

export const ConversationHub: React.FC = () => {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  const handleToolResult = (toolName: string, result: any) => {
    // Add tool result to artifacts
    setArtifacts([...artifacts, {
      id: crypto.randomUUID(),
      type: "tool_result",
      timestamp: new Date(),
      data: { tool_name: toolName, result }
    }]);
  };

  return (
    <div className="flex h-full">
      {/* Main conversation thread */}
      <div className="flex-1">
        <ConversationThread messages={messages} />
      </div>

      {/* Artifacts sidebar */}
      <ArtifactSidebar artifacts={artifacts} />
    </div>
  );
};
```

### Artifact Types

**1. Tool Results**
- JSON display with syntax highlighting
- Collapsible sections for large results
- Copy-to-clipboard button

**2. Agent Reasoning**
- Step-by-step agent plan
- Tool selection rationale
- Execution progress indicator

**3. Visualizations**
- Entity relationship graphs (vis.js or D3.js)
- Time series charts (Chart.js or Recharts)
- Heatmaps for connection strength

---

## Success Metrics

**Performance targets:**
- ✅ Sidebar toggle <16ms (single frame)
- ✅ Artifact rendering <100ms (smooth UI)

**User experience targets:**
- ✅ 80% users discover sidebar within first session
- ✅ 60% users actively use sidebar (click/explore artifacts)
- ✅ Reduced "what does this JSON mean?" support questions

**Quality targets:**
- ✅ 90%+ test coverage for sidebar components
- ✅ WCAG 2.1 Level AA accessibility compliance
- ✅ Responsive design (desktop, tablet, mobile)

---

## Testing Strategy

**Component tests:**
```typescript
describe('ArtifactSidebar', () => {
  test('renders tool results in correct tab', () => {
    const artifacts = [
      { id: '1', type: 'tool_result', data: { tool_name: 'search', result: {} } }
    ];

    render(<ArtifactSidebar artifacts={artifacts} />);

    expect(screen.getByText('Tool Results')).toBeInTheDocument();
    expect(screen.getByText('search')).toBeInTheDocument();
  });

  test('collapses sidebar when toggle clicked', () => {
    render(<ArtifactSidebar artifacts={[]} />);

    const toggle = screen.getByRole('button', { name: /collapse/i });
    fireEvent.click(toggle);

    expect(screen.queryByText('Tool Results')).not.toBeVisible();
  });
});
```

**Integration tests:**
```typescript
describe('ConversationHub with Sidebar', () => {
  test('adds artifact to sidebar when tool executed', async () => {
    render(<ConversationHub />);

    // Execute tool
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Search for ACME' } });
    fireEvent.submit(input);

    // Wait for tool result
    await waitFor(() => {
      expect(screen.getByText('Tool Results')).toBeInTheDocument();
      expect(screen.getByText('search_knowledge_graph')).toBeInTheDocument();
    });
  });
});
```

---

## Future Enhancements

**Post-Phase 3:**

1. **Artifact Export**
   - Export tool results as JSON/CSV
   - Save visualizations as PNG/SVG
   - Share artifacts via URL

2. **Artifact Comparison**
   - Side-by-side comparison of multiple tool results
   - Diff view for temporal changes
   - Highlight differences in entity data

3. **Custom Visualizations**
   - User-defined chart types
   - Saved visualization templates
   - Interactive filtering and drilling

4. **Artifact Search**
   - Full-text search across all artifacts
   - Filter by type, timestamp, tool name
   - Quick jump to specific artifact

---

## References

**Primary Research:**
- See `RESEARCH-REFERENCES.md` - Phase 3 section
- See `PLANNING.md` - Week 6 (Phase 3) section
- See `IMPLEMENTATION.md` - Week 6 implementation steps

**Related ADRs:**
- ADR-004: Claude Agents Integration (agent reasoning artifacts)
- ADR-006: Shadcn/ui Component Library (sidebar components)
- ADR-007: Apple Minimalist Design System (visual hierarchy)

**External Documentation:**
- Claude.ai Artifacts: https://www.anthropic.com/news/claude-3-5-sonnet
- Apple HIG: https://developer.apple.com/design/human-interface-guidelines/
- Shadcn/ui Sidebar: https://ui.shadcn.com/docs/components/sidebar

---

**Last Updated:** 2025-10-21
**Status:** Accepted for Phase 3 implementation
**Review Date:** 2025-11-21 (after 1 month of usage)
