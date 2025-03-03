from __future__ import annotations
import time
import threading
import logging
from typing import TYPE_CHECKING
from Libraries.Method.Image_reco import Color
from Libraries.Method.Cal_Method import task_str2task_enum
from Libraries.RecoPart import RecoPart, RecoPartMode
if TYPE_CHECKING:
    from Libraries.Car import Car, CarSpeedMode
    from Libraries.Software.Calculate import CalculateTurnMode


logger = logging.getLogger(__name__)


class Task:
    color_point = {Color.RED: -150, Color.GREEN: 0, Color.BLUE: 150}

    def __init__(self, car: Car, car_speed: CarSpeedMode, reco_part: RecoPart):
        self.car: Car = car
        self.speed_mode: CarSpeedMode = car_speed
        self.reco_part: RecoPart = reco_part

    def _ingredient2rough(self, walk_compensate: float, turn_mode: CalculateTurnMode):
        self.car.walk(-375 - walk_compensate, 0, self.speed_mode.Fast)
        self.car.turn(90, self.speed_mode.Turn, turn_mode)
        self.car.walk(1620, 0, self.speed_mode.Fast)
        self.car.turn(90, self.speed_mode.Turn, turn_mode)

    def _rough2staging(self, now_circle_color: Color, next_circle_color: Color, turn_mode: CalculateTurnMode):
        compensate_1 = self.color_point[now_circle_color]
        compensate_2 = self.color_point[next_circle_color]
        self.car.walk(-785 - compensate_1, 0, self.speed_mode.Fast)
        self.car.turn(-90, self.speed_mode.Turn, turn_mode)
        # print(f"{next_circle_color}，从转角到暂存区的距离{-785 + compensate_2}")
        self.car.walk(-755 + compensate_2, 0, self.speed_mode.Fast)

    def _material_correct(self) -> float:  # 根据摄像头返回的值来移动
        self.reco_part.start(RecoPartMode.RECO)
        compensate: float = 0
        for i in range(2):
            x, y = self.reco_part.material_correct()
            if x != 0 or y != 0:
                compensate += x
                logger.info(f"车辆前进{x}，左右移动{y}")
                self.car.creep(x, y, self.speed_mode.Creep)
                time.sleep(1)
                logger.info(f"物料校准第{i+1}次，完成")
        self.reco_part.stop(RecoPartMode.RECO)
        logger.info("物料校准任务结束")
        return compensate

    def _place_correct(self, correct_color: Color):
        self.reco_part.start(RecoPartMode.RECO)
        time.sleep(0.5)
        for i in range(2):
            x, y = self.reco_part.place_correct(correct_color)
            if x != 0 or y != 0:
                logger.info(f"x方向行走：{x}，y方向行走：{y}")
                self.car.creep(x, y, self.speed_mode.Creep)
                logger.info(f"放置校准第{i+1}次完成")
        self.reco_part.stop(RecoPartMode.RECO)
        logger.info("放置校准任务结束")

    def _get_material_from_ground(self, task: list[Color]):
        now_color = task[-1]
        for i, color in enumerate(task):
            self.car.creep(self.color_point[color] - self.color_point[now_color], 0, self.speed_mode.Creep)
            self._get_material(color, 925)
            now_color = color

    def _get_material_from_ingredient(self, task: list[Color], down_degree=500) -> float:
        """
        :param task: 放置顺序。
        :return: 移动补偿值。
        """
        compensate = self._material_correct()
        self.reco_part.start(RecoPartMode.RECO)
        for i, color in enumerate(task):
            logger.info(f"开始从第 {i + 1} 个位置 ({color}) 获取材料")
            self._get_material(color, down_degree, True)
        self.reco_part.stop(RecoPartMode.RECO)
        return compensate

    def _place_material(self, task: list[Color], degree: float, now_color: Color):  # 车默认走到绿色
        """
        :param task: 放置顺序。
        :param degree: 放置时的升降机构的下角度。
        :param now_color: 当前所在颜色点。
        """
        # 遍历放置点，逐一处理
        for i, color in enumerate(task):
            diff = self.color_point[color] - self.color_point[now_color]
            logger.info(f"第 {i + 1} 次放置行走：{diff}")
            if diff != 0:
                self.car.creep(diff, 0, self.speed_mode.Creep)
            self._place_correct(color)
            self.car.put(degree, color)
            now_color = color  # 更新当前位置


    def repeat_task(self, task: list, place_degree: float, turn_mode: CalculateTurnMode):
        # get material from ingredient
        logger.info('从原料区拿物料')
        self.car.creep(0, 40, self.speed_mode.Creep)
        first, second, third = task
        walk_compensate = self._get_material_from_ingredient(task)
        self.car.creep(0, -40, self.speed_mode.Creep)
        self.car.correct_creep_turn()
        logger.info('原料区的物料全部拿取完毕')
        logger.info('-' * 50)

        # ingredient area to rough machining area
        logger.info("从原料区到粗加工区")
        self._ingredient2rough(walk_compensate, turn_mode)
        logger.info("到达粗加工区")
        logger.info('-' * 50)

        # place material
        self.car.creep(0, 80, self.speed_mode.Creep)
        logger.info("开始将物料放置到粗加工区")
        self._place_material(task, 925, Color.GREEN)
        self.car.correct_creep_turn()
        logger.info("物料已全部放置到粗加工区")
        logger.info('-' * 50)

        # get material from ground
        logger.info('将放置于粗加工区的物料拿起')
        self._get_material_from_ground(task)
        self.car.creep(0, -80, self.speed_mode.Creep)
        self.car.correct_creep_turn()
        logger.info("粗加工区的物料全部拿取完毕")
        logger.info('-' * 50)

        # rough machining area to staging area
        logger.info("从粗加工区到暂存区")
        self._rough2staging(task[-1], task[0], turn_mode)
        logger.info("到达暂存区")
        logger.info('-' * 50)

        # place material
        self.car.creep(0, 80, self.speed_mode.Creep)
        logger.info("开始将物料放置到暂存区")
        self._place_material(task, place_degree, task[0])
        self.car.creep(0, -80, self.speed_mode.Creep)
        self.car.correct_creep_turn()
        logger.info("物料已全部放置到暂存区")
        logger.info('-' * 50)

    def _get_material(self, color: Color, degree: float, check: bool = False):
        self.car.ready_get(degree, color)
        if check:
            self.reco_part.check_is_target(color)
        self.car.get(degree)

    def scan_qr(self):
        self.reco_part.start(RecoPartMode.QRSCAN)
        task_str: str = self.reco_part.scan_qr()
        task_enum: list = task_str2task_enum(task_str)
        self.reco_part.stop(RecoPartMode.QRSCAN)
        return task_enum, task_str
