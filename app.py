import os
import pickle
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__, static_folder="static", template_folder="templates")

model = None
model_path = os.path.join(app.root_path, "ddos_model.pkl")
if os.path.exists(model_path):
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
    except Exception:
        model = None

attack_history = []
traffic_logs = []
ip_counter = {}
blocked_ips = set()
requests_data = [
    {
        "id": 1,
        "company": "ABC Cloud",
        "website": "abc.com",
        "status": "Pending"
    }
]

@app.before_request
def monitor_traffic():

    ip = request.remote_addr

    if ip in blocked_ips:
        return "Access Blocked 🚫"

    ip_counter[ip] = ip_counter.get(ip, 0) + 1

    count = ip_counter[ip]

    if count <= 20:
        status = "NORMAL 🟢"
    elif count <= 50:
        status = "SUSPICIOUS ⚠️"
    else:
        status = "ATTACK 🔴"

    traffic_logs.append({
        "ip": ip,
        "page": request.path,
        "time": datetime.now().strftime("%H:%M:%S"),
        "requests": count,
        "status": status
    })

    if ip != "127.0.0.1" and count > 100:
        blocked_ips.add(ip)

        attack_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": ip,
            "result": "ATTACK 🔴",
            "severity": "High"
        })


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/stream_predict", methods=["GET"])
def stream_predict():
    try:
        packet_rate = random.randint(60, 1250)
        byte_size = random.randint(320, 1600)
        connection_count = random.randint(3, 180)

        score = packet_rate * 0.5 + byte_size * 0.2 + connection_count * 2
        if score > 800:
            result = "ATTACK 🔴"
            severity = "High"
        elif score > 550:
            result = "SUSPICIOUS ⚠️"
            severity = "Medium"
        else:
            result = "NORMAL 🟢"
            severity = "Low"

        entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "packet_rate": packet_rate,
            "byte_size": byte_size,
            "connection_count": connection_count,
            "result": result,
            "severity": severity,
        }

        record_history(entry)
        return jsonify(entry)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/attack_history", methods=["GET"])
def get_attack_history():
    return jsonify({"history": attack_history})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    try:
        packet_rate = float(data.get("packet_rate", 0))
        byte_size = float(data.get("byte_size", 0))
        connection_count = float(data.get("connection_count", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid numeric values"}), 400

    features = [[packet_rate, byte_size, connection_count]]
    prediction = None
    confidence = None

    if model is not None:
        try:
            label = model.predict(features)[0]
            prediction = "ATTACK 🔴" if int(label) == 1 else "NORMAL 🟢"
            if hasattr(model, "predict_proba"):
                confidence = float(max(model.predict_proba(features)[0]))
        except Exception:
            prediction = "UNKNOWN"
    else:
        prediction = "ATTACK 🔴" if random.random() > 0.6 else "NORMAL 🟢"

    response = {
        "packet_rate": packet_rate,
        "byte_size": byte_size,
        "connection_count": connection_count,
        "prediction": prediction,
        "confidence": f"{confidence:.2f}" if confidence is not None else None,
    }
    return jsonify(response)

@app.route("/traffic")
def traffic():
    return render_template("traffic.html")


@app.route("/attack")
def attack():
    return render_template("attack.html")


@app.route("/blocked")
def blocked():
    return render_template("blocked.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/settings")
def settings():
    return render_template("settings.html")
@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")


@app.route("/detection")
def detection():
    return render_template("detection.html")


@app.route("/architecture")
def architecture():
    return render_template("architecture.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/history")
def history():
    return render_template("history.html")
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
@app.route("/submit_request", methods=["GET", "POST"])
def submit_request():
    
    if request.method == "POST":
        company = request.form.get("company")
        website = request.form.get("website")
        ip = request.form.get("ip")
        email = request.form.get("email")
        protection = request.form.get("protection")

        print("Company:", company)
        print("Website:", website)
        print("IP:", ip)
        print("Email:", email)
        print("Protection:", protection)

        return f"""
        <h1>Request Submitted Successfully ✅</h1>
        <p>Company: {company}</p>
        <p>Website: {website}</p>
        <p>Status: Pending Approval</p>
        <a href='/'>Back to Home</a>
        """

    return render_template("submit_request.html")
@app.route("/my_requests")
def my_requests():
    return render_template("my_requests.html")
@app.route("/admin_request")
def admin_request():
    return render_template(
        "admin_request.html",
        requests=requests_data
    )
@app.route("/approve/<int:id>")
def approve(id):

    for req in requests_data:
        if req["id"] == id:
            req["status"] = "Approved"

    return redirect("/admin_request")

@app.route("/reject/<int:id>")
def reject(id):

    for req in requests_data:
        if req["id"] == id:
            req["status"] = "Rejected"

    return redirect("/admin_request")
@app.route("/traffic_logs")
def traffic_logs_page():
    return jsonify(traffic_logs)
@app.route("/blocked_ips")
def blocked_ips_page():
    return jsonify(list(blocked_ips))
@app.route("/protected_site")
def protected_site():
    return render_template("protected_site.html")

if __name__ == "__main__":
    # 🔥 IMPORTANT FIX: FORCE PORT 8000
    app.run(host="127.0.0.1", port=8000, debug=True)