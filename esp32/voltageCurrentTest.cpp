#include <Wire.h>
#include <Adafruit_INA226.h>

Adafruit_INA226 INA226;

void setup()
    {
    Serial.begin(115200);
    Wire.begin(21,22); //SDA AND SCL
    if (!ina226.begin()) {
        Serial.println("INA226 not found!");
        while (1);
    }

    Serial.println("INA226 Ready");
    }

    void loop()
        {
    Serial.print("Voltage: ");
    Serial.print(voltage);
    Serial.print("Current: ");
    Serial.print(current);
    Serial.print(" Power: ");
    Serial.print(power);
    Serial.println(" W");

    delay(1000);
        }