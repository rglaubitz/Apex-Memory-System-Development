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
        echo "      Install with: brew install python@3.12"
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
    project=$(gcloud config get-value core/project 2>/dev/null)
    region=$(gcloud config get-value compute/region 2>/dev/null)
    if [ -n "$project" ]; then
        echo "   - Project: $project"
    else
        echo "   - Project: (not set) - Run: gcloud config set project <project-id>"
    fi
    if [ -n "$region" ]; then
        echo "   - Region: $region"
    else
        echo "   - Region: (not set) - Run: gcloud config set compute/region us-central1"
    fi
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

# Check Pulumi login status
echo "6. Pulumi Cloud Login:"
if pulumi whoami &> /dev/null; then
    echo "   ✅ Logged in as: $(pulumi whoami)"
else
    echo "   ⚠️  Not logged in - Run: pulumi login"
fi
echo ""

# Summary
echo "=== Summary ==="
all_good=true

if ! command -v pulumi &> /dev/null; then
    all_good=false
fi

if ! command -v python3 &> /dev/null; then
    all_good=false
else
    version=$(python3 --version | cut -d' ' -f2)
    major=$(echo $version | cut -d'.' -f1)
    minor=$(echo $version | cut -d'.' -f2)
    if [ "$major" -ne 3 ] || [ "$minor" -lt 11 ]; then
        all_good=false
    fi
fi

if ! command -v uv &> /dev/null; then
    all_good=false
fi

if ! command -v gcloud &> /dev/null; then
    all_good=false
fi

if $all_good; then
    echo "✅ All required tools are installed!"
    echo ""
    echo "Next steps:"
    echo "1. gcloud auth application-default login  (if not done)"
    echo "2. pulumi login  (if not done)"
    echo "3. cd deployment/pulumi && uv venv && source venv/bin/activate"
    echo "4. uv pip install -r requirements.txt"
    echo "5. pulumi stack init dev"
    echo "6. pulumi preview"
else
    echo "❌ Some required tools are missing. Install them and run this script again."
fi
echo ""
