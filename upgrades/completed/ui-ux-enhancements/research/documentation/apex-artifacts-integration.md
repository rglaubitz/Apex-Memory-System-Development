# Apex Artifacts Integration - Use Cases & Best Practices

**Purpose:** Apex Memory System specific artifact implementations
**Date Created:** 2025-10-21
**Documentation Tier:** Internal (Apex Memory System)

**Related Documentation:**
- For layout patterns → see `artifacts-layout.md`
- For rendering → see `artifact-types.md`
- For Sheet component → see `sheet-component.md`

---

## Overview

This document provides Apex-specific patterns for integrating Claude Artifacts with the Apex Memory System's multi-database architecture.

**Apex Artifact Use Cases:**
1. **Cypher Query Artifacts** - Neo4j queries with execution
2. **Data Visualization Artifacts** - Charts from Apex query results
3. **Report Generation Artifacts** - Formatted intelligence reports
4. **Code Snippet Artifacts** - API usage examples

---

## Use Case 1: Cypher Query Artifacts

### User Flow

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

### Artifact Structure

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
    database: "neo4j",
    requires_confirmation: true
  }
}
```

### Implementation

```tsx
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { SyntaxHighlighter } from '@/components/syntax-highlighter';

interface CypherArtifactProps {
  artifact: Artifact;
}

