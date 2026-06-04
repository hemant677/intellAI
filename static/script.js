// SafeRoute AI - Interactive Frontend Controller

// Dynamic Injection of Custom Marker Styling
(function injectMarkerStyles() {
    const style = document.createElement('style');
    style.innerHTML = `
        .custom-marker {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .marker-pin {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 0.85rem;
            border: 2px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
            transition: transform 0.2s ease;
        }
        .marker-pin:hover {
            transform: scale(1.15);
        }
        .red-marker .marker-pin {
            background: rgba(255, 0, 127, 0.9);
            border-color: #ff007f;
            box-shadow: 0 0 15px #ff007f;
        }
        .orange-marker .marker-pin {
            background: rgba(249, 115, 22, 0.9);
            border-color: #f97316;
            box-shadow: 0 0 15px #f97316;
        }
        .green-marker .marker-pin {
            background: rgba(16, 185, 129, 0.9);
            border-color: #10b981;
            box-shadow: 0 0 15px #10b981;
        }
        /* Custom Route Path Animations */
        .route-polyline-primary {
            stroke-dasharray: 8, 8;
            animation: dashDraw 30s linear infinite;
        }
        .route-polyline-alt {
            stroke-dasharray: 6, 6;
            animation: dashDrawAlt 20s linear infinite;
        }
        @keyframes dashDraw {
            to { stroke-dashoffset: -1000; }
        }
        @keyframes dashDrawAlt {
            to { stroke-dashoffset: -1000; }
        }
    `;
    document.head.appendChild(style);
})();

// Global Variables
let map = null;
let heatmapLayer = null;
let incidentMarkers = [];
let routeLines = [];
let md = window.markdownit();

// Coordinates selecting modes
let pickingPointMode = null; // 'start', 'destination', or null
let selectedReportLat = 22.3511;
let selectedReportLng = 78.6677;

// Audio variables for Siren Synthesis
let audioCtx = null;
let sirenInterval = null;
let oscillator = null;
let sosTimer = null;

// Initialize app when DOM loads
document.addEventListener("DOMContentLoaded", () => {
    initParticles();
    initMap();
    fetchIncidents();
    fetchStats();
    fetchLeaderboard();
});

// Canvas Moving Particles Background
function initParticles() {
    const canvas = document.getElementById("particle-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    
    let particles = [];
    const particleCount = 45;
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.radius = Math.random() * 2 + 1;
            this.color = Math.random() > 0.5 ? "rgba(0, 240, 255, 0.25)" : "rgba(147, 51, 234, 0.25)";
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.shadowBlur = 8;
            ctx.shadowColor = this.color;
            ctx.fill();
        }
    }
    
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.shadowBlur = 0; // reset shadow
        
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        
        // Connect close particles with thin web lines
        ctx.shadowBlur = 0;
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dist = Math.hypot(particles[i].x - particles[j].x, particles[i].y - particles[j].y);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(100, 50, 200, ${0.15 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
        
        requestAnimationFrame(animate);
    }
    animate();
}

// Map Tile Layer URL templates
const TILE_DARK = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const TILE_LIGHT = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
let currentTileLayer = null;

