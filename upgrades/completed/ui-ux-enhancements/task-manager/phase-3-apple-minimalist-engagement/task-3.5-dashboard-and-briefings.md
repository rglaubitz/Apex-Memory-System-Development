# Task 3.5: Hidden Dashboard & Briefings

**Phase:** 3 - Apple Minimalist Engagement Layer
**Status:** ✅ Complete
**Estimated Duration:** 8 hours (Day 5)
**Completed:** 2025-10-22

---

## Overview

Build hidden dashboard (not landing page) with single-metric-at-a-time display and subtle briefing notifications via menu badge. Dashboard accessible via menu, briefings open in full-screen elegant modal with NO popups or interruptions.

---

## Dependencies

**Required Before Starting:**
- Task 3.1: Design System Foundation (requires design-system.ts constants)
- Task 3.2: Backend Engagement APIs (requires /api/v1/briefings/ and /api/v1/analytics/ endpoints)

**Enables After Completion:**
- Phase 3 complete → Phase 4: Collaboration & Polish

---

## Success Criteria

✅ Dashboard component shows one metric at a time
✅ Pagination dots navigate between metrics
✅ Generous spacing (p-16, max-w-2xl, text-6xl for value)
✅ Dashboard NOT default landing page (conversation-first approach)
✅ AppLayout shows badge on menu when briefing available
✅ Badge is subtle (2px blue dot, no animation)
✅ Briefing opens in full-screen modal (elegant typography)
✅ No popups, toasts, or interruptions
✅ 8 frontend component tests passing (3 Dashboard + 4 AppLayout + 1 integration)

---

## Research References

**Technical Documentation:**
- research/documentation/react-hooks-patterns.md (Lines: 1-100)
  - Key concepts: useEffect, useState, custom hooks

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 3092-3249)
  - Complete Dashboard and AppLayout implementation with BriefingModal

---

## Test Specifications

**Frontend Component Tests:** 8 tests
- TESTING.md: Lines 1624-1756 (Dashboard + AppLayout test suites)

**Dashboard tests (3):**
1. Displays single metric at a time
2. Navigates between metrics with pagination
3. Applies generous spacing

**AppLayout tests (4):**
4. Shows badge on menu when briefing available
5. Opens briefing modal on menu click
6. Briefing modal has elegant typography
7. No popup notifications shown

**Integration test (1):**
8. Badge disappears after briefing read

**Total Tests:** 8

---

## Implementation Steps

### Subtask 3.5.1: Create Dashboard Component

**Duration:** 2 hours
**Status:** ✅ Complete

**Files to Create:**
- `apex-memory-system/frontend/src/components/Dashboard.tsx`

**Steps:**
1. Create Dashboard component file
2. Define Metric and DashboardProps interfaces
3. Implement single-metric display with pagination
4. Add pagination dots navigation
5. Apply Apple-style generous spacing
6. Use design-system constants

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 3096-3145 for complete code
import React, { useState } from 'react';

interface Metric {
  label: string;
  value: string;
  description: string;
}

interface DashboardProps {
  metrics: Metric[];
}

