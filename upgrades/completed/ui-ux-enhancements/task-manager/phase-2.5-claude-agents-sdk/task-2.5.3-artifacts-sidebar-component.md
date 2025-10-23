# Task 2.5.3: Artifacts Sidebar Component

**Phase:** 2.5 - Claude Agents SDK Integration
**Status:** ⬜ Not Started
**Estimated Duration:** 6 hours (Days 4-5)
**Assigned To:** (filled during execution)

---

## Overview

Build Artifacts sidebar using Sheet component (Claude.ai pattern) with 5 visualization components for different tool result types (search results, relationships, timeline, similar docs, statistics).

---

## Dependencies

**Required Before Starting:**
- Task 2.5.1: Backend Streaming with Tool Use (requires tool result schemas)
- Task 1.2: Frontend Authentication UI (requires UI component library)

**Enables After Completion:**
- Task 2.5.4: ConversationHub Streaming Integration

---

## Success Criteria

✅ ArtifactSidebar component functional with Sheet animation
✅ 5 visualization components rendering correctly
✅ SearchResultsView displays documents with scores
✅ RelationshipsView shows graph connections
✅ TimelineView renders temporal events
✅ SimilarDocsView shows similar documents
✅ StatisticsView displays metrics grid
✅ Sidebar slides in/out smoothly (Sheet component)

---

## Research References

**Technical Documentation:**
- research/documentation/artifacts-layout.md (Lines: 1-100)
  - Key concepts: Claude.ai artifacts pattern, Sheet component, visualization types

- research/documentation/shadcn-ui-sheet.md (Lines: 1-80)
  - Key concepts: Sheet component API, side prop, onOpenChange

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2675-2810)
  - Complete ArtifactSidebar and all 5 view components

---

## Test Specifications

**Frontend Component Tests:** (5 tests, part of 10 frontend tests)
- TESTING.md: Lines 1491-1534 (useApexChat tests cover integration)
- File: `frontend/src/__tests__/components/ArtifactSidebar.test.tsx`

**Tests to pass:**
1. ArtifactSidebar renders with Sheet component
2. SearchResultsView renders results
3. RelationshipsView renders graph connections
4. TimelineView renders events chronologically
5. StatisticsView renders metrics grid

**Total Tests:** 5 (part of 10 total frontend tests)

---

## Implementation Steps

### Subtask 2.5.3.1: Create ArtifactSidebar Shell

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/components/ArtifactSidebar.tsx`

**Steps:**
1. Install shadcn/ui Sheet component: `npx shadcn-ui@latest add sheet`
2. Create TypeScript interfaces (Artifact type with union type)
3. Create ArtifactSidebarProps interface
4. Implement ArtifactSidebar component shell
5. Use Sheet, SheetContent, SheetHeader, SheetTitle from shadcn
6. Set Sheet side="right" and width w-[600px]
7. Map over artifacts array to render each artifact
8. Add conditional rendering based on artifact.type

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2677-2735 for complete code
import React from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';

interface Artifact {
  type: 'search_results' | 'relationships' | 'timeline' | 'similar_docs' | 'statistics';
  title: string;
  data: any;
}

interface ArtifactSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  artifacts: Artifact[];
}

export function ArtifactSidebar({ isOpen, onClose, artifacts }: ArtifactSidebarProps) {
  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-[600px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Tool Artifacts</SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {artifacts.map((artifact, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-3">{artifact.title}</h3>
              {/* Conditional rendering for each type */}
            </div>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
}
```

**Validation:**
```bash
# Test component renders
cd frontend
npm run dev

# Open browser, import component
# Verify Sheet animation works
```

**Expected Result:**
- Sheet component slides in from right
- 600px width sidebar
- SheetHeader with "Tool Artifacts" title
- Artifacts map correctly

---

### Subtask 2.5.3.2: Implement 5 Visualization Components

