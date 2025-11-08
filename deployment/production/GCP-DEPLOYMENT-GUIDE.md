# Apex Memory System - GCP Deployment Guide

**Purpose:** Complete step-by-step guide to deploy Apex Memory System to Google Cloud Platform.

**Prerequisites:** ⚠️ **MUST complete [../DEPLOYMENT-NEEDS.md](../DEPLOYMENT-NEEDS.md) before starting this guide.**

**Timeline:** 8-12 hours for first deployment, 2-4 hours for subsequent deployments.

**Cost:** ~$720-950/month (production), free for first 90 days with GCP trial credits.

---

## ⚠️ PREREQUISITES - COMPLETE FIRST

**CRITICAL:** Before starting Phase 1, you MUST have:

📋 **[Complete prerequisite checklist: ../DEPLOYMENT-NEEDS.md](../DEPLOYMENT-NEEDS.md)**

**Quick verification:**
- [ ] GCP account created with billing enabled ($300 free credit)
- [ ] Temporal Cloud namespace created ($100-150/month)
- [ ] Grafana Cloud Pro account ($19/month)
- [ ] OpenAI API key obtained and stored in password manager
- [ ] Anthropic API key obtained and stored in password manager
- [ ] Docker Desktop licensed correctly (check if Business license needed)
- [ ] All secrets generated (SECRET_KEY, DB passwords) and stored securely
- [ ] gcloud CLI installed and authenticated (`gcloud auth login`)
- [ ] Pulumi CLI installed (`pulumi version`)
- [ ] 2FA enabled on all cloud accounts
- [ ] All 156+ tests passing locally (`pytest`)

**Estimated setup time:** 4-6 hours (if starting from scratch)
**Monthly cost after prerequisites:** $411-807/month (or $149-249/month for first 90 days with GCP credits)

**⛔ DO NOT PROCEED** until ALL checkboxes above are complete.

See **[../DEPLOYMENT-NEEDS.md](../DEPLOYMENT-NEEDS.md)** for detailed setup instructions.

---

## Table of Contents

