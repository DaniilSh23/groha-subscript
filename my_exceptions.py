class MyException(Exception):
    """
    Класс для кастомного исключения.
    """
    def __init__(self, message):
        super().__init__(message)

    def my_exception_handler(self):
        pass


class MyExcSessionExpired(Exception):
    """
    Класс для кастомного исключения на случай, если файл сессии аккаунта устарел
    """
    def __init__(self, message):
        super().__init__(message)

    def my_exception_handler(self):
        pass
