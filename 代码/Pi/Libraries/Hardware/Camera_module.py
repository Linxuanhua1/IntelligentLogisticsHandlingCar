import cv2
import threading
import time
import numpy as np
from Libraries.Call.Broker import Notification
from Libraries.Call import Builder
from Libraries.Call.Stream import StreamIn
import queue
import logging


logger = logging.getLogger(__name__)


class Camera(Notification, StreamIn, Builder.Parameter):
    def __init__(self, src: str, camera_name: str):
        Notification.__init__(self, self.__class__.__name__)
        StreamIn.__init__(self)
        self.is_rotated: bool = None  # 视频帧旋转角度
        self.is_sender: bool = None  # 是否传回电脑
        self.thread: threading.Thread = None  # 线程
        self.camera_name: str = camera_name  # 摄像头名字
        self.src: str = src  # 视频源
        self.start_update_event: threading.Event = threading.Event()  # 关闭更新事件
        self.is_stopped_event: threading.Event = threading.Event()  # 设备关闭事件
        self.cap: cv2.VideoCapture = None  # 摄像头对象
        self.frame: np.ndarray = None  # 视频帧
        self.data_queue: queue.Queue = None  # socket用队列

    def set_queue(self, data_queue: queue.Queue):
        self.data_queue = data_queue
        # 这里有个更优雅的写法，直接让这个函数从父函数继承就行，但是我懒得改了
    
    def set_parameter(self, is_rotated: bool, is_sender: bool = False):
        self.is_sender = is_sender
        self.is_rotated = is_rotated
    
    def _rotate_frame(self):
        if self.is_rotated:
            self.frame = cv2.rotate(self.frame, cv2.ROTATE_180)
            
    def update(self):
        while self.start_update_event.is_set():
            self.cap.grab()
            ret, self.frame = self.cap.read()
            if ret and self.frame is not None:
                self._rotate_frame()
                b, g, r = cv2.split(self.frame)
                g = cv2.subtract(g, 30)  # 减少绿色通道的值
                r = cv2.subtract(r, 10)  # 减少红色通道的值
                b = cv2.subtract(b, 10)  # 减少蓝色通道的值
                # 合并通道
                self.frame = cv2.merge((b, g, r))
                if self.is_sender:
                    self.data_queue.put(self.frame)
                self.notify(self.frame.copy())
                time.sleep(0.03)
            else:
                logger.info(f"没有获取到摄像头{self.camera_name}的视频帧")
        self.is_stopped_event.set()

    def open(self):
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 0)  # 默认亮度
        self.cap.set(cv2.CAP_PROP_CONTRAST, 32)  # 默认对比度
        self.cap.set(cv2.CAP_PROP_SATURATION, 64)  # 默认饱和度
        self.cap.set(cv2.CAP_PROP_HUE, 0)  # 默认色调
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)  # 关闭自动白平衡
        self.cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 3800)  # 设置手动白平衡，默认值4600
        self.cap.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))  # 设置读取格式为MJPEG
        logger.info(f"{self.camera_name}: {self.cap.isOpened()}")

    def put(self):
        return self.frame.copy()

    def start(self):
        self.thread = threading.Thread(name=f'{self.camera_name}', target=self.update, args=())
        if self.cap.isOpened():
            # 预先读取几次
            while self.frame is None:
                ret, self.frame = self.cap.read()
                time.sleep(0.1)
        else:
            raise Exception(f'摄像头{self.camera_name}未能成功打开')
        # print(f"{self.camera_name} is ready")
        self.start_update_event.set()  # 开始更新事件激活
        self.thread.start()  # 启动

    def stop(self):
        self.start_update_event.clear()  # 开始更新事件关闭
        self.frame = None

    def close(self):  # 关闭摄像头
        if self.cap is not None:
            self.cap.release()
        # print(f"{self.camera_name} is closed")
