# ADR-007: Apple Minimalist Design System

**Status:** Accepted
**Date:** 2025-10-21
**Decision Makers:** Development Team
**Affected Components:** Frontend UI, Design System, Visual Identity

---

## Context

### Problem Statement

The Apex Memory System UI needs a cohesive design language that:

1. **Conveys Intelligence and Sophistication**
   - Professional aesthetic for enterprise users
   - Suggests AI/knowledge capabilities without being gimmicky
   - Trust-inspiring visual identity

2. **Prioritizes Content Over Chrome**
   - Information architecture clarity
   - Minimal visual distractions
   - Focus on user goals (finding knowledge, not navigating UI)

3. **Feels Responsive and Fast**
   - Smooth animations and transitions
   - Clear interaction feedback
   - Perceived performance (feels fast even when processing)

4. **Scales Across Use Cases**
   - Simple queries (search box + results)
   - Complex queries (multi-tool agent orchestration with sidebar)
   - Data exploration (graphs, tables, visualizations)

### Current State (Phase 2)

**Week 2-4 delivers basic UI with:**
- Standard Tailwind defaults (rounded corners, blue accents)
- No cohesive design language
- Generic SaaS aesthetic
- Inconsistent spacing and typography

**Feedback from stakeholders:**
- "Feels like every other SaaS tool"
- "Doesn't convey the intelligence of the system"
- "Too busy - want focus on content"

---

## Decision

**We will implement an Apple-inspired Minimalist Design System in Phase 3 (Week 6).**

### Design Philosophy

**Core Principles:**

**1. Content First**
- Typography is the primary design element
- Generous whitespace around content
- Subtle UI chrome (borders, backgrounds)
- User attention on conversation and results

**2. Monochrome Foundation**
- Black, white, grays as primary palette
- Color used sparingly for emphasis (blue for interactive, red for errors)
- High contrast for readability
- Professional, timeless aesthetic

**3. Typography-Driven Hierarchy**
- SF Pro / Inter font family
- Clear heading levels (6 levels with distinct sizes)
- Consistent line height (1.5 for body, 1.2 for headings)
- Tracking adjustments for readability

