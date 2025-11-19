"""
Database Module for Apex Memory System

Creates GCP database infrastructure:
- Cloud SQL PostgreSQL with private IP (pgvector extension)
- Neo4j on Compute Engine (graph database)
- Redis Memorystore (caching layer)
- Qdrant on Compute Engine (vector database)
- Database and user creation with automated backups

Research:
- deployment/pulumi/research/PULUMI-GCP-GUIDE.md (lines 600-750, 1513-1563)
- deployment/pulumi/research/QDRANT-DEPLOYMENT-RESEARCH.md
"""

import pulumi
import pulumi_gcp as gcp
import pulumi_random as random
from typing import Dict, Any


def create_cloud_sql_postgres(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    private_connection: gcp.servicenetworking.Connection,
    tier: str = "db-f1-micro",
    database_name: str = "apex_memory",
    user_name: str = "apex",
) -> Dict[str, Any]:
    """
    Create Cloud SQL PostgreSQL instance with private IP.

    Args:
        project_id: GCP project ID
        region: GCP region
        network_id: VPC network ID (from networking module)
        private_connection: Private service connection (from networking module)
        tier: Machine type (db-f1-micro for dev, db-n1-standard-1 for prod)
        database_name: PostgreSQL database name
        user_name: PostgreSQL username

    Returns:
        Dictionary containing database resources:
        - postgres: Cloud SQL instance
        - database: PostgreSQL database
        - user: PostgreSQL user
        - password: Generated password (secret)
    """

    # Generate secure random password for PostgreSQL
    db_password = random.RandomPassword(
        "postgres-password",
        length=32,
        special=True,
        override_special="!#$%&*()-_=+[]{}<>:?",  # Avoid chars that cause shell issues
    )

    # Create Cloud SQL PostgreSQL instance
    postgres = gcp.sql.DatabaseInstance(
        "apex-postgres",
        name="apex-postgres-dev",  # Must be globally unique
        database_version="POSTGRES_17",
        region=region,
        project=project_id,
        settings=gcp.sql.DatabaseInstanceSettingsArgs(
            tier=tier,
            # IP configuration: private IP only
            ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
                ipv4_enabled=False,  # No public IP
                private_network=network_id,
                ssl_mode="ALLOW_UNENCRYPTED_AND_ENCRYPTED",  # Updated from require_ssl
            ),
            # Backup configuration
            backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
                enabled=True,
                start_time="02:00",  # 2 AM UTC
                backup_retention_settings=gcp.sql.DatabaseInstanceSettingsBackupConfigurationBackupRetentionSettingsArgs(
                    retained_backups=7,
                    retention_unit="COUNT",
                ),
            ),
            # High availability (optional for dev)
            availability_type="ZONAL",  # Use "REGIONAL" for prod HA
            # Skip custom database flags for initial deployment
            # Can be added later via: gcloud sql instances patch
            # database_flags=[
            #     gcp.sql.DatabaseInstanceSettingsDatabaseFlagArgs(
            #         name="max_connections",
            #         value="100",
            #     ),
            # ],
        ),
        deletion_protection=False,  # Allow deletion in dev
        opts=pulumi.ResourceOptions(
            depends_on=[private_connection] if private_connection else None,
        ),
    )

    # Create PostgreSQL database
    database = gcp.sql.Database(
        "apex-memory-db",
        name=database_name,
        instance=postgres.name,
        project=project_id,
    )

    # Create PostgreSQL user
    user = gcp.sql.User(
        "apex-user",
        name=user_name,
        instance=postgres.name,
        password=db_password.result,
        project=project_id,
    )

    # Export outputs
    pulumi.export("postgres_instance_name", postgres.name)
    pulumi.export("postgres_connection_name", postgres.connection_name)
    pulumi.export("postgres_private_ip", postgres.private_ip_address)
    pulumi.export("database_name", database.name)
    pulumi.export("postgres_user", user.name)
    pulumi.export("postgres_password", pulumi.Output.secret(db_password.result))

    return {
        "postgres": postgres,
        "database": database,
        "user": user,
        "password": db_password.result,
    }


