import re
from datetime import datetime
from exceptions import *
from random import randint


def msg_parser(msg: str):
    """
    Функция принимает на вход сообщение от пользователя в формате (текст сообщения -> str)

    [Название категории] [опц: +-] [Сумма] [опц: Дата]

    и извлекает из него необходимые данные:

    - Название категрии -> str

    - Тип категории -> 'in' (если '+') - доход, или 'out' (если '-' или ничего не указано) - расход

    - Сумма -> int или float

    - Дата в формате '%Y-%m-%d' -> str
    """
    p_msg = re.match(r'(?:([\d/]+)\s+)?'        # group(1) - дата
                     r'((?:\d*[.,])?\d+)\s*'    # group(2) - сумма
                     r'([+-])?\s+'              # group(3) - знак
                     r'(.+)',                   # group(4) - категория
                     msg[::-1].strip())

    category = p_msg.group(4)[::-1].lower()
    amount = p_msg.group(2)[::-1].replace(',', '.')

    if re.search(r'(?:(?<=\.)\d{1,2}\Z)|(^\d+\Z)', amount) is None:
        raise WrongAmount
    if '.' in amount:
        amount = float(amount)
    else:
        amount = int(amount)

    d = datetime.today()

    if p_msg.group(1) is not None:
        nums = p_msg.group(1)[::-1].split('/')
        length = len(nums)

        if length >= 1:
            d = d.replace(day=int(nums[0]))
        if length >= 2:
            d = d.replace(month=int(nums[1]))
        if length == 3:
            d = d.replace(year=int(nums[2]))

        if d > datetime.today():
            raise WrongDate

    if p_msg.group(3) is None or p_msg.group(3) == '-':
        c_type = 'out'
    else:
        c_type = 'in'

    return category, c_type, amount, d.strftime('%Y-%m-%d')


def test_msg(msg):
    txt = msg.text.strip().lower()
    if re.search(r'.+\s+[-+]?\s*\d+(?:[.,]\d*)?'
                 r'(?:(?:\s+\d+)|(?:\s+\d+(?:/\d+){1,2}))?$', txt):
        return 1


def answers(t: str) -> str:
    answer = ''
    if t == 'No':
        x = randint(1, 4)
        switch = {
            1: 'На нет и суда нет',
            2: 'Хорошо не буду',
            3: 'Ну и пожалуйста, не очень то и хотелось',
            4: 'Нет так нет'
        }
        answer = switch[x]
    if t == 'Yes':
        x = randint(1, 4)
        switch = {
            1: 'Сделал как ты и просил',
            2: 'Сделано',
            3: 'Задание выполнено',
            4: 'Готово'
        }
        answer = switch[x]
    return answer
