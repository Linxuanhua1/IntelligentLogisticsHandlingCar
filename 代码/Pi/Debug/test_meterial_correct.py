import sys
import os
import threading

sys.path.append(os.path.abspath("/root/Pi"))

from Libraries.Car import CarSpeedMode, Car
from Libraries.RecoPart import RecoPart
from Libraries.Config import RecoPartConfig, CameraQRConfig
from Libraries.Call import Builder
from Libraries.Task_module import Task
from Libraries.Hardware.Camera_module import Camera
from Libraries.Software.Socket import SocketQRCameraSender, SocketRecoPartSender
import queue
import logging
from typing import Optional


def configure_logger(
    log_file: Optional[str] = 'log.log',
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_format: str = '%(asctime)s | %(name)s - %(funcName)s | %(levelname)s: %(message)s',
    date_format: str = '%Y-%m-%d %H:%M:%S',
    encoding: str = 'utf-8'
) -> logging.Logger:
    # 创建 Formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 获取全局日志器
    logger = logging.getLogger()
    logger.setLevel(min(console_level, file_level))  # 日志器级别设为最小的级别

    # 清除已有的 Handler，避免重复日志
    if logger.handlers:
        logger.handlers.clear()

    # 配置控制台日志 Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 配置文件日志 Handler（如果指定了日志文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='w', encoding=encoding)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


if __name__ == '__main__':
    logger = configure_logger()
    speed_mode = CarSpeedMode()
    my_car: Car = Car()
    qr_camera: Camera = Builder.builder(Camera, CameraQRConfig)
    Builder.set_parameter(qr_camera, CameraQRConfig)
    qr_camera.open()

    # 发送队列
    stream_qr_camera_queue = queue.Queue()
    socket_qr_camera_stream = SocketQRCameraSender(stream_queue=stream_qr_camera_queue)
    qr_camera.set_queue(stream_qr_camera_queue)
    socket_qr_camera_stream.start()

    stream_reco_part_queue = queue.Queue()
    socket_reco_part_stream = SocketRecoPartSender(stream_queue=stream_reco_part_queue)
    socket_reco_part_stream.start()
    reco_part: RecoPart = Builder.builder(RecoPart, RecoPartConfig)
    reco_part.set_queue(stream_reco_part_queue)
    reco_part.set_camera(my_car.reco_camera, qr_camera)

    task: Task = Task(my_car, speed_mode, reco_part)

    my_car.my_store_arm.set(True)
    task._material_correct()
    socket_qr_camera_stream.stop()
    socket_reco_part_stream.stop()
    my_car.socket_reco_camera_stream.stop()
    print(threading.enumerate())