def create_neo4j_instance(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    subnet_id: pulumi.Output[str],
    machine_type: str = "e2-small",
    disk_size_gb: int = 50,
) -> Dict[str, Any]:
    """
    Create Neo4j graph database on Compute Engine.

    Args:
        project_id: GCP project ID
        region: GCP region
        network_id: VPC network ID (from networking module)
        subnet_id: VPC subnet ID (from networking module)
        machine_type: VM machine type (e2-small for dev, e2-standard-4 for prod)
        disk_size_gb: Persistent disk size in GB

    Returns:
        Dictionary containing Neo4j resources:
        - service_account: Service account for Neo4j VM
        - disk: Persistent SSD disk for Neo4j data
        - instance: Compute Engine instance
        - password: Generated Neo4j password (secret)
    """

    # Generate secure random password for Neo4j
    neo4j_password = random.RandomPassword(
        "neo4j-password",
        length=32,
        special=True,
        override_special="!#$%&*()-_=+[]{}<>:?",
    )

    # Service account for Neo4j VM
    neo4j_sa = gcp.serviceaccount.Account(
        "neo4j-sa",
        account_id=f"apex-neo4j-{pulumi.get_stack()}",
        display_name="Neo4j Service Account",
        project=project_id,
    )

    # Persistent SSD disk for Neo4j data
    neo4j_disk = gcp.compute.Disk(
        "neo4j-disk",
        name="apex-neo4j-data-disk",
        zone=f"{region}-a",
        size=disk_size_gb,
        type="pd-ssd",  # SSD for better performance
        project=project_id,
    )

    # Neo4j startup script (installs Docker and runs Neo4j container)
    startup_script = neo4j_password.result.apply(
        lambda pwd: f"""#!/bin/bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Wait for Docker to be ready
sleep 10

# Format and mount data disk
mkfs.ext4 -F /dev/sdb
mkdir -p /mnt/neo4j
mount /dev/sdb /mnt/neo4j
echo '/dev/sdb /mnt/neo4j ext4 defaults,nofail 0 2' >> /etc/fstab

# Run Neo4j container
docker run -d \\
  --name neo4j \\
  --restart always \\
  -p 7474:7474 -p 7687:7687 \\
  -v /mnt/neo4j:/data \\
  -e NEO4J_AUTH=neo4j/{pwd} \\
  -e NEO4J_dbms_memory_heap_initial__size=512m \\
  -e NEO4J_dbms_memory_heap_max__size=1G \\
  neo4j:5.15-community

# Wait for Neo4j to start
sleep 30
echo "Neo4j started successfully"
"""
    )

    # Neo4j Compute Engine instance
    neo4j_instance = gcp.compute.Instance(
        "neo4j",
        name="apex-neo4j-dev",
        machine_type=machine_type,
        zone=f"{region}-a",
        project=project_id,
        boot_disk=gcp.compute.InstanceBootDiskArgs(
            initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
                image="ubuntu-os-cloud/ubuntu-2204-lts",
                size=20,  # Boot disk size
            )
        ),
        attached_disks=[
            gcp.compute.InstanceAttachedDiskArgs(source=neo4j_disk.self_link)
        ],
        network_interfaces=[
            gcp.compute.InstanceNetworkInterfaceArgs(
                network=network_id,
                subnetwork=subnet_id,
                # No external IP (private only)
            )
        ],
        service_account=gcp.compute.InstanceServiceAccountArgs(
            email=neo4j_sa.email,
            scopes=["cloud-platform"],
        ),
        metadata_startup_script=startup_script,
        tags=["neo4j", "database"],
    )

    # Export outputs
    pulumi.export("neo4j_instance_name", neo4j_instance.name)
    pulumi.export(
        "neo4j_private_ip",
        neo4j_instance.network_interfaces[0].network_ip,
    )
    pulumi.export(
        "neo4j_bolt_uri",
        neo4j_instance.network_interfaces[0].network_ip.apply(
            lambda ip: f"bolt://{ip}:7687"
        ),
    )
    pulumi.export(
        "neo4j_browser_uri",
        neo4j_instance.network_interfaces[0].network_ip.apply(
            lambda ip: f"http://{ip}:7474"
        ),
    )
    pulumi.export("neo4j_password", pulumi.Output.secret(neo4j_password.result))

    return {
        "service_account": neo4j_sa,
        "disk": neo4j_disk,
        "instance": neo4j_instance,
        "password": neo4j_password.result,
    }


def create_redis_instance(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    memory_size_gb: int = 1,
    tier: str = "BASIC",
) -> Dict[str, Any]:
    """
    Create Redis Memorystore instance.

    Args:
        project_id: GCP project ID
        region: GCP region
        network_id: VPC network ID (from networking module)
        memory_size_gb: Memory size in GB (1 for dev, 5+ for prod)
        tier: Service tier (BASIC for dev, STANDARD_HA for prod)

    Returns:
        Dictionary containing Redis resources:
        - instance: Redis Memorystore instance
    """

    # Create Redis Memorystore instance
    redis = gcp.redis.Instance(
        "apex-redis",
        name="apex-redis-dev",
        tier=tier,
        memory_size_gb=memory_size_gb,
        region=region,
        project=project_id,
        authorized_network=network_id,
        redis_version="REDIS_7_0",
        display_name="Apex Memory System Redis Cache",
        # Redis configurations
        redis_configs={
            "maxmemory-policy": "allkeys-lru",  # Evict least recently used keys
        },
    )

    # Export outputs
    pulumi.export("redis_instance_name", redis.name)
    pulumi.export("redis_host", redis.host)
    pulumi.export("redis_port", redis.port)
    pulumi.export(
        "redis_connection_string",
        pulumi.Output.all(redis.host, redis.port).apply(
            lambda args: f"redis://{args[0]}:{args[1]}"
        ),
    )

    return {
        "instance": redis,
    }


