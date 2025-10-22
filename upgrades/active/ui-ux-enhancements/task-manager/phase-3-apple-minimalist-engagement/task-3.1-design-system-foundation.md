# Task 3.1: Design System Foundation

**Phase:** 3 - Apple Minimalist Engagement Layer
**Status:** ⬜ Not Started
**Estimated Duration:** 4 hours (Day 1)
**Assigned To:** (filled during execution)

---

## Overview

Establish Apple-inspired minimalist design system with 90% monochrome palette, generous spacing, and subtle animation principles. Creates single source of truth for colors, typography, spacing, and animation constants.

---

## Dependencies

**Required Before Starting:**
- Task 1.2: Frontend Authentication UI (requires UI component library setup)
- Phase 2 complete (existing frontend structure)

**Enables After Completion:**
- Task 3.2: Backend Engagement APIs
- Task 3.3: Minimal Gamification Components
- Task 3.4: Integrated Recommendations
- Task 3.5: Hidden Dashboard & Briefings

---

## Success Criteria

✅ design-system.ts file created with all constants
✅ Color palette: 90% monochrome + 10% accent (Apple blue)
✅ Typography using -apple-system font stack
✅ Spacing scale (8px base: xs=8, sm=16, md=24, lg=32, xl=48, xxl=64)
✅ Animation duration (fast=200ms, normal=300ms) with cubic-bezier easing
✅ Shadow system (subtle, card, elevated) with low opacity
✅ Glass morphism variables defined
✅ No tests required (constants file)

---

## Research References

**Technical Documentation:**
- research/documentation/apex-integration-strategy.md (Lines: 1-149)
  - Key concepts: Apple minimalist design, Shadcn/ui integration, gradual adoption

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2887-2954)
  - Complete design-system.ts implementation with Apple philosophy

---

## Test Specifications

**No tests required** - This is a constants/configuration file with no runtime logic to test.

**Validation:**
- TypeScript compilation passes
- File exports all constants successfully
- Can be imported in other components

---

## Implementation Steps

### Subtask 3.1.1: Create Design System File Structure

**Duration:** 0.5 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/styles/design-system.ts`

**Steps:**
1. Create styles directory if not exists
2. Create design-system.ts file
3. Add TypeScript module header with Apple philosophy comment
4. Export all constants as named exports
5. Ensure no default export (explicit imports encouraged)

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2893-2953 for complete code
/**
 * Apex Memory - Apple Minimalist Design System
 *
 * Philosophy: "Sleek, simple, gorgeous, expensive-looking, not busy"
 * Inspiration: Steve Jobs era Apple (2007-2014)
 */

export const colors = {
  // Primary palette (90% of UI)
  background: '#FFFFFF',
  surface: '#F5F5F7',      // Apple gray
  text: '#1D1D1F',         // Almost black
  textSecondary: '#86868B', // System gray

  // Accent (10% of UI)
  accent: '#007AFF',        // Apple blue

  // Depth & Glass
  shadow: 'rgba(0, 0, 0, 0.08)',
  glass: 'rgba(255, 255, 255, 0.8)',
  glassDark: 'rgba(0, 0, 0, 0.05)',
};
```

**Validation:**
```bash
# Check TypeScript compilation
cd frontend
npm run type-check

# Verify exports work
npm run dev
# Check browser console for import errors
```

**Expected Result:**
- File created successfully
- TypeScript compiles without errors
- All constants properly typed

---

### Subtask 3.1.2: Define Color Palette

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/styles/design-system.ts` (add color constants)

**Steps:**
1. Define primary monochrome palette (background, surface, text)
2. Add Apple blue accent (#007AFF)
3. Define shadow colors (rgba with low opacity ~0.08)
4. Add glass morphism variables
5. Document 90/10 rule (90% monochrome, 10% accent)
6. Ensure contrast ratios meet WCAG AA standards

**Code Example:**
```typescript
export const colors = {
  // Primary palette (90% of UI)
  background: '#FFFFFF',
  surface: '#F5F5F7',      // Apple gray (matches Apple.com)
  text: '#1D1D1F',         // Almost black (4.5:1 contrast on white)
  textSecondary: '#86868B', // System gray (3:1 contrast on white)

  // Accent (10% of UI) - Used sparingly
  accent: '#007AFF',        // Apple blue (timeline accent, links, active states)

  // Depth & Glass
  shadow: 'rgba(0, 0, 0, 0.08)', // Subtle shadow (Apple standard)
  glass: 'rgba(255, 255, 255, 0.8)', // Glass background
  glassDark: 'rgba(0, 0, 0, 0.05)', // Glass overlay
};
```

**Validation:**
```bash
# Visual test: Create test component using colors
# Verify 90% monochrome, 10% accent visually
```

**Expected Result:**
- 90% of color usage is grayscale
- Single accent color (blue) used sparingly
- All contrast ratios WCAG AA compliant
- Matches Apple.com aesthetic

---

### Subtask 3.1.3: Define Typography Scale

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/styles/design-system.ts` (add typography)

