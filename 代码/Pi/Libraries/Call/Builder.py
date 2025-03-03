from abc import abstractmethod, ABCMeta


class Unpack(metaclass=ABCMeta):
    @abstractmethod
    def unpack(self):
        pass


class SetParameter(metaclass=ABCMeta):
    @abstractmethod
    def unpack_parameter(self):
        pass


class Parameter(metaclass=ABCMeta):
    @abstractmethod
    def set_parameter(self, *args, **kwargs):
        pass


def builder(cls, config):
    return cls(*config.unpack())


def set_parameter(o, config):
    o.set_parameter(*config.unpack_parameter())
