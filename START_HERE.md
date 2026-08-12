# 🚀 START HERE - Cek Bansos API

**Welcome!** This is your complete NIK verification API with dual AI provider support.

---

## ⚡ Quick Deploy (Choose One)

### Option 1: Cloud API (Fastest - 2 minutes)

```bash
# 1. Get 9router API key from https://9router.com
# 2. Configure
cp .env.example .env
nano .env

# Set these values:
API_KEY=your-secret-key
AI_PROVIDER=9router
NINEROUTER_API_KEY=your-9router-key

# 3. Deploy
docker compose -f docker-compose.9router.yml up -d

# 4. Test
curl http://localhost:8000/health
```

**Pros:** Fast (~12s), no setup, no RAM needed  
**Cons:** Costs per request

---

### Option 2: Self-Hosted (Free - 15 minutes)

```bash
# 1. Configure
cp .env.example .env
nano .env

# Set these values:
API_KEY=your-secret-key
AI_PROVIDER=ollama

# 2. Deploy (downloads model automatically)
docker compose -f docker-compose.ollama.yml up -d

# 3. Wait for model download (10-15 minutes)
docker compose -f docker-compose.ollama.yml logs -f model-downloader

# 4. Test
curl http://localhost:8000/health
```

**Pros:** Free, private, unlimited requests  
**Cons:** Slower (~47s), needs 4GB RAM

---

## 📖 Full Documentation

- **QUICKSTART.md** - Detailed setup guide
- **AI_PROVIDER_GUIDE.md** - Compare both providers
- **README.md** - Complete API documentation
- **FEATURES.md** - Feature list
- **DEPLOYMENT.md** - Production deployment

---

## 🧪 Test the API

```bash
curl -X POST http://localhost:8000/check-nik \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"nik": "1234567890123456"}'
```

---

## 📊 Interactive Docs

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔄 Switch Providers Anytime

```bash
docker compose down
nano .env  # Change AI_PROVIDER
docker compose up -d
```

---

## 🆘 Need Help?

1. Check logs: `docker compose logs -f api`
2. Restart: `docker compose restart api`
3. Read docs: See README.md and other guides

---

## ✅ You're Ready!

Pick an option above and deploy in 2-15 minutes! 🚀
