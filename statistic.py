import matplotlib.pyplot as plt
from db import get_user_data


def pie_plot_creation(u_id, d_from, d_to, title):
    """
    Данная функция нужна для построения круговой диаграммы по данным пользователя.
    Круговая диаграмма может быть построена:
    - за сегодня
    - за текущий месяц
    - за предыдущий месяц
    :param u_id: id пользователя
    :param d_from: начальная дата
    :param d_to: конечная дата
    :param title: название диаграммы
    :return: True - диагрмма построена, False - данных за указанный период нет
    """
    query = """
    SELECT t1.description AS name, sum(t2.value) AS value
    FROM u_inout AS t1
    INNER JOIN inout AS t2
    ON t1.io_id = t2.io_id
    WHERE t1.u_id = %s
    AND t1.type = 'out'
    AND t2.date BETWEEN %s AND %s
    GROUP BY t1.description
    ORDER BY value DESC;
    """
    params = (u_id, d_from, d_to)

    df = get_user_data(query=query, params=params)
    if df.empty:
        return False

    # Делаем в названиях категорий все первые буквы заглавными
    df['name'] = df['name'].str.capitalize()

    # теперь нам нужно отделить мелкие траты от крупных, добавить в DF с крупными данными строку Отальное
    # (если кол-во строк для Остальных трат больше >=2)
    # Создаем вспомогательную колонку weight
    # (признак, по которому мы будем определять, нужно ли нам отделять траты в Остальное)
    df['weight'] = df.value * 100 / df.value.sum()

    # Если количество трат (величина которых больше пяти процентов от общего количества за рассматриваемый период)
    # больше одной, то есть смысл отделить их в отдельную круговую диатрамму,
    # а в основной такие траты обьединить в Остальное
    if df[df.weight <= 5].weight.count() >= 2:
        other_data = df[df.weight <= 5][['name', 'value']].reset_index(drop=True)
        main_data = df[df.weight > 5][['name', 'value']].append({'name': 'Остальное', 'value': other_data.value.sum()},
                                                                ignore_index=True)

        # Делаем легенду для первой диаграммы с Основными тратами
        legend1 = list()
        for i, value in enumerate(main_data.value):
            legend1.append('{}: {:.2f} руб.'.format(main_data.name[i], value))

        # И также легенду для диаграммы с Остальными тратами
        legend2 = list()
        for i, value in enumerate(other_data.value):
            legend2.append('{}: {:.2f} руб.'.format(other_data.name[i], value))

        # Строим наши диаграммы
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 6.5))
        ax1.pie(main_data.value, labels=main_data.name, autopct=lambda pct: pie_data(pct), pctdistance=0.75,
                startangle=0, wedgeprops=dict(width=0.5))
        ax2.pie(other_data.value, labels=other_data.name, autopct=lambda pct: pie_data(pct), pctdistance=0.75,
                startangle=0, wedgeprops=dict(width=0.5))
        ax1.legend(legend1, loc=9, bbox_to_anchor=(0.5, 0))
        ax2.legend(legend2, loc=9, bbox_to_anchor=(0.5, 0))
        ax1.set_title(f'Траты {title}\nОсновные')
        ax2.set_title(f'Траты {title}\nОстальное')
        ax1.axis('equal')
        ax2.axis('equal')
        fig.tight_layout(rect=(0, 0, 1, 1))

        plt.savefig(f'{u_id}.png', bbox_inches='tight', dpi=80)

    # Если нет смысла отделять данные в категорию остальное, то отправим одну круговую диаграмму
    else:
        # Делаем легенду для диаграммы
        legend = list()
        for i, value in enumerate(df.value):
            legend.append('{}: {:.2f} руб.'.format(df.name[i], value))

        # Строим нашу диаграмму
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))
        ax.pie(df.value, labels=df.name, autopct=lambda pct: pie_data(pct), pctdistance=0.75, startangle=0,
               wedgeprops=dict(width=0.5))
        ax.legend(legend, loc=9, bbox_to_anchor=(0.5, 0))
        ax.set_title(f'Траты {title}')
        ax.axis('equal')
        fig.tight_layout(rect=(0, 0, 1, 1))

        plt.savefig(f'{u_id}.png', bbox_inches='tight', dpi=80)
    return True


def pie_data(pct):
    return "{:.1f}%".format(pct)
