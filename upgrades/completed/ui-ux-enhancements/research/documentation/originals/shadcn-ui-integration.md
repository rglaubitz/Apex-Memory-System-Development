# Shadcn/ui Integration Guide - Component Library for Apex UI

**Primary Source:** https://ui.shadcn.com/docs
**Date Accessed:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Documentation)

---

## Executive Summary

**What is Shadcn/ui?**
Shadcn/ui is **NOT a traditional component library** you install via npm. Instead, it's a **collection of copy-paste components** built on Radix UI primitives and styled with Tailwind CSS that you **own and modify directly** in your codebase.

**Philosophy:** "How you build your component library" - not "What components you install"

**Key Differentiator:**
- **Traditional Library:** `npm install react-component-lib` → Use as black box
- **Shadcn/ui:** `npx shadcn@latest add button` → Copy source code into your project → Modify freely

**For Apex Memory System:**
Perfect match! We're already using **Radix UI + Tailwind CSS** in the existing UI. Shadcn/ui provides pre-styled, production-ready versions of Radix components that we can customize for the Apex design system.

---

## Part 1: Core Principles

### 1. Open Code

You receive the **actual component source code**, not compiled packages. Full transparency and control.

```bash
# Installing button component
npx shadcn@latest add button

# Creates:
# /components/ui/button.tsx (source code you own)
```

**Result:**
```tsx
// YOU OWN THIS FILE - Modify freely!
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center...",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        // ADD YOUR OWN VARIANTS HERE ↓
        apex: "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600..."
      }
    }
  }
)

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export function Button({ className, variant, ...props }: ButtonProps) {
  // Modify implementation as needed
  return <button className={cn(buttonVariants({ variant, className }))} {...props} />
}
```

### 2. Composition

All components use **standardized, predictable interfaces**. Learn once, apply everywhere.

```tsx
// Dialog component
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    {/* Content */}
    <DialogFooter>
      <Button>Close</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>

// Sheet component (same pattern)
<Sheet>
  <SheetTrigger>Open</SheetTrigger>
  <SheetContent>
    <SheetHeader>
      <SheetTitle>Title</SheetTitle>
      <SheetDescription>Description</SheetDescription>
    </SheetHeader>
    {/* Content */}
    <SheetFooter>
      <Button>Close</Button>
    </SheetFooter>
  </SheetContent>
</Sheet>
```

### 3. Beautiful Defaults

Components come **pre-styled** with a modern design system, but every style is customizable via Tailwind classes.

**Default:**
```tsx
<Button>Click me</Button>
```

**Custom:**
```tsx
<Button className="bg-purple-500 hover:bg-purple-600 shadow-lg shadow-purple-500/50">
  Apex Style
</Button>
```

### 4. AI-Ready

Open code structure allows AI models (like Claude!) to:
- Read component implementations
- Suggest improvements
- Generate new variants
- Create custom components following patterns

### 5. Flat Distribution

Components are **flat files** in your project, not nested dependencies. Easy to:
- Share components across projects
- Create internal component libraries
- Maintain consistency in monorepos

---

## Part 2: Installation & Setup

### Step 1: Initialize Shadcn/ui in Project

```bash
# Navigate to frontend directory
cd apex-memory-system/src/apex_memory/frontend

# Initialize shadcn/ui (creates components.json config)
npx shadcn@latest init
```

**Interactive Prompts:**
```
✔ Would you like to use TypeScript? … Yes
✔ Which style would you like to use? › Default
✔ Which color would you like to use as base color? › Neutral
✔ Where is your global CSS file? › src/index.css
✔ Would you like to use CSS variables for colors? … Yes
✔ Are you using a custom tailwind prefix? › No
✔ Where is your tailwind.config.js located? › tailwind.config.js
✔ Configure the import alias for components: › @/components
✔ Configure the import alias for utils: › @/lib/utils
✔ Are you using React Server Components? › No
```

**Creates `components.json`:**
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

### Step 2: Add Components

