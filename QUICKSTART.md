# Quick Start Guide

Choose your deployment method based on your needs:

---

## 🚀 Option 1: Cloud (9router) - Fastest Setup

**Best for:** Quick testing, low volume, no infrastructure

**Time to deploy:** 2 minutes

```bash
# 1. Get API key from https://9router.com
# 2. Configure
cp .env.example .env
nano .env

# Set:
# AI_PROVIDER=9router
# NINEROUTER_API_KEY=your-key-here

# 3. Start
docker compose up -d api

# 4. Test
curl -X POST http://localhost:8000/check-nik \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"nik": "1234567890123456"}'
```

**Pros:** Fast (10-15s), no setup, no RAM needed  
**Cons:** Costs per request, requires internet

---

## 🏠 Option 2: Self-Hosted (Ollama) - Free Forever

**Best for:** High volume, privacy, self-hosting

**Time to deploy:** 15 minutes

```bash
# 1. Configure
cp .env.example .env
nano .env

# Set:
# AI_PROVIDER=ollama

# 2. Start (downloads model automatically)
docker compose --profile ollama up -d

# Wait ~10 minutes for model download
docker compose logs -f model-downloader

# 3. Test
curl -X POST http://localhost:8000/check-nik \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"nik": "1234567890123456"}'
```

**Pros:** Free, private, unlimited  
**Cons:** Slower (47s), needs 4GB RAM, setup time

---

## 📊 Comparison

| Feature | 9router Cloud | Ollama Local |
|---------|--------------|--------------|
| Setup time | 2 min | 15 min |
| Cost | ~$0.001/request | Free |
| Speed | 10-15s | 47s |
| RAM needed | 0 | 4GB+ |
| Privacy | Cloud | 100% local |
| Best for | Testing, low volume | Production, high volume |

---

## 🔄 Switch Providers Anytime

```bash
# Stop services
docker compose down

# Edit .env
nano .env
# Change AI_PROVIDER=ollama or AI_PROVIDER=9router

# Restart
docker compose --profile ollama up -d  # for Ollama
# or
docker compose up -d api  # for 9router
```

---

## 📚 Full Documentation

- **Detailed Guide:** [AI_PROVIDER_GUIDE.md](./AI_PROVIDER_GUIDE.md)
- **API Usage:** [README.md](./README.md)
- **Deployment:** [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 🆘 Troubleshooting

### 9router Issues
```bash
# Test API key
curl https://api.9router.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Ollama Issues
```bash
# Check model downloaded
docker compose exec ollama ollama list

# Re-download model
docker compose exec ollama ollama pull gemma4:e2b
```

### API Issues
```bash
# Check logs
docker compose logs api

# Restart
docker compose restart api
```

---

## ✅ What's Next?

1. **Test with real NIK** (Indonesian national ID)
2. **Monitor CAPTCHA accuracy**
3. **Scale if needed** (add more containers)
4. **Add monitoring** (logs, metrics)

---

**Ready to deploy?** Pick your option above and get started! 🎉
