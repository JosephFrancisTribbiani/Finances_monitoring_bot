from telebot import types


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
    cb_button_current_month = 'stat|cur_m'
    cb_button_previous_month = 'stat|pre_m'
    cb_button_today = 'stat|td'

    titles = {
        cb_button_today: "За сегодня",
        cb_button_current_month: "За текущий месяц",
        cb_button_previous_month: "За предыдущий месяц"
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(titles[cb_button_today], callback_data=cb_button_today))
    markup.add(types.InlineKeyboardButton(titles[cb_button_current_month], callback_data=cb_button_current_month))
    markup.add(types.InlineKeyboardButton(titles[cb_button_previous_month], callback_data=cb_button_previous_month))

    return markup
