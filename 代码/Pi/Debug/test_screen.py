import sys
import os
sys.path.append(os.path.abspath("/root/Pi"))

from Libraries.Hardware.Arduino_module import Arduino
from Libraries.Config import ArduinoConfig
from Libraries.Call.Builder import builder

my_arduino: Arduino = builder(Arduino, ArduinoConfig)
while True:
    text = input("请输入文本：")
    my_arduino.monitor(text)