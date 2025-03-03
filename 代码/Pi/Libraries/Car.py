import logging
import queue
from Libraries.Software.Socket import SocketRecoCameraSender
from Libraries.Config import *
from Libraries.Call import Builder
from Libraries.Hardware import Motor_module
from Libraries.Hardware.Camera_module import Camera
from Libraries.Hardware.Gyro_module import Gyro
from Libraries.Hardware.Arduino_module import Arduino
from Libraries.Hardware.Can_module import Can
from Libraries.Software import Store
from Libraries.Software.Control import *
from Libraries.Software.Calculate import *
from Libraries.Software.Feedback import *


logger = logging.getLogger(__name__)

class CarSpeedMode(CarSpeedConfig):
    pass


class Car:
    def __init__(self):
        # 硬件生产
        self.my_can: Can = Builder.builder(Can, CanConfig)
        self.my_motor: Motor_module.Motor = Builder.builder(Motor_module.Motor, MotorConfig(can=self.my_can))
        self.my_gyro: Gyro = Builder.builder(Gyro, GyroConfig)
        self.my_arduino: Arduino = Builder.builder(Arduino, ArduinoConfig)

        # 生成摄像头对象，同时生成socket发送对象
        self.reco_camera: Camera = Builder.builder(Camera, CameraRecoConfig)
        stream_reco_camera_queue = queue.Queue()
        self.socket_reco_camera_stream = SocketRecoCameraSender(stream_queue=stream_reco_camera_queue)
        self.socket_reco_camera_stream.start()
        Builder.set_parameter(self.reco_camera, CameraRecoConfig)
        self.reco_camera.open()
        self.reco_camera.set_queue(stream_reco_camera_queue)

        # 驱动事件生产
        self.my_motor_receive = Builder.builder(Motor_module.MotorReceive, MotorCarReceiveConfig(can=self.my_can))

        # 抓取生产
        self.my_store_motor: Motor_module.Motor = Builder.builder(Motor_module.Motor, MotorConfig(can=self.my_can))
        self.my_store_lift: Store.Lift = Builder.builder(Store.Lift, StoreLiftConfig(motor=self.my_store_motor))
        self.my_store_plate: Store.Plate = Builder.builder(Store.Plate, StorePlateConfig(control=self.my_arduino))
        self.my_store_arm: Store.Other = Builder.builder(Store.Other, StoreArmConfig(control=self.my_arduino))
        self.my_store_hand: Store.Other = Builder.builder(Store.Other, StoreHandConfig(control=self.my_arduino))
        Builder.set_parameter(self.my_store_lift, StoreLiftConfig(motor=self.my_store_motor))
        Builder.set_parameter(self.my_store_plate, StorePlateConfig(control=self.my_arduino))
        Builder.set_parameter(self.my_store_arm, StoreArmConfig(control=self.my_arduino))
        Builder.set_parameter(self.my_store_hand, StoreHandConfig(control=self.my_arduino))
        self.my_store = Store.Store(
            my_hand=self.my_store_hand,
            my_arm=self.my_store_arm,
            my_lift=self.my_store_lift,
            my_plate=self.my_store_plate
        )

        # 软件生产
        self.my_control_walk: ControlWalk = ControlWalk(self.my_motor)
        self.my_control_turn: ControlTurn = ControlTurn(self.my_motor)
        self.my_control_creep: ControlCreep = ControlCreep(self.my_motor)
        self.my_calculation_walk: CalculateWalk = CalculateWalk()
        self.my_calculation_turn: CalculateTurn = CalculateTurn()
        self.my_calculation_creep: CalculateCreep = CalculateCreep()
        self.my_feedback_walk: FeedbackWalk = FeedbackWalk(
            motor_receive=self.my_motor_receive,
            gyro=self.my_gyro,
            camera=self.reco_camera
        )
        self.my_feedback_turn: FeedbackTurn = FeedbackTurn(gyro=self.my_gyro)
        self.my_feedback_creep: FeedbackCreep = FeedbackCreep()

        # 软件配置
        Builder.set_parameter(self.my_calculation_walk, CalculationWalkConfig)
        Builder.set_parameter(self.my_calculation_turn, CalculationTurnConfig)

        # 软件生产链绑定
        self.my_control_walk.set_next(
            next_cal=self.my_calculation_walk
        )
        self.my_control_turn.set_next(
            next_cal=self.my_calculation_turn
        )
        self.my_control_creep.set_next(
            next_cal=self.my_calculation_creep
        )
        self.my_calculation_walk.set_next(
            next_control=self.my_control_walk,
            next_feedback=self.my_feedback_walk
        )
        self.my_calculation_turn.set_next(
            next_control=self.my_control_turn,
            next_feedback=self.my_feedback_turn
        )
        self.my_calculation_creep.set_next(
            next_control=self.my_control_creep,
            next_feedback=self.my_feedback_creep
        )
        self.my_feedback_walk.set_next(
            next_control=self.my_control_walk,
            next_cal=self.my_calculation_walk
        )
        self.my_feedback_turn.set_next(
            next_control=self.my_control_turn,
            next_cal=self.my_calculation_turn
        )
        self.my_feedback_creep.set_next(
            next_control=self.my_control_creep,
            next_cal=self.my_calculation_creep
        )

        # 在初始化车的时候，设置绝对Yaw角
        Calculate.set_absolute_yaw(self.my_gyro)

    def walk(self, x, y, speed):
        logger.info("开始行走")
        self.my_control_walk.run(x, y, speed)
        self.check_walk_device_is_stop()
        self.check_walk_device_clear()
        sleep(0.2)
        logger.info("行走结束")
        logger.debug(f"行走结束后还存活的线程: {[t.name for t in threading.enumerate()]}")

    def check_walk_device_is_stop(self):
        self.my_gyro.is_stopped_event.wait()
        self.reco_camera.is_stopped_event.wait()
        self.my_calculation_walk.is_stopped_event.wait()
        self.my_control_walk.is_stopped_event.wait()
        self.my_feedback_walk.is_stopped_event.wait()

    def check_walk_device_clear(self):
        self.my_gyro.is_stopped_event.clear()
        self.reco_camera.is_stopped_event.clear()
        self.my_calculation_walk.is_stopped_event.clear()
        self.my_control_walk.is_stopped_event.clear()
        self.my_feedback_walk.is_stopped_event.clear()

    def turn(self, degrees, car_speed: CarSpeedMode, turn_mode: CalculateTurnMode, correct_times=3):
        logger.info("开始旋转")
        self.my_control_turn.run(degrees, car_speed, turn_mode, correct_times)
        self.my_gyro.is_stopped_event.wait()
        sleep(0.2)
        logger.info("旋转结束")
        logger.debug(f"旋转结束后还存活的线程: {[t.name for t in threading.enumerate()]}")

    def creep(self, x, y, speed):
        self.my_control_creep.run(x, y, speed)
        sleep(0.2)

    def correct_creep_turn(self):
        logger.info('开始爬行后的矫正车身')
        self.my_gyro.start()
        sleep(0.1)
        now_yaw = self.my_gyro.put().Yaw
        logger.info(f"绝对Yaw角: {self.my_calculation_walk.absolute_yaw}, 现在的Yaw: {now_yaw}")
        yaw_diff = Cal_Method.yaw_diff_cal(now_yaw - self.my_calculation_walk.absolute_yaw)
        self.turn(yaw_diff, CarSpeedMode.Turn, CalculateTurnMode.CORRECTION)
        self.my_gyro.stop()
        sleep(0.1)
        logger.info('爬行后矫正车身结束')

    # 料盘要用到的部分
    def get(self, degree):
        self.my_store.get(degree)

    def ready_get(self, degree, get_color: Color):
        self.my_store.ready_get(degree, get_color)

    def put(self, degree, put_color: Color):
        self.my_store.put(degree, put_color)


