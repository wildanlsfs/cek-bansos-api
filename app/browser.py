import json
import logging
import os
import re

logger = logging.getLogger(__name__)


def _make_llm():
    from browser_use.llm.openai.like import ChatOpenAILike
    from browser_use.llm.openai.chat import ChatOpenAI

    provider = os.getenv("AI_PROVIDER", "ollama").lower()

    if provider == "9router":
        api_key = os.getenv("NINEROUTER_API_KEY", "nokey")
        base_url = os.getenv("NINEROUTER_URL", "https://api.9router.com").rstrip("/")
        model = os.getenv("NINEROUTER_MODEL", "gemma4:e2b")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        return ChatOpenAILike(model=model, api_key=api_key, base_url=base_url)
    else:
        api_key = "ollama"
        base_url = os.getenv("OLLAMA_URL", "http://ollama:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        return ChatOpenAILike(model=model, api_key=api_key, base_url=base_url)


TASK_TEMPLATE = """
Go to https://cekbansos.kemensos.go.id/ and check bansos status for NIK: {nik}

Steps:
1. Navigate to https://cekbansos.kemensos.go.id/
2. Fill in the NIK input field with: {nik}
3. Look at the captcha image on the page and read the characters carefully
4. Type the captcha text into the captcha input field
5. Click the search/submit button
6. Wait for results to appear
7. If the captcha is wrong, reload the page and retry from step 2

When done, extract data and output ONLY valid JSON — no explanation, no markdown:
- If data found: {{"status":"success","nama":"[name]","desil":"[decile]","sembako_status":"[status]","sembako_periode":"[period]","pkh_status":"[status]","pkh_periode":"[period]","pbijk_status":"[status]","pbijk_periode":"[period]","status_kpd":"[status]"}}
- If not found: {{"status":"not_found"}}
- If captcha keeps failing: {{"status":"captcha_failed"}}
"""


async def _run_agent(nik: str) -> dict:
    from browser_use import Agent
    from browser_use.browser import BrowserSession

    llm = _make_llm()
    session = BrowserSession(headless=True, disable_security=True)
    task = TASK_TEMPLATE.format(nik=nik)

    agent = Agent(
        task=task,
        llm=llm,
        browser_session=session,
        use_vision=True,
        max_failures=3,
    )

    history = await agent.run(max_steps=20)

    raw = history.final_result()
    if not raw:
        raise Exception("Agent completed but returned no result")

    match = re.search(r'\{.*\}', raw, re.S)
    if not match:
        raise Exception(f"No JSON found in agent result: {raw[:200]}")

    return json.loads(match.group())


async def check_nik_bansos(nik: str) -> dict:
    if not nik.isdigit() or len(nik) != 16:
        raise ValueError("NIK must be exactly 16 digits")

    raw = await _run_agent(nik)
    status = raw.get("status", "success")

    if status == "not_found":
        return {
            "status": "not_found",
            "nik": nik,
            "data": {},
            "message": "NIK tidak ditemukan pada data penerima manfaat bansos",
        }

    if status == "captcha_failed":
        raise Exception("CAPTCHA solving failed after maximum attempts")

    data = {k: v for k, v in raw.items() if k != "status"}
    return {"status": "success", "nik": nik, "data": data}
