# MCP Server Deployment - Issues & Fixes

**Last Updated:** November 7, 2025
**Deployment Status:** 🟡 Phase 2 - Manual Testing (82% complete)

---

## Active Issues

### Issue #1: Python Version Mismatch (CRITICAL)

**Discovered:** November 7, 2025
**Status:** 🔴 Blocking Phase 2 Testing
**Severity:** Critical - Prevents MCP server from starting

#### Problem

Claude Desktop cannot load `apex-mcp-server` package due to Python version mismatch:
- **Claude Desktop uses:** Python 3.14 (`/usr/local/bin/python3`)
- **Package installed in:** Python 3.12
- **Error:** `ModuleNotFoundError: No module named 'apex_mcp_server'`

#### Root Cause

1. System Python was upgraded (likely macOS/Homebrew update)
2. Python 3.14 appeared at `/usr/local/bin/python3`
3. Claude Desktop config uses generic `python3` command
4. Package remains installed in Python 3.12's site-packages
5. Python 3.14 cannot import modules from Python 3.12

#### Evidence

**Error in logs** (`~/Library/Logs/Claude/mcp-server-apex-memory.log`):
```
/usr/local/bin/python3: Error while finding module specification for 'apex_mcp_server.server'
(ModuleNotFoundError: No module named 'apex_mcp_server')
```

**Last occurrence:** 2025-11-07 21:07:16

#### Solution Options

**Option 1: Update Claude Desktop Config (RECOMMENDED)**

✅ Quick fix (1 minute)
✅ Uses stable Python 3.12
✅ No reinstallation needed

```json
// File: ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "apex-memory": {
    "command": "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
    "args": ["-m", "apex_mcp_server.server"],
    "env": { ... }
  }
}
```

**Option 2: Reinstall in Python 3.14**

✅ Uses latest Python
⚠️ Python 3.14 very new (potential compatibility issues)
⚠️ Requires dependency reinstallation

```bash
/usr/local/bin/python3 -m pip install -e /Users/richardglaubitz/Projects/Apex-Memory-System-Development/apex-mcp-server
```

**Option 3: Switch to uvx (FUTURE)**

✅ Automatic environment management
✅ No version conflicts
⚠️ Requires PyPI publishing first

```json
{
  "apex-memory": {
    "command": "uvx",
    "args": ["apex-mcp-server"],
    "env": { ... }
  }
}
```

#### Resolution Plan

**Immediate (Today):**
1. ✅ Apply Option 1 (update config to Python 3.12)
2. ✅ Restart Claude Desktop
3. ✅ Verify MCP server connects
4. ✅ Complete Phase 2 manual testing

**Short-term (This Week):**
- Complete Phases 3-5 (documentation, TestPyPI, PyPI)
- Switch to Option 3 (uvx) after PyPI publish

**Long-term (Future):**
- Consider Python 3.14 compatibility once ecosystem matures

#### Impact Assessment

**Before Fix:**
- ❌ MCP server cannot start
- ❌ Claude Desktop cannot access Apex Memory tools
- ❌ Phase 2 testing blocked
- ❌ PyPI publishing blocked

**After Fix:**
- ✅ MCP server connects successfully
- ✅ Phase 2 testing can proceed
- ✅ Unblocks Phases 3-8

---

## Deployment Blockers

### Blocker #1: Phase 2 Manual Testing (ACTIVE)

**Blocks:** Phases 3-8 (all subsequent phases)
**Status:** 🟡 In Progress
**Estimated Time:** 2-3 hours

**Required Testing:**

- [ ] **Installation Script**
  - Run `./install-apex-mcp.sh`
  - Verify package installs correctly
  - Verify dependencies installed
  - Verify config file created

- [ ] **Claude Desktop Integration**
  - Verify MCP server appears in Claude Desktop
  - Verify server starts without errors
  - Check logs for successful connection

- [ ] **Tool Functionality (10 tools)**
  - [ ] `add_memory()` - Add single message
  - [ ] `add_conversation()` - Add multi-turn conversation
  - [ ] `search_memory()` - Semantic search
  - [ ] `list_recent_memories()` - List episodes
  - [ ] `temporal_search()` - Time-based search
  - [ ] `get_entity_timeline()` - Entity history
  - [ ] `get_communities()` - Community detection
  - [ ] `get_graph_stats()` - Analytics
  - [ ] `search_semantic()` - Pure vector search
  - [ ] `ask_apex()` - LLM orchestration (3-6 queries)

- [ ] **Error Handling**
  - Test with API server down
  - Test with invalid API URL
  - Test with network errors
  - Verify graceful degradation

**Completion Criteria:**
- ✅ Installation script works end-to-end
- ✅ All 10 tools tested and working
- ✅ Error handling verified
- ✅ No errors in Claude Desktop logs

---

## Issue History

### Resolved Issues

None yet - Issue #1 is first recorded issue.

---

## Next Steps (Post-Fix)

### Immediate (After Python Fix)

1. **Complete Phase 2 Testing** (2-3 hours)
   - Test all 10 MCP tools
   - Document test results
   - Update deployment checklist

2. **Move to Phase 3: Documentation Review** (1 hour)
   - Review `deployment/mcp-server/DEPLOYMENT-CHECKLIST.md`
   - Review `apex-mcp-server/README.md`
   - Verify all documentation accurate

3. **Phase 4: TestPyPI Publishing** (30 minutes)
   - Build package: `python -m build`
   - Upload to TestPyPI: `twine upload --repository testpypi dist/*`
   - Test installation: `pip install --index-url https://test.pypi.org/simple/ apex-mcp-server`

4. **Phase 5: Production PyPI Publishing** (15 minutes)
   - Final review
   - Upload to PyPI: `twine upload dist/*`
   - Test installation: `pip install apex-mcp-server`

5. **Phase 6: Installation Verification** (30 minutes)
   - Test `uvx apex-mcp-server` on clean machine
   - Verify Claude Desktop integration
   - Document any issues

6. **Phase 7-8: Documentation & Announcement** (1 hour)
   - Update all READMEs with PyPI installation instructions
   - Announce in Claude Desktop MCP community
   - Update deployment status to ✅ Complete

### Total Estimated Time to Complete Deployment

**From current state → PyPI published:** 5-6 hours

**Breakdown:**
- Phase 2: 2-3 hours
- Phase 3: 1 hour
- Phase 4: 30 minutes
- Phase 5: 15 minutes
- Phase 6: 30 minutes
- Phase 7-8: 1 hour

---

## Related Documentation

- **Deployment Checklist:** [DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md)
- **Publishing Guide:** [PUBLISHING.md](PUBLISHING.md)
- **MCP Server README:** `../../apex-mcp-server/README.md`
- **Investigation Report:** (This document, Section 1)

---

## Notes

### Why This Wasn't Caught Earlier

- MCP server only fails on Claude Desktop startup
- No automated health checks for Claude Desktop integration
- Error only visible in Claude Desktop logs (not terminal)
- Python version mismatch is environment-specific

### Lessons Learned

1. **Add Health Check:** Create automated MCP server health check
2. **Document Python Version:** Document required Python version in README
3. **Use uvx Early:** Recommend uvx from the start to avoid version conflicts
4. **Test in Clean Environment:** Test installation on clean machine before publishing

### Prevention for Future

**Recommendations:**
1. Add `python_requires=">=3.11,<3.15"` to `pyproject.toml`
2. Create automated Claude Desktop integration test
3. Add health check endpoint to MCP server
4. Document Python version in installation instructions
5. Switch to uvx immediately after PyPI publish

---

**Document Status:** Active - Will be updated as issues are discovered and resolved
