#include <Servo.h>

#define Min_Frequency 500
#define Max_Frequency 2500
#define Delay_coe 15
#define Hand_Degree 130
#define Arm_Degree 10
#define Plate_Degree 0

namespace localservo
{
  class MyServo
  {
  public:
    long delay_coefficient; // 舵机等待系数
    int o_pin;           // 针脚
    int o_min_frequency; // 最小脉宽
    int o_max_frequency; // 最大脉宽
    int o_degree;        // 初始角度
    Servo my_servo;      // 添加Arduino Servo模块的实例
  private:
    bool check_pos(int degree);
    void pos_delay(int pos, int pos_old);

  public:
    MyServo(int pin, int min_frequency, int max_frequency, long delay_coe, int degree);
    bool set(int degree, bool is_block);
    void setup();
  };

  void setup();
  void update(int index, int value, bool is_block);
}