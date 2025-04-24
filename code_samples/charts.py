import matplotlib.pyplot as plt
import json
from typing import TypedDict

class DataEntry(TypedDict):
    count: int
    city_code: str
    city_name: str
    color: str

plt.style.use('_mpl-gallery')

with open("./data.json", "r", encoding='utf-8') as data_file:
    data: list[DataEntry] = json.load(data_file)
    x = [city['city_code'] for city in data]
    y = [city['count'] for city in data]

    fig, ax = plt.subplots()

    ax.bar(x, y, width=1, edgecolor="white", linewidth=1)

    plt.show()