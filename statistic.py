import pandas as pd
import matplotlib.pyplot as plt
from db import get_user_data


def pie_plot_creation(u_id, d_from, d_to):
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

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, startangle=0, wedgeprops=dict(width=0.5))
    ax1.axis('equal')

    plt.savefig(f'{u_id}.jpg', dpi=150)
    return True
