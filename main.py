from config import TOKEN
from db import init_db, collect_user, collect_msg_into_db, add_cat_into_db, check_user, check_category
from db import get_my_cat_db, add_exp_into_db, get_limit, set_state, set_limit_db, get_state
from db import spent_daily
from logics import msg_parser, test_msg, answers
from statistic import pie_plot_creation
from keyboards import *
from exceptions import *
from _collections import defaultdict
from datetime import date, timedelta
import telebot
import re

bot = telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    if not check_user(message.from_user.id):
        collect_user(message.from_user)
        bot.send_message(message.chat.id, 'Привет!\n'
                                          'Я помогу тебе контролировать твои расходы\n'
                                          'Для начала рекомендую тебе установить твой суточный лимит. '
                                          'Это величина, которую не должна будет превышать сумма твоих трат за день\n'
                                          'Это можно сделать с помощью команды /set\_limit\n\n'
                                          'Для того, что бы узнать что я еще умею воспользуйся командой /help',
                         parse_mode='Markdown', reply_markup=main_keyboard())
    else:
        bot.send_message(message.chat.id, 'Мы с тобой уже знакомы ' + u'\U0001F609' + '\n'
                                                                                      'Если что-то непонятно, '
                                                                                      'воспользуйся\n/help',
                         reply_markup=main_keyboard())


@bot.message_handler(commands=['help'])
def help_ini(message):
    collect_user(message.from_user)
    bot.send_message(message.chat.id, 'Для того, чтобы я мог записать трату, отправь мне сообщение в формате:\n'
                                      '*[Категория] [+-][сумма] [дата]*\n'
                                      'где *дата* - необязательный параметр\n'
                                      'Например:\n'
                                      '_Продукты 25.50 1/11/2019_\n'
                                      'Это значит что 1-го ноября 2019 года я потратил 25 руб. 50 копеек на '
                                      'продукты\n'
                                      '_Зарплата +5000_ - сегодня я получил зарплату в размере 5 т.р.\n'
                                      '*"+"* или *"-"* необходимо указывать если категория новая '
                                      '(что бы я мог понять куда ее отнести - к доходам или к расходам). По '
                                      'умолчанию *"-"* (если не укажешь)\n'
                                      'Если дату не укажешь, я пойму что трата была совершена сегодня\n'
                                      'Также можно указать только день, в таком случае месяц и '
                                      'год будут считаться текущими\n'
                                      'Или день и месяц, тогда год - текущий\n\n'
                                      'Описание команд ты можешь посмотреть с помощью /commands', parse_mode='Markdown')


@bot.message_handler(commands=['commands'])
def all_commands(message):
    bot.send_message(message.chat.id, '/start - стартовая команда для того, чтобы начать со мной диалог. '
                                      'Повторно запускать не нужно\n'
                                      '/help - если не понятно как я работаю и вообще зачем я нужен, '
                                      'воспользуйся этой командой\n'
                                      '/set_limit - с помощью этой команды ты можешь установить суточный лимит. '
                                      'Это величина, которую не должна будет превышать сумма твоих трат за день\n'
                                      '/get_limit - эта команда позволяет узнать величину твоего суточного лимита\n'
                                      '/set_outcome - добавить категории трат (бензин, продукты и т.д.)\n'
                                      'Если их несколько, перечисли их через запятую\n'
                                      '/set_income - добавить категории доходов (зарплата, репетиторство и т.д.)\n'
                                      'Если их несколько, перечисли их через запятую\n'
                                      '/my_categories - эта команда выведет список твоих категорий трат и доходов\n'
                                      '/stop - команда, сбрасывающая состояние пользователя (например, если '
                                      'после вызова команды /set_limit, вы передумали изменять свой суточный лимит')


@bot.message_handler(commands=['stop'])
def drop_state(message):
    set_state(0, message.chat.id)
    if get_state(message.chat.id) == 0:
        bot.send_message(message.chat.id, answers('Yes'))
    else:
        bot.send_message(message.chat.id, 'Ошибка, попробуй еще раз')


