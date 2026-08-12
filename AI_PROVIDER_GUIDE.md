# AI Provider Configuration Guide

This service supports two AI providers for CAPTCHA solving:

1. **Local Ollama** (free, requires setup)
2. **9router Proxy** (paid API, no setup required)

---

## Option 1: Local Ollama (Recommended for Self-Hosting)

### Pros
- ✅ Free (no API costs)
- ✅ Complete privacy (data stays local)
- ✅ No internet dependency after setup
- ✅ Unlimited requests

### Cons
- ❌ Requires 4GB+ RAM
- ❌ ~10-15 minute initial model download
- ❌ ~47 seconds per CAPTCHA
- ❌ Requires Docker or local installation

### Setup with Docker Compose

```bash
# 1. Configure environment
cp .env.example .env
nano .env
```

Edit `.env`:
```bash
API_KEY=your-secret-api-key-here
AI_PROVIDER=ollama
OLLAMA_URL=http://ollama:11434
```

```bash
# 2. Start with Ollama profile
docker compose --profile ollama up -d

# This will:
# - Start Ollama service
# - Download gemma4:e2b model (~7.2GB)
# - Start API service

# 3. Wait for model download (check logs)
docker compose logs -f model-downloader

# 4. Test
curl -X POST http://localhost:8000/check-nik \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"nik": "1234567890123456"}'
```

### Setup Locally (Without Docker)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama
ollama serve &

# 3. Download model
ollama pull gemma4:e2b

# 4. Configure environment
export API_KEY=your-secret-api-key-here
export AI_PROVIDER=ollama
export OLLAMA_URL=http://localhost:11434

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Start API
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Option 2: 9router Proxy (Recommended for Quick Start)

### Pros
- ✅ No local setup required
- ✅ Faster inference (~10-15 seconds)
- ✅ No RAM requirements
- ✅ Cloud-based, scalable
- ✅ Works anywhere with internet

### Cons
- ❌ Costs per API call
- ❌ Requires internet connection
- ❌ Data sent to third-party
- ❌ Requires API key

### Setup

```bash
# 1. Get API Key
# Visit https://9router.com and create an account
# Get your API key from dashboard

# 2. Configure environment
cp .env.example .env
nano .env
```

Edit `.env`:
```bash
API_KEY=your-secret-api-key-here
AI_PROVIDER=9router
NINEROUTER_API_KEY=your-9router-api-key-here
```

```bash
# 3. Start API only (no Ollama needed)
docker compose up -d api

# Or locally:
export API_KEY=your-secret-api-key-here
export AI_PROVIDER=9router
export NINEROUTER_API_KEY=your-9router-api-key-here
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 9router Pricing

Check current pricing at: https://9router.com/pricing

Estimated costs:
- Per CAPTCHA solve: ~$0.001-0.01 (depending on model and usage)
- 1,000 requests: ~$1-10
- Monthly subscription plans may be available

---

## Option 3: Hybrid (Switch Between Providers)

You can switch between providers by changing the `AI_PROVIDER` environment variable:

```bash
# Switch to 9router
docker compose down
nano .env  # Change AI_PROVIDER=9router
docker compose up -d api

# Switch back to Ollama
docker compose down
nano .env  # Change AI_PROVIDER=ollama
docker compose --profile ollama up -d
```

---

## Comparison Table

| Feature | Local Ollama | 9router Proxy |
|---------|--------------|---------------|
| **Setup Time** | 15 minutes | 2 minutes |
| **Cost** | Free | Pay per request |
| **Speed** | ~47 seconds | ~10-15 seconds |
| **RAM Required** | 4GB+ | None |
| **Internet Required** | Setup only | Always |
| **Privacy** | Complete | Data sent to API |
| **Scalability** | Limited by hardware | Unlimited |
| **Best For** | Self-hosting, privacy | Quick start, scale |

---

## Testing Both Providers

```bash
# Test Ollama
export AI_PROVIDER=ollama
export OLLAMA_URL=http://localhost:11434
python3 << 'EOF'
from app.captcha import solve_captcha
result = solve_captcha("/tmp/test_captcha.png")
print(f"Ollama result: {result}")
EOF

# Test 9router
export AI_PROVIDER=9router
export NINEROUTER_API_KEY=your-api-key
python3 << 'EOF'
from app.captcha import solve_captcha
result = solve_captcha("/tmp/test_captcha.png")
print(f"9router result: {result}")
EOF
```

---

## Recommended Setup by Use Case

### For Production (High Volume)
- Use **Local Ollama** if you have infrastructure
- Saves costs at scale
- Better privacy and control

### For Development/Testing
- Use **9router Proxy** for quick start
- No setup overhead
- Easy to test and validate

### For Low Volume (<1000 requests/month)
- Use **9router Proxy**
- No infrastructure costs
- Faster response time

### For High Security/Privacy
- Use **Local Ollama**
- Data never leaves your server
- Complete control

---

## Troubleshooting

### Ollama Issues

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check model is downloaded
ollama list | grep gemma4

# Re-download model
ollama pull gemma4:e2b

# Check logs
docker compose logs ollama
```

### 9router Issues

```bash
# Test API key
curl -X POST https://api.9router.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:e2b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Check balance/quota
# Visit https://9router.com/dashboard

# Check service status
# Visit https://status.9router.com
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | - | Your API authentication key |
| `AI_PROVIDER` | No | `ollama` | AI provider: `ollama` or `9router` |
| `OLLAMA_URL` | No | `http://ollama:11434` | Ollama server URL (for ollama provider) |
| `NINEROUTER_API_KEY` | Conditional | - | 9router API key (required for 9router provider) |

---

## Migration Between Providers

### From Ollama to 9router

1. Stop services: `docker compose down`
2. Edit `.env`: Set `AI_PROVIDER=9router` and add `NINEROUTER_API_KEY`
3. Start API only: `docker compose up -d api`
4. No data migration needed

### From 9router to Ollama

1. Stop services: `docker compose down`
2. Edit `.env`: Set `AI_PROVIDER=ollama`
3. Start with Ollama: `docker compose --profile ollama up -d`
4. Wait for model download
5. No data migration needed

---

## Performance Benchmarks

Based on testing with gemma4:e2b model:

| Provider | CAPTCHA Solve Time | Total Request Time | Accuracy |
|----------|-------------------|-------------------|----------|
| Local Ollama | ~47 seconds | ~60-70 seconds | TBD |
| 9router Proxy | ~10-15 seconds | ~25-35 seconds | TBD |

*Note: Accuracy testing pending with real CAPTCHA samples*

---

## Support

- **Ollama Documentation**: https://ollama.com/docs
- **9router Documentation**: https://docs.9router.com
- **Issues**: Open an issue on GitHub
