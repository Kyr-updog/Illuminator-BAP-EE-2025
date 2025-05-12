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
uint8_t i = 0, j = 0;
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
      SerialUSB.write(85);
        switch (j){
          case 0:
            animationSpeed = SerialUSB.read(); 
            //animationSpeed << 8;  
            //animationSpeed = animationSpeed | SerialUSB.read();
            SerialUSB.write(animationSpeed);
            j++;
            break;
          case 1: 
            direction = SerialUSB.read() && 1;
            SerialUSB.write(direction);
            j++;
            break;
          case 2: 
            r = SerialUSB.read();
            SerialUSB.write(r);
            j++;
            break;
          case 3:
            g = SerialUSB.read();
            SerialUSB.write(g);
            j++;
            break;
          case 4:
            b = SerialUSB.read();
            SerialUSB.write(b);
            j = 0;
            break;
          default:
          j = 0;
          animationSpeed = 0;
          direction = 0;
          r = 10;
          g = 10;
          b = 10;
          break;
        }
      //ID = EEPROM.read(0);
      //SerialUSB.write(ID);
    }
    else{
      //SerialUSB.refresh();
      SerialUSB.write(6);
    }
    //SerialUSB.delay(10);
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
