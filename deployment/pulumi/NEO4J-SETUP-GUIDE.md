# Neo4j Setup Guide

**Date:** 2025-11-16
**Status:** ✅ Complete
**Instance:** apex-neo4j-dev

---

## 📋 Overview

This guide covers how to access, manage, and use the Neo4j graph database deployed in Week 2.

**Instance Details:**
- Name: `apex-neo4j-dev`
- Private IP: `10.0.0.2`
- Machine: e2-small (2 vCPU, 2GB RAM)
- Zone: us-central1-a
- Version: Neo4j 5.15 Community Edition
- Data Storage: 50GB SSD at `/mnt/neo4j`

---

## 🌐 Accessing Neo4j Browser

Neo4j Browser provides a visual interface for running Cypher queries and exploring graph data.

### From Cloud Shell (Recommended)

**Step 1: Open Cloud Shell**
```bash
# Navigate to: https://shell.cloud.google.com
```

**Step 2: Create SSH Tunnel**
```bash
# Forward Neo4j browser port (7474) and Bolt port (7687)
gcloud compute ssh apex-neo4j-dev \
  --zone=us-central1-a \
  --project=apex-memory-dev \
  --ssh-flag="-L 7474:localhost:7474" \
  --ssh-flag="-L 7687:localhost:7687"
```

**Step 3: Access Browser**
```
# In Cloud Shell, click "Web Preview" → "Preview on port 7474"
# Or open: https://ssh.cloud.google.com/devshell/proxy?port=7474
```

**Step 4: Login**
```
Connect URL: bolt://localhost:7687
Username: neo4j
Password: {*i-ouY!AZEp1Gf+h0u[A6)R]utvhb#0
```

---

### From Compute Engine VM (Alternative)

If you have a VM in the same VPC:

```bash
# Install Neo4j Python driver (for CLI queries)
pip3 install neo4j

# Or use cypher-shell (requires Java)
# Access directly via: http://10.0.0.2:7474
```

---

## 📊 Cypher Query Examples

### Basic Node Operations

**Create a Node:**
```cypher
// Create a person node
CREATE (p:Person {
  name: "Alice",
  age: 30,
  email: "alice@example.com"
})
RETURN p
```

**Find Nodes:**
```cypher
// Find all Person nodes
MATCH (p:Person)
RETURN p

// Find specific person
MATCH (p:Person {name: "Alice"})
RETURN p

// Find people over 25
MATCH (p:Person)
WHERE p.age > 25
RETURN p.name, p.age
ORDER BY p.age DESC
```

**Update Nodes:**
```cypher
// Update a person's age
MATCH (p:Person {name: "Alice"})
SET p.age = 31
RETURN p

// Add a property
MATCH (p:Person {name: "Alice"})
SET p.city = "San Francisco"
RETURN p
```

**Delete Nodes:**
```cypher
// Delete a specific node
MATCH (p:Person {name: "Alice"})
DELETE p

// Delete all Person nodes (careful!)
MATCH (p:Person)
DELETE p
```

---

### Relationship Operations

**Create Relationships:**
```cypher
// Create two people with a KNOWS relationship
CREATE (a:Person {name: "Alice", age: 30})
CREATE (b:Person {name: "Bob", age: 25})
CREATE (a)-[:KNOWS {since: 2020}]->(b)
RETURN a, b
```

**Query Relationships:**
```cypher
// Find who Alice knows
MATCH (a:Person {name: "Alice"})-[:KNOWS]->(friend)
RETURN friend.name

// Find mutual friends
MATCH (a:Person {name: "Alice"})-[:KNOWS]->(mutual)<-[:KNOWS]-(b:Person {name: "Charlie"})
RETURN mutual.name

// Find friends of friends
MATCH (a:Person {name: "Alice"})-[:KNOWS*2]->(foaf)
RETURN DISTINCT foaf.name
```

**Complex Patterns:**
```cypher
// Find shortest path between two people
MATCH path = shortestPath(
  (a:Person {name: "Alice"})-[:KNOWS*]-(b:Person {name: "Charlie"})
)
RETURN path

// Find triangles (3-person networks)
MATCH (a:Person)-[:KNOWS]->(b:Person)-[:KNOWS]->(c:Person)-[:KNOWS]->(a)
RETURN a.name, b.name, c.name
```

---

### Aggregations and Analytics

**Count Nodes:**
```cypher
// Count all Person nodes
MATCH (p:Person)
RETURN count(p)

// Count by property
MATCH (p:Person)
RETURN p.city, count(p) AS population
ORDER BY population DESC
```

**Calculate Metrics:**
```cypher
// Average age
MATCH (p:Person)
RETURN avg(p.age) AS average_age

// Degree centrality (number of connections)
MATCH (p:Person)
OPTIONAL MATCH (p)-[:KNOWS]-(friend)
RETURN p.name, count(friend) AS num_connections
ORDER BY num_connections DESC
```

