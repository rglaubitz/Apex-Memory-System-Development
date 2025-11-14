# Pulumi Fundamentals: Core Architecture and Concepts

**Source:** Official Pulumi Documentation (pulumi.com/docs)
**Date:** November 2025
**Tier:** Official Documentation (Tier 1)

---

## Table of Contents

1. [What is Pulumi?](#what-is-pulumi)
2. [Core Architecture](#core-architecture)
3. [How Pulumi Works](#how-pulumi-works)
4. [State Management](#state-management)
5. [Resources](#resources)
6. [Inputs and Outputs](#inputs-and-outputs)
7. [Stacks](#stacks)
8. [Secrets Management](#secrets-management)
9. [Python SDK Specifics](#python-sdk-specifics)
10. [CLI Reference](#cli-reference)

---

## What is Pulumi?

Pulumi is a **modern Infrastructure as Code (IaC) platform** that enables you to define and manage cloud infrastructure using familiar programming languages instead of domain-specific languages (DSL) like HCL or YAML.

### Key Characteristics

- **Multi-language support:** TypeScript, JavaScript, Python, Go, C#, Java, and YAML
- **Multi-cloud:** 150+ cloud providers (AWS, Azure, GCP, Kubernetes, etc.)
- **Declarative with imperative power:** Desired state model with full programming language capabilities
- **Open source:** Core engine is Apache 2.0 licensed

### Why Pulumi Over Terraform?

| Feature | Pulumi | Terraform |
|---------|--------|-----------|
| Language | Any programming language | HCL (domain-specific) |
| Logic | Full language features (loops, conditionals, functions) | Limited HCL constructs |
| Type safety | Native IDE support, IntelliSense | Limited |
| Testing | Standard testing frameworks (pytest, jest) | Specialized tools |
| Reusability | Standard package managers (npm, PyPI) | Module registry |

**Source:** https://www.pulumi.com/docs/iac/comparisons/terraform/

---

## Core Architecture

Pulumi's architecture consists of **three primary components** that work together to manage infrastructure:

```
┌─────────────────┐
│  Language Host  │ ← Executes your Python/TS/Go code
└────────┬────────┘
         │ Registers resources
         ↓
┌─────────────────────┐
│ Deployment Engine   │ ← Compares desired vs actual state
└────────┬────────────┘
         │ Calls CRUD operations
         ↓
┌─────────────────────┐
│ Resource Providers  │ ← Manages cloud resources (GCP, AWS, etc.)
└─────────────────────┘
```

### 1. Language Host

- Executes your infrastructure code (Python, TypeScript, etc.)
- Translates resource declarations into resource registration requests
- Sends registrations to the deployment engine
- **Important:** When you instantiate a resource (e.g., `gcp.storage.Bucket()`), it returns **immediately** with a resource object—it does NOT wait for the actual cloud resource to be created

### 2. Deployment Engine

- Receives resource registrations from language host
- Compares desired state (your code) against current state (stored in state file)
- Computes the **diff** (what needs to be created, updated, or deleted)
- Orchestrates resource operations in dependency order
- Manages state file updates
- Provides **transactional checkpointing** for fault tolerance

### 3. Resource Providers

- Implement CRUD operations for specific cloud platforms
- Examples: `pulumi-gcp`, `pulumi-aws`, `pulumi-kubernetes`
- Each provider is a dynamically loaded plugin
- Providers translate Pulumi operations into cloud provider API calls

**Source:** https://www.pulumi.com/docs/iac/concepts/how-pulumi-works/

---

## How Pulumi Works

Pulumi uses a **desired state (declarative) model** with the flexibility of imperative programming languages.

### The Desired State Model

> "When you author a Pulumi program the end result will be the state you declare, regardless of the current state of your infrastructure."

Pulumi ensures your infrastructure matches your code by:

1. **Computing desired state** by running your program
2. **Comparing with current state** stored in the state file
3. **Calculating diff** to determine required changes
4. **Executing operations** to reach desired state

### Execution Flow: `pulumi up`

```
Step 1: Run your program
  ├─ Language host executes Python/TS code
  └─ Resources are registered (NOT created yet)

Step 2: Build resource graph
  ├─ Deployment engine collects all registrations
  ├─ Identifies dependencies (output → input relationships)
  └─ Creates directed acyclic graph (DAG)

Step 3: Compute diff
  ├─ Compare desired state vs current state
  ├─ Identify creates, updates, deletes
  └─ Determine operation order based on dependencies

Step 4: Execute operations
  ├─ Parallel execution where possible
  ├─ Respect dependencies (wait for outputs)
  └─ Call provider CRUD methods

Step 5: Update state
  ├─ Record new resource states
  ├─ Update outputs
  └─ Create checkpoint for recovery
```

### Dependency Management

**Automatic dependency tracking** occurs when:
- Resource outputs become inputs to other resources
- Example: VPC ID (output) → Subnet VPC reference (input)

**Manual dependencies** via `dependsOn` option when:
- Resource A must exist before B, but B doesn't use A's outputs
- Example: IAM role must exist before service deployment

### Update Behavior

**Default: Replace After Create**
```python
# Pulumi creates new resource BEFORE deleting old one
# Enables zero-downtime updates
db = gcp.sql.DatabaseInstance("db", ...)
```

**Alternative: Delete Before Replace**
```python
# Use when resource names must be unique
db = gcp.sql.DatabaseInstance("db",
    opts=pulumi.ResourceOptions(delete_before_replace=True)
)
```

**Source:** https://www.pulumi.com/docs/iac/concepts/how-pulumi-works/

---

## State Management

Pulumi stores **metadata about your infrastructure** in a state file to enable:
- Tracking which resources exist
- Determining what changes are needed
- Preventing concurrent modifications
- Maintaining deployment history

### What's in the State File?

- Resource URNs (Uniform Resource Names)
- Resource types and names
- Input and output values (outputs stored as plain text, except secrets)
- Resource metadata (provider versions, creation time)
- Dependency graph
- Encrypted secrets

### What's NOT in the State File?

**Cloud credentials are NEVER stored in state:**
> "Pulumi state does not include your cloud credentials. Credentials are kept local to your client — wherever the CLI runs."

Credentials remain on your local machine or in your CI/CD environment.

### Backend Options

Pulumi supports two classes of backends:

#### 1. Pulumi Cloud (Managed SaaS)

**Default backend** (`app.pulumi.com`):

**Pros:**
- ✅ Transactional checkpointing with fault tolerance
- ✅ Concurrent locking (prevents team conflicts)
- ✅ Full deployment history and audit trails
- ✅ Encrypted storage (data encrypted at rest and in transit)
- ✅ Role-based access control (RBAC)
- ✅ Managed secret encryption via HSM keys
- ✅ No infrastructure to manage

**Cons:**
- ❌ Requires internet connectivity
- ❌ State stored on Pulumi's infrastructure (though credentials never leave your machine)

**Pricing:**
- Free tier for individuals
- Paid plans for teams and enterprises

**Setup:**
```bash
# Already configured by default
pulumi login
```

#### 2. DIY Backends (Self-Managed)

Store state in your own infrastructure:

| Backend | URI Format | Use Case |
|---------|------------|----------|
| **Local filesystem** | `file://~/.pulumi` | Local development, testing |
| **AWS S3** | `s3://<bucket-name>` | AWS-centric organizations |
| **Azure Blob** | `azblob://<container>` | Azure-centric organizations |
| **Google Cloud Storage** | `gs://<bucket-name>` | **Recommended for Apex Memory System** |
| **S3-compatible** | `s3://<endpoint>/<bucket>` | Minio, Ceph, etc. |

**Setup (GCS example):**
```bash
# Create GCS bucket first
gsutil mb gs://apex-pulumi-state

# Login to DIY backend
pulumi login gs://apex-pulumi-state
```

**DIY Backend State Structure:**

```
.pulumi/
├── meta.yaml              # Backend metadata
├── stacks/
│   ├── dev.json           # Dev stack state
│   ├── staging.json       # Staging stack state
│   └── production.json    # Production stack state
├── locks/                 # Concurrent operation locks
└── history/               # Historical checkpoints
```

**Pros of DIY Backends:**
- ✅ Complete control over storage
- ✅ No external dependencies
- ✅ Works in air-gapped environments
- ✅ Use existing cloud infrastructure

**Cons of DIY Backends:**
- ❌ You manage backups and disaster recovery
- ❌ You implement team collaboration features
- ❌ Limited concurrent locking (basic file locking)
- ❌ No built-in audit trails or deployment history UI

### State Encryption

All backends encrypt secrets in state using configurable encryption providers:

| Provider | Configuration |
|----------|---------------|
| **Pulumi Cloud** | `--secrets-provider="service"` (default) |
| **AWS KMS** | `--secrets-provider="awskms://key-id"` |
| **Azure Key Vault** | `--secrets-provider="azurekeyvault://vault-url/key-name"` |
| **Google Cloud KMS** | `--secrets-provider="gcpkms://projects/PROJECT/locations/LOCATION/keyRings/RING/cryptoKeys/KEY"` |
| **Passphrase** | `--secrets-provider="passphrase"` (DIY backends default) |

**Example:**
```bash
# Initialize stack with GCP KMS encryption
pulumi stack init production \
  --secrets-provider="gcpkms://projects/apex-memory/locations/us-central1/keyRings/pulumi/cryptoKeys/state-encryption"
```

### State Migration

Move stacks between backends using export/import:

```bash
# Export from current backend
pulumi stack export --file stack-state.json

# Login to new backend
pulumi login gs://new-backend-bucket

# Import to new backend
pulumi stack import --file stack-state.json
```

**Source:** https://www.pulumi.com/docs/iac/concepts/state-and-backends/

---

## Resources

Resources are the **fundamental units** of Pulumi infrastructure. Each resource represents a single cloud object (e.g., VM, database, storage bucket).

### Resource Types

Pulumi has two resource subclasses:

#### 1. CustomResource

**Cloud resources managed by providers** (AWS, GCP, Azure, Kubernetes, etc.)

- Has full CRUD lifecycle (Create, Read, Update, Delete)
- Managed by external cloud provider APIs
- Examples: `gcp.storage.Bucket`, `gcp.compute.Instance`, `gcp.sql.DatabaseInstance`

**Example:**
```python
import pulumi_gcp as gcp

# CustomResource - managed by GCP provider
bucket = gcp.storage.Bucket("apex-data",
    location="US",
    force_destroy=True
)
```

#### 2. ComponentResource

**Logical grouping of resources** with no direct cloud representation:

- No CRUD operations (children have CRUD)
- Used for creating reusable infrastructure patterns
- Examples: "Web server with load balancer", "Microservice with database"

**Example:**
```python
class ApexMemoryStack(pulumi.ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__('apex:stack:ApexMemory', name, None, opts)

        # Child resources
        self.vpc = gcp.compute.Network(f"{name}-vpc",
            opts=pulumi.ResourceOptions(parent=self))

        self.database = gcp.sql.DatabaseInstance(f"{name}-db",
            opts=pulumi.ResourceOptions(parent=self))

        # Register outputs
        self.register_outputs({
            "vpc_id": self.vpc.id,
            "db_connection": self.database.connection_name
        })
```

### Resource Naming

**Logical name** (Pulumi name):
```python
bucket = gcp.storage.Bucket("apex-data", ...)
#                            ^^^^^^^^^
#                            Logical name (used in state file)
```

**Physical name** (cloud provider name):
```python
bucket = gcp.storage.Bucket("apex-data",
    name="apex-memory-prod-us-central1-data"
    #    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #    Physical name (actual GCS bucket name)
)
```

**Best practice:** Let Pulumi auto-generate physical names to avoid naming conflicts during updates.

### Resource Options

All resources accept a `pulumi.ResourceOptions` argument:

```python
resource = gcp.storage.Bucket("bucket",
    location="US",
    opts=pulumi.ResourceOptions(
        depends_on=[other_resource],           # Manual dependency
        protect=True,                          # Prevent deletion
        delete_before_replace=True,            # Delete old before creating new
        ignore_changes=["labels"],             # Ignore external changes
        parent=component,                      # Logical parent
        provider=custom_provider,              # Use specific provider instance
        custom_timeouts=pulumi.CustomTimeouts(
            create="10m",
            update="10m",
            delete="30m"
        )
    )
)
```

**Source:** https://www.pulumi.com/docs/iac/concepts/resources/

---

## Inputs and Outputs

Pulumi uses special **Input** and **Output** types to track dependencies and enable declarative infrastructure management.

### Why Inputs and Outputs?

**Problem:** Cloud resources are created asynchronously. When you create a VPC, you don't immediately know its ID—GCP assigns it after creation.

**Solution:** Pulumi wraps values in `Output` types that represent "eventual values" and tracks dependencies automatically.

### Inputs

**Inputs** are values you provide to resources. They accept both plain values and `Output` values:

```python
# All of these are valid inputs
bucket = gcp.storage.Bucket("bucket",
    location="US",                    # Plain string
    force_destroy=True,               # Plain boolean
    labels={"env": "prod"}            # Plain dict
)

# Inputs can also be Outputs from other resources
subnet = gcp.compute.Subnetwork("subnet",
    network=vpc.id,                   # vpc.id is an Output[str]
    ip_cidr_range="10.0.0.0/24"
)
```

### Outputs

**Outputs** represent values that are **only known after resource creation**:

```python
vpc = gcp.compute.Network("vpc", auto_create_subnetworks=False)

# vpc.id is Output[str] - value is unknown until GCP creates the VPC
# vpc.self_link is Output[str]
# vpc.name is Output[str]
```

**Key characteristics:**
- Outputs are **asynchronous** (promises/futures)
- You **cannot directly access** their values (no `print(vpc.id)`)
- They automatically track **dependencies**

### Working with Outputs: `apply()`

To use an Output's value, use the `apply()` method:

```python
vpc = gcp.compute.Network("vpc")

# WRONG - won't work (vpc.id is Output, not string)
# print(f"VPC ID: {vpc.id}")

# CORRECT - use apply()
vpc.id.apply(lambda id: print(f"VPC ID: {id}"))

# apply() can transform values
vpc_url = vpc.self_link.apply(lambda link: f"https://console.cloud.google.com{link}")

# apply() can create new resources
firewall = vpc.id.apply(lambda vpc_id:
    gcp.compute.Firewall("firewall", network=vpc_id, ...)
)
```

### Working with Multiple Outputs: `Output.all()`

Combine multiple Outputs:

```python
# Combine outputs
combined = pulumi.Output.all(vpc.id, subnet.id).apply(
    lambda args: f"VPC: {args[0]}, Subnet: {args[1]}"
)

# Using dictionary unpacking (cleaner)
config_json = pulumi.Output.all(
    vpc_id=vpc.id,
    db_host=database.ip_address,
    bucket_name=bucket.name
).apply(lambda args: json.dumps(args))
```

### Python-Specific Helpers

```python
# JSON serialization
config = pulumi.Output.json_dumps({
    "database": database.connection_name,
    "bucket": bucket.url
})

# Conditional outputs
message = pulumi.Output.all(env, is_prod).apply(
    lambda args: f"Production" if args[1] else f"Development ({args[0]})"
)
```

### Exporting Stack Outputs

Make values available outside the stack:

```python
# In __main__.py
import pulumi

vpc = gcp.compute.Network("vpc")
database = gcp.sql.DatabaseInstance("db")

# Export values (accessible via pulumi stack output)
pulumi.export("vpc_id", vpc.id)
pulumi.export("vpc_self_link", vpc.self_link)
pulumi.export("db_connection_name", database.connection_name)
```

```bash
# Access outputs from CLI
pulumi stack output vpc_id
pulumi stack output db_connection_name

# Get all outputs as JSON
pulumi stack output --json
```

### Dependency Tracking

**Automatic dependencies:**
```python
vpc = gcp.compute.Network("vpc")
subnet = gcp.compute.Subnetwork("subnet",
    network=vpc.id  # Output → Input = automatic dependency
)
# Pulumi knows: create VPC before subnet
```

**Manual dependencies:**
```python
role = gcp.projects.IAMBinding("role", ...)
service = gcp.cloudrun.Service("api",
    opts=pulumi.ResourceOptions(depends_on=[role])
)
# Service waits for role, even though it doesn't use role's outputs
```

**Source:** https://www.pulumi.com/docs/iac/concepts/inputs-outputs/

---

## Stacks

A **stack** is an isolated, independently configurable instance of a Pulumi program.

### What is a Stack?

Think of stacks as **environments** or **deployment instances**:

- Each stack has its own state file
- Each stack has its own configuration
- One Pulumi program → Multiple stacks
- Common pattern: `dev`, `staging`, `production` stacks

### Stack Structure

```
project-name/
├── Pulumi.yaml           # Project metadata
├── __main__.py           # Pulumi program (shared across stacks)
├── Pulumi.dev.yaml       # Dev stack config
├── Pulumi.staging.yaml   # Staging stack config
└── Pulumi.prod.yaml      # Production stack config
```

### Stack Lifecycle

#### Creating a Stack

```bash
# Create new stack
pulumi stack init dev

# Stack naming format
pulumi stack init [<organization>/]<project-name>/<stack-name>

# Examples
pulumi stack init dev
pulumi stack init acme-corp/apex-memory/production
```

#### Listing Stacks

```bash
pulumi stack ls

# Output
NAME          LAST UPDATE       RESOURCE COUNT  URL
dev*          5 minutes ago     12              https://app.pulumi.com/.../dev
staging       2 hours ago       12              https://app.pulumi.com/.../staging
production    1 day ago         15              https://app.pulumi.com/.../production

# * indicates active stack
```

#### Selecting a Stack

```bash
# Switch to a different stack
pulumi stack select staging

# All subsequent pulumi commands operate on selected stack
pulumi preview
pulumi up
pulumi destroy
```

#### Removing a Stack

```bash
# First, destroy all resources
pulumi destroy

# Then remove the stack (and its state)
pulumi stack rm dev

# Force removal (leaves resources orphaned - dangerous!)
pulumi stack rm dev --force
```

### Stack Configuration

Each stack has **independent configuration** stored in `Pulumi.<stack-name>.yaml`:

```bash
# Set configuration values
pulumi config set gcp:project apex-memory-dev
pulumi config set gcp:region us-central1
pulumi config set instanceSize small

# Set secrets (encrypted in config file)
pulumi config set dbPassword S3cr3t! --secret

# Get configuration values
pulumi config get gcp:project
pulumi config get dbPassword  # Shows encrypted value

# List all config
pulumi config
```

**Example `Pulumi.dev.yaml`:**
```yaml
config:
  gcp:project: apex-memory-dev
  gcp:region: us-central1
  apex-memory:instanceSize: small
  apex-memory:dbPassword:
    secure: AAABADpUlGlMJ...  # Encrypted secret
```

### Using Configuration in Code

```python
import pulumi

# Get configuration
config = pulumi.Config()

# Get required values
instance_size = config.require("instanceSize")  # Throws if not set

# Get optional values with defaults
region = config.get("region") or "us-central1"

# Get integers/booleans
replica_count = config.get_int("replicaCount") or 1
enable_backup = config.get_bool("enableBackup") or False

# Get secrets (automatically decrypted)
db_password = config.require_secret("dbPassword")

# Get GCP provider config
gcp_config = pulumi.Config("gcp")
project_id = gcp_config.require("project")
```

### Stack References

Access outputs from **other stacks**:

```python
# In production stack, reference shared-infrastructure stack
infra_stack = pulumi.StackReference("acme-corp/shared-infrastructure/production")

# Use outputs from that stack
vpc_id = infra_stack.get_output("vpc_id")
subnet_id = infra_stack.get_output("subnet_id")

# Use in resources
service = gcp.cloudrun.Service("api",
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            containers=[...],
        ),
        metadata=gcp.cloudrun.ServiceTemplateMetadataArgs(
            annotations={
                "run.googleapis.com/vpc-access-connector": infra_stack.get_output("vpc_connector")
            }
        )
    )
)
```

### Stack Tagging

Organize stacks with tags:

```bash
# Add tags to stack
pulumi stack tag set environment production
pulumi stack tag set team backend
pulumi stack tag set cost-center engineering

# List tags
pulumi stack tag ls

# Remove tag
pulumi stack tag rm team
```

**Source:** https://www.pulumi.com/docs/iac/concepts/stacks/

---

## Secrets Management

Pulumi encrypts sensitive configuration data to prevent exposure in state files.

### Why Secrets Management?

**Problem:** State files contain all resource configuration. Without encryption, passwords, API keys, and tokens would be visible in plain text.

**Solution:** Pulumi encrypts secrets in:
- Configuration files (`Pulumi.<stack>.yaml`)
- State files (stored in backend)

### Creating Secrets

#### CLI Method

```bash
# Set secret configuration value
pulumi config set dbPassword MyS3cr3t! --secret

# Stored encrypted in Pulumi.<stack>.yaml
# config:
#   apex-memory:dbPassword:
#     secure: AAABADpUlGlMJ8Rz...
```

#### Programmatic Method

```python
import pulumi

# Method 1: Read from config (marked as secret)
config = pulumi.Config()
db_password = config.require_secret("dbPassword")

# Method 2: Wrap any value as secret
api_key = pulumi.secret("sk-1234567890abcdef")

# Use in resources
database = gcp.sql.DatabaseInstance("db",
    root_password=db_password  # Encrypted in state
)
```

### Secret Transitive Tracking

**Secrets propagate automatically:**

```python
# db_password is a secret
db_password = config.require_secret("dbPassword")

# database.root_password is automatically a secret (inherited)
database = gcp.sql.DatabaseInstance("db", root_password=db_password)

# connection_string is automatically a secret (derived from secret)
connection_string = pulumi.Output.all(
    database.ip_address,
    db_password
).apply(lambda args: f"postgresql://user:{args[1]}@{args[0]}/db")

# Export as secret (shown as "[secret]" in CLI)
pulumi.export("db_connection", connection_string)
```

### Encryption Providers

Pulumi supports multiple encryption backends:

#### 1. Pulumi Cloud (Default)

```bash
# Uses Pulumi's managed encryption (HSM-backed)
pulumi stack init production --secrets-provider="service"
```

**Pros:**
- Managed service (no setup)
- Hardware Security Module (HSM) backed
- No key management

**Cons:**
- Requires Pulumi Cloud
- Less control over keys

#### 2. AWS KMS

```bash
pulumi stack init production \
  --secrets-provider="awskms://arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
```

**Pros:**
- Use existing AWS KMS infrastructure
- Full control over keys
- Works with DIY backends

#### 3. Azure Key Vault

```bash
pulumi stack init production \
  --secrets-provider="azurekeyvault://mykeyvault.vault.azure.net/keys/pulumi-secrets"
```

#### 4. Google Cloud KMS

```bash
pulumi stack init production \
  --secrets-provider="gcpkms://projects/apex-memory/locations/us-central1/keyRings/pulumi/cryptoKeys/state-secrets"
```

**Recommended for Apex Memory System** (GCP-native):

```bash
# Create KMS key ring (one-time setup)
gcloud kms keyrings create pulumi \
  --location us-central1 \
  --project apex-memory

# Create encryption key (one-time setup)
gcloud kms keys create state-secrets \
  --keyring pulumi \
  --location us-central1 \
  --purpose encryption \
  --project apex-memory

# Create stack with GCP KMS encryption
pulumi stack init production \
  --secrets-provider="gcpkms://projects/apex-memory/locations/us-central1/keyRings/pulumi/cryptoKeys/state-secrets"
```

#### 5. Passphrase (DIY Backends Default)

```bash
# Uses passphrase-based encryption
pulumi stack init production --secrets-provider="passphrase"

# You'll be prompted for passphrase
# IMPORTANT: Do not lose this passphrase - cannot be recovered!
```

### Pulumi ESC (Environments, Secrets, and Configuration)

**Modern approach:** Centralized secret management across teams and stacks.

**Features:**
- Cross-cloud support (AWS Secrets Manager, Azure KeyVault, GCP Secret Manager)
- RBAC controls
- Dynamic credentials (time-bound tokens via OIDC)
- Environment inheritance
- Secret versioning

**Example:**
```yaml
# environments/production.yaml
values:
  gcp:
    login:
      fn::open::gcp-login:
        project: apex-memory
        oidc:
          workloadPoolId: pulumi-oidc
          providerId: pulumi
          serviceAccount: pulumi-production@apex-memory.iam.gserviceaccount.com

  secrets:
    fn::open::gcp-secrets:
      access:
        - projects/apex-memory/secrets/db-password/versions/latest

  databasePassword:
    fn::secret: ${secrets.db-password}
```

**Usage in Pulumi:**
```python
# Import environment
import pulumi_esc as esc

env = esc.Environment("production")
db_password = env.require_secret("databasePassword")
```

### Best Practices

1. **Always use `--secret` flag for sensitive data:**
   ```bash
   pulumi config set apiKey xyz --secret  # ✅
   pulumi config set apiKey xyz           # ❌ Plain text!
   ```

2. **Never log or export decrypted secrets:**
   ```python
   # ❌ BAD - exposes secret
   db_password.apply(lambda pwd: print(f"Password: {pwd}"))

   # ✅ GOOD - keeps secret encrypted
   pulumi.export("db_password_set", db_password.apply(lambda _: True))
   ```

3. **Use apply() carefully with secrets:**
   ```python
   # ❌ BAD - could expose secret in error messages
   url = db_password.apply(lambda pwd: requests.get(f"http://api.com?key={pwd}"))

   # ✅ GOOD - secret never leaves trusted code
   url = db_password.apply(lambda pwd: create_signed_url(pwd))
   ```

4. **Check configuration files into source control:**
   ```bash
   # Safe to commit (secrets are encrypted)
   git add Pulumi.*.yaml
   git commit -m "Add production config"
   ```

5. **Use GCP Secret Manager for runtime secrets:**
   ```python
   # Store Pulumi config secrets in GCP Secret Manager
   # Then reference them in application code at runtime
   secret = gcp.secretmanager.Secret("db-password",
       secret_id="apex-db-password",
       replication=gcp.secretmanager.SecretReplicationArgs(
           automatic=gcp.secretmanager.SecretReplicationAutomaticArgs()
       )
   )

   secret_version = gcp.secretmanager.SecretVersion("db-password-v1",
       secret=secret.id,
       secret_data=db_password  # Pulumi secret → GCP Secret Manager
   )
   ```

**Source:** https://www.pulumi.com/docs/iac/concepts/secrets/

---

## Python SDK Specifics

Pulumi's Python SDK provides idiomatic Python patterns for infrastructure as code.

### Installation

```bash
# Install Pulumi CLI (macOS)
brew install pulumi

# Create new Python project
mkdir apex-memory-infra && cd apex-memory-infra
pulumi new gcp-python

# This creates:
# - Pulumi.yaml (project metadata)
# - __main__.py (main program)
# - requirements.txt (Python dependencies)
# - venv/ (virtual environment)
```

### Dependency Management

Pulumi supports **three Python package managers**:

#### 1. pip (Default)

```bash
# Pulumi creates venv and installs from requirements.txt
pulumi up

# Manual installation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure venv directory:**
```yaml
# Pulumi.yaml
runtime:
  name: python
  options:
    virtualenv: venv
```

#### 2. Poetry (Recommended for production)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Pulumi uses pyproject.toml
pulumi up  # Automatically invokes poetry
```

**Requirements:**
- Poetry 1.8.0+
- `pyproject.toml` in project root

**Pulumi auto-converts `requirements.txt` → `pyproject.toml` if needed**

#### 3. uv (Fastest)

```bash
# Install uv
pip install uv

# Pulumi uses pyproject.toml
pulumi up
```

**Configuration:**
```yaml
# Pulumi.yaml
runtime:
  name: python
  options:
    toolchain: uv
    virtualenv: .venv
```

### Type Safety

**Pulumi Python SDK supports type checking** (as of v3.113.0):

```yaml
# Pulumi.yaml
runtime:
  name: python
  options:
    typechecker: mypy  # or pyright
```

**Automatic type checking before `pulumi up`:**
```bash
pulumi up
# Runs mypy first
# If type errors found, deployment is blocked
```

**Benefits:**
- Catch errors before deployment
- IDE autocomplete (IntelliSense)
- Better refactoring support

### Async/Await Patterns

Pulumi's Python runtime is **single-threaded with an internal event loop**:

```python
# ✅ You can use async/await
async def create_resources():
    bucket = gcp.storage.Bucket("data")
    return bucket

# ✅ Pulumi handles the event loop
resources = await create_resources()

# ❌ Don't create your own event loop
# asyncio.run(create_resources())  # Will conflict with Pulumi's loop
```

**Recommended pattern:**
```python
import pulumi
import pulumi_gcp as gcp

# Standard synchronous code (most common)
vpc = gcp.compute.Network("vpc")
subnet = gcp.compute.Subnetwork("subnet", network=vpc.id)

# Use apply() for transformations (not async/await)
vpc_url = vpc.self_link.apply(lambda link: f"https://console.cloud.google.com{link}")
```

### Input Type Patterns

Pulumi Python resources accept inputs as **classes or dictionaries**:

#### Class-based (TypedDict approach)

```python
from pulumi_gcp import storage

bucket = storage.Bucket("data",
    location="US",
    force_destroy=True,
    versioning=storage.BucketVersioningArgs(
        enabled=True
    ),
    lifecycle_rules=[
        storage.BucketLifecycleRuleArgs(
            action=storage.BucketLifecycleRuleActionArgs(
                type="Delete"
            ),
            condition=storage.BucketLifecycleRuleConditionArgs(
                age=90
            )
        )
    ]
)
```

#### Dictionary-based (more concise)

```python
bucket = storage.Bucket("data",
    location="US",
    force_destroy=True,
    versioning={"enabled": True},
    lifecycle_rules=[{
        "action": {"type": "Delete"},
        "condition": {"age": 90}
    }]
)
```

**Both are equivalent and type-safe** (with modern providers).

### Common Patterns

#### Reading Configuration

```python
import pulumi

config = pulumi.Config()

# Required values (throw if missing)
project_id = config.require("gcp:project")
region = config.require("gcp:region")

# Optional values with defaults
instance_type = config.get("instanceType") or "e2-small"

# Typed values
replica_count = config.get_int("replicaCount") or 3
enable_ha = config.get_bool("enableHA") or False

# Secrets (automatically decrypted)
db_password = config.require_secret("dbPassword")
```

#### Exporting Outputs

```python
import pulumi

vpc = gcp.compute.Network("vpc")
database = gcp.sql.DatabaseInstance("db")

# Export single values
pulumi.export("vpc_id", vpc.id)
pulumi.export("vpc_name", vpc.name)

# Export complex objects
pulumi.export("database_info", {
    "connection_name": database.connection_name,
    "ip_address": database.ip_address.get("0").ip_address,
    "region": database.region
})

# Export transformed outputs
pulumi.export("db_url", pulumi.Output.all(
    database.ip_address,
    config.require_secret("dbPassword")
).apply(lambda args: f"postgresql://user:{args[1]}@{args[0][0].ip_address}/db"))
```

#### Component Resources

```python
from typing import Optional
import pulumi
import pulumi_gcp as gcp

class DatabaseStack(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 tier: str = "db-f1-micro",
                 opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__('apex:database:Stack', name, None, opts)

        # Create resources as children
        self.instance = gcp.sql.DatabaseInstance(f"{name}-instance",
            database_version="POSTGRES_15",
            tier=tier,
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.database = gcp.sql.Database(f"{name}-db",
            instance=self.instance.name,
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Register outputs
        self.register_outputs({
            "instance_name": self.instance.name,
            "connection_name": self.instance.connection_name
        })

# Usage
db_stack = DatabaseStack("apex-memory", tier="db-g1-small")
pulumi.export("db_connection", db_stack.instance.connection_name)
```

### Package References

| Package | Purpose | Installation |
|---------|---------|--------------|
| `pulumi` | Core SDK | `pip install pulumi` |
| `pulumi-gcp` | GCP provider | `pip install pulumi-gcp` |
| `pulumi-policy` | Policy as Code | `pip install pulumi-policy` |
| `pulumi-esc` | ESC integration | `pip install pulumi-esc` |

**Pre-release versions:**
```bash
pip install --pre pulumi-gcp  # Latest development version
```

**Source:** https://www.pulumi.com/docs/iac/languages-sdks/python/

---

## CLI Reference

Pulumi CLI provides comprehensive infrastructure management commands.

### Core Workflow Commands

#### `pulumi up`

**Create or update resources in a stack**

```bash
# Preview and prompt for approval
pulumi up

# Auto-approve (CI/CD)
pulumi up --yes

# Specify stack
pulumi up --stack production

# Use different project directory
pulumi up --cwd /path/to/project

# Set config inline
pulumi up --config gcp:project=apex-memory

# Refresh state before update
pulumi up --refresh

# Target specific resources
pulumi up --target urn:pulumi:prod::apex::gcp:storage/bucket:Bucket::data

# Parallel execution (default: 10)
pulumi up --parallel 20

# Show detailed diff
pulumi up --diff

# Skip preview (dangerous!)
pulumi up --skip-preview --yes
```

**Output:**
```
Previewing update (dev)

     Type                         Name                 Plan
 +   pulumi:pulumi:Stack          apex-memory-dev      create
 +   ├─ gcp:compute:Network       vpc                  create
 +   ├─ gcp:compute:Subnetwork    subnet               create
 +   └─ gcp:sql:DatabaseInstance  database             create

Resources:
    + 4 to create

Do you want to perform this update? yes
Updating (dev)

     Type                         Name                 Status
 +   pulumi:pulumi:Stack          apex-memory-dev      created
 +   ├─ gcp:compute:Network       vpc                  created
 +   ├─ gcp:compute:Subnetwork    subnet               created
 +   └─ gcp:sql:DatabaseInstance  database             created

Outputs:
    vpc_id: "projects/apex-memory/global/networks/vpc-12345"

Resources:
    + 4 created

Duration: 3m45s
```

#### `pulumi preview`

**Show preview of updates without applying changes**

```bash
# Show what would change
pulumi preview

# Show detailed diff
pulumi preview --diff

# JSON output (for CI/CD)
pulumi preview --json

# Refresh state first
pulumi preview --refresh

# Non-interactive mode
pulumi preview --non-interactive
```

**Use cases:**
- CI/CD pipeline checks
- Review changes before approval
- Debugging deployment issues

#### `pulumi destroy`

**Delete all resources in a stack**

```bash
# Preview and prompt
pulumi destroy

# Auto-approve (dangerous!)
pulumi destroy --yes

# Target specific resources
pulumi destroy --target urn:pulumi:dev::apex::gcp:storage/bucket:Bucket::temp-data

# Skip protected resources
pulumi destroy --exclude-protected

# Continue despite errors
pulumi destroy --continue-on-error

# Remove stack after destroying
pulumi destroy --remove
```

**⚠️ WARNING:** `pulumi destroy` deletes all resources. Always run `pulumi preview --destroy` first in production!

#### `pulumi refresh`

**Update state file to match actual cloud resources**

```bash
# Refresh current stack
pulumi refresh

# Auto-approve refresh
pulumi refresh --yes

# Show expected changes
pulumi refresh --expect-no-changes

# Non-interactive
pulumi refresh --non-interactive
```

**Use cases:**
- Detect manual changes to resources
- Reconcile state after out-of-band modifications
- Update state after provider API changes

### Stack Management

#### `pulumi stack init`

```bash
# Create new stack
pulumi stack init dev

# With organization
pulumi stack init acme-corp/apex-memory/production

# With custom secrets provider
pulumi stack init production \
  --secrets-provider="gcpkms://projects/apex/locations/us-central1/keyRings/pulumi/cryptoKeys/secrets"

# Copy configuration from existing stack
pulumi stack init staging --copy-config-from dev
```

#### `pulumi stack ls`

```bash
# List all stacks
pulumi stack ls

# JSON output
pulumi stack ls --json

# Show all metadata
pulumi stack ls --all
```

#### `pulumi stack select`

```bash
# Switch to stack
pulumi stack select production

# Create if doesn't exist
pulumi stack select staging --create
```

#### `pulumi stack output`

```bash
# Show all outputs
pulumi stack output

# Show specific output
pulumi stack output vpc_id

# JSON format
pulumi stack output --json

# Show secrets (decrypted)
pulumi stack output db_password --show-secrets
```

#### `pulumi stack rm`

```bash
# Remove stack (after destroying resources)
pulumi stack rm dev

# Force remove (leaves resources orphaned - dangerous!)
pulumi stack rm dev --force

# Preserve config file
pulumi stack rm dev --preserve-config

# Remove backups (DIY backends)
pulumi stack rm dev --remove-backups
```

### Configuration Management

#### `pulumi config set`

```bash
# Set plain value
pulumi config set gcp:project apex-memory

# Set secret (encrypted)
pulumi config set dbPassword S3cr3t! --secret

# Set JSON object
pulumi config set --path 'dbConfig.host' localhost
pulumi config set --path 'dbConfig.port' 5432

# Set from file
pulumi config set sslCert --path ./cert.pem
```

#### `pulumi config get`

```bash
# Get value
pulumi config get gcp:project

# Show all config
pulumi config

# Show secrets (decrypted)
pulumi config get dbPassword --show-secrets

# JSON output
pulumi config --json
```

#### `pulumi config rm`

```bash
# Remove config value
pulumi config rm instanceType
```

### State Management

#### `pulumi state export`

```bash
# Export state to file
pulumi state export --file state.json

# Export from specific stack
pulumi state export --stack production --file prod-state.json
```

#### `pulumi state import`

```bash
# Import state from file
pulumi state import --file state.json

# Force import (overwrite conflicts)
pulumi state import --file state.json --force
```

#### `pulumi state delete`

```bash
# Remove resource from state (without deleting resource)
pulumi state delete 'urn:pulumi:dev::apex::gcp:storage/bucket:Bucket::old-bucket'

# Dangerous! Only use when resource no longer exists
```

### Import Existing Resources

```bash
# Import existing GCP resource into Pulumi
pulumi import gcp:storage/bucket:Bucket data-bucket apex-memory-data-us-central1

# General syntax
pulumi import <resource-type> <pulumi-name> <cloud-resource-id>
```

### Diagnostic Commands

#### `pulumi whoami`

```bash
# Show current user
pulumi whoami

# Show current backend
pulumi whoami --backends

# JSON output
pulumi whoami --json
```

#### `pulumi about`

```bash
# Show version and environment info
pulumi about

# Includes:
# - Pulumi CLI version
# - Backend URL
# - Runtime versions (Python, Node, etc.)
# - Installed plugins
```

#### `pulumi plugin ls`

```bash
# List installed providers
pulumi plugin ls

# Output:
# NAME     KIND      VERSION  SIZE
# gcp      resource  7.38.0   234 MB
# random   resource  4.16.3   21 MB
```

#### `pulumi login`

```bash
# Login to Pulumi Cloud
pulumi login

# Login to self-managed backend
pulumi login gs://apex-pulumi-state

# Login with access token
pulumi login --cloud-url https://api.pulumi.com
```

#### `pulumi logout`

```bash
# Logout from current backend
pulumi logout

# Logout from all backends
pulumi logout --all
```

### Advanced Commands

#### `pulumi cancel`

```bash
# Cancel current update
pulumi cancel

# Force cancel
pulumi cancel --yes
```

#### `pulumi history`

```bash
# Show deployment history
pulumi history

# Show full details
pulumi history --full-dates

# Show specific number of entries
pulumi history --show-secrets 10
```

#### `pulumi logs`

```bash
# Stream logs from cloud resources
pulumi logs

# Follow logs in real-time
pulumi logs --follow

# Since specific time
pulumi logs --since 2h

# Filter by resource
pulumi logs --resource urn:pulumi:prod::apex::gcp:cloudrun/service:Service::api
```

**Source:** https://www.pulumi.com/docs/iac/cli/commands/

---

## Quick Reference Card

### Essential Commands

```bash
# Initialize new project
pulumi new gcp-python

# Create stack
pulumi stack init dev

# Configure GCP
pulumi config set gcp:project apex-memory-dev
pulumi config set gcp:region us-central1

# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up

# View outputs
pulumi stack output

# Destroy resources
pulumi destroy

# Remove stack
pulumi stack rm dev
```

### Key Concepts Summary

| Concept | Description | Example |
|---------|-------------|---------|
| **Resource** | Cloud infrastructure unit | `gcp.storage.Bucket()` |
| **Stack** | Deployment instance | `dev`, `staging`, `prod` |
| **State** | Current infrastructure state | Stored in backend |
| **Input** | Value provided to resource | `location="US"` |
| **Output** | Value known after creation | `bucket.url` |
| **Config** | Stack-specific settings | `pulumi config set` |
| **Secret** | Encrypted configuration | `--secret` flag |
| **Backend** | State storage location | Pulumi Cloud or GCS |

### Python Code Template

```python
import pulumi
import pulumi_gcp as gcp

# Configuration
config = pulumi.Config()
project = config.require("gcp:project")
region = config.require("gcp:region")

# Resources
vpc = gcp.compute.Network("vpc",
    auto_create_subnetworks=False
)

subnet = gcp.compute.Subnetwork("subnet",
    network=vpc.id,
    ip_cidr_range="10.0.0.0/24",
    region=region
)

# Exports
pulumi.export("vpc_id", vpc.id)
pulumi.export("subnet_id", subnet.id)
```

---

## Best Practices Summary

1. **Use one Pulumi program, multiple stacks** for environment management
2. **Store state in GCS** for GCP-based projects (self-managed backend)
3. **Use GCP KMS for secrets encryption** (GCP-native approach)
4. **Always use `--secret` flag** for sensitive configuration
5. **Run `pulumi preview`** before every `pulumi up` in production
6. **Use stack references** to share infrastructure across projects
7. **Enable type checking** (`typechecker: mypy` in Pulumi.yaml)
8. **Let Pulumi auto-generate physical names** to avoid conflicts
9. **Use component resources** for reusable infrastructure patterns
10. **Export outputs** for cross-stack references and operational visibility

---

## Next Steps

- Read **[PULUMI-GCP-GUIDE.md](./PULUMI-GCP-GUIDE.md)** for GCP-specific patterns and examples
- Review [Official Pulumi Documentation](https://www.pulumi.com/docs/)
- Explore [Pulumi GCP Provider Registry](https://www.pulumi.com/registry/packages/gcp/)
- Check [Pulumi Examples Repository](https://github.com/pulumi/examples) for working code samples

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Maintained By:** research-coordinator (documentation-hunter agent)
