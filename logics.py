import re
from datetime import datetime
from exceptions import *


def msg_parser(msg: str):
    p_msg = re.match(r'((?:(?:\d{4}(?:/\d{1,2}){2}\s+)|(?:\d{1,2}/\d{1,2}\s+)|(?:\d{1,2}\s+)|\b)\d{,2}[.,]?\d+) (.*)', msg[::-1].strip())

    if p_msg is None:
        raise WrongMsgFormat

    category = p_msg.group(2)[::-1].strip()
    nums = re.split(r'/+|\s+', p_msg.group(1)[::-1].strip())

    length = len(nums)

    amount = float(nums[0].replace(',', '.'))
    d = datetime.today()

    if length >= 2:
        d = d.replace(day=int(nums[1]))
    if length >= 3:
        d = d.replace(month=int(nums[2]))
    if length == 4:
        d = d.replace(year=int(nums[3]))

    if d > datetime.today():
        raise WrongDate

    return category, amount, d.strftime('%Y-%m-%d')