```bash
# Add individual components
npx shadcn@latest add button
npx shadcn@latest add dialog
npx shadcn@latest add input
npx shadcn@latest add popover
npx shadcn@latest add tabs

# Add multiple at once
npx shadcn@latest add button dialog input popover tabs

# Add all components (not recommended - adds 80+ components)
npx shadcn@latest add --all
```

**Created Files:**
```
src/
├── components/
│   └── ui/
│       ├── button.tsx
│       ├── dialog.tsx
│       ├── input.tsx
│       ├── popover.tsx
│       └── tabs.tsx
└── lib/
    └── utils.ts  (helper functions)
```

### Step 3: Import and Use

```tsx
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';

function MyComponent() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <p>Dialog content here</p>
      </DialogContent>
    </Dialog>
  );
}
```

---

## Part 3: Core Components for Apex

### Recommended Components to Add

**Layout & Structure:**
- `card` - Content containers
- `separator` - Dividers
- `scroll-area` - Custom scrollbars
- `sidebar` - Navigation sidebars

**Overlays & Dialogs:**
- `dialog` - Modal dialogs
- `sheet` - Slide-out panels (perfect for Artifacts sidebar!)
- `popover` - Floating content
- `tooltip` - Hover information
- `drawer` - Bottom drawer (mobile)

**Navigation:**
- `tabs` - Tab navigation
- `navigation-menu` - Complex navigation
- `breadcrumb` - Breadcrumb trails

**Forms & Inputs:**
- `button` - Buttons with variants
- `input` - Text inputs
- `textarea` - Multi-line text
- `select` - Dropdown selects
- `checkbox` - Checkboxes
- `radio-group` - Radio buttons
- `switch` - Toggle switches
- `slider` - Range sliders
- `form` - Form composition (with React Hook Form)

**Data Display:**
- `table` - Tables
- `badge` - Labels and tags
- `avatar` - User avatars
- `skeleton` - Loading skeletons
- `progress` - Progress bars

**Feedback:**
- `alert` - Alert messages
- `toast` - Toast notifications
- `alert-dialog` - Confirmation dialogs

**Command & Search:**
- `command` - Command palette (⌘K)
- `combobox` - Autocomplete select

---

## Part 4: Integration with Existing Apex UI

### Current Apex Stack

```
✅ React 18.3.1
✅ TypeScript 5.7.2
✅ Vite 6.0.6
✅ TailwindCSS 3.4.17
✅ Radix UI (primitives)
✅ Framer Motion 12.23.22
✅ Lucide React (icons)
```

**Perfect Match:** Shadcn/ui uses the **exact same stack**!

### Migration Strategy

**Phase 1: Add Shadcn/ui (Non-Breaking)**
```bash
# Initialize without replacing existing components
npx shadcn@latest init

# Add new components we don't have yet
npx shadcn@latest add command sheet form
```

**Phase 2: Gradual Replacement**
Replace custom components with Shadcn/ui versions:

**Before (Custom):**
```tsx
// Custom button
function ApexButton({ children, variant, ...props }) {
  const classes = variant === 'primary'
    ? 'bg-gradient-to-r from-purple-500 to-pink-500...'
    : 'bg-white/10...';

  return <button className={classes} {...props}>{children}</button>;
}
```

**After (Shadcn/ui with customization):**
```tsx
// /components/ui/button.tsx (modified)
const buttonVariants = cva(
  "inline-flex items-center justify-center...",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        // ADD APEX VARIANTS ↓
        apex: "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600",
        apexGhost: "bg-white/10 hover:bg-white/20 border border-white/10"
      }
    }
  }
);
```

**Usage:**
```tsx
import { Button } from '@/components/ui/button';

// Use apex variant
<Button variant="apex">Apex Style</Button>
```

**Phase 3: Enhance with Framer Motion**
Shadcn/ui components work perfectly with Framer Motion:

