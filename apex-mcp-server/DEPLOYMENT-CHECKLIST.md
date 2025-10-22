# Apex MCP Server - Deployment Task List

**Mission:** Ship the Apex MCP Server to production with npm-style installation

**Status:** 🟡 Pre-Production (Testing Phase)

---

## 📋 Pre-Deployment Checklist

### Phase 1: Testing & Validation ✅ COMPLETE

- [x] **Unit tests passing** - 17/17 tests ✅
- [x] **Package installable locally** - `pip install -e .` works ✅
- [x] **Console script working** - `apex-mcp-server` command registered ✅
- [x] **Config templates created** - uvx, pipx, local variants ✅
- [x] **Documentation complete** - README, INSTALLATION, EXAMPLES, TROUBLESHOOTING, PUBLISHING ✅

### Phase 2: Manual Testing (IN PROGRESS)

**Owner:** You
**Deadline:** Before PyPI publish

- [ ] **Install script tested**
  ```bash
  cd apex-mcp-server
  ./install-apex-mcp.sh
  ```
  - [ ] Verify Python version check works
  - [ ] Verify Apex API connectivity check works
  - [ ] Verify package installs correctly
  - [ ] Verify Claude Desktop config created
  - [ ] Verify .env file created

- [ ] **Claude Desktop integration tested**
  - [ ] Add config to Claude Desktop
  - [ ] Restart Claude Desktop completely (⌘+Q)
  - [ ] Verify MCP server appears in Claude Desktop
  - [ ] Test basic memory: "Remember I prefer Python"
  - [ ] Test search: "What do you remember?"
  - [ ] Test ask_apex(): "Tell me everything about [topic]"
  - [ ] Verify logs at `~/Library/Logs/Claude/mcp*.log`

- [ ] **All 10 tools tested**
  - [ ] `add_memory()` - Store single memory
  - [ ] `add_conversation()` - Multi-turn conversation
  - [ ] `search_memory()` - Semantic search
  - [ ] `list_recent_memories()` - Recent episodes
  - [ ] `clear_memories()` - Delete data (with confirmation)
  - [ ] `temporal_search()` - Point-in-time queries
  - [ ] `get_entity_timeline()` - Entity evolution
  - [ ] `get_communities()` - Knowledge clusters
  - [ ] `get_graph_stats()` - Analytics
  - [ ] `ask_apex()` - **THE KILLER FEATURE** - Multi-query orchestration

- [ ] **Error handling tested**
  - [ ] Missing Anthropic API key (ask_apex should fail gracefully)
  - [ ] Apex API down (should show clear error)
  - [ ] Invalid user input (should validate)

### Phase 3: PyPI Publishing Setup

**Owner:** You
**Deadline:** Before first publish

- [ ] **PyPI account setup**
  - [ ] Create account at https://pypi.org/account/register/
  - [ ] Enable 2FA
  - [ ] Create API token: https://pypi.org/manage/account/token/
  - [ ] Store token securely (keyring or ~/.pypirc)

- [ ] **Build tools installed**
  ```bash
  pip install build twine
  ```

- [ ] **Package metadata verified**
  - [ ] Check `pyproject.toml` name: "apex-mcp-server"
  - [ ] Check version: "0.1.0"
  - [ ] Check description is clear
  - [ ] Check authors/email correct
  - [ ] Check license: MIT
  - [ ] Check requires-python: ">=3.11"

- [ ] **Package name availability**
  - [ ] Search PyPI: https://pypi.org/search/?q=apex-mcp-server
  - [ ] Confirm "apex-mcp-server" is available
  - [ ] If taken, choose alternative name

### Phase 4: Test Publishing (TestPyPI)

**Owner:** You
**Deadline:** Before production publish

- [ ] **Create TestPyPI account**
  - [ ] Register: https://test.pypi.org/account/register/
  - [ ] Create separate API token for TestPyPI

- [ ] **Build package**
  ```bash
  rm -rf dist/ build/ *.egg-info
  python -m build
  ```

- [ ] **Upload to TestPyPI**
  ```bash
  twine upload --repository testpypi dist/*
  ```

- [ ] **Test installation from TestPyPI**
  ```bash
  uvx --index-url https://test.pypi.org/simple/ apex-mcp-server --help
  ```

- [ ] **Verify it works**
  - [ ] Server starts without errors
  - [ ] Config loads correctly
  - [ ] Can connect to Apex API

---

## 🚀 Production Deployment

### Phase 5: PyPI Production Publishing

**Owner:** You
**Status:** ⏸️ WAITING (blocked by Phase 2-4)

