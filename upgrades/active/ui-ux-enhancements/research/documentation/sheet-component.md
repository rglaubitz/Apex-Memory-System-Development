# Sheet Component Implementation - Shadcn/ui Integration

**Purpose:** Technical implementation of Artifacts sidebar using Shadcn/ui Sheet
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 2 (Verified GitHub Examples + Official Shadcn/ui docs)

**Related Documentation:**
- For layout patterns → see `artifacts-layout.md`
- For artifact types → see `artifact-types.md`
- For Shadcn/ui installation → see `shadcn-installation.md`

---

## Overview

The Artifacts sidebar is implemented using **Shadcn/ui's Sheet component** - a versatile side panel that slides in from any edge of the screen.

**Key Benefits:**
- Built on Radix UI (accessible by default)
- Fully customizable (copy-paste, not npm package)
- Responsive behavior baked in
- Smooth animations via Framer Motion
- **Perfect match for existing Apex stack**

---

## Technical Stack

### Common Dependencies Across All Implementations

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@radix-ui/react-dialog": "^1.x",
    "@radix-ui/react-separator": "^1.x",
    "tailwindcss": "^3.4.17",
    "framer-motion": "^12.x",
    "lucide-react": "latest"
  }
}
```

**Why This Stack?**

- **React + TypeScript** - Type-safe component rendering
- **Radix UI** - Accessible primitives (Dialog, Popover, Tabs)
- **Tailwind CSS** - Rapid styling (matches Claude's design system)
- **Framer Motion** - Smooth sidebar animations
- **Lucide React** - Icon library (consistent with Apex UI)

**⭐ Perfect Match:** This is the **exact stack already in use** in Apex Memory System UI!

---

## Sheet Component Anatomy

### Basic Structure

```tsx
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

<Sheet>
  <SheetTrigger>Open</SheetTrigger>
  <SheetContent>
    <SheetHeader>
      <SheetTitle>Are you absolutely sure?</SheetTitle>
      <SheetDescription>
        This action cannot be undone.
      </SheetDescription>
    </SheetHeader>
  </SheetContent>
</Sheet>
```

### Components Breakdown

| Component | Purpose | Required |
|-----------|---------|----------|
| `Sheet` | Root container, manages open/close state | ✅ Yes |
| `SheetTrigger` | Button to open sheet | Optional |
| `SheetContent` | Actual panel that slides in | ✅ Yes |
| `SheetHeader` | Header section (title + description) | Recommended |
| `SheetTitle` | Main heading (accessibility) | Recommended |
| `SheetDescription` | Subtitle/context (accessibility) | Recommended |
| `SheetFooter` | Bottom actions area | Optional |
| `SheetClose` | Close button | Optional |

---

## Artifacts Sidebar Implementation

### Complete Example

```tsx
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { useArtifactStore } from '@/stores/artifact-store';

