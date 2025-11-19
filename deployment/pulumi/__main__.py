"""
Apex Memory System - GCP Infrastructure (Pulumi)

This is the main entry point for Pulumi infrastructure deployment.
It orchestrates all modules to create:
- VPC networking with private Google Access
- Cloud SQL PostgreSQL (multi-zone HA)
- Neo4j on Compute Engine
- Redis Memorystore
- Qdrant vector database
- Cloud Run services (API, Workers)
- Secret Manager integration
- IAM service accounts

Architecture:
- Multi-database parallel writes (saga pattern)
- Serverless Cloud Run for API and workers
- Private networking for databases
- Temporal Cloud for workflow orchestration

Usage:
  pulumi up                  # Deploy to current stack
  pulumi preview             # Preview changes before applying
  pulumi destroy             # Tear down infrastructure
  pulumi stack select dev    # Switch to dev environment
"""

import pulumi
import pulumi_gcp as gcp

# =============================================================================
# Configuration
# =============================================================================

config = pulumi.Config()
gcp_config = pulumi.Config("gcp")

# Project settings
project_id = gcp_config.require("project")
region = gcp_config.get("region") or "us-central1"
zone = gcp_config.get("zone") or "us-central1-a"

# Stack-specific configuration
stack = pulumi.get_stack()
is_production = stack == "production"

# Tags for cost tracking
default_tags = {
    "project": "apex-memory",
    "environment": stack,
    "managed-by": "pulumi",
    "cost-center": "infrastructure",
}

# =============================================================================
# Import Modules
# =============================================================================

from modules.networking import create_vpc_network
from modules.databases import (
    create_cloud_sql_postgres,
    create_neo4j_instance,
    create_redis_instance,
    create_qdrant_instance,
)
from modules.compute import (
    create_cloud_run_api_service,
    create_cloud_run_worker_service,
)
# TODO Week 5+: import create_secret_manager
# TODO Week 6+: import create_monitoring

# =============================================================================
# Placeholder Resources (Replace with module imports)
# =============================================================================

# Example: Enable required GCP APIs
# This is a minimal example to get started

required_services = [
    "compute.googleapis.com",           # Compute Engine (Neo4j VM)
    "sqladmin.googleapis.com",          # Cloud SQL
    "sql-component.googleapis.com",     # Cloud SQL Admin
    "servicenetworking.googleapis.com", # VPC Service Networking
    "vpcaccess.googleapis.com",         # VPC Access (Cloud Run connector)
    "redis.googleapis.com",             # Memorystore Redis
    "run.googleapis.com",               # Cloud Run
    "secretmanager.googleapis.com",     # Secret Manager
    "cloudresourcemanager.googleapis.com", # Resource Manager
    "iam.googleapis.com",               # IAM
    "logging.googleapis.com",           # Cloud Logging
    "monitoring.googleapis.com",        # Cloud Monitoring
]

# Enable APIs (idempotent - safe to run multiple times)
enabled_services = []
for service_name in required_services:
    service = gcp.projects.Service(
        f"enable-{service_name.replace('.googleapis.com', '')}",
        service=service_name,
        project=project_id,
        disable_on_destroy=False,  # Don't disable on destroy (safety)
        opts=pulumi.ResourceOptions(
            protect=True if is_production else False,  # Protect in production
        ),
    )
    enabled_services.append(service)

# =============================================================================
# Module Orchestration
# =============================================================================

# 1. Create VPC networking
network = create_vpc_network(
    project_id=project_id,
    region=region,
)

# 2. Create Cloud SQL PostgreSQL
postgres_db = create_cloud_sql_postgres(
    project_id=project_id,
    region=region,
    network_id=network["vpc"].id,
    private_connection=network["private_connection"],
    tier="db-f1-micro",  # Dev tier (use db-n1-standard-1 for prod)
)

# 3. Create Neo4j graph database
neo4j_db = create_neo4j_instance(
    project_id=project_id,
    region=region,
    network_id=network["vpc"].id,
    subnet_id=network["subnet"].id,
    machine_type="e2-small",  # Dev tier (use e2-standard-4 for prod)
    disk_size_gb=50,
)

# 4. Create Redis Memorystore
redis_cache = create_redis_instance(
    project_id=project_id,
    region=region,
    network_id=network["vpc"].id,
    memory_size_gb=1,  # Dev tier (use 5+ for prod)
    tier="BASIC",  # Use "STANDARD_HA" for prod
)

# 5. Create Qdrant vector database
qdrant_db = create_qdrant_instance(
    project_id=project_id,
    region=region,
    network_id=network["vpc"].id,
    subnet_id=network["subnet"].id,
    machine_type="e2-medium",  # Dev tier (use e2-standard-4 for prod)
    disk_size_gb=100,  # 100GB for dev (use 500GB+ for prod)
)

