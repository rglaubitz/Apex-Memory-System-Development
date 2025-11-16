# Authentication System - Deployment Guide

**Feature:** User Authentication with JWT Tokens
**Status:** ✅ Implemented (OPTIONAL for Initial Deployment)
**Impact:** Low - Only needed if API requires public access
**Deployment Week:** Week 3 (OPTIONAL)

---

## Overview

AuthService provides user authentication, password hashing (Bcrypt), and JWT token management.

**Features:**
- User registration and login
- Bcrypt password hashing
- JWT token generation and validation
- API key support (optional)

**When to Deploy:**
- API needs to be public-facing
- Multiple users/teams access the system
- Granular access control required

**When to Skip:**
- Internal-only deployment
- Single-user system
- VPC-protected API

**Dependencies:**
- PostgreSQL (users, api_keys tables)
- SECRET_KEY environment variable (already configured)
- Python packages: `bcrypt`, `python-jose`

---

## Setup Instructions

### Step 1: Run Database Migration

```bash
cd apex-memory-system
alembic upgrade head

# Verify tables
export PGPASSWORD=apexmemory2024
psql -h localhost -U apex -d apex_memory -c "\d users"
psql -h localhost -U apex -d apex_memory -c "\d api_keys"
```

**Migration:** `alembic/versions/f0ca98480aa7_add_users_and_api_keys_tables.py`

### Step 2: Verify SECRET_KEY

```bash
# SECRET_KEY should already be set from Phase 1 prerequisites
gcloud run services describe apex-api --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | grep SECRET_KEY

# If not set, create from Secret Manager
gcloud secrets versions access latest --secret="apex-secret-key"
```

### Step 3: Set JWT Configuration (Optional)

```bash
# Defaults: HS256 algorithm, 3600s (1 hour) expiration
# To customize:
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="JWT_ALGORITHM=HS256,JWT_EXPIRATION=3600"
```

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | (from Secret Manager) | JWT signing key |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `JWT_EXPIRATION` | No | `3600` | Token TTL (seconds) |
| `API_KEY_ENABLED` | No | `false` | Enable API key auth |

---

## Deployment

```bash
# 1. Migration
cd apex-memory-system && alembic upgrade head

# 2. Verify SECRET_KEY exists
gcloud secrets versions access latest --secret="apex-secret-key"

# 3. (Optional) Set JWT config
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="JWT_ALGORITHM=HS256,JWT_EXPIRATION=3600"
```

---

## Verification

### Test User Registration

```bash
export API_URL=$(gcloud run services describe apex-api --region=us-central1 --format="value(status.url)")

curl -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassword123!"
  }'

# Expected: {"user_id": "...", "email": "test@example.com", ...}
```

### Test Login

```bash
curl -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'

# Expected: {"access_token": "eyJhbGc...", "token_type": "bearer"}
```

### Test Protected Endpoint

```bash
export TOKEN=$(curl -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePassword123!"}' | jq -r '.access_token')

curl -X GET "$API_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# Expected: {"email": "test@example.com", "username": "testuser", ...}
```

---

## Troubleshooting

**Issue:** SECRET_KEY not found
**Solution:**
```bash
# Generate new secret
openssl rand -base64 32 | gcloud secrets create apex-secret-key --data-file=-

# Update Cloud Run
gcloud run services update apex-api \
  --region=us-central1 \
  --set-secrets="SECRET_KEY=apex-secret-key:latest"
```

**Issue:** Password hash mismatch
**Solution:**
```bash
# Verify bcrypt is installed
cd apex-memory-system
python -c "import bcrypt; print(bcrypt.__version__)"

# Test hash/verify locally
python -c "
from apex_memory.services.auth_service import AuthService
hash = AuthService.get_password_hash('test123')
print(AuthService.verify_password('test123', hash))
"
# Should print: True
```

---

## Rollback

```bash
# Simply don't require authentication on endpoints
# No code changes needed - authentication is opt-in per endpoint

# (Optional) Revert migration
cd apex-memory-system && alembic downgrade -1
```

---

## Cost Breakdown

**$0/month** - Uses existing infrastructure

---

**Deployment Status:** ✅ Ready (OPTIONAL)
**Recommendation:** Deploy only if API needs public access
**Next Step:** Proceed to Agent Interactions (deferred)
