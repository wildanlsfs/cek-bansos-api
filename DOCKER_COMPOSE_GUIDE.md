# Docker Compose Files Guide

This project includes **3 docker-compose files** for flexible deployment:

---

## 📁 Available Files

### 1. `docker-compose.ollama.yml` (Recommended for Self-Hosting)
Full stack with local Ollama AI.

**Use when:**
- You want free, unlimited requests
- Privacy is important
- You have 4GB+ RAM available

**Deploy:**
```bash
docker compose -f docker-compose.ollama.yml up -d
```

**Services:**
- `ollama` - AI model server
- `model-downloader` - Downloads gemma4:e2b model
- `api` - FastAPI application

---

### 2. `docker-compose.9router.yml` (Recommended for Cloud)
API only, uses 9router cloud API.

**Use when:**
- You want fast setup (2 minutes)
- Speed is priority (~2.5x faster)
- You don't have much RAM

**Deploy:**
```bash
docker compose -f docker-compose.9router.yml up -d
```

**Services:**
- `api` - FastAPI application only

---

### 3. `docker-compose.yml` (Default/Legacy)
Generic configuration that adapts based on environment variables.

**Use when:**
- You want backward compatibility
- You're migrating from v1.0

**Deploy:**
```bash
docker compose up -d
```

**Note:** This file is kept for compatibility. New deployments should use the specific compose files above.

---

## 🚀 Quick Start

### For Ollama (Self-Hosted):
```bash
cp .env.example .env
nano .env  # Set AI_PROVIDER=ollama
docker compose -f docker-compose.ollama.yml up -d
```

### For 9router (Cloud):
```bash
cp .env.example .env
nano .env  # Set AI_PROVIDER=9router, NINEROUTER_API_KEY=...
docker compose -f docker-compose.9router.yml up -d
```

### Using deploy.sh (Auto-selects):
```bash
./deploy.sh
# Automatically uses the correct compose file based on .env
```

---

## 📊 Comparison

| Feature | ollama.yml | 9router.yml | default.yml |
|---------|-----------|-------------|-------------|
| **Services** | 3 (ollama, downloader, api) | 1 (api only) | 1 (api only) |
| **Setup Time** | 15 minutes | 2 minutes | Varies |
| **RAM Required** | 4GB+ | <1GB | Varies |
| **Cost** | Free | Pay per use | Varies |
| **Speed** | ~47s/request | ~12s/request | Varies |
| **Best For** | Production, high volume | Testing, quick start | Migration |

---

## 🔧 Common Commands

### Start Services
```bash
# Ollama
docker compose -f docker-compose.ollama.yml up -d

# 9router
docker compose -f docker-compose.9router.yml up -d
```

### Stop Services
```bash
# Ollama
docker compose -f docker-compose.ollama.yml down

# 9router
docker compose -f docker-compose.9router.yml down
```

### View Logs
```bash
# Ollama
docker compose -f docker-compose.ollama.yml logs -f api

# 9router
docker compose -f docker-compose.9router.yml logs -f api
```

### Restart Services
```bash
# Ollama
docker compose -f docker-compose.ollama.yml restart api

# 9router
docker compose -f docker-compose.9router.yml restart api
```

---

## 🔄 Switching Between Providers

To switch from one provider to another:

```bash
# 1. Stop current services
docker compose -f docker-compose.ollama.yml down
# or
docker compose -f docker-compose.9router.yml down

# 2. Update .env
nano .env  # Change AI_PROVIDER

# 3. Start new services
docker compose -f docker-compose.9router.yml up -d
# or
docker compose -f docker-compose.ollama.yml up -d
```

---

## 📝 Environment Variables

### For Ollama (docker-compose.ollama.yml)
```bash
API_KEY=your-secret-key
AI_PROVIDER=ollama
OLLAMA_URL=http://ollama:11434  # Auto-configured
```

### For 9router (docker-compose.9router.yml)
```bash
API_KEY=your-secret-key
AI_PROVIDER=9router
NINEROUTER_API_KEY=your-9router-key
```

---

## 🆘 Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
docker compose -f docker-compose.ollama.yml ps

# Check model download progress
docker compose -f docker-compose.ollama.yml logs model-downloader

# Restart Ollama
docker compose -f docker-compose.ollama.yml restart ollama
```

### 9router Issues
```bash
# Check API logs
docker compose -f docker-compose.9router.yml logs api

# Verify API key
echo $NINEROUTER_API_KEY

# Restart API
docker compose -f docker-compose.9router.yml restart api
```

---

## 💡 Best Practices

1. **Use specific compose files** instead of the default one
2. **Choose based on needs:** Ollama for production, 9router for testing
3. **Keep .env secure** with strong API keys
4. **Monitor logs** regularly
5. **Use ./deploy.sh** for automatic configuration

---

## 📚 More Information

- See **AI_PROVIDER_GUIDE.md** for detailed provider comparison
- See **QUICKSTART.md** for step-by-step setup
- See **README.md** for complete documentation
