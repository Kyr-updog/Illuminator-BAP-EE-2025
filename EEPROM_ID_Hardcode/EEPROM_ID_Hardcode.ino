#include "EEPROM.h"

uint8_t ID;

void setup() {
  ID = 1;  //type the ID number for current pair here. List of used IDs: 1, ...
  EEPROM.write(0, ID);
}

void loop(){}
