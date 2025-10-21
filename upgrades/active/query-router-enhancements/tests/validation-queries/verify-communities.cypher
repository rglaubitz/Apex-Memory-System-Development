// Validation Query: Verify Communities Exist
// Purpose: Check that communities were created and have members
// Expected: At least 3 communities with 5+ members each

// Query 1: Count total communities
MATCH (c:Community {group_id: "default"})
RETURN count(c) as community_count
// Expected: community_count >= 3

// Query 2: List communities with member counts
MATCH (c:Community {group_id: "default"})
WITH c, size((c)-[:HAS_MEMBER]->()) as member_count
WHERE member_count >= 5
RETURN c.uuid as community_id, c.name as name, c.summary as summary, member_count
ORDER BY member_count DESC;
// Expected: Multiple communities with summaries

// Query 3: Verify community summaries exist
MATCH (c:Community {group_id: "default"})
WHERE c.summary IS NOT NULL AND c.summary <> ""
RETURN count(c) as communities_with_summaries
// Expected: communities_with_summaries == community_count (all have summaries)

// Query 4: Check community member distribution by entity type
MATCH (c:Community {group_id: "default"})-[:HAS_MEMBER]->(e:Entity)
WITH c, e.entity_type as entity_type, count(e) as type_count
RETURN c.name as community, entity_type, type_count
ORDER BY c.name, type_count DESC;
// Expected: Diverse entity types within communities
