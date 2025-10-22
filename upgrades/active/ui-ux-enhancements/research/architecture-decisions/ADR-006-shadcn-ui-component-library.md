# ADR-006: Shadcn/ui Component Library

**Status:** Accepted
**Date:** 2025-10-21
**Decision Makers:** Development Team
**Affected Components:** Frontend UI, All React Components, Design System

---

## Context

### Problem Statement

The Apex Memory System UI requires a comprehensive component library to implement the interface efficiently. The library must support:

1. **Rapid Development**
   - Pre-built components for common patterns (buttons, forms, modals)
   - Consistent styling across all components
   - Easy customization for brand-specific needs

2. **Apple Minimalist Design Alignment**
   - Clean, uncluttered visual style
   - Typography-focused design
   - Subtle animations and transitions
   - Monochrome color palette support

3. **Accessibility Standards**
   - WCAG 2.1 Level AA compliance
   - Keyboard navigation
   - Screen reader support
   - Focus management

4. **Developer Experience**
   - TypeScript support
   - React hooks integration
   - Clear documentation
   - Active maintenance

### Current State (Phase 2)

**Week 2-4 implementation uses:**
- Basic HTML elements with Tailwind CSS classes
- No component library (custom components only)
- Inconsistent styling patterns
- Manual accessibility implementation

**Pain points:**
- Repetitive code for common UI patterns
- Inconsistent spacing and colors
- Accessibility features require manual implementation
- No design system enforcing consistency

---

## Decision

**We will adopt Shadcn/ui as our component library for all UI development starting in Phase 3 (Week 6).**

### Why Shadcn/ui?

**1. Copy-Paste Architecture** (Not a package dependency)
- Components are copied into your codebase (`src/components/ui/`)
- Full control over component code
- No version lock-in or breaking changes from external updates
- Can customize any component without forking

**2. Built on Radix UI Primitives**
- Industry-leading accessibility (WAI-ARIA compliant)
- Unstyled primitives provide flexibility
- Keyboard navigation built-in
- Focus management handled automatically

**3. Tailwind CSS Native**
- Uses same utility classes we're already using
- No additional CSS-in-JS dependencies
- Consistent with our existing styling approach
- Easy theming through Tailwind config

**4. Minimal Visual Styling**
- Components are styled minimally by default
- Easy to adapt to Apple minimalist aesthetic
- No opinionated design system to override
- Typography-focused approach aligns with our goals

---

## Research Support

### Tier 1 Sources

**Shadcn/ui Documentation**
- **Source:** https://ui.shadcn.com/
- **Tier:** 2 (Community Project - 40k+ stars)
- **Version:** 1.0+
- **Reference:** RESEARCH-REFERENCES.md (Phase 3 section)

**Key features:**
- 47+ accessible components
- Copy-paste installation
- Dark mode support
- TypeScript first

**Radix UI Documentation**
- **Source:** https://www.radix-ui.com/
- **Tier:** 1 (Official Documentation)
- **Version:** 1.0+
- **Reference:** RESEARCH-REFERENCES.md (Phase 3 section)

**Accessibility commitments:**
- WAI-ARIA Design Patterns implemented
- Tested with screen readers (NVDA, JAWS, VoiceOver)
- Keyboard navigation patterns
- Focus trap management

**Tailwind CSS Documentation**
- **Source:** https://tailwindcss.com/docs
- **Tier:** 1 (Official Documentation)
- **Version:** 3.4+
- **Reference:** RESEARCH-REFERENCES.md (Phase 3 section)

---

## Alternatives Considered

### Alternative 1: Material-UI (MUI)

**Approach:** Use Material Design component library

**Pros:**
- ✅ Mature ecosystem (10+ years)
- ✅ Comprehensive component set (100+ components)
- ✅ Large community and support
- ✅ Excellent documentation

**Cons:**
- ❌ Opinionated Material Design aesthetic (conflicts with Apple minimalist goal)
- ❌ Heavy bundle size (~300KB gzipped)
- ❌ Requires significant customization to achieve minimal look
- ❌ CSS-in-JS adds complexity (Emotion/styled-components)
- ❌ Breaking changes between major versions

