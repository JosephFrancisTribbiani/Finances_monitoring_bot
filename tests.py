import unittest
from logics import msg_parser
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
        msg = '   Такси до аэропорта   99   7  '
        day = 7
        month = datetime.today().month
        year = datetime.today().year
        d = date(year, month, day)
        d = d.strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('Такси до аэропорта', 99, d))

    def testMsgParser2(self):
        msg = '   Такси 365 до аэропорта номер 9   250.60   1/07  '
        day = 1
        month = 7
        year = datetime.today().year
        d = date(year, month, day)
        d = d.strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('Такси 365 до аэропорта номер 9', 250.60, d))

    def testMsgParser3(self):
        msg = '   Такси до аэропорта5   9   '
        d = datetime.today().strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('Такси до аэропорта5', 9, d))

    def testMsgParser4(self):
        msg = '   Такси 365 до аэропорта номер 9   250.60   11/12/2019  '
        day = 11
        month = 12
        year = 2019
        d = date(year, month, day)
        d = d.strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('Такси 365 до аэропорта номер 9', 250.60, d))

    def testMsgParser5(self):
        msg = '   Такси 365 до аэропорта номер 9   250.60   1/2/20200  '
        self.assertRaises(WrongMsgFormat, msg_parser, msg)

    def testMsgParser6(self):
        msg = '   Такси 365 до аэропорта номер 9   250.60   1/299  '
        self.assertRaises(WrongMsgFormat, msg_parser, msg)

    def testMsgParser7(self):
        msg = '   Такси 365 до аэропорта номер 9   250.60   1/2//2020  '
        self.assertRaises(WrongMsgFormat, msg_parser, msg)

    def testMsgParser8(self):
        msg = '   Такси 365 до аэропорта номер 9   250.60   /1/2  '
        self.assertRaises(WrongMsgFormat, msg_parser, msg)

    def testMsgParser9(self):
        msg = '   Такси 365 до аэропорта номер 9   250.677   1/2/2020  '
        self.assertRaises(WrongMsgFormat, msg_parser, msg)

    def testMsgParser10(self):
        msg = '   Такси 365 до аэропорта номер 9   250.677'
        self.assertRaises(WrongMsgFormat, msg_parser, msg)

    def testMsgParser11(self):
        msg = '   Такси до аэропорта5   9,58   '
        d = datetime.today().strftime('%Y-%m-%d')
        self.assertEqual(msg_parser(msg), ('Такси до аэропорта5', 9.58, d))

    def testMsgParser12(self):
        msg = '   Такси до аэропорта   250.67   40/2/2020  '
        self.assertRaises(ValueError, msg_parser, msg)

    def testMsgParser13(self):
        msg = '   Такси до аэропорта   250.67   1/13/2020  '
        self.assertRaises(ValueError, msg_parser, msg)

    def testMsgParser14(self):
        msg = '   Такси до аэропорта   250.67   1/12/3000  '
        self.assertRaises(WrongDate, msg_parser, msg)
