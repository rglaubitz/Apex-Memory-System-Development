// Validation Query: Verify Graph Connectivity
// Purpose: Check that graph has sufficient connectivity for analytics
// Expected: Well-connected graph with paths between entities

// Query 1: Calculate graph density
MATCH (e:Entity)
WITH count(e) as node_count
MATCH ()-[r]->()
WITH node_count, count(r) as edge_count
RETURN
  node_count,
  edge_count,
  (2.0 * edge_count) / (node_count * (node_count - 1)) as density
// Expected: density > 0.01 (at least 1% connected)

// Query 2: Find connected components
MATCH (e:Entity)
WHERE NOT (e)-[]-()
RETURN count(e) as isolated_nodes
// Expected: isolated_nodes < (total_nodes * 0.05) - less than 5% isolated

// Query 3: Verify shortest paths exist
MATCH (e1:Entity {entity_type: "Equipment"}), (e2:Entity {entity_type: "Maintenance"})
MATCH path = shortestPath((e1)-[*1..5]-(e2))
RETURN count(path) as paths_found
LIMIT 100
// Expected: paths_found > 10 (multiple connections between equipment and maintenance)

// Query 4: Check relationship type diversity
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
// Expected: Multiple relationship types (not just one type dominating)
