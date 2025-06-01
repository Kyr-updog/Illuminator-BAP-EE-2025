#include <Adafruit_NeoPixel.h>
#include "DigiCDC.h"
#include "EEPROM.h"

#define LED_PIN 0   // WS2812B Data Line on PB0 (Pin 0)
#define LED_COUNT 20 // Number of LEDs
#define ID 1 //the ID of the attiny
#define DUMMY 1 //1 is dummy, 2 is controller

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

uint16_t animationSpeed = 0;  // Default speed, max 65535
uint8_t direction = 0;
uint8_t r = 10;
uint8_t g = 10;
uint8_t b = 10;
uint8_t i = 0, j = 1;

void setup() {
  SerialUSB.begin();  // Initialize USB Serial
  strip.begin();
  strip.show();

  //ID = EEPROM.read(0);
  //delay(2000);
  //SerialUSB.write(ID);
}

void loop() {
  requestSpeedFromPi();  // Ask Raspberry Pi for speed
  if (j == 1){
    cyanFlowAnimation(animationSpeed, r, g, b, direction);  // Run animation
  }
}

void requestSpeedFromPi() {
    if (SerialUSB.available()) {
      switch (j){
        case 1:
          animationSpeed = SerialUSB.read();
          SerialUSB.write(j);
          j++;
          break;
        case 2: 
          direction = SerialUSB.read();
          SerialUSB.write(j);
          j++;
          break;
        case 3:
          r = SerialUSB.read();
          SerialUSB.write(j);
          j++;
          break;
        case 4: 
          g = SerialUSB.read();
          SerialUSB.write(j);
          j++;
          break;
        case 5:
          b = SerialUSB.read();
          SerialUSB.write(j);
          j = 1;
          SerialUSB.write(ID);
          SerialUSB.write(DUMMY);
          break;
      }
    }
    else{
      //SerialUSB.refresh();
    }
}

 // Cyan Flow Animation with dynamic speed
 void cyanFlowAnimation(int wait, uint8_t r, uint8_t g, uint8_t b, bool direction) {

  if (wait == 0){
    for (uint8_t pos=0; pos < LED_COUNT; pos++){
      strip.setPixelColor(pos, strip.Color(r, g, b));
    }
    strip.show();
    SerialUSB.delay(10);
    return;
  }
  

  int pos = 0;
  if (direction == 0){
    pos = LED_COUNT - i - 1;
    }
  else{
    pos = i;
  }
  strip.clear();
  strip.setPixelColor(pos, strip.Color(r, g, b));  // Cyan color
  strip.show();
  SerialUSB.delay(wait);

  i++;
  if (i > LED_COUNT){
    i = 0;
  }
}