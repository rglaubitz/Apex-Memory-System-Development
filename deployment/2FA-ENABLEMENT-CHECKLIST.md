# 2FA Enablement Checklist

**Date:** 2025-11-15
**Time:** 30-40 minutes
**Cost:** FREE (all accounts support free 2FA)

---

## Why Enable 2FA?

**Two-Factor Authentication (2FA)** adds a second layer of security beyond passwords:

- ✅ **99.9% effective** against automated attacks (Google Security Study)
- ✅ **Required for production** best practices
- ✅ **Protects against:** Password leaks, phishing, brute force attacks
- ✅ **Compliance:** Many frameworks require 2FA (SOC 2, ISO 27001)

**What is 2FA?**
- **Something you know** (password) + **Something you have** (phone, security key)
- Even if password is leaked, attacker can't access account without second factor

**7 Critical Accounts** for Apex Memory System deployment must have 2FA enabled.

---

## Quick Setup Overview

**Authenticator App Recommended:**
- ✅ **Authy** (recommended) - Multi-device, cloud backup
- ✅ **Google Authenticator** - Simple, widely supported
- ✅ **Microsoft Authenticator** - Good for Microsoft services

**Install Authenticator App:**

```bash
# Install Authy (recommended)
brew install --cask authy

# Or use your phone
# iOS: App Store → "Authy" or "Google Authenticator"
# Android: Play Store → "Authy" or "Google Authenticator"
```

---

## Account 1: GCP (Google Cloud Platform)

**Time:** 5 minutes | **Priority:** ⭐⭐⭐⭐⭐ CRITICAL

### Enable 2FA

1. **Navigate to:** https://myaccount.google.com/security
2. **Find:** "2-Step Verification" section
3. **Click:** "Get started"
4. **Choose method:**
   - **Authenticator app** (recommended) - Use Authy or Google Authenticator
   - **SMS** (backup only) - Less secure but better than nothing
5. **Scan QR code** with authenticator app
6. **Save backup codes** - Store in password manager (8 codes, use once each)

### Test 2FA

```bash
# Log out and back in to test
gcloud auth login

# Should prompt for:
# 1. Email + password
# 2. 6-digit code from authenticator app
```

**Checklist:**
- [ ] 2FA enabled on GCP account
- [ ] Backup codes saved in password manager
- [ ] Tested login with 2FA

---

## Account 2: GitHub

**Time:** 5 minutes | **Priority:** ⭐⭐⭐⭐⭐ CRITICAL

### Enable 2FA

1. **Navigate to:** https://github.com/settings/security
2. **Find:** "Two-factor authentication"
3. **Click:** "Enable two-factor authentication"
4. **Choose:** "Set up using an app" (recommended)
5. **Scan QR code** with authenticator app
6. **Save recovery codes** - Store in password manager (16 codes)

### Alternative: Security Key (Hardware)

```bash
# If you have a YubiKey or similar:
# GitHub Settings → Security → Two-factor authentication → Security keys
# More secure than app-based 2FA
```

**Checklist:**
- [ ] 2FA enabled on GitHub account
- [ ] Recovery codes saved in password manager
- [ ] Tested login with 2FA

---

## Account 3: OpenAI

**Time:** 5 minutes | **Priority:** ⭐⭐⭐⭐ HIGH

### Enable 2FA

1. **Navigate to:** https://platform.openai.com/account/security
2. **Find:** "Two-factor authentication"
3. **Click:** "Enable"
4. **Choose:** Authenticator app
5. **Scan QR code** with authenticator app
6. **Save recovery codes** - Store in password manager

**Test API Key:**

```bash
# After enabling 2FA, verify API key still works
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Should return list of models (200 OK)
```

**Checklist:**
- [ ] 2FA enabled on OpenAI account
- [ ] Recovery codes saved in password manager
- [ ] API key tested and working

---

## Account 4: Anthropic

**Time:** 5 minutes | **Priority:** ⭐⭐⭐⭐ HIGH

### Enable 2FA

1. **Navigate to:** https://console.anthropic.com/settings/security
2. **Find:** "Two-factor authentication"
3. **Click:** "Enable"
4. **Choose:** Authenticator app
5. **Scan QR code** with authenticator app
6. **Save recovery codes** - Store in password manager

**Test API Key:**

```bash
# After enabling 2FA, verify API key still works
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'

# Should return response (200 OK)
```

**Checklist:**
- [ ] 2FA enabled on Anthropic account
- [ ] Recovery codes saved in password manager
- [ ] API key tested and working

---

## Account 5: Temporal Cloud

**Time:** 5 minutes | **Priority:** ⭐⭐⭐⭐ HIGH

