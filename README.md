# SafeRoute AI - AI-Powered Women's Safety Path Advisor

SafeRoute AI is an interactive, premium web application designed to empower women and commuters with real-time safety insights, road-snapped safe path routing, community-verified hazard feeds, and AI-driven safety recommendations for cities across India.

---

## ✨ Features

- 🗺️ **Interactive Leaflet & OpenStreetMap Canvas**: Fully custom tile map rendering with seamless Dark and Light theme integration (no billing constraints or API activation locks).
- 🚗 **OSRM Road-Snapped Routing**: Computes travel routes snapped strictly to real roads and highways (provides both a primary path and a safer alternative path).
- 📍 **Nominatim Reverse Geocoding**: Select start and destination locations directly by clicking coordinates on the map to auto-resolve human-readable address names.
- 🤖 **AI safety Advisor (Gemini 2.5 Flash Lite)**: Analyzes safety index ratings, nearby crime/hazard feeds, and dynamically compiles structured warnings and safety recommendations.
- 🚨 **Live Safety Dashboard & Incident Feed**: Displays stats for active safety alerts, verified safe stations, and high-risk zones. Includes a community report verification system.
- 🔊 **Emergency SOS & Siren Synthesizer**: Web Audio API oscillator synthesis generating high-intensity emergency sirens and emergency alert options directly in-browser.

---

## 🛠️ Technology Stack

- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism & Neon theme system), JavaScript (ES6+).
- **Map & Geocoding**: Leaflet JS, OpenStreetMap CartoDB Tiles, OSRM Routing Engine API, Nominatim Geocoding API.
- **Backend**: Flask (Python 3.x), `google-genai` SDK.
- **AI Models**: Gemini 2.5 Flash Lite.

---

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/hemant677/intellAI.git
cd intellAI
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
```

### 3. Install Dependencies
Ensure you have Python 3 installed. Install backend packages using pip:
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` does not exist, install manually: `pip install flask python-dotenv google-genai requests`)*

### 4. Run the Application
Start the Flask development server:
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 👥 Contributing
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License
This project is open-source under the MIT License.
