# Скрипт для автоматизации работы с сервисами по накрутке (vtope, socpanel)

### Основной функционал проекта:
* Получение заданий в сервисе vtope и socpanel в категориях: подписки на каналы(группы) телеграм, оставление реакций под постами в телеграм.
* Выполнение этих заданий посредством автоматизации действий телеграм юзеров

### Структура проекта:
* Директория "accounts" - хранит пары файлов .session - .json для одного аккаунта телеграм
* Директория "settings" - хранит файлы: 
    * "api_keys.json" - API ключи для сервисов socpanel, vtope
      * "vtope_utoken" - utoken из ЛК сервиса vtope
      * "vtope_btoken" - будет получен после запроса к vtope и записан в api_keys.json (необходим для получения atoken)
      * "tlg_id" - ID Telegram (необходим для получения atoken) 
      * "tlg_username" - Username Telegram (необходим для получения atoken) 
      * "vtope_atoken" - токен vtope, который необходим для получения заданий

    * "limit.json" - Настройки для работы скрипта:
      * "time_auth_accounts" - таймаут между подписками в сек.
      * "subscription_account_limit" - макс. кол-во подписок для одного аккаунта
      * "failed_attempt" - макс. кол-во неудачных попыток какого-либо действия (подписка) для одного аккаунта
      * "flood_account" - макс. таймаут флуда для одного аккаунта, выданный телеграммом. При превышении аккаунт исключается из работы и помещается в отдельную папку
      * "time_auth_service" - таймаут между запросами заданий в сервисах socpanel, vtope. Актуален тогда, когда запрос задания в сервисе не дал результата
      * "stream_account" - кол-во потоков для работы с телеграммом.
      * "time_auth_proxy" - таймаут для подключения через прокси
      * "reset_accounts" - кол-во повторных попыток подключения через прокси
* Директория "logs" - содержит файлы логов. Для каждого запуска скрипта создаются файлы "logs_{now_datetime}.log", "sys_logs_{now_datetime}.log". Эти файлы включают в себя стандартное логирование работы программы и системные логи об ошибках и иной отладочной информации.

#### ! Файлы в папке settings с препиской _example являются примерами. Файлы для работы должны называться без _example, например api_keys.json вместо api_keys_example.json