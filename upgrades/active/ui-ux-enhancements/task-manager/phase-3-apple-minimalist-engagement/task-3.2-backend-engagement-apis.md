# Task 3.2: Backend Engagement APIs

**Phase:** 3 - Apple Minimalist Engagement Layer
**Status:** ⬜ Not Started
**Estimated Duration:** 12 hours (Days 1-2)
**Assigned To:** (filled during execution)

---

## Overview

Build backend APIs for subtle engagement features: AI-generated briefings, achievement tracking, enhanced search recommendations, and privacy-first analytics. All designed to be invisible - no popups, no notifications, only when user explicitly checks.

---

## Dependencies

**Required Before Starting:**
- Task 1.1: Backend Authentication (requires User model and auth middleware)
- Task 2.2: Backend Conversation API (requires database models pattern)
- Phase 2 complete (existing API structure)

**Enables After Completion:**
- Task 3.3: Minimal Gamification Components
- Task 3.4: Integrated Recommendations
- Task 3.5: Hidden Dashboard & Briefings

---

## Success Criteria

✅ Briefings API (`/api/v1/briefings/`) with CRUD endpoints
✅ Achievements API (`/api/v1/achievements/`) with tracking logic
✅ Analytics API (`/api/v1/analytics/`) with privacy-first metrics
✅ Enhanced search with recommendation ranking
✅ All 20 backend tests passing (5 per API endpoint group)
✅ Database models created (Briefing, Achievement, UserMetric)
✅ Background jobs for briefing generation (daily digest)
✅ No user-facing notifications (pull-based only)

---

## Research References

**Technical Documentation:**
- research/documentation/fastapi-best-practices.md (Lines: 1-150)
  - Key concepts: Router patterns, dependency injection, background tasks

**Implementation Guide:**
- IMPLEMENTATION.md (Lines: 2881-3253)
  - References to `/api/v1/briefings/latest` and engagement patterns

**Note:** Backend implementation details not explicitly in IMPLEMENTATION.md - inferred from frontend usage. This task defines the missing backend APIs needed by frontend components.

---

## Test Specifications

**Backend Tests:** 20 tests total (5 tests per API group)
- TESTING.md: Lines 1538-1760 (Phase 3 testing section)
- **Note:** Backend test details not explicitly documented. Create tests following Phase 1/2 patterns.

**Test Coverage:**
- Briefings API: 5 tests (create, get latest, mark read, list, permissions)
- Achievements API: 5 tests (track event, get achievements, unlock logic, stats, permissions)
- Analytics API: 5 tests (record event, get metrics, privacy filters, aggregation, permissions)
- Search Recommendations: 5 tests (rank results, personalization, privacy, caching, fallback)

---

## Implementation Steps

### Subtask 3.2.1: Create Database Models

**Duration:** 3 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/src/apex_memory/models/briefing.py`
- `apex-memory-system/src/apex_memory/models/achievement.py`
- `apex-memory-system/src/apex_memory/models/user_metric.py`

**Steps:**
1. Create Briefing model (id, user_id, title, content, generated_at, read_at)
2. Create Achievement model (id, user_id, achievement_type, unlocked_at, metadata)
3. Create UserMetric model (id, user_id, metric_type, value, timestamp)
4. Add Alembic migrations for all 3 tables
5. Create Pydantic schemas for request/response
6. Add foreign key constraints to User model

**Code Example:**
```python
# briefing.py
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from apex_memory.models.base import Base


class BriefingDB(Base):
    """Briefing database model."""

    __tablename__ = "briefings"

    uuid = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    generated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    read_at = Column(TIMESTAMP, nullable=True)


class Briefing(BaseModel):
    """Briefing response schema."""

    uuid: UUID
    title: str
    content: str
    generated_at: datetime
    read_at: datetime | None = None
    has_unread: bool = False

    class Config:
        from_attributes = True
```

**Validation:**
```bash
# Create migration
cd apex-memory-system
alembic revision --autogenerate -m "Add briefing, achievement, user_metric tables"

# Apply migration
alembic upgrade head

