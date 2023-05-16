import json
import os
import random
import time

import requests

from my_exceptions import MyException
from requests_functions import get_vtope_atoken, get_vtope_acc_status, get_vtope_btoken
from settings.settings import MY_LOGGER, BASE_DIR


def handling_if_exist_btoken(api_values_file_path: str, btoken=None):
    """
    Обработка, если установлен btoken
    """
    # Открываем файл и достаём json преобразовав его в словарь
    with open(file=api_values_file_path, mode='r', encoding='utf-8') as file:
        api_values: dict = json.load(fp=file)

    if not api_values.get('tlg_id'):
        while True:  # Запрос Telegram ID
            tlg_id = input('Введите Telegram ID Вашей учётной записи\n>>> ')
            if not tlg_id.isdigit():
                MY_LOGGER.warning(f'Telegram ID должен содержать только цифры, введённое Вами значение: {tlg_id}')
            else:
                break
    else:
        tlg_id = api_values.get('tlg_id')

    if not api_values.get('tlg_username'):
        tlg_username = input('Введите Telegram username Вашей учётной записи\n>>> ')
    else:
        tlg_username = api_values.get('tlg_username')

    resp = get_vtope_atoken()  # Запрос к vtope для получения atoken
    if resp:

        # Записываем Telegram ID, Telegram username и atoken в api_keys.json
        api_values['tlg_id'] = tlg_id
        api_values['tlg_username'] = tlg_username
        api_values['vtope_atoken'] = resp.get('atoken')
        if btoken:
            api_values['vtope_btoken'] = btoken
        with open(file=api_values_file_path, mode='w', encoding='utf-8') as file:
            json.dump(obj=api_values, fp=file, indent=4)


def choose_service_new():
    MY_LOGGER.info('Выбор сервиса для работы')
    # Запрашиваем выбор сервиса
    while True:
        user_choice = input('Выберите сервис для работы:\n1 - socpanel\n2 - vtope\n>>> ')
        if user_choice not in ('1', '2'):
            MY_LOGGER.warning('Неверный выбор! Пожалуйста, введите 1 - для выбора socpanel или 2 - для выбора vtope')
        else:
            MY_LOGGER.info(f"Вы выбрали: {'socpanel' if user_choice == '1' else 'vtope'!r}")
            break

    # Если выбран vtope
    if user_choice == '2':
        api_values_file_path = os.path.join(BASE_DIR, 'settings', 'api_keys.json')
        with open(file=api_values_file_path, mode='r', encoding='utf-8') as file:
            api_values: dict = json.load(fp=file)

        # Проверяем наличие внесённых значений для vtope
        for i_key in ['vtope_atoken', 'vtope_btoken', 'vtope_utoken']:
            i_value = api_values.get(i_key)

            # Если значение для atoken установлено
            if i_key == 'vtope_atoken' and i_value:
                resp = get_vtope_acc_status()  # Запрос на проверку статуса аккаунта в сервисе vtope
                if resp:
                    return '2'

            # Если значение для btoken установлено
            elif i_key == 'vtope_btoken' and i_value:
                handling_if_exist_btoken(api_values_file_path=api_values_file_path)

                # Запрос на проверку статуса аккаунта в сервисе vtope
                resp = get_vtope_acc_status()
                if resp:
                    return '2'

            # Если есть только utoken
            elif i_key == 'vtope_utoken' and i_value:
                resp = get_vtope_btoken()  # Получаем btoken в сервисе vtope
                if resp:
                    # Выполняем дальнейшую обработку, когда уже есть btoken
                    handling_if_exist_btoken(api_values_file_path=api_values_file_path, btoken=resp.get('btoken'))

                    # Запрос на проверку статуса аккаунта в сервисе vtope
                    resp = get_vtope_acc_status()
                    if resp:
                        return '2'
        else:
            MY_LOGGER.warning('Токены для vtope не найдены! Пожалуйста внесите хотя бы utoken в файл api.keys.json\n'
                              'Его можно скопировать из ЛК сервиса vtope.')
    # TODO: дописать условие его тело для выбора socpanel


