import os
import json
import math
from datetime import datetime
import requests
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

app = Flask(__name__)

# In-memory database of incidents
# Initialized with 20 realistic incidents/safe-zones around Indore
incidents = [
    {
        "id": 1,
        "location_name": "Vijay Nagar near C21 Mall",
        "incident_type": "Harassment",
        "description": "Catcalling and group loitering reported after 9 PM near the back alley.",
        "risk_level": "High",
        "latitude": 22.7533,
        "longitude": 75.8937,
        "time": "09:30 PM",
        "reports_count": 14,
        "verification_count": 8
    },
    {
        "id": 2,
        "location_name": "Palasia Square Behind Petrol Pump",
        "incident_type": "Poor Lighting",
        "description": "Entire stretch of the back lane has non-functional streetlights.",
        "risk_level": "Medium",
        "latitude": 22.7244,
        "longitude": 75.8839,
        "time": "10:45 PM",
        "reports_count": 8,
        "verification_count": 4
    },
    {
        "id": 3,
        "location_name": "Bhawarkua Girls Hostel Lane",
        "incident_type": "Suspicious Activity",
        "description": "Unidentified bikers riding repeatedly and stalling near hostellers' entry gate.",
        "risk_level": "Medium",
        "latitude": 22.6986,
        "longitude": 75.8654,
        "time": "08:15 PM",
        "reports_count": 12,
        "verification_count": 6
    },
    {
        "id": 4,
        "location_name": "Rajendra Nagar Railway Station Road",
        "incident_type": "Isolated Area",
        "description": "Very dark and desolate stretch, no commercial activity or security patrol after 8 PM.",
        "risk_level": "High",
        "latitude": 22.6732,
        "longitude": 75.8290,
        "time": "11:00 PM",
        "reports_count": 19,
        "verification_count": 11
    },
    {
        "id": 5,
        "location_name": "AITR Campus Main Gate Security",
        "incident_type": "Safe Zone",
        "description": "24/7 Security post, active CCTV monitoring, and emergency SOS call station.",
        "risk_level": "Safe Zone",
        "latitude": 22.8224,
        "longitude": 75.9378,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 6,
        "location_name": "Vijay Nagar Police Station Hub",
        "incident_type": "Safe Zone",
        "description": "Active police station with standard night patrolling vehicles starting here.",
        "risk_level": "Safe Zone",
        "latitude": 22.7540,
        "longitude": 75.8910,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 7,
        "location_name": "Bengali Square Bypass Link",
        "incident_type": "Poor Lighting",
        "description": "Construction work has blocked streetlights, creating deep dark zones.",
        "risk_level": "Medium",
        "latitude": 22.7231,
        "longitude": 75.9129,
        "time": "11:15 PM",
        "reports_count": 7,
        "verification_count": 3
    },
    {
        "id": 8,
        "location_name": "LIG Square Subway Exit",
        "incident_type": "Suspicious Activity",
        "description": "Groups gather near the subway staircase drinking in the dark.",
        "risk_level": "High",
        "latitude": 22.7397,
        "longitude": 75.8885,
        "time": "10:00 PM",
        "reports_count": 15,
        "verification_count": 9
    },
    {
        "id": 9,
        "location_name": "Khajrana Temple Ring Road Side",
        "incident_type": "Isolated Area",
        "description": "Dark empty plots near the side entrance, no streetlights present.",
        "risk_level": "Medium",
        "latitude": 22.7305,
        "longitude": 75.9048,
        "time": "09:00 PM",
        "reports_count": 9,
        "verification_count": 5
    },
    {
        "id": 10,
        "location_name": "Geeta Bhawan Square Bus Stop",
        "incident_type": "Unsafe Road",
        "description": "Uneven road and heavy construction with no safety barricades or illumination.",
        "risk_level": "Medium",
        "latitude": 22.7177,
        "longitude": 75.8800,
        "time": "08:30 PM",
        "reports_count": 5,
        "verification_count": 2
    },
    {
        "id": 11,
        "location_name": "Annapurna Temple Road Plaza",
        "incident_type": "Safe Zone",
        "description": "Well-lit public square with high footfall, CCTV, and regular security patrolling.",
        "risk_level": "Safe Zone",
        "latitude": 22.7011,
        "longitude": 75.8360,
        "time": "06:00 AM - 10:00 PM",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 12,
        "location_name": "Rajwada Palace Security Booth",
        "incident_type": "Safe Zone",
        "description": "Police outpost with active staff stationed in the central commercial market.",
        "risk_level": "Safe Zone",
        "latitude": 22.7196,
        "longitude": 75.8577,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 13,
        "location_name": "MR 10 Road near Flyover",
        "incident_type": "Poor Lighting",
        "description": "Flyover lower deck has zero lights. Highly dark lane for pedestrians.",
        "risk_level": "Medium",
        "latitude": 22.7660,
        "longitude": 75.8890,
        "time": "10:30 PM",
        "reports_count": 6,
        "verification_count": 3
    },
    {
        "id": 14,
        "location_name": "Chappan Dukan Food Street",
        "incident_type": "Safe Zone",
        "description": "Brightly illuminated, high crowd density, and permanent police presence.",
        "risk_level": "Safe Zone",
        "latitude": 22.7247,
        "longitude": 75.8784,
        "time": "11:00 AM - 11:30 PM",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 15,
        "location_name": "Rau Bypass Junction",
        "incident_type": "Isolated Area",
        "description": "Deserted highway junction. Trucks parked along sides, poorly illuminated.",
        "risk_level": "High",
        "latitude": 22.6390,
        "longitude": 75.8080,
        "time": "11:45 PM",
        "reports_count": 18,
        "verification_count": 10
    },
    {
        "id": 16,
        "location_name": "Malhar Mall Backside Road",
        "incident_type": "Harassment",
        "description": "Teasing and speed-driving incidents reported repeatedly in the evening.",
        "risk_level": "High",
        "latitude": 22.7562,
        "longitude": 75.8964,
        "time": "08:45 PM",
        "reports_count": 16,
        "verification_count": 9
    },
    {
        "id": 17,
        "location_name": "Bhawarkua Police Station",
        "incident_type": "Safe Zone",
        "description": "Active local police station providing rapid emergency response.",
        "risk_level": "Safe Zone",
        "latitude": 22.6980,
        "longitude": 75.8640,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 18,
        "location_name": "Manorama Ganj Back Road",
        "incident_type": "Poor Lighting",
        "description": "Lush trees block out what few streetlights exist, making it extremely dark.",
        "risk_level": "Medium",
        "latitude": 22.7202,
        "longitude": 75.8891,
        "time": "09:15 PM",
        "reports_count": 5,
        "verification_count": 2
    },
    {
        "id": 19,
        "location_name": "Kesar Bagh Road near Garden",
        "incident_type": "Isolated Area",
        "description": "Long stretch of road with no open shops or houses directly facing it.",
        "risk_level": "Medium",
        "latitude": 22.6845,
        "longitude": 75.8450,
        "time": "10:15 PM",
        "reports_count": 11,
        "verification_count": 5
    },
    {
        "id": 20,
        "location_name": "Niranjanpur Crossing",
        "incident_type": "Unsafe Road",
        "description": "Damaged road with heavy traffic, lack of clear lane indicators or pedestrian crossings.",
        "risk_level": "Medium",
        "latitude": 22.7745,
        "longitude": 75.8970,
        "time": "09:30 PM",
        "reports_count": 8,
        "verification_count": 4
    },
    # --- Delhi ---
    {
        "id": 21,
        "location_name": "Kashmere Gate ISBT Underpass",
        "incident_type": "Isolated Area",
        "description": "Poorly lit underpass near bus terminal. Multiple reports of snatching and eve-teasing after dark.",
        "risk_level": "High",
        "latitude": 28.6667,
        "longitude": 77.2289,
        "time": "10:00 PM",
        "reports_count": 22,
        "verification_count": 14
    },
    {
        "id": 22,
        "location_name": "Connaught Place Inner Circle",
        "incident_type": "Safe Zone",
        "description": "Well-lit commercial hub with heavy police presence, CCTV coverage, and tourist police booths.",
        "risk_level": "Safe Zone",
        "latitude": 28.6315,
        "longitude": 77.2167,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 23,
        "location_name": "Sarojini Nagar Market Back Lane",
        "incident_type": "Harassment",
        "description": "Dense crowd areas with reports of groping and pickpocketing during evening rush.",
        "risk_level": "High",
        "latitude": 28.5745,
        "longitude": 77.2000,
        "time": "07:30 PM",
        "reports_count": 18,
        "verification_count": 10
    },
    {
        "id": 24,
        "location_name": "India Gate Rajpath",
        "incident_type": "Safe Zone",
        "description": "High-security zone with continuous police patrolling and floodlights. Safe for evening walks.",
        "risk_level": "Safe Zone",
        "latitude": 28.6129,
        "longitude": 77.2295,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    # --- Mumbai ---
    {
        "id": 25,
        "location_name": "Andheri Subway Walkway",
        "incident_type": "Poor Lighting",
        "description": "Subway connecting east and west Andheri is dimly lit with broken CCTV cameras.",
        "risk_level": "Medium",
        "latitude": 19.1197,
        "longitude": 72.8464,
        "time": "09:45 PM",
        "reports_count": 15,
        "verification_count": 8
    },
    {
        "id": 26,
        "location_name": "Marine Drive Promenade",
        "incident_type": "Safe Zone",
        "description": "Iconic seafront with bright lights, high footfall, and regular police presence till midnight.",
        "risk_level": "Safe Zone",
        "latitude": 18.9438,
        "longitude": 72.8232,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 27,
        "location_name": "Dharavi Cross Road Night Stretch",
        "incident_type": "Isolated Area",
        "description": "Narrow lanes with minimal lighting and no police visibility after 10 PM.",
        "risk_level": "High",
        "latitude": 19.0418,
        "longitude": 72.8558,
        "time": "10:30 PM",
        "reports_count": 20,
        "verification_count": 12
    },
    # --- Bangalore ---
    {
        "id": 28,
        "location_name": "Majestic Bus Stand Rear Exit",
        "incident_type": "Harassment",
        "description": "Crowded bus station with frequent reports of verbal harassment and stalking near back exits.",
        "risk_level": "High",
        "latitude": 12.9767,
        "longitude": 77.5713,
        "time": "09:00 PM",
        "reports_count": 17,
        "verification_count": 9
    },
    {
        "id": 29,
        "location_name": "MG Road & Brigade Road Junction",
        "incident_type": "Safe Zone",
        "description": "Premium commercial zone with heavy security, well-lit streets, and active CCTV monitoring.",
        "risk_level": "Safe Zone",
        "latitude": 12.9758,
        "longitude": 77.6068,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    # --- Kolkata ---
    {
        "id": 30,
        "location_name": "Park Street Late Night Zone",
        "incident_type": "Suspicious Activity",
        "description": "Reports of inebriated groups loitering near restaurant alleys after midnight.",
        "risk_level": "Medium",
        "latitude": 22.5521,
        "longitude": 88.3531,
        "time": "12:30 AM",
        "reports_count": 11,
        "verification_count": 6
    },
    {
        "id": 31,
        "location_name": "Victoria Memorial Garden",
        "incident_type": "Safe Zone",
        "description": "Heritage site with guards, well-maintained pathways, and tourist police presence.",
        "risk_level": "Safe Zone",
        "latitude": 22.5448,
        "longitude": 88.3426,
        "time": "06:00 AM - 06:00 PM",
        "reports_count": 0,
        "verification_count": 0
    },
    # --- Chennai ---
    {
        "id": 32,
        "location_name": "T. Nagar Ranganathan Street Side Alley",
        "incident_type": "Harassment",
        "description": "Overcrowded shopping street with reports of groping during peak hours.",
        "risk_level": "High",
        "latitude": 13.0410,
        "longitude": 80.2340,
        "time": "06:00 PM",
        "reports_count": 14,
        "verification_count": 7
    },
    {
        "id": 33,
        "location_name": "Marina Beach Promenade",
        "incident_type": "Safe Zone",
        "description": "Long beach promenade with police patrol booths and good lighting. Safe for morning/evening walks.",
        "risk_level": "Safe Zone",
        "latitude": 13.0500,
        "longitude": 80.2824,
        "time": "05:00 AM - 09:00 PM",
        "reports_count": 0,
        "verification_count": 0
    },
    # --- Pune ---
    {
        "id": 34,
        "location_name": "FC Road Student Zone",
        "incident_type": "Safe Zone",
        "description": "Vibrant college area with high foot traffic, well-lit cafes, and police chowki nearby.",
        "risk_level": "Safe Zone",
        "latitude": 18.5270,
        "longitude": 73.8410,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 35,
        "location_name": "Hadapsar IT Park Back Road",
        "incident_type": "Poor Lighting",
        "description": "Service road behind tech parks with non-functional streetlights and minimal traffic.",
        "risk_level": "Medium",
        "latitude": 18.5089,
        "longitude": 73.9260,
        "time": "10:00 PM",
        "reports_count": 9,
        "verification_count": 4
    },
    # --- Hyderabad ---
    {
        "id": 36,
        "location_name": "Charminar Old City Narrow Lanes",
        "incident_type": "Suspicious Activity",
        "description": "Winding narrow lanes with low visibility and reports of chain-snatching incidents.",
        "risk_level": "Medium",
        "latitude": 17.3616,
        "longitude": 78.4747,
        "time": "08:00 PM",
        "reports_count": 13,
        "verification_count": 7
    },
    {
        "id": 37,
        "location_name": "HITEC City Cyber Towers Hub",
        "incident_type": "Safe Zone",
        "description": "IT corridor with private security, bright LED streetlights, and 24/7 CCTV surveillance.",
        "risk_level": "Safe Zone",
        "latitude": 17.4435,
        "longitude": 78.3772,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    # --- Jaipur ---
    {
        "id": 38,
        "location_name": "Hawa Mahal Road Tourist Area",
        "incident_type": "Safe Zone",
        "description": "Major tourist corridor with tourist police, heritage guards, and active CCTV monitoring.",
        "risk_level": "Safe Zone",
        "latitude": 26.9239,
        "longitude": 75.8267,
        "time": "Always Open",
        "reports_count": 0,
        "verification_count": 0
    },
    {
        "id": 39,
        "location_name": "Mansarovar D-Block Inner Lane",
        "incident_type": "Poor Lighting",
        "description": "Residential back lanes with broken streetlights and stray dogs causing safety concerns.",
        "risk_level": "Medium",
        "latitude": 26.8662,
        "longitude": 75.7630,
        "time": "09:30 PM",
        "reports_count": 7,
        "verification_count": 3
    },
    # --- Ahmedabad ---
    {
        "id": 40,
        "location_name": "Sabarmati Riverfront Walk",
        "incident_type": "Safe Zone",
        "description": "Modern riverfront promenade with excellent lighting, CCTV, and security personnel.",
        "risk_level": "Safe Zone",
        "latitude": 23.0395,
        "longitude": 72.5802,
        "time": "06:00 AM - 10:00 PM",
        "reports_count": 0,
        "verification_count": 0
    }
]

# Base list of areas with center points for leaderboard calculations
areas_db = {
    # Indore
    "Vijay Nagar, Indore": {"lat": 22.7533, "lng": 75.8937},
    "Palasia, Indore": {"lat": 22.7244, "lng": 75.8839},
    "Rajwada, Indore": {"lat": 22.7196, "lng": 75.8577},
    "Rau Bypass, Indore": {"lat": 22.6390, "lng": 75.8080},
    # Delhi
    "Connaught Place, Delhi": {"lat": 28.6315, "lng": 77.2167},
    "Kashmere Gate, Delhi": {"lat": 28.6667, "lng": 77.2289},
    "Sarojini Nagar, Delhi": {"lat": 28.5745, "lng": 77.2000},
    # Mumbai
    "Marine Drive, Mumbai": {"lat": 18.9438, "lng": 72.8232},
    "Andheri, Mumbai": {"lat": 19.1197, "lng": 72.8464},
    # Bangalore
    "MG Road, Bangalore": {"lat": 12.9758, "lng": 77.6068},
    "Majestic, Bangalore": {"lat": 12.9767, "lng": 77.5713},
    # Kolkata
    "Park Street, Kolkata": {"lat": 22.5521, "lng": 88.3531},
    # Chennai
    "Marina Beach, Chennai": {"lat": 13.0500, "lng": 80.2824},
    "T. Nagar, Chennai": {"lat": 13.0410, "lng": 80.2340},
    # Pune
    "FC Road, Pune": {"lat": 18.5270, "lng": 73.8410},
    # Hyderabad
    "HITEC City, Hyderabad": {"lat": 17.4435, "lng": 78.3772},
    "Charminar, Hyderabad": {"lat": 17.3616, "lng": 78.4747},
    # Jaipur
    "Hawa Mahal, Jaipur": {"lat": 26.9239, "lng": 75.8267},
    # Ahmedabad
    "Sabarmati, Ahmedabad": {"lat": 23.0395, "lng": 72.5802}
}

ai_analyses_performed = 0

# Helper function to calculate distance using Haversine formula
def get_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# India-Wide Geocoding Helper using OpenStreetMap Nominatim API
def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "SafeRouteAI-SafetyNavigator/1.0"
    }
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "in"  # Limit queries specifically to India
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=6)
        if response.status_code == 200:
            res_json = response.json()
            if res_json:
                return float(res_json[0]["lat"]), float(res_json[0]["lon"])
    except Exception as e:
        print(f"OSM Nominatim Geocoding Error for '{address}': {e}")
    return None

# Helper to run Gemini requests
def call_gemini(prompt, system_instruction=None, custom_key=None):
    api_key = custom_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            res_json = response.json()
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        else:
            print(f"Gemini API returned error status {response.status_code}: {response.text}")
        return None
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

# Fallback AI Response Engine
def get_fallback_chat_reply(message):
    message_lower = message.lower()
    
    if "vijay nagar" in message_lower:
        return """### 📍 Vijay Nagar Safety Profile

Vijay Nagar is a major commercial hub in Indore. While it is generally bustling and well-lit during the evening, specific safety hazards have been reported:
- **C21 Mall back alley**: Reports of loitering and verbal harassment after 9:00 PM.
- **Malhar Mall backside**: High-risk zone for teasing and suspicious gatherings.

**Recommendations:**
- Prefer using the main A.B. Road corridor which has high footfall and active police presence.
- The **Vijay Nagar Police Station Hub** (Safe Zone) is located nearby at `(22.7540, 75.8910)`. Feel free to head there if you feel unsafe.
- Avoid desolated alleys behind major malls after 9:00 PM.
"""
    elif "rajendra nagar" in message_lower:
        return """### 📍 Rajendra Nagar Safety Profile

Rajendra Nagar contains residential zones but the area around the railway station and outer bypass can get isolated:
- **Railway Station Road**: Extremely dark stretch after 8:00 PM. High risk score due to lack of illumination.

**Recommendations:**
- If traveling to Rajendra Nagar, use the main road through Reti Mandi/Chanakya Puri rather than the railway station bypass link.
- Carry a flashlight and keep emergency contacts on speed dial.
"""
    elif "aitr" in message_lower or "acropolis" in message_lower:
        return """### 🏫 AITR (Acropolis Institute) Safety Profile

The AITR campus area is located near the Indore Bypass Road.
- **Main Campus Entrance**: Safe zone with 24/7 security guards and cameras.
- **Bypass Outer Stretch**: Highly isolated after college hours (past 6:00 PM).

**Recommendations:**
- Avoid waiting on the bypass road for public transport after dark. Use campus-approved transport or coordinate with peers.
- Head directly to the campus security hub if you observe suspicious activity.
"""
    elif "highest risk" in message_lower or "worst area" in message_lower or "unsafe" in message_lower or "high risk" in message_lower:
        return """### ⚠️ High Risk Areas Alert

Based on community reports, the following areas in Indore currently have the highest risk levels:
1. **Rajendra Nagar Railway Station Road** - High isolation, poor lighting.
2. **Rau Bypass Junction** - Highway traffic, low pedestrian lighting, isolated.
3. **Vijay Nagar (Malhar/C21 Backside)** - Harassment and loitering reports.
4. **LIG Square Subway Exit** - Anti-social gatherings in dark areas after 10 PM.

Please plan your travels to bypass these specific areas or travel with a companion.
"""
    elif "safe" in message_lower or "safest" in message_lower:
        return """### 🟢 Safe Zones & Patrolled Hubs

The safest locations in our Indore database include:
1. **Vijay Nagar Police Station Hub** - 24/7 active police presence.
2. **Chappan Dukan Food Street** - Extremely busy, well-lit, and CCTV monitored.
3. **Bhawarkua Police Station** - Close to major coaching institutes, high police patrolling.
4. **AITR Campus Security Hub** - Dedicated security post.
5. **Rajwada Palace Security Booth** - Central Indore police point.

If you feel unsafe, head to these coordinates or use the floating SOS button to alert emergency dispatchers.
"""
    else:
        return f"""### 🤖 SafeRoute AI Assistant

I am your real-time safety advisor. I can advise you on paths across any city in India! 

Since you asked: *"{message}"*
Currently, I am running in local-rules fallback mode because no active Gemini API key has been saved. 

**💡 Hackathon Settings Feature:**
To test live safety chat responses for **Delhi, Mumbai, Bangalore, or any other location in India**, please click the **⚙️ API Settings** gear button in the navigation header and save your personal Gemini API Key. It will instantly connect the live models!
"""

def get_fallback_route_analysis(start_name, dest_name, primary_risk_score, safety_level, nearby_incidents):
    summary = f"Route analysis from **{start_name}** to **{dest_name}** completed."
    
    if primary_risk_score > 60:
        risk_exp = f"This route has a high risk score of **{primary_risk_score}%**. It passes through or near areas with reported incidents, including:"
        for inc in nearby_incidents[:2]:
            risk_exp += f"\n- **{inc['location_name']}**: {inc['incident_type']} ({inc['description']})"
        rec = "We strongly recommend taking the **Alternative Safe Route** (highlighted in Green), which bypasses these zones and has a lower risk score. Avoid walking alone along dark stretches."
        time_tip = "Best travel time: **6:00 AM to 7:30 PM**. Avoid travel after 9:00 PM unless absolutely necessary."
        avoid = f"Avoid the back lanes near {[inc['location_name'] for inc in nearby_incidents][:2]}."
    elif primary_risk_score > 30:
        risk_exp = f"This route has a moderate risk score of **{primary_risk_score}%**. While generally traversable, it contains some points of caution."
        for inc in nearby_incidents[:1]:
            risk_exp += f"\n- **{inc['location_name']}**: {inc['incident_type']} ({inc['description']})"
        rec = "Stay on the main transit roads. Keep your live location shared with a trusted contact."
        time_tip = "Best travel time: **6:00 AM to 9:30 PM**."
        avoid = "Avoid dark shortcuts or alleys."
    else:
        risk_exp = f"This route is highly safe, scoring only **{primary_risk_score}%**. It remains close to active safe zones and has high public visibility."
        rec = "Standard travel safety precautions apply. The route is well-patrolled."
        time_tip = "Best travel time: **Anytime** (24/7 visibility on main roads)."
        avoid = "No major warning zones detected."
        
    markdown_content = f"""### 🛡️ SafeRoute AI Route Analysis

#### 1. Route Summary
{summary}

#### 2. Risk Explanation
{risk_exp}

#### 3. Safety Recommendations
{rec}

#### 4. Best Travel Time
{time_tip}

#### 5. Areas to Avoid
{avoid}

---
*Note: Currently running in local-rules fallback mode. Save a Gemini API Key in the navbar settings to enable real-time geospatial safety analysis all over India.*
"""
    return markdown_content


@app.route('/')
def index():
    google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    return render_template('index.html', google_maps_api_key=google_maps_api_key)


@app.route('/get-incidents', methods=['GET'])
def get_incidents():
    return jsonify({"incidents": incidents})


@app.route('/report', methods=['POST'])
def report_incident():
    global incidents
    data = request.json or {}
    
    location_name = data.get('location_name', 'Unknown Location').strip()
    incident_type = data.get('incident_type', 'Suspicious Activity')
    description = data.get('description', '').strip()
    
    try:
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid coordinates"}), 400
        
    if not location_name or not description:
        return jsonify({"success": False, "error": "Location name and description are required"}), 400

    # Determine risk level based on incident type
    if incident_type == 'Harassment':
        risk_level = 'High'
    elif incident_type in ['Poor Lighting', 'Isolated Area', 'Suspicious Activity', 'Unsafe Road']:
        risk_level = 'Medium'
    elif incident_type == 'Safe Zone':
        risk_level = 'Safe Zone'
    else:
        risk_level = 'Medium'

    new_incident = {
        "id": len(incidents) + 1,
        "location_name": location_name,
        "incident_type": incident_type,
        "description": description,
        "risk_level": risk_level,
        "latitude": latitude,
        "longitude": longitude,
        "time": datetime.now().strftime("%I:%M %p"),
        "reports_count": 1,
        "verification_count": 1
    }
    
    incidents.append(new_incident)
    return jsonify({"success": True, "incident": new_incident})


@app.route('/get-leaderboard', methods=['GET'])
def get_leaderboard():
    # Calculate scores dynamically for areas
    scores = []
    for name, coords in areas_db.items():
        base_score = 100
        # Check nearby incidents to adjust score
        for inc in incidents:
            dist = get_distance_km(coords['lat'], coords['lng'], inc['latitude'], inc['longitude'])
            if dist <= 2.0:
                if inc['risk_level'] == 'High':
                    base_score -= 22
                elif inc['risk_level'] == 'Medium':
                    base_score -= 12
                elif inc['risk_level'] == 'Safe Zone':
                    base_score += 15
        
        # Clamp score between 10 and 100
        base_score = max(10, min(100, base_score))
        scores.append({"name": name, "score": int(base_score), "coords": coords})
        
    # Sort areas
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    
    safest = sorted_scores[:5]
    # For riskiest, reverse and take top 5
    riskiest = sorted(scores, key=lambda x: x['score'])[:5]
    
    return jsonify({
        "safest": safest,
        "riskiest": riskiest
    })


def fetch_osrm_route(start_lat, start_lng, dest_lat, dest_lng):
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{dest_lng},{dest_lat}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "alternatives": "true"
    }
    headers = {
        "User-Agent": "SafeRouteAI-SafetyNavigator/1.0"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=8)
        if response.status_code == 200:
            res_json = response.json()
            routes = res_json.get("routes", [])
            if routes:
                prim_coords_lng_lat = routes[0].get("geometry", {}).get("coordinates", [])
                primary_route = [[pt[1], pt[0]] for pt in prim_coords_lng_lat]
                
                alternative_route = []
                if len(routes) > 1:
                    alt_coords_lng_lat = routes[1].get("geometry", {}).get("coordinates", [])
                    alternative_route = [[pt[1], pt[0]] for pt in alt_coords_lng_lat]
                
                return primary_route, alternative_route
    except Exception as e:
        print(f"OSRM Routing Error: {e}")
    return None, None