**Duration:** 3 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ArtifactSidebar.tsx` (add view components)

**Steps:**
1. Implement SearchResultsView component
   - Display results array with title, excerpt, score
   - Show score as percentage (score * 100)
   - Gray background for each result card
2. Implement RelationshipsView component
   - Display relationships array with from → type → to format
   - Use arrow notation for visual clarity
3. Implement TimelineView component
   - Display timeline array with date, title, description
   - Add blue left border for timeline effect
4. Implement SimilarDocsView component
   - Display similar_documents array with title, similarity
   - Show similarity as percentage
5. Implement StatisticsView component
   - Display statistics object as 2-column grid
   - Large bold numbers, small gray labels

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2737-2809 for complete code
function SearchResultsView({ data }: { data: any }) {
  return (
    <div className="space-y-3">
      {data.results.map((result: any, idx: number) => (
        <div key={idx} className="bg-gray-50 p-3 rounded">
          <div className="font-medium">{result.title}</div>
          <div className="text-sm text-gray-600 mt-1">{result.excerpt}</div>
          <div className="text-xs text-gray-400 mt-1">
            Score: {(result.score * 100).toFixed(1)}%
          </div>
        </div>
      ))}
    </div>
  );
}

// ... 4 more view components (see IMPLEMENTATION.md)
```

**Validation:**
```typescript
// Test with mock data
const mockArtifacts = [
  {
    type: 'search_results',
    title: 'Search Results',
    data: { results: [{ title: 'Doc 1', excerpt: 'Excerpt', score: 0.95 }] }
  },
  // ... more mock artifacts
];

<ArtifactSidebar isOpen={true} onClose={() => {}} artifacts={mockArtifacts} />
```

**Expected Result:**
- All 5 view components render correctly
- Data formatted appropriately (percentages, arrows, grid)
- Visual hierarchy clear (bold titles, gray text)

---

### Subtask 2.5.3.3: Add Sheet Interactions

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ArtifactSidebar.tsx` (add interactions)

**Steps:**
1. Verify Sheet onOpenChange callback closes sidebar
2. Add close button in SheetHeader (already provided by shadcn)
3. Test keyboard shortcuts (Escape key closes)
4. Add click outside to close behavior (Sheet default)
5. Test smooth slide animation

**Code Example:**
```typescript
// Sheet component handles most interactions by default
<Sheet open={isOpen} onOpenChange={onClose}>
  {/* onOpenChange fires when Sheet should close */}
  {/* Escape key, click outside, close button all trigger onClose */}
</Sheet>
```

**Validation:**
```bash
# Test interactions
# 1. Open sidebar programmatically
# 2. Click outside → verify closes
# 3. Press Escape → verify closes
# 4. Click X button → verify closes
# 5. Verify smooth slide-in/out animation
```

**Expected Result:**
- Sidebar closes on Escape key
- Sidebar closes on click outside
- Close button functional
- Smooth slide animation (300ms)

---

### Subtask 2.5.3.4: Style with Apple Minimalist Theme

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ArtifactSidebar.tsx` (refine styles)

**Steps:**
1. Apply consistent spacing (16px, 24px gaps)
2. Use gray-50 for backgrounds, gray-200 for borders
3. Add subtle shadows for cards
4. Use system font stack (-apple-system, BlinkMacSystemFont)
5. Ensure 90% monochrome (gray scale)
6. Use blue-500 accent for timeline border only

**Code Example:**
```typescript
// Consistent styling
className="border border-gray-200 rounded-lg p-4 shadow-sm"
className="bg-gray-50 p-3 rounded"
className="text-sm text-gray-600"
className="border-l-2 border-blue-500 pl-3"  // Timeline accent
```

**Validation:**
```bash
# Visual inspection
# 1. Check spacing consistency
# 2. Verify monochrome palette (90%+)
# 3. Verify single accent color (blue for timeline)
# 4. Check font rendering (-apple-system used)
```

**Expected Result:**
- 90% monochrome, 10% blue accent
- Consistent spacing throughout
- Subtle shadows, not heavy
- Apple-like aesthetic

---

## Troubleshooting

**Common Issues:**

**Issue 1: Sheet component not animating**
- See TROUBLESHOOTING.md:Lines 1100-1125
- Solution: Verify @radix-ui/react-dialog installed, check Tailwind config includes animations

**Issue 2: Artifacts not rendering**
- See TROUBLESHOOTING.md:Lines 1150-1175
- Solution: Check artifact.type matches exactly, verify data structure from backend

**Issue 3: Sidebar too narrow/wide**
- See TROUBLESHOOTING.md:Lines 1200-1225
- Solution: Adjust w-[600px] in SheetContent, test on different screen sizes

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 2.5.3.1: Create ArtifactSidebar Shell
- [ ] Subtask 2.5.3.2: Implement 5 Visualization Components
- [ ] Subtask 2.5.3.3: Add Sheet Interactions
- [ ] Subtask 2.5.3.4: Style with Apple Minimalist Theme

**Tests:** 0/5 passing (0%)

**Last Updated:** 2025-10-21
