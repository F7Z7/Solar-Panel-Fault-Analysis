from flask import Flask, jsonify, request,render_template



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
    # prediction = analyze_data(voltage, current, irradiance, temperature)

    return jsonify({
        "status": "received",
        "device_id": device_id,
        # "fault": prediction
    })
def analyze_data(voltage, current, irradiance, temperature):
    # model=FaultDetector() placeholder for actual model
    # prediction = model.predict([[voltage, current, irradiance, temperature]])
    if voltage < 10 or irradiance < 200:
        return "Fault suspected"
    return "Normal"



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