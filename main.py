import os
import platform
import time
import requests
import subprocess
import threading
import ctypes
import sys
import numpy as np
from scapy.all import sniff
from collections import defaultdict
from flask import Flask, jsonify, render_template, redirect
from sklearn.ensemble import IsolationForest
from dotenv import load_dotenv

# ================================
# 🌐 CONFIGURATION
# ================================
load_dotenv('config.env')

THRESHOLD = int(os.getenv("THRESHOLD", "100"))  # Default to 100 if not set
# Telegram configuration
TELEGRAM_BOT_TOKEN = "7737893459:AAFXBllgvKQRzBH-LoNJBN5W3921x9EK9Rc"
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Request Logs for Rate Limiting
request_log = defaultdict(list)

# Traffic Data & Blocked IPs
traffic_data = defaultdict(int)
blocked_ips = set()  # Use a set to avoid duplicate entries

# Detect OS Type
OS_TYPE = platform.system()

# Dictionary to store last alert time per IP
last_alert_time = {}

# ================================
# 🎯 DDoS Detection & Blocking
# ================================
def is_trusted_ip(ip):
    """ Check if an IP is from a trusted provider (CDN, API, etc.) """
    trusted_ips = []  # Add trusted IPs like ["184.84.233.97", "184.84.233.49"]
    return ip in trusted_ips


def detect_ddos(packet):
    if packet.haslayer("IP"):
        src_ip = packet["IP"].src
        current_time = time.time()

        # Ignore Local Network & Trusted Traffic
        if src_ip.startswith(("192.168.", "10.", "127.0.0.1")) or is_trusted_ip(src_ip):
            return

        # Remove old requests (>10 sec old)
        request_log[src_ip] = [t for t in request_log[src_ip] if current_time - t < 10]

        # Add new request
        request_log[src_ip].append(current_time)
        traffic_data[src_ip] += 1

        # Check if IP exceeds threshold
        if len(request_log[src_ip]) > THRESHOLD:
            print(f"[⚠ ALERT] Possible DDoS attack detected from {src_ip}!")

            # WHOIS Lookup Before Blocking (Reduce False Positives)
            try:
                whois_data = requests.get(f"https://ipinfo.io/{src_ip}/json").json()
                print(f"🌍 WHOIS Lookup: {whois_data}")
            except Exception as e:
                print(f"[⚠ ERROR] Failed to fetch WHOIS data: {e}")
                return

            if "org" not in whois_data or "Cloudflare" not in whois_data["org"]:
                block_ip(src_ip)
                send_alert(src_ip)
                blocked_ips.add(src_ip)
                request_log[src_ip] = []


def check_admin():
    """Ensures the script is run with administrator privileges (Windows only)."""
    if OS_TYPE == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
        print("[⚠] Please run this script as Administrator.")
        sys.exit(1)


def block_ip(ip):
    if ip not in blocked_ips:
        blocked_ips.add(ip)
        log_attack(ip)

        if OS_TYPE == "Linux":
            print(f"[🔴 BLOCK] Blocking IP (Linux): {ip}")
            os.system(f"iptables -A INPUT -s {ip} -j DROP")
        elif OS_TYPE == "Windows":
            print(f"[🔴 BLOCK] Blocking IP (Windows): {ip}")
            command = f"netsh advfirewall firewall add rule name=\"Block {ip}\" dir=in action=block remoteip={ip}"
            subprocess.run(command, shell=True)


def reset_traffic_data():
    while True:
        time.sleep(3600)
        traffic_data.clear()
        print("[🔄] Traffic data reset")


def log_attack(ip):
    with open("attack_log.txt", "a") as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Blocked {ip}\n")


# ================================
# 🔔 Alert System (Telegram)
# ================================

def send_alert(ip):
    """Sends a DDoS attack alert to Telegram with WHOIS details."""
    global last_alert_time

    # Avoid duplicate alerts within 5 minutes
    current_time = time.time()
    if ip in last_alert_time and (current_time - last_alert_time[ip]) < 300:
        print(f"⏳ Skipping duplicate alert for {ip} (Cooldown active)")
        return

    # Fetch WHOIS details
    try:
        whois_data = requests.get(f"https://ipinfo.io/{ip}/json").json()
        org = whois_data.get("org", "Unknown Organization")
        country = whois_data.get("country", "Unknown Country")
        region = whois_data.get("region", "Unknown Region")
        asn = whois_data.get("asn", "Unknown ASN")
    except Exception as e:
        print(f"[⚠ ERROR] Failed to fetch WHOIS data: {e}")
        org, country, region, asn = "Unknown", "Unknown", "Unknown", "Unknown"

    # Format message
    message = (
        f"🚨 **DDoS Attack Detected!** 🚨\n\n"
        f"📌 **IP:** `{ip}`\n"
        f"🏢 **ISP/Org:** {org}\n"
        f"🌍 **Location:** {region}, {country}\n"
        f"🔢 **ASN:** {asn}\n\n"
        f"🚫 IP has been blocked!"
    )

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(telegram_url, json=data)
        if response.status_code == 200:
            print(f"✅ Telegram Alert Sent for {ip}")
            last_alert_time[ip] = current_time  # Update last alert time
        else:
            print(f"[⚠ ERROR] Telegram Alert Failed. Status Code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[⚠ ERROR] Failed to send Telegram alert: {e}")

# ================================
# 📊 Machine Learning Detection
# ================================
def train_ml_model():
    global model
    data = np.array([[10], [12], [15], [500], [8], [7], [600]])
    model = IsolationForest(contamination=0.1)
    model.fit(data)


def predict_anomaly(request_rate):
    prediction = model.predict([[request_rate]])
    return prediction[0] == -1


# ================================
# 🌐 Web Dashboard (Flask API)
# ================================
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return redirect("/stats")
    #return "Welcome to DDos Detection Tool.please kindly Redirect http://127.0.0.1:5000/static"

@app.route("/stats")
def traffic_stats():
    return render_template("stats.html")


@app.route("/api/stats")
def api_stats():
    return jsonify({
        "traffic": traffic_data,
        "blocked": list(blocked_ips)
    })


def start_flask():
    app.run(debug=False, port=5000)

# ================================
# 🚀 Start Detection
# ================================
if __name__ == "__main__":
    check_admin()
    print(f"🚀 Starting DDoS Detection System on {OS_TYPE}...")
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    train_ml_model()
    if OS_TYPE == "Linux" and os.geteuid() != 0:
        print("[⚠] WARNING: Run with `sudo` for packet sniffing.")
    sniff(filter="tcp port 80 or tcp port 443", prn=detect_ddos, store=False)