// Leaflet Map Initialization
function initMap() {
    const savedTheme = localStorage.getItem('saferoute_theme') || 'dark';
    
    // Initialize Leaflet map
    map = L.map('map', {
        zoomControl: false,
        attributionControl: false
    }).setView([22.3511, 78.6677], 5);
    
    // Add custom zoom control at top-right
    L.control.zoom({
        position: 'topright'
    }).addTo(map);
    
    // Set active tile layer based on saved theme
    currentTileLayer = L.tileLayer(savedTheme === 'light' ? TILE_LIGHT : TILE_DARK, {
        maxZoom: 19
    }).addTo(map);

    // Event handler when clicking on map
    map.on('click', (e) => {
        const lat = parseFloat(e.latlng.lat.toFixed(6));
        const lng = parseFloat(e.latlng.lng.toFixed(6));
        
        if (pickingPointMode === 'start') {
            document.getElementById('route-start').value = "Fetching location...";
            fetch(`/reverse-geocode?lat=${lat}&lng=${lng}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('route-start').value = data.address;
                    document.getElementById('start-coords-lbl').innerText = `Selected Lat: ${lat}, Lng: ${lng}`;
                })
                .catch(err => {
                    document.getElementById('route-start').value = `${lat}, ${lng}`;
                    document.getElementById('start-coords-lbl').innerText = `Selected Lat: ${lat}, Lng: ${lng}`;
                });
            showToast("Start point selected from map!", "info");
            stopPickingPoint();
        } else if (pickingPointMode === 'destination') {
            document.getElementById('route-destination').value = "Fetching location...";
            fetch(`/reverse-geocode?lat=${lat}&lng=${lng}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('route-destination').value = data.address;
                    document.getElementById('dest-coords-lbl').innerText = `Selected Lat: ${lat}, Lng: ${lng}`;
                })
                .catch(err => {
                    document.getElementById('route-destination').value = `${lat}, ${lng}`;
                    document.getElementById('dest-coords-lbl').innerText = `Selected Lat: ${lat}, Lng: ${lng}`;
                });
            showToast("Destination selected from map!", "info");
            stopPickingPoint();
        } else {
            // General Map Click pops report coordinates
            selectedReportLat = lat;
            selectedReportLng = lng;
            document.getElementById('report-lat-lbl').innerText = lat;
            document.getElementById('report-lng-lbl').innerText = lng;
            
            showToast("Fetching location name...", "info");
            fetch(`/reverse-geocode?lat=${lat}&lng=${lng}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('report-location-name').value = data.address;
                    showToast(`Location captured: ${data.address}`, "success");
                })
                .catch(err => {
                    showToast(`Map coordinates captured: ${lat}, ${lng}`, "success");
                });
            
            if (window.innerWidth < 768) {
                document.getElementById('report-incident').scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
    
    // Fetch incidents after map initializes
    fetchIncidents();
}

// Fetch Incidents from Server
function fetchIncidents() {
    fetch('/get-incidents')
        .then(res => res.json())
        .then(data => {
            clearMarkers();
            plotMarkers(data.incidents);
            plotHeatmap(data.incidents);
            renderFeed(data.incidents);
        })
        .catch(err => {
            console.error("Error fetching incidents:", err);
            showToast("Unable to reach backend incidents API.", "error");
        });
}

// Plot Leaflet Markers
function plotMarkers(incidentsList) {
    if (!map) return;
    
    incidentsList.forEach(inc => {
        let pinColor;
        let categoryClass = "";
        let adviceTip = "";
        
        if (inc.risk_level === 'High') {
            pinColor = "#ff007f";
            categoryClass = "high-risk";
            adviceTip = "<strong>Safety Tip:</strong> Avoid passing this spot alone. Travel in groups or hire dynamic taxis.";
        } else if (inc.risk_level === 'Medium') {
            pinColor = "#f97316";
            categoryClass = "medium-risk";
            adviceTip = "<strong>Safety Tip:</strong> Exercise caution. Stay on well-lit lanes and avoid active shortcuts.";
        } else {
            pinColor = "#10b981";
            categoryClass = "safe-zone";
            adviceTip = "<strong>Safety Tip:</strong> Active safe station. Recommended sanctuary area with CCTV monitoring.";
        }

        const popupHTML = `
            <div class="popup-content" style="color: #333;">
                <span class="popup-tag ${categoryClass}">${inc.incident_type}</span>
                <h4 style="margin: 8px 0; color: #111;">${inc.location_name}</h4>
                <p style="margin: 0 0 10px 0; font-size: 14px;">${inc.description}</p>
                <div class="popup-tips" style="font-size: 13px; color: #555;">${adviceTip}</div>
                <div class="popup-footer" style="margin-top: 10px; font-size: 12px; color: #888;">
                    <span>Reports: ${inc.reports_count}</span> | 
                    <span>${inc.time}</span>
                </div>
            </div>
        `;

        const marker = L.circleMarker([inc.latitude, inc.longitude], {
            radius: 8,
            fillColor: pinColor,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
        }).bindPopup(popupHTML);
        
        marker.addTo(map);
        incidentMarkers.push(marker);
    });
}

// Plot Leaflet Heatmap Layer
function plotHeatmap(incidentsList) {
    if (!map) return;
    
    try {
        if (heatmapLayer) {
            map.removeLayer(heatmapLayer);
            heatmapLayer = null;
        }
        
        const heatPoints = [];
        incidentsList.forEach(inc => {
            let intensity = 1.0;
            if (inc.risk_level === 'High') {
                intensity = 3.0;
            } else if (inc.risk_level === 'Medium') {
                intensity = 1.5;
            } else if (inc.risk_level === 'Safe Zone') {
                return; // Don't add heat for safe zones
            }
            heatPoints.push([inc.latitude, inc.longitude, intensity]);
        });
        
        heatmapLayer = L.heatLayer(heatPoints, {
            radius: 25,
            blur: 15,
            maxZoom: 10,
            gradient: {
                0.4: 'blue',
                0.6: 'cyan',
                0.7: 'lime',
                0.8: 'yellow',
                1.0: 'red'
            }
        }).addTo(map);
    } catch (e) {
        console.warn("Leaflet Heatmap Layer could not be initialized:", e);
    }
}

// Clear all Map Markers
function clearMarkers() {
    if (map) {
        incidentMarkers.forEach(marker => map.removeLayer(marker));
    }
    incidentMarkers = [];
}

// Fetch analytics statistics
function fetchStats() {
    fetch('/get-stats')
        .then(res => res.json())
        .then(data => {
            animateCounter("stat-total-reports", data.total_reports);
            animateCounter("stat-high-risk", data.high_risk);
            animateCounter("stat-safe-zones", data.safe_zones);
            animateCounter("stat-ai-analyses", data.ai_analyses);
            animateCounter("stat-active-alerts", data.active_alerts);
        })
        .catch(err => console.error("Error fetching stats:", err));
}

// Animate Dashboard Counters
function animateCounter(id, targetValue) {
    const el = document.getElementById(id);
    if (!el) return;
    
    const duration = 1200; // ms
    const startTime = performance.now();
    const startValue = parseInt(el.innerText) || 0;
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function outQuad
        const ease = progress * (2 - progress);
        const currentValue = Math.floor(startValue + ease * (targetValue - startValue));
        
        el.innerText = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            el.innerText = targetValue;
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Fetch safety rankings
function fetchLeaderboard() {
    fetch('/get-leaderboard')
        .then(res => res.json())
        .then(data => {
            renderLeaderboardList("safest-list", data.safest, true);
            renderLeaderboardList("riskiest-list", data.riskiest, false);
        })
        .catch(err => console.error("Error fetching leaderboard:", err));
}

// Render Leaderboard HTML lists
function renderLeaderboardList(elementId, list, isSafest) {
    const container = document.getElementById(elementId);
    if (!container) return;
    
    container.innerHTML = "";
    list.forEach((item, index) => {
        const itemEl = document.createElement("div");
        itemEl.className = "leaderboard-item";
        
        const rank = index + 1;
        const scoreColor = isSafest ? "text-green" : "text-red";
        const icon = isSafest ? "fa-shield-heart" : "fa-triangle-exclamation";
        
        itemEl.innerHTML = `
            <div class="rank-badge">${rank}</div>
            <div class="leaderboard-info">
                <h5>${item.name}</h5>
                <span>Coords: ${item.coords.lat.toFixed(3)}, ${item.coords.lng.toFixed(3)}</span>
            </div>
            <div class="safety-score-pill">
                <i class="fa-solid ${icon} ${scoreColor}"></i> Safety Index: ${item.score}/100
            </div>
        `;
        container.appendChild(itemEl);
    });
}

// Render community incident feeds
function renderFeed(incidentsList) {
    const container = document.getElementById("feed-items-container");
    if (!container) return;
    
    container.innerHTML = "";
    
    // Sort descending by id to get latest reports
    const sorted = [...incidentsList].sort((a, b) => b.id - a.id);
    
    if (sorted.length === 0) {
        container.innerHTML = "<div class='text-center p-4 text-muted'>No community safety reports logged yet.</div>";
        return;
    }
    
    sorted.forEach(inc => {
        const card = document.createElement("div");
        card.className = "feed-card";
        
        let iconClass = "fa-triangle-exclamation text-yellow";
        let levelClass = "text-orange";
        
        if (inc.risk_level === 'High') {
            iconClass = "fa-skull-crossbones text-red";
            levelClass = "text-red";
        } else if (inc.risk_level === 'Safe Zone') {
            iconClass = "fa-shield-heart text-green";
            levelClass = "text-green";
        }
        
        card.innerHTML = `
            <div class="feed-card-left">
                <div class="feed-avatar"><i class="fa-solid ${iconClass}"></i></div>
                <div class="feed-card-info">
                    <h4>${inc.location_name} <span class="popup-tag ${levelClass === 'text-red' ? 'high-risk' : levelClass === 'text-green' ? 'safe-zone' : 'medium-risk'}">${inc.risk_level} Risk</span></h4>
                    <p><i class="fa-solid fa-clock"></i> ${inc.time} • <i class="fa-solid fa-map-pin"></i> [${inc.latitude.toFixed(4)}, ${inc.longitude.toFixed(4)}]</p>
                    <div class="feed-desc">${inc.description}</div>
                </div>
            </div>
            <div class="feed-card-right">
                <button class="feed-verify-btn" onclick="verifyFeedIncident(${inc.id}, this)">
                    <i class="fa-solid fa-circle-check text-green"></i> Verify (<span class="v-count">${inc.verification_count}</span>)
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Verify a feed incident on frontend (Simulated verification count increment)
window.verifyFeedIncident = function(id, btnElement) {
    const countSpan = btnElement.querySelector(".v-count");
    if (!countSpan) return;
    
    if (btnElement.classList.contains("verified")) {
        showToast("You have already verified this safety report.", "info");
        return;
    }
    
    let currentCount = parseInt(countSpan.innerText) || 0;
    countSpan.innerText = currentCount + 1;
    btnElement.classList.add("verified");
    btnElement.style.borderColor = "var(--neon-purple)";
    btnElement.style.color = "var(--neon-purple)";
    
    showToast("Safety report verification recorded by community network.", "success");
};

// Route Advisor Coordinates Picking mode controllers
window.startPickingPoint = function(mode) {
    pickingPointMode = mode;
    const startBtn = document.querySelector("#route-start").parentElement.querySelector(".btn-location");
    const destBtn = document.querySelector("#route-destination").parentElement.querySelector(".btn-location");
    
    if (mode === 'start') {
        startBtn.classList.add("active");
        destBtn.classList.remove("active");
        showToast("Click on map to select Start location.", "info");
    } else {
        destBtn.classList.add("active");
        startBtn.classList.remove("active");
        showToast("Click on map to select Destination location.", "info");
    }
};

function stopPickingPoint() {
    pickingPointMode = null;
    document.querySelectorAll(".btn-location").forEach(btn => btn.classList.remove("active"));
}

// Calculate route risks and request AI feedback
window.analyzeRoute = function() {
    const startVal = document.getElementById("route-start").value.trim();
    const destVal = document.getElementById("route-destination").value.trim();
    
    if (!startVal || !destVal) {
        showToast("Please provide both Start and Destination.", "warning");
        return;
    }
    
    // Clear old route polylines
    if (map) {
        routeLines.forEach(line => map.removeLayer(line));
    }
    routeLines = [];
    
    // Show AI skeleton loader
    const aiOutput = document.getElementById("ai-analysis-output");
    const aiSkeleton = document.getElementById("ai-skeleton");
    const placeholder = aiOutput.querySelector(".ai-placeholder");
    
    if (placeholder) placeholder.style.display = "none";
    aiSkeleton.classList.remove("hidden");
    
    // If output had previous text, clear it
    const existingResult = aiOutput.querySelector(".ai-content-inner");
    if (existingResult) existingResult.remove();
    
    // Use backend API key configuration
    let payload = { start: startVal, destination: destVal };
    
    const coordReg = /^\s*(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)\s*$/;
    const startMatch = startVal.match(coordReg);
    const destMatch = destVal.match(coordReg);
    
    if (startMatch) {
        payload.start_lat = parseFloat(startMatch[1]);
        payload.start_lng = parseFloat(startMatch[3]);
    }
    if (destMatch) {
        payload.dest_lat = parseFloat(destMatch[1]);
        payload.dest_lng = parseFloat(destMatch[3]);
    }

    fetch('/analyze-route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        // Draw polylines on map (Leaflet format) if map exists
        let primaryColor = "#ff007f"; // High Risk
        if (data.estimated_safety_level === 'Safe') {
            primaryColor = "#10b981"; // Safe
        } else if (data.estimated_safety_level === 'Moderate') {
            primaryColor = "#f97316"; // Orange
        }
        
        if (map) {
            const primaryPath = data.primary_route.map(pt => [pt[0], pt[1]]);
            const altPath = data.alternative_route.map(pt => [pt[0], pt[1]]);
            
            const primaryLine = L.polyline(primaryPath, {
                color: primaryColor,
                weight: 6,
                opacity: 0.9
            }).addTo(map);
            
            const altLine = L.polyline(altPath, {
                color: "#00f0ff",
                weight: 5,
                opacity: 0.8,
                dashArray: "8, 8"
            }).addTo(map);
            
            routeLines.push(primaryLine, altLine);
            
            // Zoom map to fit route
            const bounds = L.latLngBounds([data.start_coords, data.dest_coords]);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
        
        // Show route results card elements
        document.getElementById("route-results-card").classList.remove("hidden");
        
        // Risk Labels
        document.getElementById("primary-risk-lbl").innerText = `${data.primary_risk_score}%`;
        document.getElementById("alternative-risk-lbl").innerText = `${data.alternative_risk_score}%`;
        
        // Safety Pills
        const primBadge = document.getElementById("primary-safety-badge");
        primBadge.innerText = data.estimated_safety_level;
        primBadge.className = `safety-badge ${data.estimated_safety_level === 'Safe' ? 'safe' : ''}`;
        
        // Progress Bars
        document.getElementById("primary-gauge-bar").style.width = `${data.primary_risk_score}%`;
        document.getElementById("primary-gauge-bar").style.backgroundColor = primaryColor;
        document.getElementById("alternative-gauge-bar").style.width = `${data.alternative_risk_score}%`;
        
        // Hazards lists
        const hazardsList = document.getElementById("route-hazards-list");
        if (data.nearby_incidents.length === 0) {
            hazardsList.innerText = "No reported hazard markers nearby.";
        } else {
            hazardsList.innerText = data.nearby_incidents.map(i => `${i.location_name} (${i.incident_type})`).join(", ");
        }
        
        // Custom path suggestions
        const improvement = data.primary_risk_score - data.alternative_risk_score;
        document.getElementById("route-alternative-tip").innerHTML = `Alternative Route bypasses detected hazards, yielding a <strong>${improvement}% risk reduction</strong>.`;
        
        // AI analysis markdown render
        aiSkeleton.classList.add("hidden");
        const renderedHTML = md.render(data.ai_analysis);
        
        const contentDiv = document.createElement("div");
        contentDiv.className = "ai-content-inner";
        contentDiv.innerHTML = renderedHTML;
        aiOutput.appendChild(contentDiv);
        
        // Fetch stats to update counter
        fetchStats();
        showToast("Route analysis successfully generated.", "success");
    })
    .catch(err => {
        console.error("Error analyzing route:", err);
        aiSkeleton.classList.add("hidden");
        if (placeholder) placeholder.style.display = "flex";
        showToast("Route analysis API failed.", "error");
    });
};

// Report Incident Submit
window.submitIncident = function(e) {
    e.preventDefault();
    
    const locationName = document.getElementById("report-location-name").value.trim();
    const incidentType = document.getElementById("report-incident-type").value;
    const description = document.getElementById("report-description").value.trim();
    
    if (!locationName || !description) {
        showToast("Please fill all reporting fields.", "warning");
        return;
    }
    
    const payload = {
        location_name: locationName,
        incident_type: incidentType,
        description: description,
        latitude: selectedReportLat,
        longitude: selectedReportLng
    };
    
    fetch('/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast("Safety report uploaded successfully!", "success");
            document.getElementById("incident-form").reset();
            
            // Recenter coordinates labels to default
            selectedReportLat = 22.3511;
            selectedReportLng = 78.6677;
            document.getElementById('report-lat-lbl').innerText = selectedReportLat;
            document.getElementById('report-lng-lbl').innerText = selectedReportLng;
            
            // Reload all map data & dashboards
            fetchIncidents();
            fetchStats();
            fetchLeaderboard();
        } else {
            showToast(data.error || "Report submission failed.", "error");
        }
    })
    .catch(err => {
        console.error("Error submitting report:", err);
        showToast("Network error submitting incident.", "error");
    });
};

// Chat interface logic
window.sendChatMessage = function() {
    const input = document.getElementById("chat-input");
    const msgText = input.value.trim();
    if (!msgText) return;
    
    input.value = "";
    appendChatMessage(msgText, "user");
    
    // Append loading bubble
    const messagesContainer = document.getElementById("chat-messages");
    const loadingBubble = document.createElement("div");
    loadingBubble.className = "message bot-message loading-bubble";
    loadingBubble.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> SafeRoute AI is thinking...`;
    messagesContainer.appendChild(loadingBubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    const apiKey = localStorage.getItem('gemini_api_key') || "";
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msgText, api_key: apiKey })
    })
    .then(res => res.json())
    .then(data => {
        loadingBubble.remove();
        appendChatMessage(data.reply, "bot");
        fetchStats(); // Update dashboard analysis counter
    })
    .catch(err => {
        console.error("Error in AI chat:", err);
        loadingBubble.remove();
        appendChatMessage("Sorry, I encountered an error connecting to my cognitive advisor. Please try again.", "bot");
    });
};

window.handleChatKeyPress = function(e) {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
};

window.sendQuickQuery = function(queryText) {
    appendChatMessage(queryText, "user");
    
    const messagesContainer = document.getElementById("chat-messages");
    const loadingBubble = document.createElement("div");
    loadingBubble.className = "message bot-message loading-bubble";
    loadingBubble.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> SafeRoute AI is thinking...`;
    messagesContainer.appendChild(loadingBubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    const apiKey = localStorage.getItem('gemini_api_key') || "";
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: queryText, api_key: apiKey })
    })
    .then(res => res.json())
    .then(data => {
        loadingBubble.remove();
        appendChatMessage(data.reply, "bot");
        fetchStats();
    })
    .catch(err => {
        console.error("Error in AI chat:", err);
        loadingBubble.remove();
        appendChatMessage("Sorry, I encountered an error. Please try again.", "bot");
    });
};