def get_tasks(service: str, task_type: str = '1', ):
    """
    Функция для получения заданий.
    service - выбранный сервис(1 - socpanel, 2 - vtope)
    task_type - выбранный тип задания(1 - подписка, 2 - реакции)
    """
    MY_LOGGER.info(f'Выполняем поиск заданий на {"подписку" if task_type == "1" else "реакции"!r} '
                   f'в сервисе {"vtope" if service == "2" else "socpanel"!r}')

    MY_LOGGER.debug(f'Открываем файл с настройками API для сервисов vtope | socpanel')
    with open(file=os.path.join(BASE_DIR, 'settings', 'api_keys.json'), mode='r', encoding='utf-8') as file:
        api_values = json.load(fp=file)

    MY_LOGGER.debug(f'Открываем файл с ограничениями (limit.json)')
    with open(file=os.path.join(BASE_DIR, 'settings', 'limit.json'), mode='r', encoding='utf-8') as file:
        limit_values = json.load(fp=file)

    MY_LOGGER.debug('Форматируем диапазон таймаута между запросами заданий в сервисах')
    service_timeout_range = limit_values.get("time_auth_service").replace(' ', '').split('-')
    service_timeout_range[0] = int(service_timeout_range[0])
    service_timeout_range[1] = int(service_timeout_range[1])

    # TODO: сейчас тут заглушка на задание, потом убрать
    target = random.choice(
        (
            'https://t.me/+1ZKtuEk_ivk2NmZi',
            'https://t.me/test_channel_for_my_bot32',
            'https://t.me/+2vriZ41DymY2ZjYy'
        )
    )
    task_id = 0
    return target, task_id

    if service == '2':

        MY_LOGGER.debug(f'Выбран сервис vtope. Получаем задания')
        target = False
        while not target:

            url = "https://tasks.vto.pe/botapi/tasks/m/follow"
            querystring = {"atoken": api_values.get("vtope_atoken")}
            response = requests.get(url, params=querystring)

            if response.status_code not in [200, 400]:
                MY_LOGGER.warning(f'Неудачный запрос к сервису vtope. Ответ: {response.json()}')
                raise MyException(message=f'Неудачный запрос к сервису vtope. Ответ: {response.json()}')

            MY_LOGGER.debug(f'Обработка ответа на запрос задания во vtope')
            response_data = response.json()
            if response_data.get('id'):
                MY_LOGGER.success(f'ЗАДАНИЕ ПОЛУЧЕНО УСПЕШНО. ОТВЕТ: {response_data}')
                target = 'https://t.me/+2vriZ41DymY2ZjYy'   # TODO: задание получено, но пока заглушка, надо дописать
                task_id = response_data.get('id')

            elif response_data.get('error') == 'invalid':
                MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. Описание: atoken не найден')
                raise MyException(message='При запросе заданий из vtope получена ошибка. Описание: atoken не найден')

            elif response_data.get('error') == 'validating':
                MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. Описание: аккаунт проверяется')
                raise MyException(message='При запросе заданий из vtope получена ошибка. Описание: аккаунт проверяется')

            elif response_data.get('error') == 'notfound':
                MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. '
                                  'Описание: аккаунт проверен и не найден/заблокирован')
                raise MyException(message='При запросе заданий из vtope получена ошибка. '
                                          'Описание: аккаунт проверен и не найден/заблокирован')

            elif response_data.get('error') == 'notask':
                MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. Описание: нет задания для выполнения')
                sleep_time = random.randint(service_timeout_range[0], service_timeout_range[1])
                MY_LOGGER.info(f'Ожидание перед следующим запросом задания во vtope: {sleep_time} сек.')
                time.sleep(sleep_time)

            elif response_data.get('error') == 'wait':
                MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. '
                                  'Описание: слишком часто запрашивается задание. При частых запросах возможен бан!')
                MY_LOGGER.info(f'========== НАЖМИТЕ ENTER, ЧТОБЫ ПОВТОРИТЬ ЗАПРОС '
                               f'(CTRL+C - остановить скрипт) ==========')
                input()

            elif response_data.get('error') == 'badquality':
                MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. Описание: аккаунт 0 уровня качества')
                raise MyException(message='При запросе заданий из vtope получена ошибка. '
                                          'Описание: аккаунт 0 уровня качества')

            else:
                MY_LOGGER.warning(f'Получен ответ от vtope, неописанный в документации. Ответ: {response_data}')
                MyException(message=f'Получен ответ от vtope, неописанный в документации. Ответ: {response_data}')

    # TODO: описать логику для SOCPANEL
    else:
        target = 'https://t.me/test_channel_for_my_bot32'

        # # TODO: пока будет как заглушка, потом расписать исходя из API сервисов
        # target = 'https://t.me/test_channel_for_my_bot32'
        # target = 'https://t.me/+1ZKtuEk_ivk2NmZi'
        # target = 'https://t.me/+2vriZ41DymY2ZjYy'

    return target, task_id


