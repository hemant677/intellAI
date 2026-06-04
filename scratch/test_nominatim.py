import requests

def test_nominatim():
    lat = 28.6139
    lng = 77.2090
    url = f"https://nominatim.openstreetmap.org/search?format=json&q=police&lat={lat}&lon={lng}&limit=3"
    headers = {"User-Agent": "SafeRouteAI-Hackathon"}
    resp = requests.get(url, headers=headers)
    print(resp.json())

if __name__ == "__main__":
    test_nominatim()
