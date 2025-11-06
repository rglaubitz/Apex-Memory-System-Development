# Technical Debt - Temporal Implementation

**Last Updated:** 2025-10-18
**Status:** Tracking

---

## TD-001: Temporal Activities I/O Pattern Refactor

**Priority:** Medium
**Effort:** 2-3 hours
**Target Phase:** Section 9 or 10

### Issue

Section 7 activities use `file_path` parameter instead of `document_id` + S3 download, violating Temporal best practices.

### Current State (Section 7)

```python
@activity.defn
async def parse_document_activity(file_path: str) -> dict:
    """Expects local file path - not following best practice."""
    parser = DocumentParser()
    parsed = await asyncio.to_thread(parser.parse_document, Path(file_path))
    return {...}
```

**Problem:**
- Workflow must provide local file path
- Activity doesn't handle its own I/O
- Violates Temporal principle: "Activities handle their own I/O"

### Desired State (Future Refactor)

```python
@activity.defn
async def parse_document_activity(
    document_id: str,
    storage_config: dict
) -> dict:
    """Downloads from S3 internally - follows best practice."""
    # 1. Download from S3
    s3_client = await get_s3_client(storage_config)
    temp_file = await s3_client.download(document_id)

    # 2. Parse
    parser = DocumentParser()
    parsed = await asyncio.to_thread(parser.parse_document, Path(temp_file))

    # 3. Cleanup
    os.remove(temp_file)

    return {...}
```

**Benefits:**
- ✅ Proper separation: Workflows = "what", Activities = "how"
- ✅ Better testability: Mock S3 in activity tests
- ✅ Easier retries: Activity retries include download
- ✅ Industry standard: Large data passed by reference

### Interim Solution (Section 8)

Added `download_from_s3_activity` to bridge gap:

```python
@workflow.defn
class DocumentIngestionWorkflow:
    async def run(self, document_id: str, source: str):
        # NEW: Download from S3 first
        file_path = await workflow.execute_activity(
            download_from_s3_activity,
            document_id,
            source,
            ...
        )

        # EXISTING: Parse from file path (Section 7)
        parsed = await workflow.execute_activity(
            parse_document_activity,
            file_path,  # ← Still uses file_path for now
            ...
        )
```

**Why Interim Solution:**
- Keeps Section 7's 19 passing tests unchanged
- Section 8 focused on workflow orchestration
- Proper refactor planned for later phase

### Refactor Checklist

- [ ] Modify `parse_document_activity` signature
- [ ] Add S3 download logic inside activity
- [ ] Add S3 client configuration
- [ ] Update activity tests to mock S3 client
- [ ] Update Section 8 workflow to remove `download_from_s3_activity`
- [ ] Update all 19 Section 7 tests
- [ ] Update documentation
- [ ] Verify all 65 Enhanced Saga tests still passing

### References

**Research:**
- Temporal best practices: https://docs.temporal.io/workflows
- Integration patterns: `research/documentation/temporal/integration-patterns.md` lines 156-168
- Section 7 handoff: `HANDOFF-SECTION-8.md`

**Why This Matters (from Temporal docs):**
- "For large data (>1-2MB), pass references (URLs, IDs), not data"
- "Activities should handle their own I/O operations"
- "Workflows orchestrate, activities execute"

---

## Future Technical Debt Items

_Add new items as they're identified during implementation._
