import requests
import base64
import os

def solve_captcha_ollama(image_path: str, ollama_url: str, model: str) -> str:
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    payload = {
        "model": model,
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


def solve_captcha_9router(image_path: str, api_key: str, base_url: str, model: str) -> str:
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    payload = {
        "model": model,
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

    endpoint = base_url.rstrip("/") + "/v1/chat/completions"

    response = requests.post(
        endpoint,
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

    Environment variables:
      AI_PROVIDER          : "ollama" (default) or "9router"

      For ollama:
        OLLAMA_URL         : Ollama server URL (default: http://ollama:11434)
        OLLAMA_MODEL       : Model name (default: gemma4:e2b)

      For 9router:
        NINEROUTER_API_KEY : API key (required)
        NINEROUTER_URL     : Base URL (default: https://api.9router.com)
        NINEROUTER_MODEL   : Model name (default: gemma4:e2b)
    """
    ai_provider = os.getenv("AI_PROVIDER", "ollama").lower()

    if ai_provider == "9router":
        api_key = os.getenv("NINEROUTER_API_KEY")
        if not api_key:
            raise ValueError("NINEROUTER_API_KEY is required when AI_PROVIDER=9router")
        base_url = os.getenv("NINEROUTER_URL", "https://api.9router.com")
        model = os.getenv("NINEROUTER_MODEL", "gemma4:e2b")
        return solve_captcha_9router(image_path, api_key, base_url, model)
    else:
        ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        model = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
        return solve_captcha_ollama(image_path, ollama_url, model)
