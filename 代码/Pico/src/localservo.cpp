#include <Arduino.h>
#include <Servo.h>
#include "localservo.h"

namespace localservo
{
  bool MyServo::check_pos(int degree)
  {
    if (degree > 180) return false;
    return true;
  }
  void MyServo::pos_delay(int pos, int pos_old)
  {
    int delay_pos = abs(pos - pos_old);
    if (delay_pos != 0) delay(delay_pos * delay_coefficient);
  }

  MyServo::MyServo(int pin, int min_frequency, int max_frequency, long delay_coe, int degree)
  {
    o_pin = pin;
    o_min_frequency = min_frequency;
    o_max_frequency = max_frequency;
    o_degree = degree;
    delay_coefficient = delay_coe;
  }

  void MyServo::setup()
  {
    my_servo.attach(o_pin, o_min_frequency, o_max_frequency);
    my_servo.write(o_degree);
  }

  bool MyServo::set(int degree, bool is_block)
  {
    if (not check_pos(degree)) return false;
    int pos_old = my_servo.read();
    my_servo.write(degree);
    if (is_block) pos_delay(degree, pos_old);
    return true;
  }
  MyServo My_Hand(2, Min_Frequency, Max_Frequency, Delay_coe, Hand_Degree);
  MyServo My_Arm(3, Min_Frequency, Max_Frequency, Delay_coe, Arm_Degree);
  MyServo My_Plate(4, Min_Frequency, Max_Frequency, Delay_coe, Plate_Degree);
  MyServo *My_Motor[] = {&My_Hand, &My_Arm, &My_Plate};

  void setup()
  {
    My_Hand.setup();
    My_Arm.setup();
    My_Plate.setup();
    // My_Plate.my_servo.write(50);
    // delay(2000);
    //  My_Plate.my_servo.write(0);
  }

  void update(int index, int value, bool is_block)
  {
    My_Motor[index]->set(value, is_block);
    // My_Plate.my_servo.write(value);
  }
};