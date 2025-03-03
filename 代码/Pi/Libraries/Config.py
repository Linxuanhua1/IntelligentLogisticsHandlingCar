from Libraries.Call import Builder
from Libraries.Hardware import Can_module, Motor_module, Arduino_module
from Libraries.Method.Image_reco import Color


# ------------Hardware----------------------------

class CanConfig(Builder.Unpack):
    interface: str = '/dev/ttyAMA2'
    baud_rate: float = 115200
    timeout: int = 5

    @classmethod
    def unpack(cls):
        return cls.interface, cls.baud_rate, cls.timeout


class MotorConfig(Builder.Unpack):
    segmentation: Motor_module.MotorSegmentation = Motor_module.MotorSegmentation.S32
    request_bool: bool = True
    max_speed: float = 30
    min_speed: float = 0.1

    @classmethod
    def __init__(cls, can: Can_module.Can):
        cls.can = can

    @classmethod
    def unpack(cls):
        return cls.can, cls.segmentation, cls.request_bool, cls.max_speed, cls.min_speed


class GyroConfig(Builder.Unpack):
    interface: str = '/dev/ttyAMA3'
    baud_rate: float = 9600
    delay: float = 0.02

    @classmethod
    def unpack(cls):
        return cls.interface, cls.baud_rate, cls.delay


class ArduinoConfig(Builder.Unpack):
    interface: str = '/dev/ttyAMA1'
    baud_rate: float = 115200

    @classmethod
    def unpack(cls):
        return cls.interface, cls.baud_rate


class CameraRecoConfig(Builder.Unpack):
    src: str = "/dev/reco_camera"
    camera_name: str = "reco_camera"
    is_rotated: bool = False
    is_send: bool = True

    @classmethod
    def unpack(cls):
        return cls.src, cls.camera_name

    @classmethod
    def unpack_parameter(cls):
        return cls.is_rotated, cls.is_send


class CameraQRConfig(Builder.Unpack):
    src: str = "/dev/qr_camera"
    camera_name: str = "qr_camera"
    is_rotated: bool = True
    is_send: bool = True

    @classmethod
    def unpack(cls):
        return cls.src, cls.camera_name

    @classmethod
    def unpack_parameter(cls):
        return cls.is_rotated, cls.is_send


# RecoPart
class RecoPartConfig(Builder.Unpack):
    is_send: bool = True

    @classmethod
    def unpack(cls):
        return [cls.is_send]


# ------------Hardware----------------------------

# ------------Hardware_Event----------------------

class MotorCarReceiveConfig(Builder.Unpack):
    id: Motor_module.MotorId = Motor_module.MotorId.FR_Motor
    delay: float = 0.05

    @classmethod
    def __init__(cls, can: Can_module.Can):
        cls.can = can

    def unpack(self):
        return self.can, self.id, self.delay


# ------------Hardware_Event----------------------

# ------------Software/Store----------------------------

class StoreLiftConfig(Builder.Unpack, Builder.SetParameter):
    id: Motor_module.MotorId = Motor_module.MotorId.UD_Motor
    speed: float = 30
    plate_degree: float = 250
    rail_len: float = 925
    reverse: bool = True

    @classmethod
    def __init__(cls, motor: Motor_module.Motor):
        cls.motor = motor

    @classmethod
    def unpack(cls):
        return cls.motor, cls.id

    @classmethod
    def unpack_parameter(cls):
        return cls.speed, cls.plate_degree, cls.rail_len, cls.reverse


class StoreHandConfig(Builder.Unpack, Builder.SetParameter):
    id: int = 0
    off: int = 130
    on: int = 70

    @classmethod
    def __init__(cls, control: Arduino_module.Arduino):
        cls.control = control

    @classmethod
    def unpack(cls):
        return cls.control, cls.id

    @classmethod
    def unpack_parameter(cls):
        return cls.off, cls.on


class StoreArmConfig(Builder.Unpack, Builder.SetParameter):
    id: int = 1
    off: int = 10
    on: int = 102

    @classmethod
    def __init__(cls, control: Arduino_module.Arduino):
        cls.control = control

    @classmethod
    def unpack(cls):
        return cls.control, cls.id

    @classmethod
    def unpack_parameter(cls):
        return cls.off, cls.on


class StorePlateConfig(Builder.Unpack, Builder.SetParameter):
    id: int = 2
    location: dict[Color: int] = {Color.RED: 0, Color.GREEN: 60, Color.BLUE: 120}

    @classmethod
    def __init__(cls, control: Arduino_module.Arduino):
        cls.control = control

    @classmethod
    def unpack(cls):
        return cls.control, cls.id

    @classmethod
    def unpack_parameter(cls):
        return [cls.location]


# ----------Software/Calculation----------------------------

class CalculationWalkConfig(Builder.SetParameter):
    integrate_times: int = 3
    var_coe: int = 1
    constant: int = 10
    value: int = 5  # 未知数x取的值
    start_acceleration: float = 1
    stop_deceleration: float = 1
    vy_compensate: float = 0.5
    yaw_compensate: float = 0.05

    @classmethod
    def unpack_parameter(cls):
        return (cls.integrate_times, cls.var_coe, cls.constant, cls.value, cls.start_acceleration,
                cls.stop_deceleration, cls.vy_compensate, cls.yaw_compensate)


class CalculationTurnConfig(Builder.SetParameter):
    dev = 0.1
    turn_compensate = 0

    @classmethod
    def unpack_parameter(cls):
        return cls.dev, cls.turn_compensate


# ----------CarSpeedSet-------------------------

class CarSpeedConfig:
    Fast = 350
    Creep = 150
    Turn = 1



