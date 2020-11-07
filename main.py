from config import TOKEN
from db import init_db, collect_user
import telebot

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def hello(message):
    collect_user(message.from_user)
    bot.send_message(message.chat.id, 'Hi')


def main():
    init_db(force=False)
    while True:
        bot.polling()


if __name__ == '__main__':
    main()
