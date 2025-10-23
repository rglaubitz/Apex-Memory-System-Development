# RDF Workflow - Quick Reference

**RDF = Research, Document, Finalize**

This is the automated workflow we just completed for the query router upgrade.

## How to Use

### Option 1: Full Command
```
/research-document-finalize
```

### Option 2: Short Alias
```
/rdf
```

### Option 3: With Upgrade Name
```
/rdf security-layer
```

## What It Does

The command will automatically:

### Phase 1: Research 📚
1. Read your upgrade's existing documentation
2. Identify critical research questions:
   - Latest versions?
   - Better alternatives?
   - 2025 best practices?
   - Training data needs?
3. Use **Exa** for web research (official docs, articles, benchmarks)
4. Use **GitHub API** for version verification and code examples
5. Only use Tier 1-2 sources (official docs, 1.5k+ star repos)

### Phase 2: Documentation 📝
1. Create research analysis docs (`research/documentation/[topic]/`)
2. Create implementation guide (`upgrades/[name]/IMPLEMENTATION-GUIDE.md`)
3. Create supporting files (`upgrades/[name]/examples/`)
4. Update master plan with research findings

### Phase 3: Finalization ✅
1. Review all created files
2. Git add, commit, push
3. Provide completion summary

## Example Session

```bash
You: /rdf security-layer

Claude: Executing RDF workflow for security-layer...

[Phase 1: Research]
✅ Researching authentication options (OAuth2 vs alternatives)
✅ Researching rate limiting libraries (latest versions)
✅ Researching encryption best practices (2025 standards)

[Phase 2: Documentation]
✅ Created research/documentation/security/oauth2-analysis.md
✅ Created research/documentation/security/rate-limiting-analysis.md
✅ Created upgrades/security-layer/IMPLEMENTATION-GUIDE.md
✅ Created upgrades/security-layer/examples/rate-limit-config.yaml
✅ Updated upgrades/security-layer/IMPROVEMENT-PLAN.md

[Phase 3: Finalization]
✅ Committed: "Add security layer implementation documentation"
✅ Pushed to origin/main

## RDF Workflow Complete

Ready for implementation Phase 1.
```

## When to Use RDF

**Use RDF workflow when:**
- ✅ Starting implementation of a planned upgrade
- ✅ Need to verify latest versions and alternatives
- ✅ Want comprehensive research-backed documentation
- ✅ Need implementation guide with complete examples
- ✅ Ready to commit research and docs to git

**Don't use RDF for:**
- ❌ Quick bug fixes (too heavyweight)
- ❌ Simple code changes (use regular development flow)
- ❌ Just reading/exploring code (use normal tools)

## Quality Guarantees

When RDF completes, you'll have:

**Research Quality:**
- ✅ Minimum 3 sources per question
- ✅ All Tier 1-2 sources (official docs, verified repos)
- ✅ Latest versions verified
- ✅ Comprehensive comparison tables

**Documentation Quality:**
- ✅ Complete code examples (no pseudocode)
- ✅ Exact version numbers
- ✅ Clear decision rationale
- ✅ All sources cited with URLs
- ✅ Cross-references between docs

**Implementation Quality:**
- ✅ Step-by-step instructions
- ✅ Pre-flight verification steps
- ✅ Testing strategies
- ✅ Rollback procedures

## Real Example: Query Router

We just used this workflow (manually) to create:

**Research Docs Created:**
1. `semantic-router-analysis.md` - Version 0.1.11 verified as latest
2. `claude-vs-openai-query-rewriting.md` - Claude 3.5 Sonnet superior
3. `async-best-practices-2025.md` - Full async recommended

**Implementation Docs Created:**
4. `IMPLEMENTATION-GUIDE.md` - Complete step-by-step guide
5. `training-queries.json` - 48 example queries

**Updated:**
6. `IMPROVEMENT-PLAN.md` - Latest versions and research links

**Result:**
- Commit `f2af155` with comprehensive documentation
- Ready for Phase 1 implementation
- All research questions answered with authoritative sources

## Pro Tips

1. **Let it run fully** - The workflow is designed to be autonomous
2. **Trust the research** - It uses the same Tier 1-2 source standards we established
3. **Review the output** - Check the summary to see what was created
4. **Use for planned upgrades** - Best for upgrades in `upgrades/planned/` or `upgrades/[name]/`

## Troubleshooting

**If command not found:**
```bash
ls ~/.claude/commands/ | grep rdf
```

Should show:
- `research-document-finalize.md`
- `rdf.md`

**If research incomplete:**
- Check that Exa and GitHub MCP servers are running
- Verify internet connection for web research

**If git operations fail:**
- Ensure git is configured
- Check for uncommitted changes
- Verify write permissions

## Next Steps

Try it out on your next upgrade:

```bash
/rdf ingestion-pipeline-v2
```

Or:

```bash
/rdf temporal-intelligence-enhancement
```

The workflow will handle the rest!

---

**Created:** October 7, 2025
**Based on:** Query Router Implementation Success
**Workflow Version:** 1.0
