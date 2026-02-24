import joblib
from flask import Flask, jsonify, request, render_template
import numpy as np

app = Flask(__name__)

LATEST_DATA = {}

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


def analyze_data(voltage, current, irradiance, temperature):
    region = operating_region(voltage, current, irradiance, temperature)

    if region in ["OC", "SC"]:
        fault_status = "Fault"
        fault = region
    else:
        fault_status = "Normal"
        fault = "NONE"

    return {
        "fault_type": fault,
        "fault_status": fault_status
    }


@app.route('/')
def ui():
    voltage = 32
    current = 1
    irradiance = 820
    temperature = 41.3

    result = analyze_data(voltage, current, irradiance, temperature)

    data = {
        "voltage": voltage,
        "current": current,
        "irradiance": irradiance,
        "temperature": temperature,
        "fault_status": result["fault_status"],
        "fault_type": result["fault_type"]
    }

    return render_template("dashboard.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)