# Task 3.3: Minimal Gamification Components

**Phase:** 3 - Apple Minimalist Engagement Layer
**Status:** ✅ Complete
**Estimated Duration:** 6 hours (Day 3)
**Completed:** 2025-10-22

---

## Overview

Build ProfileAchievements component with monochrome icons, text-only streak display, and NO popups/toasts/leaderboards. Achievement display is hidden in profile page - never shown unless user explicitly visits.

---

## Dependencies

**Required Before Starting:**
- Task 3.1: Design System Foundation (requires design-system.ts constants)
- Task 3.2: Backend Engagement APIs (requires /api/v1/achievements/ endpoint)

**Enables After Completion:**
- Task 3.5: Hidden Dashboard & Briefings (shares minimalist design patterns)

---

## Success Criteria

✅ ProfileAchievements component renders achievements list
✅ Streak display is text-only (large number + "day streak" label)
✅ Monochrome icons used (⬡⬢⬣⬤⬥) - NO color emoji
✅ Earned achievements have normal opacity, unearned are dimmed (opacity-50)
✅ No popups, toasts, or notifications
✅ 4 frontend component tests passing
✅ Achievements page only accessible via profile menu (not landing page)
✅ Follows Apple minimalist design (generous spacing, subtle backgrounds)

---

## Research References

**Technical Documentation:**
- research/documentation/react-testing-library.md (Lines: 1-100)
  - Key concepts: Component testing, mocking, assertions

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2956-3024)
  - Complete ProfileAchievements component implementation

---

## Test Specifications

**Frontend Component Tests:** 4 tests
- TESTING.md: Lines 1546-1621 (ProfileAchievements test suite)

**Tests to pass:**
1. Displays current streak (7 → "7 day streak")
2. Displays earned achievements with title + description
3. Shows unearned achievements as dimmed (opacity-50)
4. Uses monochrome icons only (no color emoji like 🔍🤿🕵️)

**Total Tests:** 4

---

## Implementation Steps

### Subtask 3.3.1: Create ProfileAchievements Component Shell

**Duration:** 2 hours
**Status:** ✅ Complete

**Files to Create:**
- `apex-memory-system/frontend/src/components/ProfileAchievements.tsx`

**Steps:**
1. Create ProfileAchievements component file
2. Define TypeScript interfaces (Achievement, ProfileAchievementsProps)
3. Import design-system constants
4. Set up component structure (streak + achievements list)
5. Use Tailwind classes following design system
6. Export component

**Code Example:**
```typescript
// See IMPLEMENTATION.md lines 2960-3021 for complete code
import React from 'react';
import { spacing } from '@/styles/design-system';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string; // Monochrome icon: ⬡⬢⬣⬤⬥
  earned: boolean;
  earned_at?: string;
}

interface ProfileAchievementsProps {
  achievements: Achievement[];
  currentStreak: number;
}

export function ProfileAchievements({ achievements, currentStreak }: ProfileAchievementsProps) {
  return (
    <div className="max-w-2xl mx-auto p-8">
      {/* Streak Display - Text Only */}
      <div className="mb-12 text-center">
        <div className="text-6xl font-semibold text-gray-900">{currentStreak}</div>
        <div className="mt-2 text-sm text-gray-500">day streak</div>
      </div>

      {/* Achievements list will go here */}
    </div>
  );
}
```

**Validation:**
```bash
# Test TypeScript compilation
cd frontend
npm run type-check

# Visual test in browser
npm run dev
# Navigate to profile page
```

**Expected Result:**
- Component renders without errors
- TypeScript types correct
- Generous spacing applied (max-w-2xl, p-8)

---

### Subtask 3.3.2: Implement Achievements List

**Duration:** 2 hours
**Status:** ✅ Complete

**Files to Modify:**
- `apex-memory-system/frontend/src/components/ProfileAchievements.tsx` (add achievements rendering)

**Steps:**
1. Map over achievements array
2. Render each achievement with icon, title, description
3. Apply earned vs unearned styling (opacity-50 for unearned)
4. Show earned date if available
5. Use monochrome icons (⬡⬢⬣⬤⬥)
6. Apply subtle background (bg-gray-50) for earned achievements
7. Ensure no color emoji used

**Code Example:**
```typescript
{/* Achievements - Monochrome Icons */}
<div className="space-y-6">
  {achievements.map((achievement) => (
    <div
      key={achievement.id}
      className={`flex items-start gap-4 p-4 rounded-lg transition-all ${
        achievement.earned
          ? 'bg-gray-50'
          : 'bg-transparent opacity-50'
      }`}
    >
      {/* Monochrome icon */}
      <div className={`text-3xl ${achievement.earned ? 'text-gray-900' : 'text-gray-300'}`}>
        {achievement.icon}
      </div>

      {/* Text */}
      <div className="flex-1">
        <div className={`font-semibold ${achievement.earned ? 'text-gray-900' : 'text-gray-400'}`}>
          {achievement.title}
        </div>
        <div className="text-sm text-gray-500 mt-1">
          {achievement.description}
        </div>
        {achievement.earned && achievement.earned_at && (
          <div className="text-xs text-gray-400 mt-2">
            Earned {new Date(achievement.earned_at).toLocaleDateString()}
          </div>
        )}
      </div>
    </div>
  ))}
</div>
```

**Validation:**
```bash
# Visual test with mock data
const mockAchievements = [
  {
    id: '1',
    title: 'First Query',
    description: 'Performed your first query',
    icon: '⬡',
    earned: true,
    earned_at: '2025-10-01'
  },
  {
    id: '2',
    title: 'Explorer',
    description: 'Explored 10 different entities',
    icon: '⬢',
    earned: false
  }
];

<ProfileAchievements achievements={mockAchievements} currentStreak={7} />
```