**Steps:**
1. Define fontFamily with -apple-system stack
2. Create typography scale (display, headline, body, caption)
3. Define font sizes, weights, line heights
4. Document usage guidelines
5. Ensure SF Pro loaded on macOS, fallback to Inter

**Code Example:**
```typescript
export const typography = {
  fontFamily: {
    primary: '-apple-system, BlinkMacSystemFont, "SF Pro", "Inter", sans-serif',
    mono: 'SF Mono, Monaco, "Courier New", monospace',
  },

  sizes: {
    display: { size: 32, weight: 600, lineHeight: 1.2 },  // Hero headlines
    headline: { size: 24, weight: 600, lineHeight: 1.3 }, // Section titles
    body: { size: 16, weight: 400, lineHeight: 1.6 },     // Main text
    caption: { size: 14, weight: 400, lineHeight: 1.5 },  // Secondary text
  },
};
```

**Validation:**
```bash
# Visual test: Render all typography sizes
# Verify SF Pro loads on macOS
# Test Inter fallback on non-macOS systems
```

**Expected Result:**
- SF Pro font loads on macOS
- Inter fallback works on other systems
- Typography scale provides 4 clear size options
- Line heights ensure readability

---

### Subtask 3.1.4: Define Spacing, Animation, and Shadows

**Duration:** 1.5 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/styles/design-system.ts` (add spacing, animation, shadows)

**Steps:**
1. Define spacing scale (8px base: xs through xxl)
2. Create animation durations (fast, normal)
3. Define cubic-bezier easing (Apple standard)
4. Create shadow system (subtle, card, elevated)
5. Document when to use each spacing/shadow level
6. Export all constants

**Code Example:**
```typescript
export const spacing = {
  xs: 8,   // Tight spacing (icon padding)
  sm: 16,  // Standard spacing (card padding)
  md: 24,  // Medium spacing (section gaps)
  lg: 32,  // Large spacing (component gaps)
  xl: 48,  // Extra large (page sections)
  xxl: 64, // Generous (dashboard, hero sections)
};

export const animation = {
  // Subtle animations only (fade, slide) - NO bounce/elastic
  duration: {
    fast: 200,   // Quick transitions (hover states)
    normal: 300, // Standard (modals, sheets)
  },
  easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)', // Apple standard easing
};

export const shadows = {
  subtle: `0 1px 3px ${colors.shadow}`,      // Subtle elevation (cards)
  card: `0 4px 6px ${colors.shadow}`,        // Card elevation
  elevated: `0 10px 20px ${colors.shadow}`,  // Modal elevation
};
```

**Validation:**
```bash
# TypeScript compilation
npm run type-check

# Test import in component
# import { spacing, animation, shadows } from '@/styles/design-system';
```

**Expected Result:**
- 8px-based spacing scale for consistency
- 200-300ms animation durations (Apple standard)
- Subtle shadows (no heavy drop shadows)
- All constants exported and importable

---

## Troubleshooting

**Common Issues:**

**Issue 1: TypeScript errors on import**
- See TROUBLESHOOTING.md:Lines 500-525
- Solution: Ensure path alias configured in tsconfig.json (`"@/*": ["./src/*"]`)

**Issue 2: Fonts not loading**
- See TROUBLESHOOTING.md:Lines 550-575
- Solution: -apple-system loads automatically on macOS, Inter requires CDN or npm package

**Issue 3: Colors not matching Apple.com**
- See TROUBLESHOOTING.md:Lines 600-625
- Solution: Use browser inspector on Apple.com to verify exact hex values (#F5F5F7, #007AFF)

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 3.1.1: Create Design System File Structure
- [ ] Subtask 3.1.2: Define Color Palette
- [ ] Subtask 3.1.3: Define Typography Scale
- [ ] Subtask 3.1.4: Define Spacing, Animation, and Shadows

**Tests:** N/A (no tests required for constants file)

**Last Updated:** 2025-10-21
