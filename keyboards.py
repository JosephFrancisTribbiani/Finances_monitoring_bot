from telebot import types
from datetime import datetime

MONTHS = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь'
}


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


def main_keyboard():
    main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    main_markup.add('/help', '/commands', '/stop')
    main_markup.add('/set_limit', '/set_income', '/set_outcome')
    main_markup.add('/my_categories')
    main_markup.add('/get_limit', '/get_stat')
    return main_markup


def statistic_kb():
    cb_button_monthly_stat = 'monthly_stat_current'

    titles = {
        cb_button_monthly_stat: "За текущий месяц"
    }

    markup = types.InlineKeyboardMarkup()
    keyboard = [
        types.InlineKeyboardButton(titles[cb_button_monthly_stat], callback_data=cb_button_monthly_stat)
    ]

    return markup.add(*keyboard)
