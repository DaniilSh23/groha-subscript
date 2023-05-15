class MyException(Exception):
    """
    Класс для кастомного исключения.
    """
    def __init__(self, message):
        super().__init__(message)

    def my_exception_handler(self):
        pass
