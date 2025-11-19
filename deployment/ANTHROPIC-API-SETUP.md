# Anthropic API Key Setup - Quick Guide

**Date:** 2025-11-15
**Time:** 10-15 minutes
**Cost:** $20-50/month (usage-based, Claude Haiku: $3/million input tokens)

---

## Why Anthropic API?

Your Apex Memory System uses Claude for:
- **Query rewriting** - Natural language → database queries
- **Chat/conversation** - Claude Sonnet/Haiku for responses
- **LLM classification** - Intent detection, query routing
- **Graphiti alternative** - Can use Claude instead of OpenAI for entity extraction

**You already have OpenAI ($10-30/month) ✅, now add Anthropic for Claude access.**

---

## Step 1: Create Account (5 minutes)

### 1.1 Sign Up

Go to: **https://console.anthropic.com/settings/keys**

**Account Details:**
- Use your primary email (same as GCP/Temporal if possible)
- Create strong password (store in password manager immediately)
- Verify email address

---

## Step 2: Generate API Key (3 minutes)

### 2.1 Create API Key

In Anthropic Console:
1. Navigate to: **Settings → API Keys** (or direct link above)
2. Click "Create Key"
3. **Name:** `apex-memory-prod` (or `apex-memory-dev`)
4. Click "Create Key"
5. **⚠️ CRITICAL:** Copy the key immediately (starts with `sk-ant-...`)
6. **Store in password manager RIGHT NOW** - you won't see it again!

**Expected format:**
```
sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Step 3: Add Payment Method (5 minutes)

### 3.1 Add Credit Card

1. Navigate to: **Settings → Billing**
2. Click "Add payment method"
3. Add credit card
4. Set billing email (same as account email recommended)

### 3.2 Set Usage Limits (Recommended)

**Prevent unexpected charges:**

1. Navigate to: **Settings → Billing → Usage Limits**
2. Set monthly spend limit: **$50/month** (recommended starting point)
3. Set email alerts:
   - Alert at: $25 (50% of limit)
   - Alert at: $40 (80% of limit)
4. Save limits

**Usage estimates:**
- Claude Haiku: $3/million input tokens, $15/million output tokens
- Claude Sonnet: $15/million input tokens, $75/million output tokens
- For query rewriting + chat: $20-50/month typical

---

## Step 4: Test API Key (2 minutes)

**Quick test to verify key works:**

```bash
# Test Anthropic API key
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: YOUR_API_KEY_HERE" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**Expected response:**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Hello! How can I help you today?"}],
  "model": "claude-3-haiku-20240307",
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 10, "output_tokens": 12}
}
```

---

## Step 5: Update .env File (2 minutes)

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Add Anthropic API key to .env
cat >> .env << 'EOF'

# =============================================================================
# Anthropic API Configuration
# =============================================================================
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
ANTHROPIC_MODEL=claude-3-haiku-20240307  # Fast + cheap for query rewriting
ANTHROPIC_MAX_TOKENS=4096

# Alternative models (uncomment if needed):
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Most capable, slower
# ANTHROPIC_MODEL=claude-3-opus-20240229      # Highest quality, expensive
EOF

echo "✅ Anthropic API key added to .env"
```

**Replace `YOUR_KEY_HERE`** with your actual API key.

---

## Step 6: Store in Password Manager (3 minutes)

**Copy this information to your password manager:**

```yaml
Title: Anthropic API - Apex Memory
Type: Secure Note
Category: API Keys

API Key: sk-ant-api03-[YOUR_KEY_HERE]
Created: 2025-11-15
Monthly Limit: $50
Usage Alerts: $25 (50%), $40 (80%)

Default Model: claude-3-haiku-20240307
Purpose:
  - Query rewriting (natural language → database queries)
  - Chat responses
  - LLM classification
  - Alternative to OpenAI for Graphiti entity extraction

Cost Estimate: $20-50/month (usage-based)
Pricing:
  - Haiku: $3/$15 per 1M tokens (input/output)
  - Sonnet: $15/$75 per 1M tokens (input/output)

Console: https://console.anthropic.com
Billing: https://console.anthropic.com/settings/billing
API Keys: https://console.anthropic.com/settings/keys

Notes:
  - Set $50/month usage limit
  - Email alerts at $25 and $40
  - Key format: sk-ant-api03-...
```

---

## ✅ Anthropic API Setup Complete!

### What You've Accomplished

- ✅ Anthropic account created
- ✅ API key generated and copied
- ✅ Payment method added
- ✅ Usage limits set ($50/month with alerts)
- ✅ API key tested (optional)
- ✅ .env file updated
- ✅ Credentials stored in password manager

### Cost Summary

**Combined API Costs:**
- OpenAI: $10-30/month (embeddings + Graphiti)
- Anthropic: $20-50/month (Claude for chat + query rewriting)
- **Total: $30-80/month** (usage-based, auto-scales with traffic)

---

## 🎯 Next Steps

**Update Prerequisites Tracker:**
- Mark "Anthropic API Key" as complete in `PREREQUISITES-COMPLETION-TRACKER.md`

**Continue Prerequisites:**
- Next: Grafana Cloud Pro (30-40 minutes)
- Then: Security & Secrets (30-45 minutes) - SECRET_KEY, DB passwords
- Then: 2FA on all accounts (30-40 minutes)

---

## 🧪 Optional: Test with Python SDK

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
source venv/bin/activate

pip install anthropic

python << 'EOF'
import os
from anthropic import Anthropic

# Load API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("⚠️  ANTHROPIC_API_KEY not found in environment")
    print("   Run: export ANTHROPIC_API_KEY='sk-ant-...'")
    exit(1)

# Create client
client = Anthropic(api_key=api_key)

# Test simple message
message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello! Respond with just 'API key works!'"}
    ]
)

print(f"\n✅ Anthropic API key works!")
print(f"   Model: {message.model}")
print(f"   Response: {message.content[0].text}")
print(f"   Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out\n")
EOF
```

---

## Troubleshooting

### "Invalid API Key" Error

**Problem:** API key not recognized

**Solutions:**
1. Verify key copied completely (starts with `sk-ant-api03-`)
2. Check for extra spaces/newlines
3. Regenerate key in Anthropic console

### "Credit card required" Error

**Problem:** No payment method added

**Solution:**
- Navigate to: Settings → Billing
- Add credit card
- Wait 1-2 minutes for activation

### "Rate limit exceeded" Error

**Problem:** Too many requests in short time

**Solution:**
- Free tier has lower rate limits
- Wait 1 minute and try again
- Once paid account activated, limits increase significantly

---

**Setup Complete!** 🎉

You now have both OpenAI and Anthropic API access, giving you flexibility for embeddings (OpenAI) and chat/reasoning (Claude).

**Next:** Continue with Grafana Cloud setup (30-40 minutes)
