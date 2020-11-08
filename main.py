from config import TOKEN
from db import init_db, collect_user, collect_msg_into_db
from logics import msg_parser
from exceptions import *
import telebot

bot = telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands=['start'])
def hello(message):
    collect_user(message.from_user)
    bot.send_message(message.chat.id, 'Hi')


@bot.message_handler(content_types=['text'])
def collect_exp(message):
    try:
        msg_parser(message.text)
        collect_msg_into_db(message.from_user.id, message.text)
        bot.send_message(message.chat.id, 'Записал')
    except WrongMsgFormat:
        bot.send_message(message.chat.id, 'Я тебя не понимаю, воспользуйся /help')
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка, такой даты не существует')
    except WrongDate:
        bot.send_message(message.chat.id, 'Ошибка, указанная дата больше текущей')


def main():
    init_db(force=False)
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