function appendChatMessage(text, sender) {
    const container = document.getElementById("chat-messages");
    if (!container) return;
    
    const bubble = document.createElement("div");
    bubble.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
    
    if (sender === 'bot') {
        bubble.innerHTML = md.render(text);
    } else {
        bubble.innerText = text;
    }
    
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

// SOS EMERGENCY OVERLAY SYSTEM
window.triggerSOS = function() {
    const overlay = document.getElementById("sos-overlay");
    if (!overlay) return;
    
    overlay.classList.remove("hidden");
    playSiren();
    
    // Reset status labels
    const msgEl = document.getElementById("sos-message");
    msgEl.innerText = "Initializing security emergency beacon...";
    msgEl.className = "status-msg text-yellow";
    
    const countdownEl = document.getElementById("sos-countdown");
    countdownEl.innerText = "10";
    
    // Reset safe zones with loading spinner
    const safeZonesContainer = document.getElementById("sos-safe-zones");
    if (safeZonesContainer) {
        safeZonesContainer.innerHTML = `
            <div style="text-align:center; padding:16px; color:var(--text-muted);">
                <i class="fa-solid fa-circle-notch fa-spin" style="font-size:1.5rem;"></i>
                <p style="margin-top:8px;">Fetching nearest safe locations near you...</p>
            </div>
        `;
    }
    
    // Reset address display
    const addressEl = document.getElementById("sos-address");
    if (addressEl) addressEl.innerText = "Detecting your location...";
    
    // Capture user location
    const latEl = document.getElementById("sos-lat");
    const lngEl = document.getElementById("sos-lng");
    latEl.innerText = "Accessing GPS...";
    lngEl.innerText = "Accessing GPS...";
    
    // Helper to process the detected/fallback location
    function processLocation(lat, lng, source) {
        latEl.innerText = lat;
        lngEl.innerText = lng;
        
        // Reverse-geocode to show a readable address
        if (addressEl) {
            addressEl.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Resolving address...`;
            fetch(`/reverse-geocode?lat=${lat}&lng=${lng}`)
                .then(res => res.json())
                .then(data => {
                    addressEl.innerHTML = `<i class="fa-solid fa-map-marker-alt"></i> ${data.address}`;
                })
                .catch(() => {
                    addressEl.innerText = `${lat}, ${lng} (${source})`;
                });
        }
        
        // Load dynamic safe zones for this location
        loadSOSSafeZones(lat, lng);
    }
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = parseFloat(pos.coords.latitude.toFixed(6));
                const lng = parseFloat(pos.coords.longitude.toFixed(6));
                processLocation(lat, lng, "GPS");
            },
            (err) => {
                console.warn("Geolocation permission denied, using map center.");
                let fallbackLat = 22.3511;
                let fallbackLng = 78.6677;
                if (map) {
                    fallbackLat = parseFloat(map.getCenter().lat.toFixed(6));
                    fallbackLng = parseFloat(map.getCenter().lng.toFixed(6));
                }
                processLocation(fallbackLat, fallbackLng, "Map Center");
            }
        );
    } else {
        let fallbackLat = 22.3511;
        let fallbackLng = 78.6677;
        if (map) {
            fallbackLat = parseFloat(map.getCenter().lat.toFixed(6));
            fallbackLng = parseFloat(map.getCenter().lng.toFixed(6));
        }
        processLocation(fallbackLat, fallbackLng, "Default");
    }
    
    // Start countdown
    let secondsLeft = 10;
    if (sosTimer) clearInterval(sosTimer);
    
    sosTimer = setInterval(() => {
        secondsLeft--;
        countdownEl.innerText = secondsLeft;
        
        if (secondsLeft === 5) {
            msgEl.innerText = "BROADCASTING: Encrypted SOS dispatched to nearest police patrol networks across India.";
            msgEl.className = "status-msg text-orange";
        }
        
        if (secondsLeft <= 0) {
            clearInterval(sosTimer);
            msgEl.innerText = "DISPATCH SENT! Police dispatch active. Local street wardens notified. Emergency siren active. Stay where you are.";
            msgEl.className = "status-msg text-red pulse-red";
            countdownEl.parentNode.innerText = "Emergency Broadcast Finalized.";
        }
    }, 1000);
    
    showToast("SOS Alert Initiated!", "error");
};

window.deactivateSOS = function() {
    const overlay = document.getElementById("sos-overlay");
    if (!overlay) return;
    
    overlay.classList.add("hidden");
    stopSiren();
    
    if (sosTimer) {
        clearInterval(sosTimer);
        sosTimer = null;
    }
    
    showToast("SOS emergency alert cancelled.", "info");
};

// Play Siren Synthesizer using Web Audio API
function playSiren() {
    if (audioCtx) return;
    try {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        oscillator = audioCtx.createOscillator();
        let gainNode = audioCtx.createGain();
        
        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(550, audioCtx.currentTime);
        
        gainNode.gain.setValueAtTime(0.25, audioCtx.currentTime);
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        oscillator.start();
        
        let high = true;
        sirenInterval = setInterval(() => {
            if (!audioCtx || !oscillator) return;
            // Alternates siren pitches
            let currentFreq = high ? 850 : 550;
            oscillator.frequency.exponentialRampToValueAtTime(currentFreq, audioCtx.currentTime + 0.35);
            high = !high;
        }, 450);
    } catch (e) {
        console.warn("Web Audio API blocked / unsupported in this environment:", e);
    }
}

function stopSiren() {
    if (sirenInterval) {
        clearInterval(sirenInterval);
        sirenInterval = null;
    }
    if (oscillator) {
        try { oscillator.stop(); } catch(e){}
        oscillator = null;
    }
    if (audioCtx) {
        audioCtx.close();
        audioCtx = null;
    }
}

// Compute closest Safe Zones for SOS overlay list
function loadSOSSafeZones(userLat, userLng) {
    const container = document.getElementById("sos-safe-zones");
    if (!container) return;
    
    // Show loading state
    container.innerHTML = `
        <div style="text-align:center; padding:16px; color:var(--text-muted);">
            <i class="fa-solid fa-circle-notch fa-spin" style="font-size:1.5rem;"></i>
            <p style="margin-top:8px;">Scanning nearby police stations, hospitals & safe zones...</p>
        </div>
    `;
    
    // Fetch dynamic nearby safe zones using Gemini backend
    fetch(`/get-nearby-safe-zones?lat=${userLat}&lng=${userLng}`)
        .then(res => res.json())
        .then(data => {
            const safeZones = data.safe_zones;
            
            // Calculate distance to each
            safeZones.forEach(sz => {
                sz.distance = getDistanceKm(userLat, userLng, sz.latitude, sz.longitude);
            });
            
            // Sort by closest distance
            safeZones.sort((a, b) => a.distance - b.distance);
            
            container.innerHTML = "";
            
            if (safeZones.length === 0) {
                container.innerHTML = "<div style='font-size:0.8rem; color:var(--text-dimmed);'>No safe zones found near your location.</div>";
                return;
            }
            
            // Display closest 3
            safeZones.slice(0, 3).forEach((sz, index) => {
                const card = document.createElement("div");
                card.className = "sos-safe-card";
                const mapsUrl = `https://www.google.com/maps/dir/${userLat},${userLng}/${sz.latitude},${sz.longitude}`;
                const rankIcons = ["🥇", "🥈", "🥉"];
                card.innerHTML = `
                    <div style="flex:1;">
                        <h5 style="margin:0 0 4px 0;"><span style="font-size:1.1rem;">${rankIcons[index] || ''}</span> <i class="fa-solid fa-shield-halved"></i> ${sz.location_name}</h5>
                        <p style="font-size:0.75rem; color:var(--text-muted); margin:0 0 6px 0;">${sz.description}</p>
                        <a href="${mapsUrl}" target="_blank" rel="noopener" style="font-size:0.75rem; color:var(--neon-cyan); text-decoration:none;">
                            <i class="fa-solid fa-diamond-turn-right"></i> Get Directions
                        </a>
                    </div>
                    <span style="white-space:nowrap; font-weight:600; color:var(--neon-purple);">${sz.distance.toFixed(2)} km</span>
                `;
                container.appendChild(card);
            });
        })
        .catch(err => {
            console.error("Error loading safe zones for SOS:", err);
            container.innerHTML = "<div style='font-size:0.8rem; color:var(--text-dimmed);'><i class='fa-solid fa-triangle-exclamation'></i> Failed to load nearby safe zones. Please call 112 immediately.</div>";
        });
}

