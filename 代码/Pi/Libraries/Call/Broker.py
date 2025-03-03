from abc import abstractmethod, ABCMeta
from typing import List
from threading import Lock


class Observer(metaclass=ABCMeta):
    modify_lock = Lock()

    def attach(self, notification: "Notification"):
        with Observer.modify_lock:
            if len(notification.observers) == 0:
                notification.start()
            if self not in notification.observers:
                notification.observers.append(self)

    def detach(self, notification):
        with Observer.modify_lock:
            if self in notification.observers:
                notification.observers.remove(self)
            if len(notification.observers) == 0:
                notification.stop()

    @abstractmethod
    def update(self, name, notice):
        pass


class Notification(metaclass=ABCMeta):
    def __init__(self, name):
        self.observers: List[Observer] = []
        self.notice_name = name

    def set_notice_name(self, name):
        self.notice_name = name

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def notify(self, notice):
        for observer in self.observers:
            observer.update(self.notice_name, notice)
