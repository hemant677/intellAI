import requests, json

print("=== Test 1: Delhi (28.6139, 77.2090) ===")
r = requests.get("http://127.0.0.1:5000/get-nearby-safe-zones?lat=28.6139&lng=77.2090")
d = r.json()
for i, z in enumerate(d["safe_zones"]):
    print(f"  {i+1}. {z['location_name']} - {z['description']}")
    print(f"     Coords: ({z['latitude']}, {z['longitude']})")

print()
print("=== Test 2: Indore (22.7196, 75.8577) ===")
r2 = requests.get("http://127.0.0.1:5000/get-nearby-safe-zones?lat=22.7196&lng=75.8577")
d2 = r2.json()
for i, z in enumerate(d2["safe_zones"]):
    print(f"  {i+1}. {z['location_name']} - {z['description']}")
    print(f"     Coords: ({z['latitude']}, {z['longitude']})")

print()
print("=== Test 3: Bangalore (12.9716, 77.5946) ===")
r3 = requests.get("http://127.0.0.1:5000/get-nearby-safe-zones?lat=12.9716&lng=77.5946")
d3 = r3.json()
for i, z in enumerate(d3["safe_zones"]):
    print(f"  {i+1}. {z['location_name']} - {z['description']}")
    print(f"     Coords: ({z['latitude']}, {z['longitude']})")