```tsx
import { motion } from 'framer-motion';
import { Dialog, DialogContent } from '@/components/ui/dialog';

function AnimatedDialog() {
  return (
    <Dialog>
      <DialogContent asChild>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
        >
          {/* Dialog content */}
        </motion.div>
      </DialogContent>
    </Dialog>
  );
}
```

---

## Part 5: Customization for Apex Design System

### Tailwind Theme Configuration

```js
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        // Apex color palette
        apex: {
          purple: {
            50: '#faf5ff',
            500: '#a855f7',
            600: '#9333ea',
            700: '#7e22ce'
          },
          pink: {
            500: '#ec4899',
            600: '#db2777'
          }
        },

        // Shadcn/ui semantic colors (CSS variables)
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))"
        },
        // ... more semantic colors
      }
    }
  }
}
```

### CSS Variables (Dark Mode Support)

```css
/* src/index.css */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;

    --primary: 271 91% 65%;  /* Purple */
    --primary-foreground: 0 0% 100%;

    --secondary: 330 81% 60%;  /* Pink */
    --secondary-foreground: 0 0% 100%;

    /* ... more variables */
  }

  .dark {
    --background: 0 0% 0%;  /* Black for Apex */
    --foreground: 0 0% 98%;

    --primary: 271 91% 65%;
    --primary-foreground: 0 0% 100%;

    --secondary: 330 81% 60%;
    --secondary-foreground: 0 0% 100%;

    /* ... more dark mode variables */
  }
}
```

### Component Variants

```tsx
// /components/ui/button.tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        // Default Shadcn variants
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",

        // APEX CUSTOM VARIANTS ↓
        apex: "bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 shadow-lg shadow-purple-500/50",
        apexOutline: "border-2 border-purple-500 text-purple-400 hover:bg-purple-500/10",
        apexGhost: "bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20",
        apexGlass: "backdrop-blur-xl bg-white/10 border border-white/10 hover:bg-white/15"
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
);
```

**Usage:**
```tsx
<Button variant="apex" size="lg">
  Apex Gradient Button
</Button>

<Button variant="apexGlass">
  Glass-morphism Button
</Button>
```

---

## Part 6: Essential Components for Apex

### 1. Sheet (Artifacts Sidebar)

```tsx
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';

function ArtifactsSidebar({ artifact, open, onClose }) {
  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent side="right" className="w-2/5 sm:max-w-2xl">
        <SheetHeader>
          <SheetTitle>{artifact.title}</SheetTitle>
          <SheetDescription>
            {artifact.type} · Created {artifact.created_at}
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6">
          <ArtifactRenderer artifact={artifact} />
        </div>
      </SheetContent>
    </Sheet>
  );
}
```

**Why Sheet?**
- Built-in slide-in animation
- Accessible (focus trap, escape to close)
- Responsive (full-screen on mobile)
- Customizable side (left, right, top, bottom)

### 2. Command (⌘K Palette)

```tsx
import { Command, CommandInput, CommandList, CommandGroup, CommandItem } from '@/components/ui/command';

function ApexCommandPalette() {
  return (
    <Command className="rounded-lg border shadow-md">
      <CommandInput placeholder="Search Apex..." />
      <CommandList>
        <CommandGroup heading="Actions">
          <CommandItem>
            <Search className="mr-2 h-4 w-4" />
            <span>Search Documents</span>
          </CommandItem>
          <CommandItem>
            <Network className="mr-2 h-4 w-4" />
            <span>Query Knowledge Graph</span>
          </CommandItem>
        </CommandGroup>

        <CommandGroup heading="Recent">
          <CommandItem>CAT Equipment Analysis</CommandItem>
          <CommandItem>Maintenance Report Q3</CommandItem>
        </CommandGroup>
      </CommandList>
    </Command>
  );
}
```

**Trigger with Keyboard Shortcut:**
```tsx
useEffect(() => {
  const down = (e: KeyboardEvent) => {
    if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      setOpen((open) => !open);
    }
  };

  document.addEventListener("keydown", down);
  return () => document.removeEventListener("keydown", down);
}, []);
```

### 3. Dialog (Modals)

