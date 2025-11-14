# Pulumi Installation & Setup Guide

**Time Required:** 30-45 minutes
**Prerequisites:** macOS, Admin access, Homebrew installed

---

## Quick Checklist

Before you can run `pulumi up`, you need:

- [ ] **Pulumi CLI** - Command-line tool for infrastructure deployment
- [ ] **Python 3.11+** - Runtime for Pulumi Python programs
- [ ] **uv** - Ultra-fast Python package manager (100x faster than pip)
- [ ] **gcloud CLI** - Google Cloud command-line tool for authentication

**Optional but Recommended:**
- [ ] **Visual Studio Code** - IDE with Python/Pulumi extensions
- [ ] **Pulumi VS Code Extension** - IntelliSense for Pulumi resources

---

## Step 1: Install Pulumi CLI (Required)

### macOS (Recommended - Homebrew)

```bash
# Install Pulumi CLI
brew install pulumi

# Verify installation
pulumi version
# Expected output: v3.140.0 or higher
```

### Alternative Methods

**Direct download (if no Homebrew):**
```bash
curl -fsSL https://get.pulumi.com | sh

# Add to PATH (add to ~/.zshrc or ~/.bashrc)
export PATH=$PATH:$HOME/.pulumi/bin

# Reload shell
source ~/.zshrc  # or source ~/.bashrc

# Verify
pulumi version
```

**What is Pulumi CLI?**
- The `pulumi` command-line tool
- Used for: `pulumi up`, `pulumi preview`, `pulumi destroy`, etc.
- Manages state, executes deployments, shows diffs

---

## Step 2: Install Python 3.11+ (Required)

### Check Current Version

```bash
python3 --version
# Need: Python 3.11.0 or higher
```

### Install/Upgrade Python

**Option A: Homebrew (Recommended)**
```bash
# Install Python 3.12 (latest stable)
brew install python@3.12

# Verify
python3 --version
# Expected: Python 3.12.x
```

**Option B: pyenv (Multiple Python Versions)**
```bash
# Install pyenv
brew install pyenv

# Install Python 3.12
pyenv install 3.12.0

# Set global version
pyenv global 3.12.0

# Add to shell config (~/.zshrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Verify
python3 --version
```

**Why Python 3.11+?**
- Pulumi Python SDK requires Python 3.8+ (3.11+ recommended for performance)
- Type hints improvements (better IDE support)
- Performance improvements (10-60% faster than 3.10)

---

## Step 3: Install uv (Recommended)

### Installation

```bash
# Install uv via Homebrew
brew install uv

# Verify installation
uv --version
# Expected output: uv 0.4.x or higher
```

### Alternative Installation

```bash
# Install via curl (if no Homebrew)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
```

**What is uv?**
- Ultra-fast Python package manager (100x faster than pip)
- Rust-based (same team as Ruff linter)
- Replaces: pip, pip-tools, virtualenv, poetry
- Officially supported by Pulumi (as of Nov 2024)

**Why use uv?**
- **Speed:** 100x faster than pip for package installation
- **Lockfiles:** Reproducible builds (uv.lock)
- **Single tool:** Manages venv + packages + lockfiles
- **Pulumi support:** Pulumi.yaml can specify `toolchain: uv`

---

## Step 4: Install gcloud CLI (Required for GCP)

### Installation

```bash
# Install Google Cloud SDK
brew install google-cloud-sdk

# Verify installation
gcloud --version
# Expected output: Google Cloud SDK 455.0.0 or higher
```

### Initialize gcloud

```bash
# Login to Google Cloud
gcloud auth login
# Opens browser, authenticate with Google account

# Set default project
gcloud config set project apex-memory-dev

# Set default region
gcloud config set compute/region us-central1

# Verify configuration
gcloud config list
```

### Application Default Credentials (ADC)

```bash
# Login with application default credentials (for Pulumi)
gcloud auth application-default login

# This creates: ~/.config/gcloud/application_default_credentials.json
# Pulumi uses this for GCP authentication
```

**What is gcloud CLI?**
- Google Cloud command-line tool
- Used for: authentication, project management, resource inspection
- Pulumi uses your gcloud credentials to deploy to GCP

---

## Step 5: Optional Tools (Recommended)

### Visual Studio Code with Extensions

**Install VS Code:**
```bash
brew install --cask visual-studio-code
```

**Install Extensions:**
1. **Pulumi** (pulumi.pulumi-lsp)
   - IntelliSense for Pulumi resources
   - Auto-completion for GCP resources
   - Inline documentation

2. **Python** (ms-python.python)
   - Python language support
   - Linting, formatting, debugging

3. **Pylance** (ms-python.vscode-pylance)
   - Fast type checking
   - Better IntelliSense

**Install via Command Line:**
```bash
code --install-extension pulumi.pulumi-lsp
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
```

