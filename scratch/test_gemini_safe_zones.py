import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def test_gemini():
    client = genai.Client(api_key=api_key)
    lat = 28.6139
    lng = 77.2090
    
    prompt = f"""
    You are an emergency response AI. A user is at latitude {lat}, longitude {lng}.
    Return a JSON array of the 3 closest REAL police stations, major hospitals, or safe zones near this location.
    Make sure to provide their approximate latitude and longitude coordinates.
    Format exactly as a valid JSON array:
    [
      {{
        "location_name": "Name of Police Station/Hospital",
        "description": "Brief description (e.g. 24/7 Police Station)",
        "latitude": 28.6140,
        "longitude": 77.2080
      }}
    ]
    Return ONLY the JSON array, no markdown formatting or backticks.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    print(response.text)

if __name__ == "__main__":
    test_gemini()
