#include <Arduino.h>
#include <Servo.h>
#include <FreeRTOS.h>
#include "com.h"
#include "localservo.h"
#include "light.h"
#include "screen.h"
#include "task.h"

// Servo test;
void setup()
{
  // test.attach(4);
  // test.write(170);
  light::setup();
  localservo::setup();
  com_module::setup();
  screen::setup();
  screen::set("No Task");

  xTaskCreateAffinitySet([](void *param)
                         {while(true) com_module::update(); }, "com", 4096, nullptr, 6, 1 << 0, nullptr);
  xTaskCreateAffinitySet([](void *param)
                         {while(true) screen::update(); }, "screen", 4096, nullptr, 6, 1 << 0, nullptr);
}
int start=0;
void loop()
{
  // while(true){
  //   delay(100);
  //   localservo::update(2, start++);
  //   start%=90;
  // }
}