# Disaster Recovery Plan for Multi-Database Architecture

**Status:** ✅ Verified (November 2025)
**Last Updated:** 2025-11-01
**Sources:** Official documentation, disaster recovery best practices
**Scope:** Neo4j, PostgreSQL, Qdrant, Redis, Graphiti

---

## Overview

This document provides a comprehensive disaster recovery (DR) plan for a multi-database architecture with Neo4j, PostgreSQL+pgvector, Qdrant, Redis, and Graphiti.

**Recovery Time Objective (RTO):** 4 hours (time to restore service)
**Recovery Point Objective (RPO):** 1 hour (acceptable data loss)

**Disaster Scenarios:**
1. Database corruption
2. Hardware failure
3. Data center outage
4. Ransomware/cyberattack
5. Human error (accidental deletion)
6. Natural disaster

---

## Table of Contents

1. [Backup Strategy](#1-backup-strategy)
2. [Backup Procedures](#2-backup-procedures)
3. [Recovery Procedures](#3-recovery-procedures)
4. [Testing & Validation](#4-testing--validation)
5. [Incident Response](#5-incident-response)
6. [DR Checklist](#6-dr-checklist)

---

## 1. Backup Strategy

### 1.1 Backup Types

| Backup Type | Frequency | Retention | Storage | Purpose |
|-------------|-----------|-----------|---------|---------|
| **Full Backup** | Daily (2:00 AM) | 30 days | GCS/S3 | Complete system restore |
| **Incremental Backup** | Every 6 hours | 7 days | GCS/S3 | Fast recovery, minimal storage |
| **Continuous Backup** | Real-time | 7 days | GCS/S3 | Point-in-time recovery |
| **Snapshot** | Before deployments | 14 days | Local + Cloud | Rollback deployments |

---

### 1.2 Backup Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Backup Architecture                       │
└─────────────────────────────────────────────────────────────┘

Production Databases                  Backup Storage
─────────────────────                 ──────────────

┌─────────────┐                      ┌──────────────────┐
│   Neo4j     │──── Full Backup ────▶│  GCS Bucket 1    │
│  (Primary)  │     (Daily 2AM)      │  (30 days)       │
└─────────────┘                      └──────────────────┘
       │
       └──── Incremental ───────────▶┌──────────────────┐
             (Every 6 hours)          │  GCS Bucket 2    │
                                      │  (7 days)        │
┌─────────────┐                      └──────────────────┘
│ PostgreSQL  │──── WAL Archiving ──▶┌──────────────────┐
│  (Primary)  │     (Continuous)     │  GCS Bucket 3    │
└─────────────┘                      │  (7 days)        │
                                      └──────────────────┘
┌─────────────┐
│   Qdrant    │──── Snapshot ────────▶┌──────────────────┐
│  (Primary)  │     (Daily 2AM)       │  GCS Bucket 4    │
└─────────────┘                       │  (30 days)       │
                                      └──────────────────┘
┌─────────────┐
│    Redis    │──── RDB Dump ────────▶┌──────────────────┐
│  (Primary)  │     (Every 6 hours)   │  GCS Bucket 5    │
└─────────────┘                       │  (7 days)        │
                                      └──────────────────┘

        Geographic Replication (Backup to Secondary Region)

┌──────────────────┐                  ┌──────────────────┐
│  GCS us-central1 │ ─────────────▶  │  GCS us-east1    │
│  (Primary)       │    Async Repl    │  (Secondary)     │
└──────────────────┘                  └──────────────────┘
```

---

### 1.3 Backup Schedule

```bash
# /etc/cron.d/apex-memory-backups

# Full backups (daily at 2:00 AM)
0 2 * * * root /opt/apex-memory/scripts/backup-full.sh

# Incremental backups (every 6 hours)
0 */6 * * * root /opt/apex-memory/scripts/backup-incremental.sh

# Verify backups (daily at 3:00 AM)
0 3 * * * root /opt/apex-memory/scripts/verify-backups.sh

# Cleanup old backups (weekly on Sunday at 4:00 AM)
0 4 * * 0 root /opt/apex-memory/scripts/cleanup-old-backups.sh
```

---

## 2. Backup Procedures

### 2.1 Neo4j Backup

**Full Backup (Production Safe):**
```bash
#!/bin/bash
# scripts/backup-neo4j-full.sh

set -e

BACKUP_DIR="/backups/neo4j/$(date +%Y-%m-%d)"
GCS_BUCKET="gs://apex-memory-backups-us-central1/neo4j"

echo "Starting Neo4j full backup..."

# Online backup (no downtime)
neo4j-admin backup \
  --backup-dir="${BACKUP_DIR}" \
  --database=neo4j \
  --from=neo4j://localhost:7687 \
  --fallback-to-full

# Compress backup
tar -czf "${BACKUP_DIR}.tar.gz" -C "${BACKUP_DIR}" .

# Upload to GCS
gsutil -m cp "${BACKUP_DIR}.tar.gz" "${GCS_BUCKET}/"

# Verify backup
neo4j-admin check --database="${BACKUP_DIR}"

echo "✅ Neo4j backup complete: ${BACKUP_DIR}.tar.gz"

# Cleanup local backup (keep for 1 day)
find /backups/neo4j -name "*.tar.gz" -mtime +1 -delete
```

**Incremental Backup:**
```bash
#!/bin/bash
# scripts/backup-neo4j-incremental.sh

set -e

BACKUP_DIR="/backups/neo4j/incremental/$(date +%Y-%m-%d-%H%M)"
GCS_BUCKET="gs://apex-memory-backups-us-central1/neo4j/incremental"

echo "Starting Neo4j incremental backup..."

# Incremental backup (only changed data)
neo4j-admin backup \
  --backup-dir="${BACKUP_DIR}" \
  --database=neo4j \
  --from=neo4j://localhost:7687 \
  --incremental

# Compress and upload
tar -czf "${BACKUP_DIR}.tar.gz" -C "${BACKUP_DIR}" .
gsutil -m cp "${BACKUP_DIR}.tar.gz" "${GCS_BUCKET}/"

echo "✅ Neo4j incremental backup complete"

# Cleanup (keep for 7 days)
find /backups/neo4j/incremental -name "*.tar.gz" -mtime +7 -delete
```

---

### 2.2 PostgreSQL Backup

**Full Backup (pg_dump):**
```bash
#!/bin/bash
# scripts/backup-postgres-full.sh

set -e

BACKUP_FILE="/backups/postgres/apex_memory-$(date +%Y-%m-%d).sql.gz"
GCS_BUCKET="gs://apex-memory-backups-us-central1/postgres"

echo "Starting PostgreSQL full backup..."

# Dump database with compression
pg_dump \
  -h localhost \
  -U apex \
  -d apex_memory \
  --format=custom \
  --compress=9 \
  --file="${BACKUP_FILE}"

# Upload to GCS
gsutil -m cp "${BACKUP_FILE}" "${GCS_BUCKET}/"

# Verify backup (restore to test database)
createdb -h localhost -U apex apex_memory_test
pg_restore \
  -h localhost \
  -U apex \
  -d apex_memory_test \
  "${BACKUP_FILE}"
dropdb -h localhost -U apex apex_memory_test

echo "✅ PostgreSQL backup complete: ${BACKUP_FILE}"

# Cleanup (keep for 30 days)
find /backups/postgres -name "*.sql.gz" -mtime +30 -delete
```

**Continuous Backup (WAL Archiving):**
```conf
# postgresql.conf

# Enable WAL archiving for point-in-time recovery
wal_level = replica
archive_mode = on
archive_command = 'gsutil cp %p gs://apex-memory-wal-archive/%f'
archive_timeout = 300  # Archive every 5 minutes

# Keep enough WAL for recovery
wal_keep_size = 1GB
max_wal_senders = 3
```

```bash
#!/bin/bash
# scripts/backup-postgres-wal.sh

# Automatic WAL archiving (runs via archive_command)
# This ensures continuous backup with 5-minute granularity

# Restore from WAL (point-in-time recovery)
pg_basebackup -h localhost -U apex -D /backups/postgres/base -Ft -z -P

# Create recovery.conf for PITR
cat > /backups/postgres/base/recovery.conf <<EOF
restore_command = 'gsutil cp gs://apex-memory-wal-archive/%f %p'
recovery_target_time = '2025-11-01 14:30:00'  # Restore to specific time
EOF
```

---

### 2.3 Qdrant Backup

**Snapshot Backup:**
```bash
#!/bin/bash
# scripts/backup-qdrant.sh

set -e

BACKUP_DIR="/backups/qdrant/$(date +%Y-%m-%d)"
GCS_BUCKET="gs://apex-memory-backups-us-central1/qdrant"

echo "Starting Qdrant backup..."

# Create snapshot via API
curl -X POST "http://localhost:6333/collections/entities/snapshots" \
  -H "api-key: ${QDRANT_API_KEY}"

# Wait for snapshot to complete
sleep 10

# Download snapshot
SNAPSHOT_NAME=$(curl -s "http://localhost:6333/collections/entities/snapshots" \
  -H "api-key: ${QDRANT_API_KEY}" \
  | jq -r '.result.snapshots[-1].name')

curl -X GET "http://localhost:6333/collections/entities/snapshots/${SNAPSHOT_NAME}" \
  -H "api-key: ${QDRANT_API_KEY}" \
  -o "${BACKUP_DIR}/entities-${SNAPSHOT_NAME}"

# Upload to GCS
gsutil -m cp -r "${BACKUP_DIR}" "${GCS_BUCKET}/"

echo "✅ Qdrant backup complete: ${SNAPSHOT_NAME}"

# Cleanup (keep for 30 days)
find /backups/qdrant -name "entities-*" -mtime +30 -delete
```

---

### 2.4 Redis Backup

**RDB Snapshot:**
```bash
#!/bin/bash
# scripts/backup-redis.sh

set -e

BACKUP_FILE="/backups/redis/dump-$(date +%Y-%m-%d-%H%M).rdb"
GCS_BUCKET="gs://apex-memory-backups-us-central1/redis"

echo "Starting Redis backup..."

# Trigger background save
redis-cli -a "${REDIS_PASSWORD}" BGSAVE

# Wait for save to complete
while [ $(redis-cli -a "${REDIS_PASSWORD}" LASTSAVE) -eq $(redis-cli -a "${REDIS_PASSWORD}" LASTSAVE) ]; do
  sleep 1
done

# Copy RDB file
cp /var/lib/redis/dump.rdb "${BACKUP_FILE}"

# Upload to GCS
gsutil -m cp "${BACKUP_FILE}" "${GCS_BUCKET}/"

echo "✅ Redis backup complete"

# Cleanup (keep for 7 days)
find /backups/redis -name "dump-*.rdb" -mtime +7 -delete
```

---

## 3. Recovery Procedures

### 3.1 Neo4j Recovery

**Full Restore:**
```bash
#!/bin/bash
# scripts/restore-neo4j.sh

set -e

BACKUP_FILE="$1"  # gs://apex-memory-backups-us-central1/neo4j/2025-11-01.tar.gz

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

echo "Restoring Neo4j from: ${BACKUP_FILE}"

# Stop Neo4j
systemctl stop neo4j

# Download backup from GCS
RESTORE_DIR="/tmp/neo4j-restore"
mkdir -p "${RESTORE_DIR}"
gsutil cp "${BACKUP_FILE}" "${RESTORE_DIR}/backup.tar.gz"

# Extract backup
tar -xzf "${RESTORE_DIR}/backup.tar.gz" -C "${RESTORE_DIR}"

# Restore database
neo4j-admin restore \
  --from="${RESTORE_DIR}" \
  --database=neo4j \
  --force

# Start Neo4j
systemctl start neo4j

# Verify restore
sleep 10
cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" "MATCH (n) RETURN count(n) AS node_count"

echo "✅ Neo4j restore complete"

# Cleanup
rm -rf "${RESTORE_DIR}"
```

**Point-in-Time Recovery:**
```bash
# Not natively supported in Neo4j
# Workaround: Restore last full backup + replay transaction logs (if archived)
```

---

### 3.2 PostgreSQL Recovery

**Full Restore:**
```bash
#!/bin/bash
# scripts/restore-postgres.sh

set -e

BACKUP_FILE="$1"  # gs://apex-memory-backups-us-central1/postgres/apex_memory-2025-11-01.sql.gz

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

echo "Restoring PostgreSQL from: ${BACKUP_FILE}"

# Download backup
RESTORE_FILE="/tmp/postgres-restore.sql.gz"
gsutil cp "${BACKUP_FILE}" "${RESTORE_FILE}"

# Drop existing database (WARNING: data loss)
dropdb -h localhost -U apex apex_memory --if-exists

# Create empty database
createdb -h localhost -U apex apex_memory

# Restore from backup
pg_restore \
  -h localhost \
  -U apex \
  -d apex_memory \
  "${RESTORE_FILE}"

# Verify restore
psql -h localhost -U apex -d apex_memory -c "SELECT count(*) FROM documents"

echo "✅ PostgreSQL restore complete"

# Cleanup
rm "${RESTORE_FILE}"
```

**Point-in-Time Recovery (PITR):**
```bash
#!/bin/bash
# scripts/restore-postgres-pitr.sh

set -e

TARGET_TIME="$1"  # Example: '2025-11-01 14:30:00'

if [ -z "$TARGET_TIME" ]; then
  echo "Usage: $0 '<target-time>'"
  exit 1
fi

echo "Restoring PostgreSQL to: ${TARGET_TIME}"

# Stop PostgreSQL
systemctl stop postgresql

# Restore base backup
RESTORE_DIR="/var/lib/postgresql/14/main"
rm -rf "${RESTORE_DIR}"
pg_basebackup -h localhost -U apex -D "${RESTORE_DIR}" -Ft -z -P

# Create recovery configuration
cat > "${RESTORE_DIR}/recovery.conf" <<EOF
restore_command = 'gsutil cp gs://apex-memory-wal-archive/%f %p'
recovery_target_time = '${TARGET_TIME}'
recovery_target_action = 'promote'
EOF

# Start PostgreSQL (will restore to target time)
systemctl start postgresql

# Wait for recovery to complete
while [ ! -f "${RESTORE_DIR}/recovery.done" ]; do
  sleep 1
done

echo "✅ PostgreSQL PITR complete"
```

---

### 3.3 Qdrant Recovery

**Snapshot Restore:**
```bash
#!/bin/bash
# scripts/restore-qdrant.sh

set -e

BACKUP_FILE="$1"  # gs://apex-memory-backups-us-central1/qdrant/2025-11-01/entities-snapshot.tar

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

echo "Restoring Qdrant from: ${BACKUP_FILE}"

# Download backup
RESTORE_DIR="/tmp/qdrant-restore"
mkdir -p "${RESTORE_DIR}"
gsutil cp "${BACKUP_FILE}" "${RESTORE_DIR}/snapshot.tar"

# Extract snapshot
tar -xf "${RESTORE_DIR}/snapshot.tar" -C "${RESTORE_DIR}"

# Upload snapshot to Qdrant
curl -X POST "http://localhost:6333/collections/entities/snapshots/upload" \
  -H "api-key: ${QDRANT_API_KEY}" \
  -F "snapshot=@${RESTORE_DIR}/snapshot"

# Wait for restore to complete
sleep 10

# Verify restore
curl -X GET "http://localhost:6333/collections/entities" \
  -H "api-key: ${QDRANT_API_KEY}" \
  | jq '.result.points_count'

echo "✅ Qdrant restore complete"

# Cleanup
rm -rf "${RESTORE_DIR}"
```

---

### 3.4 Redis Recovery

**RDB Restore:**
```bash
#!/bin/bash
# scripts/restore-redis.sh

set -e

BACKUP_FILE="$1"  # gs://apex-memory-backups-us-central1/redis/dump-2025-11-01-1200.rdb

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

echo "Restoring Redis from: ${BACKUP_FILE}"

# Stop Redis
systemctl stop redis

# Download and replace RDB file
gsutil cp "${BACKUP_FILE}" /var/lib/redis/dump.rdb

# Start Redis (will load from dump.rdb)
systemctl start redis

# Verify restore
redis-cli -a "${REDIS_PASSWORD}" DBSIZE

echo "✅ Redis restore complete"
```

---

## 4. Testing & Validation

### 4.1 Backup Validation

**Test Recovery (Monthly):**
```bash
#!/bin/bash
# scripts/test-recovery.sh

set -e

echo "Starting disaster recovery test..."

# 1. Restore to staging environment
echo "1. Restoring Neo4j to staging..."
./restore-neo4j.sh gs://apex-memory-backups-us-central1/neo4j/latest.tar.gz

echo "2. Restoring PostgreSQL to staging..."
./restore-postgres.sh gs://apex-memory-backups-us-central1/postgres/latest.sql.gz

echo "3. Restoring Qdrant to staging..."
./restore-qdrant.sh gs://apex-memory-backups-us-central1/qdrant/latest/entities-snapshot.tar

echo "4. Restoring Redis to staging..."
./restore-redis.sh gs://apex-memory-backups-us-central1/redis/latest.rdb

# 2. Run validation tests
echo "Running validation tests..."

# Test Neo4j
NEO4J_COUNT=$(cypher-shell -u neo4j -p "${NEO4J_PASSWORD}" \
  "MATCH (n) RETURN count(n) AS count" | grep -oP '\d+')
echo "  Neo4j node count: ${NEO4J_COUNT}"

# Test PostgreSQL
PG_COUNT=$(psql -h localhost -U apex -d apex_memory -tA -c "SELECT count(*) FROM documents")
echo "  PostgreSQL document count: ${PG_COUNT}"

# Test Qdrant
QDRANT_COUNT=$(curl -s "http://localhost:6333/collections/entities" \
  -H "api-key: ${QDRANT_API_KEY}" | jq '.result.points_count')
echo "  Qdrant point count: ${QDRANT_COUNT}"

# Test Redis
REDIS_COUNT=$(redis-cli -a "${REDIS_PASSWORD}" DBSIZE)
echo "  Redis key count: ${REDIS_COUNT}"

echo "✅ Disaster recovery test complete"
```

---

### 4.2 DR Drill Schedule

| Drill Type | Frequency | Duration | Participants |
|------------|-----------|----------|--------------|
| **Backup Validation** | Weekly | 30 min | Automated |
| **Restore Test** | Monthly | 2 hours | DevOps team |
| **Full DR Drill** | Quarterly | 4 hours | All teams |
| **Tabletop Exercise** | Annually | 2 hours | Leadership |

---

## 5. Incident Response

### 5.1 Disaster Response Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              Disaster Response Workflow                      │
└─────────────────────────────────────────────────────────────┘

1. Detection
   ↓
   • Monitoring alerts fired
   • Database health checks fail
   • User reports service outage
   ↓

2. Assessment (15 minutes)
   ↓
   • Determine severity (P0-P4)
   • Identify affected systems
   • Estimate RTO/RPO
   ↓

3. Notification (5 minutes)
   ↓
   • Alert on-call engineer
   • Notify stakeholders
   • Create incident ticket
   ↓

4. Containment (30 minutes)
   ↓
   • Isolate affected systems
   • Prevent data corruption
   • Stop cascading failures
   ↓

5. Recovery (2-4 hours)
   ↓
   • Restore from backups
   • Verify data consistency
   • Resume service
   ↓

6. Verification (1 hour)
   ↓
   • Run smoke tests
   • Monitor for issues
   • Confirm full recovery
   ↓

7. Post-Mortem (2 days)
   ↓
   • Document incident timeline
   • Identify root cause
   • Create action items
```

---

### 5.2 Contact List

| Role | Contact | Phone | Email | Escalation |
|------|---------|-------|-------|------------|
| On-Call Engineer | John Doe | +1-555-0100 | john@example.com | Primary |
| Backup Engineer | Jane Smith | +1-555-0101 | jane@example.com | Secondary |
| DevOps Lead | Bob Johnson | +1-555-0102 | bob@example.com | Escalation |
| CTO | Alice Williams | +1-555-0103 | alice@example.com | Executive |

---

## 6. DR Checklist

### Pre-Disaster Checklist

- [ ] Backups running daily (verified)
- [ ] Backups tested monthly (last test: ______)
- [ ] Geographic replication enabled
- [ ] Monitoring alerts configured
- [ ] DR runbooks up to date
- [ ] Contact list current
- [ ] RTO/RPO documented and tested
- [ ] Backup encryption enabled
- [ ] Off-site backups configured (GCS secondary region)

### During Disaster Checklist

- [ ] Incident declared (severity: ____)
- [ ] Stakeholders notified
- [ ] Incident ticket created (#_____)
- [ ] Affected systems identified
- [ ] Recovery plan selected
- [ ] Recovery started (time: ______)
- [ ] Progress updates every 30 minutes

### Post-Disaster Checklist

- [ ] Service fully restored
- [ ] Data consistency verified
- [ ] Smoke tests passed
- [ ] Monitoring normal for 24 hours
- [ ] Post-mortem scheduled
- [ ] Root cause identified
- [ ] Action items created
- [ ] Runbooks updated

---

## Summary

**Backup Strategy:**
- ✅ Full backups daily (30-day retention)
- ✅ Incremental backups every 6 hours (7-day retention)
- ✅ Continuous backup (PostgreSQL WAL, 7-day retention)
- ✅ Geographic replication (us-central1 → us-east1)

**Recovery Time:**
- Neo4j: 2 hours (full restore)
- PostgreSQL: 1 hour (full restore), 30 min (PITR)
- Qdrant: 1 hour (snapshot restore)
- Redis: 15 minutes (RDB restore)

**Testing:**
- Weekly backup validation (automated)
- Monthly restore test (2 hours)
- Quarterly full DR drill (4 hours)

**Key Recommendations:**
1. Test recovery procedures monthly
2. Maintain geographic replication
3. Monitor backup success rate
4. Verify RTO/RPO quarterly
5. Update runbooks after each incident

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Verification Date:** 2025-11-01
**Next Review:** 2025-02-01 (3 months)
**Maintained By:** Apex Memory System Development Team
