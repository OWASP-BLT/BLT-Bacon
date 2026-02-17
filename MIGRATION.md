# 🔄 Migration Guide: Flask to Cloudflare Python Worker

This document explains the migration from the Flask-based `ord-server` to the new Cloudflare Python Worker architecture.

## Overview

The BLT-BACON token distribution service has been migrated from a Flask-based server to a Cloudflare Python Worker for improved:
- **Performance**: Edge computing for lower latency
- **Scalability**: Automatic scaling across Cloudflare's global network
- **Reliability**: Built-in DDoS protection and high availability
- **Cost**: Pay-per-request pricing model

## Architecture Changes

### Before (Flask)
```
ord-server/
├── ord-api.py          # Flask application
├── requirements.txt    # Flask, python-dotenv, PyYAML, gunicorn
├── .env.example        # Environment configuration
└── ord-flask.service   # Systemd service file
```

### After (Cloudflare Worker)
```
src/
├── entry.py           # Cloudflare Worker entry point
wrangler.jsonc         # Cloudflare configuration
pyproject.toml         # Python dependencies
.env.example           # Environment configuration
```

## API Endpoint Mapping

All endpoints remain the same, ensuring backward compatibility:

| Endpoint | Method | Status |
|----------|--------|--------|
| `/mainnet/send-bacon-tokens` | POST | ✅ Migrated |
| `/regtest/send-bacon-tokens` | POST | ✅ Migrated |
| `/mainnet/wallet-balance` | GET | ✅ Migrated |

## Code Changes

### 1. Request Handling

**Before (Flask):**
```python
from flask import Flask, jsonify, request

@app.route("/mainnet/send-bacon-tokens", methods=["POST"])
def send_bacon_tokens():
    yaml_content = request.json.get("yaml_content")
    # ...
    return jsonify({"success": True, "txid": txid})
```

**After (Cloudflare Worker):**
```python
async def handle_request(self, request):
    if path == "mainnet/send-bacon-tokens":
        body = await request.json()
        return self.send_bacon_tokens_mainnet(body)
```

### 2. Response Format

**Before (Flask):**
```python
return jsonify({"success": True})
```

**After (Cloudflare Worker):**
```python
return Response(
    json.dumps({"success": True}),
    status=200,
)
```

### 3. Environment Variables

Environment variables remain the same - no changes needed to `.env` configuration!

## Deployment Changes

### Before: Deploy Flask Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:9002 ord-api:app

# Or use systemd service
sudo systemctl start ord-flask.service
```

### After: Deploy Cloudflare Worker

```bash
# Install dependencies
uv pip install pyyaml

# Deploy to Cloudflare
uv run pywrangler deploy

# Or test locally
uv run pywrangler dev
```

## Configuration Migration

### Environment Variables
No changes needed! The same environment variables work in both systems:
- `ORD_PATH`
- `BITCOIN_RPC_USER_MAINNET`
- `BITCOIN_RPC_PASSWORD_MAINNET`
- `BITCOIN_RPC_URL_MAINNET`
- `ORD_SERVER_URL_MAINNET`
- `WALLET_NAME_MAINNET`
- `WALLET_API_PASSWORD`
- etc.

### Cloudflare-Specific Configuration
New file: `wrangler.jsonc`
```jsonc
{
  "name": "blt-bacon-worker",
  "main": "src/entry.py",
  "compatibility_flags": ["python_workers"],
  "compatibility_date": "2026-02-17"
}
```

## Testing the Migration

### 1. Health Check
```bash
# Test the health endpoint
curl https://your-worker.workers.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "BLT-BACON Token Distribution Service",
  "version": "1.0.0"
}
```

### 2. Dry Run Transaction
```bash
curl -X POST https://your-worker.workers.dev/mainnet/send-bacon-tokens \
  -H "Content-Type: application/json" \
  -d '{
    "yaml_content": "outputs:\n- address: bc1...\n  runes:\n    BLT•BACON•TOKENS: 1",
    "fee_rate": 50,
    "dry_run": true
  }'
```

### 3. Wallet Balance
```bash
curl https://your-worker.workers.dev/mainnet/wallet-balance
```

## Main BLT Repository Integration

Update the main BLT repository to use the new Cloudflare Worker URL:

**In `blt/settings.py`:**
```python
# Before
ORD_SERVER_URL = "http://your-server:9002"

# After
ORD_SERVER_URL = "https://your-worker.workers.dev"
```

No other changes are needed in the main BLT repository - the API remains identical!

## Rollback Plan

If needed, the old Flask server can still be used:

1. Keep the `ord-server/` directory as backup
2. Update `ORD_SERVER_URL` back to the Flask server URL
3. Restart the Flask service

## Benefits of the New Architecture

1. **Global Distribution**: Runs on Cloudflare's edge network in 300+ cities
2. **Zero Server Management**: No need to manage servers, scaling, or updates
3. **Built-in Security**: DDoS protection, rate limiting, and SSL included
4. **Cost Effective**: Pay only for actual requests
5. **Fast Cold Starts**: Python workers start in milliseconds
6. **Automatic Scaling**: Handles traffic spikes automatically

## Timeline

- ✅ **Phase 1**: Create Cloudflare Worker structure
- ✅ **Phase 2**: Migrate all endpoints
- ✅ **Phase 3**: Add comprehensive documentation
- ⏳ **Phase 4**: Deploy to production
- ⏳ **Phase 5**: Update main BLT repository
- ⏳ **Phase 6**: Deprecate old Flask server

## Support

For questions or issues during migration:
- Open an issue on [GitHub](https://github.com/OWASP-BLT/BLT-Bacon/issues)
- Join [OWASP Slack #project-blt](https://owasp.org/slack/invite)
- Check the [documentation](https://owasp-blt.github.io/BLT-Bacon/)
