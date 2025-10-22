# Testing Guide - Query Router

**Complete guide for test execution, interpretation, and fixing failures**

---

## 📋 Overview

The query router has **223 comprehensive tests** across all 4 phases:
- **Phase 1:** 60 tests (semantic classification, query rewriting, analytics)
- **Phase 2:** 63 tests (adaptive routing, GraphRAG, caching, fusion)
- **Phase 3:** 70 tests (complexity analysis, multi-router, self-correction, query improvement)
- **Phase 4:** 30 tests (feature flags, online learning)

**Test coverage target:** 80% minimum

---

## ⚙️ Environment Setup

### 1. Install Python Dependencies

```bash
cd apex-memory-system

# Install main dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio pytest-timeout pytest-cov
```

### 2. Verify Database Services

```bash
# Start all services
cd docker && docker-compose up -d

# Wait 30 seconds for services to start
sleep 30

# Verify all services healthy
docker-compose ps

# Expected output:
#   apex-postgres    healthy
#   apex-neo4j       healthy
#   apex-qdrant      healthy
#   apex-redis       healthy
#   apex-prometheus  running
#   apex-grafana     running
```

### 3. Configure Environment Variables

```bash
# Copy example config
cp .env.example .env

# Edit .env and set:
# - OPENAI_API_KEY=your-key
# - ANTHROPIC_API_KEY=your-key
# - Database connection strings (defaults should work)

# Verify configuration
cat .env | grep API_KEY
```

### 4. Verify API Keys

```bash
# Test OpenAI API key
python -c "from openai import OpenAI; print('OpenAI: OK' if OpenAI().models.list() else 'FAIL')"

# Test Anthropic API key
python -c "import anthropic; print('Anthropic: OK' if anthropic.Anthropic().messages.create(model='claude-3-5-sonnet-20241022', max_tokens=10, messages=[{'role':'user','content':'hi'}]) else 'FAIL')"
```

---

## 🧪 Running Tests

### Quick Commands

```bash
# Run all tests (223 tests)
pytest tests/unit/test_*.py -v

# Run Phase 4 tests only (30 tests)
pytest tests/unit/test_feature_flags.py tests/unit/test_online_learning.py -v

# Run specific phase tests
pytest tests/unit/test_semantic_classifier.py -v  # Phase 1
pytest tests/unit/test_adaptive_weights.py -v     # Phase 2
pytest tests/unit/test_complexity_analyzer.py -v  # Phase 3

# Run with coverage report
pytest tests/unit/ --cov=apex_memory.query_router --cov-report=term-missing

# Run with coverage HTML report
pytest tests/unit/ --cov=apex_memory.query_router --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Organization

```
tests/unit/
├── Phase 1 (60 tests)
│   ├── test_semantic_classifier.py    # 15 tests
│   ├── test_query_rewriter.py        # 18 tests
│   ├── test_analytics.py             # 13 tests
│   └── test_router_async.py          # 14 tests
│
├── Phase 2 (63 tests)
│   ├── test_adaptive_weights.py      # 18 tests
│   ├── test_neo4j_graphrag.py        # 12 tests
│   ├── test_semantic_cache.py        # 18 tests
│   └── test_result_fusion.py         # 15 tests
│
├── Phase 3 (70 tests)
│   ├── test_complexity_analyzer.py   # 19 tests
│   ├── test_multi_router.py          # 16 tests
│   ├── test_self_correction.py       # 17 tests
│   └── test_query_improver.py        # 18 tests
│
└── Phase 4 (30 tests)
    ├── test_feature_flags.py         # 15 tests
    └── test_online_learning.py       # 15 tests
```

### Advanced Test Commands

```bash
# Run tests in parallel (faster)
pytest tests/unit/ -n auto

# Run only failed tests from last run
pytest tests/unit/ --lf

# Run tests matching pattern
pytest tests/unit/ -k "test_feature_flag"

# Stop on first failure
pytest tests/unit/ -x

# Show local variables on failure
pytest tests/unit/ -l

# Verbose output with timings
pytest tests/unit/ -vv --durations=10
```

---

## ✅ Interpreting Results

### Perfect Run (All Passing)

```
======================== test session starts ========================
platform darwin -- Python 3.12.4, pytest-8.4.1
collected 223 items

tests/unit/test_semantic_classifier.py::test_initialization PASSED    [  0%]
tests/unit/test_semantic_classifier.py::test_classify_query PASSED    [  1%]
...
tests/unit/test_online_learning.py::test_concurrent_feedback PASSED  [100%]

======================== 223 passed in 45.21s ========================
```

✅ **Status:** Ready for deployment!

---

### Partial Failures (<10 failures)

```
======================== test session starts ========================
collected 223 items

tests/unit/test_feature_flags.py::test_redis_connection FAILED       [ 10%]
tests/unit/test_online_learning.py::test_feedback_queue FAILED       [ 15%]
...
===================== 221 passed, 2 failed in 45.21s ==================
```

⚠️ **Status:** Check TROUBLESHOOTING.md for common fixes
**Action:** Review failed test output, fix issues, re-run

---

### Many Failures (>10 failures)

```
======================== test session starts ========================
collected 223 items