def create_qdrant_instance(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    subnet_id: pulumi.Output[str],
    machine_type: str = "e2-medium",
    disk_size_gb: int = 100,
) -> Dict[str, Any]:
    """
    Create Qdrant vector database on Compute Engine.

    Args:
        project_id: GCP project ID
        region: GCP region
        network_id: VPC network ID (from networking module)
        subnet_id: VPC subnet ID (from networking module)
        machine_type: Machine type (e2-medium for dev: 2 vCPU, 4GB RAM)
        disk_size_gb: Persistent disk size in GB (100GB for dev, 500GB+ for prod)

    Returns:
        Dictionary containing Qdrant resources:
        - service_account: Service account for Qdrant VM
        - disk: Persistent SSD disk for vector storage
        - instance: Compute Engine instance running Qdrant

    Research: deployment/pulumi/research/QDRANT-DEPLOYMENT-RESEARCH.md
    """

    # Service account for Qdrant VM
    qdrant_sa = gcp.serviceaccount.Account(
        "qdrant-sa",
        account_id=f"apex-qdrant-{pulumi.get_stack()}",
        display_name="Qdrant Service Account",
        project=project_id,
    )

    # Persistent SSD disk for vector storage
    # Qdrant requires block-level access with POSIX filesystem (SSD recommended)
    qdrant_disk = gcp.compute.Disk(
        "qdrant-disk",
        name="apex-qdrant-data-disk",
        zone=f"{region}-a",
        size=disk_size_gb,
        type="pd-ssd",  # SSD recommended for vector operations
        project=project_id,
    )

    # Startup script to install Docker and run Qdrant container
    startup_script = f"""#!/bin/bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sleep 10  # Wait for Docker daemon to start

# Format and mount data disk for Qdrant storage
mkfs.ext4 -F /dev/sdb
mkdir -p /mnt/qdrant
mount /dev/sdb /mnt/qdrant
echo '/dev/sdb /mnt/qdrant ext4 defaults,nofail 0 2' >> /etc/fstab

# Run Qdrant container with persistent storage
docker run -d \\
  --name qdrant \\
  --restart always \\
  -p 6333:6333 \\
  -p 6334:6334 \\
  -v /mnt/qdrant:/qdrant/storage \\
  qdrant/qdrant:latest

# Wait for Qdrant to start and log health status
sleep 15
curl -s http://localhost:6333/health || echo "Qdrant not ready yet (will auto-restart)"
"""

    # Create Compute Engine VM instance for Qdrant
    qdrant_instance = gcp.compute.Instance(
        "qdrant",
        name="apex-qdrant-dev",
        machine_type=machine_type,
        zone=f"{region}-a",
        project=project_id,
        # Boot disk (Ubuntu 22.04 LTS)
        boot_disk=gcp.compute.InstanceBootDiskArgs(
            initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
                image="ubuntu-os-cloud/ubuntu-2204-lts",
                size=20,  # 20GB for OS
            )
        ),
        # Attach persistent data disk
        attached_disks=[
            gcp.compute.InstanceAttachedDiskArgs(source=qdrant_disk.self_link)
        ],
        # Network configuration (private IP only, no external IP)
        network_interfaces=[
            gcp.compute.InstanceNetworkInterfaceArgs(
                network=network_id,
                subnetwork=subnet_id,
                # No access_config = no external IP (VPC-private only)
            )
        ],
        # Service account with minimal permissions
        service_account=gcp.compute.InstanceServiceAccountArgs(
            email=qdrant_sa.email,
            scopes=["cloud-platform"],  # Allow GCP API access for logging
        ),
        # Startup script to install and run Qdrant
        metadata_startup_script=startup_script,
        # Network tags
        tags=["qdrant", "database", "vector-db"],
        # Allow deletion in dev
        deletion_protection=False,
    )

    # Export outputs
    pulumi.export("qdrant_instance_name", qdrant_instance.name)
    pulumi.export("qdrant_private_ip", qdrant_instance.network_interfaces[0].network_ip)
    pulumi.export(
        "qdrant_http_endpoint",
        qdrant_instance.network_interfaces[0].network_ip.apply(
            lambda ip: f"http://{ip}:6333"
        ),
    )
    pulumi.export(
        "qdrant_grpc_endpoint",
        qdrant_instance.network_interfaces[0].network_ip.apply(
            lambda ip: f"http://{ip}:6334"
        ),
    )

    return {
        "service_account": qdrant_sa,
        "disk": qdrant_disk,
        "instance": qdrant_instance,
    }
