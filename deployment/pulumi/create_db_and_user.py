#!/usr/bin/env python3
"""
Manual database and user creation for apex-postgres-dev instance.

This script creates the database and user that would normally be created by Pulumi,
but is being run manually due to Pulumi state synchronization issues.
"""

import subprocess
import sys
import json


def get_postgres_password():
    """Get the PostgreSQL password from Pulumi secrets."""
    try:
        result = subprocess.run(
            ["pulumi", "stack", "output", "postgres_password", "--show-secrets"],
            capture_output=True,
            text=True,
            check=True,
        )
        # If password doesn't exist yet, use the one from the state
        if "does not have output" in result.stderr:
            # Get from random password resource
            result = subprocess.run(
                ["pulumi", "stack", "export"],
                capture_output=True,
                text=True,
                check=True,
            )
            state = json.loads(result.stdout)
            # Find the random password resource
            for resource in state.get("deployment", {}).get("resources", []):
                if resource.get("type") == "random:index/randomPassword:RandomPassword":
                    return resource.get("outputs", {}).get("result")

            # If not found, generate new one
            print("Warning: Could not find password in state, will need to set manually")
            return None

        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting password: {e}")
        print(f"stderr: {e.stderr}")
        return None


def create_database_and_user():
    """Create the database and user using gcloud SQL commands."""

    project_id = "apex-memory-dev"
    instance_name = "apex-postgres-dev"
    database_name = "apex_memory"
    user_name = "apex"

    print("Getting PostgreSQL password from Pulumi state...")
    password = get_postgres_password()

    if not password:
        print("\nERROR: Could not retrieve password from Pulumi state.")
        print("\nManual steps required:")
        print(f"1. Get password: pulumi stack export | jq '.deployment.resources[] | select(.type==\"random:index/randomPassword:RandomPassword\") | .outputs.result'")
        print(f"2. Create database: gcloud sql databases create {database_name} --instance={instance_name} --project={project_id}")
        print(f"3. Create user: gcloud sql users create {user_name} --instance={instance_name} --password=PASSWORD --project={project_id}")
        return False

    print(f"✓ Found password (length: {len(password)} chars)")

    # Create database
    print(f"\nCreating database '{database_name}'...")
    try:
        result = subprocess.run(
            [
                "gcloud", "sql", "databases", "create", database_name,
                "--instance", instance_name,
                "--project", project_id,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print(f"✓ Database '{database_name}' created successfully")
        elif "already exists" in result.stderr:
            print(f"✓ Database '{database_name}' already exists")
        else:
            print(f"✗ Failed to create database: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

    # Create user
    print(f"\nCreating user '{user_name}'...")
    try:
        result = subprocess.run(
            [
                "gcloud", "sql", "users", "create", user_name,
                "--instance", instance_name,
                "--password", password,
                "--project", project_id,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print(f"✓ User '{user_name}' created successfully")
        elif "already exists" in result.stderr:
            print(f"✓ User '{user_name}' already exists")
        else:
            print(f"✗ Failed to create user: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return False

    print("\n" + "="*60)
    print("✓ Database and user setup complete!")
    print("="*60)
    print(f"\nConnection details:")
    print(f"  Instance: {instance_name}")
    print(f"  Database: {database_name}")
    print(f"  User: {user_name}")
    print(f"  Password: (stored in Pulumi secrets)")
    print(f"\nTo view password: pulumi stack output postgres_password --show-secrets")

    return True


if __name__ == "__main__":
    success = create_database_and_user()
    sys.exit(0 if success else 1)
