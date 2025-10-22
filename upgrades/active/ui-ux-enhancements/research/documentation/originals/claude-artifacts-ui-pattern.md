# Claude Artifacts UI Pattern - Research and Implementation Guide

**Primary Sources:**
- GitHub: [claude-artifact-runner](https://github.com/claudio-silva/claude-artifact-runner) (Most comprehensive)
- GitHub: [claude-artifact-viewer-template](https://github.com/sbusso/claude-artifact-viewer-template)
- GitHub: [claude-artifacts-starter](https://github.com/endlessreform/claude-artifacts-starter)
- Simon Willison's Blog: [Claude Artifact Runner Review](https://simonwillison.net/2024/Oct/23/claude-artifact-runner/)

**Date Accessed:** 2025-10-21
**Documentation Tier:** Tier 2 (Verified GitHub Examples - 1.5k+ combined stars)

---

## Executive Summary

**What are Claude Artifacts?**
Claude's Artifacts feature allows AI-generated content (code, diagrams, documents) to appear in a **side-by-side popover sidebar** for immediate preview, refinement, and export.

**Key Pattern:** **Generate → Preview → Refine** workflow where users can iteratively improve AI-generated content without leaving the conversation.

**For Apex Memory System:**
We can adapt this pattern for:
- **Generated Cypher queries** (preview + execute)
- **Code snippets** (syntax highlighting + copy)
- **Data visualizations** (charts from query results)
- **Exported documents** (PDF/Markdown reports)

---

## Part 1: UI Pattern Analysis

### What Makes Artifacts Special

**Traditional AI Chat:**
```
User: "Create a bar chart showing document counts by type"
Claude: [Returns code as text in conversation]
User: [Copies code, creates new file, runs it manually]
```

**Artifacts Pattern:**
```
User: "Create a bar chart showing document counts by type"
Claude: [Returns code AND renders it in sidebar]
User: [Sees live chart immediately, can refine in conversation]
Claude: [Updates same artifact with new version]
```

### Three Key Components

#### 1. Conversation Area (Left)
- Standard chat interface
- User messages + Claude responses
- **Special:** Artifact references show as cards/chips in conversation
- Example: "I've created a visualization for you →" [Artifact Card]

#### 2. Artifacts Sidebar (Right)
- **Slides in from right** when artifact is generated
- **Renders content live** (React components, HTML, code)
- **Full-screen capable** (expand to see more detail)
- **Export options** (download, copy code, share)
- **Version history** (see previous iterations)

#### 3. Artifact Metadata
- **Title** - Auto-generated or user-specified
- **Type** - Code, diagram, document, data visualization
- **Language/Framework** - React, HTML, SVG, Mermaid
- **Created/Updated** timestamps

---

## Part 2: Technical Stack Analysis

### Common Dependencies Across Implementations

All three major implementations use the **exact same stack**:

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.x",
    "@radix-ui/react-*": "^1.x",
    "tailwindcss": "^3.4.17",
    "framer-motion": "^12.x",
    "lucide-react": "latest",
    "recharts": "^2.x"        // For data visualizations
  },
  "devDependencies": {
    "vite": "^6.x",
    "typescript": "^5.7.x",
    "@types/react": "^18.x"
  }
}
```

**Why This Stack?**
- **React + TypeScript** - Type-safe component rendering
- **Radix UI** - Accessible primitives (Dialog, Popover, Tabs)
- **Tailwind CSS** - Rapid styling (matches Claude's design system)
- **Framer Motion** - Smooth sidebar animations
- **Recharts** - Chart/graph rendering (supports same charts as Claude)
- **Vite** - Fast development server + HMR

**⭐ Perfect Match:** This is the **exact stack already in use** in Apex Memory System UI!

---

## Part 3: Implementation Patterns

### Pattern A: Side-by-Side Layout (Most Common)

```
┌────────────────────┬─────────────────────┐
│  Conversation      │  Artifacts Sidebar  │
│  (60% width)       │  (40% width)        │
│                    │                     │
│  User: Create...   │  ┌───────────────┐ │
│                    │  │  Artifact     │ │
│  Claude: I've...   │  │  Preview      │ │
│                    │  │  [Live Render]│ │
│                    │  │               │ │
│                    │  └───────────────┘ │
│                    │  [Export] [Edit]  │
└────────────────────┴─────────────────────┘
```

**Implementation:**
```tsx
<div className="flex h-screen">
  <main className="flex-1 min-w-0">
    <ConversationArea />
  </main>

  <AnimatePresence>
    {showArtifact && (
      <motion.aside
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        className="w-2/5 border-l border-white/10 overflow-y-auto"
      >
        <ArtifactViewer artifact={currentArtifact} />
      </motion.aside>
    )}
  </AnimatePresence>
</div>
```

### Pattern B: Popover/Dialog (Alternative)

```
┌────────────────────────────────────────┐
│  Conversation (Full Width)             │
│                                        │
│  User: Create chart                    │
│                                        │
│  Claude: Here you go ┌────────────┐   │
│                       │ Artifact   │   │
│                       │ Popover    │   │
│                       │ [Preview]  │   │
│                       └────────────┘   │
└────────────────────────────────────────┘
```

**Implementation:**
```tsx
import { Dialog, DialogContent } from '@radix-ui/react-dialog';

<Dialog open={showArtifact} onOpenChange={setShowArtifact}>
  <DialogContent className="max-w-4xl w-full h-[80vh]">
    <ArtifactViewer artifact={currentArtifact} />
  </DialogContent>
</Dialog>
```

### Pattern C: Tabbed View (claude-artifact-viewer)

```
┌────────────────────────────────────────┐
│  Navigation: [Home] [Art 1] [Art 2]    │
├────────────────────────────────────────┤
│                                        │
│  Artifact Content                      │
│  (Full Screen)                         │
│                                        │
└────────────────────────────────────────┘
```

**Use Case:** Gallery of generated artifacts, not conversation-based.

---

## Part 4: Artifact Types & Rendering

### Type 1: Code Snippets

**Supported Languages:**
- JavaScript/TypeScript
- Python
- Cypher (for Apex!)
- SQL
- HTML/CSS
- Markdown

**Rendering:**
```tsx
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

function CodeArtifact({ code, language }) {
  return (
    <div className="relative">
      <SyntaxHighlighter language={language} style={oneDark}>
        {code}
      </SyntaxHighlighter>
      <button
        onClick={() => navigator.clipboard.writeText(code)}
        className="absolute top-2 right-2 p-2 bg-white/10 rounded"
      >
        Copy
      </button>
    </div>
  );
}
```

### Type 2: React Components (Interactive)

**What Claude Generates:**
```tsx
// Claude creates full React component
export default function DataVisualization() {
  const data = [
    { name: 'PDF', count: 45 },
    { name: 'DOCX', count: 32 },
    { name: 'PPTX', count: 18 }
  ];

  return (
    <BarChart width={600} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Bar dataKey="count" fill="#8884d8" />
    </BarChart>
  );
}
```

**How to Render:**
```tsx
import { lazy, Suspense } from 'react';

// Dynamic import of artifact component
const ArtifactComponent = lazy(() => import(`./artifacts/${artifactId}.tsx`));

function ArtifactViewer({ artifactId }) {
  return (
    <Suspense fallback={<div>Loading artifact...</div>}>
      <ArtifactComponent />
    </Suspense>
  );
}
```

### Type 3: Data Visualizations (Recharts)

**Supported Chart Types:**
- BarChart
- LineChart
- PieChart
- ScatterChart
- AreaChart
- RadarChart
- TreeMap
- Sankey Diagram

**Example:**
```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function ApexDocumentStats({ data }) {
  return (
    <BarChart width={600} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="#fff2" />
      <XAxis dataKey="type" stroke="#fff" />
      <YAxis stroke="#fff" />
      <Tooltip
        contentStyle={{
          backgroundColor: '#000',
          border: '1px solid #fff3'
        }}
      />
      <Bar dataKey="count" fill="#a855f7" />
    </BarChart>
  );
}
```

### Type 4: Diagrams (Mermaid)

**Not Implemented Yet** (but planned in Claude):
- Flowcharts
- Sequence diagrams
- Entity-relationship diagrams
- Gantt charts

**Potential Integration:**
```tsx
import { Mermaid } from 'mdx-mermaid/Mermaid';

function DiagramArtifact({ mermaidCode }) {
  return <Mermaid chart={mermaidCode} />;
}
```

---

## Part 5: Artifact Lifecycle

### 1. Creation Flow

```
User Query
  ↓
Claude Detects Artifact-Worthy Content
  ↓
Claude Calls create_artifact Tool
  {
    type: "code" | "react" | "html" | "svg",
    language: "typescript" | "python" | "cypher",
    title: "Document Count Bar Chart",
    content: "<full code here>"
  }
  ↓
Backend Saves Artifact (DB or filesystem)
  ↓
Frontend Receives artifact_created Event
  ↓
Sidebar Slides In + Renders Artifact
```

### 2. Update Flow (Iterative Refinement)

```
User: "Make the bars purple instead of blue"
  ↓
Claude Calls update_artifact Tool
  {
    artifact_id: "abc123",
    changes: "Updated bar color to purple (#a855f7)"
  }
  ↓
Backend Updates Artifact (preserves version history)
  ↓
Frontend Receives artifact_updated Event
  ↓
Sidebar Re-renders with New Version
```

### 3. Export Flow

```
User Clicks "Export"
  ↓
Frontend Offers Options:
  - Copy Code
  - Download as File (.tsx, .html, .py)
  - Share Link (if hosted)
  - Export as PDF (for documents)
  ↓
User Selects Option
  ↓
Action Executed (clipboard, download, etc.)
```

---

## Part 6: State Management

### Artifact Store (Zustand Example)

```typescript
import create from 'zustand';

interface Artifact {
  id: string;
  type: 'code' | 'react' | 'chart' | 'document';
  language?: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  version: number;
}

interface ArtifactStore {
  artifacts: Artifact[];
  currentArtifact: Artifact | null;
  showSidebar: boolean;

  addArtifact: (artifact: Artifact) => void;
  updateArtifact: (id: string, updates: Partial<Artifact>) => void;
  setCurrentArtifact: (id: string) => void;
  toggleSidebar: () => void;
}

export const useArtifactStore = create<ArtifactStore>((set) => ({
  artifacts: [],
  currentArtifact: null,
  showSidebar: false,

  addArtifact: (artifact) => set((state) => ({
    artifacts: [...state.artifacts, artifact],
    currentArtifact: artifact,
    showSidebar: true
  })),

  updateArtifact: (id, updates) => set((state) => ({
    artifacts: state.artifacts.map((art) =>
      art.id === id ? { ...art, ...updates, version: art.version + 1 } : art
    ),
    currentArtifact: state.currentArtifact?.id === id
      ? { ...state.currentArtifact, ...updates }
      : state.currentArtifact
  })),

  setCurrentArtifact: (id) => set((state) => ({
    currentArtifact: state.artifacts.find((art) => art.id === id) || null,
    showSidebar: true
  })),

  toggleSidebar: () => set((state) => ({ showSidebar: !state.showSidebar }))
}));
```

---

## Part 7: Responsive Behavior

### Desktop (≥1024px)

```css
/* Side-by-side layout */
.conversation-area {
  width: 60%;
}

.artifacts-sidebar {
  width: 40%;
  position: fixed;
  right: 0;
  height: 100vh;
}
```

### Tablet (768px - 1023px)

```css
/* Popover/overlay mode */
.artifacts-sidebar {
  width: 80%;
  position: fixed;
  right: 0;
  top: 0;
  height: 100vh;
  z-index: 50;
  box-shadow: -8px 0 24px rgba(0, 0, 0, 0.5);
}
```

### Mobile (<768px)

```css
/* Full-screen modal */
.artifacts-sidebar {
  width: 100%;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100;
}
```

**Implementation:**
```tsx
const isMobile = useMediaQuery('(max-width: 768px)');
const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1023px)');
const isDesktop = useMediaQuery('(min-width: 1024px)');

