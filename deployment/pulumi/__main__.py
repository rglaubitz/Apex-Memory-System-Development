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
# TODO: Import Modules (Create these after research review)
# =============================================================================

# from modules.networking import create_vpc
# from modules.databases import create_database_cluster
# from modules.compute import create_cloudrun_services
# from modules.secrets import create_secret_manager
# from modules.monitoring import create_monitoring

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
# Module Orchestration (TODO: Uncomment after creating modules)
# =============================================================================

# # 1. Create VPC networking
# network = create_vpc(
#     project_id=project_id,
#     region=region,
#     stack=stack,
#     tags=default_tags,
# )

# # 2. Create database cluster (PostgreSQL + Redis + Neo4j + Qdrant)
# databases = create_database_cluster(
#     project_id=project_id,
#     region=region,
#     zone=zone,
#     stack=stack,
#     network=network,
#     tags=default_tags,
# )

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

# Service exports (TODO: Uncomment after module creation)
# pulumi.export("api_url", services["api"].url)
# pulumi.export("vpc_id", network.vpc.id)
# pulumi.export("postgres_connection", databases["postgres"].connection_name)
# pulumi.export("neo4j_ip", databases["neo4j"].network_interface.access_config.nat_ip)

# Summary export
pulumi.export(
    "deployment_summary",
    {
        "environment": stack,
        "project": project_id,
        "region": region,
        "status": "infrastructure-skeleton-deployed",
        "next_steps": [
            "1. Create modules/networking.py",
            "2. Create modules/databases.py",
            "3. Create modules/compute.py",
            "4. Create modules/secrets.py",
            "5. Create modules/monitoring.py",
            "6. Uncomment module orchestration above",
            "7. Run: pulumi up",
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
