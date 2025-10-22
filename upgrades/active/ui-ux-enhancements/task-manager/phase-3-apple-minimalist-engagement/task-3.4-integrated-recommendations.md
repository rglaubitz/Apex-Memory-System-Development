# Task 3.4: Integrated Recommendations

**Phase:** 3 - Apple Minimalist Engagement Layer
**Status:** ⬜ Not Started
**Estimated Duration:** 6 hours (Day 4)
**Assigned To:** (filled during execution)

---

## Overview

Enhance search interface with invisible intelligence - recommendations seamlessly woven into search results with subtle "Based on your recent activity" text. NO separate recommendation cards, NO prominent labels, just better relevance.

---

## Dependencies

**Required Before Starting:**
- Task 3.1: Design System Foundation (requires design-system.ts constants)
- Task 3.2: Backend Engagement APIs (requires enhanced search with recommendation ranking)
- Task 2.4: Frontend Chat Interface (requires existing search patterns)

**Enables After Completion:**
- Task 3.5: Hidden Dashboard & Briefings

---

## Success Criteria

✅ SearchWithRecommendations component functional
✅ Recommendations integrated into search results (not separate section)
✅ Subtle indicator "Based on your recent activity" for recommended results
✅ Search input uses Apple-style rounded design (rounded-2xl, bg-gray-50)
✅ Results have hover effect (hover:bg-gray-50)
✅ Backend ranking boosts relevant results based on user history
✅ 3 frontend component tests passing
✅ No separate "Recommendations" section (seamless integration)

---

## Research References

**Technical Documentation:**
- research/documentation/react-hooks-patterns.md (Lines: 1-100)
  - Key concepts: useEffect, useState, API integration

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 3026-3090)
  - Complete SearchWithRecommendations component

---

## Test Specifications

**Frontend Component Tests:** 3 tests (inferred from pattern, not explicitly in TESTING.md)
- File: `frontend/src/__tests__/components/SearchWithRecommendations.test.tsx`

**Tests to pass:**
1. Search input renders and handles input changes
2. Search results display with title and excerpt
3. Recommended results show subtle indicator

**Total Tests:** 3

---

## Implementation Steps

### Subtask 3.4.1: Create SearchWithRecommendations Component

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/components/SearchWithRecommendations.tsx`

**Steps:**
1. Create component file with TypeScript interfaces
2. Define SearchResult interface (uuid, title, excerpt, score, is_recommendation)
3. Set up state (query, results, loading)
4. Implement search input with Apple-style design
5. Import design-system constants
6. Create results list layout

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 3030-3087 for complete code
import React, { useState } from 'react';

interface SearchResult {
  uuid: string;
  title: string;
  excerpt: string;
  score: number;
  is_recommendation?: boolean;
}

export function SearchWithRecommendations() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-8">
      {/* Search input */}
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        placeholder="Search your knowledge graph..."
        className="w-full px-6 py-4 text-lg border-none bg-gray-50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* Results section */}
      {loading && (
        <div className="mt-8 text-center text-gray-500">Searching...</div>
      )}
    </div>
  );
}
```

**Validation:**
```bash
# Test component renders
cd frontend
npm run dev

# Visual test: Type in search input, press Enter
```

**Expected Result:**
- Search input renders with Apple-style rounded design
- Typing and Enter key work correctly
- Loading state shows during search

---

### Subtask 3.4.2: Implement Results Display with Recommendations

**Duration:** 2 hours
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/frontend/src/components/SearchWithRecommendations.tsx` (add results rendering)

**Steps:**
1. Map over results array
2. Render each result with title, excerpt
3. Add subtle indicator for recommended results (is_recommendation: true)
4. Apply hover effect (hover:bg-gray-50)
5. Use consistent spacing (space-y-3)
6. Make results clickable (cursor-pointer)

**Code Example:**
```typescript
{/* Results with integrated recommendations */}
<div className="mt-8 space-y-3">
  {results.map((result) => (
    <div
      key={result.uuid}
      className="p-4 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer"
      onClick={() => {
        // Navigate to document or open in viewer
        window.location.href = `/documents/${result.uuid}`;
      }}
    >
      <div className="font-medium text-gray-900">{result.title}</div>
      <div className="text-sm text-gray-600 mt-1">{result.excerpt}</div>

      {/* Subtle recommendation indicator */}
      {result.is_recommendation && (
        <div className="text-xs text-gray-400 mt-2">
          Based on your recent activity
        </div>
      )}
    </div>
  ))}
</div>

