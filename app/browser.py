import subprocess
import json
import time
import re
import base64
from pathlib import Path
from .captcha import solve_captcha

def run_browser_cmd(cmd: list[str], timeout: int = 30) -> str:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=_browser_env()
    )
    
    if result.returncode != 0:
        raise Exception(f"Browser command failed: {result.stderr}")
    
    return result.stdout.strip()


def _browser_env(dict=None):
    import os
    env = os.environ.copy()
    home = os.path.expanduser("~")
    if env.get("PATH"):
        env["PATH"] = f"{home}/.local/bin:{env['PATH']}"
    return env


def parse_state_elements(state_output: str) -> dict:
    nik_input_idx = None
    captcha_input_idx = None
    submit_btn_idx = None

    for line in state_output.split('\n'):
        line_lower = line.lower()
        if 'nik_input' in line_lower or 'cek_peserta_nik' in line_lower:
            match = re.search(r'\[(\d+)\]', line)
            if match:
                nik_input_idx = match.group(1)
        elif 'id=captcha' in line_lower and 'input' in line_lower:
            match = re.search(r'\[(\d+)\]', line)
            if match:
                captcha_input_idx = match.group(1)
        elif 'btnceknik' in line_lower or ('cari data' in line_lower and 'button' in line_lower):
            match = re.search(r'\[(\d+)\]', line)
            if match and submit_btn_idx is None:
                submit_btn_idx = match.group(1)

    return {
        "nik": nik_input_idx,
        "captcha": captcha_input_idx,
        "submit": submit_btn_idx,
    }


def capture_captcha(save_path: str) -> None:
    js = ("(function(){var img=document.querySelector('img[src*=captcha]');"
          "if(!img){return null;}var c=document.createElement('canvas');"
          "c.width=img.naturalWidth;c.height=img.naturalHeight;"
          "c.getContext('2d').drawImage(img,0,0);return c.toDataURL('image/png');})()")
    raw = run_browser_cmd(["browser-use", "eval", js], timeout=30)
    match = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", raw)
    if not match:
        raise Exception("Could not capture captcha image from page")
    data = base64.b64decode(match.group(1))
    with open(save_path, "wb") as f:
        f.write(data)

def check_nik_bansos(nik: str) -> dict:
    if not nik.isdigit() or len(nik) != 16:
        raise ValueError("NIK must be exactly 16 digits")
    
    captcha_attempts = 0
    max_attempts = 3
    
    try:
        run_browser_cmd(["browser-use", "close"])
    except:
        pass
    
    try:
        run_browser_cmd(["browser-use", "open", f"https://cekbansos.kemensos.go.id/?t={int(time.time()*1000)}"])
        time.sleep(2)
        
        while captcha_attempts < max_attempts:
            captcha_attempts += 1
            
            state_output = run_browser_cmd(["browser-use", "state"])
            elements = parse_state_elements(state_output)
            nik_input_idx = elements["nik"]
            captcha_input_idx = elements["captcha"]
            submit_btn_idx = elements["submit"]
            
            if not all([nik_input_idx, captcha_input_idx, submit_btn_idx]):
                for _ in range(2):
                    time.sleep(2)
                    state_output = run_browser_cmd(["browser-use", "state"])
                    elements = parse_state_elements(state_output)
                    nik_input_idx = elements["nik"]
                    captcha_input_idx = elements["captcha"]
                    submit_btn_idx = elements["submit"]
                    if all([nik_input_idx, captcha_input_idx, submit_btn_idx]):
                        break
                else:
                    raise Exception(f"Could not find form elements. NIK: {nik_input_idx}, Captcha: {captcha_input_idx}, Submit: {submit_btn_idx}")
            
            captcha_path = "/tmp/captcha.png"
            capture_captcha(captcha_path)
            
            captcha_text = solve_captcha(captcha_path)
            
            if not captcha_text:
                continue
            
            run_browser_cmd(["browser-use", "input", nik_input_idx, nik])
            time.sleep(0.5)
            
            run_browser_cmd(["browser-use", "input", captcha_input_idx, captcha_text])
            time.sleep(0.5)
            
            run_browser_cmd(["browser-use", "click", submit_btn_idx])
            time.sleep(5)

            page_html = run_browser_cmd([
                "browser-use", "get", "html"
            ])

            if "kode captcha salah" in page_html.lower():
                if captcha_attempts < max_attempts:
                    run_browser_cmd(["browser-use", "open", f"https://cekbansos.kemensos.go.id/?t={int(time.time()*1000)}"])
                    time.sleep(2)
                    continue
                else:
                    raise Exception("CAPTCHA solving failed after maximum attempts")

            if "tidak ditemukan" in page_html.lower():
                return {
                    "status": "not_found",
                    "nik": nik,
                    "data": parse_result_html(page_html),
                    "message": "NIK tidak ditemukan pada data penerima manfaat bansos"
                }

            parsed_data = parse_result_html(page_html)
            if parsed_data:
                return {
                    "status": "success",
                    "nik": nik,
                    "data": parsed_data
                }

            if captcha_attempts < max_attempts:
                continue

            raise Exception("Failed to complete NIK check after maximum attempts")
    
    finally:
        try:
            run_browser_cmd(["browser-use", "close"])
        except:
            pass

def parse_result_html(html: str) -> dict:
    result = {
        "nama": "",
        "desil": "",
        "sembako": {"status": "", "periode": ""},
        "pkh": {"status": "", "periode": ""},
        "pbijk": {"status": "", "periode": ""},
        "status_kpd": "",
        "raw_html": html
    }

    tbody_match = re.search(r"<tbody>(.*?)</tbody>", html, re.S)
    if not tbody_match:
        return {}

    cells = re.findall(r"<td[^>]*>(.*?)</td>", tbody_match.group(1), re.S)
    if not cells:
        return {}

    clean = []
    for cell in cells:
        value = re.sub(r"<[^>]+>", " ", cell)
        value = re.sub(r"\s+", " ", value).strip()
        clean.append(value)

    if len(clean) >= 2:
        result["nama"] = clean[0]
        result["desil"] = clean[1]

    if len(clean) >= 9:
        result["sembako"] = {"status": clean[2], "periode": clean[3]}
        result["pkh"] = {"status": clean[4], "periode": clean[5]}
        result["pbijk"] = {"status": clean[6], "periode": clean[7]}
        result["status_kpd"] = clean[8]

    return result
