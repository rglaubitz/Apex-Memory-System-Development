# Tool Visualization - Real-Time Tool Call Display

**Purpose:** Patterns for visualizing AI tool calls in the UI
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 1 + Internal (Official docs + Apex patterns)

**Related Documentation:**
- For SDK overview → see `vercel-ai-sdk-overview.md`
- For useChat hook → see `usechat-hook.md`
- For Apex tools → see `apex-tool-definitions.md`

---

## Overview

**Tool visualization** shows users what the AI is doing in real-time, creating transparency and trust in AI-driven interfaces.

**Key Benefits:**
- **Transparency** - Users see exactly what tools are being called
- **Trust** - Reduces "black box" feeling of AI interactions
- **Education** - Users learn what capabilities exist
- **Debug** - Developers can see tool execution flow

---

## Pattern 1: Tool Call Indicators

### Basic Tool Indicator

```tsx
import { motion } from 'framer-motion';
import { Search, Network, Clock } from 'lucide-react';

function ToolCallIndicator({ toolCall }) {
  const icons = {
    search_apex_documents: Search,
    query_apex_graph: Network,
    get_apex_temporal_data: Clock
  };

  const Icon = icons[toolCall.name] || Tool;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-3 p-3 bg-white/5 rounded-lg border border-white/10"
    >
      <Icon className="w-5 h-5 text-purple-400" />
      <div className="flex-1">
        <p className="text-sm font-medium">
          {toolCall.name.replace(/_/g, ' ')}
        </p>
        <p className="text-xs text-white/60">
          {Object.keys(toolCall.arguments).length} parameters
        </p>
      </div>
      <Spinner className="w-4 h-4" />
    </motion.div>
  );
}
```

### Expandable Tool Details

