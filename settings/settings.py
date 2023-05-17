import datetime
import os
import sys

import pytz
from loguru import logger

DEBUG = False

# Настраиваем запись логов
MY_LOGGER = logger
MY_LOGGER.remove()
MY_LOGGER.add(  # системные логи в файл
    sink=f'logs/sys_logs_{datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y_%H:%M:%S")}.log',
    filter=lambda rec: rec['level'].name in ('DEBUG', 'CRITICAL', 'ERROR'),
    rotation='10 MB',
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True
)
MY_LOGGER.add(
    sink=f'logs/logs_{datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y_%H:%M:%S")}.log',
    filter=lambda rec: rec['level'].name in ('INFO', 'WARNING', 'SUCCESS'),
    rotation='10 MB',
    compression="zip",
    enqueue=True
)  # обычные логи в файл
if DEBUG:
    MY_LOGGER.add(sink=sys.stdout)  # Все логи в терминал
else:
    MY_LOGGER.add(sink=sys.stdout, filter=lambda rec: rec['level'].name != 'DEBUG')  # в терминал все логи, кроме DEBUG


# Абсолютный путь к директории проекта
BASE_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