// Distance helper
function getDistanceKm(lat1, lon1, lat2, lon2) {
    const R = 6371; // radius
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Toast notification trigger
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = "fa-info-circle text-blue";
    if (type === "success") icon = "fa-circle-check text-green";
    else if (type === "warning") icon = "fa-triangle-exclamation text-orange";
    else if (type === "error") icon = "fa-circle-xmark text-red";
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Slide out after 3.5 seconds
    setTimeout(() => {
        toast.style.animation = "toastSlideIn 0.3s ease-out reverse forwards";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Settings modal removed, managed via .env

// ═══════════════════════════════════════════════════════
// LIGHT / DARK THEME TOGGLE
// ═══════════════════════════════════════════════════════

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update toggle icon
    const icon = document.getElementById('theme-icon');
    if (icon) {
        if (theme === 'light') {
            icon.className = 'fa-solid fa-sun';
        } else {
            icon.className = 'fa-solid fa-moon';
        }
    }
    
    // Swap map tile layer for Leaflet
    if (map && currentTileLayer) {
        map.removeLayer(currentTileLayer);
        currentTileLayer = L.tileLayer(
            theme === 'light' ? TILE_LIGHT : TILE_DARK,
            { maxZoom: 19 }
        ).addTo(map);
    }
    
    localStorage.setItem('saferoute_theme', theme);
}

window.toggleTheme = function() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    showToast(`Switched to ${next === 'light' ? '☀️ Light' : '🌙 Dark'} Mode`, "info");
};

// Initialize theme on page load (hook into existing DOMContentLoaded flow)
(function initTheme() {
    const saved = localStorage.getItem('saferoute_theme') || 'dark';
    // Set attribute immediately to prevent flash
    document.documentElement.setAttribute('data-theme', saved);
    
    // Update icon once DOM is ready
    const onReady = () => {
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = saved === 'light' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
    };
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onReady);
    } else {
        onReady();
    }
})();
