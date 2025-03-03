#include <Arduino.h>
#define TJC Serial2
namespace screen
{
  char str[100];
  void setup()
  {
    TJC.setRX(9);
    TJC.setTX(8);
    TJC.begin(9600);
    while (TJC.read() >= 0);
  }

  void set(char* txt) {
    sprintf(str, "t0.txt=\"%s\"\xff\xff\xff", txt);
    TJC.print(str);
    // Serial1.print(str);
  }

  void update()
  {
    while (TJC.read() >= 0);
    // delay(100);
    // int val = rand() % 100000;
    // sprintf(str, "t0.txt=\"%06d\"\xff\xff\xff", val);
    // TJC.print(str);
  }
}

// http://wiki2.tjc1688.com/debug/arduino/raspberrypi_pico.html
// https://arduino-pico.readthedocs.io/en/latest/freertos.html
// https://github.com/porrey/Pico-MultiCore/blob/main/Pico_MultiCore/Pico_MultiCore.ino
// https://www.raspberrypi.com/documentation/pico-sdk/high_level.html#group_multicore_fifo