#!/bin/bash

echo "=== Installing Missing Pulumi Tools ==="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install from: https://brew.sh"
    exit 1
fi

# Install Pulumi CLI
echo "1. Installing Pulumi CLI..."
if command -v pulumi &> /dev/null; then
    echo "   ✅ Pulumi already installed: $(pulumi version)"
else
    brew install pulumi
    if [ $? -eq 0 ]; then
        echo "   ✅ Pulumi CLI installed successfully!"
    else
        echo "   ❌ Pulumi installation failed"
    fi
fi
echo ""

# Install gcloud CLI
echo "2. Installing gcloud CLI..."
if command -v gcloud &> /dev/null; then
    echo "   ✅ gcloud already installed: $(gcloud --version | head -1)"
else
    brew install google-cloud-sdk
    if [ $? -eq 0 ]; then
        echo "   ✅ gcloud CLI installed successfully!"
        echo ""
        echo "   ⚠️  IMPORTANT: Add gcloud to your PATH by running:"
        echo "   echo 'source \"\$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc\"' >> ~/.zshrc"
        echo "   source ~/.zshrc"
    else
        echo "   ❌ gcloud installation failed"
    fi
fi
echo ""

echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Run: ./check-installation.sh  (verify all tools installed)"
echo "2. Run: gcloud auth login  (authenticate with Google)"
echo "3. Run: gcloud auth application-default login  (set up ADC)"
echo "4. Run: pulumi login  (authenticate with Pulumi Cloud)"
echo ""
