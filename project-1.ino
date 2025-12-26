#include "Wire.h"
#include "Adafruit_TCS34725.h"

Adafruit_TCS34725 tcs = Adafruit_TCS34725(
  TCS34725_INTEGRATIONTIME_600MS, 
  TCS34725_GAIN_1X
);

int redPin = 4;
int greenPin = 15;
int bluePin = 16;
int sensorLedPin = 17;

void setup() {
  Serial.begin(9600);

  if (tcs.begin()) {
    Serial.println("Found sensor");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }
  pinMode(sensorLedPin, OUTPUT);
  digitalWrite(sensorLedPin, LOW);
}

void loop() {
  int color;

  Serial.println("Choose color:");
  Serial.println("Red(1), Green(2), Purple(3), White(4)");

  while (Serial.available() == 0) {}
  color = Serial.parseInt();
  clearSerialBuffer();

  switch(color) {
    case 1: setColor(255, 0, 0); break;
    case 2: setColor(0, 255, 0); break;
    case 3: setColor(170, 0, 255); break;
    case 4: setColor(255, 255, 255); break;
    default: setColor(111, 255, 233); break;
  }

  Serial.println("Measuring color sensor values... (type any key to stop)");

  while (true) {
    if (Serial.available() > 0) {
      clearSerialBuffer();
      break;
    }

    uint16_t r, g, b, c;
    uint16_t colorTemp, lux;

    tcs.getRawData(&r, &g, &b, &c);
    colorTemp = tcs.calculateColorTemperature(r, g, b);
    lux = tcs.calculateLux(r, g, b);

    Serial.print("Color Temp: "); Serial.print(colorTemp); Serial.print(" K - ");
    Serial.print("Lux: "); Serial.print(lux); Serial.print(" - ");
    Serial.print("R: "); Serial.print(r); Serial.print(" ");
    Serial.print("G: "); Serial.print(g); Serial.print(" ");
    Serial.print("B: "); Serial.print(b); Serial.print(" ");
    Serial.print("C: "); Serial.println(c);

    delay(2000);
  }
}

void setColor(int redValue, int greenValue, int blueValue) {
  analogWrite(redPin, redValue);
  analogWrite(greenPin, greenValue);
  analogWrite(bluePin, blueValue);
}

void clearSerialBuffer() {
  while (Serial.available() > 0) {
    Serial.read();
  }
}



