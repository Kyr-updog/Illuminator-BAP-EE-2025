#include <Adafruit_NeoPixel.h>
#include "DigiCDC.h"
#include "EEPROM.h"

#define LED_PIN 0   // WS2812B Data Line on PB0 (Pin 0)
#define LED_COUNT 20 // Number of LEDs

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

uint16_t animationSpeed = 0;  // Default speed, max 65535
bool direction = 0;
uint8_t r = 10;
uint8_t g = 10;
uint8_t b = 10;
uint8_t i = 0;
uint8_t ID;

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
  cyanFlowAnimation(animationSpeed, r, g, b, direction);  // Run animation
}

void requestSpeedFromPi() {
    if (SerialUSB.available()) {
        while (SerialUSB.available()) 
        {
          //animationSpeed = SerialUSB.read(); //max X*255, so X_max=65535/255=257, in 128 steps
          animationSpeed << 8;  
          animationSpeed = animationSpeed | SerialUSB.read();
          direction = SerialUSB.read() && 1;
          r = SerialUSB.read();
          g = SerialUSB.read();
          b = SerialUSB.read();
        }
      ID = EEPROM.read(0);
      SerialUSB.write(ID);
    }
    else{
      SerialUSB.refresh();
    }
    SerialUSB.delay(10);
}

 // Cyan Flow Animation with dynamic speed
 void cyanFlowAnimation(int wait, uint8_t r, uint8_t g, uint8_t b, bool direction) {

if (wait == 0){
    for (uint8_t pos=0; pos < LED_COUNT; pos++){
      strip.setPixelColor(pos, strip.Color(r, g, b));
    }
    strip.show();
    delay(10);
    return;
  }
  
  for (int i = 0; i < LED_COUNT; i++){
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
    delay(wait);
  }

  i++;
  if (i > LED_COUNT){
    i = 0;
  }
}