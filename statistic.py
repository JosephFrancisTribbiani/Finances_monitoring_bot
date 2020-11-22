import matplotlib.pyplot as plt
from db import get_user_data


def pie_plot_creation(u_id, d_from, d_to, title):
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

    labels = df.name
    sizes = df.value
    legend = list()
    for i, value in enumerate(sizes):
        legend.append(f'{labels[i]}: {value} руб.')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, startangle=0, wedgeprops=dict(width=0.5))
    lgd = ax1.legend(legend, loc=6, bbox_to_anchor=(1, 0.5))
    ax1.axis('equal')

    plt.savefig(f'{u_id}.jpg', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=72.72)
    return True
