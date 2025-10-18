# Section 5 Examples: Hello World Validation

This directory contains 3 executable examples demonstrating Hello World workflow.

## Prerequisites

1. **Temporal Server running:**
   ```bash
   cd /Users/richardglaubitz/Projects/apex-memory-system/docker
   docker-compose -f temporal-compose.yml up -d
   ```

2. **Worker running:**
   ```bash
   cd /Users/richardglaubitz/Projects/apex-memory-system
   python -m apex_memory.temporal.workers.dev_worker
   ```

## Examples

### 1. Basic Workflow Execution

**File:** `hello-world-basic.py`

**Purpose:** Minimal workflow execution demonstrating simplest possible Temporal workflow.

**Usage:**
```bash
python examples/section-5/hello-world-basic.py
```

**Expected Output:**
```
Connecting to Temporal Server at localhost:7233...
Executing GreetingWorkflow...

Result: Hello, World! Welcome to Apex Memory System with Temporal.io!

✅ Success! Basic workflow execution complete.
```

---

### 2. Retry Policy Demonstration

**File:** `hello-world-with-retry.py`

**Purpose:** Demonstrates retry policy configuration and how to test retries.

**Usage:**
```bash
python examples/section-5/hello-world-with-retry.py
```

**Features:**
- Shows retry policy parameters (initial_interval=1s, max_attempts=3)
- Explains how to view retries in Temporal UI
- Provides guidance on testing retry behavior

**Expected Output:**
```
Connecting to Temporal Server at localhost:7233...
Executing GreetingWorkflow (with retry policy)...

Retry Policy Configuration:
  - Initial interval: 1 second
  - Maximum interval: 10 seconds
  - Maximum attempts: 3

Note: If activity fails, it will retry automatically.

Result: Hello, Retry Demo! Welcome to Apex Memory System with Temporal.io!

✅ Success! Workflow completed (with retry policy active).
```

---

### 3. Query Workflow Status

**File:** `hello-world-query-status.py`

**Purpose:** Query workflow status, fetch history, and display workflow details.

**Usage:**
```bash
python examples/section-5/hello-world-query-status.py
```

**Features:**
- Non-blocking workflow start
- Workflow status querying
- Event history retrieval
- Execution time calculation
- Temporal UI link generation

**Expected Output:**
```
Connecting to Temporal Server at localhost:7233...
Executing GreetingWorkflow (ID: hello-world-query-status-example)...

✅ Workflow started!
   Workflow ID: hello-world-query-status-example
   Run ID: <run-id>

📊 Querying workflow status...

✅ Workflow completed!
   Status: Completed
   Result: Hello, Status Query Demo! Welcome to Apex Memory System with Temporal.io!

📋 Workflow Details:
   Status: COMPLETED
   Start Time: 2025-10-18 14:30:00
   Close Time: 2025-10-18 14:30:01
   Execution Time: 0:00:01

📜 Fetching workflow history...
   Total events: 8
   Event types:
      1. EVENT_TYPE_WORKFLOW_EXECUTION_STARTED
      2. EVENT_TYPE_WORKFLOW_TASK_SCHEDULED
      3. EVENT_TYPE_WORKFLOW_TASK_STARTED
      4. EVENT_TYPE_WORKFLOW_TASK_COMPLETED
      5. EVENT_TYPE_ACTIVITY_TASK_SCHEDULED
      ... and 3 more events

🔗 View full details in Temporal UI:
   http://localhost:8088/namespaces/default/workflows/hello-world-query-status-example
```

---

## Troubleshooting

### Error: Connection refused

**Problem:** Temporal Server not running.

**Solution:**
```bash
cd docker
docker-compose -f temporal-compose.yml up -d
```

### Error: No workers available

**Problem:** Worker not running.

**Solution:**
```bash
python -m apex_memory.temporal.workers.dev_worker
```

### Error: Workflow timeout

**Problem:** Activity took longer than 10 seconds.

**Solution:** Check worker logs for errors. Activity should complete quickly.

---

## Temporal UI

**Access:** http://localhost:8088

**View:**
- All executed workflows
- Workflow event history
- Activity execution timeline
- Input/output values
- Error messages (if any)

---

## Next Steps

After running these examples:

1. ✅ View workflows in Temporal UI
2. ✅ Check event history for each workflow
3. ✅ Verify activity execution logs
4. ✅ Proceed to Section 6 (Monitoring & Testing)

---

**For complete documentation, see:**
`tests/section-5-hello-world/SECTION-5-SUMMARY.md`
