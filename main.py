from config import TOKEN
from db import init_db, collect_user, collect_msg_into_db, add_cat_into_db, check_user, check_category
from db import get_my_cat, add_exp_into_db
from logics import msg_parser, test_msg, answers
from exceptions import *
import telebot
from telebot import types
import re

bot = telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    collect_user(message.from_user)
    bot.send_message(message.chat.id, 'Привет!\n'
                                      'Я помогу тебе контролировать твои расходы\n'
                                      'Воспользуйся /help, что бы узнать что я умею и как этим пользоваться')


@bot.message_handler(commands=['help'])
def start(message):
    collect_user(message.from_user)
    bot.send_message(message.chat.id, 'Для того, чтобы я мог записать трату, отправь мне сообщение в формате:\n'
                                      '*[Категория] [сумма] [дата]*\n'
                                      'где *дата* - необязательный параметр\n'
                                      'Например:\n'
                                      '*Продукты 28.50 1/11/2019_\n'
                                      'Это значит что 1-го ноября 2019 года я потратил 25 руб. 50 копеек на проезд '
                                      'в общественном транспорте\n'
                                      'Если дату не укажешь, я пойму что трата была совершена сегодня\n'
                                      'Также можно указать только день, в таком случае месяц и '
                                      'год будут считаться текущими\n'
                                      'Или день и месяц, тогда год - текущий\n'
                                      '\n'
                                      'Если категория указана новая, то я предложу тебе ее добавить (вдруг ты случайно '
                                      'ошибся в написании категории - написал *ТранспАрт_ вместо *Транспорт_)\n'
                                      'Категории также можно добавить списком, для этого просто напиши мне '
                                      '*Добавь категорию продукты* или *Добавь категории продукты, бензин, одежда*\n'
                                      '\n'
                                      'Что бы вывести список твоих категорий напиши мне:\n'
                                      '*Мои категории*\n'
                                      'И я все сделаю\n'
                                      'Удачи! Надеюсь мы с тобой подружимся', parse_mode='MarkdownV2')


@bot.message_handler(func=lambda msg: test_msg(msg) == 1, content_types=['text'])
def add_categories(message):
    added_cat = list()
    t = message.text.lower()
    if bool(re.fullmatch(r'^добавь категори[ию] [а-яёa-z0-9 -+]+(?:[,][а-яёa-z0-9 -+]+)*', t)):
        categories = [c.strip() for c in t[17:].split(',')]
        if not check_user(message.from_user.id):
            collect_user(message.from_user)
        for category in categories:
            if not check_category(category, message.from_user.id):
                add_cat_into_db(message.from_user.id, category)
                added_cat.append(category)

        length = len(added_cat)
        if len(categories) == 1 and length == 1:
            r_msg = 'Добавил'
        elif length == 1:
            r_msg = f'Новая категория *{added_cat[0]}* добавлена'
        elif length > 1:
            r_msg = f'Новые категории *{", ".join(added_cat)}* добавлены'
        else:
            r_msg = f'Уже есть'
        bot.send_message(message.chat.id, r_msg, parse_mode='MarkdownV2')

    else:
        bot.send_message(message.chat.id, 'Не понимаю\nУкажи категории через запятую\nМожно использовать только '
                                          'буквы, цифры и символы - или +')


@bot.message_handler(func=lambda msg: test_msg(msg) == 2, content_types=['text'])
def return_cat(message):
    my_cat = [cat[0] for cat in get_my_cat(message.from_user.id)]
    if len(my_cat) == 0:
        bot.send_message(message.chat.id, 'Категории не добавлены')
    else:
        cat_s = '\n'.join(my_cat)
        bot.send_message(message.chat.id, f"__Твои категории:__\n{cat_s}", parse_mode='MarkdownV2')


@bot.message_handler(func=lambda msg: test_msg(msg) == 3, content_types=['text'])
def collect_exp(message):
    if not check_user(message.from_user.id):
        collect_user(message.from_user)
    try:
        cat, amount, d = msg_parser(message.text)
        collect_msg_into_db(message.from_user.id, message.text)
        if not check_category(cat, message.from_user.id):

            bot.send_message(message.chat.id, f"Категорию *{cat}* для тебя я еще не добавлял\n"
                                              "Добавить новую категорию и трату?", parse_mode='MarkdownV2',
                             reply_markup=y_n_keyboard(f'add|{cat}|{int(amount)}|{d}'))
        else:
            add_exp_into_db(message.from_user.id, cat, str(amount), d)
            bot.send_message(message.chat.id, 'Записал')

    except WrongAmount:
        bot.send_message(message.chat.id, 'Ошибка, неправильно указана сумма')
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка, такой даты не существует')
    except WrongDate:
        bot.send_message(message.chat.id, 'Ошибка, указанная дата больше текущей')


@bot.message_handler(func=lambda msg: test_msg(msg) == 0)
def some_text(message):
    bot.send_message(message.chat.id, 'Я не понимаю\nПопробуй воспользоваться /help')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        var = call.data.split('|')
        if var[0] == 'add':
            add_cat_into_db(call.message.chat.id, var[1])  # добавляем новую категорию в базу
            add_exp_into_db(call.message.chat.id, var[1], str(var[2]), var[3])
            bot.send_message(chat_id=call.message.chat.id, text=answers('Yes'))
        elif call.data == 'cb_button_no':
            bot.send_message(chat_id=call.message.chat.id, text=answers('No'))
        bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')


def main():
    init_db(force=False)
    bot.polling(none_stop=True, interval=0)


def y_n_keyboard(clb_data: str):
    """
    Функция создает inline клавиатуру с кнопками Да/Нет
    :return: обьект types.InlineKeyboardMarkup
    """
    call_back_button_yes = clb_data
    call_back_button_no = 'cb_button_no'

    titles = {
        call_back_button_yes: "Да",
        call_back_button_no: "Нет"
    }

    markup = types.InlineKeyboardMarkup()
    keyboard = [
        types.InlineKeyboardButton(titles[call_back_button_yes], callback_data=call_back_button_yes),
        types.InlineKeyboardButton(titles[call_back_button_no], callback_data=call_back_button_no)
    ]

    return markup.add(*keyboard)


if __name__ == '__main__':
    main()
