#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>

// Sensors
#include <OneWire.h>
#include <DallasTemperature.h>
#include <BH1750.h>
#include <Adafruit_INA226.h>

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

const char* serverUrl = "http://<FLASK_IP>:5000/api/esp32/data";


const char* device_id = "ESP32_SOLAR_01";

#define ONE_WIRE_BUS 4   // DS18B20

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18b20(&oneWire);

BH1750 lightMeter;
Adafruit_INA226 ina226;

unsigned long lastSend = 0;
const unsigned long interval = 200; // 200 ms


void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);

  // I2C init
  Wire.begin(21, 22);

  // Sensors init
  ds18b20.begin();

  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("BH1750 init failed!");
  }

  if (!ina226.begin()) {
    Serial.println("INA226 init failed!");
    while (1);
  }

  ina226.setAveragingCount(INA226_AVERAGES_16);
  ina226.setConversionTime(INA226_TIME_1100_us);

  connectWiFi();
}

void loop() {
  if (millis() - lastSend >= interval) {
    lastSend = millis();

    if (WiFi.status() != WL_CONNECTED) {
      connectWiFi();
      return;
    }


    // Temperature
    ds18b20.requestTemperatures();
    float temperature = ds18b20.getTempCByIndex(0);

    // Irradiance (lux → W/m² approx)
    float lux = lightMeter.readLightLevel();
    float irradiance = lux * 0.0079;  // Approx sunlight conversion

    // INA226
    float voltage = ina226.getBusVoltage_V();   // V
    float current = ina226.getCurrent_mA() / 1000.0; // A
    float power = ina226.getPower_mW() / 1000.0;     // W

    // Timestamp (seconds)
    unsigned long timestamp = millis() / 1000;

    StaticJsonDocument<256> doc;
    doc["device_id"] = device_id;

    JsonArray samples = doc.createNestedArray("samples");
    JsonObject s = samples.createNestedObject();

    s["v"]  = voltage;
    s["i"]  = current;
    s["g"]  = irradiance;
    s["t"]  = temperature;
    s["ts"] = timestamp;

    String payload;
    serializeJson(doc, payload);

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(payload);

    Serial.println("POST Payload:");
    Serial.println(payload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response:");
      Serial.println(response);
    } else {
      Serial.print("HTTP Error: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }
}