**Research Support:**
- **Source:** https://mui.com/
- **Tier:** 1 (Official Documentation)

**Decision:** Rejected - Material Design aesthetic conflicts with Apple minimalist design goal

---

### Alternative 2: Ant Design

**Approach:** Use Ant Design component library

**Pros:**
- ✅ Comprehensive component library (80+ components)
- ✅ Enterprise-focused features
- ✅ Good internationalization support
- ✅ Proven in large applications

**Cons:**
- ❌ Chinese aesthetic (not aligned with Apple minimalism)
- ❌ Heavy bundle size (~600KB gzipped with all components)
- ❌ Difficult to customize deeply
- ❌ Less CSS-in-JS or Tailwind integration
- ❌ Opinionated design system

**Research Support:**
- **Source:** https://ant.design/
- **Tier:** 1 (Official Documentation)

**Decision:** Rejected - Design aesthetic too opinionated, poor Tailwind integration

---

### Alternative 3: Headless UI

**Approach:** Use Tailwind's official Headless UI library

**Pros:**
- ✅ Official Tailwind component library
- ✅ Completely unstyled (maximum flexibility)
- ✅ TypeScript support
- ✅ Small bundle size
- ✅ Accessibility built-in

**Cons:**
- ❌ Limited component set (~10 components)
- ❌ Requires more manual styling work
- ❌ Missing complex components (Tables, Forms, Data Display)
- ❌ No pre-built design system

**Research Support:**
- **Source:** https://headlessui.com/
- **Tier:** 1 (Official Tailwind Labs Documentation)

**Decision:** Rejected - Too minimal, missing critical components (would require building ~30 components from scratch)

---

### Alternative 4: Chakra UI

**Approach:** Use Chakra UI component library

**Pros:**
- ✅ Excellent developer experience
- ✅ Accessibility focused
- ✅ Good component variety (50+ components)
- ✅ Simple theming system
- ✅ TypeScript support

**Cons:**
- ❌ Opinionated default styling
- ❌ Uses CSS-in-JS (Emotion) instead of Tailwind
- ❌ Would require migrating existing Tailwind styles
- ❌ Different mental model from utility-first approach

**Research Support:**
- **Source:** https://chakra-ui.com/
- **Tier:** 1 (Official Documentation)

**Decision:** Rejected - CSS-in-JS conflicts with our Tailwind-first approach

---

### Alternative 5: Build Custom Component Library

**Approach:** Build all components from scratch

**Pros:**
- ✅ 100% control over every aspect
- ✅ Perfect alignment with design goals
- ✅ No external dependencies
- ✅ Exact bundle size control

**Cons:**
- ❌ 4-6 weeks additional development time (estimate ~30 components)
- ❌ Manual accessibility implementation (error-prone)
- ❌ Testing burden (need comprehensive a11y test suite)
- ❌ Ongoing maintenance (bug fixes, browser compatibility)
- ❌ Reinventing solved problems

**Decision:** Rejected - Not worth 4-6 weeks for commodity components

---

## Consequences

### Positive Consequences

