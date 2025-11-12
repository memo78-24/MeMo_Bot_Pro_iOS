# MeMo Bot Pro - Deployment Guide

## Quick Start (3 Steps!)

1. **Generate webhook secret** → Set environment variables
2. **Click "Deploy"** → Choose "Autoscale"
3. **Test your bot** → Send `/start` on Telegram

Your bot will now run 24/7 even when your laptop is off! 🚀

## Required Environment Variables

Set these 3 variables before deploying:

### 1. TELEGRAM_BOT_TOKEN ✅
Already set! (From BotFather)

### 2. TELEGRAM_WEBHOOK_URL
**What**: Public URL where Telegram sends updates  
**Format**: `https://YOUR-DEPLOYED-URL.replit.app/telegram/webhook`

**How to get it**:
1. Deploy FIRST (you'll get a URL)
2. Copy that URL and add `/telegram/webhook` at the end
3. Set this environment variable
4. Redeploy

**Example**: `https://memo-bot-pro-maherfekri2025.replit.app/telegram/webhook`

### 3. TELEGRAM_WEBHOOK_SECRET 🔐
**What**: Secret token for security (prevents fake requests)

**Generate it** - Run this in Replit Shell:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and set it as environment variable.

**Example output**: `xK9_vN2mP4qR7sT1wU3yZ5aB8cD0eF6gH_9jL2nM4oP`

## Step-by-Step Deployment

### Step 1: First Deployment (Get Your URL)

1. Click **"Deploy"** button
2. Choose **"Autoscale"** (recommended!)
3. Wait for deployment to complete
4. **Copy your public URL** (e.g., `https://memo-bot-pro.replit.app`)

### Step 2: Set Environment Variables

1. Go to Secrets (or deployment settings)
2. Add these 2 new variables:

```
TELEGRAM_WEBHOOK_URL=https://YOUR-URL.replit.app/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=<paste the secret you generated>
```

**Important**: Replace `YOUR-URL` with your actual deployment URL!

### Step 3: Redeploy

1. Click **"Deploy"** again
2. Bot will now receive messages from Telegram
3. **Test it**: Send `/start` to your bot on Telegram

### Step 4: Verify It's Working

**Send these commands to your bot**:
- `/start` → Welcome message
- `/menu` → Interactive buttons
- `/profit` → Trading calculator

**Check monitoring**:
- Visit: `https://your-url.replit.app/monitor`
- Should show "Production: ONLINE" 🟢

## How Webhook Architecture Works

**OLD (Had Problems)**:
- Separate bot process using polling
- Needed Reserved VM
- Deployment kept failing

**NEW (Works Perfect)**:
- Bot runs inside web app via webhooks
- Works with Autoscale
- Telegram pushes updates to your app
- All features work: alerts, signals, profit calculator

---

## Troubleshooting

### Bot not receiving messages?

**Problem**: TELEGRAM_WEBHOOK_URL not set correctly  
**Solution**: Make sure it's your ACTUAL deployment URL + `/telegram/webhook`

**Problem**: Webhook secret mismatch  
**Solution**: Generate new secret, set it, redeploy

**Problem**: "Webhook not configured" in logs  
**Solution**: Set TELEGRAM_WEBHOOK_URL and redeploy

### Check deployment logs

Look for these success messages:
```
✅ Telegram bot initialized successfully in webhook mode
✅ Webhook configured successfully
✅ Started instant price monitoring (60/min)
✅ Started heartbeat monitoring
```

### Test webhook endpoint

```bash
curl https://your-app.replit.app/health
# Should return: {"status":"healthy"}
```

---

## Security Features

✅ **Webhook endpoint secured** with secret token  
✅ **Only Telegram can send updates** (validated header)  
✅ **Fake requests blocked** (returns 403)  
✅ **Secret rotation supported** (just generate new secret)  

**Never share your TELEGRAM_WEBHOOK_SECRET!**

---

## Cost Comparison

**Autoscale** (Current):
- Scales down when idle = SAVES MONEY
- Scales up with traffic automatically
- Perfect for crypto bot usage patterns

**Reserved VM** (Old approach):
- Always running 24/7 = Higher cost
- Not needed with webhooks

---

## Quick Reference

**Generate webhook secret**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Check webhook status** (from Shell):
```bash
curl https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo
```

**Monitor deployment**:
- Visit: `https://your-url.replit.app/monitor`
- Shows: Development + Production status side-by-side

---

## What Your Clients Will Get

Once deployed:
- ✅ **24/7 crypto price alerts** (even when your laptop is off)
- ✅ **Instant notifications** on ANY price change
- ✅ **2-hour summary reports** with BUY/SELL signals
- ✅ **Dual language support** (English + Arabic)
- ✅ **Profit calculator** for 1000 AED investment
- ✅ **Interactive menus** and clickable currency links

**Your bot will be ALWAYS ONLINE serving customers!** 🚀
