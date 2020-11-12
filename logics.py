import re
from datetime import datetime
from exceptions import *
from random import randint


def msg_parser(msg: str):
    p_msg = re.match(r'(?:([\d/]+)\s+)?'
                     r'((?:\d+[.,])?\d+)\s+(.+)', msg[::-1].strip())

    category = p_msg.group(3)[::-1].lower()
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

    return category, amount, d.strftime('%Y-%m-%d')


def test_msg(msg):
    msg_type = 0
    t = msg.text.lower().strip()
    if bool(re.search(r'^добавь категори[ию] .*', t)):
        msg_type = 1
    elif bool(re.search(r'^(?:(?:выведи )?мои категории)|(?:/my_categories)', t)):
        msg_type = 2
    elif bool(re.search(r'.+\s+\d+(?:[.,]\d*)?'
                        r'(?:(?:\s+\d+)|(?:\s+\d+(?:/\d+){1,2}))?$', t)):
        msg_type = 3
    return msg_type


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
