import requests
import base64
import os
from pathlib import Path

def solve_captcha_ollama(image_path: str, ollama_url: str) -> str:
    """Solve CAPTCHA using local Ollama instance"""
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    payload = {
        "model": "gemma4:e2b",
        "prompt": "Extract only the text characters from this CAPTCHA image. Return only the letters and numbers you see, nothing else. No explanations, no punctuation, just the exact text.",
        "images": [img_base64],
        "stream": False
    }
    
    response = requests.post(
        f"{ollama_url}/api/generate",
        json=payload,
        timeout=120
    )
    response.raise_for_status()
    
    result = response.json()
    captcha_text = result.get("response", "").strip()
    
    captcha_text = ''.join(c for c in captcha_text if c.isalnum())
    
    return captcha_text.upper()

def solve_captcha_9router(image_path: str, api_key: str) -> str:
    """Solve CAPTCHA using 9router proxy API"""
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    payload = {
        "model": "gemma4:e2b",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract only the text characters from this CAPTCHA image. Return only the letters and numbers you see, nothing else. No explanations, no punctuation, just the exact text."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.9router.com/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=120
    )
    response.raise_for_status()
    
    result = response.json()
    captcha_text = result["choices"][0]["message"]["content"].strip()
    
    captcha_text = ''.join(c for c in captcha_text if c.isalnum())
    
    return captcha_text.upper()

def solve_captcha(image_path: str) -> str:
    """
    Solve CAPTCHA using configured AI provider.
    
    Supports:
    - Local Ollama (default)
    - 9router proxy API
    
    Configuration via environment variables:
    - AI_PROVIDER: "ollama" (default) or "9router"
    - OLLAMA_URL: Ollama server URL (for ollama provider)
    - NINEROUTER_API_KEY: API key (for 9router provider)
    """
    ai_provider = os.getenv("AI_PROVIDER", "ollama").lower()
    
    if ai_provider == "9router":
        api_key = os.getenv("NINEROUTER_API_KEY")
        if not api_key:
            raise ValueError("NINEROUTER_API_KEY environment variable is required for 9router provider")
        return solve_captcha_9router(image_path, api_key)
    else:
        ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        return solve_captcha_ollama(image_path, ollama_url)
