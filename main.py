from check_functions import check_settings, check_accounts, check_proxy_file
from settings.settings import MY_LOGGER
from work_on_assignment_vtope import main_work_on_assignment_vtope
from work_with_services import choose_service_new, get_tasks, send_task_error_to_vtope, send_success_to_vtope


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
    target, task_id = get_tasks(service=chosen_service)

    # Работа по заданию
    work_rslt = main_work_on_assignment(limits_dct=limits_dct, target=target)

    # TODO: дописать обработку результатов с учётом сервисов socpanel и vtope. Пока сделано только для vtope
    MY_LOGGER.debug(f'Обрабатываем результаты работы по заданию')
    if work_rslt[2]:
        MY_LOGGER.debug(f'Обрабатывается вариант, когда от сервиса получена невалидная ссылка на канал(чат).')
        send_task_error_to_vtope(task_id=task_id)
    elif len(work_rslt[1]):
        MY_LOGGER.debug(f'Обрабатывается вариант, когда не все потоки успешно завершили работу.')
        MY_LOGGER.info(f'Не все потоки завершили работу успешно. '
                       f'{len(work_rslt[1])} потоков прервались из-за неожиданного исключения.\n'
                       f'Количество успешно подписавшихся аккаунтов: {work_rslt[0][0]} | '
                       f'всего было запущено аккаунтов: {work_rslt[0][0]}\n'
                       f'Какие будут дальнейшие действия?\n'
                       f'\tENTER - сказать сервису, что задание успешно выполнено\n'
                       f'\tCTRL+C - завершить скрипт')
        input()
        send_success_to_vtope(task_id=task_id)
    else:
        MY_LOGGER.debug(f'Обрабатывается вариант, когда задание выполнено.')
        MY_LOGGER.success(f'Задание выполнено. Потоки завершили свою работу. '
                          f'Успешно отработавших аккаунтов: {work_rslt[0][0]} | Всего аккаунтов: {work_rslt[0][1]}\n'
                          f'Отправляю запрос на проверку задания.')
        send_success_to_vtope(task_id=task_id)

    MY_LOGGER.success(f'Ну всё, чё...\nСпасибо.\nС уважением, скрипт.')


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