export function Dashboard({ metrics }: DashboardProps) {
  const [currentMetricIndex, setCurrentMetricIndex] = useState(0);

  const currentMetric = metrics[currentMetricIndex];

  return (
    <div className="max-w-2xl mx-auto p-16">
      {/* Single metric display */}
      <div className="text-center">
        <div className="text-6xl font-semibold text-gray-900 mb-4">
          {currentMetric.value}
        </div>
        <div className="text-2xl font-medium text-gray-700 mb-2">
          {currentMetric.label}
        </div>
        <div className="text-base text-gray-500 max-w-md mx-auto">
          {currentMetric.description}
        </div>
      </div>

      {/* Pagination dots */}
      <div className="flex justify-center gap-2 mt-12">
        {metrics.map((_, idx) => (
          <button
            key={idx}
            onClick={() => setCurrentMetricIndex(idx)}
            className={`w-2 h-2 rounded-full transition-all ${
              idx === currentMetricIndex
                ? 'bg-gray-900 w-6'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
```

**Validation:**
```bash
# Visual test
const mockMetrics = [
  {
    label: 'Documents Ingested',
    value: '1,234',
    description: 'Total documents in your knowledge graph'
  },
  {
    label: 'Entities Tracked',
    value: '5,678',
    description: 'Unique entities identified'
  }
];

<Dashboard metrics={mockMetrics} />
```

**Expected Result:**
- Shows one metric at a time (large 6xl value)
- Pagination dots work for navigation
- Generous spacing applied (p-16)

---

### Subtask 3.5.2: Create AppLayout with Briefing Badge

**Duration:** 3 hours
**Status:** ✅ Complete

**Files to Create:**
- `apex-memory-system/frontend/src/components/AppLayout.tsx`
- `apex-memory-system/frontend/src/hooks/useBriefing.ts`

**Steps:**
1. Create AppLayout component with menu sidebar
2. Create useBriefing hook to check for new briefings
3. Implement menu button with badge (2px blue dot)
4. Add briefing state (hasNewBriefing, isBriefingOpen)
5. Fetch briefing status from /api/v1/briefings/latest
6. Wire badge visibility to hasNewBriefing state

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 3154-3204 for complete code
import React, { useState, useEffect } from 'react';

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [hasNewBriefing, setHasNewBriefing] = useState(false);
  const [isBriefingOpen, setIsBriefingOpen] = useState(false);

  useEffect(() => {
    // Check for new briefing
    checkForNewBriefing();
  }, []);

  const checkForNewBriefing = async () => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch('/api/v1/briefings/latest', {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await response.json();
    setHasNewBriefing(data.has_unread);
  };

  return (
    <div className="flex h-screen">
      {/* Menu sidebar */}
      <nav className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-6 gap-6">
        {/* Menu button with badge */}
        <button
          className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
          onClick={() => setIsBriefingOpen(true)}
        >
          <MenuIcon />
          {hasNewBriefing && (
            <span className="absolute top-1 right-1 w-2 h-2 bg-blue-500 rounded-full" />
          )}
        </button>

        {/* Other menu items... */}
      </nav>

      {/* Main content */}
      <main className="flex-1">{children}</main>

      {/* Briefing modal will go here */}
    </div>
  );
}

function MenuIcon() {
  return (
    <svg className="w-6 h-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
}
```

**Validation:**
```bash
# Visual test
# Check menu badge appears when hasNewBriefing = true
# Badge should be 2px blue dot (subtle, no animation)
```

**Expected Result:**
- Menu sidebar renders with button
- Badge shows when briefing available
- Badge is subtle (2px dot, no flashy animation)

---

### Subtask 3.5.3: Create BriefingModal Component

**Duration:** 2 hours
**Status:** ✅ Complete

**Files to Modify:**
- `apex-memory-system/frontend/src/components/AppLayout.tsx` (add BriefingModal)

**Steps:**
1. Create BriefingModal component within AppLayout file
2. Implement full-screen modal with elegant typography
3. Add backdrop with subtle opacity (bg-opacity-20)
4. Load briefing content from /api/v1/briefings/latest
5. Mark briefing as read on close (POST /api/v1/briefings/mark_read/{id})
6. Apply generous spacing (p-16, space-y-8)

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 3206-3236 for complete code
function BriefingModal({ onClose }: { onClose: () => void }) {
  const [briefing, setBriefing] = useState(null);

  useEffect(() => {
    const fetchBriefing = async () => {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('/api/v1/briefings/latest', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setBriefing(data.briefing);
    };

    fetchBriefing();
  }, []);

  const handleClose = async () => {
    if (briefing) {
      // Mark as read
      const token = localStorage.getItem('auth_token');
      await fetch(`/api/v1/briefings/mark_read/${briefing.uuid}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
    }
    onClose();
  };

  if (!briefing) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
      <div className="bg-white rounded-3xl p-16 max-w-3xl max-h-[80vh] overflow-y-auto shadow-2xl">
        {/* Elegant typography */}
        <h1 className="text-4xl font-semibold text-gray-900 mb-6">
          {briefing.title}
        </h1>

        <div className="space-y-8 text-gray-700 leading-relaxed">
          <div dangerouslySetInnerHTML={{ __html: briefing.content }} />
        </div>

        <button
          onClick={handleClose}
          className="mt-12 px-8 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
}
```

**Validation:**
```bash
# Visual test
# Click menu button → briefing modal should open
# Check elegant typography (text-4xl, text-gray-900, leading-relaxed)
# Close modal → should mark briefing as read
```

**Expected Result:**
- Modal opens full-screen with elegant design
- Briefing content renders with rich typography
- Close button marks briefing as read
- Badge disappears after modal closed

---

### Subtask 3.5.4: Write Component Tests

**Duration:** 1 hour
**Status:** ✅ Complete

**Files to Create:**
- `apex-memory-system/frontend/src/__tests__/components/Dashboard.test.tsx`
- `apex-memory-system/frontend/src/__tests__/components/AppLayout.test.tsx`

**Steps:**
1. Create Dashboard test file (3 tests)
2. Create AppLayout test file (5 tests including integration)
3. Mock useBriefing hook for AppLayout tests
4. Test Dashboard pagination behavior
5. Test AppLayout badge visibility and modal opening
6. Run all tests and verify 8/8 passing

**Code Example:**
```typescript
// Dashboard.test.tsx
// See TESTING.md lines 1627-1681 for complete code
import { render, screen, fireEvent } from '@testing-library/react';
import { Dashboard } from '../../components/Dashboard';

describe('Dashboard Component', () => {
  const mockMetrics = [
    {
      label: 'Documents Ingested',
      value: '1,234',
      description: 'Total documents in your knowledge graph'
    },
    {
      label: 'Entities Tracked',
      value: '5,678',
      description: 'Unique entities identified'
    },
    {
      label: 'Queries This Week',
      value: '42',
      description: 'Questions asked this week'
    }
  ];

  test('displays single metric at a time', () => {
    render(<Dashboard metrics={mockMetrics} />);

    // First metric should be visible
    expect(screen.getByText('1,234')).toBeInTheDocument();
    expect(screen.getByText('Documents Ingested')).toBeInTheDocument();

    // Other metrics should not be visible
    expect(screen.queryByText('5,678')).not.toBeInTheDocument();
  });

  test('navigates between metrics with pagination', () => {
    render(<Dashboard metrics={mockMetrics} />);

    // Get pagination dots (there should be 3)
    const dots = screen.getAllByRole('button');
    expect(dots).toHaveLength(3);

    // Click second dot
    fireEvent.click(dots[1]);

    // Second metric should be visible
    expect(screen.getByText('5,678')).toBeInTheDocument();
    expect(screen.getByText('Entities Tracked')).toBeInTheDocument();
  });

  test('applies generous spacing', () => {
    const { container } = render(<Dashboard metrics={mockMetrics} />);

    const mainDiv = container.querySelector('.p-16');
    expect(mainDiv).toBeInTheDocument();
  });
});

// AppLayout.test.tsx
// See TESTING.md lines 1687-1755 for complete code
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AppLayout } from '../../components/AppLayout';

jest.mock('../../hooks/useBriefing', () => ({
  useBriefing: () => ({
    hasNewBriefing: true,
    latestBriefing: {
      uuid: 'briefing-1',
      title: 'New Insights',
      content: '<p>Your knowledge graph has evolved...</p>'
    }
  })
}));

describe('AppLayout Component', () => {
  test('shows badge on menu when briefing available', () => {
    render(
      <AppLayout>
        <div>Content</div>
      </AppLayout>
    );

    // Badge should be visible
    const badge = screen.getByRole('button').querySelector('.bg-blue-500');
    expect(badge).toBeInTheDocument();
  });

  test('opens briefing modal on menu click', async () => {
    render(
      <AppLayout>
        <div>Content</div>
      </AppLayout>
    );

    const menuButton = screen.getAllByRole('button')[0];
    fireEvent.click(menuButton);

    await waitFor(() => {
      expect(screen.getByText('New Insights')).toBeInTheDocument();
    });
  });

  test('briefing modal has elegant typography', async () => {
    render(
      <AppLayout>
        <div>Content</div>
      </AppLayout>
    );

    const menuButton = screen.getAllByRole('button')[0];
    fireEvent.click(menuButton);

    await waitFor(() => {
      const heading = screen.getByText('New Insights');
      expect(heading).toHaveClass('text-4xl');
      expect(heading).toHaveClass('font-semibold');
    });
  });

  test('no popup notifications shown', () => {
    render(
      <AppLayout>
        <div>Content</div>
      </AppLayout>
    );

    // No toast/notification components
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
});
```

**Validation:**
```bash
# Run component tests
cd frontend
npm test -- Dashboard.test.tsx AppLayout.test.tsx

# Expected: 8/8 tests passing
```

**Expected Result:**
- 3/3 Dashboard tests passing
- 5/5 AppLayout tests passing
- Total: 8/8 tests passing

---

## Troubleshooting

**Common Issues:**

**Issue 1: Badge not disappearing after briefing read**
- See TROUBLESHOOTING.md:Lines 1100-1125
- Solution: Ensure POST /mark_read called on modal close, refresh hasNewBriefing state

**Issue 2: Modal not scrolling for long briefings**
- See TROUBLESHOOTING.md:Lines 1150-1175
- Solution: Add overflow-y-auto and max-h-[80vh] to modal content div

**Issue 3: Dashboard metrics not formatted**
- See TROUBLESHOOTING.md:Lines 1200-1225
- Solution: Format large numbers with toLocaleString() (1234 → "1,234")

---

## Progress Tracking

**Subtasks:** 4/4 complete (100%) ✅

- [x] Subtask 3.5.1: Create Dashboard Component
- [x] Subtask 3.5.2: Create AppLayout with Briefing Badge
- [x] Subtask 3.5.3: Create BriefingModal Component
- [x] Subtask 3.5.4: Write Component Tests

**Tests:** 8/8 passing (100%) ✅

**Last Updated:** 2025-10-22
**Status:** ✅ Complete
