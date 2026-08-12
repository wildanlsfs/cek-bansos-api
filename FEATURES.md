# Cek Bansos API - Features

## 🎯 Core Functionality

### NIK Verification
- Check Indonesian National ID (NIK) status on Kemensos website
- Retrieve desil (welfare level) information
- Get demographic data (name, address, province, etc.)
- Structured JSON response

### API Endpoint
```
POST /check-nik
Authorization: Bearer {API_KEY}
Content-Type: application/json
Body: {"nik": "16-digit-number"}
```

---

## 🔐 Security

### Authentication
- Bearer token authentication
- Configurable API key via environment
- Secure token validation on every request

### Data Protection
- No persistent storage of NIK data
- Local processing option (Ollama)
- HTTPS ready (with reverse proxy)

---

## 🤖 AI-Powered CAPTCHA Solving

### Dual Provider Support

#### Option 1: Local Ollama
- Model: gemma4:e2b (5.1B parameters, Q4_K_M quantization)
- Size: 7.2 GB
- Speed: ~47 seconds per CAPTCHA
- Cost: Free
- Privacy: 100% local
- Requirements: 4GB+ RAM

#### Option 2: 9router Cloud API
- Model: gemma4:e2b (hosted)
- Speed: ~10-15 seconds per CAPTCHA
- Cost: Pay per request (~$0.001-0.01)
- Privacy: Cloud-based
- Requirements: API key, internet

### CAPTCHA Handling
- Automatic image capture
- Base64 encoding
- Vision model inference
- Text extraction and cleaning
- Retry logic (up to 3 attempts)

---

## 🌐 Browser Automation

### Technology
- browser-use CLI (Chromium-based)
- Headless mode by default
- Session persistence
- Element state tracking

### Capabilities
- Navigate to website
- Fill form fields
- Click buttons
- Capture screenshots
- Extract HTML content
- Handle dynamic content

### Flow
1. Open cekbansos.kemensos.go.id
2. Identify form elements (NIK input, CAPTCHA input, submit button)
3. Fill NIK value
4. Capture and solve CAPTCHA
5. Submit form
6. Wait for result
7. Extract and parse response
8. Return structured JSON

---

## 🐳 Docker Deployment

### Services
- **ollama** - AI model server (optional)
- **model-downloader** - One-time model download (optional)
- **api** - FastAPI application (always)

### Profiles
- `ollama` profile: Full stack with local AI
- Default: API only (for 9router)

### Commands
```bash
# With Ollama
docker compose --profile ollama up -d

# With 9router
docker compose up -d api

# Stop services
docker compose down

# View logs
docker compose logs -f api
```

---

## 📊 Response Format

### Success Response
```json
{
  "status": "success",
  "nik": "1234567890123456",
  "data": {
    "nama": "John Doe",
    "nik": "1234567890123456",
    "alamat": "Jl. Example No. 123",
    "desa_kelurahan": "Kelurahan Example",
    "kecamatan": "Kecamatan Example",
    "kabupaten_kota": "Kota Example",
    "provinsi": "Provinsi Example",
    "desil": "3",
    "raw_html": "..."
  }
}
```

### Error Responses
```json
{
  "detail": "Invalid API key"
}

{
  "detail": "NIK must be exactly 16 digits"
}

{
  "detail": "Error checking NIK: <error message>"
}
```

---

## ⚙️ Configuration

### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | - | API authentication key |
| `AI_PROVIDER` | No | `ollama` | AI provider: `ollama` or `9router` |
| `OLLAMA_URL` | No | `http://ollama:11434` | Ollama server URL |
| `NINEROUTER_API_KEY` | Conditional | - | 9router API key (if using 9router) |

### Docker Compose Variables
```yaml
environment:
  - API_KEY=${API_KEY}
  - AI_PROVIDER=${AI_PROVIDER:-ollama}
  - OLLAMA_URL=${OLLAMA_URL:-http://ollama:11434}
  - NINEROUTER_API_KEY=${NINEROUTER_API_KEY:-}
```

---

## 📈 Performance