### Enable 2FA

1. **Navigate to:** https://cloud.temporal.io/settings/security
2. **Find:** "Two-factor authentication" or "Security"
3. **Click:** "Enable 2FA"
4. **Choose:** Authenticator app
5. **Scan QR code** with authenticator app
6. **Save recovery codes** - Store in password manager

**Test Connection:**

```bash
# After enabling 2FA, verify Temporal CLI still works
temporal --profile cloud workflow list

# Should connect successfully (API key auth not affected by 2FA)
```

**Checklist:**
- [ ] 2FA enabled on Temporal Cloud account
- [ ] Recovery codes saved in password manager
- [ ] Temporal CLI connection tested

---

## Account 6: Grafana Cloud

**Time:** 5 minutes | **Priority:** ⭐⭐⭐ MEDIUM

### Enable 2FA

1. **Navigate to:** https://grafana.com/orgs/[your-org]/users/security
2. **Find:** "Two-factor authentication"
3. **Click:** "Set up 2FA"
4. **Choose:** Authenticator app
5. **Scan QR code** with authenticator app
6. **Save recovery codes** - Store in password manager

**Test Access:**

```bash
# After enabling 2FA, verify Grafana dashboard access
open https://apex-memory-prod.grafana.net

# Should prompt for:
# 1. Email + password
# 2. 6-digit code from authenticator app
```

**Checklist:**
- [ ] 2FA enabled on Grafana Cloud account
- [ ] Recovery codes saved in password manager
- [ ] Dashboard access tested

---

## Account 7: Password Manager (Bitwarden/1Password)

**Time:** 5 minutes | **Priority:** ⭐⭐⭐⭐⭐ CRITICAL

### Bitwarden 2FA

1. **Navigate to:** https://vault.bitwarden.com → **Settings → Security → Two-step Login**
2. **Choose:** Authenticator app (FREE) or YubiKey (Premium $10/year)
3. **Scan QR code** with **different authenticator app** (NOT the one stored in Bitwarden!)
4. **Save recovery code** - Print and store physically (NOT in Bitwarden!)

**⚠️ CRITICAL:** Use a **different authenticator app** for Bitwarden 2FA:
- ❌ Don't store Bitwarden 2FA in Bitwarden (circular dependency)
- ✅ Use phone's authenticator app OR separate device
- ✅ Print recovery code on paper, store in safe

### 1Password 2FA

1. **Navigate to:** https://my.1password.com/profile → **Security → Two-Factor Authentication**
2. **Click:** "Set up two-factor authentication"
3. **Choose:** Authenticator app
4. **Scan QR code** with **phone's authenticator app** (NOT 1Password itself!)
5. **Save emergency kit** - Print PDF, store in safe

**Checklist:**
- [ ] 2FA enabled on password manager
- [ ] Recovery codes saved OUTSIDE password manager (paper + safe)
- [ ] Tested login with 2FA

---

## ✅ Master Checklist - All Accounts

| Account | 2FA Enabled | Recovery Codes Saved | Tested |
|---------|-------------|---------------------|--------|
| **GCP** | ⬜ | ⬜ | ⬜ |
| **GitHub** | ⬜ | ⬜ | ⬜ |
| **OpenAI** | ⬜ | ⬜ | ⬜ |
| **Anthropic** | ⬜ | ⬜ | ⬜ |
| **Temporal Cloud** | ⬜ | ⬜ | ⬜ |
| **Grafana Cloud** | ⬜ | ⬜ | ⬜ |
| **Password Manager** | ⬜ | ⬜ | ⬜ |

---

## Recovery Code Storage Template

**Add to password manager (Bitwarden/1Password):**

### Secure Note: 2FA Recovery Codes

```yaml
Title: 2FA Recovery Codes - All Accounts
Type: Secure Note
Folder: Apex Memory System
Category: Security

GCP Recovery Codes:
  - XXXX-XXXX-XXXX-XXXX
  - XXXX-XXXX-XXXX-XXXX
  - XXXX-XXXX-XXXX-XXXX
  - XXXX-XXXX-XXXX-XXXX
  - XXXX-XXXX-XXXX-XXXX
  - XXXX-XXXX-XXXX-XXXX
  - XXXX-XXXX-XXXX-XXXX
  - XXXX-XXXX-XXXX-XXXX

GitHub Recovery Codes:
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX
  - XXXX-XXXX

OpenAI Recovery Codes:
  - [Your codes here]

Anthropic Recovery Codes:
  - [Your codes here]

Temporal Cloud Recovery Codes:
  - [Your codes here]

Grafana Cloud Recovery Codes:
  - [Your codes here]

⚠️ CRITICAL NOTES:
- Each recovery code can only be used ONCE
- After using a code, it becomes invalid
- Generate new codes when running low
- Store physically (paper) as backup
- DO NOT share recovery codes
```

