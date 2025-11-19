# Connection Patterns - Neo4j & Redis

**Date:** 2025-11-16
**Status:** ✅ Complete
**Architecture:** Private VPC networking (no external access)

---

## 🔒 Security Architecture

**All databases use private IP addresses only** - no external internet access.

This means:
- ✅ **Secure:** Databases not exposed to internet
- ✅ **VPC-only:** Only resources within the same VPC can connect
- ❌ **Local development:** Cannot connect from your laptop directly
- ✅ **Cloud Run:** Can connect via VPC connector
- ✅ **Compute Engine:** Can connect if in same VPC

---

## 📊 Connection Details

### Neo4j Graph Database

**Instance:** `apex-neo4j-dev`
**Private IP:** `10.0.0.2`
**Ports:**
- Bolt (driver): `7687`
- Browser (UI): `7474`

**Authentication:**
- Username: `neo4j`
- Password: (see `pulumi stack output neo4j_password --show-secrets`)

**Connection URIs:**
```bash
# Bolt protocol (Python, Java, JavaScript drivers)
bolt://10.0.0.2:7687

# Browser interface (HTTP)
http://10.0.0.2:7474
```

---

### Redis Memorystore

**Instance:** `apex-redis-dev`
**Private IP:** `10.123.172.227`
**Port:** `6379`

**Authentication:**
- No password required (VPC-native security)
- Only accessible from authorized network

**Connection String:**
```bash
redis://10.123.172.227:6379
```

---

## 🐍 Python Connection Examples

### Neo4j Connection

```python
from neo4j import GraphDatabase

# Connection details
NEO4J_URI = "bolt://10.0.0.2:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your-password-from-pulumi"  # Get via: pulumi stack output neo4j_password --show-secrets

# Create driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

try:
    # Run a simple query
    with driver.session() as session:
        result = session.run("RETURN 'Hello, Neo4j!' AS message")
        print(result.single()["message"])

    # Create a node
    with driver.session() as session:
        session.run("""
            CREATE (p:Person {name: $name, age: $age})
            RETURN p
        """, name="Alice", age=30)

    # Query relationships
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person)-[:KNOWS]->(friend:Person)
            RETURN p.name as person, friend.name as friend
        """)
        for record in result:
            print(f"{record['person']} knows {record['friend']}")

finally:
    driver.close()
```

---

### Redis Connection

```python
import redis

# Connection details
REDIS_HOST = "10.123.172.227"
REDIS_PORT = 6379

# Create Redis client
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True  # Automatically decode bytes to strings
)

# Test connection
assert r.ping() is True

# Basic operations
r.set("key", "value")
value = r.get("key")  # Returns "value"

# Expiration (TTL)
r.setex("temp_key", 60, "expires in 60 seconds")

# Hash operations (like a dictionary)
r.hset("user:123", mapping={
    "name": "Alice",
    "email": "alice@example.com",
    "age": "30"
})
user = r.hgetall("user:123")  # Returns dict

# List operations (queue)
r.rpush("queue", "task1", "task2", "task3")
task = r.lpop("queue")  # Returns "task1"

# Check configuration
config = r.config_get("maxmemory-policy")
assert config["maxmemory-policy"] == "allkeys-lru"  # LRU eviction enabled
```

---

## 🌐 Where Can You Connect From?

### ✅ **Cloud Run Services**

Cloud Run can connect via the VPC connector deployed in Week 1.

**Connection method:**
1. Set VPC connector in Cloud Run service configuration
2. Use private IPs directly (10.0.0.2, 10.123.172.227)
3. No additional networking configuration needed

**Example Cloud Run config:**
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: apex-api
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/vpc-access-connector: apex-vpc-connector
    spec:
      containers:
      - image: gcr.io/apex-memory-dev/api:latest
        env:
        - name: NEO4J_URI
          value: "bolt://10.0.0.2:7687"
        - name: REDIS_HOST
          value: "10.123.172.227"
```

---

### ✅ **Compute Engine VMs**

Any Compute Engine VM in the same VPC (`apex-memory-vpc-*`) can connect directly.

**Requirements:**
- VM must be in same VPC network
- VM must be in same region (us-central1) or use VPC peering

**Example:**
```bash
# SSH into a Compute Engine VM in the VPC
gcloud compute ssh test-vm --zone=us-central1-a

# Install Neo4j Python driver
pip install neo4j

# Test connection
python3 << EOF
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://10.0.0.2:7687", auth=("neo4j", "password"))
with driver.session() as session:
    result = session.run("RETURN 1 AS num")
    print(result.single()["num"])
driver.close()
EOF
```

---

### ❌ **Local Development (Your Laptop)**

**Cannot connect directly** because databases have private IPs only.

**Why it fails:**
```
neo4j.exceptions.ServiceUnavailable: Timed out trying to establish connection to ResolvedIPv4Address(('10.0.0.2', 7687))
```

**Solutions for local testing:**

#### Option 1: Cloud Shell (Easiest)

Use Google Cloud Shell which runs inside the VPC:

```bash
# Open Cloud Shell: https://shell.cloud.google.com

# Install Neo4j driver
pip install neo4j

# Test connection
python3 << EOF
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://10.0.0.2:7687", auth=("neo4j", "$(pulumi stack output neo4j_password --show-secrets)"))
with driver.session() as session:
    result = session.run("RETURN 1")
    print("Connected successfully!")
