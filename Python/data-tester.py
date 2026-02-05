import requests
import random
import time

URL = "http://127.0.0.1:5000/api/esp32/data"

def generate_fake_sample():
    return {
        "device_id": "ESP32_TEST_001",
        "samples": [{
            # try OC-like condition
            "v": round(random.uniform(30, 38), 2),   # high voltage
            "i": round(random.uniform(0.0, 0.3), 2), # low current
            "g": random.randint(700, 1000),          # irradiance
            "t": round(random.uniform(30, 50), 1)    # temperature
        }]
    }

while True:
    payload = generate_fake_sample()
    response = requests.post(URL, json=payload)

    print("Sent:", payload)
    print("Received:", response.json())
    print("-" * 50)

    time.sleep(2)
