# Cek Bansos API

Automated API service to check NIK (Nomor Induk Kependudukan) status on the Indonesian Ministry of Social Affairs' Cek Bansos website (https://cekbansos.kemensos.go.id/).

This service uses browser automation with AI-powered CAPTCHA solving to provide programmatic access to the Cek Bansos data.

## Features

- 🔐 **Secure API** with Bearer token authentication
- 🤖 **AI-Powered CAPTCHA Solving** with 2 provider options:
  - **Local Ollama** (free, self-hosted)
  - **9router Proxy** (cloud API, faster)
- 🌐 **Browser Automation** via browser-use CLI
- 🐳 **Docker Compose** setup for easy deployment
- 📊 **Structured JSON Response** with desil and demographic data
- ⚡ **Flexible Deployment** - Choose between local or cloud AI

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /check-nik
       │ Bearer Token
       ▼
┌─────────────────┐
│   FastAPI App   │◄──┐
└────────┬────────┘   │
         │            │
    ┌────▼─────┐      │
    │ Browser  │      │
    │   Use    │      │
    └────┬─────┘      │
         │            │
    ┌────▼────────┐   │
    │  CAPTCHA    │   │
    │   Solver    ├───┘
    └──────┬──────┘
           │
     ┌─────┴─────────────────┐
     │                       │
┌────▼────────┐   ┌──────────▼──────────┐
│   Ollama    │   │ 9router / Custom URL │
│ (local)     │   │ (OpenAI-compatible)  │
└─────────────┘   └─────────────────────┘
```

## Prerequisites

### Option 1: Local Ollama (Self-Hosted)
- Docker & Docker Compose
- 4GB+ RAM
- Internet (for initial model download)

### Option 2: 9router Proxy (Cloud)
- Docker (optional, can run without)
- 9router API key ([Get one here](https://9router.com))
- Internet connection

**See [AI_PROVIDER_GUIDE.md](./AI_PROVIDER_GUIDE.md) for detailed comparison**

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd cek-bansos-api
```

### 2. Choose your AI provider

#### Option A: Local Ollama (Free, Self-Hosted)

```bash
cp .env.example .env
nano .env
```

Configure:
```bash
API_KEY=your-secret-api-key-here
AI_PROVIDER=ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=gemma4:e2b      # change to any Ollama vision model you have
```

Start with Ollama:
```bash
docker compose -f docker-compose.ollama.yml up -d
```

This will:
1. Start Ollama service
2. Download gemma4:e2b model (~7GB, 5-10 minutes)
3. Start API service

#### Option B: 9router Proxy (Cloud API, Faster)

```bash
cp .env.example .env
nano .env
```

Configure:
```bash
API_KEY=your-secret-api-key-here
AI_PROVIDER=9router

# Required
NINEROUTER_API_KEY=your-9router-api-key-here

# Optional — customize endpoint and model
NINEROUTER_URL=https://api.9router.com      # or your own proxy URL
NINEROUTER_MODEL=gemma4:e2b                 # any vision model your endpoint supports
```

Start API only (no Ollama needed):
```bash
docker compose -f docker-compose.9router.yml up -d
```

**Get 9router API key:** https://9router.com

### 3. Verify deployment

```bash
# Check if services are running
docker compose ps

# Check API health
curl http://localhost:8000/health

# View logs
docker compose logs -f api
```

## API Usage

### Endpoint

```
POST http://localhost:8000/check-nik
```

### Authentication

All requests require a Bearer token in the Authorization header:

```
Authorization: Bearer <your-api-key>
```

### Request Body

```json
{
  "nik": "1234567890123456"
}
```

- **nik**: 16-digit Indonesian National ID number

### Response

**Success (200):**

```json
{
  "status": "success",
  "nik": "1234567890123456",
  "data": {
    "nama": "W****N L***I S******I F*****S",
    "desil": "BELUM ADA DESIL",
    "sembako": { "status": "TIDAK", "periode": "-" },
    "pkh": { "status": "TIDAK", "periode": "-" },
    "pbijk": { "status": "TIDAK", "periode": "-" },
    "status_kpd": "TIDAK",
    "raw_html": "..."
  }
}
```

**Not Found (200):**

When the NIK is found but is not registered as a bansos recipient, the API returns `status: "not_found"` with the raw result table.

```json
{
  "status": "not_found",
  "nik": "1234567890123456",
  "message": "NIK tidak ditemukan pada data penerima manfaat bansos",
  "data": {}
}
```

**Error (400):**

```json
{
  "detail": "NIK must be exactly 16 digits"
}
```

**Error (401):**

```json
{
  "detail": "Invalid API key"
}
```

**Error (500):**

```json
{
  "detail": "Error checking NIK: <error message>"
}
```

### Example cURL Request

```bash
curl -X POST http://localhost:8000/check-nik \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "nik": "1234567890123456"
  }'
```

### Example Python Request

```python
import requests

url = "http://localhost:8000/check-nik"
headers = {
    "Authorization": "Bearer your-secret-api-key-here",
    "Content-Type": "application/json"
}
data = {
    "nik": "1234567890123456"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

### Example JavaScript/Node.js Request

```javascript
const response = await fetch('http://localhost:8000/check-nik', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-secret-api-key-here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    nik: '1234567890123456'
  })
});