function CypherQueryArtifact({ artifact }: CypherArtifactProps) {
  const [results, setResults] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeQuery = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/graph/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cypher: artifact.content,
          parameters: artifact.metadata?.parameters || {}
        })
      });

      if (!response.ok) throw new Error('Query failed');

      const data = await response.json();
      setResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Query Display */}
      <SyntaxHighlighter language="cypher" code={artifact.content} />

      {/* Execution Controls */}
      <div className="flex gap-2">
        <Button
          onClick={executeQuery}
          disabled={loading}
          className="flex items-center gap-2"
        >
          {loading ? (
            <>
              <LoaderIcon className="w-4 h-4 animate-spin" />
              Running...
            </>
          ) : (
            <>
              <PlayIcon className="w-4 h-4" />
              Run Query
            </>
          )}
        </Button>
        <Button variant="outline" onClick={() => copyToClipboard(artifact.content)}>
          Copy Query
        </Button>
      </div>

      {/* Results Display */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {results && (
        <div className="space-y-2">
          <h4 className="text-sm font-semibold">Results ({results.length})</h4>
          <div className="max-h-96 overflow-auto">
            <QueryResultsTable data={results} />
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Use Case 2: Data Visualization Artifacts

### User Flow

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

### Artifact Structure

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
    data_source: "/api/v1/stats/ingestion",
    chart_type: "line"
  }
}
```

### Implementation with Live Data

```tsx
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

function ApexVisualizationArtifact({ artifact }: { artifact: Artifact }) {
  // Fetch live data from Apex API
  const { data, isLoading, error } = useQuery({
    queryKey: ['artifact-data', artifact.metadata?.data_source],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000${artifact.metadata?.data_source}`);
      return response.json();
    },
    enabled: artifact.metadata?.requires_data === true
  });

  if (isLoading) return <ChartSkeleton />;
  if (error) return <ErrorDisplay error={error} />;

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">{artifact.title}</h3>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <XAxis dataKey="date" stroke="#fff" />
          <YAxis stroke="#fff" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#000',
              border: '1px solid #fff3',
              borderRadius: '8px'
            }}
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#a855f7"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Export Options */}
      <div className="flex gap-2">
        <Button onClick={() => exportChartAsImage()}>
          Export as PNG
        </Button>
        <Button variant="outline" onClick={() => exportChartData(data)}>
          Export Data (CSV)
        </Button>
      </div>
    </div>
  );
}
```

---

## Use Case 3: Report Generation Artifacts

### User Flow

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

### Artifact Structure

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
    formats: ["pdf", "markdown", "html"],
    generated_at: "2025-10-21T10:30:00Z",
    data_sources: [
      "/api/v1/stats/ingestion",
      "/api/v1/graph/stats",
      "/api/v1/entities/top"
    ]
  }
}
```

### Implementation with PDF Export

```tsx
import ReactMarkdown from 'react-markdown';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

function ReportArtifact({ artifact }: { artifact: Artifact }) {
  const reportRef = useRef<HTMLDivElement>(null);

  const exportAsPDF = async () => {
    if (!reportRef.current) return;

    const canvas = await html2canvas(reportRef.current);
    const imgData = canvas.toDataURL('image/png');

    const pdf = new jsPDF();
    const imgWidth = 210; // A4 width in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
    pdf.save(`${artifact.title}.pdf`);
  };

  const exportAsMarkdown = () => {
    const blob = new Blob([artifact.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${artifact.title}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <div ref={reportRef} className="prose prose-invert max-w-none">
        <ReactMarkdown>{artifact.content}</ReactMarkdown>
      </div>

      <div className="flex gap-2">
        <Button onClick={exportAsPDF}>Export as PDF</Button>
        <Button variant="outline" onClick={exportAsMarkdown}>
          Download Markdown
        </Button>
      </div>
    </div>
  );
}
```

---

## Security Considerations

### Code Execution Safety

⚠️ **DO NOT execute arbitrary code from artifacts directly!**

**Safe Approaches:**

#### 1. Sandboxed Rendering (React Components)

```tsx
// Safe: React components render in controlled environment
<Suspense fallback={<Loading />}>
  <SafeArtifactComponent />
</Suspense>
```

#### 2. Read-Only Code Display

```tsx
// Safe: Syntax highlighting only, no execution
<SyntaxHighlighter language="python">
  {artifact.content}
</SyntaxHighlighter>
```

#### 3. User Confirmation for Queries

```tsx
// Safe: User must click "Run" to execute Cypher query
<CypherQuery
  query={artifact.content}
  requiresConfirmation={true}
  onConfirm={executeQuery}
/>
```

### Content Sanitization

```typescript
import DOMPurify from 'isomorphic-dompurify';
import { marked } from 'marked';

function sanitizeArtifactContent(content: string, type: string): string {
  switch (type) {
    case 'html':
      return DOMPurify.sanitize(content);

    case 'markdown':
      return DOMPurify.sanitize(marked(content));

    case 'code':
      // No sanitization needed for display-only
      return content;

    case 'cypher':
      // Validate Cypher syntax before execution
      return validateCypherSyntax(content);

    default:
      return content;
  }
}

function validateCypherSyntax(query: string): string {
  // Basic validation: prevent destructive operations in artifact queries
  const destructivePatterns = [
    /DELETE/i,
    /DROP/i,
    /CREATE\s+INDEX/i,
    /CREATE\s+CONSTRAINT/i
  ];

  for (const pattern of destructivePatterns) {
    if (pattern.test(query)) {
      throw new Error('Destructive Cypher operations not allowed in artifacts');
    }
  }

  return query;
}
```

---

## Performance Optimization

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

function LargeCodeArtifact({ lines }: { lines: string[] }) {
  return (
    <Virtuoso
      style={{ height: '100%' }}
      totalCount={lines.length}
      itemContent={(index) => (
        <div className="font-mono text-sm px-4 py-1 hover:bg-white/5">
          <span className="text-white/50 mr-4">{index + 1}</span>
          {lines[index]}
        </div>
      )}
    />
  );
}
```

### Debounced Updates

```typescript
import { debounce } from 'lodash';

// Don't re-render on every keystroke during live editing
const debouncedUpdate = useMemo(
  () => debounce((content: string) => {
    updateArtifact(artifactId, { content });
  }, 500),
  [artifactId]
);

// Usage
<textarea
  value={content}
  onChange={(e) => debouncedUpdate(e.target.value)}
/>
```

### Caching Query Results

```tsx
const { data, isLoading } = useQuery({
  queryKey: ['cypher-query', artifact.content],
  queryFn: () => executeCypherQuery(artifact.content),
  staleTime: 5 * 60 * 1000,  // Cache for 5 minutes
  cacheTime: 10 * 60 * 1000   // Keep in memory for 10 minutes
});
```

---

## Integration with Apex API

### Tool Definition

```typescript
{
  name: "create_apex_artifact",
  description: "Create an artifact to display in the sidebar",
  input_schema: {
    type: "object",
    properties: {
      type: {
        type: "string",
        enum: ["code", "react", "chart", "document"],
        description: "Type of artifact"
      },
      language: {
        type: "string",
        enum: ["typescript", "python", "cypher", "sql", "markdown"],
        description: "Programming language for code artifacts"
      },
      title: {
        type: "string",
        description: "Display title"
      },
      content: {
        type: "string",
        description: "Artifact content"
      },
      metadata: {
        type: "object",
        description: "Additional metadata (data_source, chart_type, etc.)"
      }
    },
    required: ["type", "title", "content"]
  }
}
```

### Backend Implementation

```python
# In apex_memory/api/artifacts.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/artifacts", tags=["artifacts"])

class ArtifactCreate(BaseModel):
    type: str
    language: str | None = None
    title: str
    content: str
    metadata: dict | None = None

@router.post("/")
async def create_artifact(artifact: ArtifactCreate):
    """Create a new artifact"""
    artifact_id = generate_artifact_id()

    # Save to database
    await db.artifacts.insert_one({
        "id": artifact_id,
        "type": artifact.type,
        "language": artifact.language,
        "title": artifact.title,
        "content": artifact.content,
        "metadata": artifact.metadata or {},
        "version": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    return {"artifact_id": artifact_id, "status": "created"}

@router.put("/{artifact_id}")
async def update_artifact(artifact_id: str, updates: dict):
    """Update an existing artifact"""
    # Increment version
    result = await db.artifacts.update_one(
        {"id": artifact_id},
        {
            "$set": {
                "content": updates["content"],
                "updated_at": datetime.utcnow()
            },
            "$inc": {"version": 1}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return {"status": "updated", "version": result.version + 1}
```

---

## Best Practices

### 1. Always Validate Queries

```typescript
function validateQuery(query: string, type: string): boolean {
  switch (type) {
    case 'cypher':
      return validateCypherSyntax(query);
    case 'sql':
      return validateSQLSyntax(query);
    default:
      return true;
  }
}
```

### 2. Provide Execution Feedback

```tsx
{loading && (
  <div className="flex items-center gap-2 text-sm text-white/70">
    <LoaderIcon className="w-4 h-4 animate-spin" />
    Executing query...
  </div>
)}

{results && (
  <div className="text-sm text-green-400">
    ✓ Query completed in {executionTime}ms ({results.length} results)
  </div>
)}
```

### 3. Enable Version Control

```tsx
// Always preserve version history
function updateArtifact(id: string, newContent: string) {
  const currentArtifact = getArtifact(id);

  // Save current version before updating
  saveVersion({
    artifact_id: id,
    version: currentArtifact.version,
    content: currentArtifact.content,
    created_at: new Date().toISOString()
  });

  // Update with new content
  updateArtifactContent(id, {
    content: newContent,
    version: currentArtifact.version + 1
  });
}
```

---

## References

**Apex API Documentation:**
- Query API: http://localhost:8000/api/v1/query
- Graph API: http://localhost:8000/api/v1/graph/query
- Stats API: http://localhost:8000/api/v1/stats
- Artifacts API: http://localhost:8000/api/v1/artifacts

**Related Documentation:**
- Layout patterns → `artifacts-layout.md`
- Rendering → `artifact-types.md`
- Sheet component → `sheet-component.md`

**Security Resources:**
- OWASP: https://owasp.org/www-project-web-security-testing-guide/
- DOMPurify: https://github.com/cure53/DOMPurify

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Type:** Internal Implementation Guide
