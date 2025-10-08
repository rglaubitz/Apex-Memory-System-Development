# .claude/

**Project-specific Claude Code configuration**

This directory contains your project-specific Claude Code configuration, separate from global user configuration.

---

## Overview

The `.claude/` directory allows you to customize Claude Code behavior on a per-project basis.

**What goes here:**
- Project-specific commands (slash commands)
- Custom agents for your project
- Project settings (gitignored)
- Project-specific prompts

**What doesn't go here:**
- Global user preferences (those go in `~/.claude/`)
- Source code (goes in project directory)
- Research (goes in `../research/`)

---

## Directory Structure

```
.claude/
├── README.md                    # This file
├── commands/                    # Project-specific slash commands
│   └── [command-name].md       # Command definitions
├── agents/                      # Project-specific agents
│   └── [agent-name].md         # Agent definitions
├── settings.local.json          # Project settings (gitignored)
└── prompts/                     # Reusable prompts
    └── [prompt-name].md        # Prompt templates
```

---

## Settings

### settings.local.json

**This file is gitignored** - it contains local configuration that shouldn't be shared.

```json
{
  "mcpServers": {
    "custom-server": {
      "command": "node",
      "args": ["/path/to/server.js"]
    }
  }
}
```

### settings.json (Optional)

**This file can be committed** - shared project settings.

```json
{
  "globalShortcut": "Ctrl+Shift+Space",
  "theme": "dark"
}
```

---

## Commands (Slash Commands)

### Creating Custom Commands

Commands go in `.claude/commands/[name].md`

**Example: `.claude/commands/test-feature.md`**

```markdown
---
description: Run tests for specific feature
---

Run the complete test suite for a feature:

1. Navigate to project: cd [PROJECT_NAME]
2. Run unit tests: pytest tests/unit/test_[FEATURE]*.py -v
3. Run integration tests: pytest tests/integration/test_[FEATURE]*.py -v
4. Check coverage: pytest tests/ --cov=[FEATURE] --cov-report=html
5. Report results

Use this when you need to validate a feature implementation.
```

**Usage:**
```
/test-feature query-router
```

### Common Project Commands

Create these commands for your project:

1. **`/setup-dev`** - Setup development environment
2. **`/run-tests`** - Run project test suite
3. **`/deploy-staging`** - Deploy to staging
4. **`/review-pr`** - Review pull request
5. **`/update-docs`** - Update documentation

---

## Agents

### Creating Custom Agents

Agents go in `.claude/agents/[name].md`

**Example: `.claude/agents/project-tester.md`**

```markdown
# Project Tester Agent

**Role:** Specialized testing agent for [PROJECT_NAME]

**Capabilities:**
- Run complete test suite
- Identify failing tests
- Suggest fixes for common failures
- Update test coverage reports

**Tools:** Bash, Read, Write, Grep

**When to use:**
- After implementing new features
- Before merging pull requests
- When tests are failing
- To improve test coverage

**Workflow:**
1. Run pytest with verbose output
2. Identify failures
3. Read failing test code
4. Suggest fixes or improvements
5. Update coverage report

**Example usage:**
```
You: "Test the query router feature"
Agent: [Runs tests, identifies failures, suggests fixes]
```
```

### Common Project Agents

**Consider creating:**

1. **project-tester** - Test execution and validation
2. **code-reviewer** - Code quality and standards
3. **doc-updater** - Documentation maintenance
4. **dependency-checker** - Dependency updates
5. **deployment-helper** - Deployment assistance

---

## Prompts

### Reusable Prompt Templates

Prompts go in `.claude/prompts/[name].md`

**Example: `.claude/prompts/code-review.md`**

```markdown
# Code Review Prompt

Review the following code for:

## Code Quality
- [ ] Follows project code style
- [ ] Proper error handling
- [ ] Clear variable names
- [ ] Appropriate comments

## Testing
- [ ] Unit tests present
- [ ] Edge cases covered
- [ ] Integration tests if needed

## Documentation
- [ ] Docstrings present
- [ ] README updated if needed
- [ ] CHANGELOG updated

## Performance
- [ ] No obvious performance issues
- [ ] Appropriate data structures
- [ ] Efficient algorithms

Provide specific feedback with code suggestions.
```

---

## Configuration Examples

### Example Command: Run Tests

**File:** `.claude/commands/test.md`

```markdown
---
description: Run project test suite
---

Run the complete test suite for [PROJECT_NAME]:

```bash
cd [PROJECT_NAME]/

# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

Expected results:
- All tests passing
- Coverage >= 80%

If tests fail, investigate and fix before proceeding.
```

**Usage:**
```
/test
```

### Example Agent: Deployment Helper

**File:** `.claude/agents/deployment-helper.md`

```markdown
# Deployment Helper

**Role:** Assists with safe deployment to production

**Capabilities:**
- Pre-deployment validation
- Deployment execution
- Post-deployment monitoring
- Rollback if needed

