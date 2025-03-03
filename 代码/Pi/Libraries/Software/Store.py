from __future__ import annotations
from abc import abstractmethod, ABCMeta
import logging
import functools
from typing import TYPE_CHECKING
from Libraries.Hardware.Motor_module import *
from Libraries.Method.Image_reco import Color
if TYPE_CHECKING:
    from Libraries.Hardware.Arduino_module import Arduino

logger = logging.getLogger(__name__)


class StoreDevice(metaclass=ABCMeta):
    @abstractmethod
    def set_parameter(self, *args, **kwargs):
        pass

    @abstractmethod
    def set(self, *args, **kwargs):
        pass


class Lift(StoreDevice):
    def __init__(self, motor: Motor, motor_id: MotorId):
        self.motor = motor
        self.id = motor_id
        self.plate_degree = None
        self.rail_len = None
        self.speed = None

    def set_parameter(self, speed: float, plate_degree: float, rail_len: float, reverse: bool):
        self.plate_degree = plate_degree
        self.rail_len = rail_len
        self.speed = -speed if reverse else speed

    def _limit(self, degree: float):
        if abs(degree) > self.rail_len:
            logger.error("移动角度超过导轨长度，请重新输入")
            return False
        return True

    def set(self, degree):
        if not self._limit(degree):
            return False
        speed = self.speed
        if degree < 0:
            degree = -degree
            speed = -self.speed

        self.motor.encode(self.id, MotorMode.Angle, degree, speed)
        self.motor.push()
        self.motor.anglemod_check(self.id)
        return True

    def down2plate(self, reversal: bool = False):
        if reversal:
            self.motor.encode(self.id, MotorMode.Angle, self.plate_degree, -self.speed)
        else:
            self.motor.encode(self.id, MotorMode.Angle, self.plate_degree, self.speed)
        self.motor.push()
        self.motor.anglemod_check(self.id)
        return True


class Plate(StoreDevice):
    def __init__(self, control: Arduino, plate_id: int):
        self.control: Arduino = control
        self.id = plate_id
        self.location = None

    def set_parameter(self, location: list[int]):
        self.location = location

    def set(self, get_color: Color, is_block: bool = False):
        return self.control.servo(self.id, self.location[get_color], is_block)


class Other(StoreDevice):
    def __init__(self, control: Arduino, steer_id: int):
        self.control: Arduino = control
        self.id = steer_id
        self.off = None
        self.on = None

    def set_parameter(self, off: int, on: int):
        self.off = off
        self.on = on

    def set(self, flag: bool, is_block: bool = True):
        degree = self.on if flag else self.off
        return self.control.servo(self.id, degree, is_block)


class Store:
    def __init__(self, my_hand: Other, my_arm: Other, my_lift: Lift, my_plate: Plate):
        self.hand: Other = my_hand
        self.arm: Other = my_arm
        self.lift: Lift = my_lift
        self.plate: Plate = my_plate
    #     self._motorFlag: bool = True
    #     self.hand.set = self._motor_check(self.hand.set)
    #     self.arm.set = self._motor_check(self.arm.set)
    #     self.lift.set = self._motor_check(self.lift.set)
    #     self.plate.set = self._motor_check(self.plate.set)
    #     self.lift.down2plate = self._motor_check(self.lift.down2plate)
    #
    # def _motor_check(self, func):
    #     @functools.wraps(func)
    #     def wrapper(*args, **kwargs):
    #         if not self._motorFlag:
    #             logger.error("任务出错：" + func.__name__)
    #             self._motorFlag = False
    #             return
    #         self._motorFlag = func(*args, **kwargs)
    #     return wrapper

    def ready_get(self, degree, get_color: Color):
        self.hand.set(False)  # 打开抓取臂
        self.arm.set(True)  # 升降机构朝外
        self.lift.set(degree)  # 抓取机构下降
        self.plate.set(get_color)  # 物料盘转到指定物料

    def get(self, degree: float):
        """
        :param degree: 拿取距离（或高度）
        """
        self.hand.set(True)  # 关闭抓取臂
        self.lift.set(-degree)  # 抓取机构上升
        self.arm.set(False)  # 升降机构朝内
        self.lift.down2plate(reversal=False)  # 抓取机构下降
        self.hand.set(False)  # 打开抓取臂
        self.lift.down2plate(reversal=True)  # 抓取机构上升
        self.arm.set(True)  # 升降机构朝外

    def put(self, degree: float, put_color: Color):
        """
        :param degree: 放置距离（或高度）
        :param put_color: 托盘物品槽编号
        """
        self.plate.set(put_color)  # 物料盘转到指定物料
        self.hand.set(False)  # 打开抓取臂
        self.arm.set(False)  # 升降机构朝内
        self.lift.down2plate(reversal=False)  # 抓取机构下降到料盘
        self.hand.set(True)  # 关闭抓取臂
        self.lift.down2plate(reversal=True)  # 抓取机构上升
        self.arm.set(True)  # 升降机构朝外
        self.lift.set(degree)  # 抓取机构下降
        self.hand.set(False)  # 打开抓取臂
        self.lift.set(-degree)  # 抓取机构上升

    