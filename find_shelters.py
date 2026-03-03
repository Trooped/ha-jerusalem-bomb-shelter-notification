import csv
import math
import sys
import json

# Ensure HA sent the coordinates
if len(sys.argv) < 3:
    print(json.dumps({"error": "Missing coordinates"}))
    sys.exit(1)

try:
    CURRENT_LAT = float(sys.argv[1])
    CURRENT_LON = float(sys.argv[2])
except ValueError:
    print(json.dumps({"error": "Invalid coordinates"}))
    sys.exit(1)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

shelters = []
try:
    with open('/config/Records.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row['קואורדינטות ציר x'])
                lon = float(row['קורדינטות ציר y'])
                addr = row.get('כתובת', 'Unknown Address').strip()
                dist = haversine(CURRENT_LAT, CURRENT_LON, lat, lon)
                shelters.append({'address': addr, 'dist': dist, 'lat': lat, 'lon': lon})
            except (ValueError, KeyError):
                continue
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)

# Sort and get top 3
shelters.sort(key=lambda x: x['dist'])
top_3 = shelters[:3]

# Format as JSON
result = {"shelters": []}
for s in top_3:
    result["shelters"].append({
        "address": s['address'] if s['address'] else "Unnamed Shelter",
        "distance": int(s['dist'] * 1000),
        "url": f"https://www.google.com/maps/search/?api=1&query={s['lat']},{s['lon']}"
    })

print(json.dumps(result))