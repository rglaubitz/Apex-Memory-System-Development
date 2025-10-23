# Component Catalog - Essential Shadcn/ui Components

**Purpose:** Comprehensive list of Shadcn/ui components for Apex
**Date Created:** 2025-10-21
**Documentation Tier:** Tier 1 (Official Documentation)

**Related Documentation:**
- For installation → see `shadcn-installation.md`
- For customization → see `customization-guide.md`
- For Apex integration → see `apex-integration-strategy.md`

---

## Core Components for Apex

### 1. Button

```bash
npx shadcn@latest add button
```

**Use cases:** Primary actions, form submissions, navigation

```tsx
<Button variant="default">Save</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button variant="ghost">Edit</Button>
<Button variant="link">Learn more</Button>
```

### 2. Input

```bash
npx shadcn@latest add input
```

**Use cases:** Text inputs, search bars, forms

```tsx
<Input type="text" placeholder="Search documents..." />
<Input type="email" placeholder="Email" />
<Input type="password" placeholder="Password" />
```

### 3. Dialog

```bash
npx shadcn@latest add dialog
```

**Use cases:** Modals, confirmations, forms

```tsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Confirm Delete</DialogTitle>
      <DialogDescription>
        This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="outline">Cancel</Button>
      <Button variant="destructive">Delete</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### 4. Sheet

```bash
npx shadcn@latest add sheet
```

**Use cases:** Artifacts sidebar, settings panels, side navigation

```tsx
<Sheet>
  <SheetTrigger asChild>
    <Button variant="outline">Open</Button>
  </SheetTrigger>
  <SheetContent side="right">
    <SheetHeader>
      <SheetTitle>Artifact Viewer</SheetTitle>
      <SheetDescription>
        View and edit generated artifacts
      </SheetDescription>
    </SheetHeader>
    {/* Content */}
  </SheetContent>
</Sheet>
```

### 5. Select

```bash
npx shadcn@latest add select
```

**Use cases:** Dropdowns, filters, model selection

```tsx
<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select model" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="claude-sonnet">Claude Sonnet</SelectItem>
    <SelectItem value="claude-opus">Claude Opus</SelectItem>
  </SelectContent>
</Select>
```

---

## Form Components

### 6. Form + Label

```bash
npx shadcn@latest add form label
```

**Use cases:** Complex forms with validation

```tsx
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <FormField
      control={form.control}
      name="username"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Username</FormLabel>
          <FormControl>
            <Input placeholder="shadcn" {...field} />
          </FormControl>
          <FormDescription>
            This is your public display name.
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
  </form>
</Form>
```

### 7. Textarea

```bash
npx shadcn@latest add textarea
```

**Use cases:** Multi-line input, comments, descriptions

```tsx
<Textarea placeholder="Type your message here..." />
```

### 8. Checkbox + Radio Group

```bash
npx shadcn@latest add checkbox radio-group
```

**Use cases:** Settings, preferences, filters

```tsx
<Checkbox id="terms" />
<Label htmlFor="terms">Accept terms and conditions</Label>

<RadioGroup defaultValue="option-one">
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="option-one" id="option-one" />
    <Label htmlFor="option-one">Option One</Label>
  </div>
</RadioGroup>
```

---

## Display Components

### 9. Card

```bash
npx shadcn@latest add card
```

**Use cases:** Document previews, entity cards, summaries

```tsx
<Card>
  <CardHeader>
    <CardTitle>Document Title</CardTitle>
    <CardDescription>Added 2 days ago</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Document excerpt...</p>
  </CardContent>
  <CardFooter>
    <Button variant="outline">View</Button>
  </CardFooter>
</Card>
```

### 10. Badge

```bash
npx shadcn@latest add badge
```

**Use cases:** Status indicators, tags, counts

```tsx
<Badge>New</Badge>
<Badge variant="secondary">Processing</Badge>
<Badge variant="destructive">Failed</Badge>
<Badge variant="outline">Archived</Badge>
```

### 11. Alert

```bash
npx shadcn@latest add alert
```

**Use cases:** Notifications, warnings, errors

```tsx
<Alert>
  <AlertCircle className="h-4 w-4" />
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>
    You can add components to your app using the cli.
  </AlertDescription>
