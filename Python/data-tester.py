"""
fake_sender.py  —  ESP32 data simulator for Solar Fault Monitor
Randomly fires Normal / OC / SC / Hotspot / Partial-Shading samples
at random intervals so every fault type appears naturally in the dashboard.
"""

import requests
import random
import time

URL = "http://127.0.0.1:5000/api/esp32/data"

# ── Interval range (seconds between each send) ───────────────────────────────
MIN_INTERVAL = 1.5
MAX_INTERVAL = 4.0

# ── Fault weights  (higher = appears more often) ─────────────────────────────
FAULT_WEIGHTS = {
    "normal":          40,   # most common
    "oc":              15,
    "sc":              15,
    "hotspot":         15,
    "partial_shading": 15,
}

# Ring-buffer state for partial-shading simulation
# We need 5 strictly-decreasing irradiance values sent consecutively.
_shading_sequence = []   # built up when partial_shading is chosen
_shading_index    = 0

# ── ANSI colour helpers ───────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
COLORS = {
    "normal":          "\033[92m",   # green
    "oc":              "\033[93m",   # yellow
    "sc":              "\033[95m",   # magenta
    "hotspot":         "\033[91m",   # red
    "partial_shading": "\033[94m",   # blue
}


def _make_shading_sequence():
    """Generate 5 irradiance values that strictly decrease by >5 W/m² each step."""
    start = random.randint(750, 1000)
    drops = [random.randint(6, 30) for _ in range(4)]   # 4 drops → 5 values
    values = [start]
    for d in drops:
        values.append(values[-1] - d)
    return values   # e.g. [820, 800, 780, 755, 725]


# ── Sample generators ─────────────────────────────────────────────────────────

def sample_normal():
    g = random.randint(600, 1000)
    # operating point well inside the MPP region (v_ratio ~0.7, i_ratio ~0.8)
    Voc = 0.04 * g
    Isc = 0.005 * g
    v = round(Voc * random.uniform(0.55, 0.80), 2)
    i = round(Isc * random.uniform(0.60, 0.90), 3)
    return {
        "v": v,
        "i": i,
        "g": g,
        "t": round(random.uniform(25, 54), 1),
    }


def sample_oc():
    """v_ratio > 0.9  AND  i_ratio < 0.1  →  Open Circuit"""
    g = random.randint(600, 1000)
    Voc = 0.04 * g
    Isc = 0.005 * g
    v = round(Voc * random.uniform(0.91, 0.99), 2)
    i = round(Isc * random.uniform(0.0, 0.09), 3)
    return {
        "v": v,
        "i": i,
        "g": g,
        "t": round(random.uniform(25, 54), 1),
    }


def sample_sc():
    """v_ratio < 0.1  AND  i_ratio > 0.9  →  Short Circuit"""
    g = random.randint(600, 1000)
    Voc = 0.04 * g
    Isc = 0.005 * g
    v = round(Voc * random.uniform(0.0, 0.09), 3)
    i = round(Isc * random.uniform(0.91, 1.05), 3)
    return {
        "v": v,
        "i": i,
        "g": g,
        "t": round(random.uniform(25, 54), 1),
    }


def sample_hotspot():
    """Temperature above 70 °C threshold"""
    g = random.randint(600, 1000)
    Voc = 0.04 * g
    Isc = 0.005 * g
    v = round(Voc * random.uniform(0.55, 0.80), 2)
    i = round(Isc * random.uniform(0.60, 0.90), 3)
    return {
        "v": v,
        "i": i,
        "g": g,
        "t": round(random.uniform(70.5, 95.0), 1),
    }


def sample_partial_shading():
    """
    Each call returns the next value in a strictly-decreasing irradiance
    sequence.  After 5 consecutive sends the server's ring buffer will flag
    Partial Shading.  The sequence then resets.
    """
    global _shading_sequence, _shading_index

    if _shading_index == 0 or _shading_index >= len(_shading_sequence):
        _shading_sequence = _make_shading_sequence()
        _shading_index = 0

    g = _shading_sequence[_shading_index]
    _shading_index += 1

    # Keep v/i in normal operating region so OC/SC don't shadow the shade fault
    Voc = 0.04 * g
    Isc = 0.005 * g
    v = round(Voc * random.uniform(0.55, 0.80), 2)
    i = round(Isc * random.uniform(0.60, 0.90), 3)
    return {
        "v": v,
        "i": i,
        "g": g,
        "t": round(random.uniform(25, 54), 1),
    }


# ── Dispatch table ────────────────────────────────────────────────────────────
GENERATORS = {
    "normal":          sample_normal,
    "oc":              sample_oc,
    "sc":              sample_sc,
    "hotspot":         sample_hotspot,
    "partial_shading": sample_partial_shading,
}

FAULT_NAMES = list(FAULT_WEIGHTS.keys())
WEIGHTS     = [FAULT_WEIGHTS[f] for f in FAULT_NAMES]


def pick_fault():
    return random.choices(FAULT_NAMES, weights=WEIGHTS, k=1)[0]


# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'─'*54}")
    print(f"  Solar Fault Monitor  —  ESP32 Fake Data Sender")
    print(f"  Target : {URL}")
    print(f"  Interval: {MIN_INTERVAL}–{MAX_INTERVAL} s  (random)")
    print(f"  Faults  : {', '.join(FAULT_NAMES)}")
    print(f"{'─'*54}\n")

    sample_count = 0

    while True:
        fault_type = pick_fault()
        sensor     = GENERATORS[fault_type]()

        payload = {
            "device_id": "ESP32_SIM_001",
            "samples":   [sensor],
        }

        try:
            resp     = requests.post(URL, json=payload, timeout=5)
            result   = resp.json()
            detected = result.get("prediction", {})
            color    = COLORS.get(fault_type, "")
            sample_count += 1

            print(
                f"{color}{BOLD}[#{sample_count:04d}] "
                f"SCENARIO: {fault_type.upper().replace('_',' '):<18}{RESET}"
            )
            print(
                f"  Sensors  → V={sensor['v']:>7.3f} V   "
                f"I={sensor['i']:>7.4f} A   "
                f"G={sensor['g']:>5} W/m²   "
                f"T={sensor['t']:>5.1f} °C"
            )
            print(
                f"  Detected → Status: {detected.get('fault_status','?'):<10}  "
                f"Type: {detected.get('fault_type','?')}"
            )

        except requests.exceptions.ConnectionError:
            print("  ⚠  Could not reach Flask server — is it running?")
        except Exception as e:
            print(f"  ⚠  Error: {e}")

        interval = round(random.uniform(MIN_INTERVAL, MAX_INTERVAL), 2)
        print(f"  {'─'*46}  next in {interval}s\n")
        time.sleep(interval)


if __name__ == "__main__":
    main()