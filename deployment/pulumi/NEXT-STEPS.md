# Next Steps - Pulumi Week 1 Implementation

**Last Updated:** 2025-11-08
**Current Status:** 🟢 Phase 0 Complete | 🔵 Ready for Week 1

---

## 🎯 Immediate Next: Week 1 (20-24 hours)

**Goal:** Create VPC networking + Cloud SQL PostgreSQL

**Timeline:** 3-4 days (spread over 1 week)

---

## 📋 Week 1 Task Breakdown

### Task 1: Create VPC Networking Module (8-10 hours)

**File:** `modules/networking.py`

**Deliverables:**
1. VPC network with custom subnet
   - Name: `apex-memory-vpc`
   - Auto-create subnets: `false` (manual control)
   - Private Google Access: `true`

2. Private subnet for databases
   - Name: `apex-db-subnet`
   - CIDR: `10.0.0.0/24`
   - Region: `us-central1`

3. VPC connector for Cloud Run
   - Name: `apex-vpc-connector`
   - Machine type: `e2-micro`
   - Min instances: 2
   - Max instances: 3

4. Cloud NAT for outbound internet
   - Name: `apex-nat`
   - Router: `apex-router`
   - Allows Cloud Run to access internet

5. Private service connection for Cloud SQL
   - Reserved IP range: `10.1.0.0/24`
   - Enables private IP for Cloud SQL

**Code Structure:**
```python
# modules/networking.py
import pulumi
import pulumi_gcp as gcp

def create_vpc_network(project_id: str, region: str):
    """Create VPC network with private Google Access."""
    vpc = gcp.compute.Network(
        "apex-memory-vpc",
        auto_create_subnetworks=False,
        project=project_id,
    )

    subnet = gcp.compute.Subnetwork(
        "apex-db-subnet",
        ip_cidr_range="10.0.0.0/24",
        region=region,
        network=vpc.id,
        private_ip_google_access=True,
    )

    # ... VPC connector, NAT, private connection ...

    return {
        "vpc": vpc,
        "subnet": subnet,
        "vpc_connector": vpc_connector,
    }
```

**Research References:**
- `research/PULUMI-GCP-GUIDE.md` - VPC patterns (lines 450-550)
- `research/PULUMI-EXAMPLES.md` - Networking examples (lines 1200-1400)

**Validation:**
```bash
pulumi preview  # Should show VPC, subnet, connector, NAT
pulumi up       # Deploy networking infrastructure
```

---

### Task 2: Create Cloud SQL PostgreSQL Module (8-10 hours)

**File:** `modules/databases.py`

**Deliverables:**
1. Cloud SQL PostgreSQL instance
   - Name: `apex-postgres-dev`
   - Database version: `POSTGRES_15`
   - Tier: `db-f1-micro` (dev), `db-n1-standard-1` (prod)
   - Private IP only (no public IP)

2. Database configuration
   - Database name: `apex_memory`
   - User: `apex`
   - Password: Generated via Pulumi secret

3. PostgreSQL extensions
   - `pgvector` for vector similarity search
   - `pg_stat_statements` for query monitoring

4. Connection outputs
   - Private IP address
   - Connection string
   - Database name

**Code Structure:**
```python
# modules/databases.py
import pulumi
import pulumi_gcp as gcp
import pulumi_random as random

def create_cloud_sql_postgres(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    tier: str = "db-f1-micro"
):
    """Create Cloud SQL PostgreSQL with private IP."""

    # Generate random password
    db_password = random.RandomPassword(
        "postgres-password",
        length=32,
        special=True,
    )

    # Cloud SQL instance
    postgres = gcp.sql.DatabaseInstance(
        "apex-postgres",
        database_version="POSTGRES_15",
        region=region,
        settings=gcp.sql.DatabaseInstanceSettingsArgs(
            tier=tier,
            ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
                ipv4_enabled=False,  # No public IP
                private_network=network_id,
            ),
        ),
    )

    # Database
    database = gcp.sql.Database(
        "apex-memory-db",
        instance=postgres.name,
        name="apex_memory",
    )

    # User
    user = gcp.sql.User(
        "apex-user",
        instance=postgres.name,
        name="apex",
        password=db_password.result,
    )

    return {
        "postgres": postgres,
        "database": database,
        "user": user,
        "password": db_password.result,
    }
```