tests/unit/test_semantic_classifier.py::test_initialization ERROR   [  0%]
ImportError: No module named 'semantic_router'
...
===================== 0 passed, 223 failed in 5.21s ===================
```

❌ **Status:** Environment issue
**Action:** Verify prerequisites (dependencies, databases, API keys)

---

## 🔍 Common Test Failures

### 1. ImportError: No module named 'X'

**Error:**
```
ImportError: No module named 'semantic_router'
```

**Fix:**
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Verify specific package
pip show semantic-router
```

---

### 2. Database Connection Refused

**Error:**
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**Fix:**
```bash
# Start database services
cd docker && docker-compose up -d

# Wait for services to be healthy
sleep 30
docker-compose ps

# Check specific service logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs redis
```

---

### 3. API Authentication Errors

**Error:**
```
AuthenticationError: Incorrect API key provided
```

**Fix:**
```bash
# Verify API keys in .env
cat .env | grep API_KEY

# Test OpenAI key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | jq .

# Test Anthropic key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

---

### 4. Timeout Errors

**Error:**
```
TimeoutError: Test took longer than 300 seconds
```

**Fix:**
```bash
# Increase timeout in pytest.ini
# Edit: pytest.ini
# Change: --timeout=300 → --timeout=600

# Or run specific test without timeout
pytest tests/unit/test_slow.py -o addopts="" --timeout=600
```

---

### 5. Async Test Failures

**Error:**
```
RuntimeError: Event loop is closed
```

**Fix:**
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Verify pytest.ini has asyncio_mode
cat pytest.ini | grep asyncio_mode
# Should show: asyncio_mode = auto
```

---

## 📊 Coverage Reports

### Generate Coverage Report

```bash
# Terminal report
pytest tests/unit/ --cov=apex_memory.query_router --cov-report=term-missing

# HTML report (best for browsing)
pytest tests/unit/ --cov=apex_memory.query_router --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Expected Coverage

**Minimum:** 80% overall coverage

**Target coverage by module:**
- `feature_flags.py`: 85%+
- `online_learning.py`: 85%+
- `router.py`: 75%+ (complex integration)
- `*_test.py` files: 90%+

### Coverage Report Example

```
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
apex_memory/query_router/__init__.py         12      0   100%
apex_memory/query_router/feature_flags.py   150     15    90%   45-47, 123-125
apex_memory/query_router/online_learning.py 180     20    89%   67-70, 234-240
apex_memory/query_router/router.py          450     80    82%   (complex)
-----------------------------------------------------------------------
TOTAL                                       1500    200    87%
```

✅ **Status:** Above 80% minimum, ready for deployment

---

## 🐛 Debugging Failed Tests

### Step 1: Read the Error Message

```bash
# Run single failing test with verbose output
pytest tests/unit/test_feature_flags.py::test_create_flag -vv
```

### Step 2: Add Debug Logging

```python
# In test file, add logging
import logging
logging.basicConfig(level=logging.DEBUG)

def test_create_flag(manager):
    logger = logging.getLogger(__name__)
    logger.debug("Creating flag...")
    await manager.create_flag("test", rollout_percentage=50)
    logger.debug("Flag created successfully")
```

### Step 3: Use Python Debugger

```bash
# Run test with pdb
pytest tests/unit/test_feature_flags.py::test_create_flag --pdb

# When test fails, you'll drop into pdb
# Commands:
#   l      - list code
#   p var  - print variable
#   n      - next line
#   c      - continue
#   q      - quit
```

### Step 4: Check Logs

```bash
# Application logs
tail -f logs/apex-memory.log

# Database logs
docker-compose logs -f postgres
docker-compose logs -f neo4j
docker-compose logs -f redis
```

---

## 📝 Test Checklist

**Before running tests:**
- [ ] Python 3.11+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Test dependencies installed (`pip install pytest pytest-asyncio pytest-timeout pytest-cov`)
- [ ] Database services running (`docker-compose ps` shows all healthy)
- [ ] Environment variables configured (`.env` file exists)
- [ ] OpenAI API key valid
- [ ] Anthropic API key valid

**During test run:**
- [ ] Monitor test progress
- [ ] Note any warnings or errors
- [ ] Check timing (slow tests may indicate issues)

**After test run:**
- [ ] Review coverage report (target: 80%+)
- [ ] Fix any failing tests
- [ ] Document any new issues in TROUBLESHOOTING.md
- [ ] Update tests if behavior changed

---

## 🔄 Continuous Testing

### Pre-Commit Tests

```bash
# Run fast tests only before commit
pytest tests/unit/test_feature_flags.py tests/unit/test_online_learning.py -v

# Or use git hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
pytest tests/unit/test_*.py -v --maxfail=5
EOF
chmod +x .git/hooks/pre-commit
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: pytest tests/unit/ --cov=apex_memory.query_router
```

---

## ✅ Success Criteria

**Tests are ready for deployment when:**

- [ ] All 223 tests passing (100%)
- [ ] Coverage ≥80% overall
- [ ] No timeout errors
- [ ] No database connection errors
- [ ] No API authentication errors
- [ ] Test run completes in <2 minutes

---

**Testing Guide v1.0**
**Last Updated:** 2025-10-07
**Next Review:** 2025-11-07