driver.close()
EOF
```

#### Option 2: SSH Tunnel via Compute Engine

Create an SSH tunnel through a VM in the VPC:

```bash
# Create a bastion host (if you don't have one)
gcloud compute instances create bastion \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --network=apex-memory-vpc-50b72cc \
    --no-address  # Private IP only

# Create SSH tunnel for Neo4j
gcloud compute ssh bastion --zone=us-central1-a -- \
    -L 7687:10.0.0.2:7687 \
    -L 7474:10.0.0.2:7474 \
    -L 6379:10.123.172.227:6379

# Now connect to localhost:7687 (Neo4j) or localhost:6379 (Redis)
# from your laptop
```

#### Option 3: VPN Connection

Set up a VPN to the VPC (advanced, not covered in this guide).

---

## 🧪 Running Integration Tests

### From Local Machine (Will Fail)

```bash
# This will timeout after 30 seconds
source .venv/bin/activate
PYTHONPATH=. pytest tests/integration/test_neo4j_redis.py -v

# Expected result:
# FAILED - neo4j.exceptions.ServiceUnavailable: Timed out...
```

**Why:** Your laptop is not in the VPC, cannot reach private IPs.

---

### From Cloud Shell (Will Succeed)

```bash
# 1. Open Cloud Shell: https://shell.cloud.google.com

# 2. Clone the repo and install dependencies
git clone <your-repo>
cd deployment/pulumi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install neo4j redis pytest

# 3. Run integration tests
PYTHONPATH=. pytest tests/integration/test_neo4j_redis.py -v

# Expected result:
# 10 tests PASSED ✅
```

---

### From Compute Engine VM

```bash
# 1. Create a test VM in the VPC
gcloud compute instances create test-runner \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --network=apex-memory-vpc-50b72cc \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud

# 2. SSH into the VM
gcloud compute ssh test-runner --zone=us-central1-a

# 3. Install Python and dependencies
sudo apt-get update
sudo apt-get install -y python3-pip git
pip3 install neo4j redis pytest

# 4. Clone repo and run tests
git clone <your-repo>
cd deployment/pulumi
PYTHONPATH=. pytest tests/integration/test_neo4j_redis.py -v
```

---

## 📋 Test Suite Overview

**File:** `tests/integration/test_neo4j_redis.py`

**Neo4j Tests (4 tests):**
- `test_neo4j_connection` - Basic Bolt protocol connectivity
- `test_neo4j_create_node` - Create and retrieve nodes
- `test_neo4j_relationship` - Create and query relationships
- `test_neo4j_persistence` - Verify data persists across connections

**Redis Tests (6 tests):**
- `test_redis_connection` - Basic ping/pong test
- `test_redis_set_get` - Basic key/value operations
- `test_redis_expiration` - TTL and key expiration
- `test_redis_hash_operations` - Hash (dictionary) operations
- `test_redis_list_operations` - List (queue) operations
- `test_redis_lru_eviction` - Verify LRU eviction policy

**Total:** 10 integration tests

---

## 🔧 Troubleshooting

### Connection Timeout

**Error:**
```
neo4j.exceptions.ServiceUnavailable: Timed out trying to establish connection
```

**Cause:** Trying to connect from outside the VPC (e.g., local laptop)

**Solution:** Use Cloud Shell, SSH tunnel, or Compute Engine VM in the VPC

---

### Wrong Password

**Error:**
```
neo4j.exceptions.AuthError: The client is unauthorized due to authentication failure.
```

**Solution:** Get the correct password:
```bash
pulumi stack output neo4j_password --show-secrets
```

---

### Redis Connection Refused

**Error:**
```
redis.exceptions.ConnectionError: Error 111 connecting to 10.123.172.227:6379. Connection refused.
```

**Cause:** Trying to connect from outside the VPC

**Solution:** Use Cloud Shell or Compute Engine VM in the VPC

---

### Neo4j Not Started Yet

**Error:**
```
Connection refused
```

**Cause:** Neo4j container may still be starting (takes 30-60 seconds after VM boot)

**Solution:** Wait 1-2 minutes and try again. Check Neo4j logs:
```bash
gcloud compute ssh apex-neo4j-dev --zone=us-central1-a
sudo docker logs neo4j
```

---

## 📚 Next Steps

1. ✅ **Connection patterns documented** (this file)
2. ✅ **Integration tests created** (10 tests)
3. 🔜 **Run tests from Cloud Shell** (verify connectivity)
4. 🔜 **Create Neo4j setup guide** (browser access, Cypher examples)
5. 🔜 **Create Redis setup guide** (CLI tools, monitoring)

---

## 🔗 References

**Neo4j Documentation:**
- Neo4j Python Driver: https://neo4j.com/docs/python-manual/current/
- Cypher Query Language: https://neo4j.com/docs/cypher-manual/current/

**Redis Documentation:**
- Redis Python Client: https://redis-py.readthedocs.io/
- Redis Commands: https://redis.io/commands/

**GCP Networking:**
- VPC Private Google Access: https://cloud.google.com/vpc/docs/configure-private-google-access
- VPC Connectors: https://cloud.google.com/vpc/docs/configure-serverless-vpc-access

---

**Last Updated:** 2025-11-16
**Status:** ✅ Complete
**Next:** Run integration tests from Cloud Shell to verify connectivity