### Timing Breakdown (Local Ollama)
1. Browser initialization: ~2 seconds
2. Form navigation: ~2 seconds
3. CAPTCHA capture: ~1 second
4. CAPTCHA solving: ~47 seconds
5. Form submission: ~2 seconds
6. Result extraction: ~5 seconds
**Total: ~59 seconds**

### Timing Breakdown (9router)
1. Browser initialization: ~2 seconds
2. Form navigation: ~2 seconds
3. CAPTCHA capture: ~1 second
4. CAPTCHA solving: ~12 seconds
5. Form submission: ~2 seconds
6. Result extraction: ~5 seconds
**Total: ~24 seconds**

### Throughput
- Sequential processing (one request at a time)
- ~50-60 requests/hour (Ollama)
- ~100-150 requests/hour (9router)

---

## 🔄 Retry Logic

### CAPTCHA Retries
- Maximum 3 attempts per request
- Automatic retry on incorrect CAPTCHA
- Fresh CAPTCHA image each attempt

### Error Handling
- Browser session cleanup on failure
- Timeout handling (30s for browser commands)
- Graceful degradation

---

## 📚 Documentation

### Available Docs
1. **README.md** - Main documentation
2. **QUICKSTART.md** - Fast setup guide
3. **AI_PROVIDER_GUIDE.md** - Provider comparison
4. **DEPLOYMENT.md** - Production deployment
5. **FEATURES.md** - This file
6. **API Documentation** - Swagger UI at `/docs`

### Interactive API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🛠️ Developer Features

### Python API
```python
from app.browser import check_nik_bansos

result = check_nik_bansos("1234567890123456")
print(result)
```

### CAPTCHA Solver API
```python
from app.captcha import solve_captcha

text = solve_captcha("/path/to/captcha.png")
print(text)  # "ABC123"
```

### Provider Selection
```python
import os
os.environ['AI_PROVIDER'] = 'ollama'  # or '9router'

from app.captcha import solve_captcha
text = solve_captcha("/path/to/image.png")
```

---

## 🎨 Extensibility

### Add New Providers
```python
# app/captcha.py
def solve_captcha_newprovider(image_path: str, api_key: str) -> str:
    # Implementation here
    pass

def solve_captcha(image_path: str) -> str:
    provider = os.getenv("AI_PROVIDER", "ollama")
    
    if provider == "newprovider":
        return solve_captcha_newprovider(image_path, api_key)
    # ... existing providers
```

### Custom Endpoints
```python
# app/main.py
@app.post("/custom-endpoint")
async def custom_handler():
    # Add custom logic
    pass
```

---

## 🔍 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
# {"status":"healthy"}
```

### Logs
```bash
# API logs
docker compose logs -f api

# Ollama logs
docker compose logs -f ollama

# All logs
docker compose logs -f
```

### Metrics
- Request count
- Response times
- CAPTCHA accuracy
- Error rates

---

## 🚨 Limitations

### Current Limitations
1. **Sequential Processing**: One request at a time
2. **CAPTCHA Accuracy**: Not 100% (retry mechanism helps)
3. **Speed**: 24-60 seconds per request (provider dependent)
4. **Website Dependency**: Relies on cekbansos.kemensos.go.id availability

### Future Improvements
- Parallel request processing
- CAPTCHA accuracy optimization
- Response caching
- Rate limiting
- Request queuing
- WebSocket support for real-time updates

---

## 📊 Use Cases

### Suitable For
- Batch NIK verification
- Integration with other systems
- Automated reporting
- Data validation pipelines
- Research and analysis

### Not Suitable For
- Real-time verification (too slow)
- High-frequency requests (>1000/hour)
- Mission-critical systems (website dependency)

---

## 🌟 Unique Selling Points

1. **Dual Provider** - Choose between free local or fast cloud
2. **Docker Ready** - One command deployment
3. **Well Documented** - 2,800+ lines of documentation
4. **Flexible** - Switch providers without code changes
5. **Secure** - Bearer token authentication
6. **Open Source** - MIT License
7. **Production Ready** - Error handling, retries, logging

---

## 📞 Support

- Documentation: See README.md and other docs
- Issues: GitHub Issues
- Updates: Check repository for latest version
- Community: Contributions welcome

---

**Last Updated:** August 12, 2026  
**Version:** 2.0 (Dual Provider)