if (isMobile) {
  return <FullScreenArtifactModal />;
} else if (isTablet) {
  return <OverlayArtifactSidebar />;
} else {
  return <SideBySideLayout />;
}
```

---

## Part 8: Animation Patterns

### Slide-In Animation (Recommended)

```tsx
import { motion, AnimatePresence } from 'framer-motion';

function ArtifactSidebar({ show, artifact }) {
  return (
    <AnimatePresence>
      {show && (
        <motion.aside
          initial={{ x: '100%', opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: '100%', opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed right-0 top-0 h-screen w-2/5 bg-black border-l border-white/10"
        >
          {artifact && <ArtifactRenderer artifact={artifact} />}
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
```

### Content Transition

```tsx
<motion.div
  key={artifact.id}  // Re-animate on artifact change
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3 }}
>
  <ArtifactContent content={artifact.content} />
</motion.div>
```

---

## Part 9: Integration with Apex Memory System

### Use Case 1: Cypher Query Artifacts

```
User: "Show me all CAT equipment connected to maintenance issues"
  ↓
Claude: Creates Cypher query artifact
  ↓
Sidebar Shows:
  - Syntax-highlighted Cypher query
  - [Run Query] button
  - Query explanation
  ↓
User Clicks "Run Query"
  ↓
Results appear below query in sidebar
  ↓
User: "Add a filter for last 30 days"
  ↓
Claude: Updates query artifact with date filter
  ↓
Sidebar re-renders with updated query
```

**Artifact Structure:**
```typescript
{
  type: "code",
  language: "cypher",
  title: "CAT Equipment Maintenance Query",
  content: `
    MATCH (equipment:Entity {type: 'Equipment'})-[:MANUFACTURER]->(cat:Entity {name: 'CAT'})
    MATCH (equipment)-[:HAS_ISSUE]->(issue:Entity {type: 'Maintenance'})
    WHERE issue.date > datetime() - duration('P30D')
    RETURN equipment.name, issue.description, issue.date
    ORDER BY issue.date DESC
  `,
  metadata: {
    executable: true,
    database: "neo4j"
  }
}
```

### Use Case 2: Data Visualization Artifacts

```
User: "Create a chart showing document ingestion trends"
  ↓
Claude: Queries Apex API for document stats
  ↓
Claude: Creates React chart component artifact
  ↓
Sidebar Shows:
  - Live chart rendering (Recharts)
  - Interactive tooltips
  - [Export as PNG] [Copy Code] buttons
```

**Artifact Structure:**
```typescript
{
  type: "react",
  language: "typescript",
  title: "Document Ingestion Trends",
  content: `
    import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

    export default function IngestionChart() {
      const data = [
        { date: '2025-01', count: 120 },
        { date: '2025-02', count: 185 },
        { date: '2025-03', count: 203 }
      ];

      return (
        <LineChart width={600} height={400} data={data}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="count" stroke="#a855f7" />
        </LineChart>
      );
    }
  `,
  metadata: {
    requires_data: true,
    data_source: "/api/v1/stats/ingestion"
  }
}
```

### Use Case 3: Report Generation Artifacts

```
User: "Generate a summary report of last month's activities"
  ↓
Claude: Analyzes documents, creates formatted report
  ↓
Sidebar Shows:
  - Markdown-rendered report
  - [Export as PDF] [Export as Markdown] buttons
  - Table of contents navigation
```

**Artifact Structure:**
```typescript
{
  type: "document",
  language: "markdown",
  title: "October 2025 Activity Report",
  content: `
    # October 2025 Activity Summary

    ## Document Ingestion
    - Total documents: 203
    - PDF: 120 (59%)
    - DOCX: 58 (29%)
    - PPTX: 25 (12%)

    ## Top Entities
    1. CAT Equipment (45 mentions)
    2. Maintenance Procedures (38 mentions)
    3. Safety Protocols (29 mentions)

    ## Knowledge Graph Growth
    - New entities: 127
    - New relationships: 384
    - Graph density: 2.87 connections per entity
  `,
  metadata: {
    exportable: true,
    formats: ["pdf", "markdown", "html"]
  }
}
```

---

## Part 10: Security Considerations

### Code Execution Safety

⚠️ **DO NOT execute arbitrary code from artifacts directly!**

**Safe Approaches:**

1. **Sandboxed Rendering** (React components)
```tsx
// Safe: React components render in controlled environment
<Suspense fallback={<Loading />}>
  <SafeArtifactComponent />
</Suspense>
```

2. **Read-Only Code Display**
```tsx
// Safe: Syntax highlighting only, no execution
<SyntaxHighlighter language="python">
  {artifact.content}
</SyntaxHighlighter>
```

3. **User Confirmation for Queries**
```tsx
// Safe: User must click "Run" to execute Cypher query
<CypherQuery query={artifact.content} requiresConfirmation={true} />
```

### Content Sanitization

```typescript
import DOMPurify from 'isomorphic-dompurify';

function sanitizeArtifactContent(content: string, type: string) {
  switch (type) {
    case 'html':
      return DOMPurify.sanitize(content);

    case 'markdown':
      return DOMPurify.sanitize(marked(content));

    case 'code':
      // No sanitization needed for display-only
      return content;

    default:
      return content;
  }
}
```

---

## Part 11: Performance Optimization

### Lazy Loading Artifacts

```typescript
// Don't load artifact content until sidebar opens
const { data: artifact, isLoading } = useQuery(
  ['artifact', artifactId],
  () => fetchArtifact(artifactId),
  { enabled: showSidebar }  // Only fetch when sidebar is visible
);
```

### Virtual Scrolling for Long Content

```tsx
import { Virtuoso } from 'react-virtuoso';

function LargeCodeArtifact({ lines }) {
  return (
    <Virtuoso
      style={{ height: '100%' }}
      totalCount={lines.length}
      itemContent={(index) => (
        <div className="font-mono text-sm">{lines[index]}</div>
      )}
    />
  );
}
```

### Debounced Updates

```typescript
// Don't re-render on every keystroke during live editing
const debouncedUpdate = useMemo(
  () => debounce((content) => updateArtifact(content), 500),
  []
);
```

---

## Part 12: Accessibility

### Keyboard Navigation

```tsx
function ArtifactSidebar() {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        closeSidebar();
      }
      if (e.metaKey && e.key === 'k') {
        e.preventDefault();
        toggleSidebar();
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <aside
      role="complementary"
      aria-label="Artifact viewer"
      tabIndex={-1}
    >
      {/* Artifact content */}
    </aside>
  );
}
```

### Screen Reader Announcements

```tsx
import { useAnnouncer } from '@react-aria/live-announcer';

function ArtifactCreated({ title }) {
  const announce = useAnnouncer();

  useEffect(() => {
    announce(`New artifact created: ${title}`);
  }, [title]);

  return null;
}
```

### Focus Management

```tsx
const sidebarRef = useRef<HTMLElement>(null);

useEffect(() => {
  if (showSidebar) {
    // Focus sidebar when it opens
    sidebarRef.current?.focus();
  }
}, [showSidebar]);
```

---

## References

**GitHub Repositories (Tier 2 - Verified Examples):**
- [claude-artifact-runner](https://github.com/claudio-silva/claude-artifact-runner) - Most comprehensive implementation
- [claude-artifact-viewer-template](https://github.com/sbusso/claude-artifact-viewer-template) - Template with automatic navigation
- [claude-artifacts-starter](https://github.com/endlessreform/claude-artifacts-starter) - Minimal Vite + TS + Tailwind template

**Blog Posts & Analysis:**
- [Simon Willison: Claude Artifact Runner](https://simonwillison.net/2024/Oct/23/claude-artifact-runner/) - Detailed review and analysis

**Design Patterns:**
- Radix UI Documentation: https://www.radix-ui.com/
- Framer Motion Documentation: https://www.framer.com/motion/
- Recharts Documentation: https://recharts.org/

**Additional Resources:**
- React Suspense: https://react.dev/reference/react/Suspense
- Tailwind CSS: https://tailwindcss.com/docs
- TypeScript Handbook: https://www.typescriptlang.org/docs/

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 2 (Verified GitHub Examples - 1.5k+ combined stars)