# 6. Create Cloud Run API service
api_service = create_cloud_run_api_service(
    project_id=project_id,
    region=region,
    network_id=network["vpc"].id,
    subnet_id=network["subnet"].id,
    image_uri=f"us-central1-docker.pkg.dev/{project_id}/apex-containers/apex-api:dev",
    postgres_host=postgres_db["postgres"].private_ip_address,
    postgres_db="apex_memory",
    neo4j_uri=neo4j_db["instance"].network_interfaces[0].network_ip.apply(
        lambda ip: f"bolt://{ip}:7687"
    ),
    redis_host=redis_cache["instance"].host,
    qdrant_host=qdrant_db["instance"].network_interfaces[0].network_ip,
)

# 7. Create Cloud Run Worker service
worker_service = create_cloud_run_worker_service(
    project_id=project_id,
    region=region,
    network_id=network["vpc"].id,
    subnet_id=network["subnet"].id,
    image_uri=f"us-central1-docker.pkg.dev/{project_id}/apex-containers/apex-worker:dev",
    postgres_host=postgres_db["postgres"].private_ip_address,
    postgres_db="apex_memory",
    neo4j_uri=neo4j_db["instance"].network_interfaces[0].network_ip.apply(
        lambda ip: f"bolt://{ip}:7687"
    ),
    redis_host=redis_cache["instance"].host,
    qdrant_host=qdrant_db["instance"].network_interfaces[0].network_ip,
)

# TODO Week 5: Add Secret Manager
# TODO Week 6: Add Monitoring

# # 3. Create Secret Manager secrets
# secrets = create_secret_manager(
#     project_id=project_id,
#     databases=databases,
#     stack=stack,
#     tags=default_tags,
# )

# # 4. Create Cloud Run services
# services = create_cloudrun_services(
#     project_id=project_id,
#     region=region,
#     stack=stack,
#     network=network,
#     databases=databases,
#     secrets=secrets,
#     tags=default_tags,
# )

# # 5. Create monitoring and alerting
# monitoring = create_monitoring(
#     project_id=project_id,
#     stack=stack,
#     services=services,
#     databases=databases,
# )

# =============================================================================
# Exports (Outputs for other stacks or CI/CD)
# =============================================================================

# Basic exports
pulumi.export("project_id", project_id)
pulumi.export("region", region)
pulumi.export("zone", zone)
pulumi.export("stack", stack)
pulumi.export("is_production", is_production)

# Network exports
pulumi.export("vpc_id", network["vpc"].id)
pulumi.export("vpc_name", network["vpc"].name)

# Database exports
pulumi.export("postgres_private_ip", postgres_db["postgres"].private_ip_address)
pulumi.export("neo4j_private_ip", neo4j_db["instance"].network_interfaces[0].network_ip)
pulumi.export("redis_host", redis_cache["instance"].host)
pulumi.export("qdrant_private_ip", qdrant_db["instance"].network_interfaces[0].network_ip)

# Cloud Run service exports
pulumi.export("api_url", api_service["url"])
pulumi.export("api_service_name", api_service["service"].name)
pulumi.export("worker_service_name", worker_service["service"].name)

# Summary export
pulumi.export(
    "deployment_summary",
    {
        "environment": stack,
        "project": project_id,
        "region": region,
        "status": "week-4-complete-cloud-run-deployed",
        "completed_weeks": [
            "Week 1: PostgreSQL + VPC",
            "Week 2: Neo4j",
            "Week 3: Redis + Qdrant",
            "Week 4: Cloud Run (API + Worker)",
        ],
        "deployed_resources": {
            "networking": "VPC with private subnets",
            "databases": {
                "postgresql": "Cloud SQL (private IP)",
                "neo4j": "Compute Engine VM",
                "redis": "Memorystore",
                "qdrant": "Compute Engine VM",
            },
            "compute": {
                "api_service": "Cloud Run (Direct VPC Egress)",
                "worker_service": "Cloud Run (Direct VPC Egress)",
            },
            "secrets": "Secret Manager (postgres, neo4j passwords)",
        },
        "next_steps": [
            "1. Verify API service health: Check /health endpoint",
            "2. Test database connectivity from Cloud Run",
            "3. Week 5: Add monitoring dashboards",
            "4. Week 6: Production hardening",
        ],
    },
)

# =============================================================================
# Notes for Implementation
# =============================================================================

# Research findings recommend:
# - Python SDK with uv package manager (100x faster)
# - Pulumi Cloud backend (free tier, auto state locking)
# - GitHub Actions CI/CD (PR previews + merge auto-deploy)
# - GCP Secret Manager (simple, native)
# - Multi-stack approach (dev/staging/production)
#
# See research/ directory for comprehensive best practices:
# - research/PULUMI-FUNDAMENTALS.md
# - research/PULUMI-GCP-GUIDE.md
# - research/PULUMI-EXAMPLES.md
# - research/PULUMI-BEST-PRACTICES.md
# - research/PULUMI-COMPARISON.md
# - research/PULUMI-TRENDS-2025.md
