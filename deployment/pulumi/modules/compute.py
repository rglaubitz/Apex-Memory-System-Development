"""
Compute Module - Cloud Run Services

This module creates Cloud Run services for the Apex Memory System:
- API service: FastAPI application with public access
- Worker service: Temporal worker with internal-only access

Both services use Direct VPC Egress for database connectivity.
"""

from typing import Dict, Any
import pulumi
import pulumi_gcp as gcp


def create_cloud_run_api_service(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    subnet_id: pulumi.Output[str],
    image_uri: str,
    postgres_host: str,
    postgres_db: str,
    neo4j_uri: str,
    redis_host: str,
    qdrant_host: str,
) -> Dict[str, Any]:
    """
    Create Cloud Run API service with Direct VPC Egress.

    Args:
        project_id: GCP project ID
        region: GCP region (us-central1)
        network_id: VPC network ID
        subnet_id: VPC subnet ID
        image_uri: Full image URI in Artifact Registry
        postgres_host: PostgreSQL private IP
        postgres_db: PostgreSQL database name
        neo4j_uri: Neo4j bolt URI
        redis_host: Redis private IP
        qdrant_host: Qdrant private IP

    Returns:
        Dictionary containing:
        - service: Cloud Run service resource
        - service_account: Service account for the API
        - url: Public URL of the API service
    """

    # Create service account for API
    api_sa = gcp.serviceaccount.Account(
        "api-service-account",
        account_id=f"apex-api-{pulumi.get_stack()}",
        display_name="Apex API Service Account",
        project=project_id,
    )

    # Grant Secret Manager access to service account
    for secret_name in ["postgres-password", "neo4j-password"]:
        gcp.secretmanager.SecretIamMember(
            f"api-secret-access-{secret_name}",
            project=project_id,
            secret_id=secret_name,
            role="roles/secretmanager.secretAccessor",
            member=api_sa.email.apply(lambda email: f"serviceAccount:{email}"),
        )

    # Create Cloud Run API service
    api_service = gcp.cloudrunv2.Service(
        "apex-api",
        name=f"apex-api-{pulumi.get_stack()}",
        location=region,
        project=project_id,
        ingress="INGRESS_TRAFFIC_ALL",  # Allow public access
        template=gcp.cloudrunv2.ServiceTemplateArgs(
            service_account=api_sa.email,
            execution_environment="EXECUTION_ENVIRONMENT_GEN2",  # Required for Direct VPC
            scaling=gcp.cloudrunv2.ServiceTemplateScalingArgs(
                min_instance_count=0,  # Scale to zero for dev cost savings
                max_instance_count=10,  # Cap at 10 instances for dev
            ),
            vpc_access=gcp.cloudrunv2.ServiceTemplateVpcAccessArgs(
                egress="PRIVATE_RANGES_ONLY",  # Only VPC traffic through Direct VPC
                network_interfaces=[
                    gcp.cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
                        network=network_id,
                        subnetwork=subnet_id,
                    )
                ],
            ),
            containers=[
                gcp.cloudrunv2.ServiceTemplateContainerArgs(
                    image=image_uri,
                    ports=[
                        gcp.cloudrunv2.ServiceTemplateContainerPortArgs(
                            container_port=8000,
                            name="http1",
                        )
                    ],
                    resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                        limits={
                            "cpu": "2",
                            "memory": "2Gi",
                        },
                    ),
                    startup_probe=gcp.cloudrunv2.ServiceTemplateContainerStartupProbeArgs(
                        http_get=gcp.cloudrunv2.ServiceTemplateContainerStartupProbeHttpGetArgs(
                            path="/health",
                            port=8000,
                        ),
                        initial_delay_seconds=10,
                        timeout_seconds=5,
                        period_seconds=30,
                        failure_threshold=3,
                    ),
                    envs=[
                        # Database connection details (non-sensitive)
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="POSTGRES_HOST",
                            value=postgres_host,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="POSTGRES_DB",
                            value=postgres_db,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="POSTGRES_USER",
                            value="apex",
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="NEO4J_URI",
                            value=neo4j_uri,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="REDIS_HOST",
                            value=redis_host,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="REDIS_PORT",
                            value="6379",
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="QDRANT_HOST",
                            value=qdrant_host,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="QDRANT_PORT",
                            value="6333",
                        ),
                    ],
                    volume_mounts=[
                        # Mount secrets as files
                        gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                            name="postgres-password",
                            mount_path="/secrets/postgres",
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                            name="neo4j-password",
                            mount_path="/secrets/neo4j",
                        ),
                    ],
                )
            ],
            volumes=[
                # Secret Manager volumes
                gcp.cloudrunv2.ServiceTemplateVolumeArgs(
                    name="postgres-password",
                    secret=gcp.cloudrunv2.ServiceTemplateVolumeSecretArgs(
                        secret="postgres-password",
                        default_mode=0o444,  # Read-only
                        items=[
                            gcp.cloudrunv2.ServiceTemplateVolumeSecretItemArgs(
                                version="1",  # Pin to version 1
                                path="password",
                            )
                        ],
                    ),
                ),
                gcp.cloudrunv2.ServiceTemplateVolumeArgs(
                    name="neo4j-password",
                    secret=gcp.cloudrunv2.ServiceTemplateVolumeSecretArgs(
                        secret="neo4j-password",
                        default_mode=0o444,  # Read-only
                        items=[
                            gcp.cloudrunv2.ServiceTemplateVolumeSecretItemArgs(
                                version="1",  # Pin to version 1
                                path="password",
                            )
                        ],
                    ),
                ),
            ],
        ),
    )

    # Allow unauthenticated access to API
    gcp.cloudrunv2.ServiceIamMember(
        "api-public-access",
        project=project_id,
        location=region,
        name=api_service.name,
        role="roles/run.invoker",
        member="allUsers",
    )

    return {
        "service": api_service,
        "service_account": api_sa,
        "url": api_service.uri,
    }


