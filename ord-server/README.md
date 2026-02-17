# 📦 Backend Ord Server (Flask)

> **ℹ️ NOTE**: This is the backend server that executes actual Bitcoin/Runes operations.
> 
> The Cloudflare Worker in `src/entry.py` acts as an API gateway and forwards validated requests to this backend.

## Architecture

```
Client → Cloudflare Worker (Gateway) → This Backend Server → Bitcoin Node
```

The Cloudflare Worker provides:
- Request validation
- Authentication
- Rate limiting
- Global edge distribution

This backend server provides:
- Bitcoin RPC communication
- Ord wallet operations
- Transaction execution
- File system operations

## What's Here

This directory contains the Flask-based backend server that handles BACON token distribution.

## Files

- `ord-api.py` - Flask backend application
- `requirements.txt` - Flask dependencies
- `.env.example` - Environment configuration
- `ord-flask.service` - Systemd service file
- `example-split.yaml` - Example transaction YAML format

## Setup Instructions

### 1. Install Dependencies

```bash
cd ord-server
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env
```

Configure all Bitcoin RPC and ord settings.

### 3. Run the Server

**Development:**
```bash
python ord-api.py
```

**Production with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:9002 ord-api:app
```

**With systemd:**
```bash
sudo cp ord-flask.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start ord-flask.service
sudo systemctl enable ord-flask.service
```

## Security Recommendations

- Run behind a firewall
- Only accept connections from Cloudflare Worker IPs
- Use HTTPS with valid certificates
- Keep Bitcoin RPC credentials secure
- Run as non-privileged user
- Monitor logs for suspicious activity

## Connecting to Cloudflare Worker

Once this backend is running, configure the Cloudflare Worker:

1. Set `ORD_BACKEND_URL` in the worker's environment to this server's URL
2. Ensure this backend is accessible from Cloudflare's network
3. Use HTTPS for production deployments

Example: `ORD_BACKEND_URL=https://ord-backend.example.com`

## Endpoints

This backend provides the same endpoints as documented in the main README:
- `POST /mainnet/send-bacon-tokens`
- `POST /regtest/send-bacon-tokens`
- `GET /mainnet/wallet-balance`
