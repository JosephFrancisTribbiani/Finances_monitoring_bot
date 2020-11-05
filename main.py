from config import TOKEN
# from db import test
import telebot

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def hello(message):
    # test(message)
    bot.send_message(message.chat.id, 'Hi')
    # get_info(msg=message)
    # write_to_chat(message.chat.id, message.chat.first_name, message.chat.last_name)


# def get_info(msg):
#     """
#     Данная функция извлекает данные сообщения, отправленного боту
#     и сохраняет в файл в формате json
#     :param msg: telebot object
#     :return: nothing
#     """
#     f = open('data.txt', 'a')
#     f.write(json.dumps(msg.json, sort_keys=False, indent=4) + '\n')
#     f.close()


# def write_to_chat(id, fname, lname):
#     bot.send_message(id, 'Hello, {} {}.\nYou got this message from function "write_to_chat".'.format(fname, lname))


while True:
    bot.polling()