@app.route('/analyze-route', methods=['POST'])
def analyze_route():
    global ai_analyses_performed
    data = request.json or {}
    
    start_input = data.get('start', '').strip()
    dest_input = data.get('destination', '').strip()
    custom_key = data.get('api_key', '').strip() or None
    
    start_lat = data.get('start_lat')
    start_lng = data.get('start_lng')
    dest_lat = data.get('dest_lat')
    dest_lng = data.get('dest_lng')
    
    # 1. Resolve Start Coordinates (Database lookup -> OSM Geocoding -> Indore Center Fallback)
    if start_lat is None or start_lng is None:
        start_lower = start_input.lower()
        resolved = False
        for name, coords in areas_db.items():
            if name.lower() in start_lower or start_lower in name.lower():
                start_lat, start_lng = coords['lat'], coords['lng']
                resolved = True
                break
        if not resolved:
            coords = geocode_address(start_input)
            if coords:
                start_lat, start_lng = coords
            else:
                # Default to Indore Center
                start_lat, start_lng = 22.7196, 75.8577
            
    # 2. Resolve Destination Coordinates
    if dest_lat is None or dest_lng is None:
        dest_lower = dest_input.lower()
        resolved = False
        for name, coords in areas_db.items():
            if name.lower() in dest_lower or dest_lower in name.lower():
                dest_lat, dest_lng = coords['lat'], coords['lng']
                resolved = True
                break
        if not resolved:
            coords = geocode_address(dest_input)
            if coords:
                dest_lat, dest_lng = coords
            else:
                # Default to Vijay Nagar
                dest_lat, dest_lng = 22.7533, 75.8937

    primary_route = []
    alternative_route = []
    
    # Try OSRM Road Routing
    prim_road, alt_road = fetch_osrm_route(start_lat, start_lng, dest_lat, dest_lng)
    if prim_road:
        primary_route = prim_road
        if alt_road:
            alternative_route = alt_road
        else:
            # Shift primary road path slightly to create a road-following detour alternative
            alternative_route = [[pt[0] + 0.005, pt[1] + 0.005] for pt in primary_route]
    else:
        # Fallback to straight line interpolation
        steps = 8
        for i in range(steps):
            t = i / (steps - 1)
            lat = start_lat + t * (dest_lat - start_lat)
            lng = start_lng + t * (dest_lng - start_lng)
            primary_route.append([lat, lng])
            
        # Fallback to bezier curve detour
        mid_lat = (start_lat + dest_lat) / 2
        mid_lng = (start_lng + dest_lng) / 2
        d_lat = dest_lat - start_lat
        d_lng = dest_lng - start_lng
        perp_lat = -d_lng * 0.35
        perp_lng = d_lat * 0.35
        mid_detour_lat = mid_lat + perp_lat
        mid_detour_lng = mid_lng + perp_lng
        
        alt_steps = 9
        for i in range(alt_steps):
            t = i / (alt_steps - 1)
            lat = (1-t)**2 * start_lat + 2*(1-t)*t * mid_detour_lat + t**2 * dest_lat
            lng = (1-t)**2 * start_lng + 2*(1-t)*t * mid_detour_lng + t**2 * dest_lng
            alternative_route.append([lat, lng])
            
    # Calculate primary risk score based on proximity to incidents (using a sample of coordinates to avoid heavy calculations)
    risk_points = 0
    nearby_incidents = []
    
    sample_interval = max(1, len(primary_route) // 10)
    for i in range(0, len(primary_route), sample_interval):
        pt = primary_route[i]
        for inc in incidents:
            dist = get_distance_km(pt[0], pt[1], inc['latitude'], inc['longitude'])
            if dist <= 2.5:
                if inc not in nearby_incidents:
                    nearby_incidents.append(inc)
                if inc['risk_level'] == 'High':
                    risk_points += 20
                elif inc['risk_level'] == 'Medium':
                    risk_points += 10
                elif inc['risk_level'] == 'Safe Zone':
                    risk_points -= 8
                    
    primary_risk_score = max(5, min(95, int(20 + risk_points)))
    
    if primary_risk_score <= 30:
        safety_level = "Safe"
    elif primary_risk_score <= 60:
        safety_level = "Moderate"
    else:
        safety_level = "High Risk"
        
    # Calculate alternative risk score
    alt_risk_points = 0
    alt_sample_interval = max(1, len(alternative_route) // 10)
    for i in range(0, len(alternative_route), alt_sample_interval):
        pt = alternative_route[i]
        for inc in incidents:
            dist = get_distance_km(pt[0], pt[1], inc['latitude'], inc['longitude'])
            if dist <= 2.5:
                if inc['risk_level'] == 'High':
                    alt_risk_points += 8
                elif inc['risk_level'] == 'Medium':
                    alt_risk_points += 4
                elif inc['risk_level'] == 'Safe Zone':
                    alt_risk_points -= 12
                    
    alternative_risk_score = max(5, min(primary_risk_score - 10, int(15 + alt_risk_points)))
    
    start_name = start_input if start_input else f"({start_lat:.4f}, {start_lng:.4f})"
    dest_name = dest_input if dest_input else f"({dest_lat:.4f}, {dest_lng:.4f})"
    
    incidents_text = ""
    for idx, inc in enumerate(nearby_incidents[:4]):
        incidents_text += f"- {inc['location_name']}: {inc['incident_type']} ({inc['risk_level']} risk) - Description: {inc['description']}\n"
        
    if not incidents_text:
        # Prompt LLM to evaluate based on general safety data if no incidents exist in DB
        incidents_text = "- No local community hazard reports logged in this area. Please evaluate the route using your own geographic safety training data for this part of India."

    gemini_prompt = f"""
    Analyze this travel route in India for women's safety:
    Start Point: {start_name} (Coordinates: {start_lat:.4f}, {start_lng:.4f})
    Destination: {dest_name} (Coordinates: {dest_lat:.4f}, {dest_lng:.4f})
    Primary Route Risk Score: {primary_risk_score}% ({safety_level})
    Alternative Route Risk Score: {alternative_risk_score}% (Recommended Safe Route)
    
    Local reported hazards (if any):
    {incidents_text}
    
    Generate a detailed response in markdown with:
    1. Route Summary: Overview of the primary route.
    2. Risk Explanation: Explaining the hazards, if any, and the risk score. Include details about neighborhoods, crowd density, and safety profiles if this is outside Indore, using your global safety knowledge of India.
    3. Safety Recommendations: Precautions to take.
    4. Best Travel Time: Safe hours.
    5. Areas to Avoid: Specific spots.
    Keep the advice practical, empathetic, and direct. Keep response formatting clean and readable.
    """
    
    system_instruction = "You are SafeRoute AI, a specialized safety routing system for women traveling in India. Provide structured, actionable, and encouraging safety insights using local community data or your geographic safety model."
    
    ai_response = call_gemini(gemini_prompt, system_instruction, custom_key)
    
    if not ai_response:
        ai_response = get_fallback_route_analysis(start_name, dest_name, primary_risk_score, safety_level, nearby_incidents)
        
    ai_analyses_performed += 1
    
    return jsonify({
        "start_coords": [start_lat, start_lng],
        "dest_coords": [dest_lat, dest_lng],
        "primary_route": primary_route,
        "alternative_route": alternative_route,
        "primary_risk_score": primary_risk_score,
        "alternative_risk_score": alternative_risk_score,
        "estimated_safety_level": safety_level,
        "ai_analysis": ai_response,
        "nearby_incidents": [{
            "location_name": inc["location_name"],
            "incident_type": inc["incident_type"],
            "risk_level": inc["risk_level"],
            "latitude": inc["latitude"],
            "longitude": inc["longitude"]
        } for inc in nearby_incidents[:5]]
    })


@app.route('/chat', methods=['POST'])
def chat():
    global ai_analyses_performed
    data = request.json or {}
    message = data.get('message', '').strip()
    custom_key = data.get('api_key', '').strip() or None
    
    if not message:
        return jsonify({"reply": "Please ask a valid safety question."})
        
    # Inject active incident context to the chatbot
    context_incidents = ""
    for idx, inc in enumerate(incidents):
        context_incidents += f"- {inc['location_name']}: {inc['incident_type']} ({inc['risk_level']} risk). '{inc['description']}'. Coords: {inc['latitude']},{inc['longitude']}\n"
        
    system_instruction = f"""You are SafeRoute AI, an advanced safety chatbot assisting women in navigating India (including major metropolitan areas like Delhi, Mumbai, Bangalore, Pune, Kolkata, Indore, and others).
Your goal is to provide safety recommendations, location profiles, safe zone info, and tips based on real-time data or your geographic knowledge base of Indian cities.
Here is the active safety incident database for various Indian cities:
{context_incidents}

Answer the user's question directly, clearly, and supportively. Use markdown formatting. If the question asks about a specific area inside these cities, cross-reference it with the database. For any other location in India, use your training database of safety patterns to advise them. Suggest police booths/hubs if they are nearby.
"""
    
    ai_response = call_gemini(message, system_instruction, custom_key)
    if not ai_response:
        ai_response = get_fallback_chat_reply(message)
        
    ai_analyses_performed += 1
    
    return jsonify({
        "reply": ai_response,
        "analyses_count": ai_analyses_performed
    })


@app.route('/get-stats', methods=['GET'])
def get_stats():
    global ai_analyses_performed
    total_reports = len(incidents)
    high_risk_count = sum(1 for inc in incidents if inc['risk_level'] == 'High')
    safe_zones_count = sum(1 for inc in incidents if inc['risk_level'] == 'Safe Zone')
    medium_risk_count = sum(1 for inc in incidents if inc['risk_level'] == 'Medium')
    active_alerts = high_risk_count
    
    return jsonify({
        "total_reports": total_reports,
        "high_risk": high_risk_count,
        "safe_zones": safe_zones_count,
        "ai_analyses": ai_analyses_performed,
        "active_alerts": active_alerts
    })


@app.route('/reverse-geocode', methods=['GET'])
def reverse_geocode():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    if not lat or not lng:
        return jsonify({"error": "Latitude and longitude are required"}), 400
        
    url = "https://nominatim.openstreetmap.org/reverse"
    headers = {
        "User-Agent": "SafeRouteAI-SafetyNavigator/1.0"
    }
    params = {
        "lat": lat,
        "lon": lng,
        "format": "json"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=6)
        if response.status_code == 200:
            res_json = response.json()
            if res_json:
                address_name = res_json.get("display_name", f"{lat}, {lng}")
                parts = [p.strip() for p in address_name.split(',')]
                simplified_address = ", ".join(parts[:3]) if len(parts) > 3 else address_name
                return jsonify({"address": simplified_address})
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        
    return jsonify({"address": f"{lat}, {lng}"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