export function ArtifactsSidebar() {
  const { currentArtifact, showSidebar, toggleSidebar } = useArtifactStore();

  return (
    <Sheet open={showSidebar} onOpenChange={toggleSidebar}>
      <SheetContent side="right" className="w-2/5 sm:max-w-xl">
        {currentArtifact && (
          <>
            <SheetHeader>
              <SheetTitle>{currentArtifact.title}</SheetTitle>
              <SheetDescription>
                {currentArtifact.type} • Version {currentArtifact.version}
              </SheetDescription>
            </SheetHeader>

            <div className="mt-6 space-y-4">
              <ArtifactRenderer artifact={currentArtifact} />
            </div>

            <div className="absolute bottom-4 left-4 right-4 flex gap-2">
              <Button onClick={() => exportArtifact(currentArtifact)}>
                Export
              </Button>
              <Button variant="outline" onClick={() => copyCode(currentArtifact)}>
                Copy Code
              </Button>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
```

---

## State Management

### Artifact Store (Zustand)

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
  closeSidebar: () => void;
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

  toggleSidebar: () => set((state) => ({ showSidebar: !state.showSidebar })),

  closeSidebar: () => set({ showSidebar: false })
}));
```

### Usage in Components

```tsx
// Add artifact from conversation
const { addArtifact } = useArtifactStore();

function handleClaudeResponse(message) {
  if (message.tool_use?.name === 'create_artifact') {
    addArtifact({
      id: generateId(),
      type: message.tool_use.input.type,
      title: message.tool_use.input.title,
      content: message.tool_use.input.content,
      language: message.tool_use.input.language,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      version: 1
    });
  }
}

// Update artifact from conversation
const { updateArtifact } = useArtifactStore();

function handleArtifactUpdate(message) {
  if (message.tool_use?.name === 'update_artifact') {
    updateArtifact(message.tool_use.input.artifact_id, {
      content: message.tool_use.input.content,
      updated_at: new Date().toISOString()
    });
  }
}
```

---

## Accessibility Features

### Keyboard Navigation

```tsx
function ArtifactSidebar() {
  const { closeSidebar, toggleSidebar } = useArtifactStore();

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Close with Escape
      if (e.key === 'Escape') {
        closeSidebar();
      }

      // Toggle with Cmd/Ctrl + K
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        toggleSidebar();
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [closeSidebar, toggleSidebar]);

  return (
    <Sheet>
      <SheetContent
        role="complementary"
        aria-label="Artifact viewer"
      >
        {/* Content */}
      </SheetContent>
    </Sheet>
  );
}
```

### Screen Reader Announcements

```tsx
import { useAnnouncer } from '@react-aria/live-announcer';

function ArtifactCreated({ title }: { title: string }) {
  const announce = useAnnouncer();

  useEffect(() => {
    announce(`New artifact created: ${title}`);
  }, [title, announce]);

  return null;
}

// Usage in parent component
{currentArtifact && (
  <ArtifactCreated title={currentArtifact.title} />
)}
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

return (
  <SheetContent ref={sidebarRef} tabIndex={-1}>
    {/* Content */}
  </SheetContent>
);
```

### ARIA Labels

```tsx
<Sheet open={showSidebar} onOpenChange={toggleSidebar}>
  <SheetContent
    aria-labelledby="artifact-title"
    aria-describedby="artifact-description"
  >
    <SheetHeader>
      <SheetTitle id="artifact-title">
        {currentArtifact.title}
      </SheetTitle>
      <SheetDescription id="artifact-description">
        {currentArtifact.type} artifact, version {currentArtifact.version}
      </SheetDescription>
    </SheetHeader>
  </SheetContent>
</Sheet>
```

---

## Responsive Configuration

### Breakpoint-Based Width

```tsx
<SheetContent
  side="right"
  className={cn(
    // Desktop: 40% width, max 600px
    "w-2/5 max-w-[600px]",
    // Tablet: 80% width
    "md:w-4/5",
    // Mobile: Full width
    "sm:w-full"
  )}
>
  {/* Content */}
</SheetContent>
```

### Conditional Rendering

```tsx
const isMobile = useMediaQuery('(max-width: 768px)');

if (isMobile) {
  return (
    <Sheet open={showSidebar} onOpenChange={toggleSidebar}>
      <SheetContent side="bottom" className="h-[90vh]">
        {/* Mobile: Slide up from bottom */}
      </SheetContent>
    </Sheet>
  );
}

return (
  <Sheet open={showSidebar} onOpenChange={toggleSidebar}>
    <SheetContent side="right" className="w-2/5">
      {/* Desktop: Slide in from right */}
    </SheetContent>
  </Sheet>
);
```

---

## Custom Styling

### Theme Customization

```tsx
<SheetContent
  className={cn(
    // Base styling
    "bg-black/95 backdrop-blur-sm",
    "border-l border-white/10",
    "text-white",

    // Scrollbar styling
    "[&::-webkit-scrollbar]:w-2",
    "[&::-webkit-scrollbar-track]:bg-transparent",
    "[&::-webkit-scrollbar-thumb]:bg-white/20",
    "[&::-webkit-scrollbar-thumb]:rounded-full"
  )}
>
  {/* Content */}
</SheetContent>
```

### Animation Customization

```tsx
// Override Framer Motion defaults
<motion.div
  initial={{ x: '100%' }}
  animate={{ x: 0 }}
  exit={{ x: '100%' }}
  transition={{
    type: 'spring',
    stiffness: 300,    // Higher = snappier
    damping: 30,       // Higher = less bouncy
    mass: 0.8          // Lower = faster
  }}
>
  <SheetContent>
    {/* Content */}
  </SheetContent>
</motion.div>
```

---

## Integration with Conversation

### Artifact Card in Chat

```tsx
function ArtifactCard({ artifact }: { artifact: Artifact }) {
  const { setCurrentArtifact } = useArtifactStore();

  return (
    <button
      onClick={() => setCurrentArtifact(artifact.id)}
      className="inline-flex items-center gap-2 px-3 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
    >
      <FileCodeIcon className="w-4 h-4" />
      <span className="text-sm font-medium">{artifact.title}</span>
      <ChevronRightIcon className="w-4 h-4 text-white/50" />
    </button>
  );
}

// Usage in conversation message
<div className="message">
  <p>I've created a visualization for you:</p>
  <ArtifactCard artifact={currentArtifact} />
</div>
```

---

## References

**Official Documentation:**
- Shadcn/ui Sheet: https://ui.shadcn.com/docs/components/sheet
- Radix UI Dialog: https://www.radix-ui.com/primitives/docs/components/dialog
- Framer Motion: https://www.framer.com/motion/

**Accessibility:**
- WAI-ARIA Dialog Pattern: https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
- React Aria Announcer: https://react-spectrum.adobe.com/react-aria/useAnnouncer.html

**Related Documentation:**
- Layout patterns → `artifacts-layout.md`
- Artifact rendering → `artifact-types.md`
- Shadcn/ui setup → `shadcn-installation.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 2 (Verified Implementation Pattern)
