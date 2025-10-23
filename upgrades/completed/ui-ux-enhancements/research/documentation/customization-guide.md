# Shadcn/ui Customization Guide - Theming & Styling

**Purpose:** Customizing Shadcn/ui for Apex design system
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Documentation)

**Related Documentation:**
- For installation → see `shadcn-installation.md`
- For components → see `component-catalog.md`
- For Apex integration → see `apex-integration-strategy.md`

---

## Overview

Since Shadcn/ui components are **copy-pasted into your project**, you have **full control** over styling and behavior.

**Two customization approaches:**
1. **CSS Variables** - Theme-level changes (colors, spacing)
2. **Component Modification** - Direct component edits

---

## Theme Customization with CSS Variables

### Colors

Edit `src/index.css`:

```css
:root {
  --background: 0 0% 0%;          /* Black background */
  --foreground: 0 0% 100%;        /* White text */

  --primary: 270 100% 70%;        /* Purple (#a855f7) */
  --primary-foreground: 0 0% 0%;

  --secondary: 240 5% 20%;        /* Dark gray */
  --secondary-foreground: 0 0% 100%;

  --muted: 240 5% 15%;
  --muted-foreground: 240 5% 60%;

  --accent: 240 5% 20%;
  --accent-foreground: 0 0% 100%;

  --destructive: 0 84% 60%;       /* Red for errors */
  --destructive-foreground: 0 0% 100%;

  --border: 240 5% 20%;
  --input: 240 5% 20%;
  --ring: 270 100% 70%;           /* Purple focus ring */
}
```

**Effect:** All components automatically use new colors.

### Spacing & Typography

```css
:root {
  --radius: 0.5rem;  /* Border radius for all components */
}

body {
  font-family: 'Inter', sans-serif;  /* Custom font */
}
```

---

## Component-Level Customization

### Example: Customize Button

Edit `src/components/ui/button.tsx`:

```typescript
// Add new variant
const buttonVariants = cva(
  // ... base styles
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        // Add custom Apex variant
        apex: "bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700",
      },
      size: {
        default: "h-10 py-2 px-4",
        // Add extra small size
        xs: "h-8 px-2 text-xs rounded",
      },
    },
  }
)
```

**Usage:**
```tsx
<Button variant="apex">Apex Style</Button>
<Button size="xs">Extra Small</Button>
```

---

## Dark Mode

### Setup

Shadcn/ui uses CSS variables for dark mode:

```css
.dark {
  --background: 0 0% 10%;
  --foreground: 0 0% 100%;
  /* ... other dark mode values */
}
```

### Toggle Implementation

```tsx
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
    </Button>
  )
}
```

---

## Animation Customization

### Framer Motion Integration

```tsx
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"

function AnimatedButton() {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <Button>Hover Me</Button>
    </motion.div>
  )
}
```

---

## References

**Official Documentation:**
- Theming: https://ui.shadcn.com/docs/theming
- Dark Mode: https://ui.shadcn.com/docs/dark-mode

**Related Documentation:**
- Installation → `shadcn-installation.md`
- Component catalog → `component-catalog.md`
- Apex integration → `apex-integration-strategy.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Documentation)