**Research References:**
- `research/PULUMI-GCP-GUIDE.md` - Cloud SQL patterns (lines 600-750)
- `research/PULUMI-EXAMPLES.md` - Database examples (lines 2000-2200)

**Validation:**
```bash
pulumi preview  # Should show Cloud SQL instance + database + user
pulumi up       # Deploy database infrastructure

# Test connection
pulumi stack output postgres_private_ip
psql -h <private_ip> -U apex -d apex_memory
```

---

### Task 3: Update __main__.py (2-3 hours)

**File:** `__main__.py`

**Changes:**
1. Import networking and database modules
2. Call module functions
3. Export outputs

**Code:**
```python
# __main__.py
import pulumi
import pulumi_gcp as gcp
from modules.networking import create_vpc_network
from modules.databases import create_cloud_sql_postgres

config = pulumi.Config()
gcp_config = pulumi.Config("gcp")
project_id = gcp_config.require("project")
region = gcp_config.get("region") or "us-central1"

# Enable APIs (already done)
# ... existing API enablement code ...

# Create VPC networking
networking = create_vpc_network(project_id, region)

# Create Cloud SQL PostgreSQL
databases = create_cloud_sql_postgres(
    project_id,
    region,
    networking["vpc"].id,
    tier="db-f1-micro",  # Dev tier
)

# Export outputs
pulumi.export("vpc_id", networking["vpc"].id)
pulumi.export("subnet_id", networking["subnet"].id)
pulumi.export("vpc_connector_id", networking["vpc_connector"].id)
pulumi.export("postgres_private_ip", databases["postgres"].private_ip_address)
pulumi.export("postgres_connection_name", databases["postgres"].connection_name)
pulumi.export("database_name", databases["database"].name)
```

**Validation:**
```bash
pulumi preview  # Should show ~15-20 resources
pulumi up       # Deploy all infrastructure
pulumi stack output  # View all outputs
```

---

### Task 4: Create Tests (2-3 hours)

**Files:**
- `tests/unit/test_networking.py` (3 tests)
- `tests/unit/test_databases.py` (2 tests)
- `tests/integration/test_vpc_postgres.py` (2 tests)

**Unit Tests (Mocked):**
```python
# tests/unit/test_networking.py
import unittest
from unittest.mock import patch, MagicMock
import pulumi

class TestNetworking(pulumi.runtime.test.TestCase):
    def test_vpc_creation(self):
        with pulumi.runtime.mocks.Mocks():
            from modules.networking import create_vpc_network
            networking = create_vpc_network("test-project", "us-central1")

            vpc = networking["vpc"]
            self.assertEqual(vpc.auto_create_subnetworks, False)

    def test_subnet_private_access(self):
        # Test private Google Access enabled
        pass

    def test_vpc_connector_created(self):
        # Test VPC connector for Cloud Run
        pass
```

**Integration Tests (Real Resources):**
```python
# tests/integration/test_vpc_postgres.py
import pytest
import subprocess

@pytest.mark.integration
def test_postgres_private_ip_only():
    """Verify PostgreSQL has no public IP."""
    result = subprocess.run(
        ["pulumi", "stack", "output", "postgres_private_ip"],
        capture_output=True,
        text=True,
    )
    private_ip = result.stdout.strip()

    assert private_ip.startswith("10.")  # Private IP range

@pytest.mark.integration
def test_postgres_connectivity():
    """Test PostgreSQL connection from Cloud Run."""
    # Deploy test Cloud Run service
    # Attempt connection to PostgreSQL
    # Verify connection succeeds
    pass
```

