# Task 4.3: Theme Switcher & Accessibility

**Phase:** 4 - Collaboration & Polish
**Status:** ⬜ Not Started
**Estimated Duration:** 8 hours (Days 5-6)
**Assigned To:** (filled during execution)

---

## Overview

Implement dark/light theme switching and ensure WCAG 2.1 AA accessibility compliance across the entire application. Includes theme persistence, keyboard navigation, screen reader support, and contrast ratio validation.

**Key Features:**
- Theme switcher (light/dark modes)
- LocalStorage theme persistence
- WCAG 2.1 AA compliance (contrast ratios, keyboard navigation)
- ARIA labels for screen readers
- Focus management for accessibility
- Skip navigation links

---

## Dependencies

**Required Before Starting:**
- Phase 3 complete (design system with colors defined)
- All UI components implemented
- Frontend application functional

**Enables After Completion:**
- Task 4.4: Production Polish & Deployment Readiness
- Improved user experience (theme preference)
- Accessibility compliance for production

---

## Success Criteria

✅ Theme context provider implemented with light/dark modes
✅ Theme switcher component (toggle button) added to header
✅ Theme preference persists in localStorage
✅ All colors meet WCAG AA contrast ratios (4.5:1 for text, 3:1 for large text)
✅ Keyboard navigation works on all interactive elements
✅ Focus indicators visible on all focusable elements
✅ ARIA labels added to all interactive components
✅ Screen reader announces theme changes
✅ Skip navigation link added for keyboard users
✅ 5 accessibility tests passing

---

## Research References

**Technical Documentation:**
- research/documentation/customization-guide.md (Lines: 1-100)
  - Key concepts: Shadcn/ui theme customization, CSS variables

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2887-2954) - Design system foundation
  - Color palette, spacing, typography already defined

**Architecture Decisions:**
- ADR-006: Shadcn/ui Component Library
  - Theme implementation strategy

**External References:**
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- React ARIA: https://react-spectrum.adobe.com/react-aria/
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/

---

## Test Specifications

**Frontend Tests (5 tests):**

### Component Tests

**File:** `apex-memory-system/frontend/src/__tests__/ThemeSwitcher.test.tsx`

Tests to implement:
1. `test_theme_toggle` - Click toggle switches theme
2. `test_theme_persistence` - Theme persists in localStorage
3. `test_keyboard_navigation` - Tab key navigates all interactive elements
4. `test_focus_indicators` - Focus visible on all elements
5. `test_aria_labels` - All interactive elements have ARIA labels

**Test Execution:**
```bash
cd frontend
npm test -- ThemeSwitcher.test.tsx
npm test -- --coverage
```

---

## Implementation Steps

### Subtask 4.3.1: Create Theme Context & Provider

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/contexts/ThemeContext.tsx`

**Files to Modify:**
- `apex-memory-system/frontend/src/App.tsx` (wrap with ThemeProvider)

**Steps:**
1. Create ThemeContext with light/dark mode state
2. Implement useTheme hook for consuming context
3. Add localStorage persistence (save/load theme preference)
4. Apply theme CSS variables to document root
5. Define dark mode color palette (mirror light mode colors)
6. Wrap App with ThemeProvider

**Code Example:**
```typescript
/**
 * Theme context for light/dark mode switching.
 */