---

## Best Practices

### DO ✅

- **Use authenticator app** (more secure than SMS)
- **Save recovery codes** immediately after enabling 2FA
- **Test 2FA** before leaving setup page
- **Store recovery codes** in password manager + physical backup
- **Use different authenticator** for password manager 2FA
- **Enable 2FA on email** (Gmail, etc.) - protects password reset
- **Review active sessions** quarterly (revoke old/unknown sessions)

### DON'T ❌

- **Don't use SMS only** (vulnerable to SIM swapping)
- **Don't skip recovery codes** (you'll be locked out if you lose phone)
- **Don't store password manager 2FA in itself** (circular dependency)
- **Don't disable 2FA** for convenience
- **Don't share recovery codes** with anyone
- **Don't ignore security notifications** from services

---

## Troubleshooting

### "Lost phone with authenticator app"

**Problem:** Phone lost/broken, can't access 2FA codes

**Solution:**
1. Use recovery codes you saved in password manager
2. Contact service support (may require identity verification)
3. **For Authy:** Use cloud backup to restore on new device
4. **For Google Authenticator:** No backup - must use recovery codes

**Prevention:**
- Use Authy (cloud backup)
- Print recovery codes on paper
- Enable backup 2FA method (SMS as fallback)

### "Recovery codes not working"

**Problem:** Entered recovery code, still denied access

**Solution:**
1. Check for typos (codes are case-sensitive)
2. Verify using correct account
3. Contact service support (identity verification required)

**Prevention:**
- Test one recovery code immediately after enabling 2FA
- Store codes in multiple locations (password manager + paper)

### "Authenticator app showing wrong code"

**Problem:** 6-digit code rejected as invalid

**Solution:**
1. Check device time (TOTP requires synchronized clocks)
2. Enable automatic date/time: Settings → Date & Time → Set Automatically
3. Wait for new code (codes refresh every 30 seconds)
4. Verify correct account selected in authenticator app

---

## Additional Security Layers (Optional)

### Hardware Security Keys (YubiKey)

**Benefits:**
- ✅ Most secure 2FA method (phishing-resistant)
- ✅ No phone required
- ✅ Faster than typing codes

**Cost:** $25-50/key (buy 2: primary + backup)

**Setup:**
```bash
# Supported by: Google, GitHub, 1Password, many others
# Not all services support hardware keys (check compatibility)
```

### Backup Authentication Methods

**Recommended Setup:**
1. **Primary:** Authenticator app (Authy, Google Authenticator)
2. **Backup 1:** Recovery codes (in password manager + paper)
3. **Backup 2:** SMS (less secure, but better than nothing)
4. **Backup 3:** Hardware key (YubiKey) - optional

---

## ✅ 2FA Setup Complete!

### What You've Accomplished

- ✅ 2FA enabled on all 7 critical accounts:
  - GCP (cloud infrastructure)
  - GitHub (code repository)
  - OpenAI (API access)
  - Anthropic (API access)
  - Temporal Cloud (workflow orchestration)
  - Grafana Cloud (monitoring)
  - Password Manager (credential vault)
- ✅ Recovery codes saved in password manager + physical backup
- ✅ All accounts tested with 2FA login

### Security Posture

**Before 2FA:**
- 🔴 **Vulnerable** to password leaks, phishing, brute force
- 🔴 Single point of failure (password only)
- 🔴 No protection against credential stuffing

**After 2FA:**
- 🟢 **99.9% resistant** to automated attacks
- 🟢 Multiple layers of defense
- 🟢 Compliant with security best practices
- 🟢 Ready for production deployment

---

## 🎯 Next Steps

**Update Prerequisites Tracker:**
- Mark "2FA on all accounts" as complete in `PREREQUISITES-COMPLETION-TRACKER.md`

**Final Prerequisites:**
- ⏳ Get Anthropic API key (10-15 min) - if not done yet
- ⏳ Setup Grafana Cloud (30-40 min) - if not done yet
- ⏳ Delete GENERATED-SECRETS.md (AFTER storing in password manager!)

**After Prerequisites Complete:**
- 🎉 Ready for Pulumi Week 1: Networking + Cloud SQL (20-24 hours)
- 🎉 Or: Manual Production Deployment (16-24 hours)

---

**Setup Complete!** 🛡️

Your Apex Memory System accounts are now protected with military-grade two-factor authentication. Even if passwords are compromised, attackers cannot access your accounts.

**Next:** Final verification checklist, then you're ready for production deployment!
