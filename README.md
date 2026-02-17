# 🥓 BLT-BACON Token Distribution Service

**BACON (Blockchain Assisted Contribution Network)** is a Bitcoin-based token distribution service for the OWASP BLT project, built as a Cloudflare Python Worker for high performance and global edge distribution.

## 🌟 Overview

This service handles the distribution of BACON tokens using the Bitcoin Runes protocol. It provides a simple REST API for:
- Sending BACON tokens to contributors on mainnet
- Testing token distribution on regtest
- Checking wallet balances
- Managing batch transactions

## 🏗️ Architecture

This is a **Cloudflare Python Worker** that provides a serverless, globally distributed API for BACON token operations. The worker communicates with Bitcoin nodes and ordinal servers to execute token transactions.

### Technology Stack
- **Python 3.11+** - Core language
- **Cloudflare Workers** - Serverless edge computing platform
- **Bitcoin Runes** - Fungible token protocol on Bitcoin
- **Ord** - Ordinals and Runes wallet/indexer

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 14+ (for Cloudflare tooling)
- `uv` package manager ([installation guide](https://github.com/astral-sh/uv))
- Cloudflare Workers account
- Bitcoin node with Runes support
- Ord server/indexer

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/OWASP-BLT/BLT-Bacon.git
cd BLT-Bacon
```

### 2. Install Dependencies

```bash
# Install uv if you haven't already
pip install uv

# Install project dependencies
uv pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 4. Deploy to Cloudflare

```bash
# Deploy to Cloudflare Workers
uv run pywrangler deploy

# Or run locally for testing
uv run pywrangler dev
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

Returns service status and version information.

**Response:**
```json
{
  "status": "healthy",
  "service": "BLT-BACON Token Distribution Service",
  "version": "1.0.0"
}
```

### Send Tokens (Mainnet)
```http
POST /mainnet/send-bacon-tokens
Content-Type: application/json
```

Send BACON tokens to one or more addresses on Bitcoin mainnet.

**Request Body:**
```json
{
  "yaml_content": "outputs:\n- address: bc1...\n  runes:\n    BLT•BACON•TOKENS: 10",
  "fee_rate": 50,
  "dry_run": true,
  "password": "your_secure_password"
}
```

**Parameters:**
- `yaml_content` (required): YAML-formatted transaction specification
- `fee_rate` (required): Transaction fee rate in sat/vB
- `dry_run` (optional): If true, simulates transaction without broadcasting (default: true)
- `password` (required when dry_run=false): API password for authorization

**Response:**
```json
{
  "success": true,
  "txid": "abc123...",
  "dry_run": true
}
```

### Send Tokens (Regtest)
```http
POST /regtest/send-bacon-tokens
Content-Type: application/json
```

Send BACON tokens on regtest for testing purposes.

**Request Body:**
```json
{
  "num_users": 5,
  "fee_rate": 50
}
```

**Parameters:**
- `num_users` (required): Number of recipients (generates test addresses)
- `fee_rate` (required): Transaction fee rate in sat/vB

**Response:**
```json
{
  "success": true,
  "txid": "test123...",
  "dry_run": true
}
```

### Get Wallet Balance
```http
GET /mainnet/wallet-balance
```

Get the current balance of the mainnet wallet.

**Response:**
```json
{
  "success": true,
  "balance": "..."
}
```

## 🔧 Configuration

### Environment Variables

All configuration is done through environment variables. See `.env.example` for a complete list.

**Required Variables:**
- `ORD_PATH` - Path to ord binary
- `BITCOIN_RPC_USER_MAINNET` - Bitcoin RPC username
- `BITCOIN_RPC_PASSWORD_MAINNET` - Bitcoin RPC password
- `BITCOIN_RPC_URL_MAINNET` - Bitcoin RPC URL
- `ORD_SERVER_URL_MAINNET` - Ord server URL
- `WALLET_NAME_MAINNET` - Wallet name
- `WALLET_API_PASSWORD` - API password for transactions

### Cloudflare Configuration

Edit `wrangler.jsonc` to customize deployment settings:

```jsonc
{
  "name": "blt-bacon-worker",
  "main": "src/entry.py",
  "compatibility_flags": ["python_workers"],
  "compatibility_date": "2026-02-17"
}
```

## 🧪 Testing

### Local Testing

```bash
# Run the worker locally
uv run pywrangler dev

# Test with curl
curl http://localhost:8787/health
```

### Test Token Distribution

```bash
# Test with dry-run (no actual transaction)
curl -X POST http://localhost:8787/mainnet/send-bacon-tokens \
  -H "Content-Type: application/json" \
  -d '{
    "yaml_content": "outputs:\n- address: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh\n  runes:\n    BLT•BACON•TOKENS: 1",
    "fee_rate": 50,
    "dry_run": true
  }'
```

## 🔐 Security

- **Password Protection**: Production transactions require authentication via `WALLET_API_PASSWORD`
- **Dry Run Mode**: Always test with `dry_run: true` before executing real transactions
- **Environment Variables**: Never commit credentials to version control
- **Rate Limiting**: Consider implementing rate limiting for production deployments

## 📚 Documentation

For more detailed information:
- [Full Documentation](https://owasp-blt.github.io/BLT-Bacon/)
- [OWASP BLT Project](https://owaspblt.org/)
- [Bitcoin Runes Protocol](https://docs.ordinals.com/runes.html)
- [Cloudflare Workers Python](https://developers.cloudflare.com/workers/languages/python/)

## 🤝 Contributing

We welcome contributions! Please see the [OWASP BLT Contributing Guide](https://github.com/OWASP-BLT/BLT/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is part of OWASP BLT and is licensed under the AGPL-3.0 License. See the [LICENSE](LICENSE) file for details.

## 🎯 Project Structure

```
BLT-Bacon/
├── src/
│   └── entry.py          # Main Cloudflare Worker entry point
├── docs/                 # Documentation website
├── wrangler.jsonc        # Cloudflare Workers configuration
├── pyproject.toml        # Python dependencies
├── .env.example          # Environment variables template
├── index.html            # API documentation page
└── README.md             # This file
```

## 🔗 Related Repositories

- [OWASP BLT](https://github.com/OWASP-BLT/BLT) - Main Bug Logging Tool
- [BLT-Extension](https://github.com/OWASP-BLT/BLT-Extension) - Browser extension
- [BLT-Action](https://github.com/OWASP-BLT/BLT-Action) - GitHub Action

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/OWASP-BLT/BLT-Bacon/issues)
- **Slack**: [OWASP Slack #project-blt](https://owasp.org/slack/invite)
- **Twitter**: [@OWASP_BLT](https://twitter.com/OWASP_BLT)

---

Made with ❤️ by the OWASP BLT Community