**Expected Result:**
- Earned achievements show with bg-gray-50
- Unearned achievements dimmed (opacity-50)
- Monochrome icons displayed correctly
- Earned date formatted properly

---

### Subtask 3.3.3: Wire to Backend API

**Duration:** 1 hour
**Status:** ✅ Complete

**Files to Create:**
- `apex-memory-system/frontend/src/hooks/useAchievements.ts`

**Files to Modify:**
- `apex-memory-system/frontend/src/pages/Profile.tsx` (integrate ProfileAchievements)

**Steps:**
1. Create useAchievements hook
2. Fetch achievements from /api/v1/achievements/
3. Fetch current streak from /api/v1/achievements/stats
4. Handle loading and error states
5. Integrate ProfileAchievements into Profile page
6. Add route to Profile page (not landing page)

**Code Example:**
```typescript
// useAchievements.ts
import { useState, useEffect } from 'react';
import axios from 'axios';

export function useAchievements() {
  const [achievements, setAchievements] = useState([]);
  const [currentStreak, setCurrentStreak] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAchievements = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const [achievementsRes, statsRes] = await Promise.all([
          axios.get('/api/v1/achievements/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('/api/v1/achievements/stats', {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        setAchievements(achievementsRes.data.achievements);
        setCurrentStreak(statsRes.data.current_streak);
      } catch (error) {
        console.error('Failed to fetch achievements:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAchievements();
  }, []);

  return { achievements, currentStreak, loading };
}
```

**Validation:**
```bash
# Test in browser
# Navigate to /profile
# Verify achievements load from API
# Check Network tab for API calls
```

**Expected Result:**
- Achievements load from backend
- Current streak displayed correctly
- Profile page shows achievements
- No errors in console

---

### Subtask 3.3.4: Write Component Tests

**Duration:** 1 hour
**Status:** ✅ Complete

**Files to Create:**
- `apex-memory-system/frontend/src/__tests__/components/ProfileAchievements.test.tsx`

**Steps:**
1. Create test file with React Testing Library
2. Write test: Displays current streak
3. Write test: Displays earned achievements
4. Write test: Shows unearned achievements as dimmed
5. Write test: Uses monochrome icons only (no color emoji)
6. Run all tests and verify 4/4 passing

**Code Example:**
```typescript
// See TESTING.md lines 1548-1621 for complete code
import { render, screen } from '@testing-library/react';
import { ProfileAchievements } from '../../components/ProfileAchievements';

describe('ProfileAchievements Component', () => {
  const mockAchievements = [
    {
      id: '1',
      title: 'First Query',
      description: 'Performed your first query',
      icon: '⬡',
      earned: true,
      earned_at: '2025-10-01'
    },
    {
      id: '2',
      title: 'Explorer',
      description: 'Explored 10 different entities',
      icon: '⬢',
      earned: false
    }
  ];

  test('displays current streak', () => {
    render(
      <ProfileAchievements
        achievements={mockAchievements}
        currentStreak={7}
      />
    );

    expect(screen.getByText('7')).toBeInTheDocument();
    expect(screen.getByText('day streak')).toBeInTheDocument();
  });

  test('displays earned achievements', () => {
    render(
      <ProfileAchievements
        achievements={mockAchievements}
        currentStreak={7}
      />
    );

    expect(screen.getByText('First Query')).toBeInTheDocument();
    expect(screen.getByText('Performed your first query')).toBeInTheDocument();
  });

  test('shows unearned achievements as dimmed', () => {
    const { container } = render(
      <ProfileAchievements
        achievements={mockAchievements}
        currentStreak={7}
      />
    );

    const unearnedAchievement = container.querySelector('.opacity-50');
    expect(unearnedAchievement).toBeInTheDocument();
  });

  test('uses monochrome icons only', () => {
    render(
      <ProfileAchievements
        achievements={mockAchievements}
        currentStreak={7}
      />
    );

    // Verify no color emoji
    expect(screen.queryByText(/🔍|🤿|🕵️/)).not.toBeInTheDocument();

    // Verify monochrome shapes used
    expect(screen.getByText('⬡')).toBeInTheDocument();
  });
});
```

**Validation:**
```bash
# Run component tests
cd frontend
npm test -- ProfileAchievements.test.tsx

# Expected: 4/4 tests passing
```

**Expected Result:**
- 4/4 tests passing
- Streak display validated
- Monochrome icon enforcement validated
- Dimmed unearned achievements validated

---

## Troubleshooting

**Common Issues:**

**Issue 1: Icons not rendering**
- See TROUBLESHOOTING.md:Lines 800-825
- Solution: Ensure UTF-8 encoding in component file, use Unicode characters directly

**Issue 2: Achievements not loading**
- See TROUBLESHOOTING.md:Lines 850-875
- Solution: Verify backend API running, check auth token in localStorage, inspect Network tab

**Issue 3: Styling not matching Apple aesthetic**
- See TROUBLESHOOTING.md:Lines 900-925
- Solution: Review design-system.ts constants, ensure generous spacing (p-8, mb-12, space-y-6)

---

## Progress Tracking

**Subtasks:** 4/4 complete (100%) ✅

- [x] Subtask 3.3.1: Create ProfileAchievements Component Shell
- [x] Subtask 3.3.2: Implement Achievements List
- [x] Subtask 3.3.3: Wire to Backend API
- [x] Subtask 3.3.4: Write Component Tests

**Tests:** 4/4 passing (100%) ✅

**Last Updated:** 2025-10-22
**Status:** ✅ Complete