- [ ] **Final version bump** (if needed)
  - [ ] Update version in `pyproject.toml`: `0.1.0`
  - [ ] Commit: `git commit -am "chore: Release v0.1.0"`

- [ ] **Build production package**
  ```bash
  rm -rf dist/ build/ *.egg-info
  python -m build
  ```

- [ ] **Verify build artifacts**
  ```bash
  ls -lh dist/
  # Should see:
  # apex_mcp_server-0.1.0-py3-none-any.whl
  # apex-mcp-server-0.1.0.tar.gz
  ```

- [ ] **Publish to PyPI**
  ```bash
  twine upload dist/*
  # Username: __token__
  # Password: <PyPI API token>
  ```

- [ ] **Verify on PyPI**
  - [ ] Check page: https://pypi.org/project/apex-mcp-server/
  - [ ] Verify description renders correctly
  - [ ] Verify all links work

- [ ] **Test npm-style installation**
  ```bash
  # Fresh terminal, no local install
  uvx apex-mcp-server --help
  ```

- [ ] **Test with Claude Desktop**
  - [ ] Use `uvx` config template
  - [ ] Restart Claude Desktop
  - [ ] Test all 10 tools again

### Phase 6: GitHub Release

**Owner:** You
**Status:** ⏸️ WAITING (after PyPI publish)

- [ ] **Create git tag**
  ```bash
  git tag v0.1.0
  git push origin v0.1.0
  ```

- [ ] **Create GitHub release**
  - [ ] Go to: https://github.com/your-org/apex-mcp-server/releases/new
  - [ ] Tag: `v0.1.0`
  - [ ] Title: "Release v0.1.0 - Initial Release"
  - [ ] Description: See changelog template below

- [ ] **Upload release artifacts**
  - [ ] Attach `dist/apex_mcp_server-0.1.0-py3-none-any.whl`
  - [ ] Attach `dist/apex-mcp-server-0.1.0.tar.gz`

**Changelog Template:**
```markdown
# Apex MCP Server v0.1.0 - Initial Release

## 🌟 Highlights

**The industry's first MCP server with intelligent multi-query orchestration!**

- 🧠 **ask_apex()** - Claude orchestrates 3-6 queries and synthesizes narrative answers
- 🚀 **npm-style installation** - Just `uvx apex-mcp-server`
- 📊 **10 tools** - 5 basic + 4 advanced + 1 intelligence
- 🏆 **Differentiator** - Multi-query orchestration (unique vs OpenMemory/Graphiti MCP)

## ✨ Features

### Basic Tools (5)
- `add_memory()` - Store memories with LLM entity extraction
- `add_conversation()` - Multi-turn conversations
- `search_memory()` - Intelligent semantic search
- `list_recent_memories()` - Recent episodes
- `clear_memories()` - Data deletion

### Advanced Tools (4)
- `temporal_search()` - Point-in-time queries
- `get_entity_timeline()` - Entity evolution tracking
- `get_communities()` - Knowledge clusters
- `get_graph_stats()` - Graph analytics

### Intelligence (1)
- `ask_apex()` - **THE KILLER FEATURE**
  - Orchestrates 3-6 queries automatically
  - Synthesizes narrative answers
  - Suggests follow-ups
  - Returns insights and confidence scores

## 📦 Installation

```json
{
  "mcpServers": {
    "apex-memory": {
      "command": "uvx",
      "args": ["apex-mcp-server"],
      "env": {
        "APEX_API_URL": "http://localhost:8000",
        "ANTHROPIC_API_KEY": "your-api-key"
      }
    }
  }
}
```

Restart Claude Desktop and start talking!

## 📚 Documentation

- [README](README.md) - Overview and features
- [INSTALLATION](INSTALLATION.md) - Installation guide
- [EXAMPLES](EXAMPLES.md) - Usage examples
- [TROUBLESHOOTING](TROUBLESHOOTING.md) - Common issues
- [PUBLISHING](PUBLISHING.md) - PyPI publishing guide

## 🐛 Known Issues

None at release.

## 🙏 Acknowledgments

Built on top of:
- Model Context Protocol (Anthropic)
- Apex Memory System
- FastMCP
- Graphiti

---

**Full Changelog:** v0.1.0 (initial release)
```

### Phase 7: Documentation Updates

**Owner:** You
**Status:** ⏸️ WAITING (after PyPI publish)

- [ ] **Update main project README**
  - [ ] File: `Apex-Memory-System-Development/README.md`
  - [ ] Add PyPI install badge
  - [ ] Update installation instructions with PyPI link

