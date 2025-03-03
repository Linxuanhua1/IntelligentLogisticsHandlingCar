import cv2
import socket
import time
import numpy as np
import json
import queue
import threading
import zmq
import base64


class SocketRecoCameraSender:
    def __init__(self, stream_queue: queue.Queue, port: int = 5001):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.PUB)
        self.sock.bind(f"tcp://*:{port}")

        self.stream_queue = stream_queue
        self.on_stream: bool = False

    def _send(self):
        frame = self.stream_queue.get()
        _, buffer = cv2.imencode('.jpg', frame)
        data = base64.b64encode(buffer.tobytes())
        self.sock.send(data)
        

    def _main_loop(self):
        while self.on_stream:
            self._send()

    def start(self):
        self.thread = threading.Thread(target=self._main_loop)
        self.thread.daemon = True
        self.on_stream = True
        self.thread.start()

    def stop(self):
        self.on_stream = False

    def _close(self):
        self.sock.close()


class SocketRecoPartSender:
    def __init__(self, stream_queue: queue.Queue, port: int = 5002):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.PUB)
        self.sock.bind(f"tcp://*:{port}")

        self.stream_queue = stream_queue
        self.on_stream: bool = False

    def _send(self):
        frame = self.stream_queue.get()
        _, buffer = cv2.imencode('.jpg', frame)
        data = base64.b64encode(buffer.tobytes())
        self.sock.send(data)

    def _main_loop(self):
        while self.on_stream:
            self._send()

    def start(self):
        self.thread = threading.Thread(target=self._main_loop)
        self.thread.daemon = True
        self.on_stream = True
        self.thread.start()

    def stop(self):
        self.on_stream = False

    def _close(self):
        self.sock.close()


class SocketQRCameraSender:
    def __init__(self, stream_queue: queue.Queue, port: int = 5003):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.PUB)
        self.sock.bind(f"tcp://*:{port}")

        self.stream_queue = stream_queue
        self.on_stream: bool = False

    def _send(self):
        frame = self.stream_queue.get()
        _, buffer = cv2.imencode('.jpg', frame)
        data = base64.b64encode(buffer.tobytes())
        self.sock.send(data)

    def _main_loop(self):
        while self.on_stream:
            self._send()

    def start(self):
        self.thread = threading.Thread(target=self._main_loop)
        self.thread.daemon = True
        self.on_stream = True
        self.thread.start()

    def stop(self):
        self.on_stream = False

    def _close(self):
        self.sock.close()


class SocketDataSender:
    def __init__(self, stream_queue: queue.Queue, port: int = 5004):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.PUB)
        self.sock.bind(f"tcp://*:{port}")

        self.stream_queue = stream_queue
        self.on_stream: bool = False

    def _send(self):
        buffer: str = self.stream_queue.get()
        data = base64.b64encode(buffer.encode("utf-8"))
        self.sock.send(data)

    def _main_loop(self):
        while self.on_stream:
            self._send()

    def start(self):
        self.thread = threading.Thread(target=self._main_loop)
        self.on_stream = True
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.on_stream = False

    def _close(self):
        self.sock.close()


# class Log:
#     def __init__(self, data: str, level: str = "info"):
#         self.time = time.time()
#         self.data = data
#         self.level = level
#
#     def __str__(self):
#         return json.dumps({
#             "time": self.time,
#             "data": self.data,
#             "level": self.level
#         })