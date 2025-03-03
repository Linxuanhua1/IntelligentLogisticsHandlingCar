from abc import abstractmethod, ABCMeta


class Handle(metaclass=ABCMeta):
    @abstractmethod
    def set_next(self, *args, **kwargs):
        pass

    @abstractmethod
    def set(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def stop(self):
        pass