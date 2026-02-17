# 📦 Legacy Flask Server (Deprecated)

> **⚠️ DEPRECATED**: This Flask-based server has been replaced by a Cloudflare Python Worker.
> 
> See the root directory for the new implementation in `src/entry.py`.
> 
> Read `MIGRATION.md` in the root directory for migration details.

## What's Here

This directory contains the legacy Flask-based BACON token distribution server. It is kept for reference and as a fallback option.

## Files

- `ord-api.py` - Original Flask application
- `requirements.txt` - Flask dependencies
- `.env.example` - Environment configuration
- `ord-flask.service` - Systemd service file
- `example-split.yaml` - Example transaction YAML format

## Migration Status

This implementation has been **superseded** by the Cloudflare Python Worker in `src/entry.py`. 

### Why We Migrated

1. **Performance**: Edge computing provides lower latency globally
2. **Scalability**: Automatic scaling without server management
3. **Reliability**: Built-in DDoS protection and high availability
4. **Cost**: Pay-per-request model vs. always-on server
5. **Security**: Cloudflare's security features included

## If You Need to Use This

While not recommended, you can still run the Flask server:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run the server
python ord-api.py
```

Or with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:9002 ord-api:app
```

## Recommendation

**Use the new Cloudflare Worker instead!** See the root README.md for setup instructions.

For questions, open an issue on [GitHub](https://github.com/OWASP-BLT/BLT-Bacon/issues).
