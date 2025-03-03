#include <Arduino.h>
#include "com.h"
#include "localservo.h"
#include "light.h"
#include "screen.h"
namespace com_module
{
    Packet *in;
    Packet *out;

    void setup()
    {
        Serial1.begin(115200);
        in = (Packet *)malloc(128);
        out = (Packet *)malloc(64);
    }

    uint8_t size;
    bool receiving = false;

    void handle(Packet *packet)
    {
        out->hello = 0x66;
        out->length = 1;
        out->response.happy = 6;
        switch (packet->request.command)
        {
        case CMD_SERVO:
            // Serial1.println(packet->request.servo.id);
            // Serial1.println(packet->request.servo.value);
            localservo::update(packet->request.servo.id, packet->request.servo.value, packet->request.servo.is_block);
            break;
        case CMD_PWM:
            light::update(packet->request.pwm.value);
            break;
        case CMD_SCREEN:
            screen::set(packet->request.screen.text);
            break;
        case CMD_REBOOT:
            watchdog_enable(1, 1);
            while(1);
        default:
            break;
        }
        for (auto i = 0; i < out->length + 2; i++)
        {
            Serial1.write(out->buffer[i]);
        }
    }

    void update()
    {
        while (Serial1.available())
        {
            uint8_t byte = Serial1.read();
            if (byte == 0x66 && !receiving)
            {
                size = 0;
                receiving = true;
            }
            if(!receiving) continue;
            in->buffer[size++] = byte;
            if (size > 2 && size - 2 == in->length)
            {
                handle(in);
                size = 0;
            }
            if (size > 20) {
                // fatal
                size = 0;
                receiving = false;
            }
        }
        // Serial1.write(0x11);
    }
}