---

## Step 6: Verify Installation

Run this comprehensive check script:

```bash
# Create verification script
cat > check-installation.sh << 'EOF'
#!/bin/bash

echo "=== Pulumi Installation Verification ==="
echo ""

# Check Pulumi CLI
echo "1. Pulumi CLI:"
if command -v pulumi &> /dev/null; then
    echo "   ✅ Installed: $(pulumi version)"
else
    echo "   ❌ NOT FOUND - Install with: brew install pulumi"
fi
echo ""

# Check Python
echo "2. Python:"
if command -v python3 &> /dev/null; then
    version=$(python3 --version | cut -d' ' -f2)
    major=$(echo $version | cut -d'.' -f1)
    minor=$(echo $version | cut -d'.' -f2)
    if [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; then
        echo "   ✅ Installed: Python $version"
    else
        echo "   ⚠️  Version $version is too old (need 3.11+)"
    fi
else
    echo "   ❌ NOT FOUND - Install with: brew install python@3.12"
fi
echo ""

# Check uv
echo "3. uv (Package Manager):"
if command -v uv &> /dev/null; then
    echo "   ✅ Installed: $(uv --version)"
else
    echo "   ❌ NOT FOUND - Install with: brew install uv"
fi
echo ""

# Check gcloud CLI
echo "4. gcloud CLI:"
if command -v gcloud &> /dev/null; then
    echo "   ✅ Installed: $(gcloud --version | head -1)"
    echo ""
    echo "   Current config:"
    gcloud config list --format="value(core.project,compute.region)" 2>/dev/null | \
    awk 'NR==1 {print "   - Project: " $1} NR==2 {print "   - Region: " $1}'
else
    echo "   ❌ NOT FOUND - Install with: brew install google-cloud-sdk"
fi
echo ""

# Check ADC credentials
echo "5. Google Cloud Credentials:"
if [ -f ~/.config/gcloud/application_default_credentials.json ]; then
    echo "   ✅ Application Default Credentials configured"
else
    echo "   ⚠️  ADC not found - Run: gcloud auth application-default login"
fi
echo ""

echo "=== Summary ==="
echo "If all items show ✅, you're ready to start!"
echo "If any show ❌, install the missing tool."
echo ""
EOF

# Make executable
chmod +x check-installation.sh

# Run verification
./check-installation.sh
```

**Expected Output:**
```
=== Pulumi Installation Verification ===

1. Pulumi CLI:
   ✅ Installed: v3.140.0

2. Python:
   ✅ Installed: Python 3.12.0

3. uv (Package Manager):
   ✅ Installed: uv 0.4.18

4. gcloud CLI:
   ✅ Installed: Google Cloud SDK 455.0.0

   Current config:
   - Project: apex-memory-dev
   - Region: us-central1

5. Google Cloud Credentials:
   ✅ Application Default Credentials configured

=== Summary ===
If all items show ✅, you're ready to start!
```

---

## Step 7: First-Time Pulumi Setup

### Login to Pulumi Cloud (Free Tier)

```bash
# Login to Pulumi Cloud
pulumi login

# Opens browser, authenticate with:
# - GitHub account (recommended)
# - GitLab account
# - Atlassian account
# - Email/password

# After login, you'll see:
# Logged in to pulumi.com as <your-username>
```

**What is Pulumi Cloud?**
- Free tier: 500 resources, 500 deployment minutes/month
- Automatic state storage (no need for S3/GCS buckets)
- Automatic state locking (no race conditions)
- Web UI for visualizing stacks
- **Cost:** $0/month (free tier sufficient for Apex Memory)

**Alternative: Self-Hosted Backend (Advanced)**
```bash
# Use GCS bucket instead of Pulumi Cloud
pulumi login gs://apex-pulumi-state

# Or local filesystem (dev only)
pulumi login file://~/.pulumi
```

**Recommendation:** Start with Pulumi Cloud (free), migrate to GCS later if needed.

---

## Step 8: Create First Pulumi Project

### Navigate to Pulumi Directory

```bash
cd /Users/richardglaubitz/Projects/Apex-Memory-System-Development/deployment/pulumi
```

### Create Virtual Environment with uv

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show: (venv)
```

### Install Python Dependencies

```bash
# Install Pulumi Python packages
uv pip install -r requirements.txt

# Expected output:
# Resolved 10 packages in 150ms
# Installed 10 packages in 1.2s  (100x faster than pip!)
```

### Verify Pulumi Recognizes Python

```bash
# Check Pulumi recognizes Python project
pulumi about

# Expected output should include:
# Plugins:
#   NAME    VERSION
#   python  v3.12.0
```

---

## Step 9: Create First Stack

### Initialize Dev Stack

```bash
# Create dev stack
pulumi stack init dev

# Configure GCP project
pulumi config set gcp:project apex-memory-dev