**4. Subtle Motion**
- Smooth ease-in-out transitions (150-300ms)
- Purposeful animations (not decorative)
- No bounces, spins, or flashy effects
- Physics-inspired easing (Apple's trademark feel)

**5. Considered Density**
- Not too tight (Bloomberg aesthetic) ❌
- Not too loose (Stripe aesthetic) ❌
- Just right (Apple aesthetic) ✅
- Responsive spacing (more generous on desktop)

---

## Research Support

### Tier 1 Sources

**Apple Human Interface Guidelines**
- **Source:** https://developer.apple.com/design/human-interface-guidelines/
- **Tier:** 1 (Official Apple Documentation)
- **Accessed:** 2025-10-21
- **Reference:** RESEARCH-REFERENCES.md (Phase 3 section)

**Key principles from Apple HIG:**
- **Clarity** - Text is legible at every size, icons are precise, adornments are subtle
- **Deference** - Fluid motion and crisp interface help focus on content
- **Depth** - Layers and realistic motion impart vitality

**SF Pro Font Family**
- **Source:** https://developer.apple.com/fonts/
- **Tier:** 1 (Official Apple Resource)
- **License:** Free for non-commercial use, requires license for commercial (we'll use Inter as alternative)

**Inter Font Family** (Alternative to SF Pro)
- **Source:** https://rsms.me/inter/
- **Tier:** 2 (Open Source - widely used)
- **License:** Open Font License (free for commercial use)
- **Why:** Designed for screen legibility, similar metrics to SF Pro

---

## Design System Specifications

### Typography Scale

```css
/* Font Family */
--font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-mono: "SF Mono", "Menlo", "Monaco", "Courier New", monospace;

/* Font Sizes (Type Scale) */
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */
--text-5xl: 3rem;        /* 48px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;

/* Line Heights */
--leading-tight: 1.2;    /* Headings */
--leading-normal: 1.5;   /* Body text */
--leading-relaxed: 1.75; /* Large body text */

/* Letter Spacing (Tracking) */
--tracking-tight: -0.02em;  /* Large headings */
--tracking-normal: 0;       /* Body text */
--tracking-wide: 0.02em;    /* Small text */
```

### Color Palette

```css
/* Monochrome Foundation */
--color-white: #FFFFFF;
--color-black: #000000;

/* Grays (Apple-inspired) */
--color-gray-50: #F9FAFB;   /* Lightest background */
--color-gray-100: #F3F4F6;  /* Light background */
--color-gray-200: #E5E7EB;  /* Border light */
--color-gray-300: #D1D5DB;  /* Border */
--color-gray-400: #9CA3AF;  /* Disabled text */
--color-gray-500: #6B7280;  /* Secondary text */
--color-gray-600: #4B5563;  /* Body text */
--color-gray-700: #374151;  /* Headings */
--color-gray-800: #1F2937;  /* Dark headings */
--color-gray-900: #111827;  /* Darkest text */

/* Accent Colors (Minimal Use) */
--color-blue: #007AFF;      /* Apple blue - interactive elements */
--color-blue-hover: #0051D5; /* Hover state */
--color-red: #FF3B30;       /* Errors */
--color-green: #34C759;     /* Success */
--color-yellow: #FFCC00;    /* Warnings */

/* Semantic Colors */
--color-background: var(--color-white);
--color-foreground: var(--color-gray-900);
--color-border: var(--color-gray-200);
--color-input: var(--color-gray-100);
--color-primary: var(--color-gray-900);
--color-secondary: var(--color-gray-600);
--color-accent: var(--color-blue);
```

### Spacing Scale

```css
/* Apple uses 8pt grid system */
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px - base unit */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

### Border Radius

```css
/* Subtle rounding (not too round) */
--radius-sm: 0.25rem;   /* 4px - inputs, buttons */
--radius-md: 0.5rem;    /* 8px - cards */
--radius-lg: 0.75rem;   /* 12px - modals */
--radius-xl: 1rem;      /* 16px - large cards */
--radius-full: 9999px;  /* Fully rounded (avatars) */
```

### Shadows

```css
/* Subtle, realistic shadows */
--shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
```

### Transitions

```css
/* Smooth, Apple-style easing */
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

/* Common easing functions */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);      /* Standard */
--ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Slight bounce */
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);   /* Fast start, slow end */
```

---

## Implementation Notes

### Tailwind Configuration

**Update `tailwind.config.js`:**
```javascript
const { fontFamily } = require('tailwindcss/defaultTheme');

