# Implementation Plan: Cek Bansos API Service

## Overview
Build an API service that automates NIK (Indonesian National ID) checking on https://cekbansos.kemensos.go.id/ using browser automation with AI-powered CAPTCHA solving.

---

## Phase 0: Documentation Discovery

### Target Website Analysis
**Source:** https://cekbansos.kemensos.go.id/
- **Form endpoint:** POST to `/cekbansos_nik`
- **Required fields:**
  - `_token`: CSRF token (changes per page load)
  - `nik_input`: 16-digit NIK
  - `captcha`: Text from CAPTCHA image
- **CAPTCHA:** Flat text image at `/captcha/flat?<random>`, refreshable
- **Response:** HTML rendered into modal `#respon_text`

### Browser Automation Tool
**Tool:** browser-use CLI (Python-based)
- **Installation:** `pip install browser-use`
- **Key commands:**
  - `browser-use open <url>` - Navigate
  - `browser-use state` - Get interactive elements with indices
  - `browser-use screenshot` - Capture screenshots (for CAPTCHA)
  - `browser-use input <index> "text"` - Fill form fields
  - `browser-use click <index>` - Click buttons
  - `browser-use get html` - Extract result HTML
  - `browser-use close` - Clean up session

### AI Model for CAPTCHA
**Model:** Ollama with gemma4:e2b (2B parameter model)
- **Docker image:** `ollama/ollama:latest`
- **Model pull:** `ollama pull gemma4:e2b`
- **API endpoint:** `http://localhost:11434/api/generate`
- **Usage:** Send CAPTCHA screenshot, get text response

---

## Phase 1: Project Structure & Docker Compose Setup

### 1.1 Create Project Files
```
cek-bansos-api/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── browser.py        # Browser automation logic
│   ├── captcha.py        # CAPTCHA solving with Ollama
│   └── auth.py           # API key authentication
├── README.md
└── .gitignore
```

### 1.2 Docker Compose Configuration
Create `docker-compose.yml` with:
- **ollama service:** 
  - Image: `ollama/ollama:latest`
  - Volumes: `ollama-data:/root/.ollama`
  - Ports: `11434:11434`
  - Healthcheck: `curl -f http://localhost:11434/api/tags || exit 1`
- **model-downloader service:**
  - Depends on: ollama
  - Command: `ollama pull gemma4:e2b`
  - Run once, exit after download
- **api service:**
  - Build from Dockerfile
  - Depends on: ollama, model-downloader
  - Ports: `8000:8000`
  - Environment: API_KEY, OLLAMA_URL

### 1.3 Python Dependencies
Create `requirements.txt`:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
browser-use>=0.1.0
requests==2.31.0
pillow==10.2.0
python-dotenv==1.0.0
```

---

## Phase 2: API Service Implementation

### 2.1 Authentication Middleware
File: `app/auth.py`
- Bearer token validation
- API key verification from environment variable
- Return 401 if invalid

### 2.2 FastAPI Application
File: `app/main.py`
- **Endpoint:** `POST /check-nik`
- **Request body:** `{"nik": "1234567890123456"}`
- **Response:** `{"status": "success", "data": {...}, "desil": "..."}`
- **Auth:** Require `Authorization: Bearer <API_KEY>` header
- **Flow:**
  1. Validate NIK (16 digits)
  2. Call browser automation
  3. Return JSON result

### 2.3 Browser Automation
File: `app/browser.py`

**Function:** `check_nik_bansos(nik: str) -> dict`

**Steps:**
1. `browser-use open https://cekbansos.kemensos.go.id/`
2. `browser-use state` - Get form element indices
3. `browser-use screenshot /tmp/captcha.png` - Capture CAPTCHA
4. Call `solve_captcha("/tmp/captcha.png")` - Get CAPTCHA text
5. `browser-use input <nik_index> "<nik>"` - Fill NIK field
6. `browser-use input <captcha_index> "<captcha_text>"` - Fill CAPTCHA
7. `browser-use click <submit_index>` - Submit form
8. `browser-use wait selector "#respon_text"` - Wait for result
9. `browser-use get html --selector "#respon_text"` - Extract result HTML
10. Parse HTML to JSON
11. `browser-use close` - Clean up
12. Return structured data