```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';

function ConfirmDeleteDialog({ document, open, onClose, onConfirm }) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Document?</DialogTitle>
          <DialogDescription>
            This will permanently delete "{document.title}". This action cannot be undone.
          </DialogDescription>
        </DialogHeader>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button variant="destructive" onClick={onConfirm}>Delete</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

### 4. Form (with React Hook Form)

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

function LoginForm() {
  const form = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: ''
    }
  });

  const onSubmit = (data) => {
    console.log(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="you@company.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" variant="apex" className="w-full">
          Sign In
        </Button>
      </form>
    </Form>
  );
}
```

### 5. Toast (Notifications)

```tsx
import { toast } from '@/components/ui/use-toast';

function MyComponent() {
  const showSuccess = () => {
    toast({
      title: "Document Uploaded",
      description: "Your document has been successfully indexed.",
      variant: "default"
    });
  };

  const showError = () => {
    toast({
      title: "Upload Failed",
      description: "There was an error uploading your document.",
      variant: "destructive"
    });
  };

  return (
    <>
      <Button onClick={showSuccess}>Show Success</Button>
      <Button onClick={showError}>Show Error</Button>
    </>
  );
}
```

---

## Part 7: Dark Mode Integration

Shadcn/ui has built-in dark mode support using `next-themes`:

```tsx
// /components/theme-provider.tsx
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({ children, ...props }) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}

// /main.tsx
import { ThemeProvider } from "@/components/theme-provider"

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <YourApp />
    </ThemeProvider>
  )
}

// /components/theme-toggle.tsx
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
```

---

## Part 8: Performance Considerations

### 1. Only Add What You Need

```bash
# Don't add all components
npx shadcn@latest add --all  ❌

# Add only what you use
npx shadcn@latest add button dialog input  ✅
```

### 2. Tree-Shaking

Shadcn/ui components are tree-shakeable because you own the source:

```tsx
// Only imports Button code
import { Button } from '@/components/ui/button';
```

### 3. Code Splitting

Lazy load heavy components:

```tsx
const Command = lazy(() => import('@/components/ui/command'));

<Suspense fallback={<Skeleton />}>
  <Command />
</Suspense>
```

---

## Part 9: Migration Checklist

**✅ Pre-Installation**
- [ ] Confirm Tailwind CSS is installed and configured
- [ ] Verify TypeScript is set up
- [ ] Check path aliases are configured (@/components, @/lib)

**✅ Installation**
- [ ] Run `npx shadcn@latest init`
- [ ] Choose "Default" style
- [ ] Enable CSS variables for colors
- [ ] Confirm component and utils paths

**✅ Add Core Components**
- [ ] Button, Input, Textarea (forms)
- [ ] Dialog, Sheet (overlays)
- [ ] Toast (notifications)
- [ ] Tabs (navigation)
- [ ] Command (search)

**✅ Customization**
- [ ] Add Apex color variants to button.tsx
- [ ] Configure dark mode theme
- [ ] Test components with Framer Motion
- [ ] Add Apex-specific variants

**✅ Integration**
- [ ] Replace existing components gradually
- [ ] Test accessibility (keyboard navigation, screen readers)
- [ ] Verify responsive behavior (mobile, tablet, desktop)
- [ ] Check performance (bundle size, render time)

---

## References

**Official Documentation (Tier 1):**
- Shadcn/ui Docs: https://ui.shadcn.com/docs
- Installation Guide: https://ui.shadcn.com/docs/installation
- Components: https://ui.shadcn.com/docs/components

**Dependencies:**
- Radix UI: https://www.radix-ui.com/
- Class Variance Authority (cva): https://cva.style/docs
- clsx: https://github.com/lukeed/clsx
- tailwind-merge: https://github.com/dcastil/tailwind-merge

**Patterns & Examples:**
- Shadcn/ui GitHub: https://github.com/shadcn-ui/ui
- Taxonomy Template: https://github.com/shadcn-ui/taxonomy

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Documentation)