# Configure region
pulumi config set gcp:region us-central1

# Verify stack configuration
pulumi stack

# Expected output:
# Current stack is dev:
#   Last update: never
#   Resources: 0
```

### Preview Infrastructure (Dry Run)

```bash
# Preview what would be created
pulumi preview

# Expected output (since __main__.py is skeleton):
# Previewing update (dev)
#
# Planned changes:
#   + 12 to create  (GCP APIs enabled)
#
# Resources:
#   + 12 to create
```

---

## Step 10: Test Deployment (Optional)

### Deploy API Enablement

```bash
# Deploy just the API enablement (safe, fast)
pulumi up

# Review changes, type "yes" to confirm

# Expected output:
# Updating (dev)
#
# Resources:
#   + 12 created
#
# Duration: 2m30s
```

### Verify Deployment

```bash
# View stack outputs
pulumi stack output

# Expected output:
# Current stack outputs (1):
#   OUTPUT              VALUE
#   project_id          apex-memory-dev
#   region             us-central1
#   deployment_summary  {...}
```

### Cleanup (If Testing)

```bash
# Destroy test resources
pulumi destroy

# Type "yes" to confirm

# Expected output:
# Destroying (dev)
#
# Resources:
#   - 12 deleted
#
# Duration: 1m15s
```

---

## Troubleshooting

### Issue 1: `pulumi: command not found`

**Cause:** Pulumi CLI not in PATH

**Solution:**
```bash
# If installed via Homebrew
brew info pulumi  # Check if installed

# If installed via curl
echo 'export PATH=$PATH:$HOME/.pulumi/bin' >> ~/.zshrc
source ~/.zshrc
```

---

### Issue 2: `Python version 3.x is not supported`

**Cause:** Python version too old

**Solution:**
```bash
# Check current version
python3 --version

# Install Python 3.12
brew install python@3.12

# Update Pulumi to use new Python
pulumi install python
```

---

### Issue 3: `gcloud: command not found`

**Cause:** gcloud CLI not installed or not in PATH

**Solution:**
```bash
# Install via Homebrew
brew install google-cloud-sdk

# Or add to PATH if already installed
echo 'source "$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc"' >> ~/.zshrc
source ~/.zshrc
```

---

### Issue 4: `Error: could not load plugin pulumi-gcp`

**Cause:** GCP provider plugin not installed

**Solution:**
```bash
# Install GCP provider plugin
pulumi plugin install resource gcp v7.38.0

# Or install all plugins from requirements.txt
pulumi plugin install
```

---

### Issue 5: `Error: Default credentials not found`

**Cause:** Not authenticated with GCP

**Solution:**
```bash
# Login with application default credentials
gcloud auth application-default login

# Verify credentials file exists
ls -la ~/.config/gcloud/application_default_credentials.json
```

---

## Quick Reference Card

**Essential Commands:**

```bash
# Pulumi
pulumi login               # Login to Pulumi Cloud
pulumi stack init <name>   # Create new stack
pulumi preview             # Preview changes (dry run)
pulumi up                  # Deploy infrastructure
pulumi destroy             # Tear down infrastructure
pulumi stack               # View current stack info

# Python/uv
uv venv                    # Create virtual environment
source venv/bin/activate   # Activate venv (macOS/Linux)
uv pip install -r requirements.txt  # Install dependencies

# GCP
gcloud auth login          # Login to Google Cloud
gcloud auth application-default login  # Set up ADC
gcloud config set project <project-id>  # Set default project
gcloud config set compute/region <region>  # Set default region
```

---

## Installation Complete Checklist

Before starting Week 1 implementation, verify:

- [ ] Pulumi CLI installed (`pulumi version`)
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] uv installed (`uv --version`)
- [ ] gcloud CLI installed (`gcloud --version`)
- [ ] Logged into Pulumi Cloud (`pulumi whoami`)
- [ ] Logged into GCP (`gcloud config list`)
- [ ] ADC credentials configured (`ls ~/.config/gcloud/application_default_credentials.json`)
- [ ] Virtual environment created (`source venv/bin/activate`)
- [ ] Dependencies installed (`uv pip list | grep pulumi`)
- [ ] Dev stack created (`pulumi stack`)
- [ ] First preview successful (`pulumi preview`)

**If all boxes are checked, you're ready to start Week 1 implementation!**

---

## Next Steps

1. ✅ Complete installation (this document)
2. ✅ Review [README.md](README.md) - Master guide
3. ✅ Review [ARCHITECTURE-DECISIONS.md](ARCHITECTURE-DECISIONS.md) - Decision matrix
4. ⏭️ Begin Week 1: Create `modules/networking.py`

---

**Installation Issues?** Check troubleshooting section or review research guides in `research/` directory.

**Ready to code?** Let's build `modules/networking.py`!
