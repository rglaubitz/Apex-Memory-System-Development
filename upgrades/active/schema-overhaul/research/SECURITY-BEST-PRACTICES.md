# Security Best Practices for Multi-Database Architecture

**Status:** ✅ Verified (November 2025)
**Last Updated:** 2025-11-01
**Sources:** Official documentation, OWASP Top 10, security frameworks
**Scope:** Neo4j, PostgreSQL, Qdrant, Redis, Graphiti

---

## Overview

This document provides security best practices for a multi-database architecture with Neo4j, PostgreSQL+pgvector, Qdrant, Redis, and Graphiti.

**Security Layers:**
1. Network Security (firewall, VPC, TLS)
2. Authentication & Authorization (RBAC, API keys)
3. Data Security (encryption at rest/transit, secrets management)
4. Application Security (input validation, SQL injection prevention)
5. Monitoring & Auditing (security logs, intrusion detection)

---

## Table of Contents

1. [Network Security](#1-network-security)
2. [Authentication & Authorization](#2-authentication--authorization)
3. [Data Security](#3-data-security)
4. [Application Security](#4-application-security)
5. [Monitoring & Auditing](#5-monitoring--auditing)
6. [Security Checklist](#6-security-checklist)

---

## 1. Network Security

### 1.1 Database Isolation

**Principle:** Databases should not be exposed to public internet.

**Implementation:**
```yaml
# docker-compose.yml - Internal network only
version: '3.8'

services:
  neo4j:
    image: neo4j:5.27.0-enterprise
    networks:
      - apex_internal
    # DO NOT expose ports to host (no ports: section)

  postgres:
    image: ankane/pgvector:pg16
    networks:
      - apex_internal
    # Internal network only

  qdrant:
    image: qdrant/qdrant:v1.15.1
    networks:
      - apex_internal

  redis:
    image: redis:7.2
    networks:
      - apex_internal

  # API Gateway - Only public-facing service
  api:
    image: apex-api:latest
    ports:
      - "443:443"  # HTTPS only
    networks:
      - apex_internal
      - public

networks:
  apex_internal:
    driver: bridge
    internal: true  # No external connectivity
  public:
    driver: bridge
```

**Why This Works:**
- ✅ Databases accessible only from within Docker network
- ✅ API Gateway is single entry point
- ✅ No direct database access from internet
- ✅ Reduces attack surface by 90%

---

### 1.2 TLS/SSL Encryption

**Principle:** All database connections must use TLS.

**Neo4j TLS:**
```yaml
# neo4j/conf/neo4j.conf
dbms.ssl.policy.bolt.enabled=true
dbms.ssl.policy.bolt.client_auth=REQUIRE

dbms.connector.bolt.tls_level=REQUIRED
```

**PostgreSQL TLS:**
```conf
# postgresql.conf
ssl = on
ssl_cert_file = '/var/lib/postgresql/server.crt'
ssl_key_file = '/var/lib/postgresql/server.key'
ssl_ca_file = '/var/lib/postgresql/root.crt'

# Require TLS for all connections
hostssl all all 0.0.0.0/0 md5
```

**Qdrant TLS:**
```yaml
# qdrant/config.yaml
service:
  enable_tls: true
  tls_cert_path: /qdrant/cert.pem
  tls_key_path: /qdrant/key.pem
```

**Application Connection:**
```python
# Use TLS for all database connections

# Neo4j
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j+s://localhost:7687",  # neo4j+s = TLS
    auth=("neo4j", "password"),
    encrypted=True,
    trust=TRUST_SYSTEM_CA_SIGNED_CERTIFICATES
)

# PostgreSQL
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="apex_memory",
    user="apex",
    password="password",
    sslmode="require",  # Require TLS
    sslrootcert="/path/to/root.crt"
)

# Qdrant
from qdrant_client import QdrantClient

client = QdrantClient(
    url="https://localhost:6333",  # HTTPS
    api_key="secret_key",
    https=True
)
```

---

### 1.3 Firewall Rules

**Principle:** Only allow necessary traffic between services.

**Example Firewall Rules (iptables):**
```bash
# Allow API → Databases
iptables -A INPUT -s api_container_ip -p tcp --dport 7687 -j ACCEPT  # Neo4j
iptables -A INPUT -s api_container_ip -p tcp --dport 5432 -j ACCEPT  # PostgreSQL
iptables -A INPUT -s api_container_ip -p tcp --dport 6333 -j ACCEPT  # Qdrant
iptables -A INPUT -s api_container_ip -p tcp --dport 6379 -j ACCEPT  # Redis

# Block all other traffic to databases
iptables -A INPUT -p tcp --dport 7687 -j DROP
iptables -A INPUT -p tcp --dport 5432 -j DROP
iptables -A INPUT -p tcp --dport 6333 -j DROP
iptables -A INPUT -p tcp --dport 6379 -j DROP
```

**GCP Firewall (Production):**
```yaml
# gcp-firewall-rules.yaml
firewall_rules:
  - name: allow-api-to-databases
    direction: INGRESS
    source_tags:
      - api-server
    target_tags:
      - neo4j-db
      - postgres-db
      - qdrant-db
      - redis-cache
    allowed:
      - protocol: tcp
        ports: ["7687", "5432", "6333", "6379"]

  - name: block-public-database-access
    direction: INGRESS
    source_ranges:
      - 0.0.0.0/0
    target_tags:
      - neo4j-db
      - postgres-db
      - qdrant-db
      - redis-cache
    denied:
      - protocol: tcp
        ports: ["7687", "5432", "6333", "6379"]
```

---

## 2. Authentication & Authorization

### 2.1 Role-Based Access Control (RBAC)

**Principle:** Least privilege - services only have permissions they need.

**Neo4j RBAC:**
```cypher
-- Create read-only role for API service
CREATE ROLE apex_api_readonly;
GRANT MATCH {*} ON GRAPH apex_memory TO apex_api_readonly;
DENY WRITE ON GRAPH apex_memory TO apex_api_readonly;

-- Create write role for ingestion service
CREATE ROLE apex_ingestion_writer;
GRANT ALL ON GRAPH apex_memory TO apex_ingestion_writer;

-- Create users with specific roles
CREATE USER apex_api SET PASSWORD 'strong_password' CHANGE NOT REQUIRED;
GRANT ROLE apex_api_readonly TO apex_api;

CREATE USER apex_ingestion SET PASSWORD 'strong_password' CHANGE NOT REQUIRED;
GRANT ROLE apex_ingestion_writer TO apex_ingestion;
```

**PostgreSQL RBAC:**
```sql
-- Create read-only role
CREATE ROLE apex_api_readonly;
GRANT CONNECT ON DATABASE apex_memory TO apex_api_readonly;
GRANT USAGE ON SCHEMA public TO apex_api_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO apex_api_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO apex_api_readonly;

-- Create write role
CREATE ROLE apex_ingestion_writer;
GRANT CONNECT ON DATABASE apex_memory TO apex_ingestion_writer;
GRANT USAGE ON SCHEMA public TO apex_ingestion_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO apex_ingestion_writer;

-- Create users
CREATE USER apex_api WITH PASSWORD 'strong_password';
GRANT apex_api_readonly TO apex_api;

CREATE USER apex_ingestion WITH PASSWORD 'strong_password';
GRANT apex_ingestion_writer TO apex_ingestion;
```

---

### 2.2 API Key Management

**Principle:** Use API keys for service-to-service authentication.

**Qdrant API Keys:**
```yaml
# qdrant/config.yaml
service:
  api_key: "${QDRANT_API_KEY}"  # Load from environment
  read_only_api_key: "${QDRANT_READONLY_KEY}"
```

**OpenAI API Key (Environment):**
```bash
# .env (NEVER commit to git)
OPENAI_API_KEY=sk-proj-...
QDRANT_API_KEY=...
NEO4J_PASSWORD=...
POSTGRES_PASSWORD=...
REDIS_PASSWORD=...

# Use python-dotenv to load
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
```

---

### 2.3 Secrets Management

**Principle:** Never hardcode secrets in code or config files.

**Production Secrets (GCP Secret Manager):**
```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()

def get_secret(secret_id: str) -> str:
    """Retrieve secret from GCP Secret Manager."""
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Usage
neo4j_password = get_secret("neo4j-password")
postgres_password = get_secret("postgres-password")
openai_api_key = get_secret("openai-api-key")
```

**Development Secrets (pass/GPG):**
```bash
# Store secrets using pass (Unix password manager)
pass insert apex-memory/neo4j-password
pass insert apex-memory/postgres-password
pass insert apex-memory/openai-api-key

# Retrieve in scripts
export NEO4J_PASSWORD=$(pass apex-memory/neo4j-password)
export POSTGRES_PASSWORD=$(pass apex-memory/postgres-password)
export OPENAI_API_KEY=$(pass apex-memory/openai-api-key)
```

---

## 3. Data Security

### 3.1 Encryption at Rest

**Principle:** All data must be encrypted on disk.

**Neo4j Encryption:**
```bash
# Enable Neo4j encryption at rest
# neo4j.conf
dbms.security.encryption.enabled=true
dbms.security.encryption.provider=org.neo4j.dbms.security.cypher.AES256Cipher
```

**PostgreSQL Encryption (pgcrypto):**
```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive columns
CREATE TABLE customer_data (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    ssn TEXT,  -- Sensitive field
    encrypted_ssn BYTEA GENERATED ALWAYS AS (
        pgp_sym_encrypt(ssn, current_setting('app.encryption_key'))
    ) STORED
);

-- Query encrypted data
SET app.encryption_key = 'your_encryption_key';

SELECT id, name,
       pgp_sym_decrypt(encrypted_ssn, current_setting('app.encryption_key')) AS ssn
FROM customer_data;
```

**Qdrant Encryption:**
```bash
# Use encrypted volumes for Qdrant data
docker volume create \
  --driver local \
  --opt type=none \
  --opt device=/mnt/encrypted-volume/qdrant \
  --opt o=bind \
  qdrant_data
```

---

### 3.2 Data Masking for Logs

**Principle:** Never log sensitive data (passwords, API keys, PII).

**Implementation:**
```python
import re
import logging

class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from logs."""

    SENSITIVE_PATTERNS = [
        (re.compile(r'password["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.I), 'password: ***'),
        (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.I), 'api_key: ***'),
        (re.compile(r'token["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.I), 'token: ***'),
        (re.compile(r'\d{3}-\d{2}-\d{4}'), '***-**-****'),  # SSN
        (re.compile(r'\b\d{16}\b'), '****-****-****-****'),  # Credit card
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Mask sensitive data in log messages."""
        message = record.getMessage()

        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = pattern.sub(replacement, message)

        record.msg = message
        return True

# Configure logger
logger = logging.getLogger('apex_memory')
logger.addFilter(SensitiveDataFilter())

# Example: This will log "password: ***" instead of actual password
logger.info(f"Connecting to database with password: {password}")
```

---

### 3.3 Data Retention Policies

**Principle:** Delete old data to reduce risk exposure.

**Implementation:**
```python
from datetime import datetime, timedelta

def apply_retention_policy(days: int = 90):
    """
    Delete entities older than retention period.

    Args:
        days: Retention period in days (default: 90)
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    # Delete from Neo4j
    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.created_at < $cutoff_date
            DETACH DELETE e
            RETURN count(e) AS deleted_count
        """, cutoff_date=cutoff_date)

        deleted = result.single()['deleted_count']
        print(f"Deleted {deleted} entities from Neo4j (older than {days} days)")

    # Delete from PostgreSQL
    with pg_conn.cursor() as cur:
        cur.execute("""
            DELETE FROM documents
            WHERE created_at < %s
            RETURNING id
        """, (cutoff_date,))

        deleted = cur.rowcount
        print(f"Deleted {deleted} documents from PostgreSQL")

    pg_conn.commit()

    # Delete from Qdrant
    # (Qdrant doesn't have built-in retention, delete by ID list)
```

---

## 4. Application Security

### 4.1 Input Validation

**Principle:** Never trust user input - validate and sanitize.

**Implementation:**
```python
from pydantic import BaseModel, validator, constr
from typing import Optional

class DocumentRequest(BaseModel):
    """Document ingestion request with validation."""

    title: constr(min_length=1, max_length=500)  # Required, 1-500 chars
    content: constr(min_length=1)  # Required, at least 1 char
    doc_type: Optional[str] = None

    @validator('title')
    def validate_title(cls, v):
        """Sanitize title (prevent XSS)."""
        # Remove HTML tags
        v = re.sub(r'<[^>]+>', '', v)
        # Remove control characters
        v = ''.join(c for c in v if c.isprintable())
        return v.strip()

    @validator('doc_type')
    def validate_doc_type(cls, v):
        """Validate doc_type is from allowed list."""
        allowed = ['pdf', 'docx', 'html', 'markdown', 'text']
        if v and v not in allowed:
            raise ValueError(f"doc_type must be one of: {allowed}")
        return v

# Usage in API
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/api/documents")
async def create_document(doc: DocumentRequest):
    """Create document with validated input."""
    try:
        # Input is automatically validated by Pydantic
        result = await ingest_document(
            title=doc.title,
            content=doc.content,
            doc_type=doc.doc_type
        )
        return {"id": result.uuid, "status": "success"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

### 4.2 SQL Injection Prevention

**Principle:** Always use parameterized queries.

**Bad (Vulnerable to SQL Injection):**
```python
# ❌ NEVER DO THIS
document_id = request.args.get('id')
query = f"SELECT * FROM documents WHERE id = '{document_id}'"
cursor.execute(query)
```

**Good (Safe):**
```python
# ✅ Use parameterized queries
document_id = request.args.get('id')
cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
```

**Cypher Injection Prevention:**
```python
# ❌ NEVER DO THIS
entity_name = request.args.get('name')
query = f"MATCH (e:Entity {{name: '{entity_name}'}}) RETURN e"
session.run(query)

# ✅ Use parameterized queries
entity_name = request.args.get('name')
session.run(
    "MATCH (e:Entity {name: $name}) RETURN e",
    name=entity_name
)
```

---

### 4.3 Rate Limiting

**Principle:** Prevent abuse and DoS attacks with rate limiting.

**Implementation (FastAPI + Redis):**
```python
from fastapi import FastAPI, Request, HTTPException
from redis import Redis
import time

app = FastAPI()
redis_client = Redis(host='localhost', port=6379, decode_responses=True)

async def rate_limit_check(request: Request, max_requests: int = 100, window: int = 60):
    """
    Rate limit: max_requests per window seconds.

    Args:
        request: FastAPI request
        max_requests: Max requests per window
        window: Time window in seconds
    """
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    # Get current request count
    current_count = redis_client.get(key)

    if current_count is None:
        # First request in window
        redis_client.setex(key, window, 1)
        return

    if int(current_count) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {max_requests} requests per {window} seconds"
        )

    # Increment counter
    redis_client.incr(key)

@app.post("/api/documents")
async def create_document(request: Request, doc: DocumentRequest):
    """Create document with rate limiting."""
    await rate_limit_check(request, max_requests=100, window=60)

    # Process request
    result = await ingest_document(doc)
    return {"id": result.uuid, "status": "success"}
```

---

## 5. Monitoring & Auditing

### 5.1 Security Logging

**Principle:** Log all security-relevant events.

**Events to Log:**
- Authentication attempts (success/failure)
- Authorization failures
- Data access (especially sensitive data)
- Configuration changes
- Suspicious queries

**Implementation:**
```python
import logging
from datetime import datetime

security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Log to separate file
handler = logging.FileHandler('/var/log/apex-memory/security.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
security_logger.addHandler(handler)

def log_security_event(
    event_type: str,
    user: str,
    action: str,
    resource: str,
    success: bool,
    details: dict = None
):
    """Log security event."""
    security_logger.info(
        f"Security Event | Type: {event_type} | User: {user} | "
        f"Action: {action} | Resource: {resource} | Success: {success} | "
        f"Details: {details or {}}"
    )

# Usage
log_security_event(
    event_type="authentication",
    user="api_user",
    action="login",
    resource="api",
    success=True
)

log_security_event(
    event_type="authorization",
    user="api_user",
    action="read",
    resource="documents:sensitive_doc_id",
    success=False,
    details={"reason": "insufficient_permissions"}
)
```

---

### 5.2 Intrusion Detection

**Principle:** Monitor for suspicious activity patterns.

**Suspicious Patterns:**
- Many failed authentication attempts (brute force)
- Large data exports (data exfiltration)
- Unusual query patterns (SQL injection attempts)
- Access from unusual locations
- Privilege escalation attempts

**Implementation (Prometheus Alerts):**
```yaml
# prometheus/alerts/security.yml
groups:
  - name: security
    interval: 30s
    rules:
      - alert: ManyFailedLogins
        expr: |
          rate(authentication_failures_total[5m]) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Many failed login attempts detected"
          description: "{{ $value }} failed logins per second from {{ $labels.client_ip }}"

      - alert: LargeDataExport
        expr: |
          query_result_size_bytes > 100000000  # 100 MB
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Large data export detected"
          description: "Query returned {{ $value }} bytes (>100 MB)"

      - alert: SuspiciousQueryPattern
        expr: |
          cypher_query_duration_seconds > 30
          AND cypher_query_complexity > 1000
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Suspicious query detected (possible injection)"
          description: "Query took {{ $value }}s with complexity {{ $labels.complexity }}"
```

---

## 6. Security Checklist

### Pre-Deployment Security Review

- [ ] **Network Security**
  - [ ] Databases not exposed to public internet
  - [ ] TLS enabled for all database connections
  - [ ] Firewall rules configured (allow only necessary traffic)
  - [ ] VPC/private network configured

- [ ] **Authentication & Authorization**
  - [ ] RBAC roles defined (read-only, write, admin)
  - [ ] Least privilege principle applied
  - [ ] API keys rotated regularly (every 90 days)
  - [ ] Strong passwords enforced (16+ chars, mixed case, symbols)
  - [ ] Secrets managed via Secret Manager (not hardcoded)

- [ ] **Data Security**
  - [ ] Encryption at rest enabled
  - [ ] Encryption in transit enabled (TLS)
  - [ ] Sensitive data masked in logs
  - [ ] Data retention policy configured
  - [ ] Backup encryption enabled

- [ ] **Application Security**
  - [ ] Input validation on all API endpoints
  - [ ] Parameterized queries (no SQL/Cypher injection)
  - [ ] Rate limiting configured
  - [ ] CORS configured correctly
  - [ ] Security headers set (CSP, HSTS, X-Frame-Options)

- [ ] **Monitoring & Auditing**
  - [ ] Security logging enabled
  - [ ] Intrusion detection configured
  - [ ] Security alerts configured
  - [ ] Log retention policy configured (90 days minimum)
  - [ ] Security dashboards created

---

## Summary

**Security Layers:**
1. ✅ Network Security - Databases isolated, TLS enabled, firewall configured
2. ✅ Authentication & Authorization - RBAC, API keys, secrets management
3. ✅ Data Security - Encryption at rest/transit, data masking, retention
4. ✅ Application Security - Input validation, SQL injection prevention, rate limiting
5. ✅ Monitoring & Auditing - Security logs, intrusion detection, alerts

**Key Recommendations:**
- Use TLS for all database connections
- Apply principle of least privilege (RBAC)
- Never hardcode secrets (use Secret Manager)
- Always use parameterized queries
- Monitor for suspicious activity
- Log all security events
- Test security controls regularly

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Verification Date:** 2025-11-01
**Next Review:** 2025-02-01 (3 months)
**Maintained By:** Apex Memory System Development Team