**Find Communities:**
```cypher
// Find people with most connections
MATCH (p:Person)-[:KNOWS]-(friend)
WITH p, count(friend) AS connections
WHERE connections > 5
RETURN p.name, connections
ORDER BY connections DESC
```

---

## 📥 Data Import Procedures

### Import CSV Data

**Step 1: Prepare CSV File**
```csv
# people.csv
name,age,email
Alice,30,alice@example.com
Bob,25,bob@example.com
Charlie,35,charlie@example.com
```

**Step 2: Upload to Neo4j VM**
```bash
# From Cloud Shell
gcloud compute scp people.csv apex-neo4j-dev:/tmp/people.csv \
  --zone=us-central1-a \
  --project=apex-memory-dev

# SSH into Neo4j VM
gcloud compute ssh apex-neo4j-dev \
  --zone=us-central1-a \
  --project=apex-memory-dev

# Copy into Neo4j container
sudo docker cp /tmp/people.csv neo4j:/var/lib/neo4j/import/people.csv
```

**Step 3: Import Using Cypher**
```cypher
// Load CSV and create nodes
LOAD CSV WITH HEADERS FROM 'file:///people.csv' AS row
CREATE (p:Person {
  name: row.name,
  age: toInteger(row.age),
  email: row.email
})
RETURN count(p)
```

---

### Import Relationships from CSV

**Prepare Relationships CSV:**
```csv
# relationships.csv
from,to,since
Alice,Bob,2020
Bob,Charlie,2019
Charlie,Alice,2021
```

**Import Cypher:**
```cypher
// Load relationships
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
MATCH (a:Person {name: row.from})
MATCH (b:Person {name: row.to})
CREATE (a)-[:KNOWS {since: toInteger(row.since)}]->(b)
RETURN count(*)
```

---

### Bulk Import with neo4j-admin

For large datasets (millions of nodes), use `neo4j-admin import`:

```bash
# SSH into Neo4j VM
gcloud compute ssh apex-neo4j-dev \
  --zone=us-central1-a \
  --project=apex-memory-dev

# Stop Neo4j
sudo docker stop neo4j

# Run import (example)
sudo docker run --rm \
  -v /mnt/neo4j:/data \
  -v /tmp:/import \
  neo4j:5.15-community \
  neo4j-admin database import full \
  --nodes=/import/nodes.csv \
  --relationships=/import/relationships.csv \
  neo4j

# Restart Neo4j
sudo docker start neo4j
```

---

## 💾 Backup and Restore

### Manual Backup

**Create Backup:**
```bash
# SSH into Neo4j VM
gcloud compute ssh apex-neo4j-dev \
  --zone=us-central1-a \
  --project=apex-memory-dev

# Create backup using neo4j-admin
sudo docker exec neo4j neo4j-admin database dump \
  --to-path=/data/backups \
  --database=neo4j

# Copy backup to local machine (from Cloud Shell)
gcloud compute scp apex-neo4j-dev:/mnt/neo4j/backups/neo4j.dump \
  ./neo4j-backup-$(date +%Y%m%d).dump \
  --zone=us-central1-a \
  --project=apex-memory-dev
```

---

### Restore from Backup

**Restore Backup:**
```bash
# Upload backup to Neo4j VM
gcloud compute scp ./neo4j-backup-20251116.dump \
  apex-neo4j-dev:/tmp/neo4j.dump \
  --zone=us-central1-a \
  --project=apex-memory-dev

# SSH into VM
gcloud compute ssh apex-neo4j-dev \
  --zone=us-central1-a \
  --project=apex-memory-dev

# Stop Neo4j
sudo docker stop neo4j

# Restore database
sudo docker run --rm \
  -v /mnt/neo4j:/data \
  -v /tmp:/backups \
  neo4j:5.15-community \
  neo4j-admin database load \
  --from-path=/backups \
  --database=neo4j

# Restart Neo4j
sudo docker start neo4j
```

---

### Automated Backups (Scheduled)

**Create Backup Script:**
```bash
# On Neo4j VM: /usr/local/bin/backup-neo4j.sh
#!/bin/bash

BACKUP_DIR="/mnt/neo4j/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="neo4j-backup-${TIMESTAMP}.dump"

# Create backup
docker exec neo4j neo4j-admin database dump \
  --to-path=/data/backups \
  --database=neo4j

# Rename with timestamp
mv ${BACKUP_DIR}/neo4j.dump ${BACKUP_DIR}/${BACKUP_FILE}

# Keep only last 7 days of backups
find ${BACKUP_DIR} -name "neo4j-backup-*.dump" -mtime +7 -delete

echo "Backup complete: ${BACKUP_FILE}"
```

**Schedule with Cron:**
```bash
# Add to crontab (daily at 2 AM)
0 2 * * * /usr/local/bin/backup-neo4j.sh >> /var/log/neo4j-backup.log 2>&1
```

---

## 🔧 Database Management

### Check Database Status

