import sys
import os
sys.path.append(os.path.abspath("/root/Pi"))

import cv2
import Libraries.Software.Socket as Socket
import queue
from time import sleep

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 0)  # 默认亮度
cap.set(cv2.CAP_PROP_CONTRAST, 32)  # 默认对比度
cap.set(cv2.CAP_PROP_SATURATION, 64)  # 默认饱和度
cap.set(cv2.CAP_PROP_HUE, 0)  # 默认色调
cap.set(cv2.CAP_PROP_AUTO_WB, 0)  # 关闭自动白平衡
cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 3800)  # 设置手动白平衡，默认值4600
cap.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))  # 设置读取格式为MJPEG

stream_queue = queue.Queue()

socket = Socket.SocketRecoCameraSender(stream_queue)

socket.start()

while True:
    _, frame = cap.read()
    stream_queue.put(frame)
    sleep(0.03)




