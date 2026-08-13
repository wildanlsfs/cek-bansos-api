import json
import logging
import os
import re

logger = logging.getLogger(__name__)


def _patch_markdown_strip():
    """Monkey-patch browser-use ChatOpenAI.ainvoke to strip markdown from model responses."""
    from browser_use.llm.openai import chat as _m

    _orig = _m.ChatOpenAI.ainvoke

    async def _patched(self, messages, output_format=None, **kwargs):
        if output_format is None:
            return await _orig(self, messages, output_format, **kwargs)

        _orig_validate = output_format.__dict__.get('model_validate_json')
        _cls_validate = output_format.model_validate_json

        @classmethod  # type: ignore[misc]
        def _strip_validate(cls, data, *args, **kw):
            if isinstance(data, str):
                s = data.strip()
                if s.startswith('`'):
                    s = re.sub(r'^`{1,3}(?:json)?\s*\n?', '', s)
                    s = re.sub(r'\n?`{1,3}\s*$', '', s)
                    data = s.strip()
            return _cls_validate.__func__(cls, data, *args, **kw)

        output_format.model_validate_json = _strip_validate
        try:
            return await _orig(self, messages, output_format, **kwargs)
        finally:
            if _orig_validate is not None:
                output_format.model_validate_json = _orig_validate
            else:
                del output_format.model_validate_json

    _m.ChatOpenAI.ainvoke = _patched


_patch_markdown_strip()


def _make_llm():
    from browser_use.llm.openai.like import ChatOpenAILike

    provider = os.getenv("AI_PROVIDER", "ollama").lower()

    if provider == "9router":
        api_key = os.getenv("NINEROUTER_API_KEY", "nokey")
        base_url = os.getenv("NINEROUTER_URL", "https://api.9router.com").rstrip("/")
        model = os.getenv("NINEROUTER_MODEL", "gemma4:e2b")
    else:
        api_key = "ollama"
        base_url = os.getenv("OLLAMA_URL", "http://ollama:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "gemma4:e2b")

    if not base_url.endswith("/v1"):
        base_url += "/v1"

    return ChatOpenAILike(
        model=model,
        api_key=api_key,
        base_url=base_url,
        add_schema_to_system_prompt=True,
        remove_min_items_from_schema=True,
        remove_defaults_from_schema=True,
    )


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

NO_MARKDOWN_INSTRUCTION = (
    "\nCRITICAL: Output ONLY raw JSON — never use markdown, code blocks, or backticks."
)


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
        max_failures=5,
        extend_system_message=NO_MARKDOWN_INSTRUCTION,
    )

    history = await agent.run(max_steps=25)

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
