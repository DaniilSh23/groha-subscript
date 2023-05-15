from settings.settings import MY_LOGGER
from my_exceptions import MyException


def get_vtope_acc_status():
    """
    Запрос на получение статуса аккаунта в сервисе vtope
    """
    # TODO: пока это заглушка, потом надо доделать. Тут же обработка неудачного запроса
    response = {"status": "ok", "quality": 1, "earned": 0, "earned_today": 0}

    if response.get('status') == 'ok' and response.get('quality') > 0:
        return True
    else:
        MY_LOGGER.warning(f'Ваш аккаунт ещё не прошёл проверку. Пожалуйста, перезапустите скрипт позже.\n'
                          f'Из описания vtope, аккаунт должен пройти "непродолжительную" проверку')
        raise MyException(message='Аккаунт не прошёл проверку vtope или получил иную ошибку. '
                                  f'Ответ на запрос о статусе аккаунта vtope: {response}')


def get_vtope_atoken():
    """
    Запрос для получения atoken в сервисе vtope
    """
    # TODO: заглушка, потом дописать. Тут же обработка неудачного запроса
    response = {"atoken": "zMCebNgjMcmhks77cAfAqNG0LETF7GhY"}
    if response.get('atoken'):
        return response
    else:
        MY_LOGGER.warning(f'Не удалось выполнить запрос к vtope для получения atoken.')
        raise MyException(message=f'Не удалось выполнить запрос к vtope для получения atoken. Ответ vtope: {response}')


def get_vtope_btoken():
    """
    Запрос для получения btoken в сервисе vtope.
    """
    # TODO: заглушка, потом дописать. Тут же обработка неудачного запроса
    response = {"btoken": "hVEKtDL6eE95g6IeNyl9cAty1iDYln4r", "points": 100, "and_other_keys": "with_some_values"}
    if response.get('btoken'):
        return response
    else:
        MY_LOGGER.warning(f'Не удалось выполнить запрос к vtope для получения atoken.')
        raise MyException(message=f'Не удалось выполнить запрос к vtope для получения atoken. Ответ vtope: {response}')