- [ ] **Update CLAUDE.md files**
  - [ ] File: `Apex-Memory-System-Development/CLAUDE.md`
  - [ ] File: `apex-memory-system/CLAUDE.md`
  - [ ] Note that PyPI package is available

- [ ] **Update upgrade docs**
  - [ ] File: `upgrades/completed/apex-mcp-server/README.md`
  - [ ] Add PyPI package link
  - [ ] Update status to "Published"

### Phase 8: Monitoring & Post-Launch

**Owner:** You
**Timeline:** First 7 days after launch

- [ ] **Monitor PyPI stats**
  - [ ] Check downloads: https://pypistats.org/packages/apex-mcp-server
  - [ ] Monitor for issues
  - [ ] Respond to user feedback

- [ ] **Monitor logs**
  - [ ] Check `~/Library/Logs/Claude/mcp*.log`
  - [ ] Look for common errors
  - [ ] Document patterns

- [ ] **Gather user feedback**
  - [ ] Create GitHub Discussions
  - [ ] Monitor GitHub Issues
  - [ ] Track feature requests

- [ ] **Performance metrics**
  - [ ] Track ask_apex() usage
  - [ ] Measure response times
  - [ ] Monitor API errors

---

## 🔄 Future Releases

### Version 0.1.1 (Bug Fixes)

- [ ] **Prepare**
  - [ ] Fix any bugs discovered
  - [ ] Update version: `0.1.0` → `0.1.1`
  - [ ] Update CHANGELOG.md

- [ ] **Publish**
  ```bash
  python -m build
  twine upload dist/*
  git tag v0.1.1
  git push origin v0.1.1
  ```

### Version 0.2.0 (New Features)

- [ ] **Plan features**
  - [ ] Response streaming
  - [ ] Query caching
  - [ ] Multi-user support
  - [ ] Visualization integration

- [ ] **Implement & Test**
  - [ ] Add tests for new features
  - [ ] Update documentation
  - [ ] Update version: `0.1.x` → `0.2.0`

- [ ] **Publish**
  - [ ] Same process as 0.1.1

---

## 📊 Success Metrics

Track these after launch:

| Metric | Target | Actual |
|--------|--------|--------|
| **PyPI Downloads (Week 1)** | 10+ | ___ |
| **PyPI Downloads (Month 1)** | 50+ | ___ |
| **GitHub Stars** | 25+ | ___ |
| **Issues Opened** | <5 critical bugs | ___ |
| **User Satisfaction** | >80% positive | ___ |
| **Claude Desktop Compatibility** | 100% | ___ |

---

## 🚨 Rollback Plan

If major issues discovered after launch:

### Critical Bug Rollback

1. **Yank bad version from PyPI**
   ```bash
   # Contact PyPI support or use web interface
   # https://pypi.org/manage/project/apex-mcp-server/releases/
   ```

2. **Publish hotfix**
   ```bash
   # Fix bug
   # Bump version: 0.1.0 → 0.1.1
   python -m build
   twine upload dist/*
   ```

3. **Notify users**
   - [ ] GitHub issue
   - [ ] Release notes
   - [ ] README warning

---

## 🎯 Current Priorities

**Next Actions (in order):**

1. ✅ ~~Create deployment checklist~~ (you're reading it!)
2. ⏸️ **Manual testing** (Phase 2) - YOU NEED TO DO THIS
3. ⏸️ **PyPI account setup** (Phase 3)
4. ⏸️ **TestPyPI publish** (Phase 4)
5. ⏸️ **Production PyPI publish** (Phase 5)
6. ⏸️ **GitHub release** (Phase 6)

---

## 📝 Notes

### Testing Results

**Date:** _____

**Tested by:** _____

**Results:**
- [ ] Install script: PASS / FAIL
- [ ] Claude Desktop: PASS / FAIL
- [ ] All 10 tools: PASS / FAIL
- [ ] Error handling: PASS / FAIL

**Issues found:**
1. _______________
2. _______________
3. _______________

### PyPI Publishing

**Date:** _____

**Published by:** _____

**Package URL:** https://pypi.org/project/apex-mcp-server/

**Issues encountered:**
- _______________

---

## 🔗 Quick Links

- **PyPI:** https://pypi.org/project/apex-mcp-server/ (after publish)
- **GitHub:** https://github.com/your-org/apex-mcp-server
- **Documentation:** [README.md](README.md)
- **Issues:** https://github.com/your-org/apex-mcp-server/issues
- **Publishing Guide:** [PUBLISHING.md](PUBLISHING.md)

---

**Last Updated:** 2025-10-21
**Next Review:** After manual testing (Phase 2)
**Deployment Status:** 🟡 Pre-Production (82% complete - awaiting manual tests)
