from __future__ import annotations
import threading
from enum import Enum
import time
import logging
from abc import abstractmethod, ABCMeta
from typing import TYPE_CHECKING
from Libraries.Method import Cal_Method
from Libraries.Call.Handle import Handle
from Libraries.Method import Image_reco
from Libraries.Call import Builder
from Libraries.Hardware.Gyro_module import Gyro
if TYPE_CHECKING:
    from Libraries.Software.Feedback import FeedbackWalk, FeedbackTurn, FeedbackCreep
    from Libraries.Software.Control import ControlWalk, ControlTurn, ControlCreep

logger = logging.getLogger(__name__)


class Calculate(Handle, metaclass=ABCMeta):
    absolute_yaw = None

    def __init__(self):
        self.next_feedback = None
        self.next_control = None

    @classmethod
    def set_absolute_yaw(cls, gyro: Gyro):
        logger.info("正在设置绝对Yaw角")
        cls.absolute_yaw = gyro.set_absolute_yaw()
        logger.info(f"设置完成，当前绝对Yaw角为{cls.absolute_yaw}")

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_next(self, *args, **kwargs):
        pass

    @abstractmethod
    def set(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop(self):
        pass


class CalculateWalk(Calculate, Builder.Parameter):
    def __init__(self):
        Calculate.__init__(self)
        self.yaw_compensate = None
        self.vy_compensate = None
        self._last = None
        self.speed_vector = None
        self.walk_deg_hope = None  # 到达目标位置需要转动的角度
        self.acc_degree = None  # 加速角度范围
        self.start_acceleration = None  # 起步加速度
        self.stop_deceleration = None  # 停止减速度
        self.current_degree = None  # 当前转动角度
        self.yaw = None  # 当前yaw角
        self.frame = None  # 获取的视频帧
        self.update_event = threading.Event()  # 更新事件
        self.stop_update_event = threading.Event()  # 停止更新事件
        self.is_stopped_event = threading.Event()  # 设备停止事件
        self.thread = None  # 线程

    def set_parameter(self, integrate_times: int, var_coe: int, constant: int, value: int, start_acceleration: float,
                      stop_deceleration: float, vy_compensate: float, yaw_compensate: float):
        self.yaw_compensate = yaw_compensate
        self.vy_compensate = vy_compensate
        self.start_acceleration = start_acceleration  # 起步加速度
        self.stop_deceleration = stop_deceleration  # 停止减速度
        integrate_func, x = Cal_Method.integrate_func(integrate_times, var_coe, constant)  # 接受计算加减速阈值函数和积分变量
        self.acc_degree = int(integrate_func.subs(x, value))  # 加速函数，以角度为阈值
        logger.debug(f"加速角度区间：{self.acc_degree}")

    def set_next(self, next_feedback: FeedbackWalk, next_control: ControlWalk):
        self.next_feedback: FeedbackWalk = next_feedback
        self.next_control: ControlWalk = next_control

    def update(self):
        # print("CalculateWalk is ready")
        while self.stop_update_event.is_set():
            vy_compensate = self.cal_vy_compensate(self.frame)
            yaw_compensate = self.cal_yaw_compensate(self.absolute_yaw, self.yaw)
            # print(f"now_yaw: {self.yaw}")
            rest_degree = abs(self.walk_deg_hope - self.current_degree)
            logger.debug(f"当前转动角度: {self.current_degree}, 加速角度区间：{self.acc_degree}, 剩余转动角度：{rest_degree}")
            # 升档加速条件，第一，电机转动角度大于当前档位所需要的转动角度，第二，剩余移动距离必须小于当前档位所需要的转动角度，否则进入减速状态
            if self.current_degree <= self.acc_degree and rest_degree > 1.5 * self.acc_degree:
                # 进入减速状态后，会出现降档后剩余角度>加速角度成立，为了避免这个情况，设置了一个标志，减速后进入这个判断不升档，维持原速
                speed_rad_arr = self.smooth_acceleration(vy_compensate, yaw_compensate)
                # print("State 1, acc")

            # 维持当前档位的条件，第一，电机转动角度小于升档所需的角度，第二，剩余移动距离小于当前档位所需要的转动角度，否则进入减速状态
            elif self.current_degree > self.acc_degree and rest_degree > 1.5 * self.acc_degree:
                speed_line_arr = Cal_Method.speed_cal(self.speed_vector[0], self.speed_vector[1] + vy_compensate,
                                                      yaw_compensate)
                speed_rad_arr = Cal_Method.speed2rads(speed_line_arr)
                # print("State 2, keep")
            # 不满足加速要求或者维持档位要求，进入减速状态
            else:
                speed_rad_arr = self.smooth_deceleration(vy_compensate, yaw_compensate, rest_degree)
                # print("State 3, dec")
            logger.debug(f"修正后的速度向量：{speed_rad_arr}")
            self.next_control.update(speed_rad_arr)  # 将四个轮子的线速度向量转换为角速度向量 rad/s
            self.update_event.wait()  # 等待事件激活，feedback类数据有更新这个事件就会被激活
            self.update_event.clear()  # 清除激活状态，进入下一次循环
        # print("CalculateWalk is stopped")
        self.is_stopped_event.set()

    def smooth_acceleration(self, vy_compensate, yaw_compensate):
        # 二次曲线计算系数用
        acc_coe = min(1, max(self.start_acceleration * (self.current_degree / self.acc_degree) ** 2, 0.4))
        yaw_compensate *= acc_coe
        speed_line_arr = Cal_Method.speed_cal(self.speed_vector[0], self.speed_vector[1] + vy_compensate,
                                              yaw_compensate)
        speed_rad_arr = Cal_Method.speed2rads(speed_line_arr)
        return speed_rad_arr * acc_coe  # 二次加速曲线

    def smooth_deceleration(self, vy_compensate, yaw_compensate, rest_degree):
        # 二次曲线计算系数用
        dec_coe = min(1, max(self.stop_deceleration * (rest_degree / (1.5 * self.acc_degree)) ** 2, 0.4))
        yaw_compensate *= dec_coe
        speed_line_arr = Cal_Method.speed_cal(self.speed_vector[0], self.speed_vector[1] + vy_compensate,
                                              yaw_compensate)
        speed_rad_arr = Cal_Method.speed2rads(speed_line_arr)
        return speed_rad_arr * dec_coe  # 二次减速曲线

    def set(self, x, y, speed_coe):
        self.update_event.clear()
        self.stop_update_event.clear()
        # 防止脑抽，哪里没写清除，统一清除一下

        self.current_degree = 0  # 当前转动角度置零
        self.speed_vector = Cal_Method.xy2vector(x, y, speed_coe)  # 小车的线速度向量 mm/s
        speed_line_arr = Cal_Method.speed_cal(self.speed_vector[0], self.speed_vector[1])  # 四个轮子的起步的线速度向量 mm/s
        self.walk_deg_hope = Cal_Method.xy2degree(x, y, self.speed_vector, speed_line_arr[0])  # 计算预期行驶转动角度

        # ——————————————————————————————————————————CalculateWalk set初步结束—————————————————————————————————————————
        self.next_feedback.set(self.walk_deg_hope)  # 把参数传给feedback
        speed_rad_arr = self.smooth_acceleration(0, 0)  # 转换为角速度
        logger.debug(f"电机初始角速度数组: {speed_rad_arr}")
        self.next_control.update(speed_rad_arr)
        self.thread = threading.Thread(name=self.__class__.__name__, target=self.update)
        self.thread.start()

    def stop(self):
        self.stop_update_event.clear()
        self.update_event.set()

    """
    cal_vy_compensate
    根据后续实测结果考虑是否删除，跟todo写的一样，没思路如何修改，而且陀螺仪矫正其实车不太会走歪，
    当时想的是用来检测边缘，万一走的太近拉回来一点。
    """
    def cal_vy_compensate(self, frame):
        if frame is not None:
            min_distance, closest_line = Image_reco.cal_horizontal_distance(frame, (960, 1080))
            logger.debug(f"摄像头检测距离边线的距离为: {min_distance}")
            if closest_line is None or min_distance is None:
                return 0
            if self._last is None:
                self._last = min_distance
            if min_distance < 10:
                if abs(min_distance - self._last) > 50:  # TODO:如果此次检测差值很大，就抛弃这次的检测值（算法设计有问题，还没想好怎么改）
                    self._last = min_distance
                    return 0

            self._last = min_distance

            if min_distance < 75:  # TODO: 边缘线距离，还没具体测试到底是多少
                return self.vy_compensate
            elif min_distance > 90:
                return -self.vy_compensate
            else:
                return 0
        else:
            return 0

    @staticmethod
    def cal_yaw_compensate(hope, yaw):
        yaw_diff = Cal_Method.yaw_diff_cal(hope - yaw)
        logger.debug(f"行走中yaw角和绝对yaw角的差值：{yaw_diff}")
        # yaw_compensate = -self.yaw_compensate if yaw_diff > 0 else self.yaw_compensate
        if yaw_diff < 0:
            yaw_compensate = - max(yaw_diff, -2) / 20
        else:
            yaw_compensate = - min(yaw_diff, 2) / 20
        return yaw_compensate


class CalculateTurnMode(Enum):
    INITIAL_TURN = 1  # 第一圈的第一次旋转（更新绝对Yaw角，但是不加入旋转补偿值）
    COMPENSATED_TURN = 2  # 第二圈的第一次旋转（更新绝对Yaw角，同时计算旋转补偿值）
    CORRECTION = 3  # 矫正车身（不更新绝对Yaw角）


class CalculateTurn(Calculate, Builder.Parameter):
    def __init__(self):
        super().__init__()
        self.car_speed = None
        self.dev = None
        self.motor_lock = threading.Lock()
        self.turn_compensate = None

    def set_parameter(self, dev, turn_compensate):
        self.dev = dev
        self.turn_compensate = turn_compensate

    def set_next(self, next_feedback: FeedbackTurn, next_control: ControlTurn):
        self.next_feedback: FeedbackTurn = next_feedback
        self.next_control: ControlTurn = next_control

    def set(self, turn_degree: float, car_speed: float, turn_mode: CalculateTurnMode):
        if turn_mode == CalculateTurnMode.INITIAL_TURN or turn_mode == CalculateTurnMode.COMPENSATED_TURN:
            logger.debug(f"旋转角度为：{turn_degree}，当前旋转模式：{turn_mode}")
        elif turn_mode == CalculateTurnMode.CORRECTION:
            logger.debug(f"矫正车身需要的旋转度数为：{turn_degree}，当前旋转模式：{turn_mode}")

        self.next_feedback.set()
        time.sleep(0.2)  # 等待陀螺仪的数据稳定
        self.car_speed = car_speed
        if turn_degree < 0:
            car_speed = -car_speed

        # 判断旋转模式，第一圈的时候不需要加入补偿值，第二圈的时候需要加入补偿值，矫正的时候不需要更新Yaw角
        if turn_mode == CalculateTurnMode.INITIAL_TURN:
            Calculate.absolute_yaw = Cal_Method.yaw_diff_cal(self.absolute_yaw - turn_degree)
        elif turn_mode == CalculateTurnMode.COMPENSATED_TURN:
            Calculate.absolute_yaw = Cal_Method.yaw_diff_cal(self.absolute_yaw - (turn_degree - self.turn_compensate))

        logger.debug(f"当前的绝对Yaw角值为 {self.absolute_yaw}")
        speed_line_arr = Cal_Method.speed_cal(0, 0, car_speed)
        speed_rad_arr = Cal_Method.speed2rads(speed_line_arr)
        wheel_degree = Cal_Method.cardeg2wheeldeg(turn_degree, car_speed, speed_rad_arr[0])
        logger.debug(f"转动角度: {wheel_degree}, 各轮角速度列表: {speed_rad_arr}")

        self.next_control.update(speed_rad_arr, wheel_degree)

    def stop(self):
        self.next_feedback.stop()

    def update(self):
        yaw = self.next_feedback.update()
        diff = Cal_Method.yaw_diff_cal(yaw - self.absolute_yaw)
        logger.info(f"需要再旋转的角度为 {diff}")
        if abs(diff) <= self.dev:
            return True
        else:
            car_speed = -self.car_speed if diff < 0 else self.car_speed
            speed_line_arr = Cal_Method.speed_cal(0, 0, car_speed)
            speed_rad_arr = Cal_Method.speed2rads(speed_line_arr)
            correct_wheel_degree = Cal_Method.cardeg2wheeldeg(diff, self.car_speed, speed_rad_arr[0])
            self.next_control.update(speed_rad_arr, correct_wheel_degree)
            return False


class CalculateCreep(Calculate):
    def __init__(self):
        super().__init__()

    def set_next(self, next_feedback: FeedbackCreep, next_control: ControlCreep):
        self.next_feedback: FeedbackCreep = next_feedback
        self.next_control: ControlCreep = next_control

    def set(self, x, y, speed_coe):
        self.next_control.update(*Cal_Method.creep_cal(x, y, speed_coe))

    def stop(self):
        pass

    def update(self):
        pass
