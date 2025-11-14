# Pulumi GCP Provider: Complete Production Guide

**Source:** Official Pulumi GCP Documentation (pulumi.com/registry/packages/gcp)
**Date:** November 2025
**Tier:** Official Documentation (Tier 1)

---

## Table of Contents

1. [GCP Provider Overview](#gcp-provider-overview)
2. [Installation & Configuration](#installation--configuration)
3. [Authentication Methods](#authentication-methods)
4. [Common GCP Resources](#common-gcp-resources)
5. [Cloud Run Deployment](#cloud-run-deployment)
6. [Cloud SQL Setup](#cloud-sql-setup)
7. [VPC & Networking](#vpc--networking)
8. [Connecting Cloud Run to Cloud SQL](#connecting-cloud-run-to-cloud-sql)
9. [Secrets Management with GCP Secret Manager](#secrets-management-with-gcp-secret-manager)
10. [Region & Zone Configuration](#region--zone-configuration)
11. [Production Patterns](#production-patterns)
12. [Example: Complete Apex Memory System Infrastructure](#example-complete-apex-memory-system-infrastructure)

---

## GCP Provider Overview

The **Pulumi Google Cloud (GCP) provider** enables you to provision and manage Google Cloud Platform resources using Pulumi's infrastructure as code platform.

### Supported Languages

| Language | Package Name | Installation |
|----------|--------------|--------------|
| **Python** | `pulumi-gcp` | `pip install pulumi-gcp` |
| TypeScript/JavaScript | `@pulumi/gcp` | `npm install @pulumi/gcp` |
| Go | `github.com/pulumi/pulumi-gcp/sdk/v7/go/gcp` | `go get github.com/pulumi/pulumi-gcp/sdk/v7` |
| .NET | `Pulumi.Gcp` | `dotnet add package Pulumi.Gcp` |
| Java | `com.pulumi.gcp` | Maven/Gradle |

### Current Version

**Google Cloud v9.4.0** (November 4, 2025)

**GitHub Repository:** https://github.com/pulumi/pulumi-gcp

### Coverage

The GCP provider supports **100+ GCP services**, including:

- **Compute:** Compute Engine, Cloud Run, Cloud Functions, GKE
- **Storage:** Cloud Storage, Filestore, Persistent Disks
- **Database:** Cloud SQL, Firestore, Bigtable, Spanner
- **Networking:** VPC, Cloud Load Balancing, Cloud CDN, VPC Access
- **Security:** IAM, Secret Manager, KMS, Cloud Armor
- **Monitoring:** Cloud Monitoring, Cloud Logging, Cloud Trace
- **AI/ML:** Vertex AI, AutoML, AI Platform

**Source:** https://www.pulumi.com/registry/packages/gcp/

---

## Installation & Configuration

### Step 1: Install Pulumi GCP Provider

```bash
# Python (recommended for Apex Memory System)
pip install pulumi-gcp

# Or add to requirements.txt
echo "pulumi-gcp>=7.0.0,<8.0.0" >> requirements.txt
pip install -r requirements.txt
```

### Step 2: Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Verify installation
gcloud --version

# Initialize gcloud
gcloud init
```

### Step 3: Configure Default Project

```bash
# Option 1: Using Pulumi config (per-stack)
pulumi config set gcp:project apex-memory-prod
pulumi config set gcp:region us-central1
pulumi config set gcp:zone us-central1-a

# Option 2: Using environment variables (global)
export GOOGLE_PROJECT=apex-memory-prod
export GOOGLE_REGION=us-central1
export GOOGLE_ZONE=us-central1-a
```

### Configuration Options

| Option | Environment Variable | Required | Description |
|--------|---------------------|----------|-------------|
| `project` | `GOOGLE_PROJECT` | **Yes** | GCP project ID |
| `region` | `GOOGLE_REGION` | No | Default region |
| `zone` | `GOOGLE_ZONE` | No | Default zone |
| `credentials` | `GOOGLE_CREDENTIALS` | No | Service account JSON key path |
| `access_token` | `GOOGLE_OAUTH_ACCESS_TOKEN` | No | OAuth 2.0 access token |
| `impersonate_service_account` | - | No | Service account email to impersonate |
| `scopes` | - | No | OAuth 2.0 scopes |

**Example Pulumi.yaml:**
```yaml
name: apex-memory-infrastructure
runtime:
  name: python
  options:
    virtualenv: venv
    typechecker: mypy

config:
  gcp:project:
    description: GCP project ID
  gcp:region:
    description: Default GCP region
    default: us-central1
  gcp:zone:
    description: Default GCP zone
    default: us-central1-a
```

**Source:** https://www.pulumi.com/registry/packages/gcp/installation-configuration/

---

## Authentication Methods

Pulumi GCP provider supports **three authentication methods**:

### 1. Google Cloud CLI (Local Development)

**Best for:** Local development, testing, prototyping

```bash
# Authenticate with user account
gcloud auth application-default login

# This creates credentials at:
# ~/.config/gcloud/application_default_credentials.json

# Pulumi automatically detects these credentials
pulumi up  # Works immediately
```

**Pros:**
- ✅ Easy setup for local development
- ✅ No credential management
- ✅ Automatic rotation (linked to user account)

**Cons:**
- ❌ Not suitable for CI/CD
- ❌ User-level permissions (may be too broad)
- ❌ Requires human interaction

### 2. Service Account (Production & CI/CD)

**Best for:** Production deployments, CI/CD pipelines, non-interactive environments

#### Step 2.1: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create pulumi-deployer \
  --display-name="Pulumi Infrastructure Deployer" \
  --project=apex-memory

# Grant necessary roles (example for Apex Memory System)
gcloud projects add-iam-policy-binding apex-memory \
  --member="serviceAccount:pulumi-deployer@apex-memory.iam.gserviceaccount.com" \
  --role="roles/compute.admin"

gcloud projects add-iam-policy-binding apex-memory \
  --member="serviceAccount:pulumi-deployer@apex-memory.iam.gserviceaccount.com" \
  --role="roles/cloudsql.admin"

gcloud projects add-iam-policy-binding apex-memory \
  --member="serviceAccount:pulumi-deployer@apex-memory.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding apex-memory \
  --member="serviceAccount:pulumi-deployer@apex-memory.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding apex-memory \
  --member="serviceAccount:pulumi-deployer@apex-memory.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

#### Step 2.2: Create and Download Key

```bash
# Create JSON key
gcloud iam service-accounts keys create ~/pulumi-deployer-key.json \
  --iam-account=pulumi-deployer@apex-memory.iam.gserviceaccount.com

# Secure the key (critical!)
chmod 600 ~/pulumi-deployer-key.json
```

#### Step 2.3: Configure Pulumi

**Option A: Environment Variable (Recommended)**

```bash
# Set environment variable
export GOOGLE_CREDENTIALS=$(cat ~/pulumi-deployer-key.json)

# Or point to file path
export GOOGLE_APPLICATION_CREDENTIALS=~/pulumi-deployer-key.json

# Run Pulumi
pulumi up
```

**Option B: Pulumi Config (Less secure - stores path in config file)**

```bash
# Store credential file path in Pulumi config
pulumi config set gcp:credentials ~/pulumi-deployer-key.json

# Run Pulumi
pulumi up
```

**⚠️ Security Best Practice:**
- **Never commit service account keys to Git**
- Store keys in secure secret managers (GitHub Secrets, GitLab CI/CD variables)
- Use short-lived credentials via OIDC (see Method 3)

### 3. OpenID Connect (OIDC) - Modern Approach

**Best for:** CI/CD pipelines (GitHub Actions, GitLab CI, CircleCI)

**Benefits:**
- ✅ No long-lived credentials
- ✅ Automatic token rotation
- ✅ Short-lived, scoped access
- ✅ No secrets to manage

#### Step 3.1: Configure Workload Identity Federation

```bash
# Create workload identity pool
gcloud iam workload-identity-pools create pulumi-github \
  --location="global" \
  --display-name="Pulumi GitHub Actions Pool" \
  --project=apex-memory

# Create workload identity provider (GitHub example)
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="pulumi-github" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == 'apex-org/apex-memory'" \
  --project=apex-memory

# Grant service account access to workload identity
gcloud iam service-accounts add-iam-policy-binding \
  pulumi-deployer@apex-memory.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/123456789/locations/global/workloadIdentityPools/pulumi-github/attribute.repository/apex-org/apex-memory"
```

#### Step 3.2: Use in GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Infrastructure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # Required for OIDC

    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/pulumi-github/providers/github-provider'
          service_account: 'pulumi-deployer@apex-memory.iam.gserviceaccount.com'

      - name: Deploy with Pulumi
        uses: pulumi/actions@v4
        with:
          command: up
          stack-name: production
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
```

**Source:** https://www.pulumi.com/docs/deployments/deployments/oidc/gcp/

---

## Common GCP Resources

### Compute Resources

#### Cloud Run Service

```python
import pulumi_gcp as gcp

# Cloud Run service
service = gcp.cloudrun.Service("api",
    location="us-central1",
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            containers=[gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                image="gcr.io/apex-memory/api:latest",
                ports=[gcp.cloudrun.ServiceTemplateSpecContainerPortArgs(
                    container_port=8000
                )],
                resources=gcp.cloudrun.ServiceTemplateSpecContainerResourcesArgs(
                    limits={
                        "cpu": "2",
                        "memory": "2Gi"
                    }
                ),
                envs=[
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DATABASE_URL",
                        value=db_url
                    )
                ]
            )]
        )
    )
)

# Make service publicly accessible
iam_member = gcp.cloudrun.IamMember("api-invoker",
    service=service.name,
    location=service.location,
    role="roles/run.invoker",
    member="allUsers"
)

pulumi.export("api_url", service.statuses[0].url)
```

#### Compute Engine VM

```python
# Compute Engine instance
instance = gcp.compute.Instance("worker",
    machine_type="e2-medium",
    zone="us-central1-a",
    boot_disk=gcp.compute.InstanceBootDiskArgs(
        initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
            image="debian-cloud/debian-11",
            size=50  # GB
        )
    ),
    network_interfaces=[gcp.compute.InstanceNetworkInterfaceArgs(
        network=vpc.id,
        subnetwork=subnet.id,
        access_configs=[gcp.compute.InstanceNetworkInterfaceAccessConfigArgs()]  # External IP
    )],
    metadata_startup_script="#!/bin/bash\napt-get update\napt-get install -y docker.io",
    service_account=gcp.compute.InstanceServiceAccountArgs(
        email=service_account.email,
        scopes=["cloud-platform"]
    )
)
```

### Storage Resources

#### Cloud Storage Bucket

```python
# Storage bucket
bucket = gcp.storage.Bucket("data",
    location="US",
    storage_class="STANDARD",
    uniform_bucket_level_access=True,
    versioning=gcp.storage.BucketVersioningArgs(
        enabled=True
    ),
    lifecycle_rules=[
        gcp.storage.BucketLifecycleRuleArgs(
            action=gcp.storage.BucketLifecycleRuleActionArgs(
                type="Delete"
            ),
            condition=gcp.storage.BucketLifecycleRuleConditionArgs(
                age=90,
                with_state="ARCHIVED"
            )
        )
    ],
    cors=[gcp.storage.BucketCorArgs(
        max_age_seconds=3600,
        methods=["GET", "POST"],
        origins=["https://apex-memory.com"],
        response_headers=["Content-Type"]
    )]
)

# Bucket IAM (make public read)
bucket_iam = gcp.storage.BucketIAMBinding("public-read",
    bucket=bucket.name,
    role="roles/storage.objectViewer",
    members=["allUsers"]
)
```

### Database Resources

#### Cloud SQL (PostgreSQL)

```python
# Cloud SQL instance
db_instance = gcp.sql.DatabaseInstance("postgres",
    database_version="POSTGRES_15",
    region="us-central1",
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-g1-small",  # or db-custom-2-7680
        disk_size=50,  # GB
        disk_type="PD_SSD",
        availability_type="REGIONAL",  # High availability
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            enabled=True,
            start_time="03:00",
            point_in_time_recovery_enabled=True,
            transaction_log_retention_days=7,
            backup_retention_settings=gcp.sql.DatabaseInstanceSettingsBackupConfigurationBackupRetentionSettingsArgs(
                retained_backups=30
            )
        ),
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=False,  # Disable public IP
            private_network=vpc.id,
            require_ssl=True
        ),
        database_flags=[
            gcp.sql.DatabaseInstanceSettingsDatabaseFlagArgs(
                name="max_connections",
                value="100"
            )
        ]
    ),
    deletion_protection=True
)

# Create database
database = gcp.sql.Database("apex",
    instance=db_instance.name,
    charset="UTF8",
    collation="en_US.UTF8"
)

# Create user
db_user = gcp.sql.User("app-user",
    instance=db_instance.name,
    password=db_password,  # From config secret
    type="BUILT_IN"
)
```

### Networking Resources

#### VPC Network

```python
# VPC network
vpc = gcp.compute.Network("vpc",
    auto_create_subnetworks=False,
    routing_mode="REGIONAL"
)

# Subnet
subnet = gcp.compute.Subnetwork("subnet",
    network=vpc.id,
    ip_cidr_range="10.0.0.0/24",
    region="us-central1",
    private_ip_google_access=True  # Access Google APIs via private IP
)

# Firewall rule (allow internal traffic)
firewall_internal = gcp.compute.Firewall("allow-internal",
    network=vpc.id,
    allows=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["0-65535"]
        ),
        gcp.compute.FirewallAllowArgs(
            protocol="udp",
            ports=["0-65535"]
        ),
        gcp.compute.FirewallAllowArgs(
            protocol="icmp"
        )
    ],
    source_ranges=["10.0.0.0/24"]
)

# Firewall rule (allow HTTPS from internet)
firewall_https = gcp.compute.Firewall("allow-https",
    network=vpc.id,
    allows=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["443"]
        )
    ],
    source_ranges=["0.0.0.0/0"],
    target_tags=["https-server"]
)
```

---

## Cloud Run Deployment

### Basic Cloud Run Service

```python
import pulumi
import pulumi_gcp as gcp

config = pulumi.Config()
project = config.require("gcp:project")
region = config.get("gcp:region") or "us-central1"

# Build and push container image first
# gcloud builds submit --tag gcr.io/apex-memory/api:v1.0.0

service = gcp.cloudrun.Service("apex-api",
    location=region,
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            service_account_name=service_account.email,
            containers=[gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                image="gcr.io/apex-memory/api:v1.0.0",
                ports=[gcp.cloudrun.ServiceTemplateSpecContainerPortArgs(
                    container_port=8000,
                    name="http1"
                )],
                resources=gcp.cloudrun.ServiceTemplateSpecContainerResourcesArgs(
                    limits={
                        "cpu": "2000m",  # 2 vCPUs
                        "memory": "2Gi"
                    },
                    requests={
                        "cpu": "1000m",
                        "memory": "512Mi"
                    }
                ),
                envs=[
                    # Environment variables
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="PORT",
                        value="8000"
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="PROJECT_ID",
                        value=project
                    ),
                    # Secret from Secret Manager
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DATABASE_PASSWORD",
                        value_from=gcp.cloudrun.ServiceTemplateSpecContainerEnvValueFromArgs(
                            secret_key_ref=gcp.cloudrun.ServiceTemplateSpecContainerEnvValueFromSecretKeyRefArgs(
                                name=db_secret.secret_id,
                                key="latest"
                            )
                        )
                    )
                ],
                startup_probe=gcp.cloudrun.ServiceTemplateSpecContainerStartupProbeArgs(
                    http_get=gcp.cloudrun.ServiceTemplateSpecContainerStartupProbeHttpGetArgs(
                        path="/health",
                        port=8000
                    ),
                    initial_delay_seconds=10,
                    timeout_seconds=5,
                    period_seconds=10,
                    failure_threshold=3
                ),
                liveness_probe=gcp.cloudrun.ServiceTemplateSpecContainerLivenessProbeArgs(
                    http_get=gcp.cloudrun.ServiceTemplateSpecContainerLivenessProbeHttpGetArgs(
                        path="/health",
                        port=8000
                    ),
                    period_seconds=30
                )
            )],
            container_concurrency=80,  # Max concurrent requests per instance
            timeout_seconds=300
        ),
        metadata=gcp.cloudrun.ServiceTemplateMetadataArgs(
            annotations={
                # Autoscaling
                "autoscaling.knative.dev/minScale": "1",
                "autoscaling.knative.dev/maxScale": "10",
                # CPU throttling (always allocated)
                "run.googleapis.com/cpu-throttling": "false",
                # VPC connector (for private Cloud SQL access)
                "run.googleapis.com/vpc-access-connector": vpc_connector.name,
                "run.googleapis.com/vpc-access-egress": "private-ranges-only"
            }
        )
    ),
    traffics=[gcp.cloudrun.ServiceTrafficArgs(
        percent=100,
        latest_revision=True
    )],
    metadata=gcp.cloudrun.ServiceMetadataArgs(
        annotations={
            "run.googleapis.com/ingress": "all",  # or "internal" or "internal-and-cloud-load-balancing"
            "run.googleapis.com/launch-stage": "BETA"
        }
    )
)

# IAM: Make service publicly accessible
public_access = gcp.cloudrun.IamMember("public-access",
    service=service.name,
    location=service.location,
    role="roles/run.invoker",
    member="allUsers"
)

# Export service URL
pulumi.export("api_url", service.statuses[0].url)
```

### Cloud Run with Custom Domain

```python
# Map custom domain
domain_mapping = gcp.cloudrun.DomainMapping("api-domain",
    location=service.location,
    name="api.apex-memory.com",
    metadata=gcp.cloudrun.DomainMappingMetadataArgs(
        namespace=project
    ),
    spec=gcp.cloudrun.DomainMappingSpecArgs(
        route_name=service.name
    )
)

# Output DNS records to configure
pulumi.export("dns_records", domain_mapping.status.resource_records)
```

---

## Cloud SQL Setup

### Cloud SQL with Private IP

```python
import pulumi
import pulumi_gcp as gcp

# VPC (required for private IP)
vpc = gcp.compute.Network("vpc",
    auto_create_subnetworks=False
)

# Reserve IP range for private services (Cloud SQL)
private_ip_range = gcp.compute.GlobalAddress("private-ip-range",
    purpose="VPC_PEERING",
    address_type="INTERNAL",
    prefix_length=16,
    network=vpc.id
)

# Create private VPC connection
private_vpc_connection = gcp.servicenetworking.Connection("private-vpc",
    network=vpc.id,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=[private_ip_range.name]
)

# Cloud SQL instance with private IP
db_instance = gcp.sql.DatabaseInstance("postgres",
    database_version="POSTGRES_15",
    region="us-central1",
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-custom-2-7680",  # 2 vCPU, 7.5 GB RAM
        disk_size=100,
        disk_type="PD_SSD",
        disk_autoresize=True,
        disk_autoresize_limit=500,
        availability_type="REGIONAL",  # HA with automatic failover
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            enabled=True,
            start_time="03:00",
            point_in_time_recovery_enabled=True,
            transaction_log_retention_days=7,
            backup_retention_settings=gcp.sql.DatabaseInstanceSettingsBackupConfigurationBackupRetentionSettingsArgs(
                retained_backups=30,
                retention_unit="COUNT"
            )
        ),
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=False,  # No public IP
            private_network=vpc.id,
            require_ssl=True,
            ssl_mode="ENCRYPTED_ONLY"
        ),
        maintenance_window=gcp.sql.DatabaseInstanceSettingsMaintenanceWindowArgs(
            day=7,  # Sunday
            hour=4,  # 4 AM
            update_track="stable"
        ),
        insights_config=gcp.sql.DatabaseInstanceSettingsInsightsConfigArgs(
            query_insights_enabled=True,
            query_string_length=1024,
            record_application_tags=True,
            record_client_address=True
        ),
        database_flags=[
            gcp.sql.DatabaseInstanceSettingsDatabaseFlagArgs(
                name="max_connections",
                value="200"
            ),
            gcp.sql.DatabaseInstanceSettingsDatabaseFlagArgs(
                name="shared_buffers",
                value="1966080"  # ~1.5 GB (20% of RAM)
            )
        ]
    ),
    deletion_protection=True,
    opts=pulumi.ResourceOptions(depends_on=[private_vpc_connection])
)

# Create database
database = gcp.sql.Database("apex-memory",
    instance=db_instance.name,
    charset="UTF8",
    collation="en_US.UTF8"
)

# Create user with password from config secret
config = pulumi.Config()
db_password = config.require_secret("dbPassword")

db_user = gcp.sql.User("app-user",
    instance=db_instance.name,
    password=db_password,
    type="BUILT_IN"
)

# Export connection details
pulumi.export("db_connection_name", db_instance.connection_name)
pulumi.export("db_private_ip", db_instance.private_ip_address)
```

---

## VPC & Networking

### Complete VPC Setup

```python
import pulumi
import pulumi_gcp as gcp

# VPC Network
vpc = gcp.compute.Network("apex-vpc",
    auto_create_subnetworks=False,
    routing_mode="REGIONAL",
    description="Apex Memory System VPC"
)

# Subnets
subnet_us_central = gcp.compute.Subnetwork("us-central1-subnet",
    network=vpc.id,
    ip_cidr_range="10.0.0.0/24",
    region="us-central1",
    private_ip_google_access=True,  # Access Google APIs without public IP
    secondary_ip_ranges=[
        gcp.compute.SubnetworkSecondaryIpRangeArgs(
            range_name="pods",
            ip_cidr_range="10.1.0.0/16"
        ),
        gcp.compute.SubnetworkSecondaryIpRangeArgs(
            range_name="services",
            ip_cidr_range="10.2.0.0/16"
        )
    ]
)

# Cloud Router (required for Cloud NAT)
router = gcp.compute.Router("router",
    network=vpc.id,
    region="us-central1",
    bgp=gcp.compute.RouterBgpArgs(
        asn=64514
    )
)

# Cloud NAT (for outbound internet access from private instances)
nat = gcp.compute.RouterNat("nat",
    router=router.name,
    region=router.region,
    nat_ip_allocate_option="AUTO_ONLY",
    source_subnetwork_ip_ranges_to_nat="ALL_SUBNETWORKS_ALL_IP_RANGES",
    log_config=gcp.compute.RouterNatLogConfigArgs(
        enable=True,
        filter="ALL"
    )
)

# Firewall Rules
firewall_allow_internal = gcp.compute.Firewall("allow-internal",
    network=vpc.id,
    description="Allow all internal traffic",
    allows=[
        gcp.compute.FirewallAllowArgs(protocol="tcp", ports=["0-65535"]),
        gcp.compute.FirewallAllowArgs(protocol="udp", ports=["0-65535"]),
        gcp.compute.FirewallAllowArgs(protocol="icmp")
    ],
    source_ranges=["10.0.0.0/8"],
    priority=1000
)

firewall_allow_ssh = gcp.compute.Firewall("allow-ssh",
    network=vpc.id,
    description="Allow SSH from IAP",
    allows=[gcp.compute.FirewallAllowArgs(protocol="tcp", ports=["22"])],
    source_ranges=["35.235.240.0/20"],  # IAP IP range
    priority=1000
)

firewall_allow_health_checks = gcp.compute.Firewall("allow-health-checks",
    network=vpc.id,
    description="Allow health checks from GCP",
    allows=[gcp.compute.FirewallAllowArgs(protocol="tcp")],
    source_ranges=[
        "130.211.0.0/22",   # GCP health check ranges
        "35.191.0.0/16"
    ],
    target_tags=["http-server"],
    priority=1000
)

# VPC Access Connector (for Cloud Run to access VPC resources)
vpc_connector = gcp.vpcaccess.Connector("vpc-connector",
    region="us-central1",
    network=vpc.name,
    ip_cidr_range="10.8.0.0/28",  # /28 provides 16 IPs (minimum for connector)
    min_throughput=200,  # Mbps
    max_throughput=1000  # Mbps
)

# Export VPC details
pulumi.export("vpc_id", vpc.id)
pulumi.export("vpc_name", vpc.name)
pulumi.export("subnet_id", subnet_us_central.id)
pulumi.export("vpc_connector_name", vpc_connector.name)
```

---

## Connecting Cloud Run to Cloud SQL

### Complete Integration Pattern

Cloud Run cannot directly access VPC resources without a **VPC Access Connector**. Here's the complete pattern:

```python
import pulumi
import pulumi_gcp as gcp

config = pulumi.Config()
project = config.require("gcp:project")
region = config.get("gcp:region") or "us-central1"
db_password = config.require_secret("dbPassword")

# 1. VPC Network
vpc = gcp.compute.Network("vpc",
    auto_create_subnetworks=False
)

# 2. Private IP range for Cloud SQL
private_ip_range = gcp.compute.GlobalAddress("cloudsql-ip-range",
    purpose="VPC_PEERING",
    address_type="INTERNAL",
    prefix_length=16,
    network=vpc.id
)

# 3. Private VPC connection
private_vpc = gcp.servicenetworking.Connection("cloudsql-vpc",
    network=vpc.id,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=[private_ip_range.name]
)

# 4. Cloud SQL Instance (PRIVATE IP ONLY)
db_instance = gcp.sql.DatabaseInstance("postgres",
    database_version="POSTGRES_15",
    region=region,
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-g1-small",
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=False,  # ⚠️ CRITICAL: No public IP
            private_network=vpc.id,
            require_ssl=True
        )
    ),
    deletion_protection=False,  # Set to True in production
    opts=pulumi.ResourceOptions(depends_on=[private_vpc])
)

# 5. Database
database = gcp.sql.Database("apex",
    instance=db_instance.name
)

# 6. User
db_user = gcp.sql.User("app",
    instance=db_instance.name,
    password=db_password
)

# 7. VPC Access Connector (REQUIRED for Cloud Run → VPC)
vpc_connector = gcp.vpcaccess.Connector("connector",
    region=region,
    network=vpc.name,
    ip_cidr_range="10.8.0.0/28",  # Must not overlap with other ranges
    min_throughput=200,
    max_throughput=1000
)

# 8. Service Account for Cloud Run
service_account = gcp.serviceaccount.Account("cloudrun-sa",
    account_id="apex-cloudrun",
    display_name="Cloud Run Service Account"
)

# Grant Cloud SQL Client role
sql_client_binding = gcp.projects.IAMMember("sql-client",
    project=project,
    role="roles/cloudsql.client",
    member=service_account.email.apply(lambda email: f"serviceAccount:{email}")
)

# 9. Cloud Run Service
service = gcp.cloudrun.Service("api",
    location=region,
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            service_account_name=service_account.email,
            containers=[gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                image="gcr.io/apex-memory/api:latest",
                ports=[gcp.cloudrun.ServiceTemplateSpecContainerPortArgs(
                    container_port=8000
                )],
                envs=[
                    # Database connection via PRIVATE IP
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_HOST",
                        value=db_instance.private_ip_address
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_PORT",
                        value="5432"
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_NAME",
                        value=database.name
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_USER",
                        value=db_user.name
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_PASSWORD",
                        value=db_password
                    ),
                    # Alternative: Cloud SQL Proxy connection string
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="CLOUD_SQL_CONNECTION_NAME",
                        value=db_instance.connection_name
                    )
                ]
            )]
        ),
        metadata=gcp.cloudrun.ServiceTemplateMetadataArgs(
            annotations={
                # ⚠️ CRITICAL: VPC connector annotation
                "run.googleapis.com/vpc-access-connector": vpc_connector.name,
                # Route only private IPs through VPC (Cloud SQL uses private IP)
                "run.googleapis.com/vpc-access-egress": "private-ranges-only"
            }
        )
    )
)

# 10. Make service publicly accessible
public_access = gcp.cloudrun.IamMember("public",
    service=service.name,
    location=service.location,
    role="roles/run.invoker",
    member="allUsers"
)

# Exports
pulumi.export("api_url", service.statuses[0].url)
pulumi.export("db_private_ip", db_instance.private_ip_address)
pulumi.export("db_connection_name", db_instance.connection_name)
```

### Key Integration Points

1. **VPC Access Connector** enables Cloud Run to reach VPC resources
2. **Private IP only** for Cloud SQL (no public IP)
3. **Service Account** with `cloudsql.client` role
4. **VPC egress** set to `private-ranges-only` (faster, cheaper than routing all traffic through VPC)

**Source:** https://www.pulumi.com/registry/packages/gcp/how-to-guides/gcp-py-cloudrun-cloudsql/

---

## Secrets Management with GCP Secret Manager

### Creating and Using Secrets

```python
import pulumi
import pulumi_gcp as gcp

# 1. Create secret
db_password_secret = gcp.secretmanager.Secret("db-password",
    secret_id="apex-db-password",
    replication=gcp.secretmanager.SecretReplicationArgs(
        automatic=gcp.secretmanager.SecretReplicationAutomaticArgs()
        # Or use user-managed replication for specific regions:
        # user_managed=gcp.secretmanager.SecretReplicationUserManagedArgs(
        #     replicas=[
        #         gcp.secretmanager.SecretReplicationUserManagedReplicaArgs(
        #             location="us-central1"
        #         ),
        #         gcp.secretmanager.SecretReplicationUserManagedReplicaArgs(
        #             location="us-east1"
        #         )
        #     ]
        # )
    )
)

# 2. Create secret version (store actual value)
config = pulumi.Config()
db_password = config.require_secret("dbPassword")  # From Pulumi config

db_password_version = gcp.secretmanager.SecretVersion("db-password-v1",
    secret=db_password_secret.id,
    secret_data=db_password
)

# 3. Grant Cloud Run service account access to secret
secret_accessor = gcp.secretmanager.SecretIamMember("secret-access",
    secret_id=db_password_secret.id,
    role="roles/secretmanager.secretAccessor",
    member=service_account.email.apply(lambda email: f"serviceAccount:{email}")
)

# 4. Use in Cloud Run (environment variable from Secret Manager)
service = gcp.cloudrun.Service("api",
    location="us-central1",
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            service_account_name=service_account.email,
            containers=[gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                image="gcr.io/apex-memory/api:latest",
                envs=[
                    # Secret from Secret Manager (mounted as environment variable)
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DATABASE_PASSWORD",
                        value_from=gcp.cloudrun.ServiceTemplateSpecContainerEnvValueFromArgs(
                            secret_key_ref=gcp.cloudrun.ServiceTemplateSpecContainerEnvValueFromSecretKeyRefArgs(
                                name=db_password_secret.secret_id,
                                key="latest"  # Use latest version
                            )
                        )
                    )
                ]
            )]
        )
    )
)

# Export secret name (not value)
pulumi.export("db_secret_name", db_password_secret.secret_id)
```

### Best Practice Pattern

```python
# Store all secrets in GCP Secret Manager
secrets = {
    "db-password": config.require_secret("dbPassword"),
    "api-key": config.require_secret("apiKey"),
    "jwt-secret": config.require_secret("jwtSecret")
}

created_secrets = {}
for secret_name, secret_value in secrets.items():
    secret = gcp.secretmanager.Secret(secret_name,
        secret_id=f"apex-{secret_name}",
        replication=gcp.secretmanager.SecretReplicationArgs(
            automatic=gcp.secretmanager.SecretReplicationAutomaticArgs()
        )
    )

    version = gcp.secretmanager.SecretVersion(f"{secret_name}-v1",
        secret=secret.id,
        secret_data=secret_value
    )

    # Grant access to service account
    gcp.secretmanager.SecretIamMember(f"{secret_name}-access",
        secret_id=secret.id,
        role="roles/secretmanager.secretAccessor",
        member=service_account.email.apply(lambda email: f"serviceAccount:{email}")
    )

    created_secrets[secret_name] = secret

pulumi.export("secrets", {k: v.secret_id for k, v in created_secrets.items()})
```

---

## Region & Zone Configuration

### Multi-Region Best Practices

```python
import pulumi
import pulumi_gcp as gcp

# Define regions for multi-region deployment
regions = ["us-central1", "us-east1", "europe-west1"]
primary_region = "us-central1"

# Per-region resources
regional_services = []
for region in regions:
    # Cloud Run service in each region
    service = gcp.cloudrun.Service(f"api-{region}",
        location=region,
        template=gcp.cloudrun.ServiceTemplateArgs(
            spec=gcp.cloudrun.ServiceTemplateSpecArgs(
                containers=[gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                    image="gcr.io/apex-memory/api:latest",
                    ports=[gcp.cloudrun.ServiceTemplateSpecContainerPortArgs(
                        container_port=8000
                    )]
                )]
            )
        )
    )
    regional_services.append(service)

    # Public access
    gcp.cloudrun.IamMember(f"public-{region}",
        service=service.name,
        location=service.location,
        role="roles/run.invoker",
        member="allUsers"
    )

# Global Load Balancer (distributes traffic across regions)
# ... (see GCP Load Balancer documentation)

# Multi-region storage bucket
multi_region_bucket = gcp.storage.Bucket("data-multi-region",
    location="US",  # Multi-region location
    storage_class="STANDARD"
)

# Export regional endpoints
pulumi.export("regional_endpoints", {
    region: service.statuses[0].url
    for region, service in zip(regions, regional_services)
})
```

### Zone Configuration (Compute Engine)

```python
# Multi-zone instance group for high availability
zones = ["us-central1-a", "us-central1-b", "us-central1-c"]

instances = []
for i, zone in enumerate(zones):
    instance = gcp.compute.Instance(f"worker-{i}",
        machine_type="e2-medium",
        zone=zone,
        boot_disk=gcp.compute.InstanceBootDiskArgs(
            initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
                image="debian-cloud/debian-11"
            )
        ),
        network_interfaces=[gcp.compute.InstanceNetworkInterfaceArgs(
            network=vpc.id,
            subnetwork=subnet.id
        )]
    )
    instances.append(instance)

pulumi.export("instance_zones", [inst.zone for inst in instances])
```

---

## Production Patterns

### 1. High Availability Pattern

```python
# Regional (HA) Cloud SQL
db_instance = gcp.sql.DatabaseInstance("postgres-ha",
    database_version="POSTGRES_15",
    region="us-central1",
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-custom-4-15360",  # 4 vCPU, 15 GB RAM
        availability_type="REGIONAL",  # ⚠️ Automatic failover to different zone
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            enabled=True,
            point_in_time_recovery_enabled=True,
            transaction_log_retention_days=7
        )
    ),
    deletion_protection=True
)

# Multi-region Cloud Run
for region in ["us-central1", "us-east1", "europe-west1"]:
    gcp.cloudrun.Service(f"api-{region}",
        location=region,
        template=gcp.cloudrun.ServiceTemplateArgs(
            spec=gcp.cloudrun.ServiceTemplateSpecArgs(
                containers=[...]
            ),
            metadata=gcp.cloudrun.ServiceTemplateMetadataArgs(
                annotations={
                    "autoscaling.knative.dev/minScale": "2",  # Always 2+ instances
                    "autoscaling.knative.dev/maxScale": "100"
                }
            )
        )
    )
```

### 2. Cost Optimization Pattern

```python
# Development environment (cost-optimized)
dev_db = gcp.sql.DatabaseInstance("postgres-dev",
    database_version="POSTGRES_15",
    region="us-central1",
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-f1-micro",  # Smallest tier (~$7/month)
        availability_type="ZONAL",  # No HA
        disk_size=10,
        disk_autoresize=False
    ),
    deletion_protection=False
)

dev_service = gcp.cloudrun.Service("api-dev",
    location="us-central1",
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            containers=[...],
            container_concurrency=80
        ),
        metadata=gcp.cloudrun.ServiceTemplateMetadataArgs(
            annotations={
                "autoscaling.knative.dev/minScale": "0",  # Scale to zero
                "autoscaling.knative.dev/maxScale": "3"
            }
        )
    )
)
```

### 3. Security Hardening Pattern

```python
# Least-privilege service account
service_account = gcp.serviceaccount.Account("api-sa",
    account_id="apex-api",
    description="Service account for Apex API"
)

# Grant specific permissions only
gcp.projects.IAMMember("sql-client",
    project=project,
    role="roles/cloudsql.client",
    member=service_account.email.apply(lambda e: f"serviceAccount:{e}")
)

gcp.projects.IAMMember("secret-accessor",
    project=project,
    role="roles/secretmanager.secretAccessor",
    member=service_account.email.apply(lambda e: f"serviceAccount:{e}")
)

# Private Cloud SQL (no public IP)
db_instance = gcp.sql.DatabaseInstance("postgres",
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=False,  # No public IP
            private_network=vpc.id,
            require_ssl=True,
            ssl_mode="ENCRYPTED_ONLY"
        )
    )
)

# Cloud Run with restricted ingress
service = gcp.cloudrun.Service("api",
    metadata=gcp.cloudrun.ServiceMetadataArgs(
        annotations={
            "run.googleapis.com/ingress": "internal-and-cloud-load-balancing"  # Not public
        }
    )
)
```

---

## Example: Complete Apex Memory System Infrastructure

This example shows a production-ready deployment of the Apex Memory System.

```python
import pulumi
import pulumi_gcp as gcp

# Configuration
config = pulumi.Config()
project = config.require("gcp:project")
region = config.get("gcp:region") or "us-central1"
env = pulumi.get_stack()  # dev, staging, production

# Secrets
db_password = config.require_secret("dbPassword")
neo4j_password = config.require_secret("neo4jPassword")
openai_api_key = config.require_secret("openaiApiKey")

# ============================================================================
# NETWORKING
# ============================================================================

# VPC
vpc = gcp.compute.Network("apex-vpc",
    auto_create_subnetworks=False,
    description=f"Apex Memory System VPC - {env}"
)

# Subnet
subnet = gcp.compute.Subnetwork("apex-subnet",
    network=vpc.id,
    ip_cidr_range="10.0.0.0/24",
    region=region,
    private_ip_google_access=True
)

# Private IP range for Cloud SQL
private_ip_range = gcp.compute.GlobalAddress("cloudsql-ip",
    purpose="VPC_PEERING",
    address_type="INTERNAL",
    prefix_length=16,
    network=vpc.id
)

# Private VPC connection
private_vpc = gcp.servicenetworking.Connection("cloudsql-vpc",
    network=vpc.id,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=[private_ip_range.name]
)

# VPC Access Connector
vpc_connector = gcp.vpcaccess.Connector("vpc-connector",
    region=region,
    network=vpc.name,
    ip_cidr_range="10.8.0.0/28",
    min_throughput=200,
    max_throughput=1000
)

# Firewall rules
gcp.compute.Firewall("allow-internal",
    network=vpc.id,
    allows=[
        gcp.compute.FirewallAllowArgs(protocol="tcp", ports=["0-65535"]),
        gcp.compute.FirewallAllowArgs(protocol="udp", ports=["0-65535"]),
        gcp.compute.FirewallAllowArgs(protocol="icmp")
    ],
    source_ranges=["10.0.0.0/8"]
)

# ============================================================================
# DATABASES
# ============================================================================

# PostgreSQL (metadata + pgvector)
postgres = gcp.sql.DatabaseInstance("postgres",
    database_version="POSTGRES_15",
    region=region,
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-custom-2-7680",  # 2 vCPU, 7.5 GB
        disk_size=100,
        disk_type="PD_SSD",
        availability_type="REGIONAL" if env == "production" else "ZONAL",
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            enabled=True,
            start_time="03:00",
            point_in_time_recovery_enabled=True
        ),
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=False,
            private_network=vpc.id,
            require_ssl=True
        )
    ),
    deletion_protection=env == "production",
    opts=pulumi.ResourceOptions(depends_on=[private_vpc])
)

postgres_db = gcp.sql.Database("apex",
    instance=postgres.name,
    charset="UTF8"
)

postgres_user = gcp.sql.User("apex-user",
    instance=postgres.name,
    password=db_password
)

# ============================================================================
# STORAGE
# ============================================================================

# Data bucket
data_bucket = gcp.storage.Bucket("apex-data",
    location="US",
    storage_class="STANDARD",
    uniform_bucket_level_access=True,
    versioning=gcp.storage.BucketVersioningArgs(enabled=True),
    lifecycle_rules=[
        gcp.storage.BucketLifecycleRuleArgs(
            action=gcp.storage.BucketLifecycleRuleActionArgs(type="Delete"),
            condition=gcp.storage.BucketLifecycleRuleConditionArgs(age=90)
        )
    ]
)

# Model cache bucket
model_bucket = gcp.storage.Bucket("apex-models",
    location=region,
    storage_class="STANDARD",
    uniform_bucket_level_access=True
)

# ============================================================================
# SECRETS
# ============================================================================

secrets = {
    "db-password": db_password,
    "neo4j-password": neo4j_password,
    "openai-api-key": openai_api_key
}

for secret_name, secret_value in secrets.items():
    secret = gcp.secretmanager.Secret(secret_name,
        secret_id=f"apex-{env}-{secret_name}",
        replication=gcp.secretmanager.SecretReplicationArgs(
            automatic=gcp.secretmanager.SecretReplicationAutomaticArgs()
        )
    )

    gcp.secretmanager.SecretVersion(f"{secret_name}-v1",
        secret=secret.id,
        secret_data=secret_value
    )

# ============================================================================
# COMPUTE - NEO4J (Compute Engine)
# ============================================================================

# Service account for Neo4j VM
neo4j_sa = gcp.serviceaccount.Account("neo4j-sa",
    account_id=f"apex-{env}-neo4j",
    display_name="Neo4j Service Account"
)

# Neo4j instance
neo4j_disk = gcp.compute.Disk("neo4j-disk",
    zone=f"{region}-a",
    size=100,
    type="pd-ssd"
)

neo4j_instance = gcp.compute.Instance("neo4j",
    machine_type="e2-standard-4",  # 4 vCPU, 16 GB
    zone=f"{region}-a",
    boot_disk=gcp.compute.InstanceBootDiskArgs(
        initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
            image="ubuntu-os-cloud/ubuntu-2204-lts",
            size=20
        )
    ),
    attached_disks=[gcp.compute.InstanceAttachedDiskArgs(
        source=neo4j_disk.self_link
    )],
    network_interfaces=[gcp.compute.InstanceNetworkInterfaceArgs(
        network=vpc.id,
        subnetwork=subnet.id
    )],
    service_account=gcp.compute.InstanceServiceAccountArgs(
        email=neo4j_sa.email,
        scopes=["cloud-platform"]
    ),
    metadata_startup_script=neo4j_password.apply(lambda pwd: f"""#!/bin/bash
        # Install Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh

        # Run Neo4j
        docker run -d \
          --name neo4j \
          --restart always \
          -p 7474:7474 -p 7687:7687 \
          -v /mnt/neo4j:/data \
          -e NEO4J_AUTH=neo4j/{pwd} \
          neo4j:5.15
    """)
)

# ============================================================================
# COMPUTE - CLOUD RUN API
# ============================================================================

# Service account for Cloud Run
api_sa = gcp.serviceaccount.Account("api-sa",
    account_id=f"apex-{env}-api",
    display_name="API Service Account"
)

# Grant permissions
gcp.projects.IAMMember("api-sql-client",
    project=project,
    role="roles/cloudsql.client",
    member=api_sa.email.apply(lambda e: f"serviceAccount:{e}")
)

gcp.projects.IAMMember("api-secret-accessor",
    project=project,
    role="roles/secretmanager.secretAccessor",
    member=api_sa.email.apply(lambda e: f"serviceAccount:{e}")
)

gcp.storage.BucketIAMMember("api-storage-admin",
    bucket=data_bucket.name,
    role="roles/storage.objectAdmin",
    member=api_sa.email.apply(lambda e: f"serviceAccount:{e}")
)

# Cloud Run service
api_service = gcp.cloudrun.Service("apex-api",
    location=region,
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            service_account_name=api_sa.email,
            containers=[gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                image=f"gcr.io/{project}/apex-api:latest",
                ports=[gcp.cloudrun.ServiceTemplateSpecContainerPortArgs(
                    container_port=8000
                )],
                resources=gcp.cloudrun.ServiceTemplateSpecContainerResourcesArgs(
                    limits={"cpu": "2", "memory": "2Gi"}
                ),
                envs=[
                    # Database
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_HOST",
                        value=postgres.private_ip_address
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_NAME",
                        value=postgres_db.name
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_USER",
                        value=postgres_user.name
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="DB_PASSWORD",
                        value=db_password
                    ),
                    # Neo4j
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="NEO4J_URI",
                        value=neo4j_instance.network_interfaces[0].network_ip.apply(
                            lambda ip: f"bolt://{ip}:7687"
                        )
                    ),
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="NEO4J_PASSWORD",
                        value=neo4j_password
                    ),
                    # Storage
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="GCS_BUCKET",
                        value=data_bucket.name
                    ),
                    # OpenAI
                    gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                        name="OPENAI_API_KEY",
                        value=openai_api_key
                    )
                ]
            )]
        ),
        metadata=gcp.cloudrun.ServiceTemplateMetadataArgs(
            annotations={
                "autoscaling.knative.dev/minScale": "1" if env == "production" else "0",
                "autoscaling.knative.dev/maxScale": "10",
                "run.googleapis.com/vpc-access-connector": vpc_connector.name,
                "run.googleapis.com/vpc-access-egress": "private-ranges-only"
            }
        )
    )
)

# Public access
gcp.cloudrun.IamMember("api-public",
    service=api_service.name,
    location=api_service.location,
    role="roles/run.invoker",
    member="allUsers"
)

# ============================================================================
# EXPORTS
# ============================================================================

pulumi.export("api_url", api_service.statuses[0].url)
pulumi.export("postgres_connection", postgres.connection_name)
pulumi.export("postgres_private_ip", postgres.private_ip_address)
pulumi.export("neo4j_internal_ip", neo4j_instance.network_interfaces[0].network_ip)
pulumi.export("data_bucket", data_bucket.url)
pulumi.export("vpc_id", vpc.id)
```

### Deploying the Example

```bash
# 1. Configure stack
pulumi stack init production
pulumi config set gcp:project apex-memory-prod
pulumi config set gcp:region us-central1

# 2. Set secrets
pulumi config set dbPassword <password> --secret
pulumi config set neo4jPassword <password> --secret
pulumi config set openaiApiKey <key> --secret

# 3. Preview
pulumi preview

# 4. Deploy
pulumi up

# 5. Get outputs
pulumi stack output api_url
pulumi stack output postgres_private_ip
```

---

## Quick Reference

### Common Commands

```bash
# Configure GCP project
pulumi config set gcp:project apex-memory
pulumi config set gcp:region us-central1

# Deploy infrastructure
pulumi up

# View outputs
pulumi stack output api_url

# Destroy infrastructure
pulumi destroy
```

### Essential Resources

| Resource | Python Class | Use Case |
|----------|--------------|----------|
| Cloud Run | `gcp.cloudrun.Service` | Serverless containers |
| Cloud SQL | `gcp.sql.DatabaseInstance` | Managed PostgreSQL/MySQL |
| VPC | `gcp.compute.Network` | Private networking |
| Subnet | `gcp.compute.Subnetwork` | Network segmentation |
| Storage Bucket | `gcp.storage.Bucket` | Object storage |
| Secret Manager | `gcp.secretmanager.Secret` | Secrets storage |
| VPC Connector | `gcp.vpcaccess.Connector` | Cloud Run → VPC access |
| Compute Engine | `gcp.compute.Instance` | Virtual machines |
| Service Account | `gcp.serviceaccount.Account` | Identity for services |

---

## Next Steps

- Read **[PULUMI-FUNDAMENTALS.md](./PULUMI-FUNDAMENTALS.md)** for core Pulumi concepts
- Review [GCP Provider API Documentation](https://www.pulumi.com/registry/packages/gcp/api-docs/)
- Explore [Pulumi GCP Examples](https://github.com/pulumi/examples?q=gcp)
- Check [Google Cloud Documentation](https://cloud.google.com/docs)

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Maintained By:** research-coordinator (documentation-hunter agent)
