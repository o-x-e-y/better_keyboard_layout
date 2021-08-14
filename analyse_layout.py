import json
import stat

from tools import time_this
from math import log, sqrt
import itertools
from collections import namedtuple, defaultdict
from pprint import pprint


def flatten_list(lists):
    flat = []
    for l in lists:
        flat.extend(l)
    return flat


def get_language_data(language: str) -> dict[dict[float]]:
    with open(f"language_data/{language}.json") as language_data:
        return json.load(language_data)


def get_unique_data(data: dict, precision=100000000000) -> dict:
    unique_data = defaultdict(float)
    # precision = len(data) if len(data) > precision else precision
    for key, val in data.items():
        unique_data[''.join(sorted(key))] += val
        if len(unique_data) == precision:
            break
    return dict(unique_data)


def effort_minmax(characters: dict[str, int], effort_grid: list[list[float]]) -> float:
    min_effort, max_effort = 0, 0
    flat_effort_list = flatten_list(effort_grid)
    min_effort_nums = list(sorted(flat_effort_list, reverse=False))
    max_effort_nums = list(sorted(flat_effort_list, reverse=True))

    for prevalence, num in zip(characters.values(), min_effort_nums):
        min_effort += prevalence * num
    for prevalence, num in zip(characters.values(), max_effort_nums):
        max_effort += prevalence * num

    return min_effort, max_effort


def get_effort_score(layout, characters: dict[str, int], effort_grid: list[list[float]], minmax: tuple[int, int]):
    effort = 0
    effort_min, effort_max = minmax
    for i, row in enumerate(layout):
        for j, key in enumerate(row):
            effort += characters[key] * effort_grid[i][j]
    return 1 - round((effort - effort_min)/(effort_max - effort_min), 3)


def dsfb_minmax(characters: dict, bigrams: dict, penalties: namedtuple, dsfb_mod=1.0) -> float:
    total_listed = round(sum(bigrams.values()), 5)
    print(f"{total_listed = }\n")
    bound_min, bound_max = 0.0014, 0.12  # (0.0042 / 3), (0.36 / 3), these are estimates but should be close enough

    dsfb_min = (bound_min * (penalties.jump1 + 1) * 2 + bound_min * (penalties.jump2 + 1))
    dsfb_max = (bound_max * (penalties.jump1 + 1) * 2 + bound_max * (penalties.jump2 + 1))

    return round(dsfb_min * total_listed * dsfb_mod, 5), round(dsfb_max * total_listed * dsfb_mod, 5)


def get_dsfb_score(fingers: list[list[str]],
                   dsfbs: dict[str, float],
                   minmax: tuple,
                   penalties: namedtuple) -> float:
    total = 0
    dsfb_min, dsfb_max = minmax
    double_jump_2col = [False, False, True, True, True, True, False, True, True, False, False, True, True, False, False]

    for finger in fingers:
        dsfb_repr = {"single_jump": set(), "double_jump": set()}
        nr_of_cols = len(finger) // 3
        if nr_of_cols == 1:
            finger_bigrams = [''.join(sorted(finger[0:2])), ''.join(sorted(finger[1:])), ''.join(sorted(finger[0] + finger[2]))]
            dsfb_repr["single_jump"].update({finger_bigrams[0], finger_bigrams[1]})
            dsfb_repr["double_jump"].add(finger_bigrams[2])

            for bigram in finger_bigrams:
                try:
                    if bigram in dsfb_repr["single_jump"]:
                        total += dsfbs[bigram] * penalties.jump1
                    else:
                        total += dsfbs[bigram] * penalties.jump2
                except KeyError:
                    pass

        elif nr_of_cols == 2:
            for bigram_tuple, is_double in zip(itertools.combinations(finger, 2), double_jump_2col):
                try:
                    if is_double:
                        total += dsfbs[''.join(bigram_tuple)] * penalties.jump2
                    else:
                        total += dsfbs[''.join(bigram_tuple)] * penalties.jump1
                except KeyError:
                    pass

    print(f"{minmax = }, {total = }")
    return (total - dsfb_min)/(dsfb_max - dsfb_min)


class LayoutAnalyzer:
    def __init__(self,
                 language="iweb_corpus",
                 precision=100000000000,
                 sfb_penalties=(1, 2, 3),
                 dsfb_mod=0.5,
                 is_staggered=True):
        self.effort_grid = staggered_effort_grid() if is_staggered else matrix_effort_grid()

        self.data = get_language_data(language)
        self.unique_bigrams = get_unique_data(self.data["bigrams"], precision)
        self.unique_skipgrams = get_unique_data(self.data["skipgrams"], precision)

        self.effort_minmax = effort_minmax(self.data["characters"], self.effort_grid)

        penalties = namedtuple("penalties", ["none", "jump1", "jump2"])
        self.penalties = penalties(*sfb_penalties)

        self.sfb_minmax = dsfb_minmax(self.data["characters"], self.unique_bigrams, self.penalties)
        self.skipgram_minmax = dsfb_minmax(self.data["characters"], self.unique_skipgrams, self.penalties, dsfb_mod)

    @time_this
    def analyse(self, kb):
        effort = get_effort_score(kb.layout, self.data["characters"], self.effort_grid, self.effort_minmax)
        sfbs = get_dsfb_score(kb.fingers, self.unique_bigrams, self.sfb_minmax, self.penalties)
        dsfbs = get_dsfb_score(kb.fingers, self.unique_skipgrams, self.skipgram_minmax, self.penalties)

        print(f"\n{kb.name}\n{effort = },\n{sfbs = },\n{dsfbs = }\ntotal = {effort+sfbs+dsfbs}")

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
    return sqrt(x_num**2 + y_num**2) * finger_weight


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
