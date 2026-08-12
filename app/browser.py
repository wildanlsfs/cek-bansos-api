import subprocess
import json
import time
import re
from pathlib import Path
from .captcha import solve_captcha

def run_browser_cmd(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        raise Exception(f"Browser command failed: {result.stderr}")
    
    return result.stdout.strip()

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
        run_browser_cmd(["browser-use", "open", "https://cekbansos.kemensos.go.id/"])
        time.sleep(2)
        
        while captcha_attempts < max_attempts:
            captcha_attempts += 1
            
            state_output = run_browser_cmd(["browser-use", "state"])
            
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
            
            if not all([nik_input_idx, captcha_input_idx, submit_btn_idx]):
                raise Exception(f"Could not find form elements. NIK: {nik_input_idx}, Captcha: {captcha_input_idx}, Submit: {submit_btn_idx}")
            
            captcha_path = "/tmp/captcha.png"
            run_browser_cmd(["browser-use", "screenshot", captcha_path])
            
            captcha_text = solve_captcha(captcha_path)
            
            if not captcha_text:
                continue
            
            run_browser_cmd(["browser-use", "input", nik_input_idx, nik])
            time.sleep(0.5)
            
            run_browser_cmd(["browser-use", "input", captcha_input_idx, captcha_text])
            time.sleep(0.5)
            
            run_browser_cmd(["browser-use", "click", submit_btn_idx])
            time.sleep(3)
            
            try:
                run_browser_cmd([
                    "browser-use", "wait", "selector", 
                    "#respon_text,#modal_full,.swal2-container",
                    "--timeout", "5000"
                ])
            except:
                pass
            
            html_content = run_browser_cmd([
                "browser-use", "get", "html", 
                "--selector", "#respon_text"
            ])
            
            if "tidak ditemukan" in html_content.lower() or "salah" in html_content.lower():
                if captcha_attempts < max_attempts:
                    run_browser_cmd(["browser-use", "open", "https://cekbansos.kemensos.go.id/"])
                    time.sleep(2)
                    continue
                else:
                    raise Exception("CAPTCHA solving failed after maximum attempts")
            
            if html_content and len(html_content) > 50:
                parsed_data = parse_result_html(html_content)
                return {
                    "status": "success",
                    "nik": nik,
                    "data": parsed_data
                }
        
        raise Exception("Failed to complete NIK check after maximum attempts")
    
    finally:
        try:
            run_browser_cmd(["browser-use", "close"])
        except:
            pass

def parse_result_html(html: str) -> dict:
    result = {
        "nama": extract_field(html, r"Nama\s*:?\s*([^<\n]+)"),
        "nik": extract_field(html, r"NIK\s*:?\s*([^<\n]+)"),
        "alamat": extract_field(html, r"Alamat\s*:?\s*([^<\n]+)"),
        "desa_kelurahan": extract_field(html, r"Desa[/\s]*Kelurahan\s*:?\s*([^<\n]+)"),
        "kecamatan": extract_field(html, r"Kecamatan\s*:?\s*([^<\n]+)"),
        "kabupaten_kota": extract_field(html, r"Kabupaten[/\s]*Kota\s*:?\s*([^<\n]+)"),
        "provinsi": extract_field(html, r"Provinsi\s*:?\s*([^<\n]+)"),
        "desil": extract_field(html, r"Desil\s*:?\s*([^<\n]+)"),
        "raw_html": html
    }
    
    return result

def extract_field(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        value = re.sub(r'<[^>]+>', '', value)
        return value
    return ""
