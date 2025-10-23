# Artifacts Layout Patterns - Side-by-Side UI Design

**Purpose:** Layout patterns for Claude Artifacts sidebar implementation
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 2 (Verified GitHub Examples - 1.5k+ combined stars)

**Primary Sources:**
- GitHub: [claude-artifact-runner](https://github.com/claudio-silva/claude-artifact-runner)
- GitHub: [claude-artifact-viewer-template](https://github.com/sbusso/claude-artifact-viewer-template)
- GitHub: [claude-artifacts-starter](https://github.com/endlessreform/claude-artifacts-starter)

**Related Documentation:**
- For Sheet component → see `sheet-component.md`
- For artifact types → see `artifact-types.md`
- For Apex integration → see `apex-artifacts-integration.md`

---

## What are Claude Artifacts?

**Definition:** Claude's Artifacts feature allows AI-generated content (code, diagrams, documents) to appear in a **side-by-side popover sidebar** for immediate preview, refinement, and export.

**Key Pattern:** **Generate → Preview → Refine** workflow where users can iteratively improve AI-generated content without leaving the conversation.

---

## Traditional AI Chat vs. Artifacts Pattern

### Traditional AI Chat

```
User: "Create a bar chart showing document counts by type"
Claude: [Returns code as text in conversation]
User: [Copies code, creates new file, runs it manually]
```

### Artifacts Pattern

```
User: "Create a bar chart showing document counts by type"
Claude: [Returns code AND renders it in sidebar]
User: [Sees live chart immediately, can refine in conversation]
Claude: [Updates same artifact with new version]
```

---

## Three Key Components

### 1. Conversation Area (Left)

- Standard chat interface
- User messages + Claude responses
- **Special:** Artifact references show as cards/chips in conversation
- Example: "I've created a visualization for you →" [Artifact Card]

### 2. Artifacts Sidebar (Right)

- **Slides in from right** when artifact is generated
- **Renders content live** (React components, HTML, code)
- **Full-screen capable** (expand to see more detail)
- **Export options** (download, copy code, share)
- **Version history** (see previous iterations)

### 3. Artifact Metadata

- **Title** - Auto-generated or user-specified
- **Type** - Code, diagram, document, data visualization
- **Language/Framework** - React, HTML, SVG, Mermaid
- **Created/Updated** timestamps

---

## Layout Pattern A: Side-by-Side (Most Common)

### Visual Layout

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

### Implementation

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

**When to use:** Desktop applications, primary use case

---

## Layout Pattern B: Popover/Dialog (Alternative)

### Visual Layout

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

### Implementation

```tsx
import { Dialog, DialogContent } from '@radix-ui/react-dialog';

<Dialog open={showArtifact} onOpenChange={setShowArtifact}>
  <DialogContent className="max-w-4xl w-full h-[80vh]">
    <ArtifactViewer artifact={currentArtifact} />
  </DialogContent>
</Dialog>
```

**When to use:** Modal-style artifact viewing, tablet breakpoint

---

## Layout Pattern C: Tabbed View

### Visual Layout

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

**When to use:** Gallery of generated artifacts, not conversation-based

---

## Responsive Behavior

### Desktop (≥1024px) - Side-by-Side

```css
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

### Tablet (768px - 1023px) - Overlay

```css
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

### Mobile (<768px) - Full-Screen

```css
.artifacts-sidebar {
  width: 100%;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100;
}
```

### Responsive Component

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

## Animation Patterns

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

**Animation Properties:**
- **Initial:** `x: '100%', opacity: 0` (off-screen right, invisible)
- **Animate:** `x: 0, opacity: 1` (slide in, fade in)
- **Exit:** `x: '100%', opacity: 0` (slide out, fade out)
- **Transition:** Spring animation (natural, bouncy feel)

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

**When to use:** Switching between different artifacts

---

## Complete Layout Example

```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { useArtifactStore } from '@/stores/artifact-store';

export function ArtifactsLayout() {
  const { currentArtifact, showSidebar } = useArtifactStore();

  return (
    <div className="flex h-screen bg-black text-white">
      {/* Conversation Area */}
      <main className="flex-1 min-w-0 flex flex-col">
        <ConversationHeader />
        <ConversationMessages />
        <ConversationInput />
      </main>

      {/* Artifacts Sidebar */}
      <AnimatePresence>
        {showSidebar && currentArtifact && (
          <motion.aside
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="w-2/5 border-l border-white/10 bg-black/50 backdrop-blur-sm overflow-y-auto"
          >
            <ArtifactHeader artifact={currentArtifact} />
            <ArtifactViewer artifact={currentArtifact} />
            <ArtifactActions artifact={currentArtifact} />
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  );
}
```

---

## Apex Memory System Adaptation

### For Apex UI Implementation

```tsx
// In ConversationHub.tsx

import { useArtifactStore } from '@/stores/artifact-store';
import { Sheet, SheetContent } from '@/components/ui/sheet';

export function ConversationHub() {
  const { currentArtifact, showSidebar, toggleSidebar } = useArtifactStore();

  return (
    <div className="flex h-screen">
      {/* Main conversation area */}
      <main className="flex-1">
        <ConversationMessages />
      </main>

      {/* Artifacts sidebar using Shadcn/ui Sheet */}
      <Sheet open={showSidebar} onOpenChange={toggleSidebar}>
        <SheetContent side="right" className="w-2/5">
          {currentArtifact && (
            <>
              <SheetHeader>
                <SheetTitle>{currentArtifact.title}</SheetTitle>
                <SheetDescription>
                  {currentArtifact.type} • v{currentArtifact.version}
                </SheetDescription>
              </SheetHeader>
              <ArtifactRenderer artifact={currentArtifact} />
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
```

---

## Best Practices

### 1. Always Provide Close Button

```tsx
<button
  onClick={closeSidebar}
  className="absolute top-4 right-4 p-2 rounded hover:bg-white/10"
  aria-label="Close artifact"
>
  <XIcon className="w-5 h-5" />
</button>
```

### 2. Maintain Conversation Context

Don't hide the conversation when artifact is open - keep it visible at reduced width.

### 3. Support Keyboard Shortcuts

```tsx
useEffect(() => {
  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Escape') closeSidebar();
    if (e.metaKey && e.key === 'k') toggleSidebar();
  }
  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, []);
```

### 4. Preserve Scroll Position

```tsx
const scrollRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  // Save scroll position when artifact changes
  return () => {
    const scrollPos = scrollRef.current?.scrollTop || 0;
    saveScrollPosition(currentArtifact.id, scrollPos);
  };
}, [currentArtifact]);
```

---

## References

**GitHub Repositories:**
- [claude-artifact-runner](https://github.com/claudio-silva/claude-artifact-runner) - Most comprehensive implementation
- [claude-artifact-viewer-template](https://github.com/sbusso/claude-artifact-viewer-template) - Template implementation
- [claude-artifacts-starter](https://github.com/endlessreform/claude-artifacts-starter) - Minimal starter

**Design Resources:**
- Framer Motion: https://www.framer.com/motion/
- Radix UI: https://www.radix-ui.com/
- Tailwind CSS: https://tailwindcss.com/docs

**Related Documentation:**
- Sheet component details → `sheet-component.md`
- Artifact rendering → `artifact-types.md`
- Apex integration → `apex-artifacts-integration.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 2 (Verified GitHub Examples)