@bot.message_handler(commands=['my_categories'])
def get_my_cat(message):
    """
    Функция возвращает список категорий пользователя (трат и доходов) если были добавлены
    В противном случает сообщает пользователю что категории еще не добавлены и предлагает добавить
    с помощью команд /set_outcome и /set_income
    :param message: обьект message
    :return: сообщение пользователю со списком категорий если они были добавлены
    """
    cats = defaultdict(str)
    for cat, cat_type in get_my_cat_db(message.from_user.id):
        cats[cat_type] += f'{cat}\n'

    # Отправляем категории пользователю
    r_msg = ''
    if cats == {}:
        r_msg = 'Ничего не нашел, видимо мы с тобой еще ничего не добавляли\n' \
                'Это можно сделать с помощью команд /set\_outcome и /set\_income'
    else:
        for k in cats.keys():
            if k == 'out':
                r_msg += f'*Твои категории трат:*\n{cats["out"]}'
            else:
                r_msg += f'*Твои категории доходов:\n*{cats["in"]}'
    bot.send_message(message.chat.id, r_msg, parse_mode='Markdown')


@bot.message_handler(commands=['get_limit'])
def get_limit_main(message):
    """
    Ф-ция по ID пользователя находит в DB в таблице limits значение последнего внесенного суточного лимита.
    Суточный лимит это величина, которую не дожна будет превышать сумма трат пользователя.
    Значений суточных лимитов для одного пользователя может быть несколько, но не больше одного на конкретную дату.
    :param message: обьект message
    :return: отправляет сообщение пользователю с величиной его суточного лимита
    """
    lim = get_limit(message.chat.id)
    if lim is not None:
        bot.send_message(message.chat.id, f'Твой суточный лимит: *{str(lim)}* руб.', parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'Суточный лимит еще не установлен\n'
                                          'Будем устанавливать?',
                         reply_markup=y_n_keyboard('set_limit'))


@bot.message_handler(commands=['get_stat'])
def get_stat_ini(message):
    bot.send_message(message.chat.id, 'За какой период ты хочешь получить статистику по тратам?',
                     reply_markup=statistic_kb())


@bot.message_handler(commands=['set_limit'])
def set_limit_ini(message):
    bot.send_message(message.chat.id, 'Введи сумму')
    set_state(4, message.chat.id)


@bot.message_handler(func=lambda msg: get_state(msg.chat.id) == 4, content_types=['text'])
def set_limit(message):
    try:
        value = int(message.text.strip())
        if value < 0:
            raise NegativeLimit
        set_limit_db(message.from_user.id, value)
        bot.send_message(message.chat.id, f'{answers("Yes")}\nСуточный лимит в размере *{value}* руб. установлен',
                         parse_mode='Markdown')
        set_state(0, message.from_user.id)
    except ValueError:
        bot.send_message(message.chat.id, 'Суточный лимит не установлен\n'
                                          'Используй только цифры\n'
                                          'Попробуй еще раз')
    except NegativeLimit:
        bot.send_message(message.chat.id, 'Суточный лимит не установлен\n'
                                          'Значение не должно быть отрицательным\n'
                                          'Попробуй еще раз')


@bot.message_handler(commands=['set_outcome'])
def set_outcome_ini(message):
    bot.send_message(message.chat.id, 'Введи категории трат, которые ты хочешь добавить')
    set_state(1, message.chat.id)


@bot.message_handler(commands=['set_income'])
def set_income_ini(message):
    bot.send_message(message.chat.id, 'Введи категории доходов, которые ты хочешь добавить')
    set_state(2, message.chat.id)


# В проверке состояния пользователя:
# 1 - это трата
# 2 - это доход (зарплата к примеру)
@bot.message_handler(func=lambda msg: get_state(msg.chat.id) in (1, 2), content_types=['text'])
def add_categories(message):
    txt = message.text.strip().lower()

    # Проверяем, что в перечисленных тратах присутствуют только пробелы, цифры, буквы, символы '+' или '-'
    # и они разделены запятыми если их указано несколько
    if not re.fullmatch(r'[а-яёa-z0-9 -+]+(?:[,][а-яёa-z0-9 -+]+)*', txt):
        bot.send_message(message.chat.id, 'Не понимаю\nУкажи категории через запятую\nМожно использовать только '
                                          'буквы, цифры и символы *"-"* или *"+"*', parse_mode="Markdown")
    else:
        cats = [c.strip() for c in txt.split(',')]
        if get_state(message.chat.id) == 1:
            cat_type = 'out'
        else:
            cat_type = 'in'

        for cat in cats:
            if not check_category(cat, message.chat.id):
                add_cat_into_db(message.from_user.id, cat, cat_type)

        # Все, мы добавили новые категории если они отсутствовали
        # поэтому выводим сообщение об успешно выполненой команде
        # сбрасываем состояние пользователя на 0
        set_state(0, message.chat.id)
        bot.send_message(message.chat.id, f"{answers('Yes')}\nНовые категории добавлены")