**1. Full Code Ownership** ⭐ PRIMARY BENEFIT
- Components live in our codebase (`src/components/ui/`)
- Can modify any component without forking
- No version lock-in or breaking changes
- Easy to understand (it's just your code)

**Example:**
```bash
# Install a component (copies code to your project)
npx shadcn-ui@latest add button

# Result: src/components/ui/button.tsx created
# You own this file now - modify as needed
```

**2. Excellent Accessibility**
- All components built on Radix UI primitives
- WAI-ARIA patterns implemented correctly
- Keyboard navigation works out of the box
- Screen reader tested

**3. Minimal Design Alignment**
- Components are barely styled by default
- Easy to apply Apple minimalist aesthetic
- No visual opinions to override
- Typography-focused approach

**4. Tailwind Integration**
- Uses utility classes we're already using
- No CSS-in-JS to learn or maintain
- Consistent styling approach across codebase
- Easy theme customization via `tailwind.config.js`

**5. Small Bundle Size**
- Only pay for components you use (they're in your code)
- No monolithic library to import
- Tree-shaking works naturally

---

### Negative Consequences

**1. Manual Component Updates**
- New Shadcn/ui versions require manual re-copying components
- No automatic dependency updates via npm
- Need to track which components need updates

**Mitigation:**
- Create `UI_COMPONENTS_VERSION.md` to track component versions
- Set calendar reminder to check for updates monthly
- Use git diff to see what changed in updated components
- Only update components when new features needed

**2. Limited Component Discovery**
- Can't browse all available components in IDE autocomplete
- Need to reference Shadcn/ui docs to find components
- Not immediately obvious what's available

**Mitigation:**
- Create `src/components/ui/README.md` listing all installed components
- Add JSDoc comments linking to Shadcn/ui docs
- Include component catalog in project documentation

**3. Initial Setup Time**
- Need to install components one-by-one
- Configure Tailwind and TypeScript paths
- Set up dark mode configuration

**Mitigation:**
- Week 6 dedicated to initial setup (2-3 days)
- Install most common components upfront (~20 components)
- Document setup process for future reference

**4. Customization Responsibility**
- We own any bugs we introduce via customization
- Need to test customized components thoroughly
- No upstream support for modified components

**Mitigation:**
- Minimize customization initially (use defaults where possible)
- Comprehensive test suite for customized components
- Document all customizations in component file comments

---

## Implementation Notes

### Initial Setup (Week 6, Day 1)

**1. Install Shadcn/ui:**
```bash
npx shadcn-ui@latest init
```

**2. Configure (`components.json`):**
```json
{
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

**3. Install Core Components (Day 1-2):**
```bash
# Forms & Inputs
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add form
npx shadcn-ui@latest add label
npx shadcn-ui@latest add select
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add radio-group

# Layout & Navigation
npx shadcn-ui@latest add sheet      # For ArtifactSidebar
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add scroll-area

# Feedback & Overlays
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add skeleton

# Data Display
npx shadcn-ui@latest add card
npx shadcn-ui@latest add table
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add avatar

# Total: 20 components
```

### Customization for Apple Minimalist Design

**Typography adjustments (`src/components/ui/button.tsx`):**
```typescript
// Before (Shadcn/ui default)
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium"
)

// After (Apple minimalist)
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg text-sm font-normal tracking-tight"
  // ↑ Changed: rounded-lg (more subtle), font-normal (less bold), tracking-tight
)
```

**Color palette (`tailwind.config.js`):**
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        // Apple-inspired neutrals
        primary: {
          DEFAULT: "hsl(210 10% 23%)",  // Dark gray (Apple-like)
          foreground: "hsl(0 0% 100%)",
        },
        secondary: {
          DEFAULT: "hsl(210 10% 46%)",  // Medium gray
          foreground: "hsl(0 0% 100%)",
        },
        accent: {
          DEFAULT: "hsl(212 100% 47%)",  // Apple blue
          foreground: "hsl(0 0% 100%)",
        }
      }
    }
  }
}
```

### Component Inventory Tracking

**Create `src/components/ui/UI_COMPONENTS_VERSION.md`:**
```markdown
# UI Components Inventory

**Shadcn/ui Version:** 1.0.0 (as of 2025-10-21)
**Last Updated:** 2025-10-21

## Installed Components

| Component | Installed | Version | Customized | Notes |
|-----------|-----------|---------|------------|-------|
| button | 2025-10-21 | 1.0.0 | Yes | Changed rounded-md → rounded-lg, font-medium → font-normal |
| input | 2025-10-21 | 1.0.0 | No | - |
| sheet | 2025-10-21 | 1.0.0 | No | Used for ArtifactSidebar |
| tabs | 2025-10-21 | 1.0.0 | Yes | Reduced border thickness for minimal look |

## Update Checklist

- [ ] Check Shadcn/ui changelog: https://github.com/shadcn-ui/ui/releases
- [ ] Identify components needing updates
- [ ] Re-run `npx shadcn-ui@latest add <component>` for updated versions
- [ ] Test customized components still work after update
- [ ] Update this inventory with new versions
```

