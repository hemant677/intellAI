import requests
import urllib.parse

def test_overpass():
    lat = 28.6139
    lng = 77.2090
    query = f"""
    [out:json];
    node(around:5000,{lat},{lng})[amenity=police];
    out 3;
    """
    url = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
    resp = requests.get(url)
    data = resp.json()
    for el in data.get('elements', []):
        name = el.get('tags', {}).get('name', 'Police Station')
        print(f"{name} at {el['lat']}, {el['lon']}")

if __name__ == "__main__":
    test_overpass()