const data = await response.json();
console.log(data);
```

## API Documentation

Once the service is running, interactive API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Understanding Desil

The "desil" (decile) value indicates the welfare level of a household in Indonesia:

- **Desil 1-4**: Bottom 40% of households (eligible for PKH and Sembako social assistance)
- **Desil 5**: Can be proposed for PBI-JK health insurance
- **Desil 6-10**: Top 60% of households

Desil is calculated based on socioeconomic variables including:
- Individual characteristics (occupation, education)
- Housing conditions (home condition, electricity)
- Asset ownership

Source: Data Tunggal Sosial dan Ekonomi Nasional (DTSEN)

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | — | Bearer token for API authentication |
| `AI_PROVIDER` | No | `ollama` | AI backend: `ollama` or `9router` |
| `OLLAMA_URL` | No | `http://ollama:11434` | Ollama server base URL |
| `OLLAMA_MODEL` | No | `gemma4:e2b` | Any vision-capable Ollama model |
| `NINEROUTER_API_KEY` | If 9router | — | Your 9router API key |
| `NINEROUTER_URL` | No | `https://api.9router.com` | 9router (or compatible) base URL — bring your own proxy |
| `NINEROUTER_MODEL` | No | `gemma4:e2b` | Any vision model supported by your endpoint |

### Using a Custom OpenAI-Compatible Endpoint

`NINEROUTER_URL` accepts any OpenAI-compatible base URL, not just 9router.
The service appends `/v1/chat/completions` automatically. Both forms work:

```
# Omit /v1 (auto-appended)
NINEROUTER_URL=https://9router.ruangpelaut.com

# Or include it
NINEROUTER_URL=https://9router.ruangpelaut.com/v1
```

Example for a proxy model (e.g. `ollama/gemma4` on a 9router-compatible gateway):

```
AI_PROVIDER=9router
NINEROUTER_URL=https://9router.ruangpelaut.com/v1
NINEROUTER_API_KEY=sk-xxxxx
NINEROUTER_MODEL=ollama/gemma4
```

```bash
# 9router (default)
NINEROUTER_URL=https://api.9router.com

# Self-hosted LiteLLM proxy
NINEROUTER_URL=http://my-litellm-server:4000

# Any other OpenAI-compatible proxy
NINEROUTER_URL=https://my-custom-proxy.example.com
```

### Changing the Model

You can use any vision-capable model available on your endpoint:

```bash
# Ollama examples
OLLAMA_MODEL=gemma4:e2b
OLLAMA_MODEL=qwen2.5vl:3b
OLLAMA_MODEL=llava:7b

# 9router / OpenAI-compatible examples
NINEROUTER_MODEL=gemma4:e2b
NINEROUTER_MODEL=gpt-4o
NINEROUTER_MODEL=qwen2.5vl:3b
```

### Docker Compose Files

| File | Services | Use for |
|------|----------|---------|
| `docker-compose.ollama.yml` | ollama, model-downloader, api | Local Ollama deployment |
| `docker-compose.9router.yml` | api | 9router / custom proxy deployment |
| `docker-compose.yml` | api | Generic / legacy |

## Troubleshooting

### Services won't start

```bash
docker compose -f docker-compose.ollama.yml logs
docker compose -f docker-compose.ollama.yml down
docker compose -f docker-compose.ollama.yml up -d
```

### Model download failed

```bash
docker compose -f docker-compose.ollama.yml exec ollama ollama pull gemma4:e2b
```

### CAPTCHA solving fails

The service retries up to 3 times automatically. If accuracy is low:

1. Try a larger/better vision model via `OLLAMA_MODEL` or `NINEROUTER_MODEL`
2. For 9router: verify your `NINEROUTER_URL` and `NINEROUTER_API_KEY`
3. Check API logs: `docker compose -f docker-compose.ollama.yml logs api`

### Browser automation fails

```bash
docker compose -f docker-compose.ollama.yml restart api
```

### Out of memory

Ollama with gemma4:e2b requires ~4GB RAM. Increase Docker memory limit in Docker Desktop settings or switch to `AI_PROVIDER=9router`.

## Development

### Local Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install browser-use CLI
pip install browser-use

# Set environment variables
export API_KEY=test-key
export OLLAMA_URL=http://localhost:11434

# Run Ollama locally (if not using Docker)
ollama pull gemma4:e2b

# Run the API
uvicorn app.main:app --reload
```

### Project Structure

```
cek-bansos-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── auth.py                    # API key authentication
│   ├── browser.py                 # Browser automation logic
│   └── captcha.py                 # CAPTCHA solver (Ollama + 9router/custom)
├── docker-compose.ollama.yml      # Local Ollama deployment
├── docker-compose.9router.yml     # 9router / custom proxy deployment
├── docker-compose.yml             # Generic / legacy
├── Dockerfile                     # API service container
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore
└── README.md
```

## Performance

- **Average request time**: 10-20 seconds (depends on CAPTCHA solving)
- **CAPTCHA accuracy**: ~70-80% (3 retry attempts)
- **Concurrent requests**: Limited by browser session (sequential processing)

## Limitations

- Sequential processing (one NIK check at a time)
- CAPTCHA solving accuracy depends on image quality
- Rate limiting may apply from the source website
- Requires internet connection to access cekbansos.kemensos.go.id

## Security Notes

- Never commit your `.env` file with real API keys
- Change the default `API_KEY` before deployment
- Use HTTPS in production (add reverse proxy like nginx)
- Consider rate limiting for production use
- Keep dependencies updated for security patches

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is for educational and automation purposes only. Users are responsible for complying with the terms of service of https://cekbansos.kemensos.go.id/ and applicable laws. The authors are not responsible for any misuse of this tool.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Acknowledgments

- [Ollama](https://ollama.com/) - Local AI model runtime
- [browser-use](https://github.com/browser-use/browser-use) - Browser automation CLI
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Kemensos](https://kemensos.go.id/) - Indonesian Ministry of Social Affairs