# Verify tables created
psql -U apex -d apex_memory -c "\d briefings"
```

**Expected Result:**
- 3 new database tables created
- Foreign key constraints to users table
- Pydantic schemas for all models
- Migration applied successfully

---

### Subtask 3.2.2: Build Briefings API

**Duration:** 3 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/src/apex_memory/api/briefings.py`
- `apex-memory-system/tests/unit/test_briefings.py` (5 tests)

**Steps:**
1. Create FastAPI router (`/api/v1/briefings/`)
2. Implement GET /latest endpoint (returns most recent unread briefing)
3. Implement POST /mark_read/{briefing_id} endpoint
4. Implement GET / endpoint (list all briefings with pagination)
5. Add authentication dependency (current_user)
6. Create background task for daily briefing generation
7. Wire briefing generation to graph analysis service
8. Write 5 unit tests

**Code Example:**
```python
# briefings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apex_memory.api.auth import get_current_user
from apex_memory.database import get_db
from apex_memory.models.briefing import Briefing, BriefingDB
from apex_memory.models.user import User

router = APIRouter(prefix="/api/v1/briefings", tags=["briefings"])


@router.get("/latest")
async def get_latest_briefing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get latest briefing and check for unread status."""
    latest = db.query(BriefingDB).filter(
        BriefingDB.user_id == current_user.uuid
    ).order_by(BriefingDB.generated_at.desc()).first()

    if not latest:
        return {"has_unread": False, "briefing": None}

    has_unread = latest.read_at is None

    return {
        "has_unread": has_unread,
        "briefing": Briefing.from_orm(latest) if has_unread else None
    }


@router.post("/mark_read/{briefing_id}")
async def mark_briefing_read(
    briefing_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Briefing:
    """Mark briefing as read."""
    briefing = db.query(BriefingDB).filter(
        BriefingDB.uuid == briefing_id,
        BriefingDB.user_id == current_user.uuid
    ).first()

    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")

    briefing.read_at = datetime.utcnow()
    db.commit()

    return Briefing.from_orm(briefing)
```

**Validation:**
```bash
# Test endpoints
curl -X GET http://localhost:8000/api/v1/briefings/latest \
  -H "Authorization: Bearer <token>"

# Run unit tests
pytest tests/unit/test_briefings.py -v
```

**Expected Result:**
- GET /latest returns briefing status
- POST /mark_read updates read timestamp
- 5/5 tests passing
- User isolation enforced (can't read other users' briefings)

---

### Subtask 3.2.3: Build Achievements API

**Duration:** 3 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/src/apex_memory/api/achievements.py`
- `apex-memory-system/src/apex_memory/services/achievement_tracker.py`
- `apex-memory-system/tests/unit/test_achievements.py` (5 tests)

**Steps:**
1. Define achievement types (FIRST_QUERY, EXPLORER_10_ENTITIES, WEEK_STREAK_7, etc.)
2. Create AchievementTracker service class
3. Implement track_event() method (called after queries, ingestions, etc.)
4. Implement unlock logic (check conditions, create AchievementDB record)
5. Create GET /achievements endpoint (returns all achievements with earned status)
6. Create GET /stats endpoint (current streak, total achievements, etc.)
7. Wire tracker to existing query/ingestion endpoints
8. Write 5 unit tests

**Code Example:**
```python
# achievement_tracker.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from apex_memory.models.achievement import AchievementDB, AchievementType


class AchievementTracker:
    """Tracks and unlocks user achievements."""

    ACHIEVEMENT_DEFINITIONS = {
        AchievementType.FIRST_QUERY: {
            "title": "First Query",
            "description": "Performed your first query",
            "icon": "⬡",
            "condition": lambda stats: stats["query_count"] >= 1
        },
        AchievementType.EXPLORER_10: {
            "title": "Explorer",
            "description": "Explored 10 different entities",
            "icon": "⬢",
            "condition": lambda stats: stats["unique_entities"] >= 10
        },
        # ... more achievements
    }

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    async def track_event(self, event_type: str, metadata: dict = None):
        """Track user event and check for achievement unlocks."""
        # Get current user stats
        stats = await self._get_user_stats()

        # Check all achievement conditions
        for achievement_type, definition in self.ACHIEVEMENT_DEFINITIONS.items():
            if self._is_unlocked(achievement_type):
                continue

            if definition["condition"](stats):
                await self._unlock_achievement(achievement_type)

    def _is_unlocked(self, achievement_type: AchievementType) -> bool:
        """Check if achievement already unlocked."""
        return self.db.query(AchievementDB).filter(
            AchievementDB.user_id == self.user_id,
            AchievementDB.achievement_type == achievement_type
        ).first() is not None