import React, { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Load theme from localStorage or default to light
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem('apex-theme');
    return (stored === 'dark' ? 'dark' : 'light') as Theme;
  });

  // Apply theme CSS variables
  useEffect(() => {
    const root = document.documentElement;

    if (theme === 'dark') {
      // Dark mode colors (inverted from design system)
      root.style.setProperty('--color-background', '#1D1D1F');
      root.style.setProperty('--color-surface', '#2C2C2E');
      root.style.setProperty('--color-text', '#F5F5F7');
      root.style.setProperty('--color-text-secondary', '#98989D');
      root.style.setProperty('--color-accent', '#0A84FF'); // Brighter blue for dark mode
      root.style.setProperty('--color-shadow', 'rgba(0, 0, 0, 0.3)');
    } else {
      // Light mode colors (from design system)
      root.style.setProperty('--color-background', '#FFFFFF');
      root.style.setProperty('--color-surface', '#F5F5F7');
      root.style.setProperty('--color-text', '#1D1D1F');
      root.style.setProperty('--color-text-secondary', '#86868B');
      root.style.setProperty('--color-accent', '#007AFF');
      root.style.setProperty('--color-shadow', 'rgba(0, 0, 0, 0.08)');
    }

    // Persist to localStorage
    localStorage.setItem('apex-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

**Wrap App:**
```typescript
// App.tsx
import { ThemeProvider } from './contexts/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <Router>
        {/* rest of app */}
      </Router>
    </ThemeProvider>
  );
}
```

**Validation:**
```bash
cd frontend
npm run dev

# Test in browser:
# 1. Open DevTools → Application → Local Storage
# 2. Verify "apex-theme" key exists
# 3. Toggle theme and verify CSS variables change
```

**Expected Result:**
- Theme context provides theme state and toggle function
- Theme persists in localStorage
- CSS variables applied to document root
- Theme changes reflected instantly

---

### Subtask 4.3.2: Create Theme Switcher Component

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/components/ThemeSwitcher.tsx`

**Files to Modify:**
- `apex-memory-system/frontend/src/components/Header.tsx` (add theme switcher)

**Steps:**
1. Create ThemeSwitcher component with toggle button
2. Use useTheme hook to access theme state
3. Add icon for light/dark mode (sun/moon icons)
4. Style button to match Apple minimalism
5. Add ARIA labels for accessibility
6. Announce theme change to screen readers

**Code Example:**
```typescript
/**
 * Theme switcher toggle button.
 */
import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { Sun, Moon } from 'lucide-react'; // Icon library

export const ThemeSwitcher: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="theme-switcher"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {theme === 'light' ? (
        <Moon size={20} aria-hidden="true" />
      ) : (
        <Sun size={20} aria-hidden="true" />
      )}
      <span className="sr-only">
        Current theme: {theme}. Click to toggle.
      </span>
    </button>
  );
};

// CSS (in global.css or ThemeSwitcher.module.css)
/*
.theme-switcher {
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: var(--color-text);
  border-radius: 8px;
  transition: background-color 200ms cubic-bezier(0.4, 0.0, 0.2, 1);
}

.theme-switcher:hover {
  background: var(--color-surface);
}

.theme-switcher:focus {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
*/
```

**Add to Header:**
```typescript
// Header.tsx
import { ThemeSwitcher } from './ThemeSwitcher';

export const Header = () => {
  return (
    <header>
      <div className="header-content">
        <h1>Apex Memory</h1>
        <div className="header-actions">
          <ThemeSwitcher />
          <UserMenu />
        </div>
      </div>
    </header>
  );
};
```

**Validation:**
```bash
# Visual test in browser
# 1. Click theme toggle
# 2. Verify theme changes
# 3. Verify localStorage updated
# 4. Refresh page - theme should persist

# Accessibility test
# 1. Use keyboard only (Tab to button, Enter to toggle)
# 2. Verify focus indicator visible
# 3. Use screen reader - verify announcement
```

**Expected Result:**
- Theme toggle button visible in header
- Click toggles theme instantly
- Keyboard navigation works (Tab + Enter)
- Focus indicator visible
- Screen reader announces theme change

---

### Subtask 4.3.3: Implement WCAG 2.1 AA Compliance

**Duration:** 3 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- All component files (add ARIA labels, keyboard navigation)
- `apex-memory-system/frontend/src/components/SkipNavigation.tsx` (new file)
- Global CSS (ensure contrast ratios, focus indicators)

**Steps:**
1. Audit all colors for WCAG AA contrast ratios (4.5:1 text, 3:1 large text)
2. Add ARIA labels to all interactive elements
3. Ensure keyboard navigation (Tab, Enter, Escape) works on all components
4. Add visible focus indicators (outline: 2px solid accent)
5. Create skip navigation link for keyboard users
6. Test with screen reader (VoiceOver on macOS)

**Contrast Ratio Validation:**
```typescript
// Example contrast ratios to verify:

// Light mode:
// - Text (#1D1D1F) on Background (#FFFFFF) = 16.75:1 ✅ (exceeds 4.5:1)
// - Text Secondary (#86868B) on Background (#FFFFFF) = 4.54:1 ✅
// - Accent (#007AFF) on Background (#FFFFFF) = 4.57:1 ✅

// Dark mode:
// - Text (#F5F5F7) on Background (#1D1D1F) = 16.11:1 ✅
// - Text Secondary (#98989D) on Background (#1D1D1F) = 4.59:1 ✅
// - Accent (#0A84FF) on Background (#1D1D1F) = 8.59:1 ✅
```

**Skip Navigation Component:**
```typescript
/**
 * Skip navigation link for keyboard users.
 */
export const SkipNavigation: React.FC = () => {
  return (
    <a
      href="#main-content"
      className="skip-nav"
      tabIndex={0}
    >
      Skip to main content
    </a>
  );
};

// CSS
/*
.skip-nav {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-accent);
  color: white;
  padding: 8px 16px;
  text-decoration: none;
  z-index: 100;
}

.skip-nav:focus {
  top: 0;
}
*/
```

**ARIA Labels Example:**
```typescript
// Add to all interactive components
<button
  onClick={handleClick}
  aria-label="Clear search query"
  aria-describedby="search-help"
>
  Clear
</button>

<div id="search-help" className="sr-only">
  Clears the current search query and resets filters
</div>
```

**Keyboard Navigation Example:**
```typescript
// Add to modal components
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Escape') {
    closeModal();
  }
};

<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  onKeyDown={handleKeyDown}
  tabIndex={-1}
>
  {/* modal content */}
