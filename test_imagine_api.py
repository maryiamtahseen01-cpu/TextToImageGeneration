# test_imagine_api.py
import requests
import json

API_KEY = "vk-XiIMH6B62j3u3l3RuBVmBT1NzDklqADHgtG2TZHcpCswBIL"
API_URL = "https://api.vyro.ai/v1/imagine/api/generations"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "prompt": "A beautiful sunset over mountains",
    "model": "pro",
    "style": "realistic",
    "width": 1024,
    "height": 1024,
    "steps": 25
}

try:
    print("Testing Imagine.art API...")
    response = requests.post(API_URL, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Image URL: {result.get('data', {}).get('url', 'No URL')}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")