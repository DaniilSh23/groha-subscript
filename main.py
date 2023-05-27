from check_functions import check_settings, check_accounts, check_proxy_file
from settings.settings import MY_LOGGER
from work_on_assignment_vtope import main_work_on_assignment_vtope
from work_with_services import choose_service_new


@MY_LOGGER.catch
def new_main():
    """
    Новая основная функция, с учётом принципа работы сервиса vtope
    """

    limits_dct = check_settings()
    limits_dct["stream_account"] = check_accounts(thread_numbs=int(limits_dct.get("stream_account")))

    proxy_lst = check_proxy_file()
    if len(proxy_lst) == 0:
        MY_LOGGER.warning(f'Не найдено валидных записей в файле proxy.txt\n'
                          f'Пожалуйста, заполните файл по шаблону: протокол:айпи:порт:логин:пароль\n'
                          f'Например: http:127.0.0.1:5000:login:password\n'
                          f'Логин и пароль необязательно, то есть можно и так: socks5:127.0.0.3:65535\n'
                          f'CTRL+C - Остановить скрипт')
    else:
        MY_LOGGER.success(f'Найдено {len(proxy_lst)} прокси')

    chosen_service = choose_service_new()  # 1 - socpanel, 2 - vtope
    if chosen_service == '2':
        work_rslt = main_work_on_assignment_vtope(limits_dct=limits_dct, proxy_lst=proxy_lst)
        MY_LOGGER.info(f'Потоки закончили работу. Успешно подписались {work_rslt[0]} аккаунтов из {work_rslt[1]}')

    else:
        MY_LOGGER.info(f'SOCPANEL ещё не проработана. Конец работы скрипта.')


if __name__ == '__main__':
    # main()
    new_main()
