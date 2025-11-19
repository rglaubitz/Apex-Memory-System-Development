"""
VPC Networking Module for Apex Memory System

Creates GCP networking infrastructure:
- VPC network with custom subnet
- Private Google Access enabled
- VPC connector for Cloud Run
- Cloud NAT for outbound internet access
- Private service connection for Cloud SQL

Research: deployment/pulumi/research/PULUMI-GCP-GUIDE.md (lines 450-550)
"""

import pulumi
import pulumi_gcp as gcp
from typing import Dict, Any


def create_vpc_network(project_id: str, region: str) -> Dict[str, Any]:
    """
    Create VPC network infrastructure for Apex Memory System.

    Args:
        project_id: GCP project ID
        region: GCP region (e.g., 'us-central1')

    Returns:
        Dictionary containing VPC resources:
        - vpc: The VPC network
        - subnet: The private subnet
        - vpc_connector: VPC connector for Cloud Run
        - router: Cloud Router for NAT
        - nat: Cloud NAT configuration
        - private_connection: Private service connection for Cloud SQL
    """

    # Create VPC network (no auto-created subnets for better control)
    vpc = gcp.compute.Network(
        "apex-memory-vpc",
        auto_create_subnetworks=False,
        project=project_id,
        opts=pulumi.ResourceOptions(
            protect=False,  # Allow deletion in dev
        ),
    )

    # Create private subnet for databases and services
    subnet = gcp.compute.Subnetwork(
        "apex-db-subnet",
        ip_cidr_range="10.0.0.0/24",
        region=region,
        network=vpc.id,
        private_ip_google_access=True,  # Enables access to Google APIs
        project=project_id,
    )

    # Create VPC connector for Cloud Run to access VPC resources
    vpc_connector = gcp.vpcaccess.Connector(
        "apex-vpc-connector",
        name="apex-vpc-connector",
        region=region,
        network=vpc.name,
        ip_cidr_range="10.8.0.0/28",  # Connector uses separate CIDR
        machine_type="e2-micro",  # Smallest machine type
        min_instances=2,  # HA requirement
        max_instances=3,  # Auto-scale under load
        project=project_id,
    )

    # Create Cloud Router for NAT
    router = gcp.compute.Router(
        "apex-router",
        region=region,
        network=vpc.id,
        project=project_id,
    )

    # Create Cloud NAT for outbound internet access
    nat = gcp.compute.RouterNat(
        "apex-nat",
        router=router.name,
        region=region,
        nat_ip_allocate_option="AUTO_ONLY",
        source_subnetwork_ip_ranges_to_nat="ALL_SUBNETWORKS_ALL_IP_RANGES",
        project=project_id,
    )

    # Reserve IP range for private service connection (Cloud SQL)
    private_ip_address = gcp.compute.GlobalAddress(
        "apex-private-ip",
        purpose="VPC_PEERING",
        address_type="INTERNAL",
        prefix_length=24,
        network=vpc.id,
        project=project_id,
    )

    # Create private service connection for Cloud SQL
    private_connection = gcp.servicenetworking.Connection(
        "apex-private-connection",
        network=vpc.id,
        service="servicenetworking.googleapis.com",
        reserved_peering_ranges=[private_ip_address.name],
        opts=pulumi.ResourceOptions(
            depends_on=[private_ip_address],
        ),
    )

    # Export outputs for use in other modules
    pulumi.export("vpc_name", vpc.name)
    pulumi.export("vpc_id", vpc.id)
    pulumi.export("subnet_name", subnet.name)
    pulumi.export("subnet_id", subnet.id)
    pulumi.export("vpc_connector_name", vpc_connector.name)
    pulumi.export("vpc_connector_id", vpc_connector.id)

    return {
        "vpc": vpc,
        "subnet": subnet,
        "vpc_connector": vpc_connector,
        "router": router,
        "nat": nat,
        "private_connection": private_connection,
        "private_ip_address": private_ip_address,
    }
