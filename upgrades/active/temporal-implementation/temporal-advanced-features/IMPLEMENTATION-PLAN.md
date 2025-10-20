# IMPLEMENTATION PLAN: Advanced Temporal Features

**Project:** Apex Memory System - Temporal Implementation (Sections 12, 14, 16)
**Status:** 📝 Ready for Implementation
**Timeline:** 7-8 hours (3 sections)
**Created:** 2025-10-20

---

## 🎯 Executive Summary

This implementation plan covers the final 3 critical sections of the Temporal integration:

1. **Section 14: Search Attributes** (2 hours) - Enable workflow searchability in Temporal UI
2. **Section 12: Polling Workflows** (3 hours) - Periodic API polling with continue-as-new pattern
3. **Section 16: OpenTelemetry** (3 hours) - Distributed tracing for complete observability

**Why These Sections:**
- Search Attributes → Better debugging and operational visibility
- Polling Workflows → Business capability for non-webhook integrations
- OpenTelemetry → Advanced observability (traces + metrics + logs)

**Prerequisites:**
- ✅ Sections 1-10 complete (Temporal foundation + testing)
- ✅ graphiti-json-integration complete (2 workflows operational)

---

## 📋 Table of Contents

1. [Section 14: Search Attributes](#section-14-search-attributes)
   - Configuration Script
   - Workflow Updates
   - Search Examples
   - Testing

2. [Section 12: Polling Workflows](#section-12-polling-workflows)
   - PollingWorkflow Implementation
   - Continue-As-New Pattern
   - Fetch New Records Activity
   - Testing

3. [Section 16: OpenTelemetry Integration](#section-16-opentelemetry-integration)
   - Telemetry Configuration
   - OTLP Exporter Setup
   - Trace Instrumentation
   - Jaeger Integration
   - Testing

4. [Testing Strategy](#testing-strategy)
5. [Success Criteria](#success-criteria)
6. [References](#references)

---

## SECTION 14: Search Attributes (2 hours)

### Overview

Search attributes enable filtering and searching workflows in the Temporal UI by custom metadata. This dramatically improves operational visibility and debugging.

**What You'll Build:**
- 4 custom search attributes (Source, Priority, DocumentId, Status)
- Configuration script to register attributes
- Updated workflow starts to tag attributes
- Search query examples

**Research Foundation:**
- **Temporal Docs:** https://docs.temporal.io/visibility#search-attribute
- **Search Attribute Types:** https://docs.temporal.io/visibility#search-attribute-types

---

### Step 1: Create Search Attribute Configuration Script (30 min)

**File:** `apex-memory-system/scripts/temporal/configure-search-attributes.sh`

**Purpose:** Register 4 custom search attributes with Temporal Server

**Implementation:**

```bash
#!/bin/bash
# Configure Temporal search attributes for Apex Memory System
#
# This script registers custom search attributes that enable filtering
# and searching workflows in the Temporal UI.
#
# Usage: ./configure-search-attributes.sh
#
# Prerequisites:
# - Temporal CLI installed (temporal)
# - Temporal Server running on localhost:7233
# - Temporal namespace 'default' exists

set -e

echo "🔍 Configuring Temporal Search Attributes..."
echo ""

# Define search attributes
# Format: <name>:<type>
ATTRIBUTES=(
    "Source:Keyword"          # Source system (frontapp, turvo, samsara, api, etc.)
    "Priority:Int"            # Priority level (1=low, 2=medium, 3=high, 4=urgent)
    "DocumentId:Keyword"      # Document UUID for tracking
    "Status:Keyword"          # Workflow status (pending, processing, completed, failed)
)

# Register each attribute
for attr in "${ATTRIBUTES[@]}"; do
    IFS=':' read -r name type <<< "$attr"

    echo "→ Registering: $name (type: $type)"

    temporal operator search-attribute create \
        --namespace default \
        --name "$name" \
        --type "$type" 2>&1 | grep -v "already exists" || true
done

echo ""
echo "✅ Search attributes configured successfully"
echo ""
echo "Registered attributes:"
temporal operator search-attribute list --namespace default

echo ""
echo "📝 Usage Examples:"
echo "  Search by source:      Source='frontapp'"
echo "  Search by document:    DocumentId='doc-abc-123'"
echo "  Search by priority:    Priority>=3"
echo "  Search by status:      Status='completed'"
echo "  Combined search:       Source='turvo' AND Priority=3"
```

**Validation:**

```bash
# Make executable
chmod +x apex-memory-system/scripts/temporal/configure-search-attributes.sh

# Run script
cd apex-memory-system
./scripts/temporal/configure-search-attributes.sh

# Verify attributes registered
temporal operator search-attribute list --namespace default

# Expected output:
# +-------------+---------+
# | Name        | Type    |
# +-------------+---------+
# | Source      | Keyword |
# | Priority    | Int     |
# | DocumentId  | Keyword |
# | Status      | Keyword |
# +-------------+---------+
```

---

### Step 2: Update DocumentIngestionWorkflow (30 min)

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`

**Changes:** Add search attributes to workflow execution options

**Location:** Modify the workflow start in `api/ingestion.py` where workflows are triggered

**Before:**
```python
# In api/ingestion.py (line ~180)
handle = await temporal_client.start_workflow(
    DocumentIngestionWorkflow.run,
    document_id,
    source,
    source_location,
    id=workflow_id,
    task_queue="apex-ingestion-queue",
)
```

**After:**
```python
from temporalio.client import WorkflowHandle
from temporalio.common import SearchAttributeKey, SearchAttributeValues

# Define search attribute keys (at module level)
SOURCE_ATTR = SearchAttributeKey.for_keyword("Source")
PRIORITY_ATTR = SearchAttributeKey.for_int("Priority")
DOCUMENT_ID_ATTR = SearchAttributeKey.for_keyword("DocumentId")
STATUS_ATTR = SearchAttributeKey.for_keyword("Status")

# In api/ingestion.py (line ~180)
# Determine priority based on source
priority = 3 if source == "frontapp" else 2  # FrontApp = high priority

handle = await temporal_client.start_workflow(
    DocumentIngestionWorkflow.run,
    document_id,
    source,
    source_location,
    id=workflow_id,
    task_queue="apex-ingestion-queue",
    search_attributes={
        SOURCE_ATTR: [source],
        PRIORITY_ATTR: [priority],
        DOCUMENT_ID_ATTR: [document_id],
        STATUS_ATTR: ["pending"],
    },
)
```

**Update Workflow Status During Execution:**

Add status updates inside the workflow as it progresses:

```python
# Inside DocumentIngestionWorkflow.run() method
# After parse_document_activity completes

from temporalio import workflow

# Update status to 'processing'
workflow.upsert_search_attributes({
    STATUS_ATTR: ["processing"],
})

# ... workflow continues ...

# Before returning (success case)
workflow.upsert_search_attributes({
    STATUS_ATTR: ["completed"],
})

# In error handler (failure case)
workflow.upsert_search_attributes({
    STATUS_ATTR: ["failed"],
})
```

---

### Step 3: Update StructuredDataIngestionWorkflow (20 min)

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`

**Changes:** Apply same search attributes to structured data workflow

**In api/ingestion.py (structured data endpoint, line ~600):**

```python
# POST /api/v1/ingest/structured
handle = await temporal_client.start_workflow(
    StructuredDataIngestionWorkflow.run,
    structured_data_id,
    source,
    data_type,
    raw_json,
    id=workflow_id,
    task_queue="apex-ingestion-queue",
    search_attributes={
        SOURCE_ATTR: [source],
        PRIORITY_ATTR: [priority],
        DOCUMENT_ID_ATTR: [structured_data_id],
        STATUS_ATTR: ["pending"],
    },
)
```

**In StructuredDataIngestionWorkflow:**

```python
# Update status as workflow progresses
workflow.upsert_search_attributes({STATUS_ATTR: ["processing"]})

# On completion
workflow.upsert_search_attributes({STATUS_ATTR: ["completed"]})

# On failure
workflow.upsert_search_attributes({STATUS_ATTR: ["failed"]})
```

---

### Step 4: Create Search Query Examples (20 min)

**File:** `apex-memory-system/examples/search/search-workflows.py`

**Purpose:** Demonstrate how to search workflows programmatically

```python
"""
Search Workflow Examples

Demonstrates how to search for workflows using custom search attributes.

Usage:
    python examples/search/search-workflows.py
"""

import asyncio
from temporalio.client import Client


async def search_by_source(client: Client, source: str):
    """Search workflows by source system."""
    query = f"Source='{source}'"

    print(f"🔍 Searching for workflows from source: {source}")
    print(f"   Query: {query}")

    async for workflow in client.list_workflows(query=query):
        print(f"   - {workflow.id} ({workflow.status})")


async def search_high_priority(client: Client):
    """Search for high-priority workflows (priority >= 3)."""
    query = "Priority>=3"

    print(f"🔍 Searching for high-priority workflows")
    print(f"   Query: {query}")

    async for workflow in client.list_workflows(query=query):
        print(f"   - {workflow.id} (Priority: {workflow.search_attributes.get('Priority')})")


async def search_failed_workflows(client: Client):
    """Search for failed workflows."""
    query = "Status='failed'"

    print(f"🔍 Searching for failed workflows")
    print(f"   Query: {query}")

    async for workflow in client.list_workflows(query=query):
        print(f"   - {workflow.id}")


async def search_by_document_id(client: Client, document_id: str):
    """Find workflow for specific document."""
    query = f"DocumentId='{document_id}'"

    print(f"🔍 Searching for document: {document_id}")
    print(f"   Query: {query}")

    async for workflow in client.list_workflows(query=query):
        print(f"   - Found: {workflow.id}")
        print(f"     Status: {workflow.status}")
        print(f"     Source: {workflow.search_attributes.get('Source')}")


async def combined_search(client: Client):
    """Search with multiple criteria."""
    query = "Source='turvo' AND Priority=3 AND Status='processing'"

    print(f"🔍 Combined search (Turvo + High Priority + Processing)")
    print(f"   Query: {query}")

    async for workflow in client.list_workflows(query=query):
        print(f"   - {workflow.id}")


async def main():
    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    print("=" * 60)
    print("Temporal Search Attribute Examples")
    print("=" * 60)
    print()

    # Example searches
    await search_by_source(client, "frontapp")
    print()

    await search_high_priority(client)
    print()

    await search_failed_workflows(client)
    print()

    await search_by_document_id(client, "doc-abc-123")
    print()

    await combined_search(client)


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Step 5: Testing (20 min)

**File:** `apex-memory-system/tests/integration/test_search_attributes.py`

**Tests to Create (10 tests):**

```python
"""
Test Suite: Temporal Search Attributes

Validates that workflows are properly tagged with search attributes
and can be queried via Temporal UI and API.
"""

import pytest
import uuid
from temporalio.client import Client
from apex_memory.temporal.workflows.ingestion import (
    DocumentIngestionWorkflow,
    StructuredDataIngestionWorkflow,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_search_attributes_configured():
    """TEST 1: Verify search attributes are registered in Temporal."""
    client = await Client.connect("localhost:7233")

    # Query Temporal for registered search attributes
    # (This would use temporal operator search-attribute list)
    # For now, we validate by attempting to use them

    # If attributes aren't configured, this will fail
    query = "Source='test'"
    workflows = []
    async for wf in client.list_workflows(query=query):
        workflows.append(wf)

    # If we get here without error, attributes are configured
    assert True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_document_workflow_with_source_attribute():
    """TEST 2: Document workflow tagged with Source attribute."""
    client = await Client.connect("localhost:7233")

    document_id = f"test-doc-{uuid.uuid4()}"
    source = "frontapp"

    # Start workflow with search attributes
    handle = await client.start_workflow(
        DocumentIngestionWorkflow.run,
        document_id,
        source,
        "/tmp/test.pdf",
        id=f"ingest-{document_id}",
        task_queue="apex-ingestion-queue",
        search_attributes={
            "Source": [source],
            "DocumentId": [document_id],
            "Status": ["pending"],
        },
    )

    # Wait briefly
    await asyncio.sleep(1)

    # Search for workflow
    query = f"Source='{source}'"
    found = False
    async for wf in client.list_workflows(query=query):
        if wf.id == handle.id:
            found = True
            break

    assert found, "Workflow not found by Source attribute"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_workflow_with_priority_attribute():
    """TEST 3: Workflow tagged with Priority attribute."""
    client = await Client.connect("localhost:7233")

    document_id = f"test-doc-{uuid.uuid4()}"
    priority = 3  # High priority

    handle = await client.start_workflow(
        DocumentIngestionWorkflow.run,
        document_id,
        "frontapp",
        "/tmp/test.pdf",
        id=f"ingest-{document_id}",
        task_queue="apex-ingestion-queue",
        search_attributes={
            "Source": ["frontapp"],
            "Priority": [priority],
            "DocumentId": [document_id],
            "Status": ["pending"],
        },
    )

    await asyncio.sleep(1)

    # Search for high-priority workflows
    query = "Priority>=3"
    found = False
    async for wf in client.list_workflows(query=query):
        if wf.id == handle.id:
            found = True
            assert wf.search_attributes.get("Priority") == priority
            break

    assert found, "Workflow not found by Priority attribute"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_workflow_with_document_id_attribute():
    """TEST 4: Workflow searchable by DocumentId."""
    client = await Client.connect("localhost:7233")

    document_id = f"test-doc-{uuid.uuid4()}"

    handle = await client.start_workflow(
        DocumentIngestionWorkflow.run,
        document_id,
        "api",
        "/tmp/test.pdf",
        id=f"ingest-{document_id}",
        task_queue="apex-ingestion-queue",
        search_attributes={
            "Source": ["api"],
            "DocumentId": [document_id],
            "Status": ["pending"],
        },
    )

    await asyncio.sleep(1)

    # Search by exact document ID
    query = f"DocumentId='{document_id}'"
    found = False
    async for wf in client.list_workflows(query=query):
        if wf.id == handle.id:
            found = True
            break

    assert found, "Workflow not found by DocumentId"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_workflow_status_updates():
    """TEST 5: Status attribute updates as workflow progresses."""
    client = await Client.connect("localhost:7233")

    document_id = f"test-doc-{uuid.uuid4()}"

    handle = await client.start_workflow(
        DocumentIngestionWorkflow.run,
        document_id,
        "api",
        "/tmp/test.pdf",
        id=f"ingest-{document_id}",
        task_queue="apex-ingestion-queue",
        search_attributes={
            "Status": ["pending"],
        },
    )

    # Check initial status
    workflow = await client.describe_workflow(handle.id)
    assert workflow.search_attributes.get("Status") == "pending"

    # Wait for status to change to 'processing'
    await asyncio.sleep(5)

    workflow = await client.describe_workflow(handle.id)
    status = workflow.search_attributes.get("Status")
    assert status in ["processing", "completed"], f"Unexpected status: {status}"


# TEST 6-10: Additional search queries, combined searches, error cases
# (Similar pattern to above tests)
```

---

### Success Criteria (Section 14)

✅ Configuration script runs without errors
✅ 4 search attributes registered (Source, Priority, DocumentId, Status)
✅ DocumentIngestionWorkflow tagged with all attributes
✅ StructuredDataIngestionWorkflow tagged with all attributes
✅ Status updates as workflow progresses
✅ Search queries work in Temporal UI
✅ All 10 tests passing

---

## SECTION 12: Polling Workflows (3 hours)

### Overview

Polling workflows enable periodic data fetching from external APIs that don't support webhooks. The continue-as-new pattern prevents unbounded workflow history.

**What You'll Build:**
- `PollingWorkflow` - runs indefinitely with 15-minute intervals
- `fetch_new_records` activity - source-agnostic polling
- Continue-as-new pattern (every 100 iterations)
- Child workflow spawning for each fetched record

**Research Foundation:**
- **Continue-As-New:** https://docs.temporal.io/workflows#continue-as-new
- **Sleep API:** https://docs.temporal.io/workflows#sleep
- **Child Workflows:** https://docs.temporal.io/workflows#child-workflows

---

### Step 1: Create fetch_new_records Activity (45 min)

**File:** `apex-memory-system/src/apex_memory/temporal/activities/polling.py`

**Purpose:** Fetch new records from external APIs (Samsara, Turvo, custom)

```python
"""
Polling Activities

Activities for periodic data fetching from external APIs.

Supports:
- Samsara GPS events
- Turvo shipment updates
- Custom API polling

Author: Apex Infrastructure Team
Created: 2025-10-20
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from temporalio import activity
import httpx

from apex_memory.config.settings import Settings

logger = logging.getLogger(__name__)


@activity.defn
async def fetch_new_records_activity(
    source: str,
    since_timestamp: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, any]:
    """Fetch new records from external API.

    This activity polls external APIs for new data since the last fetch.
    Supports multiple source systems with configurable polling logic.

    Args:
        source: Source system to poll ("samsara", "turvo", "custom").
        since_timestamp: ISO timestamp of last fetch (None for initial fetch).
        limit: Maximum records to fetch per poll (default: 100).

    Returns:
        Dictionary containing:
        - records: List of fetched records (dicts)
        - next_timestamp: Timestamp for next fetch
        - count: Number of records fetched
        - has_more: Boolean indicating if more records available

    Raises:
        ValueError: If source is unsupported
        httpx.HTTPError: If API request fails

    Example:
        >>> result = await fetch_new_records_activity("samsara", "2024-10-20T10:00:00Z", 50)
        >>> print(result)
        {
            "records": [{...}, {...}],
            "next_timestamp": "2024-10-20T10:15:00Z",
            "count": 2,
            "has_more": False
        }
    """
    info = activity.info()
    settings = Settings()

    logger.info(
        f"Fetching new records from {source}",
        extra={
            "workflow_id": info.workflow_id,
            "source": source,
            "since_timestamp": since_timestamp,
            "limit": limit,
            "attempt": info.attempt,
        },
    )

    # Default to last 15 minutes if no timestamp provided
    if since_timestamp is None:
        since_dt = datetime.utcnow() - timedelta(minutes=15)
        since_timestamp = since_dt.isoformat() + "Z"

    records = []
    next_timestamp = datetime.utcnow().isoformat() + "Z"

    try:
        if source == "samsara":
            records = await _fetch_samsara_gps_events(settings, since_timestamp, limit)
        elif source == "turvo":
            records = await _fetch_turvo_shipments(settings, since_timestamp, limit)
        elif source == "custom":
            records = await _fetch_custom_api(settings, since_timestamp, limit)
        else:
            raise ValueError(f"Unsupported polling source: {source}")

        logger.info(
            f"Fetched {len(records)} records from {source}",
            extra={
                "workflow_id": info.workflow_id,
                "source": source,
                "count": len(records),
            },
        )

        return {
            "records": records,
            "next_timestamp": next_timestamp,
            "count": len(records),
            "has_more": len(records) >= limit,  # May have more if we hit limit
        }

    except httpx.HTTPError as e:
        logger.error(
            f"HTTP error fetching from {source}: {e}",
            extra={
                "workflow_id": info.workflow_id,
                "source": source,
                "error": str(e),
            },
            exc_info=True,
        )
        raise

    except Exception as e:
        logger.error(
            f"Failed to fetch records from {source}: {e}",
            extra={
                "workflow_id": info.workflow_id,
                "source": source,
                "error": str(e),
            },
            exc_info=True,
        )
        raise


async def _fetch_samsara_gps_events(
    settings: Settings,
    since_timestamp: str,
    limit: int,
) -> List[Dict]:
    """Fetch GPS events from Samsara API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.samsara.com/fleet/locations",
            headers={
                "Authorization": f"Bearer {settings.samsara_api_key}",
                "Accept": "application/json",
            },
            params={
                "startMs": _iso_to_ms(since_timestamp),
                "limit": limit,
            },
            timeout=30.0,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("data", [])


async def _fetch_turvo_shipments(
    settings: Settings,
    since_timestamp: str,
    limit: int,
) -> List[Dict]:
    """Fetch shipment updates from Turvo API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.turvo.com/v1/shipments",
            headers={
                "Authorization": f"Bearer {settings.turvo_api_key}",
                "Accept": "application/json",
            },
            params={
                "updated_since": since_timestamp,
                "limit": limit,
            },
            timeout=30.0,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("shipments", [])


async def _fetch_custom_api(
    settings: Settings,
    since_timestamp: str,
    limit: int,
) -> List[Dict]:
    """Fetch from custom API endpoint."""
    # Placeholder for custom API integration
    # Replace with your specific API logic
    return []


def _iso_to_ms(iso_timestamp: str) -> int:
    """Convert ISO 8601 timestamp to milliseconds since epoch."""
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)
```

**Update __init__.py:**

```python
# In apex-memory-system/src/apex_memory/temporal/activities/__init__.py

from .polling import fetch_new_records_activity

__all__ = [
    # ... existing exports ...
    "fetch_new_records_activity",
]
```

---

### Step 2: Create PollingWorkflow (60 min)

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/polling.py`

**Purpose:** Periodic polling workflow with continue-as-new pattern

```python
"""
Polling Workflow

Periodically polls external APIs for new data and spawns child workflows
for processing. Uses continue-as-new pattern to prevent unbounded history.

Key Features:
- Configurable polling interval (default: 15 minutes)
- Continue-as-new after 100 iterations (24-hour runtime)
- Child workflow spawning for each record
- Statistics tracking

Author: Apex Infrastructure Team
Created: 2025-10-20
"""

import asyncio
from datetime import timedelta
from typing import Optional
from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activities using Temporal's safe import pattern
with workflow.unsafe.imports_passed_through():
    from apex_memory.temporal.activities.polling import fetch_new_records_activity
    from apex_memory.temporal.workflows.ingestion import StructuredDataIngestionWorkflow


@workflow.defn(name="PollingWorkflow")
class PollingWorkflow:
    """Periodic polling workflow with continue-as-new.

    This workflow runs indefinitely, polling external APIs every N minutes
    and spawning child workflows to process new records. After 100 iterations,
    it uses continue-as-new to prevent unbounded workflow history.

    Workflow Lifecycle:
        1. Fetch new records from API
        2. Spawn child workflows for each record
        3. Sleep for polling interval (default: 15 minutes)
        4. Repeat (with continue-as-new after 100 iterations)

    Examples:
        >>> # Start polling workflow
        >>> client = await Client.connect("localhost:7233")
        >>> handle = await client.start_workflow(
        ...     PollingWorkflow.run,
        ...     "samsara",  # source
        ...     15,         # interval_minutes
        ...     id="polling-samsara",
        ...     task_queue="apex-ingestion-queue",
        ... )
    """

    def __init__(self):
        """Initialize workflow instance variables."""
        self.source: Optional[str] = None
        self.interval_minutes: int = 15
        self.iteration_count: int = 0
        self.total_records_processed: int = 0
        self.last_poll_timestamp: Optional[str] = None

    @workflow.run
    async def run(
        self,
        source: str,
        interval_minutes: int = 15,
        iteration_count: int = 0,
        last_poll_timestamp: Optional[str] = None,
    ) -> None:
        """Run the polling workflow.

        Args:
            source: Source system to poll ("samsara", "turvo", "custom").
            interval_minutes: Polling interval in minutes (default: 15).
            iteration_count: Current iteration count (for continue-as-new).
            last_poll_timestamp: Timestamp of last successful poll.

        Note:
            This workflow runs indefinitely. Use continue-as-new after 100
            iterations to prevent unbounded history growth.
        """
        self.source = source
        self.interval_minutes = interval_minutes
        self.iteration_count = iteration_count
        self.last_poll_timestamp = last_poll_timestamp

        workflow.logger.info(
            f"PollingWorkflow started: source={source}, interval={interval_minutes}min"
        )

        # Continue-as-new after 100 iterations (~25 hours for 15-min interval)
        MAX_ITERATIONS = 100

        while self.iteration_count < MAX_ITERATIONS:
            self.iteration_count += 1

            workflow.logger.info(
                f"Polling iteration {self.iteration_count}/{MAX_ITERATIONS}"
            )

            # Step 1: Fetch new records
            try:
                result = await workflow.execute_activity(
                    fetch_new_records_activity,
                    args=[source, self.last_poll_timestamp, 100],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=10),
                        maximum_interval=timedelta(minutes=2),
                        maximum_attempts=3,
                    ),
                )

                records = result["records"]
                self.last_poll_timestamp = result["next_timestamp"]
                count = result["count"]

                workflow.logger.info(
                    f"Fetched {count} records from {source}"
                )

                # Step 2: Spawn child workflows for each record
                if count > 0:
                    await self._process_records(records)

                self.total_records_processed += count

            except Exception as e:
                workflow.logger.error(
                    f"Polling iteration {self.iteration_count} failed: {e}"
                )
                # Continue polling despite errors (resilient)

            # Step 3: Sleep until next poll
            workflow.logger.info(
                f"Sleeping for {self.interval_minutes} minutes..."
            )
            await asyncio.sleep(self.interval_minutes * 60)

        # Continue-as-new to prevent unbounded history
        workflow.logger.info(
            f"Reached {MAX_ITERATIONS} iterations. Using continue-as-new..."
        )

        workflow.continue_as_new(
            args=[source, interval_minutes, 0, self.last_poll_timestamp]
        )

    async def _process_records(self, records: list):
        """Spawn child workflows for each record.

        Args:
            records: List of records to process.
        """
        workflow.logger.info(
            f"Spawning {len(records)} child workflows..."
        )

        # Spawn child workflows in parallel
        child_handles = []

        for record in records:
            # Determine record ID and data
            record_id = record.get("id", workflow.uuid4())

            # Start child workflow (StructuredDataIngestionWorkflow)
            child_handle = await workflow.start_child_workflow(
                StructuredDataIngestionWorkflow.run,
                args=[
                    record_id,
                    self.source,
                    "GENERIC_JSON",  # data_type
                    record,          # raw_json
                ],
                id=f"{workflow.info().workflow_id}-child-{record_id}",
                task_queue="apex-ingestion-queue",
            )

            child_handles.append(child_handle)

        # Wait for all child workflows to start (not complete)
        # We don't wait for completion to avoid blocking polling
        workflow.logger.info(
            f"Started {len(child_handles)} child workflows"
        )

    @workflow.query
    def get_stats(self) -> dict:
        """Query workflow statistics.

        Returns:
            Dictionary containing:
            - iteration_count: Current iteration number
            - total_records_processed: Total records processed
            - last_poll_timestamp: Last successful poll timestamp
        """
        return {
            "source": self.source,
            "iteration_count": self.iteration_count,
            "total_records_processed": self.total_records_processed,
            "last_poll_timestamp": self.last_poll_timestamp,
        }
```

**Update workflows/__init__.py:**

```python
# In apex-memory-system/src/apex_memory/temporal/workflows/__init__.py

from .polling import PollingWorkflow

__all__ = [
    # ... existing exports ...
    "PollingWorkflow",
]
```

---

### Step 3: Update Worker Registration (20 min)

**File:** `apex-memory-system/src/apex_memory/temporal/workers/dev_worker.py`

**Add PollingWorkflow and fetch_new_records_activity:**

```python
# Import polling workflow and activity
from apex_memory.temporal.workflows.polling import PollingWorkflow
from apex_memory.temporal.activities.polling import fetch_new_records_activity

# Register workflows (add to existing list)
worker = Worker(
    client,
    task_queue="apex-ingestion-queue",
    workflows=[
        GreetingWorkflow,
        DocumentIngestionWorkflow,
        StructuredDataIngestionWorkflow,
        PollingWorkflow,  # NEW
    ],
    activities=[
        # ... existing activities ...
        fetch_new_records_activity,  # NEW
    ],
)
```

---

### Step 4: Create Polling Examples (30 min)

**File:** `apex-memory-system/examples/polling/start-polling-workflow.py`

```python
"""
Start Polling Workflow

Demonstrates how to start a polling workflow that runs indefinitely.

Usage:
    python examples/polling/start-polling-workflow.py --source samsara --interval 15
"""

import argparse
import asyncio
from temporalio.client import Client

from apex_memory.temporal.workflows.polling import PollingWorkflow


async def start_polling(source: str, interval_minutes: int):
    """Start a polling workflow.

    Args:
        source: Source system to poll ("samsara", "turvo", "custom").
        interval_minutes: Polling interval in minutes.
    """
    client = await Client.connect("localhost:7233")

    workflow_id = f"polling-{source}"

    print(f"🔄 Starting polling workflow: {workflow_id}")
    print(f"   Source: {source}")
    print(f"   Interval: {interval_minutes} minutes")
    print()

    handle = await client.start_workflow(
        PollingWorkflow.run,
        args=[source, interval_minutes],
        id=workflow_id,
        task_queue="apex-ingestion-queue",
    )

    print(f"✅ Polling workflow started!")
    print(f"   Workflow ID: {handle.id}")
    print(f"   View in Temporal UI: http://localhost:8088/namespaces/default/workflows/{handle.id}")
    print()
    print("💡 Query stats:")
    print(f"   temporal workflow query --workflow-id {handle.id} --query-type get_stats")


async def query_stats(workflow_id: str):
    """Query polling workflow statistics."""
    client = await Client.connect("localhost:7233")

    handle = client.get_workflow_handle(workflow_id)
    stats = await handle.query(PollingWorkflow.get_stats)

    print(f"📊 Polling Statistics for {workflow_id}:")
    print(f"   Source: {stats['source']}")
    print(f"   Iteration: {stats['iteration_count']}")
    print(f"   Total Records: {stats['total_records_processed']}")
    print(f"   Last Poll: {stats['last_poll_timestamp']}")


async def main():
    parser = argparse.ArgumentParser(description="Start polling workflow")
    parser.add_argument("--source", required=True, choices=["samsara", "turvo", "custom"])
    parser.add_argument("--interval", type=int, default=15, help="Polling interval in minutes")
    parser.add_argument("--query", action="store_true", help="Query existing workflow stats")

    args = parser.parse_args()

    if args.query:
        workflow_id = f"polling-{args.source}"
        await query_stats(workflow_id)
    else:
        await start_polling(args.source, args.interval)


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Step 5: Testing (45 min)

**File:** `apex-memory-system/tests/integration/test_polling_workflow.py`

**Tests to Create (15 tests):**

```python
"""
Test Suite: Polling Workflows

Validates periodic polling with continue-as-new pattern.
"""

import pytest
import asyncio
from datetime import datetime
from temporalio.client import Client
from temporalio.worker import Worker

from apex_memory.temporal.workflows.polling import PollingWorkflow
from apex_memory.temporal.activities.polling import fetch_new_records_activity


@pytest.mark.asyncio
@pytest.mark.integration
async def test_polling_workflow_executes():
    """TEST 1: Polling workflow runs successfully."""
    client = await Client.connect("localhost:7233")

    # Start polling workflow
    handle = await client.start_workflow(
        PollingWorkflow.run,
        args=["custom", 1],  # 1-minute interval for testing
        id=f"test-polling-{datetime.utcnow().timestamp()}",
        task_queue="apex-ingestion-queue",
    )

    # Wait for first iteration
    await asyncio.sleep(70)  # 1 min + buffer

    # Query stats
    stats = await handle.query(PollingWorkflow.get_stats)
    assert stats["iteration_count"] >= 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_polling_workflow_spawns_child_workflows():
    """TEST 2: Child workflows spawned for fetched records."""
    # Mock fetch_new_records_activity to return test data
    # Start polling workflow
    # Verify child workflows created
    pass  # Implementation similar to TEST 1


# TEST 3-15: Continue patterns, error handling, etc.
# (Similar structure)
```

---

### Success Criteria (Section 12)

✅ PollingWorkflow runs indefinitely
✅ Continue-as-new after 100 iterations
✅ Child workflows spawned for each record
✅ fetch_new_records_activity supports Samsara, Turvo, custom APIs
✅ Polling interval configurable
✅ Stats query returns accurate data
✅ All 15 tests passing

---

## SECTION 16: OpenTelemetry Integration (3 hours)

### Overview

OpenTelemetry adds distributed tracing to complement existing metrics and logs, providing complete observability.

**What You'll Build:**
- OTLP exporter configuration
- Trace instrumentation for all workflows and activities
- Jaeger integration for trace visualization
- Correlation between traces, metrics, and logs

**Research Foundation:**
- **OpenTelemetry:** https://opentelemetry.io/docs/
- **Temporal + OTel:** https://docs.temporal.io/cloud/metrics/general-setup#opentelemetry
- **OTLP Exporter:** https://opentelemetry-python.readthedocs.io/

---

### Step 1: Install OpenTelemetry Dependencies (10 min)

**File:** `apex-memory-system/requirements.txt`

**Add dependencies:**

```txt
# OpenTelemetry
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation==0.42b0
opentelemetry-instrumentation-httpx==0.42b0
opentelemetry-instrumentation-asyncpg==0.42b0
opentelemetry-exporter-otlp==1.21.0
```

**Install:**

```bash
cd apex-memory-system
pip install -r requirements.txt
```

---

### Step 2: Create Telemetry Configuration (45 min)

**File:** `apex-memory-system/src/apex_memory/config/telemetry.py`

**Purpose:** Configure OpenTelemetry with OTLP exporter

```python
"""
OpenTelemetry Configuration

Configures distributed tracing for Apex Memory System using OpenTelemetry.

Exports traces to Jaeger via OTLP protocol for visualization and analysis.

Author: Apex Infrastructure Team
Created: 2025-10-20
"""

import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor

from apex_memory.config.settings import Settings

logger = logging.getLogger(__name__)


class TelemetryConfig:
    """OpenTelemetry configuration for Apex Memory System.

    Configures tracing with OTLP export to Jaeger for distributed tracing
    visualization across workflows, activities, and database operations.

    Usage:
        >>> telemetry = TelemetryConfig()
        >>> if telemetry.is_enabled():
        ...     telemetry.configure()
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize telemetry configuration.

        Args:
            settings: Application settings (or load from environment).
        """
        self.settings = settings or Settings()
        self._configured = False

    def is_enabled(self) -> bool:
        """Check if OpenTelemetry is enabled.

        Returns:
            True if ENABLE_OPENTELEMETRY=true in settings.
        """
        return getattr(self.settings, "enable_opentelemetry", False)

    def configure(self) -> None:
        """Configure OpenTelemetry tracing.

        Sets up:
        - TracerProvider with service name
        - OTLP exporter to Jaeger
        - Automatic instrumentation for httpx and asyncpg

        Raises:
            RuntimeError: If configuration fails.
        """
        if self._configured:
            logger.warning("OpenTelemetry already configured")
            return

        if not self.is_enabled():
            logger.info("OpenTelemetry disabled (ENABLE_OPENTELEMETRY=false)")
            return

        try:
            logger.info("Configuring OpenTelemetry...")

            # Step 1: Create resource with service name
            resource = Resource(attributes={
                SERVICE_NAME: "apex-memory-system",
            })

            # Step 2: Create tracer provider
            tracer_provider = TracerProvider(resource=resource)

            # Step 3: Configure OTLP exporter
            otlp_endpoint = getattr(
                self.settings,
                "otlp_endpoint",
                "http://localhost:4317",  # Jaeger OTLP endpoint
            )

            otlp_exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint,
                insecure=True,  # Use insecure for local development
            )

            # Step 4: Add batch span processor
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)

            # Step 5: Set global tracer provider
            trace.set_tracer_provider(tracer_provider)

            # Step 6: Enable automatic instrumentation
            HTTPXClientInstrumentor().instrument()  # HTTP clients
            AsyncPGInstrumentor().instrument()      # PostgreSQL

            self._configured = True

            logger.info(
                f"✅ OpenTelemetry configured (endpoint: {otlp_endpoint})"
            )

        except Exception as e:
            logger.error(
                f"Failed to configure OpenTelemetry: {e}",
                exc_info=True,
            )
            raise RuntimeError(f"OpenTelemetry configuration failed: {e}")

    def get_tracer(self, name: str) -> trace.Tracer:
        """Get a tracer for manual instrumentation.

        Args:
            name: Tracer name (usually module name).

        Returns:
            OpenTelemetry tracer instance.

        Example:
            >>> tracer = telemetry.get_tracer(__name__)
            >>> with tracer.start_as_current_span("my_operation"):
            ...     # Operation code
        """
        return trace.get_tracer(name)


# Global telemetry instance
_telemetry: Optional[TelemetryConfig] = None


def setup_telemetry(settings: Optional[Settings] = None) -> TelemetryConfig:
    """Setup global telemetry configuration.

    Args:
        settings: Application settings.

    Returns:
        Configured TelemetryConfig instance.

    Example:
        >>> # In main.py or worker initialization
        >>> telemetry = setup_telemetry()
        >>> if telemetry.is_enabled():
        ...     telemetry.configure()
    """
    global _telemetry

    if _telemetry is None:
        _telemetry = TelemetryConfig(settings)

    return _telemetry


def get_telemetry() -> TelemetryConfig:
    """Get global telemetry instance.

    Returns:
        TelemetryConfig instance (must call setup_telemetry() first).

    Raises:
        RuntimeError: If telemetry not initialized.
    """
    if _telemetry is None:
        raise RuntimeError("Telemetry not initialized. Call setup_telemetry() first.")

    return _telemetry
```

---

### Step 3: Update Settings (15 min)

**File:** `apex-memory-system/src/apex_memory/config/settings.py`

**Add OpenTelemetry settings:**

```python
# In Settings class

# OpenTelemetry Configuration
enable_opentelemetry: bool = Field(
    default=False,
    description="Enable OpenTelemetry distributed tracing",
)

otlp_endpoint: str = Field(
    default="http://localhost:4317",
    description="OTLP exporter endpoint (Jaeger)",
)
```

**Add to .env:**

```bash
# OpenTelemetry
ENABLE_OPENTELEMETRY=true
OTLP_ENDPOINT=http://localhost:4317
```

---

### Step 4: Add Jaeger to Docker Compose (20 min)

**File:** `apex-memory-system/docker/docker-compose.yml`

**Add Jaeger service:**

```yaml
services:
  # ... existing services ...

  jaeger:
    image: jaegertracing/all-in-one:1.51
    container_name: apex-jaeger
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "16686:16686" # Jaeger UI
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - apex-network
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:14269"]
      interval: 10s
      timeout: 5s
      retries: 5
```

**Start Jaeger:**

```bash
cd apex-memory-system/docker
docker-compose up -d jaeger

# Verify Jaeger UI
open http://localhost:16686
```

---

### Step 5: Instrument Workflows and Activities (60 min)

**Manual instrumentation for custom spans**

**Example: Instrument DocumentIngestionWorkflow**

```python
# In apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py

from apex_memory.config.telemetry import get_telemetry

tracer = get_telemetry().get_tracer(__name__)

@workflow.run
async def run(...):
    # Create span for entire workflow
    with tracer.start_as_current_span(
        "document_ingestion_workflow",
        attributes={
            "document_id": document_id,
            "source": source,
        },
    ):
        # Workflow logic...

        # Nested span for parse step
        with tracer.start_as_current_span("parse_document"):
            result = await workflow.execute_activity(
                parse_document_activity, ...
            )
```

**Example: Instrument Activities**

```python
# In apex-memory-system/src/apex_memory/temporal/activities/ingestion.py

from apex_memory.config.telemetry import get_telemetry

tracer = get_telemetry().get_tracer(__name__)

@activity.defn
async def parse_document_activity(...):
    with tracer.start_as_current_span(
        "parse_document_activity",
        attributes={
            "document_id": document_id,
            "file_path": file_path,
        },
    ):
        # Activity logic...
```

---

### Step 6: Initialize Telemetry in Worker (15 min)

**File:** `apex-memory-system/src/apex_memory/temporal/workers/dev_worker.py`

**Add telemetry setup:**

```python
from apex_memory.config.telemetry import setup_telemetry

async def main():
    # Setup telemetry
    telemetry = setup_telemetry()
    if telemetry.is_enabled():
        telemetry.configure()
        logger.info("OpenTelemetry enabled - traces will be exported to Jaeger")
    else:
        logger.info("OpenTelemetry disabled")

    # ... rest of worker setup ...
```

---

### Step 7: Testing (45 min)

**File:** `apex-memory-system/tests/integration/test_opentelemetry.py`

**Tests to Create (10 tests):**

```python
"""
Test Suite: OpenTelemetry Integration

Validates distributed tracing configuration and trace export.
"""

import pytest
from apex_memory.config.telemetry import TelemetryConfig, setup_telemetry
from apex_memory.config.settings import Settings


def test_telemetry_setup():
    """TEST 1: Telemetry configures when enabled."""
    settings = Settings(enable_opentelemetry=True)
    telemetry = TelemetryConfig(settings)

    assert telemetry.is_enabled() is True

    telemetry.configure()

    # Should not raise error
    tracer = telemetry.get_tracer("test")
    assert tracer is not None


def test_telemetry_disabled():
    """TEST 2: Telemetry skipped when disabled."""
    settings = Settings(enable_opentelemetry=False)
    telemetry = TelemetryConfig(settings)

    assert telemetry.is_enabled() is False

    # configure() should be no-op
    telemetry.configure()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_workflow_traces_exported():
    """TEST 3: Workflow execution creates traces."""
    # Start workflow
    # Query Jaeger API for traces
    # Verify trace exists with correct attributes
    pass


# TEST 4-10: Additional trace validation
```

---

### Success Criteria (Section 16)

✅ OpenTelemetry dependencies installed
✅ OTLP exporter configured
✅ Jaeger running and accessible (http://localhost:16686)
✅ Workflows instrumented with spans
✅ Activities instrumented with spans
✅ Traces visible in Jaeger UI
✅ Trace correlation with workflow IDs
✅ HTTP and database operations auto-instrumented
✅ All 10 tests passing

---

## TESTING STRATEGY

### Test Categories

**1. Search Attributes (10 tests)**
- Configuration validation
- Workflow tagging
- Search queries
- Status updates

**2. Polling Workflows (15 tests)**
- Workflow execution
- Continue-as-new
- Child workflow spawning
- API polling

**3. OpenTelemetry (10 tests)**
- Configuration
- Trace export
- Span attributes
- Jaeger integration

**Total Tests:** 35 new tests

---

## SUCCESS CRITERIA

### Overall Success Metrics

✅ **Section 14:** All 4 search attributes working, 10 tests passing
✅ **Section 12:** Polling workflow operational, 15 tests passing
✅ **Section 16:** OpenTelemetry configured, 10 tests passing

✅ **Total:** 35 tests passing
✅ **Integration:** All features work together
✅ **Documentation:** Complete implementation guides
✅ **Zero breaking changes** to existing workflows

---

## REFERENCES

### Official Documentation

**Temporal:**
- Search Attributes: https://docs.temporal.io/visibility#search-attribute
- Continue-As-New: https://docs.temporal.io/workflows#continue-as-new
- Child Workflows: https://docs.temporal.io/workflows#child-workflows

**OpenTelemetry:**
- Python SDK: https://opentelemetry-python.readthedocs.io/
- OTLP Exporter: https://opentelemetry.io/docs/specs/otlp/
- Jaeger: https://www.jaegertracing.io/docs/

**Internal:**
- EXECUTION-ROADMAP.md - Original section plans
- PROJECT-STATUS-SNAPSHOT.md - Current project state
- graphiti-json-integration/ - Completed workflow patterns

---

**Implementation Plan Version:** 1.0
**Created:** 2025-10-20
**Status:** Ready for Implementation

**Next Step:** Begin Section 14 (Search Attributes - 2 hours)
