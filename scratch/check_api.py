import os
import requests
from dotenv import load_dotenv

# Load from .env
load_dotenv()

google_maps_key = os.environ.get("GOOGLE_MAPS_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY")

print(f"DEBUG: GOOGLE_MAPS_API_KEY = {google_maps_key}")
print(f"DEBUG: GEMINI_API_KEY = {gemini_key}")

if not gemini_key or gemini_key == "YOUR_GEMINI_API_KEY_HERE":
    print("Gemini API key is NOT configured in .env.")
else:
    # Test Gemini Key
    print("Testing Gemini API key...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": "Say hello!"}]}]
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print("SUCCESS: Gemini API key is VALID!")
        else:
            print(f"FAILED: Gemini API key validation failed (Status: {response.status_code}). Response: {response.text}")
    except Exception as e:
        print(f"ERROR: Could not connect to Gemini API: {e}")