</Alert>
```

### 12. Separator

```bash
npx shadcn@latest add separator
```

**Use cases:** Dividing content, visual breaks

```tsx
<div>
  <div className="space-y-1">
    <h4 className="text-sm font-medium">Section 1</h4>
  </div>
  <Separator className="my-4" />
  <div className="space-y-1">
    <h4 className="text-sm font-medium">Section 2</h4>
  </div>
</div>
```

---

## Navigation Components

### 13. Tabs

```bash
npx shadcn@latest add tabs
```

**Use cases:** Content switching, settings panels

```tsx
<Tabs defaultValue="account">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">Account settings</TabsContent>
  <TabsContent value="password">Password settings</TabsContent>
</Tabs>
```

### 14. Command

```bash
npx shadcn@latest add command
```

**Use cases:** Command palette, quick search

```tsx
<Command>
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Suggestions">
      <CommandItem>Search Documents</CommandItem>
      <CommandItem>Query Graph</CommandItem>
    </CommandGroup>
  </CommandList>
</Command>
```

---

## Feedback Components

### 15. Toast

```bash
npx shadcn@latest add toast
```

**Use cases:** Success messages, errors, notifications

```tsx
import { useToast } from "@/components/ui/use-toast"

function Component() {
  const { toast } = useToast()

  return (
    <Button
      onClick={() => {
        toast({
          title: "Scheduled: Catch up",
          description: "Friday, February 10, 2023 at 5:57 PM",
        })
      }}
    >
      Show Toast
    </Button>
  )
}
```

### 16. Progress

```bash
npx shadcn@latest add progress
```

**Use cases:** Loading states, upload progress

```tsx
<Progress value={33} />
```

### 17. Skeleton

```bash
npx shadcn@latest add skeleton
```

**Use cases:** Loading placeholders

```tsx
<div className="flex items-center space-x-4">
  <Skeleton className="h-12 w-12 rounded-full" />
  <div className="space-y-2">
    <Skeleton className="h-4 w-[250px]" />
    <Skeleton className="h-4 w-[200px]" />
  </div>
</div>
```

---

## Advanced Components

### 18. Popover

```bash
npx shadcn@latest add popover
```

**Use cases:** Tooltips, context menus, additional info

```tsx
<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline">Open popover</Button>
  </PopoverTrigger>
  <PopoverContent className="w-80">
    <div className="grid gap-4">
      <div className="space-y-2">
        <h4 className="font-medium leading-none">Dimensions</h4>
        <p className="text-sm text-muted-foreground">
          Set the dimensions for the layer.
        </p>
      </div>
    </div>
  </PopoverContent>
</Popover>
```

### 19. DropdownMenu

```bash
npx shadcn@latest add dropdown-menu
```

**Use cases:** User menus, actions menus

```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Open</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Settings</DropdownMenuItem>
    <DropdownMenuItem>Logout</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

### 20. DataTable

```bash
npx shadcn@latest add data-table
```

**Use cases:** Document lists, entity tables, query results

```tsx
<DataTable columns={columns} data={data} />
```

---

## Component Combinations

### Example: Full Form

```tsx
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
    <FormField
      control={form.control}
      name="query"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Search Query</FormLabel>
          <FormControl>
            <Input placeholder="Enter query..." {...field} />
          </FormControl>
          <FormDescription>
            Search across all documents in the knowledge base.
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />

    <FormField
      control={form.control}
      name="filters"
      render={({ field }) => (
        <FormItem>
          <FormLabel>File Type</FormLabel>
          <Select onValueChange={field.onChange} defaultValue={field.value}>
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select a type" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectItem value="pdf">PDF</SelectItem>
              <SelectItem value="docx">DOCX</SelectItem>
              <SelectItem value="pptx">PPTX</SelectItem>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />

    <Button type="submit">Search</Button>
  </form>
</Form>
```

---

## References

**Official Documentation:**
- Component Catalog: https://ui.shadcn.com/docs/components
- Component Examples: https://ui.shadcn.com/examples

**Related Documentation:**
- Installation → `shadcn-installation.md`
- Customization → `customization-guide.md`
- Apex integration → `apex-integration-strategy.md`

---

**Last Updated:** 2025-10-21
**Documentation Version:** 1.0.0
**Tier:** Tier 1 (Official Documentation)
