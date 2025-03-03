from Libraries.Software.Socket import SocketRecoCameraSender, SocketDataSender
import cv2
import queue
import threading
import time
import json
import random

stream_queue = queue.Queue()
data_queue = queue.Queue()

socket_stream = SocketRecoCameraSender(stream_queue=stream_queue)
socket_stream.start()

socket_data = SocketDataSender(stream_queue=data_queue)
socket_data.start()

def data_send():
    while True:
        log = {
            "time": time.time(),
            "data": f"test{random.randint(0, 100)}",
            "level": "info"
        }
        data_queue.put(json.dumps(log))
        time.sleep(1)
        print("sending data")

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    last_time = time.time()
    count = 0

    while True:
        if time.time() - last_time < 0.05:
            continue
        last_time = time.time()
        ret, frame = cap.read()
        if not ret:
            print("Restarting video...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 将视频位置设置为第0帧
            continue
        stream_queue.put(frame)
        count += 1
        print(f"sending frame {count}")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

video_path = 'c:/Users/shila/Videos/2024-02-17 03-45-17.mp4'
video_thread = threading.Thread(target=read_video, args=(video_path,))
video_thread.start()

data_theard = threading.Thread(target=data_send)
data_theard.start()