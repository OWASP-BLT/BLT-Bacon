# 🚀 Quick Start Guide

This guide will help you get the BLT-BACON token distribution service up and running quickly.

## Prerequisites

- Python 3.11+
- Node.js 14+ (for Cloudflare tooling)
- A running Bitcoin node with Runes support
- An ord server/indexer
- Cloudflare Workers account

## Step 1: Set Up Backend Server

The backend server handles actual Bitcoin operations.

```bash
# Navigate to backend directory
cd ord-server

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your Bitcoin RPC credentials

# Run the server (development)
python ord-api.py

# Or run with Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:9002 ord-api:app
```

**Important**: Make sure your backend server is accessible at a URL (e.g., `https://ord-backend.example.com`)

## Step 2: Configure Cloudflare Worker

The worker acts as an API gateway with validation.

```bash
# Go back to root directory
cd ..

# Install uv if not already installed
pip install uv

# Install worker dependencies
uv pip install pyyaml

# Configure environment
cp .env.example .env
nano .env  # Set ORD_BACKEND_URL to your backend server
```

**Example .env:**
```bash
ORD_BACKEND_URL=https://ord-backend.example.com
WALLET_API_PASSWORD=your_secure_password
RATE_LIMIT=60
```

## Step 3: Deploy Cloudflare Worker

```bash
# Test locally first
uv run pywrangler dev

# Deploy to Cloudflare
uv run pywrangler deploy
```

After deployment, you'll get a URL like: `https://blt-bacon-worker.your-subdomain.workers.dev`

## Step 4: Test Your Deployment

### Health Check
```bash
curl https://your-worker.workers.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "BLT-BACON Token Distribution Service",
  "version": "1.0.0",
  "architecture": "API Gateway -> Backend Ord Server"
}
```

### Dry Run Transaction (Safe Testing)
```bash
curl -X POST https://your-worker.workers.dev/mainnet/send-bacon-tokens \
  -H "Content-Type: application/json" \
  -d '{
    "yaml_content": "outputs:\n- address: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh\n  runes:\n    BLT•BACON•TOKENS: 1",
    "fee_rate": 50,
    "dry_run": true
  }'
```

Expected response:
```json
{
  "success": true,
  "txid": "...",
  "dry_run": true
}
```

### Check Wallet Balance
```bash
curl https://your-worker.workers.dev/mainnet/wallet-balance
```

## Step 5: Update Main BLT Repository

In the main BLT repository, update `blt/settings.py`:

```python
# Change this:
ORD_SERVER_URL = "http://old-server:9002"

# To this:
ORD_SERVER_URL = "https://your-worker.workers.dev"
```

## Security Checklist

Before going to production:

- [ ] Backend server is running behind HTTPS
- [ ] Backend server only accepts connections from Cloudflare IPs
- [ ] `WALLET_API_PASSWORD` is strong and unique
- [ ] Environment variables are not in version control
- [ ] Tested with `dry_run: true` multiple times
- [ ] Rate limiting is configured appropriately
- [ ] Monitoring and logging are set up

## Troubleshooting

### Worker can't reach backend
- Check firewall rules
- Verify backend URL is correct
- Ensure backend is using HTTPS
- Check backend logs

### Authentication errors
- Verify `WALLET_API_PASSWORD` matches in both worker and backend
- Check that password is provided for non-dry-run requests

### YAML validation errors
- Check YAML structure matches example in `ord-server/example-split.yaml`
- Ensure YAML is less than 1MB
- Verify addresses are valid Bitcoin addresses

## Getting Help

- **Documentation**: See README.md for detailed information
- **Issues**: https://github.com/OWASP-BLT/BLT-Bacon/issues
- **Slack**: Join #project-blt on OWASP Slack
- **Migration Guide**: See MIGRATION.md for more details

## Architecture Diagram

```
┌─────────┐
│ Client  │
└────┬────┘
     │ HTTPS
     v
┌────────────────────┐
│ Cloudflare Worker  │  <- You are here
│ (API Gateway)      │
│ - Validation       │
│ - Authentication   │
│ - Rate Limiting    │
└────────┬───────────┘
         │ HTTPS
         v
┌────────────────────┐
│ Backend Ord Server │
│ (Flask)            │
│ - Bitcoin RPC      │
│ - Ord Operations   │
└────────┬───────────┘
         │ RPC
         v
┌────────────────────┐
│ Bitcoin Node       │
│ + Runes Support    │
└────────────────────┘
```

## Next Steps

1. ✅ Backend server running
2. ✅ Worker deployed
3. ✅ Health check passing
4. ✅ Dry run test successful
5. 🔜 Update main BLT repo
6. 🔜 Monitor in production
7. 🔜 Celebrate! 🎉
