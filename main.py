from check_functions import check_settings, check_accounts, check_proxy_file
from settings.settings import MY_LOGGER
from work_on_assignment import main_work_on_assignment
from work_with_services import choose_service_new, get_tasks


@MY_LOGGER.catch
def main():
    limits_dct = check_settings()
    limits_dct["stream_account"] = check_accounts(thread_numbs=int(limits_dct.get("stream_account")))

    proxys_lst = check_proxy_file()
    if len(proxys_lst) == 0:
        MY_LOGGER.warning(f'Не найдено валидных записей в файле proxy.txt\n'
                          f'Пожалуйста, заполните файл по шаблону: протокол:айпи:порт:логин:пароль\n'
                          f'Например: http:127.0.0.1:5000:login:password\n'
                          f'Логин и пароль необязательно, то есть можно и так: socks5:127.0.0.3:65535\n'
                          f'CTRL+C - Остановить скрипт')
    else:
        MY_LOGGER.success(f'Найдено {len(proxys_lst)} прокси')

    chosen_service = choose_service_new()  # 1 - socpanel, 2 - vtope

    # TODO: target - это ссылка на канал или username, её надо будет вытягивать из ответа на запрос,
    #  пока просто указал, чтобы было
    target = get_tasks(service=chosen_service)

    # Работа по заданию
    main_work_on_assignment(limits_dct=limits_dct, target=target)


if __name__ == '__main__':
    main()
