import RPi.GPIO as GPIO
import time
import subprocess

# 设置 GPIO 模式为 BCM
GPIO.setmode(GPIO.BCM)

# 定义按钮连接的 GPIO 引脚
button_pin = 17

# 设置引脚模式为输入，并使用上拉电阻（默认高电平）
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 检测按钮是否长按，防止误触
try:
    while True:
        # 读取按钮状态
        if GPIO.input(button_pin) == GPIO.LOW:
            print("Button Pressed")
            # 开始计时
            press_start_time = time.time()
            while GPIO.input(button_pin) == GPIO.LOW:
                # 检查持续按下的时间
                if time.time() - press_start_time >= 1:  # 持续按下超过 1 秒
                    print("Button pressed for 1 second, running main.py")
                    subprocess.run(['/root/python_venv/bin/python3', '/root/Pi/main.py'])
                    break  # 跳出内层循环，避免重复运行
        # 等待一段时间，避免过于频繁的读取
        time.sleep(1)

finally:
    # 清理 GPIO 状态
    GPIO.cleanup()