**Tools:** Bash, Read, Write, WebFetch

**Safety Checks:**
1. All tests passing
2. No uncommitted changes
3. Documentation updated
4. Deployment manual followed

**Workflow:**
1. Run pre-deployment checks
2. Create deployment branch
3. Execute deployment steps
4. Monitor deployment
5. Validate success
6. Rollback if issues detected

**Example usage:**
```
You: "Deploy query router to production"
Agent: [Runs checks, deploys, monitors]
```
```

---

## Best Practices

### DO ✅

1. **Gitignore settings.local.json** - Contains local paths
2. **Document all commands** - Clear descriptions
3. **Create project-specific agents** - Specialized helpers
4. **Use prompts for repetitive tasks** - Save time
5. **Keep commands simple** - One clear purpose each

### DON'T ❌

1. **Commit secrets in settings** - Always gitignore
2. **Create too many commands** - Keep focused
3. **Duplicate global commands** - Use global when possible
4. **Skip documentation** - Document all customizations
5. **Hardcode paths** - Use placeholders

---

## Integration with Development System

### Project-Specific vs Global

**Global Configuration** (`~/.claude/`):
- User preferences
- Common commands across projects
- Personal agent settings

**Project Configuration** (`.claude/`):
- Project-specific commands
- Project-specific agents
- Team-shared configuration

### Command Resolution

Claude Code checks in this order:
1. Project `.claude/commands/`
2. Global `~/.claude/commands/`
3. Built-in commands

**Use project commands for:**
- Project-specific workflows
- Team-shared automation
- Project conventions

**Use global commands for:**
- Personal preferences
- Cross-project utilities
- General development tasks

---

## Setup Guide

### 1. Initialize .claude Directory

```bash
# In project root
mkdir -p .claude/{commands,agents,prompts}
```

### 2. Configure .gitignore

```bash
# Add to .gitignore
.claude/settings.local.json
.claude/*.log
```

### 3. Create Initial Commands

```bash
# Create common commands
touch .claude/commands/test.md
touch .claude/commands/deploy.md
touch .claude/commands/review.md
```

### 4. Create settings.local.json

```bash
# Create local settings
cat > .claude/settings.local.json << 'EOF'
{
  "projectRoot": ".",
  "testCommand": "pytest tests/ -v"
}
EOF
```

### 5. Document Configuration

```bash
# Add to project README
echo "## Claude Code Configuration" >> README.md
echo "Project-specific commands available in .claude/commands/" >> README.md
```

---

## Troubleshooting

### Commands Not Working

```bash
# Check command exists
ls .claude/commands/

# Check command format
cat .claude/commands/[command].md

# Check permissions
chmod +x .claude/commands/[command].md
```

### Settings Not Loading

```bash
# Verify settings file exists
cat .claude/settings.local.json

# Check JSON is valid
python -m json.tool < .claude/settings.local.json

# Restart Claude Code
```

### Agents Not Responding

```bash
# Check agent definition
cat .claude/agents/[agent].md

# Verify tools are specified
grep "Tools:" .claude/agents/[agent].md

# Check agent is properly formatted
```

---

## Common Patterns

### Testing Command Pattern

```markdown
---
description: Test [component]
---

1. Navigate to project
2. Run specific tests: pytest tests/[component]/ -v
3. Check coverage
4. Report results
```

### Deployment Command Pattern

```markdown
---
description: Deploy [environment]
---

1. Pre-deployment checks
2. Run tests
3. Build artifacts
4. Deploy to [environment]
5. Verify deployment
6. Monitor for issues
```

### Review Command Pattern

```markdown
---
description: Review [type]
---

1. Read relevant files
2. Check against standards
3. Suggest improvements
4. Update documentation if needed
```

---

## Example Project Setup

### Minimal Setup

```
.claude/
├── README.md
├── commands/
│   ├── test.md
│   └── deploy.md
└── settings.local.json (gitignored)
```

### Full Setup

```
.claude/
├── README.md
├── commands/
│   ├── test.md
│   ├── deploy.md
│   ├── review.md
│   ├── update-docs.md
│   └── check-deps.md
├── agents/
│   ├── project-tester.md
│   ├── deployment-helper.md
│   └── doc-updater.md
├── prompts/
│   ├── code-review.md
│   ├── bug-report.md
│   └── feature-spec.md
└── settings.local.json (gitignored)
```

---

## Next Steps

1. **Create initial commands:**
   ```bash
   mkdir -p .claude/commands
   touch .claude/commands/test.md
   ```

2. **Configure gitignore:**
   ```bash
   echo ".claude/settings.local.json" >> .gitignore
   ```

3. **Create project-specific agents:**
   ```bash
   mkdir -p .claude/agents
   # Add agent definitions
   ```

4. **Document in project README:**
   - List available commands
   - Explain how to use agents
   - Link to this README

---

**Project-specific Claude configuration makes your development workflow more efficient and team collaboration easier.**