---

## Success Metrics

**Development velocity:**
- ✅ Reduce component development time by 60% (vs. building from scratch)
- ✅ All 20 core components installed within 2 days
- ✅ First customized component (button) completed within 4 hours

**Accessibility:**
- ✅ 100% keyboard navigation support (all interactive components)
- ✅ WCAG 2.1 Level AA compliance (automated axe-core tests passing)
- ✅ Screen reader compatibility (tested with VoiceOver)

**Code quality:**
- ✅ 90%+ test coverage for customized components
- ✅ TypeScript errors: 0
- ✅ Zero runtime accessibility warnings

**User experience:**
- ✅ 80%+ user satisfaction with UI responsiveness
- ✅ Consistent styling across all pages (design system review)
- ✅ Fast UI interactions (<16ms for button clicks, <100ms for modal open)

---

## Testing Strategy

**Accessibility tests (every component):**
```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Button Component Accessibility', () => {
  test('should have no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('should be keyboard navigable', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button');

    // Tab to focus
    button.focus();
    expect(button).toHaveFocus();

    // Space or Enter to click
    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

**Visual regression tests:**
```typescript
import { test, expect } from '@playwright/test';

test('Button matches snapshot', async ({ page }) => {
  await page.goto('http://localhost:3000/components/button');

  // Default state
  await expect(page.locator('button')).toHaveScreenshot('button-default.png');

  // Hover state
  await page.locator('button').hover();
  await expect(page.locator('button')).toHaveScreenshot('button-hover.png');

  // Focus state
  await page.locator('button').focus();
  await expect(page.locator('button')).toHaveScreenshot('button-focus.png');
});
```

---

## Migration Strategy

### Phase 1: Parallel Implementation (Week 6)

**Keep existing custom components:**
- Don't replace existing components immediately
- Add Shadcn/ui components alongside
- New features use Shadcn/ui components

### Phase 2: Incremental Replacement (Week 7)

**Replace high-value components first:**
1. Forms (login, registration) → Shadcn/ui Form components
2. Modals (confirmation dialogs) → Shadcn/ui Dialog
3. Navigation (tabs, menus) → Shadcn/ui Tabs, NavigationMenu

### Phase 3: Complete Migration (Post-Week 7)

**Replace remaining custom components:**
- Week 8: Replace all buttons, inputs
- Week 9: Replace cards, badges
- Week 10: Delete old custom components

---

## Future Enhancements

**Post-Week 7:**

1. **Component Storybook**
   - Visual catalog of all installed components
   - Interactive prop exploration
   - Accessibility audit results visible

2. **Theme Presets**
   - Light mode (Apple-inspired)
   - Dark mode (Apple-inspired)
   - High contrast mode (accessibility)

3. **Component Generator**
   - CLI tool to scaffold new components based on Shadcn/ui patterns
   - Auto-generate test files
   - Auto-add to component inventory

4. **Update Automation**
   - Script to check for Shadcn/ui component updates
   - Automated diffing against local customizations
   - One-click update with merge conflict resolution

---

## References

**Primary Research:**
- See `RESEARCH-REFERENCES.md` - Phase 3 section
- See `PLANNING.md` - Week 6 (Phase 3) section
- See `IMPLEMENTATION.md` - Week 6 Day 1-2 setup steps

**Related ADRs:**
- ADR-005: Artifacts Sidebar Pattern (uses Sheet/Tabs components)
- ADR-007: Apple Minimalist Design System (visual customization approach)

**External Documentation:**
- Shadcn/ui: https://ui.shadcn.com/
- Radix UI: https://www.radix-ui.com/
- Tailwind CSS: https://tailwindcss.com/docs
- WAI-ARIA Patterns: https://www.w3.org/WAI/ARIA/apg/patterns/

---

**Last Updated:** 2025-10-21
**Status:** Accepted for Phase 3 implementation
**Review Date:** 2025-11-21 (after 1 month of usage)
