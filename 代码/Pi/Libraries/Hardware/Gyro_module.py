from time import sleep
from types import SimpleNamespace
import serial
import threading
from Libraries.Call.Broker import Notification
from Libraries.Call.Stream import StreamIn
import logging


logger = logging.getLogger(__name__)

"""
编辑者：单晨峰
编辑时间：24/11/28
修改类型：提供绝对YAW接口
"""
class Gyro(Notification, StreamIn):
    def __init__(self, interface: str, baud_rate: int, delay: float):
        Notification.__init__(self, self.__class__.__name__)
        StreamIn.__init__(self)
        self._ser = serial.Serial(interface, baud_rate)
        self.delay = delay
        if not self._ser.is_open:
            raise Exception("陀螺仪串口打开失败")
        self.AZ = None
        self.AY = None
        self.Yaw = None
        self.update_event: threading.Event = threading.Event()
        self._thread = None
        self.is_stopped_event: threading.Event = threading.Event()

    def update(self) -> None:
        logger.debug("陀螺仪启动")
        while self.update_event.is_set():
            datas = self.getdata()
            match datas[0]:
                case 82:
                    self.AY = ((datas[4] << 8) | datas[3]) / 32768.0 * 2000.0
                    self.AZ = ((datas[6] << 8) | datas[5]) / 32768.0 * 2000.0
                case 83:
                    Yaw = ((datas[6] << 8) | datas[5]) / 32768.0 * 180.0
                    if Yaw >= 180:
                        Yaw -= 360
                    logger.debug(f'当前陀螺仪的返回值是: {Yaw}')
                    self.Yaw = Yaw
            notice = SimpleNamespace()
            notice.AY = self.AY
            notice.AZ = self.AZ
            notice.Yaw = self.Yaw
            self.notify(notice)
            sleep(self.delay)
        logger.debug("陀螺仪停止")
        self.is_stopped_event.set()

    def getdata(self) -> bytes:  # 获取陀螺仪的返回数据
        state = -1
        while True:
            match state:
                case -1:  # 检测是否是帧头
                    head = self._ser.read()[0]
                    state = 0 if head == 85 else state
                case 0:  # 读取内容
                    datas = self._ser.read(10)
                    sum_me = 0x55 + sum(datas[:-2])
                    if (sum_me & 0xFF) == datas[-1]:
                        return datas
                    else:
                        state = -1
                    sleep(self.delay)

    def start(self):
        self.AZ = None
        self.AY = None
        self.Yaw = None
        self.update_event.set()
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        self._thread = threading.Thread(name=self.__class__.__name__, target=self.update)
        self._thread.start()

    def stop(self):
        self.update_event.clear()

    def put(self) -> SimpleNamespace:
        stream = SimpleNamespace()
        stream.AY = self.AY
        stream.AZ = self.AZ
        stream.Yaw = self.Yaw
        return stream

    def set_absolute_yaw(self) -> float:
        self.start()
        sleep(self.delay * 5)  # 前几个包有波动
        absolute_yaw = self.Yaw
        self.stop()
        self.is_stopped_event.wait()
        self.is_stopped_event.clear()
        return absolute_yaw

            



        
        