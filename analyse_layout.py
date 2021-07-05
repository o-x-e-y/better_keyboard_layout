import json
from tools import time_this
from math import log, sqrt
from pprint import pprint


def get_data(language: str) -> dict[dict[float]]:
    with open(f"language_data/{language}.json") as language_data:
        return json.load(language_data)


def get_effort_score(layout, data) -> float:
    return 0


def get_sfb_score(fingers: list[list[str]], data) -> float:
    return 0


def get_dsfb_score(fingers: list[list[str]], data) -> float:
    return 0


class LayoutAnalyzer:
    def __init__(self, kb, language="iweb_corpus"):
        self.data = get_data(language)
        self.effort = get_effort_score(kb.layout, self.data)
        self.sfbs = get_sfb_score(kb.fingers, self.data)
        self.dsfbs = get_dsfb_score(kb.fingers, self.data)


def analyse_layout(kb, language="iweb_corpus"):
    return 0


def fitts_law_2d(distance_x, distance_y, finger_weight, x_weight=1.5, y_weight=1):
    x_val = log(2*distance_x / 0.9 + 1, 3) * finger_weight * x_weight
    y_val = log(2*distance_y / 0.9 + 1, 3) * finger_weight * y_weight
    return finger_weight + sqrt(x_val**2 + y_val**2)


def analyse_thing():
    weight_fingers = [1.6, 1.3, 1.1, 1.0, 1.0, 1.0, 1.0, 1.1, 1.3, 1.6]

    x_matrix = [[0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]]
    y_matrix = [[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]

    x_stagger = [[0.2, 0.2, 0.2, 0.2, 0.8, 1.2, 0.2, 0.2, 0.2, 0.2],
                 [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
                 [0.3, 0.3, 0.3, 0.3, 1.2, 0.3, 0.3, 0.3, 0.3, 0.3]]
    y_stagger = [[0.9, 0.8, 0.5, 0.6, 0.6, 0.6, 0.6, 0.5, 0.8, 0.9],
                 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [1.0, 0.8, 0.7, 0.6, 0.6, 0.6, 0.6, 0.7, 0.8, 1.0]]

    grid = [[], [], []]

    for i, (x_row, y_row) in enumerate(zip(x_stagger, y_stagger)):
        for weight_finger, x_distance, y_distance in zip(weight_fingers, x_row, y_row):
            grid[i].append("%.2f" % fitts_law_2d(x_distance, y_distance, weight_finger))
    pprint(grid, width=100)
