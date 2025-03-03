import serial
import time
import threading
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CanState(Enum):
    INIT = -4
    WAIT_START = -2
    WAIT_ID = -1
    RECEIVE = 0


class Can:
    def __init__(self, interface: str, baud_rate: int, timeout: int):
        self._ser = serial.Serial(interface, baud_rate, timeout=timeout)
        self.timeout = timeout
        self._can_lock = threading.Lock()

    def request(self, motor_id: bytes) -> (int, str):
        state = CanState.INIT
        cache = None
        datas = b''
        now = time.time()
        while True:
            if 0 < self.timeout < time.time() - now:
                logger.error(f"Can请求电机id：{motor_id}超时，等待超时")
                return -1, b''

            if state not in [CanState.INIT, CanState.RECEIVE]:  # 不等于0是为了后续读取数据不漏，不等于-4是因为发送数据不需要读取
                try:
                    cache = self._ser.read()
                except Exception as e:
                    logger.error(f"Can请求电机id：{motor_id}超时，串口读取超时")
                    print(e)
                    return -1, b''
            match state:
                case CanState.INIT:
                    self.send(motor_id + b"\x00\x00\x00\x00\x00\x00\x00")
                    state = CanState.WAIT_START
                case CanState.WAIT_START:
                    state = CanState.WAIT_ID if cache == b'\x0A' else CanState.INIT
                case CanState.WAIT_ID:
                    if cache == motor_id:
                        datas += motor_id
                        state = CanState.RECEIVE
                    else:
                        state = CanState.INIT
                case CanState.RECEIVE:
                    data_raw = self._ser.read(7)
                    if len(data_raw) < 7:
                        logger.error(f"请求电机id：{motor_id}，读取内容错误，可能是丢包")
                        return -1, b''
                    datas += data_raw
                    return 0, datas

    def send(self, arr: bytes):
        with self._can_lock:
            # logger.info(f"发送数据：{arr}")
            self._ser.write(arr)
            self._ser.flush()
            # print(b'\x00' + id + arr)

    def clear(self):
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()

    # def receive(self, id: bytes):
    #     state = CanState.WAIT_START
    #     datas = b''
    #     now = time.time()
    #     while True:
    #         if 0 < self.timeout < time.time() - now:
    #             print(str(Exception("Can Timeout (Receive)")))
    #             return -1, b''
    #         cache = self._ser.read()
    #         match state:
    #             case CanState.WAIT_START:
    #                 if cache == b'\x0A':
    #                     state = CanState.WAIT_ID
    #             case CanState.WAIT_ID:
    #                 if cache == id:
    #                     datas += cache
    #                     state = CanState.RECEIVE
    #                 else:
    #                     state = CanState.WAIT_START
    #             case CanState.RECEIVE:
    #                 datas += self._ser.read(7)
    #                 return 0, datas
