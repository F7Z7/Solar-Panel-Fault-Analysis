from collections import deque

import joblib
from flask import Flask, jsonify, request, render_template
import numpy as np

app = Flask(__name__)

LATEST_DATA = {}

KNN_MODEL = joblib.load("models/knn_oc_sc_classifier.pkl")

# Ring buffer for irradiance (last 5 readings)
IRRADIANCE_BUFFER = deque(maxlen=5)

# Hotspot temperature threshold
HOTSPOT_TEMP = 65


@app.route("/api/esp32/data", methods=["POST"])
def receive_esp32_data():
    global LATEST_DATA

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    try:
        s = data["samples"][0]
        voltage = float(s["v"])
        current = float(s["i"])
        irradiance = float(s["g"])
        temperature = float(s["t"])
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    prediction = analyze_data(voltage, current, irradiance, temperature)

    LATEST_DATA = {
        "voltage": voltage,
        "current": current,
        "irradiance": irradiance,
        "temperature": temperature,
        "fault_type": prediction["fault_type"],
        "fault_status": prediction["fault_status"]
    }

    return jsonify({
        "status": "received",
        "prediction": prediction
    })


def operating_region(voltage, current, irradiance, temp):
    Voc_est = 0.04 * irradiance
    Isc_est = 0.005 * irradiance

    v_ratio = voltage / (Voc_est + 1e-6)
    i_ratio = current / (Isc_est + 1e-6)

    if v_ratio > 0.9 and i_ratio < 0.1:
        return "OC"
    elif v_ratio < 0.1 and i_ratio > 0.9:
        return "SC"
    else:
        return "NORMAL"

def detect_partial_shading(irradiance):

    IRRADIANCE_BUFFER.append(irradiance)

    # Wait until buffer is full
    if len(IRRADIANCE_BUFFER) < 5:
        return False

    values = list(IRRADIANCE_BUFFER)

    # Check continuous decrease
    for i in range(len(values) - 1):
        if values[i] <= values[i + 1]:
            return False

    return True

def analyze_data(voltage, current, irradiance, temperature):

    region = operating_region(voltage, current, irradiance, temperature)

    # OC / SC Fault
    if region in ["OC", "SC"]:
        return {
            "fault_type": region,
            "fault_status": "Fault"
        }

    # Hotspot Fault
    if temperature > HOTSPOT_TEMP:
        return {
            "fault_type": "HOTSPOT",
            "fault_status": "Fault"
        }

    # Partial Shading Fault
    if detect_partial_shading(irradiance):
        return {
            "fault_type": "PARTIAL_SHADING",
            "fault_status": "Fault"
        }

    # Normal Condition
    return {
        "fault_type": "NONE",
        "fault_status": "Normal"
    }


# @app.route("/api/latest", methods=["GET"])
# def get_latest():
#     return jsonify(LATEST_DATA)

@app.route('/')
def ui():
    global LATEST_DATA

    if not LATEST_DATA:
        return "No data received yet"

    return render_template("dashboard.html", data=LATEST_DATA)
if __name__ == "__main__":
    app.run(debug=True)