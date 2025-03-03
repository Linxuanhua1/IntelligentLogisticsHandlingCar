import numpy as np
import sympy as sp
from Libraries.Method.Image_reco import Color


def yaw_diff_cal(diff):
    while diff > 180 or diff < -180:
        if diff < -180:
            diff += 360
        if diff > 180:
            diff -= 360
    return diff


def degree_cal(speed, time) -> np.ndarray:  # 角度计算
    distance = abs(speed) * time
    # print(f"distance_arr:{distance_arr}")
    degree = distance / 239.268 * 360  # 239.268为轮子周长，单位mm
    return degree


def speed_cal(vx, vy, omega=0) -> np.ndarray:  # 轮子的线速度，omega弧度每秒
    a, b = 106, 105
    return np.array([
        vx + vy - omega * (a + b),
        vx - vy + omega * (a + b),
        vx - vy - omega * (a + b),
        vx + vy + omega * (a + b)
    ])


def xy2vector(x, y, speed_coe: float) -> np.ndarray:  # 计算小车的速度向量

    # 转换向量
    v = np.array([x, y])
    # 计算向量的模
    magnitude = np.linalg.norm(v)
    # 检查 magnitude 是否为零或 NaN
    speed_vector = v / magnitude
    # print(f"速度向量: {v}, 速度向量的模: {magnitude}, speed: {speed_vector}")
    # 调整速度模式
    speed_vector *= speed_coe
    return speed_vector  # vx, vy


def xy2degree(x, y, speed_vector, speed_line_arr) -> np.ndarray:
    time = xy2time(x, y, speed_vector)  # 计算车辆行驶时间
    return degree_cal(speed_line_arr, time)


def xy2time(x, y, speed_vector) -> float:
    distance = np.sqrt(x * x + y * y)  # 行驶的距离 mm
    time = distance / np.linalg.norm(speed_vector)  # 行驶时间 s
    return time


# 线速度转换为角速度
def speed2rads(speed_line_arr: np.ndarray) -> np.ndarray:
    return np.around(speed_line_arr / 38.1, 3)


def cardeg2wheeldeg(turn_degree, car_speed_rad: float, wheel_speed_rad) -> float:
    time = (turn_degree / 180 * np.pi) / car_speed_rad
    wheel_degree = np.around(wheel_speed_rad * time * 180 / np.pi, 3)
    return abs(wheel_degree)


def creep_cal(x, y, speed_coe: float) -> (np.ndarray, float, np.ndarray, float):
    """
    :param x: x方向移动距离，单位mm
    :param y: y方向移动距离，单位mm
    :param speed_coe: 速度系数，放大多少倍
    """
    speed_vector = xy2vector(x, y, speed_coe)
    speed_line_x = speed_cal(speed_vector[0], 0)
    speed_line_y = speed_cal(0, speed_vector[1])

    speed_rad_x = speed2rads(speed_line_x)
    speed_rad_y = speed2rads(speed_line_y)
    degree_x = xy2degree(x, y, speed_vector, speed_line_x[0])
    degree_y = xy2degree(x, y, speed_vector, speed_line_y[0])

    return speed_rad_x, degree_x, speed_rad_y, degree_y


def integrate_func(integrate_times: int, var_coe: float, constant: float) -> (sp.Symbol, sp.core.expr.Expr):
    x = sp.symbols('x')
    f = var_coe * x + constant
    for i in range(integrate_times):
        f = sp.integrate(f, x)
    return f, x


def task_str2task_enum(task_str: str) -> list:
    task_enum = []
    for char in task_str:
        if char == "+":
            continue
        task_enum.append(Color(int(char)))
    return task_enum
