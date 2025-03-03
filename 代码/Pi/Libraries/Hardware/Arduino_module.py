import serial
import logging
import struct
from enum import IntEnum


logger = logging.getLogger(__name__)


class PacketCommand(IntEnum):
    CMD_SERVO = 0
    CMD_PWM = 1
    CMD_SCREEN = 2
    CMD_REBOOT = 0xff


class Arduino:
    def __init__(self, interface: str, rate: int):
        self._ser = serial.Serial(interface, rate)
        if not self._ser.is_open:
            raise Exception("Arduino串口打开失败")

    @staticmethod
    def _pack_request(command, data):
        if command == PacketCommand.CMD_SERVO:
            packed_data = struct.pack('<ii?', data['id'], data['value'], data['is_block'])
        elif command == PacketCommand.CMD_PWM:
            packed_data = struct.pack('<i', data['value'])
        elif command == PacketCommand.CMD_SCREEN:
            text = data['text'].encode('utf-8')
            packed_data = struct.pack('<7s', text)
        else:
            raise ValueError("?")

        return struct.pack('<B', command) + packed_data

    def _pack_packet(self, command, data):
        request = self._pack_request(command, data)
        length = len(request)
        hello = 0x66
        return struct.pack('<BB', hello, length) + request

    def _unpack_response(self, buffer):
        response_format = '<BBB'
        hello, length, dummy = struct.unpack(response_format, buffer)
        return {
            'hello': hello,
            'length': length,
            'response': {'dummy': dummy},
        }

    def _send(self, command: PacketCommand, data):
        packet = self._pack_packet(command, data)
        self._ser.write(packet)
        self._ser.flush()

    def _wait_ok(self):
        buffer = self._ser.read(3)
        response = self._unpack_response(buffer)
        return response["response"]["dummy"] == b'\x06'

    def servo(self, servo_id: int, degree: int, is_block: bool) -> bool:
        if 180 < degree < 0:
            logger.warning("输入的PWN角度有误")
            return False
        self._send(PacketCommand.CMD_SERVO, {'id': servo_id, 'value': degree, 'is_block': is_block})
        return self._wait_ok()

    def monitor(self, prt_str: str) -> bool:
        self._send(PacketCommand.CMD_SCREEN, {'text': prt_str})
        return self._wait_ok()

    def pwm(self, value: int) -> bool:
        self._send(PacketCommand.CMD_PWM, {'value': value})
        return self._wait_ok()


# if __name__ == "__main__":
#     Test = Arduino('/dev/ttyAMA1', 9600, b'\xFF')
#     while True:
#         Test._send([2], "OK")
#         sleep(2)
