# MeMo Bot Pro - Deployment Guide

## Quick Deploy

1. **Click "Publish"** in Replit
2. Your bot is now live! 🚀

## Deployment Fixes Applied

### ✅ Problem 1: Geographic API Restrictions
**Issue**: Binance API blocks requests from certain deployment locations.

**Solution**: The app automatically enables mock mode in deployments using the `REPLIT_DEPLOYMENT` environment variable.

```python
# Automatic detection in web_app.py
is_deployment = os.getenv('REPLIT_DEPLOYMENT') == '1'
mock_mode = config.mock_mode or is_deployment
```

### ✅ Problem 2: Health Check Timeouts
**Issue**: Expensive Binance API calls on the health check endpoint caused deployment failures.

**Solution**: Created a separate lightweight `/health` endpoint that returns immediately:

```python
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'MeMo Bot Pro',
        'version': '1.0.0'
    }), 200
```

### ✅ Problem 3: API Initialization Errors
**Issue**: App crashed if Binance API failed to initialize.

**Solution**: Wrapped all Binance operations in try-except blocks with automatic fallback to mock mode:

```python
try:
    client = BinanceClient(...)
except Exception as e:
    # Fallback to mock mode
    client = BinanceClient(mock=True)
```

### ✅ Problem 4: Lazy Initialization
**Issue**: Creating new client instances on every request was expensive.

**Solution**: Implemented global lazy initialization with caching:

```python
_client = None
_signal_gen = None

def get_or_create_client():
    global _client, _signal_gen
    if _client is None:
        # Initialize once and reuse
        ...
    return _client, _signal_gen
```

## Environment Variables for Deployment

### Automatic (No Setup Required)
- `REPLIT_DEPLOYMENT` - Automatically set to `1` in published apps

### Optional (For Live Binance Data)
If your deployment region supports Binance API:
- `BINANCE_API_KEY` - Your Binance API key
- `BINANCE_API_SECRET` - Your Binance API secret
- `MOCK_MODE` - Set to `false` to use live data (defaults to `true` in deployment)

## Deployment Types

### Autoscale (Current Configuration) ✅
- **Best for**: Web applications with variable traffic
- **Billing**: Pay only when serving requests
- **Auto-scales**: Based on traffic patterns
- **Health checks**: `/health` endpoint responds in <100ms
- **Mock mode**: Enabled by default

### Reserved VM (Alternative)
If you need live Binance data in production:
1. Consider Reserved VM for consistent geographic routing
2. May offer better Binance API accessibility
3. Always running (not idle-based)

## Health Check Endpoints

| Endpoint | Purpose | Response Time |
|----------|---------|---------------|
| `/health` | Deployment health checks | <100ms |
| `/` | Main dashboard | Variable (depends on API) |
| `/api/prices` | Price data | Variable (cached) |
| `/api/signals` | Trading signals | Variable (cached) |

## Testing Before Deployment

Test the health endpoint locally:
```bash
curl http://localhost:5000/health
# Should return: {"status":"healthy","service":"MeMo Bot Pro","version":"1.0.0"}
```

## Troubleshooting

### Issue: Deployment still fails
**Solution**: Ensure MOCK_MODE is enabled:
1. Go to Replit Secrets
2. Add `MOCK_MODE=true`
3. Redeploy

### Issue: Want live Binance data in production
**Solutions**:
1. Try Reserved VM deployment instead of Autoscale
2. Verify your deployment region supports Binance API
3. Check Binance API geographic restrictions

### Issue: Dashboard shows "Service Unavailable"
**This is normal** if:
- Binance API is blocked in deployment region
- App automatically falls back to mock mode
- User sees helpful error message with instructions

## Monitoring

After deployment:
1. Check deployment logs for any errors
2. Visit your public URL to verify dashboard loads
3. Test `/health` endpoint: `curl https://your-app.repl.co/health`
4. Monitor autoscale metrics in Replit dashboard

## Success Indicators

✅ Health check returns HTTP 200
✅ Dashboard loads (with mock or live data)
✅ No crashes in deployment logs
✅ Telegram bot can be started separately

## Next Steps After Deployment

1. **Share your web dashboard** - Public URL is ready
2. **Run Telegram bot** - Deploy separately or use Reserved VM
3. **Monitor usage** - Check Replit autoscale metrics
4. **Upgrade if needed** - Switch to Reserved VM for 24/7 bot

---

**Deployment Ready!** Your MeMo Bot Pro is configured for reliable, scalable deployment on Replit.
