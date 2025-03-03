import sys
import os
sys.path.append(os.path.abspath("/root/Pi"))

from Libraries.Config import CanConfig
from Libraries.Hardware.Can_module import Can
from Libraries.Call import Builder
from time import sleep

test_can = Builder.builder(Can, CanConfig)

test_can.send(b'\x03\x01\x01\x20\x00\x00\x00\x64')
sleep(5)
test_can.send(b'\x03\x01\x01\x20\x00\x00\x00\x00')
