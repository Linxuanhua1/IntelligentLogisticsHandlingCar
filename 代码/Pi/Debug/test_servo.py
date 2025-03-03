import sys
import os
sys.path.append(os.path.abspath("/root/Pi"))

from Libraries.Hardware.Arduino_module import Arduino
from Libraries.Config import ArduinoConfig
from Libraries.Call.Builder import builder

my_arduino: Arduino = builder(Arduino, ArduinoConfig)
while True:
    degree = int(input("请输入角度："))
    my_arduino.servo(1, degree, is_block=False)

