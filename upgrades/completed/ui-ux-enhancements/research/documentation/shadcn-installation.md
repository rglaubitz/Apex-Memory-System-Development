# Shadcn/ui Installation - Getting Started

**Purpose:** Installation and setup guide for Shadcn/ui
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Documentation)

**Primary Source:** https://ui.shadcn.com/docs/installation

**Related Documentation:**
- For component catalog → see `component-catalog.md`
- For customization → see `customization-guide.md`
- For Apex integration → see `apex-integration-strategy.md`

---

## What is Shadcn/ui?

**NOT a component library** - It's a collection of **copy-paste components** built with Radix UI + Tailwind CSS.

**Key Difference:**
- Traditional library: `npm install component-library` → locked into their updates
- Shadcn/ui: Copy components to your project → **full ownership and customization**

**Perfect for Apex:**
- ✅ Already using React 18 + TypeScript 5
- ✅ Already using Tailwind CSS 3.4.17
- ✅ Already using Radix UI components
- ✅ Zero additional learning curve

---

## Core Principles

### 1. Copy, Don't Install

```bash
# Traditional way
npm install component-library  # ❌ Wrong approach

# Shadcn/ui way
npx shadcn@latest add button  # ✅ Copies to components/ui/button.tsx
```

### 2. Full Ownership

- Components live in **your codebase** (`components/ui/`)
- Modify styling, behavior, props as needed
- No package version conflicts

### 3. Built on Radix UI

- Accessible by default (WCAG 2.1 compliant)
- Keyboard navigation baked in
- Screen reader friendly

---

## Installation

### 1. Initialize Shadcn/ui

```bash
cd apex-memory-system/frontend  # Navigate to Apex UI
npx shadcn@latest init
```

**Configuration prompts:**
```
Would you like to use TypeScript? › Yes
Which style would you like to use? › Default
Which color would you like to use as base color? › Slate
Where is your global CSS file? › src/index.css
Would you like to use CSS variables for colors? › Yes
Where is your tailwind.config.js located? › tailwind.config.js
Configure the import alias for components: › @/components
Configure the import alias for utils: › @/lib/utils
Are you using React Server Components? › No
```

### 2. What Gets Created

```
src/
├── components/
│   └── ui/                    # Components added here
│       └── (empty initially)
├── lib/
│   └── utils.ts               # Utility functions (cn, etc.)
└── index.css                  # Updated with CSS variables
```

### 3. Add Your First Component

```bash
npx shadcn@latest add button
```

**This creates:**
```typescript
// src/components/ui/button.tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "underline-offset-4 hover:underline text-primary",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

### 4. Use the Component

```tsx
import { Button } from '@/components/ui/button';

function MyComponent() {
  return (
    <div>
      <Button variant="default">Click me</Button>
      <Button variant="outline">Cancel</Button>
      <Button variant="destructive">Delete</Button>
    </div>
  );
}
```

---

## Essential Setup

### Update tsconfig.json

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Update vite.config.ts

```typescript
import path from "path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

---

## Adding Multiple Components

```bash
# Add multiple components at once
npx shadcn@latest add button input label dialog sheet

# Or add all components (not recommended initially)
npx shadcn@latest add --all
```

**Recommended Approach:** Add components as you need them.

---

## Dependencies

Shadcn/ui automatically installs required dependencies:

```json
{
  "dependencies": {
    "@radix-ui/react-*": "^1.x",  // Specific to components used
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  }
}
```

**Already in Apex:**
- ✅ React 18.3.1
- ✅ Tailwind CSS 3.4.17
- ✅ TypeScript 5.7.2
- ✅ Vite 6.0.6

---

## Verification

Test the installation:

```tsx
// src/App.tsx
import { Button } from '@/components/ui/button';

function App() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Shadcn/ui Test</h1>
      <div className="flex gap-2">
        <Button>Default</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="destructive">Destructive</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="link">Link</Button>
      </div>
    </div>
  );
}
```

**Expected result:** Buttons render with proper styling and hover states.

---

## Common Issues

### Issue 1: Import Alias Not Working

**Problem:** `Cannot find module '@/components/ui/button'`

**Solution:** Ensure `tsconfig.json` and `vite.config.ts` are configured correctly (see Essential Setup above).

### Issue 2: Styles Not Applied

**Problem:** Components render but look unstyled

**Solution:** Ensure Tailwind CSS is configured and `index.css` has been updated with CSS variables.

### Issue 3: Radix UI Conflicts

**Problem:** Multiple versions of Radix UI components

**Solution:** Check `package.json` for duplicate Radix packages, consolidate to single versions.

---

## Next Steps

1. **Add core components** - button, input, dialog, sheet
2. **Customize theme** - see `customization-guide.md`
3. **Integrate with Apex** - see `apex-integration-strategy.md`
4. **Explore catalog** - see `component-catalog.md`

---

## References

**Official Documentation:**
- Shadcn/ui: https://ui.shadcn.com/docs
- Installation Guide: https://ui.shadcn.com/docs/installation
- CLI Reference: https://ui.shadcn.com/docs/cli

**Dependencies:**
- Radix UI: https://www.radix-ui.com/
- Tailwind CSS: https://tailwindcss.com/
- CVA (Class Variance Authority): https://cva.style/

**Related Documentation:**
- Component catalog → `component-catalog.md`
- Customization guide → `customization-guide.md`
- Apex integration → `apex-integration-strategy.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Documentation)
