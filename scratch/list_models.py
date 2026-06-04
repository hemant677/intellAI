import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

print(f"Testing API Key: {api_key}")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    response = requests.get(url, timeout=10)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        models = response.json().get('models', [])
        for m in models:
            print(f"Model: {m['name']} - Methods: {m['supportedGenerationMethods']}")
    else:
        print("Response:", response.text)
except Exception as e:
    print("Error:", e)
