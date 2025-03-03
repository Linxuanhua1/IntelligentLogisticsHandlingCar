import sys
import os
sys.path.append(os.path.abspath("/root/Pi"))
from Libraries.Car import *
from Libraries.Method.Image_reco import Color


def test_rail_len(car):
    global flag
    if flag:
        car.my_store_arm.set(True)
        car.my_store_hand.set(False)
        flag = False
    test_degree = int(input("输入下降角度："))
    car.my_store.lift.set(test_degree)  # 抓取机构下降


def test_plate_degree(car):
    global flag
    if flag:
        car.my_store_hand.set(False)
        car.my_store_arm.set(False)
        car.my_store.plate.set(Color.RED)
        flag = False
    test_degree = int(input("输入下降角度："))
    car.my_store.lift.set(test_degree)  # 抓取机构下降


def test_heap_degree(car):
    global flag
    if flag:
        car.my_store_plate.set(Color.RED)  # 物料盘转到指定物料
        car.my_store_hand.set(False)  # 打开抓取臂
        car.my_store_arm.set(False)  # 升降机构朝内
        car.my_store_lift.down2plate(reversal=False)  # 抓取机构下降到料盘
        car.my_store_hand.set(True)  # 关闭抓取臂
        car.my_store_lift.down2plate(reversal=True)  # 抓取机构上升
        car.my_store_arm.set(True)
        flag = False
    test_degree = int(input("输入下降角度："))
    car.my_store.lift.set(test_degree)  # 抓取机构下降


flag = True
mode = input('请输入测试模式(1为导轨长度测试，2为抓取机构下降到料盘的角度，3为堆垛高度):')
Test_Car = Car()
while True:
    if mode == '1':
        test_rail_len(Test_Car)
    elif mode == '2':
        test_plate_degree(Test_Car)
    elif mode == '3':
        test_heap_degree(Test_Car)
    else:
        print("输入错误，请重新输入")
        mode = input('请输入测试模式(1为导轨长度测试，2为抓取机构下降到料盘的角度):')