module.exports = {
  darkMode: ['class'],
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      fontFamily: {
        sans: ['Inter', ...fontFamily.sans],
        mono: ['SF Mono', 'Menlo', 'Monaco', ...fontFamily.mono],
      },
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        'slide-in-from-right': {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'slide-out-to-right': {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.2s ease-out',
        'slide-in': 'slide-in-from-right 0.3s ease-out',
        'slide-out': 'slide-out-to-right 0.3s ease-in',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
```

### CSS Variables (`src/index.css`)

```css
@layer base {
  :root {
    /* Light mode (default) */
    --background: 0 0% 100%;         /* White */
    --foreground: 222 47% 11%;       /* Gray 900 */

    --card: 0 0% 100%;               /* White */
    --card-foreground: 222 47% 11%;  /* Gray 900 */

    --primary: 222 47% 11%;          /* Gray 900 */
    --primary-foreground: 0 0% 100%; /* White */

    --secondary: 215 16% 47%;        /* Gray 600 */
    --secondary-foreground: 0 0% 100%; /* White */

    --accent: 217 91% 60%;           /* Apple blue */
    --accent-foreground: 0 0% 100%;  /* White */

    --destructive: 0 84% 60%;        /* Apple red */
    --destructive-foreground: 0 0% 100%; /* White */

    --muted: 210 40% 96%;            /* Gray 100 */
    --muted-foreground: 215 16% 47%; /* Gray 600 */

    --border: 214 32% 91%;           /* Gray 200 */
    --input: 214 32% 91%;            /* Gray 200 */
    --ring: 217 91% 60%;             /* Apple blue */

    --radius: 0.5rem;                /* 8px */
  }

  .dark {
    /* Dark mode (optional, minimal differences) */
    --background: 222 47% 11%;       /* Gray 900 */
    --foreground: 0 0% 100%;         /* White */

    --card: 217 33% 17%;             /* Gray 800 */
    --card-foreground: 0 0% 100%;    /* White */

    --primary: 0 0% 100%;            /* White */
    --primary-foreground: 222 47% 11%; /* Gray 900 */

    --secondary: 215 16% 47%;        /* Gray 600 */
    --secondary-foreground: 0 0% 100%; /* White */

    --accent: 217 91% 60%;           /* Apple blue */
    --accent-foreground: 0 0% 100%;  /* White */

    --destructive: 0 84% 60%;        /* Apple red */
    --destructive-foreground: 0 0% 100%; /* White */

    --muted: 217 33% 17%;            /* Gray 800 */
    --muted-foreground: 215 16% 47%; /* Gray 600 */

    --border: 215 28% 17%;           /* Gray 700 */
    --input: 215 28% 17%;            /* Gray 700 */
    --ring: 217 91% 60%;             /* Apple blue */
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}
```

### Component Style Examples

**Button (Apple-inspired):**
```typescript
// src/components/ui/button.tsx
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg text-sm font-normal tracking-tight transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "underline-offset-4 hover:underline text-primary",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3",
        lg: "h-11 px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export { Button, buttonVariants };
```

**Input (Apple-inspired):**
```typescript
// src/components/ui/input.tsx
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
```

---

## Design Patterns

### Visual Hierarchy

**1. Clear Information Layers**
```
┌─────────────────────────────────────────┐
│ H1: Main Title (text-4xl, font-semibold)│  ← Largest, most prominent
│                                          │
│ H2: Section Title (text-2xl, font-medium)│ ← Clear hierarchy
│                                          │
│ Body: Regular text (text-base, font-normal) │ ← Readable body
│                                          │
│ Caption: Small text (text-sm, text-muted-foreground) │ ← Subtle details
└─────────────────────────────────────────┘
```

**2. Generous Whitespace**
```typescript
// Bad: Cramped spacing
<div className="p-2">
  <h1 className="mb-1">Title</h1>
  <p className="mb-1">Content</p>
</div>

// Good: Apple-style spacing
<div className="p-8">
  <h1 className="mb-6">Title</h1>
  <p className="mb-8">Content</p>
</div>
```

**3. Subtle Borders**
```typescript
// Bad: Heavy borders
<div className="border-2 border-black">...</div>

// Good: Subtle, Apple-style borders
<div className="border border-gray-200">...</div>
```

### Interactive States

**1. Focus States (Accessibility)**
```typescript
// All interactive elements must have visible focus
className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue focus-visible:ring-offset-2"
```

**2. Hover States (Desktop)**
```typescript
// Subtle hover effects (not jarring)
className="hover:bg-gray-100 transition-colors duration-200"
```

**3. Active States (Pressed)**
```typescript
// Slight darkening on press
className="active:scale-98 active:bg-gray-200"
```

---

## Alternatives Considered

### Alternative 1: Material Design 3

**Approach:** Google's latest design language

**Pros:**
- ✅ Comprehensive guidelines
- ✅ Colorful, expressive
- ✅ Good accessibility standards

**Cons:**
- ❌ Too colorful for professional/enterprise feel
- ❌ Rounded corners everywhere (not sophisticated)
- ❌ Conflicts with Apple aesthetic

**Decision:** Rejected - Too playful for enterprise intelligence platform

---

### Alternative 2: Fluent Design (Microsoft)

**Approach:** Microsoft's design language

**Pros:**
- ✅ Professional aesthetic
- ✅ Enterprise-focused
- ✅ Accessibility built-in

**Cons:**
- ❌ Acrylic effects feel dated
- ❌ Not as refined as Apple
- ❌ Requires specific Windows-style components

**Decision:** Rejected - Not as timeless as Apple aesthetic

---

### Alternative 3: Carbon Design (IBM)

**Approach:** IBM's enterprise design system

**Pros:**
- ✅ Extremely professional
- ✅ Data-dense layouts
- ✅ Enterprise credibility

**Cons:**
- ❌ Too dense (Bloomberg-style)
- ❌ Dark, heavy feel
- ❌ Not modern enough

**Decision:** Rejected - Too data-dense, not modern enough

---

### Alternative 4: Custom Design Language

**Approach:** Create unique, custom design system

**Pros:**
- ✅ Complete uniqueness
- ✅ Perfect brand alignment
- ✅ No design debt

**Cons:**
- ❌ 2-3 months design work (vs. 1 week with Apple principles)
- ❌ Requires professional designer hire
- ❌ Reinventing solved problems
- ❌ Testing and iteration burden

**Decision:** Rejected - Not worth 2-3 months delay for marginal differentiation

---

## Success Metrics

**User perception (survey after Week 7):**
- ✅ 80%+ users rate UI as "professional" or "sophisticated"
- ✅ 70%+ users rate UI as "fast" or "responsive" (perceived performance)
- ✅ 60%+ users notice "Apple-like" aesthetic

**Quantitative metrics:**
- ✅ Consistent spacing (100% of components use 8pt grid)
- ✅ Typography hierarchy (6 distinct levels, all used correctly)
- ✅ Color usage (<5 colors beyond monochrome)
- ✅ Border radius consistency (all use defined --radius-* variables)

**Accessibility:**
- ✅ Focus states visible on all interactive elements
- ✅ Color contrast ratio ≥4.5:1 (WCAG AA)
- ✅ Touch targets ≥44x44px (mobile)

---

## Implementation Checklist

**Week 6, Day 3-4: Design System Setup**

- [ ] Install Inter font from Google Fonts
- [ ] Configure Tailwind with Apple-inspired colors
- [ ] Set up CSS variables for light/dark mode
- [ ] Create design system documentation page

**Week 6, Day 5: Component Styling**

- [ ] Update all Shadcn/ui components with Apple styling
- [ ] Ensure consistent spacing (8pt grid)
- [ ] Apply typography hierarchy to all text
- [ ] Test focus states on all interactive elements

**Week 7: Refinement**

- [ ] Visual QA review (spacing, typography, colors)
- [ ] Accessibility audit (axe-core tests passing)
- [ ] User feedback gathering
- [ ] Iterate based on feedback

---

## References

**Primary Research:**
- See `RESEARCH-REFERENCES.md` - Phase 3 section
- See `PLANNING.md` - Week 6 (Phase 3) section
- See `IMPLEMENTATION.md` - Week 6 Day 3-5 styling steps

**Related ADRs:**
- ADR-005: Artifacts Sidebar Pattern (visual hierarchy principles)
- ADR-006: Shadcn/ui Component Library (component styling approach)

**External Documentation:**
- Apple HIG: https://developer.apple.com/design/human-interface-guidelines/
- Inter Font: https://rsms.me/inter/
- SF Pro Font: https://developer.apple.com/fonts/
- Tailwind CSS: https://tailwindcss.com/docs

---

**Last Updated:** 2025-10-21
**Status:** Accepted for Phase 3 implementation
**Review Date:** 2025-11-21 (after 1 month of usage)
