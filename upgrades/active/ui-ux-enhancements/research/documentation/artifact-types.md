# Artifact Types and Rendering - Content Implementation Guide

**Purpose:** Rendering patterns for different artifact content types
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 2 (Verified GitHub Examples)

**Related Documentation:**
- For layout patterns → see `artifacts-layout.md`
- For Sheet component → see `sheet-component.md`
- For Apex integration → see `apex-artifacts-integration.md`

---

## Overview

Claude can generate four primary artifact types, each requiring different rendering strategies:

1. **Code Snippets** - Syntax-highlighted, copyable code
2. **React Components** - Interactive, executable components
3. **Data Visualizations** - Charts and graphs (Recharts)
4. **Documents** - Markdown or HTML formatted text

---

## Type 1: Code Snippets

### Supported Languages

- JavaScript/TypeScript
- Python
- **Cypher** (for Apex Neo4j queries!)
- SQL
- HTML/CSS
- Markdown
- JSON

### Rendering Implementation

```tsx
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';

interface CodeArtifactProps {
  code: string;
  language: string;
  title: string;
}

function CodeArtifact({ code, language, title }: CodeArtifactProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative rounded-lg overflow-hidden border border-white/10">
      <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/10">
        <span className="text-sm text-white/70">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-3 py-1 text-sm bg-white/10 rounded hover:bg-white/20 transition-colors"
        >
          {copied ? (
            <>
              <CheckIcon className="w-4 h-4" />
              Copied!
            </>
          ) : (
            <>
              <CopyIcon className="w-4 h-4" />
              Copy
            </>
          )}
        </button>
      </div>

      <SyntaxHighlighter
        language={language}
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: '1rem',
          background: 'transparent'
        }}
        showLineNumbers
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}
```

---

## Type 2: React Components (Interactive)

### What Claude Generates

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

### How to Render Dynamically

```tsx
import { lazy, Suspense } from 'react';

interface ReactArtifactProps {
  artifactId: string;
  content: string;
}

function ReactArtifact({ artifactId, content }: ReactArtifactProps) {
  // Option 1: Dynamic import (if saved as file)
  const ArtifactComponent = lazy(() => import(`./artifacts/${artifactId}.tsx`));

  return (
    <Suspense fallback={<ArtifactLoadingSkeleton />}>
      <ArtifactComponent />
    </Suspense>
  );
}

// Option 2: Runtime compilation (advanced)
function ReactArtifactRuntime({ content }: { content: string }) {
  const [Component, setComponent] = useState<React.ComponentType | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      // Use Sucrase or Babel to transpile TypeScript → JavaScript
      const transpiled = transpile(content);
      const compiled = new Function('React', 'return ' + transpiled)(React);
      setComponent(() => compiled);
    } catch (err) {
      setError(err.message);
    }
  }, [content]);

  if (error) return <ErrorDisplay error={error} />;
  if (!Component) return <ArtifactLoadingSkeleton />;

  return <Component />;
}
```

---

## Type 3: Data Visualizations (Recharts)

### Supported Chart Types

- BarChart
- LineChart
- PieChart
- ScatterChart
- AreaChart
- RadarChart
- TreeMap
- Sankey Diagram

### Complete Implementation

```tsx
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface ChartData {
  [key: string]: string | number;
}

interface ChartArtifactProps {
  type: 'bar' | 'line' | 'pie' | 'area';
  data: ChartData[];
  xKey: string;
  yKey: string;
  title: string;
}

function ChartArtifact({ type, data, xKey, yKey, title }: ChartArtifactProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">{title}</h3>

      <ResponsiveContainer width="100%" height={400}>
        {type === 'bar' && (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#fff2" />
            <XAxis dataKey={xKey} stroke="#fff" />
            <YAxis stroke="#fff" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#000',
                border: '1px solid #fff3',
                borderRadius: '8px'
              }}
            />
            <Bar dataKey={yKey} fill="#a855f7" />
          </BarChart>
        )}

        {type === 'line' && (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#fff2" />
            <XAxis dataKey={xKey} stroke="#fff" />
            <YAxis stroke="#fff" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#000',
                border: '1px solid #fff3',
                borderRadius: '8px'
              }}
            />
            <Line type="monotone" dataKey={yKey} stroke="#a855f7" strokeWidth={2} />
          </LineChart>
        )}
      </ResponsiveContainer>

      {/* Export options */}
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => exportChartAsImage()}
        >
          Export as PNG
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => exportChartData(data)}
        >
          Export Data (CSV)
        </Button>
      </div>
    </div>
  );
}
```

