# Pulumi Production Best Practices

**Comprehensive guide for production-grade Pulumi deployments on GCP**

**Last Updated:** November 8, 2025
**Target Deployment:** Multi-database, multi-service GCP infrastructure (Apex Memory System)

---

## Table of Contents

1. [Project Organization](#1-project-organization)
2. [Module Design](#2-module-design)
3. [State Management](#3-state-management)
4. [Security](#4-security)
5. [Testing](#5-testing)
6. [Deployment Patterns](#6-deployment-patterns)
7. [Cost Optimization](#7-cost-optimization)
8. [Performance & Reliability](#8-performance--reliability)
9. [Common Anti-Patterns](#9-common-anti-patterns)

---

## 1. Project Organization

### 1.1 Monorepo vs Multi-Repo Decision Tree

**Use Monorepo when:**
- ✅ Single team owns all infrastructure
- ✅ Resources share lifecycle (deploy/update together)
- ✅ Need tight version control across projects
- ✅ Starting small, optimizing for simplicity

**Use Multi-Repo when:**
- ✅ Multiple teams with different ownership
- ✅ Services deploy at different cadences
- ✅ Need granular RBAC per service
- ✅ Large-scale org (100+ engineers)

**Recommended:** Monorepo with multiple Pulumi projects (best of both worlds)

### 1.2 Project Structure: Micro-Stacks Pattern

**DO:** Separate infrastructure by lifecycle and ownership

```
pulumi/
├── infrastructure/              # Base networking (VPC, subnets)
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.staging.yaml
│   ├── Pulumi.prod.yaml
│   └── index.ts
│
├── databases/                   # Database clusters (Neo4j, PostgreSQL, etc.)
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.prod.yaml
│   └── index.ts
│
├── services/                    # Application services (GKE, Cloud Run)
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.prod.yaml
│   └── index.ts
│
└── shared/                      # Reusable components
    ├── components/
    │   ├── PostgresInstance.ts
    │   ├── GKECluster.ts
    │   └── index.ts
    └── policies/
        └── index.ts
```

**Benefits:**
- Independent deployment cadences (databases update quarterly, services weekly)
- Granular RBAC (DBAs control `databases/`, devs control `services/`)
- Smaller blast radius (change in `services/` won't touch VPC)
- Faster builds (only rebuild changed projects)

### 1.3 Stack Organization Best Practices

**DO:** Use consistent stack naming conventions

```yaml
# Format: <env>-<region>-<purpose>
dev-us-central1-api
staging-us-central1-api
prod-us-central1-api
prod-europe-west1-api
```

**DO:** Apply stack tags for cloud-based filtering

```yaml
# Pulumi.prod.yaml
config:
  pulumi:tags:
    environment: production
    costCenter: engineering
    owner: platform-team
    criticality: high
```

**DO:** Use separate configuration files per stack

```
Pulumi.yaml              # Project definition
Pulumi.dev.yaml          # Dev environment settings
Pulumi.staging.yaml      # Staging environment settings
Pulumi.prod.yaml         # Production environment settings
```

### 1.4 Stack References for Inter-Project Dependencies

**DO:** Use StackReferences for cross-project communication

```typescript
// In services/index.ts
import * as pulumi from "@pulumi/pulumi";

const infraStack = new pulumi.StackReference("org/infrastructure/prod");
const vpcId = infraStack.getOutput("vpcId");
const subnetIds = infraStack.getOutput("subnetIds");

// Use outputs from infrastructure project
const cluster = new gcp.container.Cluster("gke-cluster", {
    network: vpcId,
    subnetwork: subnetIds[0],
});
```

**DON'T:** Hard-code resource IDs across projects

```typescript
// ❌ BAD: Hard-coded VPC ID
const cluster = new gcp.container.Cluster("gke-cluster", {
    network: "projects/apex-memory/global/networks/vpc-prod",
});
```

### 1.5 Code Organization Within Projects

**DO:** Separate concerns into modules

```typescript
// index.ts - Main entry point
import { createVPC } from "./networking";
import { createDatabases } from "./databases";
import { createMonitoring } from "./monitoring";

const config = new pulumi.Config();
const vpc = createVPC(config);
const dbs = createDatabases(vpc);
const monitoring = createMonitoring([vpc, dbs]);

export const vpcId = vpc.id;
export const dbEndpoints = dbs.endpoints;
```

**DON'T:** Put everything in a single 2000-line file

---

## 2. Module Design

### 2.1 Component Resources: Reusable Building Blocks

**DO:** Encapsulate complex patterns as ComponentResources

```typescript
// shared/components/PostgresInstance.ts
import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

export interface PostgresInstanceArgs {
    region: pulumi.Input<string>;
    tier: pulumi.Input<string>;
    databaseVersion?: pulumi.Input<string>;
    backupEnabled?: pulumi.Input<boolean>;
}

export class PostgresInstance extends pulumi.ComponentResource {
    public readonly instance: gcp.sql.DatabaseInstance;
    public readonly connectionName: pulumi.Output<string>;

    constructor(name: string, args: PostgresInstanceArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:database:PostgresInstance", name, {}, opts);

        // Enforce best practices automatically
        this.instance = new gcp.sql.DatabaseInstance(`${name}-instance`, {
            databaseVersion: args.databaseVersion || "POSTGRES_15",
            region: args.region,
            settings: {
                tier: args.tier,
                backupConfiguration: {
                    enabled: args.backupEnabled ?? true,
                    pointInTimeRecoveryEnabled: true,
                },
                ipConfiguration: {
                    requireSsl: true,  // Security best practice
                    ipv4Enabled: false, // Private IP only
                },
            },
        }, { parent: this });

        this.connectionName = this.instance.connectionName;
        this.registerOutputs({
            connectionName: this.connectionName,
        });
    }
}
```

**Benefits:**
- Security defaults baked in (SSL required, private IP only)
- Consistent configuration across all PostgreSQL instances
- Write once, use in any language (TypeScript, Python, Go, etc.)
- Centralized updates (fix one component, all instances benefit)

### 2.2 Input Validation and Constraints

**DO:** Validate inputs to prevent costly mistakes

```typescript
export interface GKEClusterArgs {
    nodeCount: pulumi.Input<number>;
    machineType: pulumi.Input<string>;
}

export class GKECluster extends pulumi.ComponentResource {
    constructor(name: string, args: GKEClusterArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:compute:GKECluster", name, {}, opts);

        // Validate inputs
        const nodeCount = pulumi.output(args.nodeCount);
        nodeCount.apply(count => {
            if (count < 3) {
                throw new Error("GKE cluster must have at least 3 nodes for HA");
            }
            if (count > 100) {
                throw new Error("Node count exceeds safety limit. Use auto-scaling instead.");
            }
        });

        // ... rest of implementation
    }
}
```

### 2.3 Composition Over Inheritance

**DO:** Compose components from smaller components

```typescript
export class WebApplication extends pulumi.ComponentResource {
    constructor(name: string, opts?: pulumi.ComponentResourceOptions) {
        super("custom:app:WebApplication", name, {}, opts);

        // Compose from smaller components
        const db = new PostgresInstance(`${name}-db`, {
            region: "us-central1",
            tier: "db-g1-small",
        }, { parent: this });

        const cache = new RedisInstance(`${name}-cache`, {
            region: "us-central1",
            memorySizeGb: 1,
        }, { parent: this });

        const api = new CloudRunService(`${name}-api`, {
            image: "gcr.io/apex-memory/api:latest",
            envVars: {
                DB_CONNECTION: db.connectionName,
                REDIS_HOST: cache.host,
            },
        }, { parent: this });

        this.registerOutputs({});
    }
}
```

### 2.4 Multi-Language Support

**DO:** Publish components as Pulumi packages for cross-language use

```bash
# Create a Pulumi package schema
pulumi package add-provider apex-components

# Use TypeScript component from Python
from pulumi_apex_components import PostgresInstance

db = PostgresInstance("my-db",
    region="us-central1",
    tier="db-g1-small"
)
```

**Resources:**
- [Pulumi Package Authoring Guide](https://www.pulumi.com/docs/iac/guides/building-extensions/component-authoring/)
- [Component Resources Docs](https://www.pulumi.com/docs/iac/concepts/components/)

---

## 3. State Management

### 3.1 Backend Selection

**Recommended for Production: Pulumi Cloud (managed backend)**

```bash
# Login to Pulumi Cloud
pulumi login

# Benefits:
# - Automatic state backups
# - Built-in locking mechanism
# - Team collaboration features
# - Policy enforcement
# - Audit logging
# - Zero operational overhead
```

**Alternative: Self-Managed GCS Backend**

```bash
# Login to Google Cloud Storage backend
pulumi login gs://apex-pulumi-state

# Required setup:
# - Bucket versioning enabled
# - Object lifecycle policies for backups
# - IAM permissions properly configured
# - Manual locking mechanism (if concurrent updates)
```

**Decision Tree:**

| Use Pulumi Cloud When | Use Self-Managed When |
|----------------------|----------------------|
| Team > 1 person | Solo developer only |
| Need RBAC | Full cloud access for everyone |
| Want audit logs | Already have compliance tooling |
| Prefer managed service | Data sovereignty requirements |
| Need policy enforcement | Budget extremely constrained |

### 3.2 State Locking

**Pulumi Cloud:** Automatic locking (no configuration needed)

**Self-Managed GCS:** Implement advisory locking

```typescript
// Use Pulumi Automation API for safe concurrent updates
import * as automation from "@pulumi/pulumi/automation";

const stack = await automation.LocalWorkspace.selectStack({
    stackName: "prod",
    projectName: "apex-infrastructure",
});

// Automation API handles locking automatically
const upResult = await stack.up({ onOutput: console.log });
```

**DO:** Use CI/CD serialization for additional safety

```yaml
# GitLab CI example
deploy-prod:
  resource_group: prod-deployment  # Only one job at a time
  script:
    - pulumi up --yes --stack prod
```

### 3.3 State Backup Strategies

**DO:** Enable bucket versioning for self-managed backends

```bash
# Enable versioning on GCS bucket
gsutil versioning set on gs://apex-pulumi-state

# Lifecycle policy for backups
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 100,
          "matchesPrefix": [".pulumi/stacks/"]
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://apex-pulumi-state
```

**DO:** Export state periodically for disaster recovery

```bash
# Export stack state to local file
pulumi stack export --file prod-backup-$(date +%Y%m%d).json

# Store in secure location (encrypted S3/GCS bucket)
gcloud storage cp prod-backup-*.json gs://apex-dr-backups/pulumi-state/
```

**DO:** Test state recovery procedures quarterly

```bash
# Test import on non-production stack
pulumi stack init prod-recovery
pulumi stack import --file prod-backup-20251108.json
pulumi preview  # Verify no unexpected changes
```

### 3.4 State Security

**DO:** Encrypt state at rest

```yaml
# Pulumi.yaml
backend:
  url: gs://apex-pulumi-state
encryptionsalt: v1:...  # Automatically generated
```

**DO:** Use secrets provider for sensitive values

```yaml
# Pulumi.prod.yaml
config:
  gcp:project: apex-memory-prod
  apex:dbPassword:
    secure: AAABADi...  # Encrypted with Pulumi secrets provider
```

**DO:** Implement least-privilege IAM for state access

```bash
# GCS backend: Minimal permissions
# - storage.buckets.get
# - storage.objects.create
# - storage.objects.delete
# - storage.objects.get
# - storage.objects.list

# Pulumi Cloud: Team-based RBAC
pulumi org set-default-policy --policy require-approval
```

### 3.5 Disaster Recovery

**DO:** Document state recovery procedures

```markdown
# State Recovery Runbook

## Scenario 1: Corrupted State File
1. pulumi stack export --file corrupted.json
2. Edit JSON manually (remove corrupted resource)
3. pulumi stack import --file fixed.json
4. pulumi refresh

## Scenario 2: Complete State Loss
1. Retrieve latest backup from gs://apex-dr-backups/
2. pulumi stack init <stack-name>
3. pulumi stack import --file backup.json
4. pulumi refresh --diff
5. Manually reconcile any drift

## Scenario 3: Wrong Stack Deleted
1. Contact Pulumi support (Cloud backend recovers deleted stacks)
2. Self-managed: Restore from GCS versioned object
```

---

## 4. Security

### 4.1 Secret Management

**DO:** Use Pulumi ESC for centralized secrets

```yaml
# environments/prod.yaml (Pulumi ESC)
values:
  apex:
    dbPassword:
      fn::secret:
        fn::open::gcp-secrets:
          region: us-central1
          get:
            secretId: apex-db-password

  gcp:
    credentials:
      fn::open::gcp-login:
        project: apex-memory-prod
        oidc:
          workloadIdentityPool: pulumi-pool
          serviceAccount: pulumi-deployer@apex-memory-prod.iam.gserviceaccount.com
```

**Import into Pulumi stack:**

```yaml
# Pulumi.prod.yaml
environment:
  - prod  # Import from Pulumi ESC
```

**Benefits:**
- Dynamic, short-lived credentials (OIDC)
- No long-lived API keys
- Centralized secret rotation
- Version control for non-sensitive config

**DON'T:** Store secrets in code or stack config (plaintext)

```yaml
# ❌ BAD: Plaintext password
config:
  apex:dbPassword: SuperSecret123
```

```typescript
// ❌ BAD: Hard-coded secret
const dbPassword = "SuperSecret123";
```

### 4.2 IAM Least Privilege

**DO:** Use service accounts with minimal permissions

```typescript
// Create service account for application
const appSA = new gcp.serviceaccount.Account("app-sa", {
    accountId: "apex-api-service",
    displayName: "Apex Memory API Service Account",
});

// Grant ONLY required permissions
const dbRole = new gcp.projects.IAMMember("app-db-access", {
    project: config.require("gcpProject"),
    role: "roles/cloudsql.client",  // Not admin, just client
    member: pulumi.interpolate`serviceAccount:${appSA.email}`,
});
```

**DO:** Use Workload Identity for GKE pods

```typescript
const k8sSA = new k8s.core.v1.ServiceAccount("app-k8s-sa", {
    metadata: {
        name: "apex-api",
        annotations: {
            "iam.gke.io/gcp-service-account": appSA.email,
        },
    },
});

const workloadIdentityBinding = new gcp.serviceaccount.IAMBinding("workload-identity", {
    serviceAccountId: appSA.name,
    role: "roles/iam.workloadIdentityUser",
    members: [
        pulumi.interpolate`serviceAccount:${gcpProject}.svc.id.goog[default/apex-api]`,
    ],
});
```

### 4.3 Network Security

**DO:** Use Private Google Access and VPC Service Controls

```typescript
const vpc = new gcp.compute.Network("vpc", {
    autoCreateSubnetworks: false,
});

const subnet = new gcp.compute.Subnetwork("subnet", {
    network: vpc.id,
    ipCidrRange: "10.0.0.0/24",
    region: "us-central1",
    privateIpGoogleAccess: true,  // Access Google APIs via private IPs
});

// VPC Service Controls perimeter
const servicePerimeter = new gcp.accesscontextmanager.ServicePerimeter("perimeter", {
    parent: pulumi.interpolate`accessPolicies/${accessPolicy.name}`,
    title: "Apex Memory Perimeter",
    status: {
        restrictedServices: [
            "storage.googleapis.com",
            "sqladmin.googleapis.com",
        ],
    },
});
```

**DO:** Enforce SSL/TLS everywhere

```typescript
const postgresInstance = new gcp.sql.DatabaseInstance("db", {
    settings: {
        ipConfiguration: {
            requireSsl: true,  // Reject non-SSL connections
        },
    },
});
```

### 4.4 Audit Logging

**DO:** Enable Cloud Audit Logs for compliance

```typescript
import * as gcp from "@pulumi/gcp";

// Enable audit logs for all services
const auditConfig = new gcp.organizations.IAMAuditConfig("audit", {
    orgId: config.require("orgId"),
    service: "allServices",
    auditLogConfigs: [
        { logType: "ADMIN_READ" },
        { logType: "DATA_READ" },
        { logType: "DATA_WRITE" },
    ],
});
```

**DO:** Export Pulumi audit events

```bash
# Pulumi Cloud automatically logs all operations
# Query via CLI:
pulumi stack history --full

# Export to SIEM:
pulumi stack export --show-secrets | jq '.deployment'
```

### 4.5 Compliance (HIPAA, SOC2, PCI-DSS)

**DO:** Use Policy as Code to enforce compliance

```typescript
// policies/compliance.ts
import { PolicyPack, validateResourceOfType } from "@pulumi/policy";

new PolicyPack("compliance", {
    policies: [
        {
            name: "gcs-encryption-required",
            description: "GCS buckets must use customer-managed encryption",
            enforcementLevel: "mandatory",
            validateResource: validateResourceOfType(gcp.storage.Bucket, (bucket, args, reportViolation) => {
                if (!bucket.encryption?.defaultKmsKeyName) {
                    reportViolation("GCS bucket must use CMEK encryption for compliance");
                }
            }),
        },
        {
            name: "sql-backup-retention",
            description: "SQL instances must retain backups for 30 days (PCI-DSS)",
            enforcementLevel: "mandatory",
            validateResource: validateResourceOfType(gcp.sql.DatabaseInstance, (db, args, reportViolation) => {
                const retainedBackups = db.settings?.backupConfiguration?.backupRetentionSettings?.retainedBackups;
                if (!retainedBackups || retainedBackups < 30) {
                    reportViolation("SQL backup retention must be >= 30 days");
                }
            }),
        },
    ],
});
```

**Resources:**
- [Pulumi Compliance Ready Policies](https://www.pulumi.com/docs/iac/using-pulumi/crossguard/compliance-ready-policies/)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)

---

## 5. Testing

### 5.1 Unit Testing

**DO:** Mock cloud resources for fast, offline testing

```typescript
// __tests__/postgres.test.ts
import * as pulumi from "@pulumi/pulumi";
import { PostgresInstance } from "../shared/components/PostgresInstance";

pulumi.runtime.setMocks({
    newResource: function(args: pulumi.runtime.MockResourceArgs): {id: string, state: any} {
        return {
            id: args.name + "_id",
            state: args.inputs,
        };
    },
    call: function(args: pulumi.runtime.MockCallArgs) {
        return args.inputs;
    },
});

describe("PostgresInstance", () => {
    let instance: PostgresInstance;

    before(async () => {
        instance = new PostgresInstance("test-db", {
            region: "us-central1",
            tier: "db-f1-micro",
        });
    });

    it("enforces SSL by default", (done) => {
        pulumi.all([instance.instance.settings]).apply(([settings]) => {
            assert.strictEqual(settings.ipConfiguration.requireSsl, true);
            done();
        });
    });

    it("enables backups by default", (done) => {
        pulumi.all([instance.instance.settings]).apply(([settings]) => {
            assert.strictEqual(settings.backupConfiguration.enabled, true);
            done();
        });
    });
});
```

**Run unit tests in CI:**

```yaml
# .gitlab-ci.yml
unit-tests:
  script:
    - npm install
    - npm test
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
```

### 5.2 Property Testing (Policy as Code)

**DO:** Validate resource properties during deployment

```typescript
// policies/security.ts
import { PolicyPack, validateResourceOfType } from "@pulumi/policy";
import * as gcp from "@pulumi/gcp";

new PolicyPack("security", {
    policies: [
        {
            name: "no-public-buckets",
            description: "GCS buckets must not be publicly accessible",
            enforcementLevel: "mandatory",
            validateResource: validateResourceOfType(gcp.storage.Bucket, (bucket, args, reportViolation) => {
                if (bucket.uniformBucketLevelAccess?.enabled === false) {
                    reportViolation("Bucket must use uniform bucket-level access");
                }
            }),
        },
        {
            name: "database-private-only",
            description: "SQL instances must use private IP only",
            enforcementLevel: "mandatory",
            validateResource: validateResourceOfType(gcp.sql.DatabaseInstance, (db, args, reportViolation) => {
                if (db.settings?.ipConfiguration?.ipv4Enabled) {
                    reportViolation("Database must not have public IPv4 address");
                }
            }),
        },
    ],
});
```

**Run policies during preview:**

```bash
# Local validation
pulumi preview --policy-pack ./policies

# Enforce org-wide (Pulumi Cloud)
pulumi policy publish policies/
pulumi policy enable apex-org/security latest
```

### 5.3 Integration Testing

**DO:** Deploy ephemeral infrastructure and test real endpoints

```typescript
// tests/integration/api.test.ts
import * as automation from "@pulumi/pulumi/automation";
import * as assert from "assert";
import axios from "axios";

describe("API Integration Tests", () => {
    let stack: automation.Stack;
    let apiUrl: string;

    before(async function() {
        this.timeout(600000);  // 10 minutes for deployment

        // Create ephemeral stack
        stack = await automation.LocalWorkspace.createStack({
            stackName: `integration-test-${Date.now()}`,
            projectName: "apex-services",
        });

        // Deploy
        const upResult = await stack.up();
        apiUrl = upResult.outputs.apiUrl.value;
    });

    it("returns health check", async () => {
        const response = await axios.get(`${apiUrl}/health`);
        assert.strictEqual(response.status, 200);
        assert.strictEqual(response.data.status, "healthy");
    });

    it("authenticates with valid token", async () => {
        const response = await axios.post(`${apiUrl}/auth/login`, {
            username: "test@example.com",
            password: "test123",
        });
        assert.strictEqual(response.status, 200);
        assert.ok(response.data.token);
    });

    after(async function() {
        this.timeout(300000);  // 5 minutes for cleanup
        await stack.destroy();
        await stack.workspace.removeStack(stack.name);
    });
});
```

**Run integration tests nightly:**

```yaml
# .gitlab-ci.yml
integration-tests:
  only:
    - schedules  # Run nightly, not on every commit
  script:
    - npm run test:integration
  artifacts:
    reports:
      junit: test-results.xml
```

### 5.4 Testing Strategy Summary

**Recommended approach for Apex Memory System:**

```
Unit Tests (Fast)         → Run on every commit
├── Component validation
├── Configuration parsing
└── Resource property checks

Property Tests (Medium)   → Run during pulumi preview
├── Security policies
├── Compliance validation
└── Cost guardrails

Integration Tests (Slow)  → Run nightly or pre-release
├── End-to-end workflows
├── Multi-service interaction
└── Performance validation
```

**Coverage targets:**
- Unit tests: 80%+ coverage
- Property tests: 100% of critical security policies
- Integration tests: All public APIs and critical user paths

---

## 6. Deployment Patterns

### 6.1 Blue-Green Deployments

**Pattern:** Maintain two identical environments, switch traffic atomically

```typescript
// Toggle between blue and green stacks
const config = new pulumi.Config();
const activeStack = config.require("activeStack");  // "blue" or "green"

// Create both stacks
const blueStack = new pulumi.StackReference("org/apex-api/blue");
const greenStack = new pulumi.StackReference("org/apex-api/green");

// Route traffic to active stack
const loadBalancer = new gcp.compute.GlobalForwardingRule("lb", {
    target: activeStack === "blue"
        ? blueStack.getOutput("backendServiceId")
        : greenStack.getOutput("backendServiceId"),
});
```

**Deployment workflow:**

```bash
# 1. Deploy new version to inactive stack (green)
cd services
pulumi up --stack green

# 2. Run smoke tests against green
npm run test:smoke -- --url $(pulumi stack output apiUrl --stack green)

# 3. Switch traffic to green
cd ../routing
pulumi config set activeStack green
pulumi up

# 4. Monitor for issues
sleep 300  # 5 minute soak period

# 5. If issues, instant rollback
pulumi config set activeStack blue
pulumi up
```

### 6.2 Canary Deployments

**Pattern:** Gradually shift traffic to new version

```typescript
import * as gcp from "@pulumi/gcp";

const config = new pulumi.Config();
const canaryPercent = config.requireNumber("canaryPercent");  // 0-100

const backendService = new gcp.compute.BackendService("api", {
    backends: [
        {
            group: stableBackend.instanceGroup,
            balancingMode: "UTILIZATION",
            capacityScaler: (100 - canaryPercent) / 100,  // 90% to stable
        },
        {
            group: canaryBackend.instanceGroup,
            balancingMode: "UTILIZATION",
            capacityScaler: canaryPercent / 100,  // 10% to canary
        },
    ],
});
```

**Gradual rollout:**

```bash
# Phase 1: 5% canary
pulumi config set canaryPercent 5
pulumi up
sleep 600  # 10 min observation

# Phase 2: 25% canary
pulumi config set canaryPercent 25
pulumi up
sleep 900  # 15 min observation

# Phase 3: 50% canary
pulumi config set canaryPercent 50
pulumi up
sleep 1800  # 30 min observation

# Phase 4: 100% (full rollout)
pulumi config set canaryPercent 100
pulumi up
```

### 6.3 Rollback Strategies

**DO:** Tag all deployments for easy rollback

```typescript
const deployment = new gcp.cloudrun.Service("api", {
    template: {
        metadata: {
            annotations: {
                "deployment.timestamp": new Date().toISOString(),
                "deployment.commit": process.env.CI_COMMIT_SHA || "local",
                "deployment.pulumi-stack": pulumi.getStack(),
            },
        },
        spec: {
            containers: [{
                image: `gcr.io/apex-memory/api:${config.require("imageTag")}`,
            }],
        },
    },
});
```

**Fast rollback using stack history:**

```bash
# View deployment history
pulumi stack history

# Rollback to previous version (version N-1)
pulumi stack export --version 42 | pulumi stack import
pulumi up  # Apply previous state
```

**Atomic rollback using stack references:**

```bash
# Instant rollback: point to last known good stack
pulumi config set activeStack prod-v1.42
pulumi up --yes
```

### 6.4 Drift Detection and Remediation

**DO:** Run drift detection daily

```bash
#!/bin/bash
# scripts/drift-detection.sh

STACKS=("prod" "staging")

for stack in "${STACKS[@]}"; do
    echo "Checking drift for stack: $stack"

    # Refresh and detect changes
    pulumi refresh --yes --stack $stack --diff > drift-report-$stack.txt

    # Alert if drift detected
    if grep -q "~" drift-report-$stack.txt || grep -q "+" drift-report-$stack.txt; then
        echo "⚠️ DRIFT DETECTED in $stack"
        # Send to Slack, PagerDuty, etc.
        curl -X POST $SLACK_WEBHOOK -d "{\"text\":\"Drift detected in $stack\"}"
    fi
done
```

**DO:** Auto-remediate approved drift

```typescript
// Enable automatic import of manually created resources
const vpc = new gcp.compute.Network("vpc", {
    autoCreateSubnetworks: false,
}, {
    protect: true,  // Prevent accidental deletion
    import: "projects/apex-memory-prod/global/networks/vpc-prod",  // Import existing
});
```

### 6.5 Change Management and Approvals

**DO:** Require manual approval for production changes

```yaml
# .gitlab-ci.yml
deploy-prod:
  stage: deploy
  when: manual  # Require button click
  only:
    - main
  script:
    - pulumi preview --stack prod | tee preview.txt
    - pulumi up --yes --stack prod
  artifacts:
    paths:
      - preview.txt
```

**DO:** Use Pulumi Deployments for controlled rollouts

```yaml
# Pulumi.prod.yaml
deployment:
  settings:
    operation: update
    source:
      git:
        repoURL: https://github.com/apex-memory/infrastructure
        branch: refs/heads/main
    triggerUpdate:
      schedule: "0 2 * * 0"  # Weekly at 2am Sunday
```

---

## 7. Cost Optimization

### 7.1 Resource Tagging for Cost Tracking

**DO:** Apply consistent tags to ALL resources

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

// Global tagging function
export function apexTags(additionalTags?: Record<string, string>): pulumi.Input<Record<string, string>> {
    const config = new pulumi.Config();
    const stack = pulumi.getStack();

    return {
        environment: stack.includes("prod") ? "production" : "development",
        project: "apex-memory-system",
        managed_by: "pulumi",
        cost_center: config.get("costCenter") || "engineering",
        owner: config.get("owner") || "platform-team",
        ...additionalTags,
    };
}

// Apply to every resource
const instance = new gcp.compute.Instance("vm", {
    labels: apexTags({ service: "api" }),
});

const bucket = new gcp.storage.Bucket("data", {
    labels: apexTags({ service: "storage" }),
});
```

**DO:** Query costs by tag in Cloud Billing

```sql
-- BigQuery cost analysis
SELECT
  labels.value AS cost_center,
  SUM(cost) AS total_cost
FROM `apex-memory-prod.billing.gcp_billing_export_v1`
CROSS JOIN UNNEST(labels) AS labels
WHERE labels.key = 'cost_center'
  AND EXTRACT(MONTH FROM usage_start_time) = EXTRACT(MONTH FROM CURRENT_DATE())
GROUP BY labels.value
ORDER BY total_cost DESC;
```

### 7.2 Right-Sizing Resources

**DO:** Use Policy as Code to prevent oversized instances

```typescript
// policies/cost-control.ts
new PolicyPack("cost-control", {
    policies: [
        {
            name: "gke-node-size-limit",
            description: "GKE nodes must not exceed n1-standard-8",
            enforcementLevel: "mandatory",
            validateResource: validateResourceOfType(gcp.container.Cluster, (cluster, args, reportViolation) => {
                const allowedMachineTypes = [
                    "e2-medium", "e2-standard-2", "e2-standard-4",
                    "n1-standard-1", "n1-standard-2", "n1-standard-4",
                ];

                cluster.nodeConfig?.machineType.apply(machineType => {
                    if (!allowedMachineTypes.includes(machineType)) {
                        reportViolation(`Machine type ${machineType} exceeds approved sizes`);
                    }
                });
            }),
        },
    ],
});
```

**DO:** Create component with cost-optimized defaults

```typescript
export class CostOptimizedPostgres extends pulumi.ComponentResource {
    constructor(name: string, opts?: pulumi.ComponentResourceOptions) {
        super("custom:database:CostOptimizedPostgres", name, {}, opts);

        const stack = pulumi.getStack();

        // Dev/staging: Small, deletable
        const tier = stack.includes("prod") ? "db-n1-standard-2" : "db-f1-micro";
        const deletionProtection = stack.includes("prod");

        const instance = new gcp.sql.DatabaseInstance(`${name}-instance`, {
            databaseVersion: "POSTGRES_15",
            settings: {
                tier: tier,
                diskAutoresize: true,
                diskSize: 10,  // Start small
            },
            deletionProtection: deletionProtection,
        }, { parent: this });
    }
}
```

### 7.3 Auto-Scaling Strategies

**DO:** Configure horizontal pod autoscaling for GKE

```typescript
const deployment = new k8s.apps.v1.Deployment("api", {
    spec: {
        replicas: 2,  // Minimum replicas
        template: {
            spec: {
                containers: [{
                    name: "api",
                    resources: {
                        requests: {
                            cpu: "100m",
                            memory: "128Mi",
                        },
                        limits: {
                            cpu: "500m",
                            memory: "512Mi",
                        },
                    },
                }],
            },
        },
    },
});

const hpa = new k8s.autoscaling.v2.HorizontalPodAutoscaler("api-hpa", {
    spec: {
        scaleTargetRef: {
            apiVersion: "apps/v1",
            kind: "Deployment",
            name: deployment.metadata.name,
        },
        minReplicas: 2,
        maxReplicas: 10,
        metrics: [
            {
                type: "Resource",
                resource: {
                    name: "cpu",
                    target: {
                        type: "Utilization",
                        averageUtilization: 70,
                    },
                },
            },
        ],
    },
});
```

**DO:** Use GKE cluster autoscaling

```typescript
const cluster = new gcp.container.Cluster("gke", {
    clusterAutoscaling: {
        enabled: true,
        resourceLimits: [
            { resourceType: "cpu", minimum: 4, maximum: 32 },
            { resourceType: "memory", minimum: 16, maximum: 128 },
        ],
        autoscalingProfile: "OPTIMIZE_UTILIZATION",  // Cost-optimized
    },
});
```

### 7.4 Scheduled Scaling (Dev Environment Cost Reduction)

**DO:** Scale down non-production environments outside business hours

```typescript
// Cloud Scheduler to scale down dev clusters at night
const scaleDownJob = new gcp.cloudscheduler.Job("scale-down-dev", {
    schedule: "0 19 * * 1-5",  // 7 PM weekdays
    timeZone: "America/New_York",
    httpTarget: {
        uri: pulumi.interpolate`https://container.googleapis.com/v1/${cluster.id}/nodePools/default`,
        httpMethod: "PATCH",
        body: Buffer.from(JSON.stringify({
            autoscaling: {
                enabled: true,
                minNodeCount: 0,  // Scale to zero
                maxNodeCount: 0,
            },
        })).toString("base64"),
        oauthToken: {
            serviceAccountEmail: scalerSA.email,
        },
    },
});

const scaleUpJob = new gcp.cloudscheduler.Job("scale-up-dev", {
    schedule: "0 8 * * 1-5",  // 8 AM weekdays
    timeZone: "America/New_York",
    httpTarget: {
        uri: pulumi.interpolate`https://container.googleapis.com/v1/${cluster.id}/nodePools/default`,
        httpMethod: "PATCH",
        body: Buffer.from(JSON.stringify({
            autoscaling: {
                enabled: true,
                minNodeCount: 2,
                maxNodeCount: 10,
            },
        })).toString("base64"),
        oauthToken: {
            serviceAccountEmail: scalerSA.email,
        },
    },
});
```

**Estimated savings:** 60-70% reduction in dev environment costs

### 7.5 Cost Monitoring and Alerts

**DO:** Set up budget alerts

```typescript
const budget = new gcp.billing.Budget("monthly-budget", {
    billingAccount: config.require("billingAccount"),
    amount: {
        specifiedAmount: {
            currencyCode: "USD",
            units: "1000",  // $1,000/month
        },
    },
    thresholdRules: [
        { thresholdPercent: 0.5 },  // 50% alert
        { thresholdPercent: 0.75 }, // 75% alert
        { thresholdPercent: 0.9 },  // 90% alert
        { thresholdPercent: 1.0 },  // 100% alert
    ],
    allUpdatesRule: {
        pubsubTopic: alertTopic.id,
    },
});
```

**DO:** Export billing data to BigQuery for analysis

```bash
# Enable billing export
gcloud beta billing projects link apex-memory-prod \
  --billing-account=0X0X0X-0X0X0X-0X0X0X

# Export to BigQuery
gcloud alpha billing export bigquery setup \
  --billing-account=0X0X0X-0X0X0X-0X0X0X \
  --dataset-id=billing \
  --table-id=gcp_billing_export_v1
```

---

## 8. Performance & Reliability

### 8.1 Parallel Resource Creation

**DO:** Use `Promise.all()` for independent resources

```typescript
// ❌ BAD: Sequential creation (slow)
const bucket1 = new gcp.storage.Bucket("bucket-1");
const bucket2 = new gcp.storage.Bucket("bucket-2");
const bucket3 = new gcp.storage.Bucket("bucket-3");
// Total time: 30 seconds (10s each)

// ✅ GOOD: Parallel creation (fast)
const buckets = Promise.all([
    new gcp.storage.Bucket("bucket-1"),
    new gcp.storage.Bucket("bucket-2"),
    new gcp.storage.Bucket("bucket-3"),
]);
// Total time: 10 seconds (all at once)
```

**DO:** Set `--parallel` flag for large deployments

```bash
# Default: 10 parallel operations
pulumi up --parallel 20  # Double parallelism
```

### 8.2 Resource Dependencies Optimization

**DO:** Only declare explicit dependencies when necessary

```typescript
// Pulumi automatically detects dependencies via resource properties
const vpc = new gcp.compute.Network("vpc");
const subnet = new gcp.compute.Subnetwork("subnet", {
    network: vpc.id,  // Implicit dependency: subnet waits for vpc
});

// ❌ DON'T: Redundant explicit dependency
const subnet = new gcp.compute.Subnetwork("subnet", {
    network: vpc.id,
}, { dependsOn: [vpc] });  // Unnecessary
```

**DO:** Use `dependsOn` for non-obvious ordering

```typescript
// Database must be ready before running migrations
const migrationJob = new gcp.cloudrun.Job("migrations", {
    template: {
        template: {
            containers: [{
                image: "gcr.io/apex-memory/migrations:latest",
            }],
        },
    },
}, { dependsOn: [postgresInstance] });  // Explicit dependency needed
```

### 8.3 Timeouts and Retries

**DO:** Configure appropriate timeouts for slow resources

```typescript
const cluster = new gcp.container.Cluster("gke", {
    initialNodeCount: 3,
}, {
    customTimeouts: {
        create: "30m",  // GKE cluster creation can take 20+ minutes
        update: "20m",
        delete: "30m",
    },
});
```

**DO:** Use `retryOnConflict` for eventually consistent resources

```typescript
const iamBinding = new gcp.projects.IAMBinding("binding", {
    project: config.require("project"),
    role: "roles/viewer",
    members: ["serviceAccount:app@apex-memory.iam.gserviceaccount.com"],
}, {
    retryOnConflict: true,  // Retry IAM conflicts automatically
});
```

### 8.4 High Availability Patterns

**DO:** Deploy across multiple zones

```typescript
const nodePool = new gcp.container.NodePool("default", {
    cluster: cluster.name,
    nodeLocations: [
        "us-central1-a",
        "us-central1-b",
        "us-central1-c",
    ],
    initialNodeCount: 1,  // 1 node per zone = 3 total
});
```

**DO:** Use regional resources over zonal

```typescript
// ✅ GOOD: Regional GKE cluster (multi-zone control plane)
const regionalCluster = new gcp.container.Cluster("regional", {
    location: "us-central1",  // Region, not zone
});

// ❌ BAD: Zonal cluster (single point of failure)
const zonalCluster = new gcp.container.Cluster("zonal", {
    location: "us-central1-a",  // Single zone
});
```

### 8.5 Multi-Region Deployments

**DO:** Use for-loops for multi-region infrastructure

```typescript
const regions = ["us-central1", "europe-west1", "asia-southeast1"];

const regionalClusters = regions.map(region =>
    new gcp.container.Cluster(`gke-${region}`, {
        location: region,
        initialNodeCount: 3,
    })
);

// Global load balancer routing to all regions
const globalLB = new gcp.compute.GlobalForwardingRule("global-lb", {
    target: backendService.id,
    portRange: "443",
});
```

**DO:** Use Traffic Director for global load balancing

```typescript
const backendService = new gcp.compute.BackendService("global", {
    backends: regions.map((region, i) => ({
        group: regionalClusters[i].instanceGroupUrls[0],
        balancingMode: "RATE",
        maxRatePerInstance: 100,
    })),
    healthChecks: [healthCheck.id],
    loadBalancingScheme: "EXTERNAL_MANAGED",
});
```

---

## 9. Common Anti-Patterns

### 9.1 Hard-Coded Values

**❌ DON'T:**

```typescript
const cluster = new gcp.container.Cluster("gke", {
    location: "us-central1",  // Hard-coded region
    initialNodeCount: 3,  // Hard-coded size
});
```

**✅ DO:**

```typescript
const config = new pulumi.Config();
const cluster = new gcp.container.Cluster("gke", {
    location: config.require("region"),
    initialNodeCount: config.requireNumber("nodeCount"),
});
```

### 9.2 Shared State Across Teams

**❌ DON'T:** Multiple teams modifying the same stack

```bash
# Team A and Team B both running:
pulumi up --stack shared-infra  # Conflict!
```

**✅ DO:** Separate stacks per team with StackReferences

```bash
# Team A owns infrastructure
cd infrastructure/
pulumi up --stack prod

# Team B consumes infrastructure
cd services/
const infraStack = new pulumi.StackReference("org/infrastructure/prod");
```

### 9.3 Manual Resource Creation

**❌ DON'T:** Create resources in Cloud Console, then import into Pulumi

```bash
# Manually created VPC in console, then:
pulumi import gcp:compute/network:Network vpc projects/apex/global/networks/vpc
# Results in drift, missing properties
```

**✅ DO:** Define everything in Pulumi from day one

```typescript
const vpc = new gcp.compute.Network("vpc", {
    autoCreateSubnetworks: false,
});
```

### 9.4 Ignoring Pulumi Preview

**❌ DON'T:** Skip preview and run `pulumi up --yes` blindly

```bash
pulumi up --yes  # DANGEROUS: No review
```

**✅ DO:** Always review preview output

```bash
pulumi preview  # Review changes
# Verify expected changes
pulumi up  # Approve interactively
```

### 9.5 Storing Secrets in Code

**❌ DON'T:**

```typescript
const dbPassword = "SuperSecret123";  // Checked into Git!

const user = new gcp.sql.User("db-user", {
    password: dbPassword,
});
```

**✅ DO:**

```typescript
const config = new pulumi.Config();
const dbPassword = config.requireSecret("dbPassword");  // Encrypted

const user = new gcp.sql.User("db-user", {
    password: dbPassword,
});
```

### 9.6 Monolithic Programs

**❌ DON'T:** 3000-line `index.ts` with everything

**✅ DO:** Modular structure with components

```
pulumi/
├── index.ts              # Entry point (50 lines)
├── networking.ts         # VPC, subnets
├── databases.ts          # SQL, Redis
├── compute.ts            # GKE, Cloud Run
└── components/
    ├── PostgresHA.ts
    └── GKECluster.ts
```

### 9.7 Missing Resource Protection

**❌ DON'T:** Allow accidental deletion of critical resources

```typescript
const productionDB = new gcp.sql.DatabaseInstance("prod-db");
// Can be deleted with `pulumi destroy`
```

**✅ DO:** Protect critical resources

```typescript
const productionDB = new gcp.sql.DatabaseInstance("prod-db", {
    deletionProtection: true,  // GCP-level protection
}, {
    protect: true,  // Pulumi-level protection
});
```

### 9.8 No Testing

**❌ DON'T:** Deploy directly to production without testing

**✅ DO:** Implement testing pyramid

```
Integration Tests (10%) → Deploy to ephemeral env, test APIs
Property Tests (30%)    → Validate security/compliance policies
Unit Tests (60%)        → Mock resources, test logic
```

### 9.9 Poor Change Management

**❌ DON'T:** Allow anyone to run `pulumi up` on production

**✅ DO:** Use CI/CD with approvals

```yaml
# .gitlab-ci.yml
deploy-prod:
  stage: deploy
  when: manual
  only:
    - main
  environment:
    name: production
  script:
    - pulumi preview --stack prod
    - pulumi up --yes --stack prod
```

### 9.10 Ignoring State Management

**❌ DON'T:** Use local state file for team projects

```bash
pulumi login --local  # State stored locally, not shared
```

**✅ DO:** Use centralized backend

```bash
pulumi login  # Pulumi Cloud
# OR
pulumi login gs://apex-pulumi-state  # GCS backend
```

---

## Summary Checklist

### Before Production Deployment

**Project Organization:**
- [ ] Multiple projects for different lifecycles
- [ ] Consistent stack naming convention
- [ ] Stack tags for cost tracking
- [ ] StackReferences for cross-project dependencies

**Security:**
- [ ] Pulumi ESC for secrets management
- [ ] OIDC authentication (no long-lived keys)
- [ ] IAM least privilege for all service accounts
- [ ] SSL/TLS enforced everywhere
- [ ] Cloud Audit Logs enabled

**State Management:**
- [ ] Centralized backend (Pulumi Cloud or GCS)
- [ ] State backups configured
- [ ] Recovery procedures documented
- [ ] Team RBAC configured

**Testing:**
- [ ] Unit tests for components (80%+ coverage)
- [ ] Policy as Code for security/compliance
- [ ] Integration tests for critical paths
- [ ] CI/CD running all tests

**Cost Optimization:**
- [ ] Resource tagging strategy implemented
- [ ] Budget alerts configured
- [ ] Dev environments scale down after hours
- [ ] Right-sized instances (policy enforced)

**Deployment:**
- [ ] Blue-green or canary strategy defined
- [ ] Rollback procedures tested
- [ ] Manual approval for production changes
- [ ] Drift detection running daily

**Reliability:**
- [ ] Multi-zone deployment
- [ ] Auto-scaling configured
- [ ] Health checks implemented
- [ ] Monitoring and alerting active

---

## Additional Resources

### Official Documentation
- [Pulumi Best Practices Guide](https://www.pulumi.com/docs/iac/guides/basics/organizing-projects-stacks/)
- [Pulumi CrossGuard (Policy as Code)](https://www.pulumi.com/docs/iac/using-pulumi/crossguard/)
- [Pulumi ESC (Secrets Management)](https://www.pulumi.com/product/esc/)
- [Pulumi Testing Guide](https://www.pulumi.com/docs/iac/guides/testing/)

### Blog Posts & Case Studies
- [IaC Best Practices: Structuring Projects](https://www.pulumi.com/blog/iac-best-practices-structuring-pulumi-projects/)
- [RBAC and Security](https://www.pulumi.com/blog/iac-best-practices-implementing-rbac-and-security/)
- [Policy as Code Deployment Guardrails](https://www.pulumi.com/blog/deployment-guardrails-with-pulumi-crossguard/)
- [FinOps with Pulumi](https://www.pulumi.com/blog/finops-with-pulumi/)

### GCP-Specific Resources
- [GCP Well-Architected Framework](https://cloud.google.com/architecture/framework)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)
- [Pulumi GCP Provider Docs](https://www.pulumi.com/registry/packages/gcp/)

### Community
- [Pulumi Community Slack](https://slack.pulumi.com/)
- [Pulumi GitHub Discussions](https://github.com/pulumi/pulumi/discussions)
- [Pulumi Examples Repository](https://github.com/pulumi/examples)

---

**Document Version:** 1.0
**Last Updated:** November 8, 2025
**Maintained By:** Platform Team (standards-researcher agent)
**Next Review:** February 2026