@bot.message_handler(func=lambda msg: test_msg(msg) == 1 and get_state(msg.from_user.id) == 0, content_types=['text'])
def collect_exp(message):
    """
    Фунция записывает трату/доход в базу

    На вход принимает обьект message и передает текст сообщения (str) ф-ции msg_parser

    msg_parser парсит сообщение и возвращает данные которые необходимо занести в базу - категорию, ее тип (in/out),
    сумму и дату.
    """
    try:
        cat, c_type, amount, d = msg_parser(message.text)
        collect_msg_into_db(message.from_user.id, message.text)  # записываем текст сообщения в базу данных

        if not check_category(cat, message.chat.id):
            bot.send_message(message.chat.id, f"Категорию {'трат' if c_type == 'out' else 'доходов'} *{cat}* "
                                              f"для тебя я еще не добавлял\n"
                                              "Добавить новую категорию?", parse_mode='Markdown',
                             reply_markup=y_n_keyboard(f'add|{cat}|{c_type}|{amount}|{d}'))
        else:
            add_exp_into_db(message.from_user.id, cat, amount, d)
            record_confirm(message.chat.id)
    except WrongAmount:
        bot.send_message(message.chat.id, 'Ошибка, неправильно указана сумма')
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка, такой даты не существует')
    except WrongDate:
        bot.send_message(message.chat.id, 'Ошибка, указанная дата больше текущей')


@bot.message_handler(func=lambda msg: test_msg(msg) is None)
def some_text(message):
    bot.send_message(message.chat.id, 'Я не понимаю\nПопробуй воспользоваться /help')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        var = call.data.split('|')
        if var[0] == 'add':
            # var[1] - категория
            # var[2] - тип (in или out)
            # var[3] - сумма
            # var[4] - дата
            add_cat_into_db(call.message.chat.id, var[1], var[2])  # добавляем новую категорию в базу
            add_exp_into_db(call.message.chat.id, var[1], var[3], var[4])
            record_confirm(msg_id=call.message.chat.id)
        elif var[0] == 'set_limit':
            set_limit_ini(call.message)
        elif call.data == 'cb_button_no':
            bot.send_message(chat_id=call.message.chat.id, text=answers('No'))
        elif call.data == 'monthly_stat_current':
            d_from = date.today().replace(day=1).strftime('%Y-%m-%d')
            d_to = (date.today().replace(day=1, month=date.today().month + 1) - timedelta(days=1)).strftime('%Y-%m-%d')
            if not pie_plot_creation(u_id=call.message.chat.id, d_from=d_from, d_to=d_to):
                bot.send_message(call.message.chat.id, 'Данные за указаный период отсутствуют')
            else:
                bot.send_photo(call.message.chat.id, photo=open(f"{call.message.chat.id}.jpg", 'rb'))
        bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')


def main():
    init_db(force=False)
    bot.polling(none_stop=True, interval=0)


def record_confirm(msg_id):
    lim = get_limit(msg_id)
    spent = spent_daily(msg_id)

    if lim is not None:
        value = lim - spent
        if value < 0:
            bot.send_message(msg_id, f'{answers("Yes")}\n'
                                     f'Суточный лимит превышен на\n*{-value}* руб.', parse_mode='Markdown')
        else:
            bot.send_message(msg_id, f'{answers("Yes")}\n'
                                     f'Осталось на сегодня\n*{value}* руб.', parse_mode='Markdown')
    else:
        bot.send_message(msg_id, f'{answers("Yes")}\n')


if __name__ == '__main__':
    main()
