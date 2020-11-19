class WrongMsgFormat(Exception):
    def __init__(self):
        self.message = 'Неправильный формат сообщения'

    def __str__(self):
        return self.message


class WrongDate(Exception):
    def __init__(self):
        self.message = 'Дата больше текущей'

    def __str__(self):
        return self.message


class WrongAmount(Exception):
    def __init__(self):
        self.message = 'Указана неправильная сумма'

    def __str__(self):
        return self.message


class NegativeLimit(Exception):
    def __init__(self):
        self.message = 'Указана неправильная сумма'

    def __str__(self):
        return self.message
