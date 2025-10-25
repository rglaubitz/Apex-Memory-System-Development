# Task 4.2: Add Entity Type Detection

**Phase:** 4 - Metadata Bias Fix
**Time:** 1 hour
**Dependencies:** Task 4.1
**Status:** 📝 Planned

---

## Objective

Extract entity types from queries to improve routing precision.

---

## Implementation

```python
def extract_entity_types(query: str) -> List[str]:
    """Extract entity types mentioned in query."""
    entity_map = {
        "driver": ["driver", "drivers"],
        "customer": ["customer", "customers", "clients"],
        "equipment": ["equipment", "machinery", "vehicles"],
        "invoice": ["invoice", "invoices", "bills"],
    }

    found_types = []
    query_lower = query.lower()

    for entity_type, keywords in entity_map.items():
        if any(kw in query_lower for kw in keywords):
            found_types.append(entity_type)

    return found_types
```

---

## Success Criteria

✅ Entity types extracted
✅ Used in routing decisions

---

**Created:** 2025-10-25
