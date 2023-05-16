import asyncio
import json
import math
import os
import random
import shutil
import threading
import time
from typing import List, Tuple
import socks

from telethon.errors import ChannelsTooMuchError, ChannelInvalidError, ChannelPrivateError, InviteHashEmptyError, \
    InviteHashExpiredError, InviteHashInvalidError, SessionPasswordNeededError, UsersTooMuchError, \
    UserAlreadyParticipantError
from telethon import TelegramClient
from telethon.network import connection
from telethon.tl import functions

from my_exceptions import MyException
from settings.settings import BASE_DIR, MY_LOGGER


async def do_subscription(client, target, thread_id) -> Tuple[int, str]:
    """
    Выполняем подписку на нужный канал или группу в Telegram.
    client - объект клиента telethon
    target - идентификатор(ссылка, юзернейм и т.п.) канала, на который надо подписаться
    thread_id - номер потока

    Коды возвратов этой функции:
        Базовые коды:
            1 - все прошло хорошо, аккаунт успешно подписался на канал / группу
            2 - неожиданное исключение, которое не обрабатывается классами telethon
        Коды о проблемах с каналом(чатом):
            3 - в ссылке отсутствует хэш, необходимый для подписки
            4 - пригласительная ссылка просрочена
            5 - неверная пригласительная ссылка
            8 - превышено максимальное количество пользователей в данном чате
            11 - недопустимый тип канала (чата), возможно проблема в ссылке
        Коды о проблемах с аккаунтом:
            6 - аккаунт уже присоединён к большому количеству каналов (групп)
            7 - включена 2ФА и требуется пароль
            9 - пользователь уже является участником данного канала (чата)
            10 - аккаунт уже вступил в слишком большое количество каналов (чатов)
            12 - юзер быд забанен в канале (чате) или канал приватный и у юзера нет прав для вступления

    :return (code, description)
    """

    if target.split('/')[-1].startswith('+'):

        MY_LOGGER.debug(f'Поток № {thread_id}\tДля подписки передан приватный канал/чат.')
        lnk_hash = target.split('/')[-1].replace('+', '')

        MY_LOGGER.debug(f'Проверяем, что ссылка-приглашение активна')
        try:
            await client(functions.messages.CheckChatInviteRequest(hash=lnk_hash))
        except InviteHashEmptyError as err:
            MY_LOGGER.warning(f'В ссылке отсутствует хэш, необходимый для подписки! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 3, str(err)
        except InviteHashExpiredError as err:
            MY_LOGGER.warning(f'Ссылка-приглашение просрочена! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 4, str(err)
        except InviteHashInvalidError as err:
            MY_LOGGER.warning(f'Неверная ссылка-приглашение! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 5, str(err)
        except Exception as err:
            MY_LOGGER.error(f'В процессе проверке ссылки-приглашения получена неожиданная ошибка. Текст ошибки: {err}')
            return 2, str(err)

        MY_LOGGER.debug(f'Пробуем вступить в канал по ссылке: {target}')
        try:
            await client(functions.messages.ImportChatInviteRequest(lnk_hash))
        except ChannelsTooMuchError as err:
            MY_LOGGER.warning(f'Аккаунт уже присоединён к большому кол-ву каналов/групп! '
                              f'Текст ошибки: {err}')
            return 6, str(err)
        except InviteHashEmptyError as err:
            MY_LOGGER.warning(f'В ссылке отсутствует хэш, необходимый для подписки! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 3, str(err)
        except InviteHashExpiredError as err:
            MY_LOGGER.warning(f'Ссылка-приглашение просрочена! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 4, str(err)
        except InviteHashInvalidError as err:
            MY_LOGGER.warning(f'Неверная ссылка-приглашение! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 5, str(err)
        except SessionPasswordNeededError as err:
            MY_LOGGER.warning(f'Включена 2-ФА и требуется пароль.! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 7, str(err)
        except UsersTooMuchError as err:
            MY_LOGGER.warning(f'Превышено максимальное кол-во пользователей в данном чате! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 8, str(err)
        except UserAlreadyParticipantError as err:
            MY_LOGGER.warning(f'Пользователь уже является участником канала/чата! '
                              f'Ссылка: {target}. Текст ошибки: {err}')
            return 9, str(err)
        except Exception as err:
            MY_LOGGER.error(f'Не удалось подписаться на канал/чат: {target}. Текст ошибки: {err}')
            return 2, str(err)

    else:
        MY_LOGGER.debug(f'Поток № {thread_id}\tДля подписки передан приватный канал/чат.')
        try:
            MY_LOGGER.info(f'Поток № {thread_id}\tПробуем вступить в канал {target}')
            await client(functions.channels.JoinChannelRequest(
                channel=target
            ))
        except ChannelsTooMuchError as err:
            MY_LOGGER.warning(f'Не удалось подписаться на канал: {target}. '
                              f'Причина: аккаунт присоединился к слишком большому количеству каналов. Текст ошибки: {err}')
            return 10, str(err)
        except ChannelInvalidError as err:
            MY_LOGGER.warning(f'Не удалось подписаться на канал: {target}. '
                              f'Причина: недопустимый тип канала, убедитесь, что Вы передаёте правильный идентификатор '
                              f'канала. Текст ошибки: {err}')
            return 11, str(err)
        except ChannelPrivateError as err:
            MY_LOGGER.warning(f'Не удалось подписаться на канал: {target}. '
                              f'Причина: канал является приватным и у аккаунта нет прав, или аккаунт был '
                              f'забанен в канале/чате. Текст ошибки: {err}')
            return 12, str(err)
        except Exception as err:
            MY_LOGGER.error(f'Не удалось подписаться на канал: {target}. Текст ошибки: {err}')
            return 2, str(err)

    MY_LOGGER.success(f'Поток № {thread_id}\tАккаунт успешно подписался на канал {target}')
    return 1, 'all right'


def worker(proxy_string: str, time_auth_proxy: str, time_auth_accounts: str, reset_accounts: str, thread_id: int,
           thread_accs: List[str], target: str) -> Tuple[int, str]:
    """
    Работа по заданию в потоке.
        proxy_string - список проксей в виде строки,
        time_auth_proxy - таймаут подключения аккаунта к проксе,
        reset_accounts - кол-во попыток подключения аккаунта к проксе,
        thread_id - номер потока,
        thread_accs - список аккаунтов для данного потока (название файла без расширения)
        target - username или ссылка на канал, на который подписываемся

    Коды возврата потока:
        1 - Успешная отработка по заданию
        2 - Во время выполнения задания возникло неожиданное исключение
        3 - Во время работы по заданию возникла проблема с каналом(группой) на которую надо подписаться
        (проблема в задании)

    :return (code, description)
    """
    MY_LOGGER.info(f'Поток № {thread_id}\tПолучил в работу {len(thread_accs)} аккаунтов.')

    # Собираем прокси в список
    MY_LOGGER.debug(f'Собираем прокси в список')
    proxy_lst = []
    for i_proxy in proxy_string.split('\n'):
        if i_proxy != '':
            i_proxy = i_proxy.split(':')
            proxy_dct = {
                'addr': i_proxy[1],
                'port': i_proxy[2],
            }
            # Если к проксе указан логин и пароль
            if len(i_proxy) == 5:
                proxy_dct['username'] = i_proxy[3]
                proxy_dct['password'] = i_proxy[4]
            # Устанавливаем протокол соединения для прокси
            if i_proxy[0] == 'http':
                proxy_dct['proxy_type'] = connection.ConnectionHttp
            elif i_proxy[0] == 'https':
                proxy_dct['proxy_type'] = connection.ConnectionHttp
            elif i_proxy[0] == 'socks4':
                proxy_dct['proxy_type'] = socks.SOCKS4
                proxy_dct['rdns'] = True
            elif i_proxy[0] == 'socks5':
                proxy_dct['proxy_type'] = socks.SOCKS5
                proxy_dct['rdns'] = True
            # Добавляем проксю в общий список
            proxy_lst.append(proxy_dct)

    success_accs = 0    # успешно отработавшие аккаунты
    for i_indx, i_acc in enumerate(thread_accs):
        MY_LOGGER.info(f'Поток № {thread_id}\tБерёт в работу {i_indx + 1} аккаунт '
                       f'из {len(thread_accs)} аккаунтов в потоке.')

        MY_LOGGER.debug(f'Вытягиваем рандомную проксю и форматируем её для работы')
        rand_proxy = random.choice(proxy_lst)

        # TODO: с телетоном надо прям проверить, что всё ок

        # Коннектим аккаунт через прокси
        MY_LOGGER.info(f'Поток № {thread_id}\tАккаунт № {i_indx + 1} коннектится к проксе: {rand_proxy}')

        # Достаём инфу об аккаунте из json файла
        MY_LOGGER.debug(f'Поток № {thread_id}\tДостаём инфу об аккаунте из json файла')
        with open(file=os.path.join(BASE_DIR, 'accounts', f'{i_acc}.json'),
                  mode='r', encoding='utf-8') as json_file:
            json_dct = json.load(fp=json_file)

        # Создаём отдельный event loop asyncio
        MY_LOGGER.debug(f'Поток № {thread_id}\tСоздаём отдельный event loop asyncio')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=loop)

        # Запускаем итерируемый аккаунт телеги
        MY_LOGGER.debug(f'Поток № {thread_id}\tЗапускаем итерируемый аккаунт телеги ({i_acc!r})')
        try:
            with TelegramClient(
                    session=os.path.join(BASE_DIR, 'accounts', f'{i_acc}.session'),
                    api_id=json_dct.get("app_id"),
                    api_hash=json_dct.get("app_hash"),
                    proxy=rand_proxy,
                    timeout=int(time_auth_proxy),
                    connection_retries=int(reset_accounts),
                    app_version=json_dct.get("app_version").split()[0],
                    system_version=json_dct.get("sdk"),
                    lang_code=json_dct.get("lang_pack"),
                    system_lang_code=json_dct.get("system_lang_pack"),
            ) as client:
                rslt = loop.run_until_complete(do_subscription(client=client, target=target, thread_id=thread_id))
                MY_LOGGER.debug(f'Поток № {thread_id}\tРезультат работы акка {i_acc!r} == {rslt}')

                # Перемещение файлов для аккаунта в папку done
                if rslt[0] == 1:
                    MY_LOGGER.debug(f'Поток № {thread_id}\tПеремещаем аккаунт {i_acc!r} в папку "done"')
                    done_dir = os.path.join(BASE_DIR, 'done')
                    if not os.path.exists(done_dir):
                        MY_LOGGER.debug(f'Поток № {thread_id}\tПапка done отсутствует и будет создана.')
                        os.mkdir(done_dir)
                    shutil.move(
                        src=os.path.join(BASE_DIR, 'accounts', f'{i_acc}.session'),
                        dst=os.path.join(BASE_DIR, 'done', f'{i_acc}.session')
                    )
                    shutil.move(
                        src=os.path.join(BASE_DIR, 'accounts', f'{i_acc}.json'),
                        dst=os.path.join(BASE_DIR, 'done', f'{i_acc}.json')
                    )
                    success_accs += 1

                if rslt[0] == 2:
                    MY_LOGGER.debug(f'Поток № {thread_id}\tПолучен код ответа 2 от функции подписки. '
                                    f'Поток будет остановлен.')
                    return 2, rslt[1]

                elif rslt[0] in (3, 4, 5, 8, 11):
                    MY_LOGGER.debug(f'Поток № {thread_id}\tПроблема с каналом, на который необходимо подписаться. '
                                    f'Поток будет остановлен')
                    return 3, rslt[1]

        except ConnectionError as err:
            MY_LOGGER.warning(f'Поток № {thread_id}\tАккаунту {i_acc} не удалось подключится к прокси {rand_proxy}. '
                              f'Текст ошибки: {err}')

            # Перемещение файлов аккаунта, которому не удалось подключиться к проксе в папку no_connect
            no_connect_dir = os.path.join(BASE_DIR, 'no_connect')
            if not os.path.exists(no_connect_dir):
                MY_LOGGER.debug(f'Поток № {thread_id}\tПапка no_connect отсутствует, создаём её.')
                os.mkdir(no_connect_dir)
            MY_LOGGER.debug(f'Поток № {thread_id}\tПеремещаем файлы аккаунта {i_acc!r} в папку no_connect')
            shutil.move(src=os.path.join(BASE_DIR, 'accounts', f'{i_acc}.session'),
                        dst=os.path.join(no_connect_dir, f'{i_acc}.session'))
            shutil.move(src=os.path.join(BASE_DIR, 'accounts', f'{i_acc}.json'),
                        dst=os.path.join(no_connect_dir, f'{i_acc}.json'))

        # Таймаут между действиями аккаунтов
        if i_indx + 1 < len(thread_accs):   # Проверяем, что аккаунт не последний в списке
            MY_LOGGER.debug(f'Поток № {thread_id}\tРассчитываем таймаут между действиями аккаунтов. '
                            f'Диапазон паузы: {time_auth_accounts}')
            acc_timeout = time_auth_accounts.replace(' ', '').split('-')
            sleep_between_actions = random.randint(int(acc_timeout[0]), int(acc_timeout[1]))
            MY_LOGGER.info(f'Поток № {thread_id}\tПауза перед действием для следующего аккаунта: '
                           f'{sleep_between_actions} сук.')
            time.sleep(sleep_between_actions)

        main_result = 1, f'{success_accs}|{len(thread_accs)}'
        MY_LOGGER.info(f'Поток № {thread_id}\tОтработал. Успешно подписались {success_accs} из {len(thread_accs)}')
        return main_result


def main_work_on_assignment(limits_dct: dict, target: str):
    """
    Основная функция работы по заданиям.
    :param limits_dct - ограничения для работы по заданию.
    :param target - ссылка, username для канала, на который подписываемся.
    """
    # Записываем необходимые данные в переменные
    MY_LOGGER.debug(f'Записываем необходимые данные для выполнения задания в переменные')
    threads_numb = limits_dct.get('stream_account')
    time_auth_proxy = limits_dct.get('time_auth_proxy')  # Таймаут подключения через проксю
    reset_accounts = limits_dct.get('reset_accounts')  # Кол-во попыток подключения аккаунта через проксю
    time_auth_accounts = limits_dct.get('time_auth_accounts')  # Таймаут между действиями аккаунта

    # Открываем файл с проксями и складываем их в список
    MY_LOGGER.debug(f'Открываем файл с проксями и складываем их в список')
    with open(file=os.path.join(BASE_DIR, 'settings', 'proxy.txt'), mode='r', encoding='utf-8') as proxy_file:
        proxy_string = proxy_file.read()

    # Распределяем аккаунты по потокам
    MY_LOGGER.debug(f'Распределяем аккаунты по потокам')
    acc_dir_path = os.path.join(BASE_DIR, 'accounts')
    general_acc_lst = []  # здесь будут названия файлов без расширений
    for i_file in os.listdir(acc_dir_path):  # Формируем общий список аккаунтов

        if os.path.isfile(os.path.join(acc_dir_path, i_file)) and os.path.splitext(i_file)[1] == '.session':
            MY_LOGGER.debug(f'Условие: итерируемый объект директории файл с расширением .session проверено успешно')
            i_file_name = os.path.splitext(i_file)[0]

            # Проверяем, что существует пара файлов session-json
            MY_LOGGER.debug(f'Проверяем, что существует пара файлов session-json')
            if os.path.exists(os.path.join(acc_dir_path, f'{i_file_name}.session')) and \
                    os.path.exists(os.path.join(acc_dir_path, f'{i_file_name}.json')):
                general_acc_lst.append(i_file_name)
            else:
                MY_LOGGER.warning(f'Не найдена пара файлов session-json для {i_file} '
                                  f'при распределении аккаунтов по потокам')

    MY_LOGGER.debug(f'Формируем списки аккаунтов для потоков')
    threads_acc_dct = dict()  # Словарь с акками, распределёнными по потокам
    accs_for_one_thread = math.ceil(len(general_acc_lst) / int(threads_numb))
    for i_indx in range(int(threads_numb)):  # Формируем списки аккаунтов для каждого потока
        threads_acc_dct[i_indx + 1] = general_acc_lst[:accs_for_one_thread]
        general_acc_lst = general_acc_lst[accs_for_one_thread:]  # срезаем те акки, которые уже забрали

    # Запускаем потоки
    MY_LOGGER.debug(f'Запускаем потоки')
    threads = []
    for i_thread_id in range(1, int(threads_numb) + 1):
        MY_LOGGER.info(f'Запускаем поток № {i_thread_id}')
        i_thread_accs = threads_acc_dct.get(i_thread_id)
        thread = threading.Thread(target=lambda: setattr(threading.current_thread(), 'result', worker(
            proxy_string, time_auth_proxy, time_auth_accounts, reset_accounts, i_thread_id, i_thread_accs, target
        )))
        thread.start()
        threads.append(thread)

    work_rslt = [0, 0]  # [Кол-во успешно подписанных аккаунтов, общее кол-во аккаунтов]
    for i_thread in threads:
        i_thread.join()
        thread_result = i_thread.result

        if thread_result[0] == 1:
            MY_LOGGER.debug(f'Плюсуем результат работы потока к успешно отработавшим аккаунтам и общему их числу')
            work_rslt[0] += thread_result[1].split('|')[0]
            work_rslt[1] += thread_result[1].split('|')[1]

        elif thread_result[0] == 2:
            # TODO: обработка для неожиданного исключения в потоке
            pass

        elif thread_result[0] == 2:
            # TODO: обработка для хренового задания, полученного от сервиса (учесть также какой был выбран сервис)
            pass