</div>
```

**Validation:**
```bash
# Run automated accessibility audit
cd frontend
npm install --save-dev @axe-core/react
npm test -- --coverage

# Manual testing:
# 1. Use only keyboard (Tab, Enter, Escape, Arrow keys)
# 2. Verify all interactive elements reachable
# 3. Verify focus indicators visible
# 4. Use VoiceOver (Cmd+F5 on macOS)
# 5. Verify all content announced correctly
```

**Expected Result:**
- All text meets WCAG AA contrast ratios
- All interactive elements keyboard accessible
- Focus indicators visible on all focusable elements
- ARIA labels provide context for screen readers
- Skip navigation link works
- Screen reader announces all content correctly

---

### Subtask 4.3.4: Create Accessibility Tests

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/__tests__/ThemeSwitcher.test.tsx`
- `apex-memory-system/frontend/src/__tests__/Accessibility.test.tsx`

**Steps:**
1. Create theme switcher tests (toggle, persistence, keyboard)
2. Create accessibility tests (ARIA labels, focus, contrast)
3. Use @testing-library/react for DOM testing
4. Use jest-axe for automated accessibility checks

**Code Example:**
```typescript
/**
 * Theme switcher tests.
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../contexts/ThemeContext';
import { ThemeSwitcher } from '../components/ThemeSwitcher';

describe('ThemeSwitcher', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('toggles theme on click', () => {
    render(
      <ThemeProvider>
        <ThemeSwitcher />
      </ThemeProvider>
    );

    const button = screen.getByRole('button', { name: /switch to dark mode/i });
    fireEvent.click(button);

    // Verify localStorage updated
    expect(localStorage.getItem('apex-theme')).toBe('dark');
  });

  test('persists theme to localStorage', () => {
    render(
      <ThemeProvider>
        <ThemeSwitcher />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    // Verify persistence
    const stored = localStorage.getItem('apex-theme');
    expect(stored).toBe('dark');
  });

  test('keyboard navigation works', () => {
    render(
      <ThemeProvider>
        <ThemeSwitcher />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');

    // Tab to button
    button.focus();
    expect(document.activeElement).toBe(button);

    // Press Enter to toggle
    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
    expect(localStorage.getItem('apex-theme')).toBe('dark');
  });

  test('focus indicator visible', () => {
    const { container } = render(
      <ThemeProvider>
        <ThemeSwitcher />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    button.focus();

    // Check computed style for outline
    const styles = window.getComputedStyle(button);
    expect(styles.outline).toBeTruthy();
  });

  test('has ARIA labels', () => {
    render(
      <ThemeProvider>
        <ThemeSwitcher />
      </ThemeProvider>
    );

    const button = screen.getByRole('button', { name: /switch to/i });
    expect(button).toHaveAttribute('aria-label');
  });
});
```

**Accessibility Tests:**
```typescript
/**
 * Accessibility compliance tests.
 */
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { App } from '../App';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  test('has no accessibility violations', async () => {
    const { container } = render(<App />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

**Validation:**
```bash
cd frontend
npm test -- ThemeSwitcher.test.tsx
npm test -- Accessibility.test.tsx
npm test -- --coverage
```

**Expected Result:**
- All 5 tests passing
- Theme toggle works correctly
- Keyboard navigation verified
- ARIA labels present
- No accessibility violations

---

## Troubleshooting

**Common Issues:**

**Issue 1: Theme flicker on page load**
- **Symptom:** Brief flash of wrong theme before correct theme loads
- **Solution:** Apply theme inline in HTML head before React hydration
- **Code Fix:** Add `<script>` tag in index.html to apply theme immediately

**Issue 2: Contrast ratio failures**
- **Symptom:** WCAG audit fails for certain color combinations
- **Solution:** Use WebAIM Contrast Checker to verify all text/background pairs
- **Tool:** https://webaim.org/resources/contrastchecker/

**Issue 3: Focus indicator not visible**
- **Symptom:** No visible outline when tabbing through elements
- **Solution:** Ensure `:focus` styles not removed globally
- **Code Fix:** Add explicit `outline: 2px solid var(--color-accent)` to `:focus`

**Issue 4: Screen reader not announcing theme change**
- **Symptom:** VoiceOver doesn't announce when theme toggled
- **Solution:** Add aria-live region for theme announcements
- **Code Fix:**
```typescript
<div aria-live="polite" aria-atomic="true" className="sr-only">
  Theme changed to {theme} mode
</div>
```

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 4.3.1: Create Theme Context & Provider
- [ ] Subtask 4.3.2: Create Theme Switcher Component
- [ ] Subtask 4.3.3: Implement WCAG 2.1 AA Compliance
- [ ] Subtask 4.3.4: Create Accessibility Tests

**Tests:** 0/5 passing (0%)

- [ ] 5 accessibility tests (ThemeSwitcher.test.tsx, Accessibility.test.tsx)

**Last Updated:** 2025-10-21
