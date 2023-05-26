import json
import os

from my_exceptions import MyException
from requests_functions import get_vtope_btoken
from settings.settings import MY_LOGGER, BASE_DIR


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

        # Проверяем наличие utoken
        if api_values.get('utoken'):
            btoken = get_vtope_btoken(utoken=api_values.get('utoken'))  # Получаем btoken в сервисе vtope

            if btoken:
                # Записываем Telegram ID, Telegram username и atoken в api_keys.json
                api_values['vtope_btoken'] = btoken
                with open(file=api_values_file_path, mode='w', encoding='utf-8') as file:
                    json.dump(obj=api_values, fp=file, indent=4)
                return '2'

        else:
            MY_LOGGER.warning('Токены для vtope не найдены! Пожалуйста внесите хотя бы utoken в файл api.keys.json\n'
                              'Его можно скопировать из ЛК сервиса vtope.')
            raise MyException(message='В файле api_keys.json отсутствует utoken для сервиса vtope')
            return  # TODO: потом убрать, так как тут ф-я закончится

    # TODO: дописать условие его тело для выбора socpanel



