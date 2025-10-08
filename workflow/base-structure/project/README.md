# [Project Name]

**Your main project codebase**

This directory contains the actual implementation codebase. This is typically a symlink to your project repository or a git submodule.

---

## Overview

This is the **main project directory** that contains your actual source code, tests, and project-specific files.

**What goes here:**
- Source code (`src/`)
- Tests (`tests/`)
- Configuration files
- Package management (`requirements.txt`, `package.json`, etc.)
- Docker configurations
- CI/CD pipelines
- Project-specific documentation

**What doesn't go here:**
- Research documentation (goes in `../research/`)
- Upgrade planning (goes in `../upgrades/`)
- Workflow documentation (goes in `../workflow/`)
- Claude configuration (goes in `../.claude/`)

---

## Recommended Setup

### Option A: Symlink (Recommended)

```bash
# Link to your actual project repository
ln -s /path/to/your/actual/project ./project-name

# Or use relative path
ln -s ../path/to/project ./project-name
```

**Benefits:**
- Keep project in its own repository
- Separate git history for project and development system
- Easy to update project independently

### Option B: Git Submodule

```bash
# Add project as submodule
git submodule add https://github.com/your-org/your-project.git project-name
git submodule update --init --recursive
```

**Benefits:**
- Version controlled relationship
- Explicit project version tracking
- Good for multiple collaborators

### Option C: Direct Directory

```bash
# Clone project directly
cd workflow-directory
git clone https://github.com/your-org/your-project.git project-name
```

**Note:** Add to `.gitignore` to avoid nested repositories

---

## Directory Structure

**Typical project structure:**

```
project-name/
├── src/                    # Source code
│   └── [your-module]/     # Module directories
│       ├── __init__.py
│       └── *.py
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                   # Project-specific docs
├── docker/                 # Docker configurations
│   └── docker-compose.yml
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── README.md              # Project README
└── CLAUDE.md             # Project-specific Claude instructions
```

---

## Integration with Development System

### Research Integration

**Link research to implementation:**

```python
# In your code, reference research decisions
"""
Query routing implementation.

Based on research:
- ../research/documentation/query-routing/semantic-router.md
- ../research/documentation/query-routing/adaptive-routing-learning.md

Uses semantic-router 0.1.11 (verified Oct 2025)
"""
```

### Upgrade Integration

**Track upgrades affecting this project:**

```
../upgrades/
├── active/query-router/        # Currently implementing
├── planned/security-layer/     # Next upgrade
└── completed/documentation/    # Previous upgrade
```

### Claude Configuration

**Project-specific Claude instructions:**

Create `CLAUDE.md` in project root:

```markdown
# Project-Specific Claude Instructions

## Code Style
- [Your code style]

## Testing Requirements
- [Your test requirements]

## Dependencies
- [Key dependencies]

## Common Commands
- [Frequent commands]
```

---

## Development Workflow

### 1. Feature Development

```bash
# Start in development system root
cd /path/to/development-system

# Research phase
# Document in research/

# Planning phase
# Create in upgrades/planned/[feature]/

# Implementation phase
cd project-name/
# Implement feature
# Run tests
# Commit
```

### 2. Running Project

```bash
# Navigate to project
cd project-name/

# Setup environment
cp .env.example .env
# Edit .env with your values

# Install dependencies
pip install -r requirements.txt

# Start services (if using Docker)
docker-compose up -d

# Run application
python -m your_module
```

### 3. Testing

```bash
# Navigate to project
cd project-name/

# Run all tests
pytest

# Run specific test suite
pytest tests/unit/ -v

# Run with coverage
pytest --cov=your_module --cov-report=html
```

---

## Project Documentation

### Keep in Project

**These stay in project directory:**
- API documentation
- Installation instructions
- Usage guides
- Contribution guidelines
- License
- Changelog

### Keep in Development System

**These go in parent directory:**
- Research documentation (`../research/`)
- Upgrade plans (`../upgrades/`)
- Workflow documentation (`../workflow/`)
- Architecture Decision Records (`../research/architecture-decisions/`)

---

## Environment Management

### Environment Variables