{results.length === 0 && !loading && query && (
  <div className="mt-8 text-center text-gray-500">
    No results found
  </div>
)}
```

**Validation:**
```bash
# Visual test with backend running
# Perform search → should see results
# Recommended results should have "Based on your recent activity" text
```

**Expected Result:**
- Results display with title and excerpt
- Hover effect smooth (hover:bg-gray-50)
- Recommended results show subtle indicator
- No separate "Recommendations" section

---

### Subtask 3.4.3: Verify Backend Ranking Integration

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Modify:**
- `apex-memory-system/src/apex_memory/services/recommendation_ranker.py` (verify implementation from Task 3.2)

**Steps:**
1. Verify RecommendationRanker service exists (created in Task 3.2)
2. Check search endpoint uses ranker to boost results
3. Test recommendation flagging (is_recommendation: true for boosted results)
4. Verify privacy-first approach (no query content tracking)
5. Test fallback behavior (no crash if user has no history)

**Code Example:**
```python
# In existing search endpoint (from Task 3.2)
from apex_memory.services.recommendation_ranker import RecommendationRanker

@router.post("/search")
async def search(
    query: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search with personalized ranking."""
    # Get base search results
    results = await search_service.search(query)

    # Apply personalized ranking
    ranker = RecommendationRanker(db, current_user.uuid)
    ranked_results = await ranker.rank_results(results, query)

    return {"results": ranked_results}
```

**Validation:**
```bash
# Test search with and without user history
# User with history → should see is_recommendation: true on some results
# New user → should see normal results (no is_recommendation)
```

**Expected Result:**
- Backend ranking boosts relevant results
- is_recommendation flag set correctly
- Privacy maintained (no query tracking)

---

### Subtask 3.4.4: Write Component Tests

**Duration:** 1 hour
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/frontend/src/__tests__/components/SearchWithRecommendations.test.tsx`

**Steps:**
1. Create test file with React Testing Library
2. Mock fetch API
3. Write test: Search input renders and handles input
4. Write test: Search results display correctly
5. Write test: Recommended results show indicator
6. Run tests and verify 3/3 passing

**Code Example:**
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SearchWithRecommendations } from '../../components/SearchWithRecommendations';

global.fetch = jest.fn();

describe('SearchWithRecommendations Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('search input renders and handles input changes', () => {
    render(<SearchWithRecommendations />);

    const input = screen.getByPlaceholderText(/search your knowledge graph/i);
    expect(input).toBeInTheDocument();

    fireEvent.change(input, { target: { value: 'ACME Corporation' } });
    expect(input).toHaveValue('ACME Corporation');
  });

  test('search results display with title and excerpt', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => ({
        results: [
          {
            uuid: 'doc-1',
            title: 'ACME Corporation Overview',
            excerpt: 'Leading supplier in industrial...',
            score: 0.95,
            is_recommendation: false
          }
        ]
      })
    });

    render(<SearchWithRecommendations />);

    const input = screen.getByPlaceholderText(/search your knowledge graph/i);
    fireEvent.change(input, { target: { value: 'ACME' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText('ACME Corporation Overview')).toBeInTheDocument();
      expect(screen.getByText(/Leading supplier in industrial/)).toBeInTheDocument();
    });
  });

  test('recommended results show subtle indicator', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      json: async () => ({
        results: [
          {
            uuid: 'doc-1',
            title: 'Recommended Doc',
            excerpt: 'This is a recommended document',
            score: 0.98,
            is_recommendation: true
          }
        ]
      })
    });

    render(<SearchWithRecommendations />);

    const input = screen.getByPlaceholderText(/search your knowledge graph/i);
    fireEvent.change(input, { target: { value: 'test' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText('Based on your recent activity')).toBeInTheDocument();
    });
  });
});
```

**Validation:**
```bash
# Run component tests
cd frontend
npm test -- SearchWithRecommendations.test.tsx

# Expected: 3/3 tests passing
```

**Expected Result:**
- 3/3 tests passing
- Input handling validated
- Results display validated
- Recommendation indicator validated

---

## Troubleshooting

**Common Issues:**

**Issue 1: Search not returning recommendations**
- See TROUBLESHOOTING.md:Lines 950-975
- Solution: Verify backend RecommendationRanker service implemented, check user has query history

**Issue 2: Styling not matching Apple design**
- See TROUBLESHOOTING.md:Lines 1000-1025
- Solution: Ensure rounded-2xl on input, bg-gray-50, hover:bg-gray-50 on results

**Issue 3: Enter key not triggering search**
- See TROUBLESHOOTING.md:Lines 1050-1075
- Solution: Use onKeyDown (not onKeyPress), check for e.key === 'Enter'

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 3.4.1: Create SearchWithRecommendations Component
- [ ] Subtask 3.4.2: Implement Results Display with Recommendations
- [ ] Subtask 3.4.3: Verify Backend Ranking Integration
- [ ] Subtask 3.4.4: Write Component Tests

**Tests:** 0/3 passing (0%)

**Last Updated:** 2025-10-21
