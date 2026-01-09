import base64
import io
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt


def get_graph(dates, prices):
    plt.clf()
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(5, 3))
    plt.plot(dates, prices, marker='o', linestyle='-', color='b')
    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph