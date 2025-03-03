#include <Arduino.h>

enum PacketCommand : uint8_t {
    CMD_SERVO = 0,
    CMD_PWM = 1,
    CMD_SCREEN = 2,
    CMD_REBOOT = 0xff
};

struct Packet_Request {
    PacketCommand command;
    union {
        struct {
            int32_t id;
            int32_t value;
            bool is_block;
        } servo;
        struct {
            // uint8_t id;
            int32_t value;
        } pwm;
        struct {
            char text[20];
        } screen;
    };
} __attribute__((packed));

struct Packet_Response {
    uint8_t happy;
} __attribute__((packed));

union Packet {
    uint8_t buffer[1];
    struct {
        uint8_t hello;
        uint8_t length;
        union {
            Packet_Request request;
            Packet_Response response;
        };
    } __attribute__((packed));
};

namespace com_module {
    void setup();
    void update();
}