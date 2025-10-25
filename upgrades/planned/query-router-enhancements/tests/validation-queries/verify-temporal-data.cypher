// Validation Query: Verify Temporal Data Exists
// Purpose: Check that temporal edges and entity states exist for analytics
// Expected: Multiple entities with temporal state history

// Query 1: Count entities with temporal states
MATCH (e:Entity)-[:TEMPORAL_EDGE]->(state:EntityState)
WITH e, count(state) as state_count
RETURN count(e) as entities_with_states, avg(state_count) as avg_states_per_entity
// Expected: entities_with_states > 0, avg_states_per_entity >= 2

// Query 2: Check temporal data recency
MATCH (e:Entity)-[:TEMPORAL_EDGE]->(state:EntityState)
WITH state.valid_from as valid_from
ORDER BY valid_from DESC
LIMIT 10
RETURN valid_from
// Expected: Recent dates (within last 90 days)

// Query 3: Verify property tracking over time
MATCH (e:Entity {entity_type: "Equipment"})-[:TEMPORAL_EDGE]->(state:EntityState)
WHERE state.properties.maintenance_cost IS NOT NULL
WITH e, count(state) as state_count
RETURN count(e) as equipment_with_maintenance_history, avg(state_count) as avg_history_length
// Expected: equipment_with_maintenance_history > 0, avg_history_length >= 3

// Query 4: Check time range coverage
MATCH (e:Entity)-[:TEMPORAL_EDGE]->(state:EntityState)
WITH min(state.valid_from) as earliest, max(state.valid_from) as latest
RETURN earliest, latest, duration.between(earliest, latest).days as time_span_days
// Expected: time_span_days >= 30 (at least 1 month of data)
