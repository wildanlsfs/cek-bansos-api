#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/user/Documents/Development/KOMINFO/cek-bansos-api')

os.environ['API_KEY'] = 'test-key'
os.environ['OLLAMA_URL'] = 'http://localhost:11434'

from app.browser import check_nik_bansos

try:
    print("Testing NIK: 1234567890123456")
    print("This will take 60-120 seconds...")
    result = check_nik_bansos("1234567890123456")
    print("\n✓ SUCCESS!")
    print(f"Status: {result['status']}")
    print(f"NIK: {result['nik']}")
    print(f"\nData:")
    for key, value in result['data'].items():
        if key != 'raw_html':
            print(f"  {key}: {value}")
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
