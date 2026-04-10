/**
 * LIFE LINE SOS - AI EMERGENCY HUD
 * Standalone Script for Real-time Tracking & Vitals
 */

// Global Variables
let map, marker;
const config = {
    highAccuracy: true,
    timeout: 10000,
    maxAge: 0,
    vitalsInterval: 2500
};

/**
 * 1. LIVE HIGH-ACCURACY GPS TRACKING
 * Uses watchPosition to follow the user in real-time
 */
function initTracking() {
    const gpsDisplay = document.getElementById("gps");
    const googleLink = document.getElementById("googleMapsLink");
    const latInput = document.getElementById("lat");
    const lngInput = document.getElementById("lng");

    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            position => {
                const { latitude, longitude } = position.coords;

                // Update hidden form inputs for submission
                if (latInput) latInput.value = latitude;
                if (lngInput) lngInput.value = longitude;

                // Update HUD Text
                if (gpsDisplay) {
                    gpsDisplay.innerText = `📍 LIVE: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
                    gpsDisplay.style.color = "#00f2ff";
                }

                // Update LIVE Google Maps Link
                // This link opens the user's current spot and searches for nearby hospitals
                if (googleLink) {
                    googleLink.href = `https://www.google.com/maps/dir/?api=1&origin=${latitude},${longitude}&destination=hospital&travelmode=driving`;
                }

                // Update Leaflet HUD Map
                updateMap(latitude, longitude);
            },
            error => {
                if (gpsDisplay) {
                    gpsDisplay.innerText = "⚠️ GPS SIGNAL LOST / DENIED";
                    gpsDisplay.style.color = "#ff073a";
                }
                console.error("Geolocation Error:", error);
            },
            { 
                enableHighAccuracy: config.highAccuracy, 
                maximumAge: config.maxAge, 
                timeout: config.timeout 
            }
        );
    } else {
        if (gpsDisplay) gpsDisplay.innerText = "❌ GPS NOT SUPPORTED";
    }
}

/**
 * 2. MAP CONTROLLER
 * Handles the dark-themed HUD map updates
 */
function updateMap(lat, lng) {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    if (!map) {
        // Initialize Map if it doesn't exist
        map = L.map('map', { zoomControl: false }).setView([lat, lng], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        marker = L.marker([lat, lng]).addTo(map);
    } else {
        // Update existing marker and view
        marker.setLatLng([lat, lng]);
        map.setView([lat, lng]);
    }
}

/**
 * 3. AI VITALS SIMULATION
 * Mimics real-time medical monitoring
 */
function simulateVitals() {
    const bpmEl = document.getElementById("bpm");
    const spo2El = document.getElementById("spo2");
    const alertBox = document.getElementById("alertBox");
    const bpmCard = document.getElementById("vital-bpm");
    const criticalRadio = document.getElementById("critical");

    if (!bpmEl || !spo2El) return;

    // Generate realistic fluctuating data
    let bpm = Math.floor(Math.random() * 45) + 70; // 70-115 range
    let spo2 = Math.floor(Math.random() * 6) + 94;  // 94-100 range

    bpmEl.innerText = bpm;
    spo2El.innerText = spo2;

    // AI Logic: Trigger alert if vitals are dangerous
    if (bpm > 105 || spo2 < 93) {
        if (alertBox) alertBox.style.display = "block";
        if (bpmCard) bpmCard.style.borderBottomColor = "#ff073a";
        if (criticalRadio) criticalRadio.checked = true;
    } else {
        if (alertBox) alertBox.style.display = "none";
        if (bpmCard) bpmCard.style.borderBottomColor = "#00f2ff";
    }
}

/**
 * 4. EVENT LISTENERS & INITIALIZATION
 */
document.addEventListener("DOMContentLoaded", () => {
    // Start Live Tracking
    initTracking();

    // Start Vitals Monitoring
    setInterval(simulateVitals, config.vitalsInterval);

    // Handle Image Upload Feedback
    const photoInput = document.getElementById("photo");
    const gpsDisplay = document.getElementById("gps");
    
    if (photoInput) {
        photoInput.onchange = function() {
            if (this.files.length > 0 && gpsDisplay) {
                gpsDisplay.innerText = "📸 EVIDENCE ATTACHED & READY";
                gpsDisplay.style.color = "#00f2ff";
            }
        };
    }
});