**Error handling:**
- Retry CAPTCHA if incorrect (max 3 attempts)
- Timeout after 30 seconds
- Clean up browser session on failure

### 2.4 CAPTCHA Solver
File: `app/captcha.py`

**Function:** `solve_captcha(image_path: str) -> str`

**Steps:**
1. Load image from path
2. Convert to base64
3. POST to Ollama API at `http://ollama:11434/api/generate`:
   ```json
   {
     "model": "gemma4:e2b",
     "prompt": "Extract only the text characters from this CAPTCHA image. Return only the letters/numbers without any explanation.",
     "images": ["<base64_image>"],
     "stream": false
   }
   ```
4. Extract text from response
5. Clean and return (uppercase, no spaces)

---

## Phase 3: Dockerfile & Dependencies

### 3.1 Dockerfile
```dockerfile
FROM python:3.11-slim

# Install browser dependencies
RUN apt-get update && apt-get install -y \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Expose API port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.2 Environment Configuration
Create `.env.example`:
```
API_KEY=your-secret-api-key-here
OLLAMA_URL=http://ollama:11434
```

---

## Phase 4: Documentation & Repository Setup

### 4.1 README.md
Include:
- Project description
- Prerequisites (Docker, Docker Compose)
- Quick start:
  ```bash
  cp .env.example .env
  # Edit .env with your API_KEY
  docker-compose up -d
  ```
- API usage example:
  ```bash
  curl -X POST http://localhost:8000/check-nik \
    -H "Authorization: Bearer YOUR_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"nik": "1234567890123456"}'
  ```
- Architecture diagram
- Troubleshooting

### 4.2 .gitignore
```
__pycache__/
*.pyc
.env
.venv/
*.log
/tmp/
```

### 4.3 License
MIT License (open source)

---

## Phase 5: Testing & Verification

### 5.1 Docker Compose Build
```bash
docker-compose build
docker-compose up -d
```

**Verify:**
- Ollama service running: `curl http://localhost:11434/api/tags`
- Model downloaded: Check for gemma4:e2b in tags
- API service running: `curl http://localhost:8000/docs`

### 5.2 API Testing
```bash
# Test authentication
curl -X POST http://localhost:8000/check-nik \
  -H "Authorization: Bearer wrong-key" \
  -d '{"nik": "1234567890123456"}'
# Expected: 401 Unauthorized

# Test with valid key
curl -X POST http://localhost:8000/check-nik \
  -H "Authorization: Bearer <YOUR_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"nik": "1234567890123456"}'
# Expected: 200 with result data
```

### 5.3 Browser Automation Test
- Verify browser-use can open website
- Verify CAPTCHA screenshot capture
- Verify form submission
- Verify result extraction

### 5.4 End-to-End Test
Test complete flow with real NIK (if available from public examples)

---

## Anti-Patterns to Avoid

1. ❌ Don't assume browser element indices - always run `state` first
2. ❌ Don't forget to `browser-use close` - prevents zombie processes
3. ❌ Don't use `--headed` mode in Docker - use headless
4. ❌ Don't hardcode CAPTCHA solving prompts - tune based on actual accuracy
5. ❌ Don't expose API without authentication
6. ❌ Don't commit `.env` file with secrets

---

## Success Criteria

- ✅ Docker Compose starts all services successfully
- ✅ Ollama downloads gemma4:e2b model on first run
- ✅ API endpoint accepts NIK and returns structured JSON
- ✅ CAPTCHA solving accuracy >70%
- ✅ API key authentication works
- ✅ Browser sessions clean up properly
- ✅ README includes clear setup instructions
- ✅ Repository is public and complete

---

## Next Steps

After plan approval:
1. Create project structure
2. Implement Docker Compose configuration
3. Implement API service
4. Implement browser automation
5. Implement CAPTCHA solver
6. Write documentation
7. Test and verify
8. Push to public GitHub repository