---

## Type 4: Documents (Markdown/HTML)

### Markdown Rendering

```tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

interface DocumentArtifactProps {
  content: string;
  title: string;
}

function DocumentArtifact({ content, title }: DocumentArtifactProps) {
  return (
    <div className="prose prose-invert max-w-none">
      <h1>{title}</h1>

      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                language={match[1]}
                PreTag="div"
                {...props}
              >
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

      {/* Export options */}
      <div className="mt-6 flex gap-2">
        <Button onClick={() => exportAsPDF(content, title)}>
          Export as PDF
        </Button>
        <Button variant="outline" onClick={() => downloadMarkdown(content, title)}>
          Download Markdown
        </Button>
      </div>
    </div>
  );
}
```

---

## Artifact Lifecycle

### 1. Creation Flow

```
User Query
  ↓
Claude Detects Artifact-Worthy Content
  ↓
Claude Calls create_artifact Tool
  {
    type: "code" | "react" | "chart" | "document",
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

## Artifact Renderer (Universal)

```tsx
interface Artifact {
  id: string;
  type: 'code' | 'react' | 'chart' | 'document';
  language?: string;
  title: string;
  content: string;
  metadata?: Record<string, any>;
}

function ArtifactRenderer({ artifact }: { artifact: Artifact }) {
  switch (artifact.type) {
    case 'code':
      return (
        <CodeArtifact
          code={artifact.content}
          language={artifact.language || 'text'}
          title={artifact.title}
        />
      );

    case 'react':
      return (
        <ReactArtifact
          artifactId={artifact.id}
          content={artifact.content}
        />
      );

    case 'chart':
      return (
        <ChartArtifact
          type={artifact.metadata?.chartType || 'bar'}
          data={JSON.parse(artifact.content)}
          xKey={artifact.metadata?.xKey}
          yKey={artifact.metadata?.yKey}
          title={artifact.title}
        />
      );

    case 'document':
      return (
        <DocumentArtifact
          content={artifact.content}
          title={artifact.title}
        />
      );

    default:
      return <div>Unsupported artifact type</div>;
  }
}
```

---

## Version History

### Storage Pattern

```typescript
interface ArtifactVersion {
  version: number;
  content: string;
  changes: string;
  created_at: string;
}

interface ArtifactWithHistory extends Artifact {
  versions: ArtifactVersion[];
}
```

### Version Viewer Component

```tsx
function VersionHistory({ artifact }: { artifact: ArtifactWithHistory }) {
  const [selectedVersion, setSelectedVersion] = useState(artifact.version);

  const currentVersionContent = artifact.versions.find(
    v => v.version === selectedVersion
  )?.content || artifact.content;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Version History</h4>
        <select
          value={selectedVersion}
          onChange={(e) => setSelectedVersion(Number(e.target.value))}
          className="text-sm bg-white/10 rounded px-2 py-1"
        >
          {artifact.versions.map((v) => (
            <option key={v.version} value={v.version}>
              v{v.version} - {new Date(v.created_at).toLocaleDateString()}
            </option>
          ))}
        </select>
      </div>

      <ArtifactRenderer
        artifact={{ ...artifact, content: currentVersionContent }}
      />
    </div>
  );
}
```

---

## Export Utilities

### Copy to Clipboard

```typescript
async function copyToClipboard(content: string) {
  try {
    await navigator.clipboard.writeText(content);
    toast.success('Copied to clipboard');
  } catch (err) {
    toast.error('Failed to copy');
  }
}
```

### Download as File

```typescript
function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Usage
downloadFile(artifact.content, `${artifact.title}.tsx`, 'text/typescript');
```

### Export Chart as Image

```typescript
import html2canvas from 'html2canvas';

async function exportChartAsImage(chartRef: HTMLElement) {
  const canvas = await html2canvas(chartRef);
  const dataUrl = canvas.toDataURL('image/png');

  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = 'chart.png';
  link.click();
}
```

---

## References

**Rendering Libraries:**
- react-syntax-highlighter: https://github.com/react-syntax-highlighter/react-syntax-highlighter
- Recharts: https://recharts.org/
- react-markdown: https://github.com/remarkjs/react-markdown
- html2canvas: https://html2canvas.hertzen.com/

**Related Documentation:**
- Layout patterns → `artifacts-layout.md`
- Sheet component → `sheet-component.md`
- Apex integration → `apex-artifacts-integration.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 2 (Verified Implementation Pattern)