```bash
# In project root
.env                 # Local config (gitignored)
.env.example        # Template (committed)
```

**Example `.env.example`:**
```bash
# Database
DATABASE_URL=postgresql://localhost/mydb

# APIs
API_KEY=your_api_key_here

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Dependencies

**Python:**
```txt
# requirements.txt
package-name==1.2.3
another-package>=2.0.0
```

**Node.js:**
```json
{
  "dependencies": {
    "package-name": "^1.2.3"
  }
}
```

---

## Git Workflow

### If Symlink

```bash
# Project has its own git
cd project-name/
git status
git add .
git commit -m "feat: add new feature"
git push

# Development system tracks separately
cd ..
git status  # Symlink not tracked
```

### If Submodule

```bash
# Update project
cd project-name/
git pull origin main

# Update submodule reference in parent
cd ..
git add project-name
git commit -m "chore: update project submodule"
git push
```

---

## Best Practices

### DO ✅

1. **Separate concerns** - Project code separate from research/upgrades
2. **Use symlink or submodule** - Don't duplicate repositories
3. **Keep .env in .gitignore** - Never commit secrets
4. **Document project-specific Claude instructions** - Create CLAUDE.md
5. **Reference research in code comments** - Link to research docs
6. **Run tests before committing** - Maintain code quality

### DON'T ❌

1. **Mix research with source code** - Keep research in ../research/
2. **Commit .env files** - Always use .env.example
3. **Skip project README** - Document setup clearly
4. **Ignore dependency versions** - Pin versions in requirements
5. **Commit without testing** - Always run tests first

---

## Common Commands

### Setup

```bash
# Initial setup
cd project-name/
cp .env.example .env
pip install -r requirements.txt
docker-compose up -d
```

### Development

```bash
# Run application
python -m your_module

# Run tests
pytest -v

# Format code
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

### Docker

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

## Integration Examples

### Research-Backed Implementation

```python
# src/your_module/component.py

"""
Component implementing [feature].

Research foundation:
- [Framework]: ../research/documentation/[framework]/[doc].md
- [Pattern]: ../research/examples/[pattern]/[example].md

Upgrade tracking:
- Implemented in: ../upgrades/active/[feature]/

Architecture decision:
- Decision rationale: ../research/architecture-decisions/ADR-001.md

Version: [framework]==[version] (verified Oct 2025)
"""

from framework import Feature

class Component:
    """Implementation of [feature]."""

    def __init__(self):
        # Based on research recommendation
        self.feature = Feature(
            param=value  # From ADR-001
        )
```

### Upgrade-Tracked Code

```python
# src/your_module/upgraded_component.py

"""
Component upgraded in [upgrade-name].

Upgrade details:
- Plan: ../upgrades/completed/[upgrade]/IMPROVEMENT-PLAN.md
- Phase: Phase 2 (Intelligent Features)
- Date: October 2025

Changes from original:
- Added [feature]
- Improved [aspect]
- Performance: [metric] improvement
"""
```

---

## Troubleshooting

### Symlink Issues

```bash
# If symlink breaks
ls -la  # Check if link exists
rm project-name  # Remove broken link
ln -s /correct/path/to/project project-name  # Recreate
```

### Submodule Issues

```bash
# If submodule is empty
git submodule update --init --recursive

# If submodule is out of date
cd project-name
git pull origin main
cd ..
git add project-name
git commit -m "chore: update submodule"
```

### Environment Issues

```bash
# If dependencies fail
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# If .env is missing
cp .env.example .env
# Edit .env with correct values
```

---

## Next Steps

1. **Setup project link:**
   ```bash
   ln -s /path/to/your/project ./your-project-name
   ```

2. **Create project CLAUDE.md:**
   - Add project-specific instructions
   - Document code style
   - List common commands

3. **Initialize environment:**
   ```bash
   cd your-project-name/
   cp .env.example .env
   pip install -r requirements.txt
   ```

4. **Run tests:**
   ```bash
   pytest -v
   ```

5. **Start development:**
   - Follow Features Implementation Workflow
   - Document research
   - Track upgrades

---

**This is your main codebase. Keep it clean, tested, and well-documented.**