- [Prerequisites](#prerequisites---complete-first)
- [Phase 1: Foundation Setup](#phase-1-foundation-setup)
- [Phase 2: Database Deployment](#phase-2-database-deployment)
- [Phase 3: Temporal Setup](#phase-3-temporal-setup)
- [Phase 4: Application Deployment](#phase-4-application-deployment)
- [Phase 5: Monitoring Setup](#phase-5-monitoring-setup)
- [Phase 6: CI/CD Pipeline](#phase-6-cicd-pipeline)
- [Phase 7: Production Validation](#phase-7-production-validation)
- [Phase 8: Production Release](#phase-8-production-release)
- [Troubleshooting](#troubleshooting)

---

## Phase 1: Foundation Setup

**Goal:** Set up GCP project, enable APIs, configure networking, initialize Secret Manager.

**Time:** 1-2 hours

**Cost Impact:** ~$0 (foundation infrastructure, minimal costs)

---

### 1.1 GCP Project Creation

**Create a new GCP project for production:**

```bash
# Set project variables
export PROJECT_ID="apex-memory-prod"
export PROJECT_NAME="Apex Memory Production"
export REGION="us-central1"  # Change if needed (us-west1, europe-west1, etc.)
export ZONE="${REGION}-a"

# Create project
gcloud projects create $PROJECT_ID \
  --name="$PROJECT_NAME" \
  --set-as-default

# Link billing account (find billing account ID first)
gcloud billing accounts list
export BILLING_ACCOUNT_ID="YOUR_BILLING_ACCOUNT_ID"

gcloud billing projects link $PROJECT_ID \
  --billing-account=$BILLING_ACCOUNT_ID

# Set default project
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE
```

**Validation:**
```bash
gcloud projects describe $PROJECT_ID
# Expected: Project details displayed, billingAccountName present
```

---

### 1.2 Enable Required APIs

**Enable all necessary GCP APIs:**

```bash
# Core compute and networking
gcloud services enable compute.googleapis.com
gcloud services enable vpcaccess.googleapis.com

# Databases
gcloud services enable sqladmin.googleapis.com
gcloud services enable redis.googleapis.com

# Application hosting
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Secrets and configuration
gcloud services enable secretmanager.googleapis.com

# Monitoring
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Networking
gcloud services enable servicenetworking.googleapis.com

# Wait for APIs to propagate (1-2 minutes)
sleep 120
```

**Validation:**
```bash
gcloud services list --enabled | grep -E "compute|sql|run|redis|secret"
# Expected: All above services listed
```

---

### 1.3 Configure VPC Networking

**Create VPC network for database and service communication:**

```bash
# Create VPC network
gcloud compute networks create apex-network \
  --subnet-mode=auto \
  --bgp-routing-mode=regional

# Create VPC connector for Cloud Run <-> Cloud SQL/Redis communication
gcloud compute networks vpc-access connectors create apex-connector \
  --region=$REGION \
  --network=apex-network \
  --range=10.8.0.0/28 \
  --min-instances=2 \
  --max-instances=3

# Reserve IP range for Private Service Connection (Cloud SQL)
gcloud compute addresses create google-managed-services-apex-network \
  --global \
  --purpose=VPC_PEERING \
  --prefix-length=16 \
  --network=apex-network

# Create Private Service Connection
gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --ranges=google-managed-services-apex-network \
  --network=apex-network
```

**Validation:**
```bash
# Check VPC connector
gcloud compute networks vpc-access connectors describe apex-connector \
  --region=$REGION
# Expected: State: READY

# Check private service connection
gcloud compute addresses describe google-managed-services-apex-network \
  --global
# Expected: status: RESERVED
```

**Troubleshooting:**
- **"Quota exceeded" error:** Request quota increase for VPC connectors (default: 0 in new projects)
- **Connector stuck in CREATING:** Wait 5-10 minutes, VPC connector creation is slow
- **Private connection failed:** Ensure servicenetworking API is enabled

---

### 1.4 Initialize Secret Manager

**Create secrets for all credentials:**

```bash
# OpenAI API key
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy="automatic"

# PostgreSQL password (generate strong password)
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
echo -n "$POSTGRES_PASSWORD" | gcloud secrets create postgres-password \
  --data-file=- \
  --replication-policy="automatic"

# Neo4j password (generate strong password)
export NEO4J_PASSWORD=$(openssl rand -base64 32)
echo -n "$NEO4J_PASSWORD" | gcloud secrets create neo4j-password \
  --data-file=- \
  --replication-policy="automatic"

# Save passwords locally (TEMPORARY - delete after adding to password manager)
echo "PostgreSQL password: $POSTGRES_PASSWORD" > /tmp/apex-passwords.txt
echo "Neo4j password: $NEO4J_PASSWORD" >> /tmp/apex-passwords.txt
echo "Passwords saved to /tmp/apex-passwords.txt - MOVE TO PASSWORD MANAGER AND DELETE!"

# Grant Cloud Run access to secrets
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding postgres-password \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding neo4j-password \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Validation:**
```bash
# List secrets
gcloud secrets list
# Expected: openai-api-key, postgres-password, neo4j-password

# Test access
gcloud secrets versions access latest --secret=openai-api-key
# Expected: Your OpenAI API key displayed
```

---

### 1.5 Configure Budget Alerts

**Set up budget monitoring (CRITICAL):**

```bash
# Create budget via gcloud (or use Console for more options)
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT_ID \
  --display-name="Apex Memory Production Budget" \
  --budget-amount=1500USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

**Alternative: Use GCP Console (Recommended for detailed config):**

1. Navigate to: https://console.cloud.google.com/billing/budgets
2. Click "Create Budget"
3. Budget name: "Apex Memory Production Budget"
4. Amount: $1,500/month
5. Threshold alerts: 50%, 80%, 90%, 100%
6. Email recipients: Your email
7. Click "Finish"

**Validation:**
- Check email for budget alert confirmation
- View budget: https://console.cloud.google.com/billing/budgets

---

### Phase 1 Summary

**Completed:**
- ✅ GCP project created and configured
- ✅ All necessary APIs enabled
- ✅ VPC networking configured
- ✅ Secret Manager initialized with credentials
- ✅ Budget alerts configured

**Time Spent:** ~1-2 hours

**Next Phase:** [Phase 2: Database Deployment](#phase-2-database-deployment)

---

## Phase 2: Database Deployment

**Goal:** Deploy all 4 databases (Cloud SQL, Memorystore Redis, Compute Engine for Neo4j, Cloud Run for Qdrant).

**Time:** 3-4 hours

**Cost Impact:** ~$420-570/month

---

### 2.1 Deploy Cloud SQL (PostgreSQL + pgvector)

**Create Cloud SQL instance:**

```bash
# Create Cloud SQL instance (takes 5-10 minutes)
gcloud sql instances create apex-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-n1-standard-2 \
  --region=$REGION \
  --network=projects/$PROJECT_ID/global/networks/apex-network \
  --no-assign-ip \
  --database-flags=cloudsql.enable_pgvector=on

# Wait for instance to be ready
gcloud sql instances describe apex-postgres --format="value(state)"
# Expected: RUNNABLE

# Create database
gcloud sql databases create apex_memory \
  --instance=apex-postgres

# Retrieve postgres password from Secret Manager
export POSTGRES_PASSWORD=$(gcloud secrets versions access latest --secret=postgres-password)

# Set root password
gcloud sql users set-password postgres \
  --instance=apex-postgres \
  --password=$POSTGRES_PASSWORD

# Create application user
gcloud sql users create apex \
  --instance=apex-postgres \
  --password=$POSTGRES_PASSWORD

# Get instance connection name (needed for Cloud Run)
export SQL_CONNECTION_NAME=$(gcloud sql instances describe apex-postgres \
  --format="value(connectionName)")

echo "SQL Connection Name: $SQL_CONNECTION_NAME"
echo "Save this - you'll need it for Cloud Run deployment"
```

**Install pgvector extension:**

```bash
# Connect to database
gcloud sql connect apex-postgres --user=postgres --quiet

# Once connected (will prompt for password):
\c apex_memory
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

**Validation:**
```bash
# Check instance status
gcloud sql instances list
# Expected: apex-postgres in RUNNABLE state

# Test connection
gcloud sql connect apex-postgres --user=postgres
\c apex_memory
SELECT extname FROM pg_extension WHERE extname = 'vector';
# Expected: vector extension listed
\q
```

**Cost:** ~$250-350/month (db-n1-standard-2: 2 vCPU, 7.5GB RAM)

**Troubleshooting:**
- **"Could not connect" error:** Check VPC network configuration, ensure Private Service Connection is active
- **pgvector extension not found:** Ensure `cloudsql.enable_pgvector=on` flag is set
- **Slow instance creation:** Normal, Cloud SQL instances take 5-10 minutes to provision

---

### 2.2 Deploy Memorystore (Redis)

**Create Redis instance:**

```bash
# Create Memorystore Redis instance (takes 5-10 minutes)
gcloud redis instances create apex-redis \
  --size=1 \
  --region=$REGION \
  --network=projects/$PROJECT_ID/global/networks/apex-network \
  --tier=basic \
  --redis-version=redis_7_0

# Wait for instance to be ready
gcloud redis instances describe apex-redis --region=$REGION \
  --format="value(state)"
# Expected: READY

# Get Redis connection details
export REDIS_HOST=$(gcloud redis instances describe apex-redis \
  --region=$REGION --format="value(host)")
export REDIS_PORT=$(gcloud redis instances describe apex-redis \
  --region=$REGION --format="value(port)")

echo "Redis Host: $REDIS_HOST"
echo "Redis Port: $REDIS_PORT"
echo "Connection string: redis://$REDIS_HOST:$REDIS_PORT"
```

**Validation:**
```bash
# Check instance status
gcloud redis instances list --region=$REGION
# Expected: apex-redis in READY state

# Test connection (requires VM in same VPC or Cloud Shell)
# We'll validate this after Cloud Run deployment
```

**Cost:** ~$50-80/month (Basic tier, 1GB)

**Troubleshooting:**
- **"Quota exceeded":** Request Memorystore quota increase
- **Instance stuck in CREATING:** Normal, wait 5-10 minutes
- **Connection issues:** Ensure Redis instance is in same VPC as apex-network

---

### 2.3 Deploy Neo4j (Compute Engine)

**Create VM for Neo4j:**

```bash
# Create Compute Engine instance for Neo4j
gcloud compute instances create apex-neo4j \
  --zone=$ZONE \
  --machine-type=e2-medium \
  --network-interface=network=apex-network,subnet=default \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --metadata=startup-script='#!/bin/bash
# Install Java
apt-get update
apt-get install -y openjdk-11-jdk wget

# Install Neo4j
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add -
echo "deb https://debian.neo4j.com stable latest" > /etc/apt/sources.list.d/neo4j.list
apt-get update
apt-get install -y neo4j=1:5.15.0

# Configure Neo4j
sed -i "s/#server.bolt.listen_address=:7687/server.bolt.listen_address=0.0.0.0:7687/" /etc/neo4j/neo4j.conf
sed -i "s/#server.http.listen_address=:7474/server.http.listen_address=0.0.0.0:7474/" /etc/neo4j/neo4j.conf
sed -i "s/#server.default_listen_address=0.0.0.0/server.default_listen_address=0.0.0.0/" /etc/neo4j/neo4j.conf

# Set initial password
export NEO4J_PASSWORD=$(gcloud secrets versions access latest --secret=neo4j-password)
neo4j-admin set-initial-password $NEO4J_PASSWORD

# Start Neo4j
systemctl enable neo4j
systemctl start neo4j
'

# Wait for VM to start
sleep 60

# Get Neo4j internal IP
export NEO4J_INTERNAL_IP=$(gcloud compute instances describe apex-neo4j \
  --zone=$ZONE --format="value(networkInterfaces[0].networkIP)")

echo "Neo4j Internal IP: $NEO4J_INTERNAL_IP"
echo "Neo4j Bolt URL: bolt://$NEO4J_INTERNAL_IP:7687"
```

**Validation:**
```bash
# SSH into VM
gcloud compute ssh apex-neo4j --zone=$ZONE

# Check Neo4j status
sudo systemctl status neo4j
# Expected: active (running)

# Check Neo4j logs
sudo journalctl -u neo4j -n 50
# Expected: "Started" message, listening on port 7687

# Exit VM
exit
```

**Cost:** ~$70-90/month (e2-medium: 2 vCPU, 4GB RAM)

**Troubleshooting:**
- **Neo4j not starting:** Check logs with `sudo journalctl -u neo4j`
- **Password not set:** Manually set with `neo4j-admin set-initial-password`
- **Connection refused:** Ensure firewall rules allow internal VPC traffic

---

### 2.4 Deploy Qdrant (Cloud Run)

**Build and deploy Qdrant as container:**

```bash
# Create directory for Qdrant deployment
mkdir -p /tmp/qdrant-deploy
cd /tmp/qdrant-deploy

# Create Dockerfile for Qdrant
cat > Dockerfile <<'EOF'
FROM qdrant/qdrant:v1.7.4

# Expose Qdrant ports
EXPOSE 6333 6334

# Default configuration (override via env vars)
ENV QDRANT__SERVICE__HTTP_PORT=6333
ENV QDRANT__SERVICE__GRPC_PORT=6334
EOF

# Build and push to Artifact Registry
gcloud artifacts repositories create apex-containers \
  --repository-format=docker \
  --location=$REGION

# Build image
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/qdrant:latest

# Deploy to Cloud Run
gcloud run deploy qdrant \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/qdrant:latest \
  --region=$REGION \
  --platform=managed \
  --memory=2Gi \
  --cpu=1 \
  --port=6333 \
  --allow-unauthenticated \
  --vpc-connector=apex-connector \
  --max-instances=3 \
  --min-instances=1

# Get Qdrant URL
export QDRANT_URL=$(gcloud run services describe qdrant \
  --region=$REGION --format="value(status.url)")

echo "Qdrant URL: $QDRANT_URL"
```

**Validation:**
```bash
# Test Qdrant health endpoint
curl $QDRANT_URL/healthz
# Expected: "healthz check passed"

# Create test collection
curl -X PUT "${QDRANT_URL}/collections/test" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    }
  }'
# Expected: {"result": true, "status": "ok"}

# Delete test collection
curl -X DELETE "${QDRANT_URL}/collections/test"
```

**Cost:** ~$40-60/month (Cloud Run: 1 vCPU, 2GB RAM, 1 min instance)

**Troubleshooting:**
- **Cloud Run deployment failed:** Check build logs with `gcloud builds log [BUILD_ID]`
- **Out of memory errors:** Increase memory to 4Gi if needed
- **Connection timeout:** Ensure VPC connector is attached

---

### Phase 2 Summary

**Completed:**
- ✅ Cloud SQL (PostgreSQL + pgvector) deployed
- ✅ Memorystore Redis deployed
- ✅ Neo4j on Compute Engine deployed
- ✅ Qdrant on Cloud Run deployed

**Connection Details:**
```bash
# Save these for application configuration
PostgreSQL: $SQL_CONNECTION_NAME (unix socket via Cloud SQL Proxy)
Redis: redis://$REDIS_HOST:$REDIS_PORT
Neo4j: bolt://$NEO4J_INTERNAL_IP:7687
Qdrant: $QDRANT_URL
```

**Time Spent:** ~3-4 hours

**Cost Impact:** ~$420-570/month

**Next Phase:** [Phase 3: Temporal Setup](#phase-3-temporal-setup)

---

## Phase 3: Temporal Setup

**Goal:** Configure Temporal Cloud connection, install certificates, test worker connectivity.

**Time:** 1-2 hours

**Cost Impact:** ~$100-150/month (Temporal Cloud Essentials tier)

---

### 3.1 Configure Temporal Cloud Namespace

**From Temporal Cloud Console (https://cloud.temporal.io/):**

1. **Create Namespace:**
   - Name: `apex-memory-prod`
   - Region: `aws-us-east-1` or `aws-us-west-2` (closest to your GCP region)
   - Retention: 7 days (free tier) or 30 days (paid)

2. **Download Certificates:**
   - Navigate to Namespace → Settings → Certificates
   - Download `ca.pem`, `client.pem`, `client.key`
   - Save securely

3. **Get Connection Details:**
   - Namespace URL: `apex-memory-prod.[ACCOUNT_ID].tmprl.cloud:7233`
   - Save this URL

---

### 3.2 Upload Temporal Certificates to Secret Manager

**Store certificates securely:**

```bash
# Navigate to where you downloaded certificates
cd ~/Downloads/temporal-certs  # Adjust path

# Upload certificates to Secret Manager
gcloud secrets create temporal-ca-cert --data-file=ca.pem
gcloud secrets create temporal-client-cert --data-file=client.pem
gcloud secrets create temporal-client-key --data-file=client.key

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding temporal-ca-cert \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding temporal-client-cert \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding temporal-client-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Validation:**
```bash
gcloud secrets list | grep temporal
# Expected: temporal-ca-cert, temporal-client-cert, temporal-client-key
```

---

### 3.3 Test Temporal Connection (Local)

**Before deploying to Cloud Run, test Temporal connection locally:**

```bash
# Return to your project directory
cd /Users/richardglaubitz/Projects/apex-memory-system

# Create temporary test script
cat > test_temporal_connection.py <<'EOF'
import asyncio
from temporalio.client import Client, TLSConfig

async def main():
    # Load certificates (adjust paths to your downloaded certs)
    with open("ca.pem", "rb") as f:
        ca_cert = f.read()
    with open("client.pem", "rb") as f:
        client_cert = f.read()
    with open("client.key", "rb") as f:
        client_key = f.read()

    # Configure TLS
    tls_config = TLSConfig(
        server_root_ca_cert=ca_cert,
        client_cert=client_cert,
        client_private_key=client_key,
    )

    # Connect to Temporal Cloud
    client = await Client.connect(
        "apex-memory-prod.[ACCOUNT_ID].tmprl.cloud:7233",  # Replace with your URL
        namespace="apex-memory-prod",
        tls=tls_config,
    )

    print("✅ Successfully connected to Temporal Cloud!")
    print(f"Namespace: {client.namespace}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Run test
python test_temporal_connection.py
# Expected: "✅ Successfully connected to Temporal Cloud!"

# Delete test script
rm test_temporal_connection.py
```

**Troubleshooting:**
- **Certificate validation failed:** Ensure using correct ca.pem, client.pem, client.key
- **Connection timeout:** Check Temporal Cloud namespace URL
- **Permission denied:** Verify certificates are not expired

---

### 3.4 Configure Temporal Environment Variables

**Prepare environment variables for Cloud Run:**

```bash
# Save Temporal configuration
export TEMPORAL_HOST="apex-memory-prod.[ACCOUNT_ID].tmprl.cloud:7233"  # Replace
export TEMPORAL_NAMESPACE="apex-memory-prod"

echo "Temporal Host: $TEMPORAL_HOST"
echo "Temporal Namespace: $TEMPORAL_NAMESPACE"
# Save these for Phase 4
```

---

### Phase 3 Summary

**Completed:**
- ✅ Temporal Cloud namespace created
- ✅ Certificates downloaded and uploaded to Secret Manager
- ✅ Temporal connection tested locally
- ✅ Environment variables prepared

**Connection Details:**
```bash
TEMPORAL_HOST: $TEMPORAL_HOST
TEMPORAL_NAMESPACE: $TEMPORAL_NAMESPACE
# Certificates stored in Secret Manager
```

**Time Spent:** ~1-2 hours

**Cost Impact:** ~$100-150/month

**Next Phase:** [Phase 4: Application Deployment](#phase-4-application-deployment)

---

## Phase 4: Application Deployment

**Goal:** Build Docker image, deploy FastAPI application to Cloud Run, configure environment variables.

**Time:** 2-3 hours

**Cost Impact:** ~$50-80/month

---

### 4.1 Prepare Application Code

**Ensure your code is ready:**

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Run all tests one final time
pytest

# Expected: 156/156 tests passing
# If any fail, DO NOT PROCEED - fix locally first
```

---

### 4.2 Create Production Dockerfile

**Create optimized Dockerfile for production:**

```bash
# Check if Dockerfile exists
ls Dockerfile

# If not, create production-optimized Dockerfile:
cat > Dockerfile <<'EOF'
# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/apex_memory ./apex_memory
COPY src/main.py .

# Expose FastAPI port
EXPOSE 8080

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
EOF
```

---

### 4.3 Build and Push Docker Image

**Build using Cloud Build:**

```bash
# Submit build to Cloud Build (builds in cloud, faster)
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:latest

# This takes 5-10 minutes
# Watch progress in Cloud Console: https://console.cloud.google.com/cloud-build/builds
```

**Validation:**
```bash
# Check image in Artifact Registry
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers
# Expected: apex-memory-api listed with "latest" tag
```

---

### 4.4 Deploy to Cloud Run

**Deploy FastAPI application:**

```bash
# Deploy Cloud Run service with all environment variables
gcloud run deploy apex-memory-api \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:latest \
  --region=$REGION \
  --platform=managed \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=80 \
  --max-instances=10 \
  --min-instances=1 \
  --port=8080 \
  --allow-unauthenticated \
  --vpc-connector=apex-connector \
  --add-cloudsql-instances=$SQL_CONNECTION_NAME \
  --set-env-vars="ENVIRONMENT=production" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest" \
  --set-secrets="POSTGRES_PASSWORD=postgres-password:latest" \
  --set-secrets="NEO4J_PASSWORD=neo4j-password:latest" \
  --set-secrets="TEMPORAL_CLIENT_CERT=temporal-client-cert:latest" \
  --set-secrets="TEMPORAL_CLIENT_KEY=temporal-client-key:latest" \
  --set-secrets="TEMPORAL_CA_CERT=temporal-ca-cert:latest" \
  --update-env-vars="DATABASE_URL=postgresql://apex:postgres@/apex_memory?host=/cloudsql/$SQL_CONNECTION_NAME" \
  --update-env-vars="REDIS_URL=redis://$REDIS_HOST:$REDIS_PORT" \
  --update-env-vars="NEO4J_URI=bolt://$NEO4J_INTERNAL_IP:7687" \
  --update-env-vars="NEO4J_USER=neo4j" \
  --update-env-vars="QDRANT_URL=$QDRANT_URL" \
  --update-env-vars="TEMPORAL_HOST=$TEMPORAL_HOST" \
  --update-env-vars="TEMPORAL_NAMESPACE=$TEMPORAL_NAMESPACE"

# Get service URL
export API_URL=$(gcloud run services describe apex-memory-api \
  --region=$REGION --format="value(status.url)")

echo "API URL: $API_URL"
```

**Validation:**
```bash
# Test health endpoint
curl $API_URL/health
# Expected: {"status": "healthy"}

# Test API docs
curl $API_URL/docs
# Expected: HTML response (FastAPI Swagger UI)

# View in browser
open $API_URL/docs  # macOS
# or navigate to $API_URL/docs in browser
```

---

### 4.5 Deploy Temporal Worker (Separate Cloud Run Service)

**Deploy dedicated worker for Temporal workflows:**

```bash
# Create worker Dockerfile
cat > Dockerfile.worker <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/apex_memory ./apex_memory

# Run Temporal worker
CMD ["python", "-m", "apex_memory.temporal.workers.dev_worker"]
EOF

# Build worker image
gcloud builds submit -f Dockerfile.worker \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-worker:latest

# Deploy worker as Cloud Run service
gcloud run deploy apex-memory-worker \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-worker:latest \
  --region=$REGION \
  --platform=managed \
  --memory=1Gi \
  --cpu=1 \
  --no-cpu-throttling \
  --max-instances=5 \
  --min-instances=2 \
  --no-allow-unauthenticated \
  --vpc-connector=apex-connector \
  --add-cloudsql-instances=$SQL_CONNECTION_NAME \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest" \
  --set-secrets="POSTGRES_PASSWORD=postgres-password:latest" \
  --set-secrets="NEO4J_PASSWORD=neo4j-password:latest" \
  --set-secrets="TEMPORAL_CLIENT_CERT=temporal-client-cert:latest" \
  --set-secrets="TEMPORAL_CLIENT_KEY=temporal-client-key:latest" \
  --set-secrets="TEMPORAL_CA_CERT=temporal-ca-cert:latest" \
  --update-env-vars="DATABASE_URL=postgresql://apex:postgres@/apex_memory?host=/cloudsql/$SQL_CONNECTION_NAME" \
  --update-env-vars="REDIS_URL=redis://$REDIS_HOST:$REDIS_PORT" \
  --update-env-vars="NEO4J_URI=bolt://$NEO4J_INTERNAL_IP:7687" \
  --update-env-vars="NEO4J_USER=neo4j" \
  --update-env-vars="QDRANT_URL=$QDRANT_URL" \
  --update-env-vars="TEMPORAL_HOST=$TEMPORAL_HOST" \
  --update-env-vars="TEMPORAL_NAMESPACE=$TEMPORAL_NAMESPACE"
```

**Validation:**
```bash
# Check worker logs
gcloud run services logs read apex-memory-worker --region=$REGION --limit=50
# Expected: "Worker started" messages, no errors

# Check Temporal Cloud UI
# Navigate to https://cloud.temporal.io/
# Workers tab should show "apex-memory-worker" as connected
```

---

### Phase 4 Summary

**Completed:**
- ✅ Production Dockerfile created
- ✅ Docker image built and pushed
- ✅ FastAPI application deployed to Cloud Run
- ✅ Temporal worker deployed
- ✅ All environment variables configured
- ✅ Health endpoints validated

**Service URLs:**
```bash
API: $API_URL
API Docs: $API_URL/docs
Worker: (internal, no public URL)
```

**Time Spent:** ~2-3 hours

**Cost Impact:** ~$50-80/month

**Next Phase:** [Phase 5: Monitoring Setup](#phase-5-monitoring-setup)

---

## Phase 5: Monitoring Setup

**Goal:** Configure Cloud Monitoring, set up alerts, create dashboards.

**Time:** 1-2 hours

**Cost Impact:** ~$0-20/month (within free tier for most use cases)

---

### 5.1 Enable Cloud Monitoring

**Cloud Monitoring is automatically enabled with your GCP project. Verify:**

```bash
# Check monitoring is enabled
gcloud services list --enabled | grep monitoring
# Expected: monitoring.googleapis.com listed
```

---

### 5.2 Create Alert Policies

**Set up critical alerts:**

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \  # Get from console
  --display-name="High Error Rate - Apex Memory API" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s \
  --condition-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="apex-memory-api" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"'
```

**Alternative: Create alerts via Console (Recommended for first time):**

1. Navigate to: https://console.cloud.google.com/monitoring/alerting
2. Click "Create Policy"
3. Create these alerts:

**Alert 1: High Error Rate**
- Condition: Cloud Run request count (5xx) > 5% for 5 minutes
- Notification: Email

**Alert 2: High Latency**
- Condition: Cloud Run request latency P99 > 5s for 5 minutes
- Notification: Email

**Alert 3: Cloud SQL CPU**
- Condition: Cloud SQL CPU > 80% for 10 minutes
- Notification: Email

**Alert 4: Cloud Run Memory**
- Condition: Cloud Run memory > 90% for 5 minutes
- Notification: Email

---

### 5.3 Create Monitoring Dashboard

**Create custom dashboard for Apex Memory System:**

1. Navigate to: https://console.cloud.google.com/monitoring/dashboards
2. Click "Create Dashboard"
3. Name: "Apex Memory Production"
4. Add charts:

**Chart 1: API Request Rate**
- Resource: Cloud Run Revision
- Metric: Request count
- Filter: service_name = apex-memory-api
- Group by: response_code_class

**Chart 2: API Latency (P50, P95, P99)**
- Resource: Cloud Run Revision
- Metric: Request latencies
- Aggregation: 50th, 95th, 99th percentile

**Chart 3: Database Connections**
- Resource: Cloud SQL Database
- Metric: Active connections

**Chart 4: Redis Hit Rate**
- Resource: Redis Instance
- Metric: Cache hit ratio

**Chart 5: Temporal Workflow Metrics**
- (Configured separately in Temporal Cloud UI)

**Chart 6: Error Rate**
- Resource: Cloud Run Revision
- Metric: Request count
- Filter: response_code_class = 5xx

---

### 5.4 Configure Log Aggregation

**Set up structured logging:**

```bash
# Create log-based metric for application errors
gcloud logging metrics create apex_application_errors \
  --description="Count of application errors" \
  --log-filter='resource.type="cloud_run_revision"
resource.labels.service_name="apex-memory-api"
severity>=ERROR'

# Create log sink for long-term storage (optional)
gcloud logging sinks create apex-logs-archive \
  storage.googleapis.com/apex-logs-archive-bucket \
  --log-filter='resource.type="cloud_run_revision"
resource.labels.service_name="apex-memory-api"'
```

---

### Phase 5 Summary

**Completed:**
- ✅ Cloud Monitoring enabled
- ✅ Alert policies created (error rate, latency, CPU, memory)
- ✅ Monitoring dashboard created
- ✅ Log aggregation configured

**Monitoring URLs:**
- Dashboards: https://console.cloud.google.com/monitoring/dashboards
- Alerts: https://console.cloud.google.com/monitoring/alerting
- Logs: https://console.cloud.google.com/logs

**Time Spent:** ~1-2 hours

**Cost Impact:** ~$0-20/month

**Next Phase:** [Phase 6: CI/CD Pipeline](#phase-6-cicd-pipeline)

---

## Phase 6: CI/CD Pipeline

**Goal:** Set up automated testing and deployment with Cloud Build.

**Time:** 2-3 hours

**Cost Impact:** $0-10/month (within free tier: 120 build-minutes/day)

---

### 6.1 Connect Cloud Build to GitHub

**Connect your GitHub repository:**

1. Navigate to: https://console.cloud.google.com/cloud-build/triggers
2. Click "Connect Repository"
3. Source: GitHub
4. Authenticate with GitHub
5. Select repository: `apex-memory-system`
6. Click "Connect"

---

### 6.2 Create Cloud Build Configuration

**Create `cloudbuild.yaml` in your repository:**

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

cat > cloudbuild.yaml <<'EOF'
steps:
  # Step 1: Run tests
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        pytest tests/unit/ -v
        pytest tests/integration/ -v --tb=short

  # Step 2: Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:${SHORT_SHA}'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:latest'
      - '.'

  # Step 3: Push Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api'

  # Step 4: Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'apex-memory-api'
      - '--image=${_REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:${SHORT_SHA}'
      - '--region=${_REGION}'
      - '--platform=managed'

substitutions:
  _REGION: 'us-central1'

options:
  machineType: 'N1_HIGHCPU_8'
  timeout: '1800s'

images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:${SHORT_SHA}'
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:latest'
EOF

# Commit and push
git add cloudbuild.yaml
git commit -m "feat: Add Cloud Build CI/CD configuration"
git push origin main
```

---

### 6.3 Create Build Trigger

**Set up automatic deployment on push to main:**

```bash
gcloud builds triggers create github \
  --repo-name=apex-memory-system \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --description="Deploy on push to main"
```

**Alternative: Create via Console (Recommended):**

1. Navigate to: https://console.cloud.google.com/cloud-build/triggers
2. Click "Create Trigger"
3. Name: "Deploy on push to main"
4. Event: Push to branch
5. Branch: `^main$`
6. Build configuration: Cloud Build configuration file
7. Location: `cloudbuild.yaml`
8. Click "Create"

---

### 6.4 Test CI/CD Pipeline

**Trigger a build manually:**

1. Make a small change:
```bash
echo "# CI/CD Test" >> README.md
git add README.md
git commit -m "test: Trigger CI/CD pipeline"
git push origin main
```

2. Watch build:
```bash
# View build logs
gcloud builds list --limit=5

# Get build ID from output, then:
gcloud builds log [BUILD_ID] --stream
```

3. Verify deployment:
```bash
# After build completes, test API
curl $API_URL/health
# Expected: {"status": "healthy"}
```

**Validation:**
- Build completes successfully
- All tests pass
- Docker image built and pushed
- Cloud Run service updated
- API responds to requests

---

### Phase 6 Summary

**Completed:**
- ✅ Cloud Build connected to GitHub
- ✅ `cloudbuild.yaml` configuration created
- ✅ Build trigger configured
- ✅ CI/CD pipeline tested

**Deployment Flow:**
1. Push to `main` branch
2. Cloud Build triggers
3. Tests run (unit + integration)
4. Docker image built
5. Image pushed to Artifact Registry
6. Cloud Run service deployed
7. Smoke tests (manual or automated)

**Time Spent:** ~2-3 hours

**Cost Impact:** $0-10/month

**Next Phase:** [Phase 7: Production Validation](#phase-7-production-validation)

---

## Phase 7: Production Validation

**Goal:** Run comprehensive tests, validate performance, ensure system health.

**Time:** 2-4 hours

**Cost Impact:** $0 (testing only)

---

### 7.1 Smoke Tests

**Run critical path validation:**

```bash
# Test 1: Health check
curl $API_URL/health
# Expected: {"status": "healthy"}

# Test 2: Database connectivity
curl -X POST $API_URL/admin/validate-databases
# Expected: All databases report "connected"

# Test 3: Temporal connectivity
curl $API_URL/admin/temporal/status
# Expected: Worker status "active"

# Test 4: Document ingestion (end-to-end)
curl -X POST $API_URL/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test document for validation",
    "source": "production-smoke-test"
  }'
# Expected: 201 Created, workflow ID returned
```

---

### 7.2 Load Testing (Optional but Recommended)

**Run load tests against production:**

```bash
# Install locust (if not already)
pip install locust

# Create locustfile.py
cat > locustfile.py <<'EOF'
from locust import HttpUser, task, between

class ApexMemoryUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def ingest_document(self):
        self.client.post("/api/ingest", json={
            "content": "Load test document",
            "source": "load-test"
        })
EOF

# Run load test (10 users, 1 minute)
locust -f locustfile.py --host=$API_URL --users=10 --spawn-rate=1 --run-time=1m --headless
```

**Validation:**
- P95 latency < 2s
- Error rate < 1%
- No Cloud Run scaling issues

---

### 7.3 Performance Benchmarks

**Validate against SLA targets:**

| Metric | Target | Command | Expected |
|--------|--------|---------|----------|
| API Latency (P95) | <1s | `curl -w "@%{time_total}\n" $API_URL/health` | <1.0s |
| Ingestion Throughput | >10 docs/sec | Load test | >10/sec |
| Cache Hit Rate | >70% | Check Redis metrics | >70% |
| Database Query Time | <500ms | Check Cloud SQL metrics | <500ms |

---

### 7.4 Final Validation Checklist

**Before go-live:**

- [ ] All 156 tests passing in production environment
- [ ] Smoke tests successful (health, databases, Temporal)
- [ ] Load testing completed (10+ docs/sec)
- [ ] Performance benchmarks met
- [ ] Monitoring dashboards showing data
- [ ] Alerts configured and tested
- [ ] CI/CD pipeline working (push to main triggers deployment)
- [ ] Rollback procedure tested
- [ ] Documentation complete

---

### Phase 7 Summary

**Completed:**
- ✅ Smoke tests passed
- ✅ Load testing completed
- ✅ Performance benchmarks validated
- ✅ Final validation checklist complete

**Time Spent:** ~2-4 hours

**Next Phase:** [Phase 8: Production Release](#phase-8-production-release)

---

## Phase 8: Production Release

**Goal:** Final security review, go-live, post-deployment monitoring.

**Time:** 1-2 hours

**Cost Impact:** N/A (already accounted for)

---

### 8.1 Final Security Review

**Complete security checklist:**

- [ ] No secrets in code repository
- [ ] All credentials in Secret Manager
- [ ] IAM permissions follow least privilege
- [ ] VPC networking properly configured
- [ ] Cloud Run services have appropriate access controls
- [ ] Budget alerts active
- [ ] Backup procedures documented
- [ ] Incident response plan documented

---

### 8.2 Go-Live

**Make system publicly available:**

1. **Update DNS (if using custom domain):**
   - Point A record to Cloud Run IP
   - Update SSL certificate (Cloud Run handles automatically)

2. **Remove maintenance mode (if set):**
   ```bash
   # If you set a maintenance page, remove it now
   gcloud run services update apex-memory-api \
     --region=$REGION \
     --remove-env-vars=MAINTENANCE_MODE
   ```

3. **Announce go-live:**
   - Update documentation
   - Notify stakeholders
   - Monitor closely for first 24 hours

---

### 8.3 Post-Deployment Monitoring (24 Hours)

**Monitor these metrics closely for first day:**

1. **Error Rate:**
   - Check: https://console.cloud.google.com/monitoring
   - Target: <0.1%

2. **Latency:**
   - P50: <500ms
   - P95: <1s
   - P99: <2s

3. **Resource Usage:**
   - Cloud Run CPU: <70%
   - Cloud SQL connections: <50% of max
   - Redis memory: <80%

4. **Cost:**
   - Check: https://console.cloud.google.com/billing
   - Expected: ~$25/day ($750/month)

---

### 8.4 Create Operational Runbook

**Document common operations:**

**Runbook saved to:** `research/deployment/OPERATIONAL-RUNBOOK.md`

**Contents:**
1. How to scale Cloud Run instances
2. How to rollback deployment
3. How to access database for debugging
4. How to view logs
5. How to respond to alerts
6. Emergency contact procedures

---

### Phase 8 Summary

**Completed:**
- ✅ Final security review completed
- ✅ System live and publicly available
- ✅ Post-deployment monitoring active
- ✅ Operational runbook created

**Production Status:** 🚀 LIVE

**Time Spent:** ~1-2 hours

**Total Deployment Time:** ~20-30 hours

---

## Troubleshooting

### Common Issues and Solutions

#### Cloud Build Failures

**Issue:** Build fails with "timeout exceeded"

**Solution:**
```bash
# Increase timeout in cloudbuild.yaml
options:
  timeout: '3600s'  # 1 hour
```

---

**Issue:** Tests fail in Cloud Build but pass locally

**Solution:**
```bash
# Check test logs
gcloud builds log [BUILD_ID]

# Common causes:
# 1. Missing environment variables
# 2. Database not accessible (need VPC connector)
# 3. Different Python version
```

---

#### Cloud Run Deployment Failures

**Issue:** "Container failed to start"

**Solution:**
```bash
# Check logs
gcloud run services logs read apex-memory-api --region=$REGION --limit=100

# Common causes:
# 1. Port mismatch (must match CMD port and --port flag)
# 2. Missing environment variables
# 3. Database connection issues
```

---

**Issue:** "Service Unavailable (503)"

**Solution:**
```bash
# Check service status
gcloud run services describe apex-memory-api --region=$REGION

# Check if instances are running
gcloud run services describe apex-memory-api --region=$REGION \
  --format="value(status.conditions)"

# Common causes:
# 1. Application crash on startup
# 2. Health check failures
# 3. Insufficient resources (increase memory/CPU)
```

---

#### Database Connection Issues

**Issue:** "Could not connect to Cloud SQL"

**Solution:**
```bash
# Verify Cloud SQL Proxy configuration
gcloud run services describe apex-memory-api --region=$REGION \
  --format="value(metadata.annotations.'run.googleapis.com/cloudsql-instances')"

# Ensure matches: $SQL_CONNECTION_NAME

# Check VPC connector
gcloud compute networks vpc-access connectors describe apex-connector \
  --region=$REGION
# Should be: State: READY
```

---

**Issue:** "Redis connection timeout"

**Solution:**
```bash
# Verify VPC connector attached
gcloud run services describe apex-memory-api --region=$REGION \
  --format="value(metadata.annotations.'run.googleapis.com/vpc-access-connector')"

# Test Redis from Cloud Shell (in same VPC)
gcloud redis instances describe apex-redis --region=$REGION
# Note HOST and PORT

# Connect from Cloud Shell
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping
# Expected: PONG
```

---

#### Temporal Connection Issues

**Issue:** "Worker not connecting to Temporal Cloud"

**Solution:**
```bash
# Check Temporal certificates in Secret Manager
gcloud secrets versions access latest --secret=temporal-client-cert
gcloud secrets versions access latest --secret=temporal-client-key

# Verify Temporal environment variables
gcloud run services describe apex-memory-worker --region=$REGION \
  --format="value(spec.template.spec.containers[0].env)"

# Check worker logs
gcloud run services logs read apex-memory-worker --region=$REGION --limit=50
```

---

#### Cost Overruns

**Issue:** Costs higher than expected

**Solution:**
```bash
# Check cost breakdown
gcloud billing accounts describe $BILLING_ACCOUNT_ID

# Common culprits:
# 1. Cloud Run min-instances too high (reduce to 0 or 1)
# 2. Cloud SQL oversized (downgrade from db-n1-standard-2 to db-n1-standard-1)
# 3. Excessive egress (check data transfer)
# 4. Temporal Cloud usage (check workflow count)

# View detailed cost analysis
# Navigate to: https://console.cloud.google.com/billing/reports
```

---

## Next Steps

**After successful deployment:**

1. **Monitor for 7 days:**
   - Check metrics daily
   - Adjust resources as needed
   - Optimize costs

2. **Implement improvements:**
   - Set up automated backups (see OPERATIONAL-RUNBOOK.md)
   - Add more comprehensive monitoring
   - Implement blue-green deployments

3. **Scale as needed:**
   - Increase Cloud Run instances
   - Upgrade database tiers
   - Add read replicas

4. **Learn more:**
   - [UPDATE-WORKFLOW.md](UPDATE-WORKFLOW.md) - How to deploy changes
   - [COST-OPTIMIZATION.md](COST-OPTIMIZATION.md) - Reduce costs
   - [TESTING-STRATEGY.md](TESTING-STRATEGY.md) - Comprehensive testing

---

## Quick Reference

**Essential Commands:**

```bash
# Check all service health
gcloud run services list

# View API logs
gcloud run services logs read apex-memory-api --region=$REGION --limit=50

# Manual deployment
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:v2
gcloud run deploy apex-memory-api \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/apex-containers/apex-memory-api:v2 \
  --region=$REGION

# Rollback
gcloud run services update-traffic apex-memory-api --to-revisions=PREVIOUS_REVISION=100

# Check costs
gcloud billing accounts describe $BILLING_ACCOUNT_ID
```

---

**Congratulations! Your Apex Memory System is now deployed to production! 🎉**

---

**Last Updated:** 2025-01-20
**Version:** 1.0.0
**Author:** Claude Code (Apex Memory System Deployment)