def create_cloud_run_worker_service(
    project_id: str,
    region: str,
    network_id: pulumi.Output[str],
    subnet_id: pulumi.Output[str],
    image_uri: str,
    postgres_host: str,
    postgres_db: str,
    neo4j_uri: str,
    redis_host: str,
    qdrant_host: str,
    temporal_host: str = "localhost",  # TODO: Update when Temporal is deployed
) -> Dict[str, Any]:
    """
    Create Cloud Run Worker service for Temporal workflows.

    Args:
        project_id: GCP project ID
        region: GCP region
        network_id: VPC network ID
        subnet_id: VPC subnet ID
        image_uri: Full image URI in Artifact Registry
        postgres_host: PostgreSQL private IP
        postgres_db: PostgreSQL database name
        neo4j_uri: Neo4j bolt URI
        redis_host: Redis private IP
        qdrant_host: Qdrant private IP
        temporal_host: Temporal server host (default: localhost)

    Returns:
        Dictionary containing:
        - service: Cloud Run service resource
        - service_account: Service account for the worker
    """

    # Create service account for worker
    worker_sa = gcp.serviceaccount.Account(
        "worker-service-account",
        account_id=f"apex-worker-{pulumi.get_stack()}",
        display_name="Apex Worker Service Account",
        project=project_id,
    )

    # Grant Secret Manager access to service account
    for secret_name in ["postgres-password", "neo4j-password"]:
        gcp.secretmanager.SecretIamMember(
            f"worker-secret-access-{secret_name}",
            project=project_id,
            secret_id=secret_name,
            role="roles/secretmanager.secretAccessor",
            member=worker_sa.email.apply(lambda email: f"serviceAccount:{email}"),
        )

    # Create Cloud Run Worker service
    worker_service = gcp.cloudrunv2.Service(
        "apex-worker",
        name=f"apex-worker-{pulumi.get_stack()}",
        location=region,
        project=project_id,
        ingress="INGRESS_TRAFFIC_INTERNAL_ONLY",  # Internal access only
        template=gcp.cloudrunv2.ServiceTemplateArgs(
            service_account=worker_sa.email,
            execution_environment="EXECUTION_ENVIRONMENT_GEN2",  # Required for Direct VPC
            scaling=gcp.cloudrunv2.ServiceTemplateScalingArgs(
                min_instance_count=1,  # Always-on for Temporal workflows
                max_instance_count=3,  # Cap at 3 workers for dev
            ),
            vpc_access=gcp.cloudrunv2.ServiceTemplateVpcAccessArgs(
                egress="PRIVATE_RANGES_ONLY",  # Only VPC traffic through Direct VPC
                network_interfaces=[
                    gcp.cloudrunv2.ServiceTemplateVpcAccessNetworkInterfaceArgs(
                        network=network_id,
                        subnetwork=subnet_id,
                    )
                ],
            ),
            containers=[
                gcp.cloudrunv2.ServiceTemplateContainerArgs(
                    image=image_uri,
                    resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                        limits={
                            "cpu": "1",
                            "memory": "1Gi",
                        },
                    ),
                    envs=[
                        # Database connection details
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="POSTGRES_HOST",
                            value=postgres_host,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="POSTGRES_DB",
                            value=postgres_db,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="POSTGRES_USER",
                            value="apex",
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="NEO4J_URI",
                            value=neo4j_uri,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="REDIS_HOST",
                            value=redis_host,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="REDIS_PORT",
                            value="6379",
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="QDRANT_HOST",
                            value=qdrant_host,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="QDRANT_PORT",
                            value="6333",
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="TEMPORAL_HOST",
                            value=temporal_host,
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                            name="TEMPORAL_PORT",
                            value="7233",
                        ),
                    ],
                    volume_mounts=[
                        # Mount secrets as files
                        gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                            name="postgres-password",
                            mount_path="/secrets/postgres",
                        ),
                        gcp.cloudrunv2.ServiceTemplateContainerVolumeMountArgs(
                            name="neo4j-password",
                            mount_path="/secrets/neo4j",
                        ),
                    ],
                )
            ],
            volumes=[
                # Secret Manager volumes
                gcp.cloudrunv2.ServiceTemplateVolumeArgs(
                    name="postgres-password",
                    secret=gcp.cloudrunv2.ServiceTemplateVolumeSecretArgs(
                        secret="postgres-password",
                        default_mode=0o444,  # Read-only
                        items=[
                            gcp.cloudrunv2.ServiceTemplateVolumeSecretItemArgs(
                                version="1",  # Pin to version 1
                                path="password",
                            )
                        ],
                    ),
                ),
                gcp.cloudrunv2.ServiceTemplateVolumeArgs(
                    name="neo4j-password",
                    secret=gcp.cloudrunv2.ServiceTemplateVolumeSecretArgs(
                        secret="neo4j-password",
                        default_mode=0o444,  # Read-only
                        items=[
                            gcp.cloudrunv2.ServiceTemplateVolumeSecretItemArgs(
                                version="1",  # Pin to version 1
                                path="password",
                            )
                        ],
                    ),
                ),
            ],
        ),
    )

    return {
        "service": worker_service,
        "service_account": worker_sa,
    }
