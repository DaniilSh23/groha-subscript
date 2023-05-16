import json
import os
import re
from typing import List

from my_exceptions import MyException
from settings.settings import MY_LOGGER, BASE_DIR


def validate_settings(setting_name, value) -> re.Match | None:
    """
    Валидация настроек из файла limit.json. Вернёт объект re.Match или None
    """
    settings = (
        ('time_auth_accounts', r'^\d+-\d+'),  # Диапазон чисел через дефис (10-40)
        ('subscription_account_limit', r'^\d+'),  # Целое число
        ('failed_attempt', r'^\d+'),
        ('flood_account', r'^\d+'),
        ('time_auth_service', r'^\d+-\d+'),
        ('stream_account', r'^\d+'),
    )
    for i_setting, i_pattern in settings:
        if i_setting == setting_name:
            check_rslt = re.match(pattern=i_pattern, string=value)
            return check_rslt


def check_settings() -> dict:
    """
    Функция для проверки настроек из файла limit.json
    Возвращает словарь с настройками.
    """
    # Открываем и преобразуем в словарь json файл с настройками
    with open(file=os.path.join(BASE_DIR, 'settings', 'limit.json'), mode='r', encoding='utf-8') as file:
        limits_dct: dict = json.load(fp=file)
    for i_setting in ('time_auth_accounts', 'subscription_account_limit', 'failed_attempt',
                      'flood_account', 'time_auth_service', 'stream_account'):
        # Проверяем, что настройка введена и она корректна
        if limits_dct.get(i_setting) and validate_settings(setting_name=i_setting, value=limits_dct.get(i_setting)):
            MY_LOGGER.success(f'Настройка найдена: {i_setting, limits_dct[i_setting]}')
        else:
            MY_LOGGER.warning(f'Настройка {i_setting} НЕ найдена!')
            # Запрашиваем настройку, пока не введёт корректно
            while True:
                user_input = input('Введите значение для настройки >>> ')
                check_rslt = validate_settings(setting_name=i_setting, value=user_input)
                if check_rslt:
                    limits_dct[i_setting] = user_input
                    break
                else:
                    MY_LOGGER.info(f'Значение {user_input} не валидно. Введите корректное значение.')
    return limits_dct


def check_accounts(thread_numbs: int) -> str:
    """
    Функция для проверки наличия аккаунтов и их количества.
    Возвращает число потоков (строка, чтобы дальше изменит словарь с настройками,
    а в словаре данные лежат в виде строки. Так что не будем портить фен-шуй).
    """
    acc_dir_path = os.path.join(BASE_DIR, 'accounts')
    acc_pairs_numb = 0

    # Шерстим все файлы в директории accounts
    for i_file in os.listdir(acc_dir_path):
        if os.path.isfile(os.path.join(acc_dir_path, i_file)) and os.path.splitext(i_file)[1] == '.session':
            i_file_name = os.path.splitext(i_file)[0]

            # Проверяем, что существует пара файлов session-json
            if os.path.exists(os.path.join(acc_dir_path, f'{i_file_name}.session')) and \
                    os.path.exists(os.path.join(acc_dir_path, f'{i_file_name}.json')):
                acc_pairs_numb += 1
            else:
                MY_LOGGER.warning(f'Не найдена пара файлов session-json для {i_file}')

    if acc_pairs_numb == 0:
        MY_LOGGER.warning(f'Не обнаружены аккаунты в папке accounts. '
                          f'Пожалуйста, добавьте аккаунты в указанную папку и повторите запуск скрипта')
        raise MyException(message='Не обнаружены аккаунты в папке accounts.')

    # Если кол-во потоков больше, чем аккаунтов
    elif thread_numbs > acc_pairs_numb:
        MY_LOGGER.warning(f'Количество потоков {thread_numbs!r} больше, чем аккаунтов {acc_pairs_numb!r}. '
                          f'Уменьшаем число потоков до {acc_pairs_numb}!')
        thread_numbs = acc_pairs_numb
    return str(thread_numbs)


def check_proxy_file() -> List:
    """
    Функция для проверки файла с проксями.
    Возвращает список валидных проксей.
    """
    MY_LOGGER.debug(f'Проверяем прокси на валидность.')
    proxys_rlst = []
    with open(file=os.path.join(BASE_DIR, 'settings', 'proxy.txt'), mode='r', encoding='utf-8') as file:
        for i_line in file:
            i_proxy_lst = i_line.split(':')
            i_proxy_lst[2] = int(i_proxy_lst[2])
            for_check = (
                ('http', 'https', 'socks4', 'socks5'),
                r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
                range(0, 65536),
            )
            i_check_rslt = []
            for i_indx, i_elem in enumerate(i_proxy_lst[:3]):

                if i_indx == 1:  # Проверяем IP
                    MY_LOGGER.debug(f'Проверка домена прокси')
                    # i_check_rslt.append(True if re.match(for_check[1], i_elem) else False)
                    continue    # Пока пропускаем

                i_check_rslt.append(i_elem in for_check[i_indx])  # Проверка протокола или порта
            if all(i_check_rslt):  # Если прокся валидна
                proxys_rlst.append(i_line.replace('\n', ''))
                MY_LOGGER.debug(f'Прокся валидна: {i_line}')
            else:
                MY_LOGGER.warning(f'Невалидная запись о проксе: {i_line}. Пропускаем её...')
    return proxys_rlst
