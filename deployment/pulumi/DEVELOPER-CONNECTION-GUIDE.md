# Developer Connection Guide

**Last Updated:** 2025-11-16
**PostgreSQL Version:** 17  
**Instance:** apex-postgres-dev

---

## Quick Start

```bash
# Terminal 1 - Start Cloud SQL Proxy
cloud-sql-proxy apex-memory-dev:us-central1:apex-postgres-dev

# Terminal 2 - Connect
export PGPASSWORD=$(cat /tmp/apex-postgres-password.txt)
psql -h 127.0.0.1 -p 5432 -U apex -d apex_memory
```

---

## Prerequisites

**Install Cloud SQL Proxy:**
```bash
brew install cloud-sql-proxy
```

**Get Password:**
```bash
cat /tmp/apex-postgres-password.txt
```

**Connection Details:**
- Instance: apex-postgres-dev
- Connection Name: apex-memory-dev:us-central1:apex-postgres-dev  
- Database: apex_memory
- User: apex
- Port: 5432 (local proxy)

---

## Local Development

**Start Proxy:**
```bash
cloud-sql-proxy apex-memory-dev:us-central1:apex-postgres-dev
```

**Connect with psql:**
```bash
PGPASSWORD=$(cat /tmp/apex-postgres-password.txt) psql -h 127.0.0.1 -U apex -d apex_memory
```

**Python Connection:**
```python
import psycopg2

with open('/tmp/apex-postgres-password.txt') as f:
    password = f.read().strip()

conn = psycopg2.connect(
    host='127.0.0.1',
    port=5432,
    database='apex_memory',
    user='apex',
    password=password
)
```

---

## Cloud Run Connection

**Use Unix Socket:**
```python
INSTANCE_CONNECTION_NAME = 'apex-memory-dev:us-central1:apex-postgres-dev'

conn = psycopg2.connect(
    host=f'/cloudsql/{INSTANCE_CONNECTION_NAME}',
    database='apex_memory',
    user='apex',
    password=os.environ['DB_PASSWORD']
)
```

---

## Common Tasks

**Check Version:**
```sql
SELECT version();
```

**List Tables:**
```sql
\dt
```

**Test Connection:**
```sql
SELECT current_database(), current_user, inet_server_addr();
```

---

## Troubleshooting

**Proxy not found:**
```bash
brew install cloud-sql-proxy
```

**Connection refused:**
```bash
# Check proxy running
ps aux | grep cloud-sql-proxy

# Restart
cloud-sql-proxy apex-memory-dev:us-central1:apex-postgres-dev
```

**Auth failed:**
```bash
gcloud auth application-default login
```

---

For complete documentation, see ARCHITECTURE-DIAGRAM.md and POSTGRESQL-17-UPGRADE.md
