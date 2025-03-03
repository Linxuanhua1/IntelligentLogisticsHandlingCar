import sys
import os
sys.path.append(os.path.abspath("/root/Pi"))
from Libraries.Hardware.Gyro_module import Gyro
from Libraries.Config import GyroConfig
from Libraries.Call import Builder
import logging
from typing import Optional

def configure_logger(
    log_file: Optional[str] = 'log.log',
    console_level: int = logging.DEBUG,
    file_level: int = logging.DEBUG,
    log_format: str = '%(asctime)s | %(name)s - %(funcName)s | %(levelname)s: %(message)s',
    date_format: str = '%Y-%m-%d %H:%M:%S',
    encoding: str = 'utf-8'
) -> logging.Logger:
    # 创建 Formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 获取全局日志器
    logger = logging.getLogger()
    logger.setLevel(min(console_level, file_level))  # 日志器级别设为最小的级别

    # 清除已有的 Handler，避免重复日志
    if logger.handlers:
        logger.handlers.clear()

    # 配置控制台日志 Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 配置文件日志 Handler（如果指定了日志文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='w', encoding=encoding)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger



logger = configure_logger()
test_gyro: Gyro = Builder.builder(Gyro, GyroConfig)
test_gyro.start()
