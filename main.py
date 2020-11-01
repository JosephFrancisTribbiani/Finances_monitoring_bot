from config import *
import telebot

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'hi'])
def hello(message):
	bot.send_message(message.chat.id, 'HI')

bot.polling()