**Run Tests:**
```bash
# Unit tests (fast, mocked)
pytest tests/unit/ -v

# Integration tests (slow, real resources)
pytest tests/integration/ -v -m integration
```

---

## 📚 Research References

**Before starting, review:**

1. **PULUMI-GCP-GUIDE.md** (required)
   - VPC networking patterns (lines 450-550)
   - Cloud SQL setup (lines 600-750)
   - Service account creation (lines 800-900)

2. **PULUMI-EXAMPLES.md** (helpful)
   - Networking examples (lines 1200-1400)
   - Database examples (lines 2000-2200)
   - Multi-resource patterns (lines 3000-3200)

3. **PULUMI-BEST-PRACTICES.md** (optional)
   - Module organization (lines 100-200)
   - Testing strategies (lines 500-600)
   - Security patterns (lines 700-800)

---

## 🚀 Quick Start Commands

**Resume work from here:**

```bash
# Navigate to Pulumi directory
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development/deployment/pulumi

# Activate virtual environment
source .venv/bin/activate

# Verify stack
pulumi stack

# Create modules directory
mkdir -p modules tests/unit tests/integration

# Create first module
touch modules/__init__.py
touch modules/networking.py

# Start implementing (see Task 1 above)
code modules/networking.py
```

---

## ✅ Week 1 Completion Checklist

**Before moving to Week 2:**

- [ ] `modules/networking.py` created and working
- [ ] `modules/databases.py` created and working
- [ ] `__main__.py` updated to use modules
- [ ] `pulumi preview` shows ~15-20 resources
- [ ] `pulumi up` deploys without errors
- [ ] PostgreSQL has private IP only (no public IP)
- [ ] VPC connector created for Cloud Run
- [ ] 5 unit tests passing
- [ ] 2 integration tests passing
- [ ] All outputs exported correctly
- [ ] Documentation updated (README.md progress section)

---

## 📊 Expected Timeline

**Day 1 (8 hours):**
- Create `modules/networking.py`
- Test VPC creation
- Create unit tests for networking

**Day 2 (8 hours):**
- Create `modules/databases.py`
- Test Cloud SQL creation
- Create unit tests for databases

**Day 3 (4-6 hours):**
- Update `__main__.py`
- Deploy full stack
- Create integration tests

**Day 4 (2-4 hours):**
- Debug any issues
- Verify connectivity
- Update documentation

**Total: 22-26 hours spread over 4-5 days**

---

## 🎯 Success Criteria

**Week 1 is complete when:**

1. ✅ All infrastructure deploys successfully
2. ✅ PostgreSQL accessible via private IP only
3. ✅ VPC connector enables Cloud Run → PostgreSQL connectivity
4. ✅ All tests passing (7 total)
5. ✅ Documentation updated
6. ✅ No hardcoded secrets in code
7. ✅ All outputs exported correctly

**After Week 1, you'll have:**
- Production-ready VPC networking
- Private PostgreSQL database
- Foundation for Week 2 (Neo4j + Redis)

---

## 💡 Pro Tips

**Before starting:**
- Read SESSION-2025-11-08.md for context
- Review PULUMI-GCP-GUIDE.md for patterns
- Keep Pulumi docs open: https://www.pulumi.com/docs/

**During implementation:**
- Use `pulumi preview` frequently (cheap, fast)
- Test incrementally (don't wait until end)
- Export all important outputs
- Use `pulumi.Output.all()` for dependencies

**Common gotchas:**
- VPC connector takes 5-10 minutes to create
- Cloud SQL takes 10-15 minutes to create
- Private service connection requires IP range reservation
- Always use `private_network` for Cloud SQL (not public IP)

---

**Ready to start?** Begin with Task 1: Create VPC Networking Module!
