import cv2
import math
import numpy as np
from enum import Enum

k = np.ones((3, 3), dtype=np.uint8)


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    ALL = 4


def find_color(frame: np.ndarray, color: Color):
    """
    :param frame: 图片对象
    :param color: 输入red,green,blue
    :return: 矩形左下角坐标
    """
    color_masks: dict[Color, np.ndarray] = {}
    # 将图片转换为hsv色彩空间
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # 定义颜色的色相、明度、饱和度范围
    if color in [Color.RED, Color.ALL]:  # 追踪红色
        lower_red1 = np.array([0, 80, 80])
        upper_red1 = np.array([15, 255, 255])
        lower_red2 = np.array([165, 80, 80])
        upper_red2 = np.array([180, 255, 255])

        mask_red1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)

        color_masks[Color.RED] = cv2.bitwise_or(mask_red1, mask_red2)
    if color in [Color.GREEN, Color.ALL]:  # 追踪绿色
        lower_green = np.array([40, 80, 80])
        upper_green = np.array([90, 255, 255])

        color_masks[Color.GREEN] = cv2.inRange(hsv_frame, lower_green, upper_green)
    if color in [Color.BLUE, Color.ALL]:  # 追踪蓝色
        lower_blue = np.array([100, 80, 80])
        upper_blue = np.array([130, 255, 255])
        color_masks[Color.BLUE] = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    for key in color_masks.keys():
        color_masks[key] = cv2.morphologyEx(color_masks[key], cv2.MORPH_OPEN, k)
        color_masks[key] = cv2.morphologyEx(color_masks[key], cv2.MORPH_CLOSE, k)

    return color_masks


def find_centre(color_masks) -> dict:
    centre_points = {}
    for key in color_masks.keys():
        contours, layer = cv2.findContours(color_masks[key], cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)  # 返回边缘点集
        # 初始化物体中心，center是一个包含两个整数的元组，表示轮廓的质心坐标
        if len(contours) > 0:  # 说明检测到轮廓
            # 找到面积最大的轮廓的点集，从轮廓列表中，计算出面积最大的轮廓的点集。contourArea是计算轮廓面积的函数。
            # max的第一个参数：可以为一个列表。第二个参数：固定为   key=功能函数。
            # 作用：从列表中遍历成员实现功能函数。
            max_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_contour)
            cv2.rectangle(color_masks[key], (x, y), (x + w, y + h), (255, 255, 255), 2)
            # 计算中心点
            if w < 300 or h < 300:
                continue
            else:
                centre_x = int(x + w // 2)
                centre_y = int(y + h // 2)
                centre_points[key] = (centre_x, centre_y)

    return centre_points


def qr_decode(frame):
    """
    :param frame: 图片对象
    :return: 二维码扫描结果的字符串
    """
    qrcode = cv2.QRCodeDetector()  # 初始化二维码识别对象
    qr, points, code = qrcode.detectAndDecode(frame)
    if code is None:
        return None
    else:
        return qr


def cal_horizontal_distance(frame, point):
    x0, y0 = point
    # 降噪
    blur = cv2.medianBlur(frame, 11)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    # 灰色掩膜
    gray_lower = np.array([100, 0, 80])
    gray_upper = np.array([130, 10, 255])
    gray_mask = cv2.inRange(hsv, gray_lower, gray_upper)
    # 黄色掩膜
    yellow_lower_1 = np.array([15, 0, 100])
    yellow_upper_1 = np.array([25, 20, 255])
    yellow_mask_1 = cv2.inRange(hsv, yellow_lower_1, yellow_upper_1)
    yellow_lower_2 = np.array([50, 0, 100])
    yellow_upper_2 = np.array([80, 20, 255])
    yellow_mask_2 = cv2.inRange(hsv, yellow_lower_2, yellow_upper_2)
    yellow_mask = cv2.bitwise_or(yellow_mask_1, yellow_mask_2)
    # 将掩模进行位运算以提取交界处的边缘
    mask = cv2.bitwise_or(gray_mask, yellow_mask)

    edges = cv2.Canny(mask, 50, 150)
    # 使用霍夫变换检测直线
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    min_distance = float('inf')
    closest_line = None
    if lines is not None:
        # 检测从摄像头边框到最短距离的直线
        for line in lines:
            rho, theta = line[0]
            a, b, c = np.cos(theta), np.sin(theta), -rho  # 直线的系数
            # 计算点 (x0, y0) 到直线的距离
            distance = abs(a * x0 + b * y0 + c) / np.sqrt(a ** 2 + b ** 2) / 5.65  # 5.65 是像素转换成实际距离的比例
            # 找到最小距离的直线
            if distance < min_distance:
                min_distance = distance
                closest_line = line
        # rho, theta = closest_line[0]
        # if abs(theta - np.pi / 2) < 1:
        #     a = np.cos(theta)
        #     b = np.sin(theta)
        #     x0 = a * rho
        #     y0 = b * rho
        #     x1 = int(x0 + 1000 * (-b))
        #     y1 = int(y0 + 1000 * (a))
        #     x2 = int(x0 - 1000 * (-b))
        #     y2 = int(y0 - 1000 * (a))
        #     cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    return min_distance, closest_line


def closest2centre(points: dict) -> tuple[float, float]:
    if points:
        # 解包中心点的坐标
        centre_x, centre_y = (960, 540)
        check_list = []  # 存储的是监测点到中心点的距离
        for color, (point_x, point_y) in points.items():
            dy = centre_y - point_y
            dx = centre_x - point_x
            distance = math.sqrt(dx * dx + dy * dy)
            check_list.append((distance, color))

        closest_point = points[min(check_list, key=lambda x: x[0])[1]]
    else:
        closest_point = (-1, -1)
    return closest_point


"""
实测下来该方法检测准确度不高，暂时弃用
def find_circle_centre(frame):
    :param frame: 图片对象
    :return: 返回圆心坐标和半径
    frame_open = cv2.morphologyEx(frame, cv2.MORPH_OPEN, k)  # 开运算一次
    frame_close = cv2.morphologyEx(frame_open, cv2.MORPH_CLOSE, k)  # 闭运算一次
    edges = cv2.Canny(frame_close, 50, 150)  # 做边缘算法检测
    # cv2.imshow('edges', edges)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1, minDist=300, param1=200, param2=100, minRadius=100,
                               maxRadius=0)
    # 对结果进行霍夫圆检测
    if circles is not None:  # 至少检测到一个圆
        circles = np.round(circles[0, :]).astype("int")
        # print(circles)
        # TODO:找到目标的圆心，暂时还没想到什么筛选条件
        return circles
    else:
        print("No circles")
        return None
"""