```tsx
import { ChevronDown } from 'lucide-react';

function ExpandableToolCall({ toolCall }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-white/10 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10"
      >
        <Tool className="w-5 h-5" />
        <span className="flex-1 text-left text-sm font-medium">
          {toolCall.name}
        </span>
        <ChevronDown
          className={`w-4 h-4 transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}
        />
      </button>

      {isExpanded && (
        <div className="p-3 bg-black/50 border-t border-white/10">
          <pre className="text-xs text-white/80">
            {JSON.stringify(toolCall.arguments, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
```

---

## Pattern 2: Multi-Step Workflows

### Workflow Progress

```tsx
interface WorkflowStage {
  stage: string;
  status: 'pending' | 'in_progress' | 'complete' | 'error';
  tool?: string;
  duration?: number;
}

function WorkflowProgress({ stages }: { stages: WorkflowStage[] }) {
  return (
    <div className="space-y-2">
      {stages.map((stage, i) => (
        <div key={i} className="flex items-center gap-3">
          <StatusIcon status={stage.status} />
          <span className="text-sm flex-1">{stage.stage}</span>
          {stage.tool && (
            <Badge variant="secondary" className="text-xs">
              {stage.tool}
            </Badge>
          )}
          {stage.duration && (
            <span className="text-xs text-white/50">
              {stage.duration}ms
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

function StatusIcon({ status }) {
  const icons = {
    pending: <Circle className="w-4 h-4 text-white/30" />,
    in_progress: <Loader className="w-4 h-4 text-purple-400 animate-spin" />,
    complete: <CheckCircle className="w-4 h-4 text-green-400" />,
    error: <XCircle className="w-4 h-4 text-red-400" />
  };

  return icons[status];
}
```

### Usage in Conversation

```tsx
function ConversationWithWorkflow() {
  const [currentStages, setCurrentStages] = useState<WorkflowStage[]>([]);

  const { messages } = useChat({
    api: '/api/apex/conversation',
    onToolCall: (toolCall) => {
      // Add new stage when tool is called
      setCurrentStages((stages) => [
        ...stages,
        {
          stage: `Calling ${toolCall.name}...`,
          status: 'in_progress',
          tool: toolCall.name
        }
      ]);
    }
  });

  return (
    <div>
      {currentStages.length > 0 && (
        <WorkflowProgress stages={currentStages} />
      )}
      <MessageList messages={messages} />
    </div>
  );
}
```

---

## Pattern 3: Apex-Specific Tool Visualization

### Apex Tool Call Component

```tsx
interface ApexToolCall {
  name: 'search_apex_documents' | 'query_apex_graph' | 'get_apex_temporal_data';
  arguments: Record<string, any>;
  status: 'executing' | 'complete' | 'error';
  result?: any;
}

function ApexToolVisualization({ toolCall }: { toolCall: ApexToolCall }) {
  const config = {
    search_apex_documents: {
      icon: Search,
      color: 'text-blue-400',
      label: 'Searching Documents'
    },
    query_apex_graph: {
      icon: Network,
      color: 'text-purple-400',
      label: 'Querying Graph'
    },
    get_apex_temporal_data: {
      icon: Clock,
      color: 'text-green-400',
      label: 'Analyzing Patterns'
    }
  };

  const { icon: Icon, color, label } = config[toolCall.name];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="p-4 bg-gradient-to-br from-white/5 to-white/10 rounded-lg border border-white/10"
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-6 h-6 ${color}`} />
        <div className="flex-1">
          <h4 className="font-medium">{label}</h4>
          <p className="text-sm text-white/60 mt-1">
            {getToolDescription(toolCall)}
          </p>

          {toolCall.status === 'complete' && toolCall.result && (
            <div className="mt-3 p-2 bg-black/30 rounded text-xs">
              {formatToolResult(toolCall.result)}
            </div>
          )}
        </div>

        <StatusBadge status={toolCall.status} />
      </div>
    </motion.div>
  );
}

function getToolDescription(toolCall: ApexToolCall): string {
  switch (toolCall.name) {
    case 'search_apex_documents':
      return `Searching for: "${toolCall.arguments.query}"`;
    case 'query_apex_graph':
      return 'Executing Cypher query on knowledge graph';
    case 'get_apex_temporal_data':
      return `Analyzing temporal patterns for: ${toolCall.arguments.entity_name}`;
  }
}
```

---

## Pattern 4: Tool Result Preview

### Inline Result Preview

```tsx
function ToolResultPreview({ result, type }) {
  switch (type) {
    case 'search_results':
      return (
        <div className="space-y-2">
          <p className="text-xs text-white/60">
            Found {result.total} documents
          </p>
          <div className="space-y-1">
            {result.results.slice(0, 3).map((doc, i) => (
              <div key={i} className="text-xs p-2 bg-white/5 rounded">
                <p className="font-medium">{doc.title}</p>
                <p className="text-white/50 truncate">{doc.excerpt}</p>
              </div>
            ))}
          </div>
        </div>
      );

    case 'graph_results':
      return (
        <div className="text-xs">
          <p className="text-white/60">
            Found {result.nodes.length} nodes, {result.relationships.length} relationships
          </p>
        </div>
      );

    case 'temporal_data':
      return (
        <div className="text-xs">
          <p className="text-white/60">
            {result.patterns.length} patterns detected
          </p>
        </div>
      );
  }
}
```

---

## Tool Use Integration

### Backend Route (Next.js API)

```typescript
// /app/api/apex/conversation/route.ts
import { streamText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: anthropic('claude-sonnet-4-5'),
    messages,
    tools: {
      search_apex_documents: {
        description: 'Search the Apex knowledge base for documents',
        parameters: z.object({
          query: z.string(),
          filters: z.object({
            file_type: z.enum(['pdf', 'docx', 'pptx']).optional()
          }).optional()
        }),
        execute: async ({ query, filters }) => {
          const response = await fetch('http://localhost:8000/api/v1/query', {
            method: 'POST',
            body: JSON.stringify({ query, filters })
          });
          return await response.json();
        }
      },

      query_apex_graph: {
        description: 'Execute Cypher query on Neo4j knowledge graph',
        parameters: z.object({
          cypher: z.string(),
          parameters: z.record(z.any()).optional()
        }),
        execute: async ({ cypher, parameters }) => {
          const response = await fetch('http://localhost:8000/api/v1/graph/query', {
            method: 'POST',
            body: JSON.stringify({ cypher, parameters })
          });
          return await response.json();
        }
      },

      get_apex_temporal_data: {
        description: 'Retrieve temporal patterns for an entity',
        parameters: z.object({
          entity_name: z.string(),
          time_range: z.string().optional()
        }),
        execute: async ({ entity_name, time_range }) => {
          const response = await fetch('http://localhost:8000/api/v1/temporal/entity', {
            method: 'POST',
            body: JSON.stringify({ entity_name, time_range })
          });
          return await response.json();
        }
      }
    }
  });

  return result.toDataStreamResponse();
}
```

### Frontend Hook Usage

```tsx
function ApexConversation() {
  const [toolCalls, setToolCalls] = useState<ApexToolCall[]>([]);

  const { messages, input, handleSubmit } = useChat({
    api: '/api/apex/conversation',

    onToolCall: async (toolCall) => {
      // Add tool call to visualization
      setToolCalls((calls) => [
        ...calls,
        { ...toolCall, status: 'executing' }
      ]);

      console.log('Tool called:', toolCall.name, toolCall.arguments);
    },

    onFinish: (message) => {
      // Mark all tools as complete
      setToolCalls((calls) =>
        calls.map((call) => ({ ...call, status: 'complete' }))
      );

      // Save conversation
      saveConversation(messages);
    }
  });

  return (
    <div className="conversation">
      {/* Tool visualizations */}
      {toolCalls.length > 0 && (
        <div className="space-y-2 mb-4">
          {toolCalls.map((call, i) => (
            <ApexToolVisualization key={i} toolCall={call} />
          ))}
        </div>
      )}

      {/* Messages */}
      {messages.map((m) => (
        <Message key={m.id} message={m} />
      ))}

      {/* Input */}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={(e) => setInput(e.target.value)} />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

---

## References

**Official Documentation:**
- Vercel AI SDK: https://ai-sdk.dev/docs
- Tool Use Guide: https://ai-sdk.dev/docs/ai-sdk-core/tools-and-tool-calling

**Apex API:**
- Query API: http://localhost:8000/api/v1/query
- Graph API: http://localhost:8000/api/v1/graph/query
- Temporal API: http://localhost:8000/api/v1/temporal/entity

**Related Documentation:**
- SDK overview → `vercel-ai-sdk-overview.md`
- useChat hook → `usechat-hook.md`
- Apex tool definitions → `apex-tool-definitions.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 + Internal (Official + Apex Patterns)
