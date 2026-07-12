#!/usr/bin/env python
"""Test if backend is running"""
import time
import requests

time.sleep(2)  # Wait for server to start

try:
    resp = requests.get('http://127.0.0.1:8000/status', timeout=5)
    print(f'Status Code: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'Backend is responding!')
        print(f'  - LLM Provider: {data.get("llm_provider")}')
        print(f'  - Indexed Chunks: {data.get("indexed_chunks")}')
    else:
        print(f'Response: {resp.text[:200]}')
except requests.exceptions.ConnectionError:
    print('ERROR: Backend not responding on http://127.0.0.1:8000')
except Exception as e:
    print(f'ERROR: {e}')
