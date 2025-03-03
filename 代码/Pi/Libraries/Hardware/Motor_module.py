from enum import Enum
from time import sleep
from abc import abstractmethod, ABCMeta
from queue import Queue
import threading
from Libraries.Hardware.Can_module import Can
from Libraries.Call.Broker import Notification


class MotorMode(Enum):
    Speed = b"\x01"
    Angle = b"\x02"
    Power = b"\x03"
    Absolute = b"\x04"


class MotorId(Enum):
    FL_Motor = b"\x01"
    FR_Motor = b"\x02"
    RL_Motor = b"\x03"
    RR_Motor = b"\x04"
    UD_Motor = b"\x05"


class MotorSegmentation(Enum):
    S2 = b"\x02"
    S4 = b"\x04"
    S8 = b"\x08"
    S16 = b"\x10"
    S32 = b"\x20"


class Motor:
    def __init__(self, can: Can, segmentation: MotorSegmentation, request_bool: bool,
                 max_speed: float, min_speed: float):
        # self._id = id.value
        self._segmentation = segmentation.value
        self._request_bool = request_bool
        self._can = can
        self._mod_check = False
        self._max_speed = max_speed
        self._min_speed = min_speed
        self._queue: Queue = Queue()
        self._Motor_lock = threading.Lock()

    def push(self):
        with self._Motor_lock:
            while not self._queue.empty():
                self._can.send(self._queue.get())

    def close(self, motor_id: MotorId):
        self._can.send(motor_id.value + b"\x01\x01" + self._segmentation + b"\x00\x00\x00\x00")

    def encode(self, motor_id: MotorId, mod: MotorMode, degree: float, speed: float):
        send_data = bytearray(motor_id.value + mod.value)
        degree = int(degree * 10)
        # 确定朝向
        toward = b'\x00' if speed < 0 else b'\x01'
        speed = abs(speed)
        # 检测速度是否过低或者过快
        speed = int(max(self._min_speed, min(speed, self._max_speed)) * 10)
        send_data.extend(toward + self._segmentation)
        send_data.extend([(degree >> 8) & 0xFF, degree & 0xFF,
                          (speed >> 8) & 0xFF, speed & 0xFF])
        self._queue.put(send_data)

    def _receive(self, motor_id: MotorId) -> (bool, float):
        with self._Motor_lock:
            state, datas_raw = self._can.request(motor_id.value)
            if state == -1:
                raise Exception(f"未能成功获取电机{motor_id}的返回值")
            check = (datas_raw[1] == 1)  # 检测是否完成任务
        return check, float((datas_raw[6] << 8) | datas_raw[7]) / 10

    def anglemod_check(self, motor_id: MotorId):
        while True:
            check, degree = self._receive(motor_id)
            if check:
                return
            sleep(0.1)

    def clear(self, motor_id: MotorId):
        self._can.send(motor_id.value + b"\x01\x01" + self._segmentation + b"\x00\x00\x00\x00")


class MotorEvent(Notification, metaclass=ABCMeta):
    def __init__(self, can: Can, motor_id: MotorId, delay: float):
        Notification.__init__(self, self.__class__.__name__)
        self._thread = None
        self._can = can
        self._id = motor_id.value
        # self._request_bool = request_bool
        self.delay = delay
        self.stop_receive_event = threading.Event()
        self.is_stopped_event = threading.Event()

    def start(self):
        self.stop_receive_event.set()
        self._thread = threading.Thread(name=self.__class__.__name__, target=self.receive)
        self._thread.start()

    def stop(self):
        self.stop_receive_event.clear()

    @abstractmethod
    def receive(self):
        pass


# 检测电机是否完成任务
class MotorReceive(MotorEvent):
    def receive(self):
        # print("MotorEvent is Ready")
        while self.stop_receive_event.is_set():
            state, datas_raw = self._can.request(self._id)
            if state == -1:
                raise Exception(f"未能成功获取电机{self._id}的返回值")
            self.notify(notice=float((datas_raw[6] << 8) | datas_raw[7]) / 10)
            sleep(self.delay)
        # print("MotorEvent is Stop")
        self.stop_receive_event.set()


# 角度模式检测是否完成任务
# class MotorAngleModCheck(MotorEvent):
#     def receive(self):
#         self._can.clear()  # 清除上次接受的残留数据(可能的话)
#         while self.stop_receive_event:
#             state, datas_raw = self._can.request(self._id)
#             # state, datas_raw = self._can.request(self._id) if self._request_bool else self._can.receive(self._id)
#             if state == -1:
#                 raise Exception(f"未能成功获取电机{self._id}的返回值")
#             check = (datas_raw[1] == 1)
#             if check:
#                 self.notify(check)
#                 self.stop()
#             sleep(self.delay)
