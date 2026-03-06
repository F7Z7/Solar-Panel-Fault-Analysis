#include <Wire.h>
#include <BH1750.h>

BH1750 lightMeter;

void setup(){
  Serial.begin(115200);
  Wire.begin(21,22);

  lightMeter.begin();
  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("BH1750 not found!");
    while (1);
  }

  Serial.println("BH1750 Ready");
}
void loop(){
  float lux = lightMeter.readLightLevel();

  float irr= lux*.0079
  Serial.print("Irradiance = : ");
  Serial.print(irr);
}