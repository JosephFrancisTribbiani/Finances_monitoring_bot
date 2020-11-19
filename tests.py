import unittest
from logics import msg_parser, test_msg
from datetime import datetime, date
from exceptions import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()


# Тестируем функцию msg_parser из модуля logics
class TestMsgParser(unittest.TestCase):

    def testMsgParser1(self):
        msg = '   Такси до аэропорта     99    7'
        day = 7
        month = datetime.today().month
        year = datetime.today().year
        d = date(year, month, day)
        d = d.strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('такси до аэропорта', 'out', 99, d))

    def testMsgParser2(self):
        msg = '   Такси 365 до аэропорта номер 9   250.60   1/07  '
        day = 1
        month = 7
        year = datetime.today().year
        d = date(year, month, day)
        d = d.strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('такси 365 до аэропорта номер 9', 'out', 250.6, d))

    def testMsgParser3(self):
        msg = '   Зарплата   +9   '
        d = datetime.today().strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('зарплата', 'in', 9, d))

    def testMsgParser4(self):
        msg = '   Такси 365 до аэропорта номер 9    250.60    11/12/2019  '
        day = 11
        month = 12
        year = 2019
        d = date(year, month, day)
        d = d.strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('такси 365 до аэропорта номер 9', 'out', 250.6, d))

    def testMsgParser5(self):
        msg = 'Коммунальные услуги 4696.94 10/08'
        day = 10
        month = 8
        year = datetime.today().year
        d = date(year, month, day)
        d = d.strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('коммунальные услуги', 'out', 4696.94, d))

    def testMsgParser9(self):
        msg = '   Такси 365 до аэропорта номер 9   250.677   1/2/2020  '
        self.assertRaises(WrongAmount, msg_parser, msg)

    def testMsgParser10(self):
        msg = '   Такси 365 до аэропорта номер 9   250.677'
        self.assertRaises(WrongAmount, msg_parser, msg)

    def testMsgParser11(self):
        msg = '   Такси до аэропорта5   9,58   '
        d = datetime.today().strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('такси до аэропорта5', 'out', 9.58, d))

    def testMsgParser12(self):
        msg = '   Такси до аэропорта   -250.67   44/2/2020  '
        self.assertRaises(ValueError, msg_parser, msg)

    def testMsgParser13(self):
        msg = '   Такси до аэропорта   250.67   1/13/2020  '
        self.assertRaises(ValueError, msg_parser, msg)

    def testMsgParser14(self):
        msg = '   Такси до аэропорта   250.67   1/12/3000  '
        self.assertRaises(WrongDate, msg_parser, msg)

    def testMsgParser15(self):
        msg = '   Такси до аэропорта   250.67   4/2/20200  '
        self.assertRaises(ValueError, msg_parser, msg)

    def testMsgParser16(self):
        msg = '   Подработка у майора на даче   +250   11/12/2019  '
        day = 11
        month = 12
        year = 2019
        d = date(year, month, day)
        d = d.strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('подработка у майора на даче', 'in', 250, d))


# Тестируем функцию test_msg из модуля logics
class Msg:
    text = 'Default text'


message = Msg()


class TestMsgTypes(unittest.TestCase):

    def testMsgTypes1(self):
        message.text = '   Такси 5 до аэропорта    -250.555    1/1/2020'
        self.assertEqual(test_msg(message), 1)

    def testMsgTypes2(self):
        message.text = '   Такси 5 до аэропорта    250.550000    1/1/2020'
        self.assertEqual(test_msg(message), 1)

    def testMsgTypes3(self):
        message.text = '   Такси 5 до аэропорта    250    11/12'
        self.assertEqual(test_msg(message), 1)

    def testMsgTypes4(self):
        message.text = '   Такси 5 до аэропорта    250.    11/12'
        self.assertEqual(test_msg(message), 1)

    def testMsgTypes5(self):
        message.text = '   Такси 5 до аэропорта    250    11/12/202'
        self.assertEqual(test_msg(message), 1)

    def testMsgTypes6(self):
        message.text = '   Зарплата    +250    11/12/2020'
        self.assertEqual(test_msg(message), 1)

    def testMsgTypes7(self):
        message.text = '   Такси 5 до аэропорта   '
        self.assertNotEqual(test_msg(message), 1)

    def testMsgTypes8(self):
        message.text = '   Такси 5 до аэропорта   11/12/2020'
        self.assertNotEqual(test_msg(message), 1)

    def testMsgTypes9(self):
        message.text = '   Такси 5 до аэропорта   11/12'
        self.assertNotEqual(test_msg(message), 1)

    def testMsgTypes10(self):
        message.text = '   Такси 5 до аэропорта  - 300,22   11/12'
        self.assertEqual(test_msg(message), 1)
