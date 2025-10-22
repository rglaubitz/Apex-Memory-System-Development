# Publishing to PyPI

This guide explains how to publish `apex-mcp-server` to PyPI so users can install it with `uvx` or `pipx` (npm-style).

---

## 📦 Why Publish to PyPI?

Publishing to PyPI enables **npm-style installation**:

```json
// Users just add this to Claude Desktop config
{
  "mcpServers": {
    "apex-memory": {
      "command": "uvx",
      "args": ["apex-mcp-server"]
    }
  }
}
```

No manual installation needed! `uvx` auto-downloads from PyPI.

---

## 🚀 Publishing Steps

### 1. Prerequisites

```bash
# Install build tools
pip install build twine

# Get PyPI account
# 1. Create account: https://pypi.org/account/register/
# 2. Enable 2FA
# 3. Create API token: https://pypi.org/manage/account/token/
```

### 2. Prepare Package

**Update version in `pyproject.toml`:**

```toml
[project]
name = "apex-mcp-server"
version = "0.1.0"  # Increment this for each release (e.g., 0.1.1, 0.2.0)
```

**Version numbering:**
- `0.1.0` → `0.1.1` - Bug fixes
- `0.1.0` → `0.2.0` - New features
- `0.1.0` → `1.0.0` - Breaking changes

**Verify package metadata:**

```bash
# Check pyproject.toml
cat pyproject.toml

# Ensure these are correct:
# - name: "apex-mcp-server"
# - version: "X.Y.Z"
# - description
# - authors
# - license
# - requires-python: ">=3.11"
```

### 3. Run Tests

```bash
# Ensure all tests pass before publishing
pytest -v

# Expected: 17/17 tests passing
```

### 4. Build Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build wheel and source distribution
python -m build

# This creates:
# dist/apex_mcp_server-0.1.0-py3-none-any.whl
# dist/apex-mcp-server-0.1.0.tar.gz
```

### 5. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation
uvx --index-url https://test.pypi.org/simple/ apex-mcp-server --help

# If it works, proceed to real PyPI
```

### 6. Publish to PyPI

```bash
# Upload to real PyPI
twine upload dist/*

# You'll be prompted for:
# - Username: __token__
# - Password: <your PyPI API token>
```

### 7. Verify Installation

```bash
# Test npm-style installation
uvx apex-mcp-server --help

# Should show:
# "Starting Apex MCP Server..."
```

---

## 📋 Post-Publishing Checklist

After publishing, update documentation:

- [ ] **README.md** - Update installation instructions
- [ ] **GitHub Releases** - Create release tag with changelog
- [ ] **Documentation** - Update version numbers
- [ ] **Upgrade docs** - Document in `upgrades/completed/apex-mcp-server/`

---

## 🔄 Publishing Workflow (Future Releases)

For subsequent releases:

```bash
# 1. Make changes
git add .
git commit -m "feat: New feature description"

# 2. Update version in pyproject.toml
# 0.1.0 → 0.1.1 (bug fix)
# 0.1.0 → 0.2.0 (new feature)
# 0.1.0 → 1.0.0 (breaking change)

# 3. Run tests
pytest -v

# 4. Build and publish
rm -rf dist/
python -m build
twine upload dist/*

# 5. Create git tag
git tag v0.1.1
git push origin v0.1.1

# 6. Create GitHub release
# Go to: https://github.com/your-org/apex-mcp-server/releases/new
# Tag: v0.1.1
# Title: "Release v0.1.1 - Bug fixes"
# Description: Changelog
```

---

## 🔐 Security Best Practices

### PyPI API Token

**Store securely:**

```bash
# Option 1: Use keyring
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__

# Option 2: Use ~/.pypirc
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
EOF
chmod 600 ~/.pypirc
```

**NEVER commit API tokens to git!**

### Package Security

- ✅ Enable 2FA on PyPI account
- ✅ Use API tokens (not password)
- ✅ Limit token scope to single project
- ✅ Rotate tokens regularly
- ✅ Review all files in dist/ before uploading

---

## 📊 Package Statistics

After publishing, monitor:

- **Downloads:** https://pypistats.org/packages/apex-mcp-server
- **Security:** https://pypi.org/project/apex-mcp-server/
- **Issues:** GitHub Issues

---

## 🐛 Troubleshooting

### "Package already exists"

```bash
# Error: File already exists on PyPI
# Solution: Increment version number in pyproject.toml
```

### "Invalid distribution"

```bash
# Error: Missing required metadata
# Solution: Check pyproject.toml has all required fields:
# - name, version, description, authors, readme, license
```

### "Uploaded successfully but can't install"

```bash
# Wait 1-2 minutes for PyPI CDN to update
# Then try: uvx apex-mcp-server --help
```

### "Import error when running"

```bash
# Check dependencies in pyproject.toml are correct
# Test locally first: pip install -e . && python -m apex_mcp_server.server
```

---

## 📚 Resources

- **PyPI Packaging Guide:** https://packaging.python.org/tutorials/packaging-projects/
- **PyPI API Tokens:** https://pypi.org/help/#apitoken
- **Twine Documentation:** https://twine.readthedocs.io/
- **uv Documentation:** https://github.com/astral-sh/uv

---

## ✅ Quick Checklist

Before publishing:

- [ ] All tests passing (`pytest -v`)
- [ ] Version incremented in `pyproject.toml`
- [ ] `dist/` cleaned (`rm -rf dist/`)
- [ ] Built distribution (`python -m build`)
- [ ] Reviewed files in `dist/`
- [ ] PyPI API token configured
- [ ] Uploaded to PyPI (`twine upload dist/*`)
- [ ] Tested installation (`uvx apex-mcp-server --help`)
- [ ] Created git tag
- [ ] Created GitHub release
- [ ] Updated documentation

---

**First-time publishing?** Follow steps 1-7 above.

**Subsequent releases?** Use the "Publishing Workflow" section.
