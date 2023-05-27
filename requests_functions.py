import random
from typing import Tuple

import requests

from settings.settings import MY_LOGGER
from my_exceptions import MyException


def get_vtope_acc_status(atoken: str) -> bool | None:
    """
    Запрос на получение статуса аккаунта в сервисе vtope
    """

    req_url = f'https://vto.pe/botapi/m/account?atoken={atoken}'
    response = requests.get(url=req_url)
    resp_data = response.json()
    MY_LOGGER.debug(f'Ответ vtope на проверку статуса акка по atoken == {atoken!r}.\n{response.text}')
    if resp_data.get('status') == 'ok' and resp_data.get('quality') > 0:
        return True
    else:
        MY_LOGGER.warning('Аккаунт не прошёл проверку vtope или получил иную ошибку. '
                          f'Ответ на запрос: {response.text}')


def get_vtope_atoken(btoken, tlg_id, tlg_username) -> str | None:
    """
    Запрос для получения atoken в сервисе vtope
    """

    req_url = f'https://vto.pe/botapi/m/account?btoken={btoken}&id={tlg_id}&nick={tlg_username}'
    response = requests.get(url=req_url)
    resp_data = response.json()
    if resp_data.get('atoken'):
        MY_LOGGER.success(f'Успешный запрос для получения atoken vtope')
        MY_LOGGER.debug(f'Получен atoken для акка {tlg_id!r}|{tlg_username}. Его значение {resp_data.get("atoken")!r}')
        return resp_data.get('atoken')
    else:
        MY_LOGGER.warning(f'Не удалось выполнить запрос к vtope для получения atoken. Ответ vtope: {response.text}')


def get_vtope_btoken(utoken: str) -> str:
    """
    Запрос для получения btoken в сервисе vtope.
    Возвращает btoken
    """

    auth_url = f'https://vto.pe/botapi/user?utoken={utoken}&device=moikompahule&program=SubScript&bot=TestBot'
    response = requests.get(url=auth_url)
    resp_data = response.json()

    if resp_data.get('btoken'):
        return resp_data.get('btoken')
    else:
        MY_LOGGER.warning(f'Не удалось выполнить запрос к vtope для получения btoken.')
        raise MyException(message=f'Не удалось выполнить запрос к vtope для получения btoken. '
                                  f'Ответ vtope: {response.text}')


def get_vtope_subs_task(atoken: str) -> Tuple:
    """
    Функция для получения заданий на подписку из vtope
    Возвращаем Tuple(successed: bool, response_data: dict | description: str)
    """
    MY_LOGGER.debug(f'Получаем задания на подписку во vtope')

    # TODO: заглушка на получение заданий, потом удалить
    rand_target = random.choice(
        (
            'https://t.me/+1ZKtuEk_ivk2NmZi',
            'https://t.me/+2vriZ41DymY2ZjYy',
            # 'https://t.me/test_channel_for_my_bot32',
        )
    )
    return True, {'shortcode': rand_target, 'id': 0}
    # TODO: ==============================================

    url = "https://tasks.vto.pe/botapi/tasks/m/follow"
    querystring = {"atoken": atoken}
    response = requests.get(url, params=querystring)

    if response.status_code not in [200, 400]:
        MY_LOGGER.warning(f'Неудачный запрос к сервису vtope. Ответ: {response.text}')

    MY_LOGGER.debug(f'Обработка ответа на запрос задания во vtope. Ответ vtope: {response.text}')
    response_data = response.json()
    if response_data.get('id'):
        MY_LOGGER.success(f'ЗАДАНИЕ ПОЛУЧЕНО УСПЕШНО. ОТВЕТ: {response_data}')
        return True, response_data

    elif response_data.get('error') == 'invalid':
        MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. Описание: atoken не найден')
        return False, 'atoken не найден'

    elif response_data.get('error') == 'validating':
        MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. Описание: аккаунт проверяется')
        return False, 'аккаунт ещё не проверен'

    elif response_data.get('error') == 'notfound':
        MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. '
                          'Описание: аккаунт проверен и не найден/заблокирован')
        return False, 'аккаунт не найден или заблокирован'

    elif response_data.get('error') == 'notask':
        MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. Описание: нет задания для выполнения')
        return False, 'нет заданий для выполнения'

    elif response_data.get('error') == 'wait':
        MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. '
                          'Описание: слишком часто запрашивается задание. При частых запросах возможен бан!')
        return False, 'аккаунт слишком часто запрашивает задания'

    elif response_data.get('error') == 'badquality':
        MY_LOGGER.warning('При запросе заданий из vtope получена ошибка. Описание: аккаунт 0 уровня качества')
        return False, 'аккаунт низкого качества'

    else:
        MY_LOGGER.warning(f'Получен ответ от vtope, неописанный в документации. Ответ: {response.text}')
        return False, 'получен ответ от vtope, неописанный в документации этого сервиса'


def send_success_to_vtope(task_id, atoken):
    """
    Отправка запроса к vtope об успешно выполненном задании.
    :param atoken:
    :param task_id:
    :return:
    """
    # TODO: запросы требуют реальной проверки

    MY_LOGGER.debug(f'Выполняем запрос к vtope')
    url = "https://tasks.vto.pe/botapi/tasks/m/done/ok"
    querystring = {"atoken": atoken, "id": task_id}
    response = requests.get(url, params=querystring)
    MY_LOGGER.debug(f'Подтверждение выполнения задания vtope, atoken={atoken!r}|task_id={task_id!r}. '
                    f'Ответ на запрос: {response.text}')

    if response.status_code not in [200, 400]:
        MY_LOGGER.warning(f'Неудачный запрос к сервису vtope. Ответ: {response.json()}')

    response_data = response.json()
    if response_data.get('error') == 'ok':
        MY_LOGGER.info(f'Задание vtope ID={task_id!r}|atoken={atoken!r} успешно отправлено на проверку.')
    elif response_data.get('error') == 'invalid':
        MY_LOGGER.warning(f'Задание vtope ID={task_id!r}|atoken={atoken!r}. Ответ vtope: не найден аккаунт/задание')


def send_task_error_to_vtope(task_id, atoken, err_type='taskerror'):
    """
    Отправка запроса к vtope для информирования об ошибке при выполнении задания из-за невалидной ссылки.
    :return:
    """
    # TODO: запросы требуют реальной проверки

    MY_LOGGER.debug(f'Выполняем запрос к vtope')
    url = f"https://tasks.vto.pe/botapi/tasks/m/done/{err_type}"
    querystring = {"atoken": atoken, "id": task_id}
    response = requests.get(url, params=querystring)
    MY_LOGGER.debug(f'Запрос на отмену задания vtope. Причина фэйла: {err_type!r}|task_id={task_id!r}|atoken={atoken!r}'
                    f'Ответ на запрос: {response.text}')

    if response.status_code not in [200, 400]:
        MY_LOGGER.warning(f'Неудачный запрос к сервису vtope. Ответ: {response.json()}')

    response_data = response.json()
    if response_data.get('error') == 'ok':
        MY_LOGGER.info(f'Задание отмечено как невалидное.')
    elif response_data.get('error') == 'invalid':
        MY_LOGGER.warning(f'не найден аккаунт/задание')