```

**Validation:**
```bash
# Test achievement unlock
# Perform first query → should unlock FIRST_QUERY achievement

# Run unit tests
pytest tests/unit/test_achievements.py -v
```

**Expected Result:**
- Achievement tracking works automatically
- Unlock conditions evaluated correctly
- GET /achievements returns earned status
- 5/5 tests passing

---

### Subtask 3.2.4: Build Analytics API and Search Enhancement

**Duration:** 3 hours
**Status:** ⬜ Not Started

**Files to Create:**
- `apex-memory-system/src/apex_memory/api/analytics.py`
- `apex-memory-system/src/apex_memory/services/recommendation_ranker.py`
- `apex-memory-system/tests/unit/test_analytics.py` (5 tests)
- `apex-memory-system/tests/unit/test_recommendations.py` (5 tests)

**Steps:**
1. Create UserMetric tracking (privacy-first: aggregate only, no PII)
2. Implement POST /analytics/event endpoint (record query, view, etc.)
3. Implement GET /analytics/metrics endpoint (return dashboard metrics)
4. Create RecommendationRanker service
5. Enhance existing search to boost results based on user history
6. Add privacy filters (no tracking of query content, only metadata)
7. Write 10 tests total (5 analytics + 5 recommendations)

**Code Example:**
```python
# analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apex_memory.api.auth import get_current_user
from apex_memory.database import get_db
from apex_memory.models.user_metric import UserMetricDB, MetricType

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.post("/event")
async def record_event(
    event_type: MetricType,
    metadata: dict = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record analytics event (privacy-first: no content tracking)."""
    metric = UserMetricDB(
        user_id=current_user.uuid,
        metric_type=event_type,
        value=1,  # Increment counter
        # NO query content stored, only metadata like timestamp
    )
    db.add(metric)
    db.commit()

    return {"status": "recorded"}


@router.get("/metrics")
async def get_metrics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics (aggregated only)."""
    from sqlalchemy import func

    query_count = db.query(func.count(UserMetricDB.uuid)).filter(
        UserMetricDB.user_id == current_user.uuid,
        UserMetricDB.metric_type == MetricType.QUERY
    ).scalar()

    # ... aggregate other metrics

    return {
        "query_count": query_count,
        "documents_ingested": 0,  # From ingestion logs
        "entities_tracked": 0,     # From graph
    }
```

**Validation:**
```bash
# Test analytics recording
curl -X POST http://localhost:8000/api/v1/analytics/event \
  -H "Authorization: Bearer <token>" \
  -d '{"event_type": "QUERY"}'

# Run tests
pytest tests/unit/test_analytics.py tests/unit/test_recommendations.py -v
```

**Expected Result:**
- Analytics recorded without PII
- Metrics API returns dashboard data
- Search recommendations boost relevant results
- 10/10 tests passing

---

## Troubleshooting

**Common Issues:**

**Issue 1: Briefing generation slow**
- See TROUBLESHOOTING.md:Lines 650-675
- Solution: Use background tasks, cache graph analysis, run daily digest job

**Issue 2: Achievement conditions complex**
- See TROUBLESHOOTING.md:Lines 700-725
- Solution: Keep conditions simple (count-based), avoid complex graph queries

**Issue 3: Privacy concerns with analytics**
- See TROUBLESHOOTING.md:Lines 750-775
- Solution: Never store query content, only aggregate counts and timestamps

---

## Progress Tracking

**Subtasks:** 0/4 complete (0%)

- [ ] Subtask 3.2.1: Create Database Models
- [ ] Subtask 3.2.2: Build Briefings API
- [ ] Subtask 3.2.3: Build Achievements API
- [ ] Subtask 3.2.4: Build Analytics API and Search Enhancement

**Tests:** 0/20 passing (0%)

**Last Updated:** 2025-10-21
