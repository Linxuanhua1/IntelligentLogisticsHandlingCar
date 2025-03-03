#include <Arduino.h>

namespace light {
  void setup(){
    pinMode(5, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);
    
    
  }
  void update(int value) {
    analogWrite(5, value);
    analogWrite(LED_BUILTIN, value);
    // Serial1.println(value);
  }
}