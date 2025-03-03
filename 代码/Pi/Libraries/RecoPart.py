from __future__ import annotations

import cv2
import queue
import logging
from time import sleep
from enum import Enum
import numpy as np
from typing import TYPE_CHECKING
from Libraries.Call.Stream import StreamOut
from Libraries.Method.Image_reco import *
if TYPE_CHECKING:
    from Libraries.Hardware.Camera_module import Camera


logger = logging.getLogger(__name__)


class RecoPartMode(Enum):
    QRSCAN = 1
    RECO = 2


class RecoPart(StreamOut):
    def __init__(self, is_send: bool):
        StreamOut.__init__(self)
        self.reco_camera = None
        self.qr_camera = None
        self.is_send: bool = is_send  # 是否发送
        self.data_queue: queue.Queue = None

    def set_queue(self, data_queue: queue.Queue):
        self.data_queue = data_queue

    def set_camera(self, reco_camera: Camera, qr_camera: Camera):
        self.qr_camera: Camera = qr_camera
        self.reco_camera: Camera = reco_camera

    def start(self, mode: RecoPartMode):
        if mode == RecoPartMode.QRSCAN:
            self.bind(self.qr_camera)
        elif mode == RecoPartMode.RECO:
            self.bind(self.reco_camera)

    def stop(self, mode: RecoPartMode):
        self.unbind()
        if mode == RecoPartMode.QRSCAN:
            self.qr_camera.is_stopped_event.wait()
            self.qr_camera.is_stopped_event.clear()
        elif mode == RecoPartMode.RECO:
            self.reco_camera.is_stopped_event.wait()
            self.reco_camera.is_stopped_event.clear()

    def material_correct(self) -> (float, float):
        """
        :return: 返回 物料中心距离摄像头中心点的距离单位是mm
        """
        pos_newx, pos_newy = self._track_target_until_stationary(Color.ALL)
        return - (pos_newx - 960) / 14.14, -(pos_newy - 540) / 14.14

    def scan_qr(self) -> str:
        while True:
            frame: np.ndarray = self.get()
            code = qr_decode(frame)
            if code is not None:
                break
            else:
                sleep(0.3)
                logger.info('没有识别到二维码，过0.3s后重试')
        logger.info(f"成功识别到二维码，内容是{code}")
        return code

    def place_correct(self, reco_color: Color) -> (float, float):
        """
        :param reco_color: 识别圆环的颜色
        :return: 返回识别圆环中心距离摄像头中心的距离，单位是mm
        """
        while True:
            frame = self.get()
            centre_x, centre_y = self.trace_target(reco_color, frame)
            # print(centre_x, centre_y)
            if centre_x == -1:
                continue
            else:
                return - (centre_x - 960) / 5.32, -(centre_y - 540) / 5.32

    def trace_target(self, reco_color: Color, frame) -> tuple[float, float]:
        """
        :param frame: 视频帧
        :param reco_color: 使用枚举传入RED,GREEN,BLUE,ALL
        :return: 返回的是距离摄像头最近的点
        """
        masks = find_color(frame, reco_color)  # 获取颜色掩码
        centre_points_dict = find_centre(masks)  # 获取每个掩码的中心点
        centre_point = closest2centre(centre_points_dict)
        # print(f"centre_point: {centre_point}")
        if self.is_send:
            combined_mask = np.zeros((1080, 1920), dtype=np.uint8)
            for mask in masks.values():
                combined_mask = cv2.bitwise_or(combined_mask, mask)
            new_frame = cv2.bitwise_and(frame, frame, mask=combined_mask)
            # cv2.circle(new_frame, (int(centre_point[0]), int(centre_point[1])), 1, (0, 0, 255), -1)
            self.data_queue.put(new_frame)
        return centre_point

    def check_is_target(self, reco_color: Color):
        self._track_target_until_stationary(reco_color)
        logger.info("检测到目标，开始抓取")

    def _track_target_until_stationary(self, color: Color, frame_delay: float = 0.3, movement_threshold: int = 10) \
            -> (float, float):
        """
        通用的物料追踪逻辑，追踪物料直到静止。

        :param color: 要追踪的物料颜色
        :param frame_delay: 每次扫描之间的延迟
        :param movement_threshold: 检测移动的阈值，单位为像素
        :return: 静止后物料的中心坐标 (pos_newx, pos_newy)
        """
        frame = self.get()
        pos_oldx, pos_oldy = self.trace_target(color, frame)
        sleep(frame_delay)
        while True:
            frame = self.get()
            pos_newx, pos_newy = self.trace_target(color, frame)
            # print(pos_newx, pos_newy)
            if pos_newx == -1:  # 没有检测到物料
                continue
            if abs(pos_oldx - pos_newx) >= movement_threshold or abs(pos_oldy - pos_newy) >= movement_threshold:
                logger.info("物料正在移动")
                pos_oldx = pos_newx
                pos_oldy = pos_newy
                sleep(frame_delay)
            else:
                return pos_newx, pos_newy
