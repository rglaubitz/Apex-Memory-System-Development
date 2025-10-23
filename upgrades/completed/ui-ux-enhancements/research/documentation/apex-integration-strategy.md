# Apex Integration Strategy - Adding Shadcn/ui to Apex UI

**Purpose:** Strategic guide for integrating Shadcn/ui into existing Apex UI
**Date Created:** 2025-10-21
**Documentation Tier:** Internal (Apex-specific)

**Related Documentation:**
- For installation → see `shadcn-installation.md`
- For components → see `component-catalog.md`
- For customization → see `customization-guide.md`

---

## Integration Strategy

### Gradual Adoption

**DON'T:** Replace all components at once
**DO:** Add Shadcn/ui components incrementally as needed

**Phase 1:** New features only (Artifacts sidebar, tool indicators)
**Phase 2:** Replace components during refactors
**Phase 3:** Full migration (if desired)

---

## Priority Components for Apex

### 1. Sheet (Artifacts Sidebar)

```bash
npx shadcn@latest add sheet
```

**Why:** Core to Artifacts UI pattern

```tsx
import { Sheet, SheetContent } from '@/components/ui/sheet';

function ArtifactsSidebar() {
  return (
    <Sheet>
      <SheetContent side="right" className="w-2/5">
        {/* Artifact content */}
      </SheetContent>
    </Sheet>
  );
}
```

### 2. Button

```bash
npx shadcn@latest add button
```

**Why:** Consistent button styling across app

### 3. Dialog

```bash
npx shadcn@latest add dialog
```

**Why:** Modals, confirmations, settings

### 4. Command

```bash
npx shadcn@latest add command
```

**Why:** Command palette for quick actions

---

## Integration Checklist

- [ ] Run `npx shadcn@latest init`
- [ ] Update tsconfig.json with path aliases
- [ ] Update vite.config.ts with resolve alias
- [ ] Add Sheet component (`npx shadcn@latest add sheet`)
- [ ] Add Button component
- [ ] Add Dialog component
- [ ] Customize theme colors in index.css
- [ ] Test integration with existing components
- [ ] Update Artifacts sidebar to use Sheet
- [ ] Create ToolUseIndicator with Shadcn/ui
- [ ] Update forms to use Shadcn/ui components

---

## Coexistence with Existing Components

**Shadcn/ui can coexist with your existing components:**

```tsx
// Existing Apex button
import { ApexButton } from '@/components/ApexButton';

// New Shadcn/ui button
import { Button } from '@/components/ui/button';

function MyComponent() {
  return (
    <div>
      <ApexButton>Old Button</ApexButton>
      <Button>New Button</Button>
    </div>
  );
}
```

**Gradually migrate as you refactor.**

---

## Performance Considerations

### Tree Shaking

Components are only included if imported:

```tsx
// ✅ Good: Only Button is bundled
import { Button } from '@/components/ui/button';

// ❌ Bad: Entire library bundled (not possible with Shadcn/ui anyway)
```

### Bundle Size

- Each component: ~2-5KB gzipped
- Radix UI: ~15-20KB gzipped (shared across all components)
- Total overhead: ~20-30KB for typical usage

---

## References

**Official Documentation:**
- Shadcn/ui: https://ui.shadcn.com/
- Installation: https://ui.shadcn.com/docs/installation

**Related Documentation:**
- Installation → `shadcn-installation.md`
- Component catalog → `component-catalog.md`
- Customization → `customization-guide.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Type:** Internal Integration Guide
