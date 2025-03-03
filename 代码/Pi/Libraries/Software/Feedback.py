import time
from abc import abstractmethod, ABCMeta
from threading import Event, Lock
from typing import TYPE_CHECKING
from Libraries.Call import Broker, Stream
from Libraries.Call.Handle import Handle
from Libraries.Hardware.Camera_module import Camera
from Libraries.Hardware.Gyro_module import Gyro
from Libraries.Hardware.Motor_module import MotorReceive

if TYPE_CHECKING:
    from Libraries.Software.Control import ControlWalk, ControlTurn, ControlCreep
    from Libraries.Software.Calculate import CalculateWalk, CalculateTurn, CalculateCreep


class Feedback(Handle, metaclass=ABCMeta):
    def __init__(self):
        self.next_cal = None
        self.next_control = None
        self.dev = 0.1

    @abstractmethod
    def set_next(self, *args, **kwargs):
        pass

    @abstractmethod
    def set(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class FeedbackWalk(Feedback, Broker.Observer):
    def __init__(self, motor_receive: MotorReceive, gyro: Gyro, camera: Camera):
        Feedback.__init__(self)
        Broker.Observer.__init__(self)
        self.motor_receive = motor_receive
        self.gyro = gyro
        self.camera = camera
        self._Yaw = 0
        self.walk_degree_hope = None
        self.degree_now = None
        self.update_event = Event()  # 更新事件的标志
        self.stop_event = Event()  # 停止时间的标志
        self.stop_lock = Lock()  # 停止任务的锁
        self.is_stopped_event = Event()  # 是否停止完成的标志

    def set_next(self, next_cal, next_control):
        self.next_cal: CalculateWalk = next_cal
        self.next_control: ControlWalk = next_control

    def update(self, name, notice):
        if self.update_event.is_set():
            if name == self.motor_receive.__class__.__name__:
                if notice >= self.walk_degree_hope:
                    if not self.stop_event.is_set():
                        self.stop_event.set()
                        self.stop()
                    return
                self.next_cal.current_degree = notice
                self.next_cal.update_event.set()
            match name:
                case self.gyro.__class__.__name__:
                    if notice.Yaw is not None:
                        # 判断新获取的yaw角和旧yaw角是否在偏差值内，超出偏差值就更新
                        if abs(notice.Yaw - self._Yaw) < self.dev:
                            self.next_cal.yaw = notice.Yaw
                            self.next_cal.update_event.set()
                            return
                        else:
                            self._Yaw = notice.Yaw
                    else:
                        return
                case self.camera.__class__.__name__:
                    self.next_cal.frame = notice
                    self.next_cal.update_event.set()

    def set(self, walk_degree_hope):
        self.update_event.clear()
        self.stop_event.clear()
        self.walk_degree_hope = walk_degree_hope
        self.degree_now = 0
        self.start()

    def start(self):
        self.attach(self.gyro)
        self.attach(self.motor_receive)
        self.attach(self.camera)
        while self.next_cal.frame is None:
            if self.camera.frame is not None:
                self.next_cal.frame = self.camera.frame.copy()
            time.sleep(0.1)
        self.update_event.set()
        self.next_cal.update_event.clear()
        self.next_cal.stop_update_event.set()

    def stop(self):
        self.next_control.stop()
        self.next_cal.stop()
        self.update_event.clear()
        self.detach(self.motor_receive)
        self.detach(self.gyro)
        self.detach(self.camera)
        # print("FeedbackWalk is stopped")
        self.is_stopped_event.set()


class FeedbackTurn(Feedback, Stream.StreamOut):
    def __init__(self, gyro: Gyro):
        super().__init__()
        self.gyro = gyro

    def set_next(self, next_cal, next_control):
        self.next_cal: CalculateTurn = next_cal
        self.next_control: ControlTurn = next_control

    def set(self):
        self.bind(self.gyro)

    def stop(self):
        self.unbind()

    def update(self):
        while True:
            yaw = self.get().Yaw
            if yaw is not None:
                return yaw


class FeedbackCreep(Feedback):
    def set(self):
        pass

    def set_next(self, next_cal, next_control):
        self.next_cal: CalculateCreep = next_cal
        self.next_control: ControlCreep = next_control

    def start(self):
        pass

    def stop(self):
        pass

    def update(self):
        pass