```bash
# SSH into Neo4j VM
gcloud compute ssh apex-neo4j-dev \
  --zone=us-central1-a \
  --project=apex-memory-dev

# Check Docker container status
sudo docker ps | grep neo4j

# Check logs
sudo docker logs neo4j --tail 100

# Check resource usage
sudo docker stats neo4j --no-stream
```

---

### Restart Neo4j

```bash
# Restart container
sudo docker restart neo4j

# Check if running
sudo docker ps | grep neo4j
```

---

### View Configuration

```bash
# View Neo4j configuration
sudo docker exec neo4j cat /var/lib/neo4j/conf/neo4j.conf
```

---

### Performance Tuning

**Check Memory Settings:**
```cypher
// In Neo4j Browser
CALL dbms.listConfig()
YIELD name, value
WHERE name STARTS WITH 'dbms.memory'
RETURN name, value
```

**Modify Memory (requires container restart):**
```bash
# Stop Neo4j
sudo docker stop neo4j

# Run with new memory settings
sudo docker run -d \
  --name neo4j \
  --restart always \
  -p 7474:7474 -p 7687:7687 \
  -v /mnt/neo4j:/data \
  -e NEO4J_AUTH=neo4j/{password} \
  -e NEO4J_dbms_memory_heap_initial__size=1G \
  -e NEO4J_dbms_memory_heap_max__size=2G \
  neo4j:5.15-community
```

---

## 🔍 Monitoring and Metrics

### Query Performance

**Check Slow Queries:**
```cypher
// Show query execution plan
EXPLAIN
MATCH (p:Person)-[:KNOWS*2]->(foaf)
RETURN foaf

// Show actual execution stats
PROFILE
MATCH (p:Person)-[:KNOWS*2]->(foaf)
RETURN foaf
```

**Create Indexes:**
```cypher
// Create index on Person.name
CREATE INDEX person_name FOR (p:Person) ON (p.name)

// Create composite index
CREATE INDEX person_name_age FOR (p:Person) ON (p.name, p.age)

// List all indexes
SHOW INDEXES
```

---

### Database Statistics

```cypher
// Count all nodes
MATCH (n)
RETURN count(n)

// Count all relationships
MATCH ()-[r]->()
RETURN count(r)

// Node counts by label
MATCH (n)
RETURN labels(n), count(n)
ORDER BY count(n) DESC

// Relationship counts by type
MATCH ()-[r]->()
RETURN type(r), count(r)
ORDER BY count(r) DESC
```

---

## 🐛 Troubleshooting

### Neo4j Not Starting

**Check Docker Container:**
```bash
# View logs
sudo docker logs neo4j

# Common issues:
# - Data directory permissions
# - Out of memory
# - Port conflicts
```

**Fix Permissions:**
```bash
# Fix data directory ownership
sudo chown -R 7474:7474 /mnt/neo4j
sudo docker restart neo4j
```

---

### Connection Timeout

**Error:**
```
neo4j.exceptions.ServiceUnavailable: Timed out trying to establish connection
```

**Causes:**
1. Not in VPC (cannot access private IP 10.0.0.2)
2. Neo4j container not running
3. Firewall rules blocking ports

**Solutions:**
- Connect from Cloud Shell or Compute Engine VM in VPC
- Check container status: `sudo docker ps | grep neo4j`
- Verify VM running: `gcloud compute instances describe apex-neo4j-dev`

---

### Authentication Failure

**Error:**
```
neo4j.exceptions.AuthError: The client is unauthorized due to authentication failure
```

**Solution:**
```bash
# Get password from Pulumi
pulumi stack output neo4j_password --show-secrets

# Or reset password by recreating container
```

---

### Out of Memory

**Symptoms:**
- Slow queries
- Container restarts
- OOM errors in logs

**Solution:**
```bash
# Increase heap size (see Performance Tuning section)
# Or upgrade to larger machine type (e2-medium, e2-standard-2)
```

---

## 📚 Learning Resources

**Official Documentation:**
- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/current/
- Neo4j Operations Manual: https://neo4j.com/docs/operations-manual/current/

**Interactive Learning:**
- Neo4j GraphAcademy: https://graphacademy.neo4j.com/
- Cypher Query Language: https://neo4j.com/docs/getting-started/cypher-intro/

**Community:**
- Neo4j Community Forum: https://community.neo4j.com/
- Stack Overflow: https://stackoverflow.com/questions/tagged/neo4j

---

## 🚀 Next Steps

1. ✅ **Access Neo4j Browser** - Set up SSH tunnel from Cloud Shell
2. ✅ **Run Example Queries** - Try the Cypher examples above
3. ✅ **Import Sample Data** - Load CSV data to test import process
4. ✅ **Create Backup** - Set up automated backup schedule
5. 🔜 **Integrate with Application** - Connect from Cloud Run service

---

**Last Updated:** 2025-11-16
**Status:** ✅ Complete
**Next:** Redis Setup Guide

