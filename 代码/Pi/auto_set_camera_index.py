import subprocess
import time


def run_command(command):
    """运行 shell 命令并返回输出"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def check_camera_mappings(output):
    """检查 qr_camera 和 reco_camera 是否映射到 video0 或 video4"""
    qr_camera = None
    reco_camera = None

    for line in output.splitlines():
        if 'qr_camera' in line:
            if 'video0' in line or 'video4' in line:
                qr_camera = True
        if 'reco_camera' in line:
            if 'video0' in line or 'video4' in line:
                reco_camera = True

    return qr_camera and reco_camera


def main():
    while True:
        # 重新加载规则并触发
        subprocess.run("sudo udevadm control --reload-rules", shell=True)
        subprocess.run("sudo udevadm trigger", shell=True)

        time.sleep(0.2)
        # 获取 /dev 列表并过滤与 camera 相关的内容
        output = run_command("ls -l /dev | grep camera")

        # 打印输出以便调试（可选）
        print(output)

        # 检查相机映射
        if check_camera_mappings(output):
            print("qr_camera 和 reco_camera 映射到 video0 或 video4，停止运行")
            break


if __name__ == "__main__":
    main()
