import json
from tools import time_this
from math import log, sqrt
from pprint import pprint


def flatten_list(lists):
    flat = []
    for l in lists:
        flat.extend(l)
    return flat


def get_language_data(language: str) -> dict[dict[float]]:
    with open(f"language_data/{language}.json") as language_data:
        return json.load(language_data)


def effort_minmax(characters: dict[str, int], effort_grid: list[list[float]], is_max=True) -> float:
    effort = 0
    effort_nums = list(sorted(flatten_list(effort_grid), reverse=is_max))
    for prevalence, num in zip(characters.values(), effort_nums):
        effort += prevalence*num
    return effort


def get_effort_score(layout, characters: dict[str, int], effort_grid: list[list[float]], minmax: tuple[int, int]):
    effort = 0
    effort_min, effort_max = minmax
    for i, row in enumerate(layout):
        for j, key in enumerate(row):
            effort += characters[key] * effort_grid[i][j]
    print(effort_min, effort_max, effort)
    return round((effort_min + effort)/(effort_min + effort_max), 3)


def get_sfb_score(fingers: list[list[str]], data: dict, sfb_penalties: tuple[float, float, float]) -> float:
    return 0


def get_dsfb_score(fingers: list[list[str]], data) -> float:
    return 0


class LayoutAnalyzer:
    def __init__(self, sfb_penalties=(0, 1, 2), dsfb_penalty=0.5, is_staggered=True, language="iweb_corpus"):
        self.sfb_penalties = sfb_penalties
        self.dsfb_penalty = dsfb_penalty
        self.effort_grid = staggered_effort_grid() if is_staggered else matrix_effort_grid()
        self.data = get_language_data(language)
        effort_min = effort_minmax(self.data["characters"], self.effort_grid, is_max=False)
        effort_max = effort_minmax(self.data["characters"], self.effort_grid, is_max=True)
        self.effort_minmax = (effort_min, effort_max)

    def analyse(self, kb):
        effort = get_effort_score(kb.layout, self.data["characters"], self.effort_grid, self.effort_minmax)
        sfbs = get_sfb_score(kb.fingers, self.data, self.sfb_penalties)
        dsfbs = get_dsfb_score(kb.fingers, self.data)
        print(f"\n{effort = }, {sfbs = }, {dsfbs = }\ntotal = {effort+sfbs+dsfbs}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self


# def fitts_law_2d(distance_x, distance_y, finger_weight, x_weight=1.5, y_weight=1):
#     x_val = log(2*distance_x / 0.9 + 1, 3) * finger_weight * x_weight
#     y_val = log(2*distance_y / 0.9 + 1, 3) * finger_weight * y_weight
#     return finger_weight + sqrt(x_val**2 + y_val**2)


def distance(distance_x, distance_y, finger_weight, x_weight=1.5, y_weight=1):
    x_num = distance_x * finger_weight * x_weight + finger_weight
    y_num = distance_y * finger_weight * y_weight + finger_weight
    return sqrt(x_num**2 + y_num**2)


def matrix_effort_grid():
    weight_fingers = [1.6, 1.3, 1.1, 1.0, 1.0, 1.0, 1.0, 1.1, 1.3, 1.6]
    x_dist = [[0.0, 0.0, 0.0, 0.0, 0.6, 0.6, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.6, 0.6, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.6, 0.6, 0.0, 0.0, 0.0, 0.0]]
    y_dist = [[0.6, 0.3, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.3, 0.6],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.6, 0.6, 0.5, 0.4, 0.5, 0.5, 0.4, 0.5, 0.6, 0.6]]
    grid = [[], [], []]

    for i, (x_row, y_row) in enumerate(zip(x_dist, y_dist)):
        for weight_finger, x_distance, y_distance in zip(weight_fingers, x_row, y_row):
            grid[i].append(distance(x_distance, y_distance, weight_finger))
    return grid


def staggered_effort_grid():
    weight_fingers = [1.6, 1.3, 1.1, 1.0, 1.0, 1.0, 1.0, 1.1, 1.3, 1.6]
    x_dist = [[0.0, 0.0, 0.0, 0.0, 0.5, 0.8, 0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0, 0.6, 0.6, 0.0, 0.0, 0.0, 0.0],
              [0.2, 0.2, 0.2, 0.2, 1.2, 0.2, 0.2, 0.2, 0.2, 0.2]]
    y_dist = [[0.6, 0.3, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.3, 0.6],
              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
              [0.6, 0.6, 0.5, 0.4, 0.5, 0.5, 0.4, 0.5, 0.6, 0.6]]
    grid = [[], [], []]

    for i, (x_row, y_row) in enumerate(zip(x_dist, y_dist)):
        for weight_finger, x_distance, y_distance in zip(weight_fingers, x_row, y_row):
            grid[i].append(distance(x_distance, y_distance, weight_finger))
    return grid
