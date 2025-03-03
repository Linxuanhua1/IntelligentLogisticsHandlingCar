from abc import abstractmethod, ABCMeta

class StreamIn(metaclass=ABCMeta):
    @abstractmethod
    def put(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

class StreamOut:
    def __init__(self):
        self.stream = None

    def get(self):
        return self.stream.put()

    def bind(self, stream_in: StreamIn):
        self.stream = stream_in
        self.stream.start()

    def unbind(self):
        self.stream.stop()
        # print("Stream stopped")