def send_task_error_to_vtope(task_id):
    """
    Отправка запроса к vtope для информирования об ошибке при выполнении задания из-за невалидной ссылки.
    :return:
    """
    # TODO: запросы требуют реальной проверки

    MY_LOGGER.debug(f'Открываем файл с настройками API для сервисов vtope | socpanel')
    with open(file=os.path.join(BASE_DIR, 'settings', 'api_keys.json'), mode='r', encoding='utf-8') as file:
        api_values = json.load(fp=file)

    MY_LOGGER.debug(f'Выполняем запрос к vtope')
    url = "https://tasks.vto.pe/botapi/tasks/m/done/taskerror"
    querystring = {"atoken": api_values.get("vtope_atoken"), "id": task_id}
    response = requests.get(url, params=querystring)

    if response.status_code not in [200, 400]:
        MY_LOGGER.warning(f'Неудачный запрос к сервису vtope. Ответ: {response.json()}')
        raise MyException(message=f'Неудачный запрос к сервису vtope. Ответ: {response.json()}')

    response_data = response.json()
    if response_data.get('error') == 'ok':
        MY_LOGGER.info(f'Задание отмечено как невалидное.')
    elif response_data.get('error') == 'invalid':
        MY_LOGGER.warning(f'не найден аккаунт/задание')


def send_success_to_vtope(task_id):
    """
    Отправка запроса к vtope об успешно выполненном задании.
    :param task_id:
    :return:
    """
    # TODO: запросы требуют реальной проверки

    MY_LOGGER.debug(f'Открываем файл с настройками API для сервисов vtope | socpanel')
    with open(file=os.path.join(BASE_DIR, 'settings', 'api_keys.json'), mode='r', encoding='utf-8') as file:
        api_values = json.load(fp=file)

    MY_LOGGER.debug(f'Выполняем запрос к vtope')
    url = "https://tasks.vto.pe/botapi/tasks/m/done/ok"
    querystring = {"atoken": api_values.get("vtope_atoken"), "id": task_id}
    response = requests.get(url, params=querystring)

    if response.status_code not in [200, 400]:
        MY_LOGGER.warning(f'Неудачный запрос к сервису vtope. Ответ: {response.json()}')
        raise MyException(message=f'Неудачный запрос к сервису vtope. Ответ: {response.json()}')

    response_data = response.json()
    if response_data.get('error') == 'ok':
        MY_LOGGER.info(f'Задание успешно отправлено на проверку.')
    elif response_data.get('error') == 'invalid':
        MY_LOGGER.warning(f'не найден аккаунт/задание')
