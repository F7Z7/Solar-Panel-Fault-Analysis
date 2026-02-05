import joblib
from flask import Flask, jsonify, request,render_template

import pickle
import numpy as np

app=Flask(__name__)


@app.route('/')
def home():
    return "Welcome to the Flask API!"

#loading models
KNN_MODEL = joblib.load("models/knn_oc_sc_classifier.pkl")


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
        "region": prediction["region"],
        "fault_type": prediction["fault_type"]
    }

    return jsonify({
        "status": "received",
        "prediction": prediction
    })

def operating_region(voltage, current,irradiance):
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

def analyze_data(voltage, current, irradiance, temperature):
    region = operating_region(voltage, current, irradiance)

    if region in ["OC", "SC"]:
        features = np.array([[voltage, current, irradiance, temperature]])
        fault = KNN_MODEL.predict(features)[0]
    else:
        fault = "NONE"

    return {
        "region": region,
        "fault_type": str(fault)
    }

@app.route('/ui')
def ui():
    if LATEST_DATA is None:
        return "No ESP32 data received yet."

    return render_template("dashboard.html", data=LATEST_DATA)

if __name__ == "__main__":
    app.run(debug=True)