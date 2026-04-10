import os
import json
import math
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'alpha_neural_core_secure_key_2026'

# ---------------- FOLDERS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
DATA_FOLDER = os.path.join(BASE_DIR, 'data')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

LOGIN_JSON = os.path.join(DATA_FOLDER, 'logins.json')
PATIENT_JSON = os.path.join(DATA_FOLDER, 'patients.json')

# ---------------- INIT FILES ----------------
for f in [LOGIN_JSON, PATIENT_JSON]:
    if not os.path.exists(f):
        with open(f, 'w') as file:
            json.dump({}, file)

# ---------------- USERS ----------------
CREDENTIALS = {
    "admin": {"password": "admin@alpha", "role": "ADMIN"},
    "police": {"password": "police@alpha", "role": "POLICE"},
    "ems": {"password": "ems@alpha", "role": "EMS"},
    "patient": {"password": "user@alpha", "role": "PATIENT"}
}

# ---------------- HOSPITALS ----------------
HOSPITALS = [
    {"id": 1, "name": "City Cardiac Center", "lat": 12.9716, "lng": 77.5946, "specialty": "Cardiology", "inventory": {"icu_beds": 2, "status": "AVAILABLE"}},
    {"id": 2, "name": "Metro Trauma Care", "lat": 12.9800, "lng": 77.6000, "specialty": "Trauma", "inventory": {"icu_beds": 0, "status": "UNAVAILABLE"}},
    {"id": 3, "name": "General Health Hub", "lat": 12.9500, "lng": 77.5800, "specialty": "General", "inventory": {"icu_beds": 10, "status": "AVAILABLE"}}
]

# ---------------- HELPERS ----------------
def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def float_or_default(value, default):
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return "ACCESS DENIED", 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

# ---------------- AI + SAFETY ----------------
def predict_risk(bpm, spo2):
    if bpm > 130 or spo2 < 90:
        return "HIGH 🚨"
    elif spo2 < 95:
        return "MEDIUM ⚠️"
    return "LOW ✅"

def assign_responder(risk):
    return "EMS" if risk == "HIGH 🚨" else random.choice(["POLICE", "EMS"])

def calculate_priority(risk):
    return {"HIGH 🚨": 1, "MEDIUM ⚠️": 2, "LOW ✅": 3}[risk]

def is_valid_location(lat, lng):
    return 10 < lat < 20 and 70 < lng < 80

def is_spam(user, data):
    user_cases = [e for e in data.values() if e.get("user") == user]
    return len(user_cases) >= 3

def update_trust_score(user, change):
    logins = load_json(LOGIN_JSON)
    score = logins.get(user, {}).get("score", 50)
    score += change
    score = max(0, min(100, score))
    logins[user] = {"score": score}
    save_json(LOGIN_JSON, logins)
    return score

def find_best_hospital(lat, lng):
    return min(HOSPITALS, key=lambda h: math.sqrt((h['lat']-lat)**2 + (h['lng']-lng)**2))

def send_alert(msg):
    print(f"🚨 {msg}")

# ---------------- CORE EMERGENCY ----------------
def create_emergency(v, lat, lng, user, photo=None):
    data = load_json(PATIENT_JSON)

    if not is_valid_location(lat, lng):
        return None, "Invalid GPS location!"

    if is_spam(user, data):
        return None, "Too many requests! You are temporarily blocked."

    if v in data and data[v]["status"] != "COMPLETED":
        return v, None

    bpm = random.randint(70,150)
    spo2 = random.randint(85,100)
    risk = predict_risk(bpm, spo2)

    if risk == "HIGH 🚨" and not photo:
        return None, "Photo proof required for critical emergency!"

    hospital = find_best_hospital(lat, lng)
    assigned = assign_responder(risk)

    data[v] = {
        "vehicle": v,
        "user": user,
        "risk": risk,
        "priority": calculate_priority(risk),
        "assigned_to": assigned,
        "status": "ASSIGNED",
        "hospital": hospital['name'],
        "location": {"lat": lat, "lng": lng},
        "eta": f"{random.randint(5,15)} min",
        "time": str(datetime.now()),
        "photo": photo
    }

    save_json(PATIENT_JSON, data)
    update_trust_score(user, +5)
    send_alert(f"{v} assigned to {assigned}")

    return v, None

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return render_template('index.html')

# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in CREDENTIALS and CREDENTIALS[u]['password'] == p:
            session['user'] = u
            session['role'] = CREDENTIALS[u]['role']
            return redirect(url_for({
                "ADMIN": "admin",
                "POLICE": "police",
                "EMS": "ems",
                "PATIENT": "emergency"
            }[session['role']]))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# EMERGENCY
@app.route('/emergency', methods=['GET','POST'])
@login_required()
def emergency():
    if request.method == 'POST':
        # Load existing data
        emergencies = load_json(PATIENT_JSON)
        
        # Create new record with ALL coordinates and vitals
        vehicle = request.form.get("vehicle_number")
        new_entry = {
            "vehicle": vehicle,
            "severity": request.form.get("severity"),
            "lat": request.form.get("lat"),
            "lng": request.form.get("lng"),
            "vitals": {
                "bpm": request.form.get("bpm", "N/A"),
                "spo2": request.form.get("spo2", "N/A")
            },
            "status": "PENDING",
            "user": session.get("user"),
            "time": str(datetime.now())
        }
        
        emergencies[vehicle] = new_entry
        save_json(PATIENT_JSON, emergencies)
        return redirect(url_for('track', v=vehicle))

    return render_template('emergency.html')

# GUEST
@app.route('/guest_emergency', methods=['GET','POST'])
def guest_emergency():
    if request.method == 'POST':
        v = request.form['vehicle_number']
        lat = float_or_default(request.form.get('lat'), 12.97)
        lng = float_or_default(request.form.get('lng'), 77.59)
        user = "guest"

        v, error = create_emergency(v, lat, lng, user)

        if error:
            return error

        return redirect(url_for('track', v=v))

    return render_template('emergency.html')

# TRACK
@app.route('/track/<v>')
def track(v):
    data = load_json(PATIENT_JSON).get(v,{})
    return render_template('tracking.html', data=data, vehicle_number=v)

# ACCEPT
@app.route('/accept/<v>', methods=['POST'])
def accept(v):
    data = load_json(PATIENT_JSON)
    if v in data:
        data[v]["status"] = "IN PROGRESS"
        data[v]["accepted_by"] = session.get("role")
    save_json(PATIENT_JSON, data)
    return redirect(request.referrer)

# COMPLETE
@app.route('/complete/<v>')
def complete(v):
    data = load_json(PATIENT_JSON)
    if v in data:
        data[v]["status"] = "COMPLETED"
    save_json(PATIENT_JSON, data)
    return redirect(request.referrer)

# DASHBOARDS
@app.route('/police')
@login_required('POLICE')
def police():
    data = load_json(PATIENT_JSON)
    calls = []
    for i, e in enumerate(data.values(), 1):
        e_copy = e.copy()
        e_copy['id'] = i
        calls.append(e_copy)
    return render_template('police.html', calls=calls, hospitals=HOSPITALS)

@app.route('/ems')
@login_required('EMS')
def ems():
    data = load_json(PATIENT_JSON)
    emergencies = []
    for i, e in enumerate(data.values(), 1):
        e_copy = e.copy()
        e_copy['id'] = i
        emergencies.append(e_copy)
    return render_template('ems_center.html', emergencies=emergencies, hospitals=HOSPITALS)

@app.route('/admin')
@login_required('ADMIN')
def admin():
    data = load_json(PATIENT_JSON)
    emergencies = []
    for i, e in enumerate(data.values(), 1):
        e_copy = e.copy()
        e_copy['id'] = i
        emergencies.append(e_copy)
    stats = {
        "total": len(data),
        "critical": len([e for e in data.values() if e['risk']=="HIGH 🚨"])
    }
    return render_template('admin.html', emergencies=emergencies, stats=stats, hospitals=HOSPITALS)

# API
@app.route('/api/<v>')
def api(v):
    return jsonify(load_json(PATIENT_JSON).get(v,{}))

# RUN
if __name__ == '__main__':
    app.run(debug=True)