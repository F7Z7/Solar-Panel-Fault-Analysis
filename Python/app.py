from flask import Flask, jsonify, request,render_template

import pickle
import numpy as np

app=Flask(__name__)


@app.route('/')
def home():
    return "Welcome to the Flask API!"



@app.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name)


@app.route("/api/esp32/data", methods=["POST"])

def receive_esp32_data():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    device_id = data.get("device_id")

    try:
        samples = data["samples"]
        s = samples[0]

        voltage = float(s["v"])
        current = float(s["i"])
        irradiance = float(s["g"])
        temperature = float(s["t"])


    except (KeyError, IndexError, TypeError, ValueError) as e:
        return jsonify({
            "error": "Invalid or malformed sample data",
            "details": str(e)
        }), 400
    prediction = analyze_data(voltage, current, irradiance, temperature)

    return jsonify({
        "status": "received",
        "device_id": device_id,
        # "fault": prediction
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
    # model=FaultDetector() placeholder for actual model
    # prediction = model.predict([[voltage, current, irradiance, temperature]])

    region=operating_region(voltage, current, irradiance)

    if region in ["OC", "SC"]:
        model_path = "Python//models//knn_oc_sc_classifier.pkl"
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        features = np.array([[voltage, current, irradiance, temperature]])
        fault = model.predict(features)
        print(fault)
        return {
            "region": region,
            "fault_type": fault
        }
    else:
        fault = hotspot_model.predict([[voltage, current, irradiance, temperature]])
        return {
            "region": "NORMAL_OPERATION",
            "fault_type": fault
        }


@app.route('/ui')
def ui():

    voltage = 32.5          # V
    current = 5.2           # A
    irradiance = 820        # W/m²
    temperature = 41.3      # °C
    fault_status = "Normal"
    fault_type = "None"

    data = {
        "voltage": voltage,
        "current": current,
        "irradiance": irradiance,
        "temperature": temperature,
        "fault_status": fault_status,
        "fault_type": fault_type
    }

    return render_template('dashboard.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)