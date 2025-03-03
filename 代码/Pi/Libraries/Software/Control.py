from __future__ import annotations
import numpy as np
import logging
from abc import abstractmethod, ABCMeta
from time import sleep
from typing import TYPE_CHECKING
from threading import Lock, Event
from Libraries.Call.Handle import Handle
from Libraries.Hardware.Motor_module import Motor, MotorId, MotorMode

if TYPE_CHECKING:
    from Libraries.Software.Calculate import CalculateWalk, CalculateTurn, CalculateCreep, CalculateTurnMode

logger = logging.getLogger(__name__)


class Control(Handle, metaclass=ABCMeta):
    def __init__(self, motor: Motor):
        self.motor = motor
        self.speed_rad_arr = None
        self.next_cal = None

    def encode_and_push(self, mode: MotorMode, degree: float, speed_rad_arr: np.ndarray):
        if speed_rad_arr is not None:
            self.motor.encode(MotorId.FL_Motor, mode, degree, +speed_rad_arr[0])
            self.motor.encode(MotorId.RR_Motor, mode, degree, -speed_rad_arr[3])
            self.motor.encode(MotorId.FR_Motor, mode, degree, -speed_rad_arr[1])
            self.motor.encode(MotorId.RL_Motor, mode, degree, +speed_rad_arr[2])
            self.motor.push()

    def clear_motor(self):
        self.motor.clear(MotorId.FL_Motor)
        self.motor.clear(MotorId.FR_Motor)
        self.motor.clear(MotorId.RL_Motor)
        self.motor.clear(MotorId.RR_Motor)

    def close_motor(self):
        self.motor.close(MotorId.FL_Motor)
        self.motor.close(MotorId.FR_Motor)
        self.motor.close(MotorId.RL_Motor)
        self.motor.close(MotorId.RR_Motor)

    @abstractmethod
    def set_next(self, *args, **kwargs):
        pass

    @abstractmethod
    def set(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class ControlWalk(Control):
    def __init__(self, motor: Motor):
        super().__init__(motor)
        self.control_lock = Lock()
        self.run_wait = Event()  # 等待数据更新，数据更新就重新发送数据
        self.is_finished = False  # 运行是否完成
        self.is_stopped_event = Event()

    def set_next(self, next_cal: CalculateWalk):
        self.next_cal: CalculateWalk = next_cal

    def set(self, x, y, speed_coe: float):
        self.next_cal.set(x, y, speed_coe)
        self.run_wait.clear()

    def update(self, speed_rad_arr):
        with self.control_lock:
            self.speed_rad_arr = speed_rad_arr
            self.run_wait.set()

    def stop(self):
        self.is_finished = False
        self.run_wait.set()

    def run(self, x, y, speed_coe: float):
        self.is_finished = True
        self.clear_motor()
        self.set(x, y, speed_coe)
        while self.is_finished:
            self.encode_and_push(MotorMode.Speed, 0, self.speed_rad_arr)
            self.run_wait.wait()
            self.run_wait.clear()
        self.close_motor()
        # print("ControlWalk Stop")
        self.is_stopped_event.set()


class ControlTurn(Control):
    def __init__(self, motor: Motor):
        super().__init__(motor)
        self.wheel_degree = None

    def set_next(self, next_cal: CalculateTurn):
        self.next_cal: CalculateTurn = next_cal

    def set(self, turn_degree: float, car_speed: float, turn_mod: CalculateTurnMode):
        self.clear_motor()
        self.next_cal.set(turn_degree, car_speed, turn_mod)

    def update(self, speed_rad_arr, wheel_degree):
        self.encode_and_push(MotorMode.Angle, wheel_degree, speed_rad_arr)
        self.motor.anglemod_check(MotorId.FL_Motor)
        # print("motor OK")

    def stop(self):
        pass

    def run(self, turn_degree: float, car_speed, turn_mode: CalculateTurnMode, correct_times=3):
        self.set(turn_degree, car_speed, turn_mode)
        for i in range(correct_times):
            sleep(0.2)
            logger.info(f"第{i+1}次旋转校正")
            if self.next_cal.update():
                break
        self.next_cal.stop()
        # print("turn ok")


class ControlCreep(Control):
    def __init__(self, motor: Motor):
        super().__init__(motor)

    def set_next(self, next_cal: CalculateCreep):
        self.next_cal: CalculateCreep = next_cal

    def set(self, x, y, speed_coe):
        self.next_cal.set(x, y, speed_coe)

    def update(self, speed_rad_x, degree_x, speed_rad_y, degree_y):
        # x方向移动
        self.encode_and_push(MotorMode.Angle, degree_x, speed_rad_x)
        self.motor.anglemod_check(MotorId.FL_Motor)

        # y方向移动
        self.encode_and_push(MotorMode.Angle, degree_y, speed_rad_y)
        self.motor.anglemod_check(MotorId.FL_Motor)

    def stop(self):
        pass

    def run(self, x, y, speed_coe):
        self.set(x, y, speed_coe)
        # print("creep ok")
