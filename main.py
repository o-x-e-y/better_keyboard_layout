from corpus_analysis.analyse_corpus import analyse_corpus, make_unique_corpus_copy
from keyboards import *
from analyse_layout import LayoutAnalyzer, get_language_data, get_unique_data
import math
from math import log
from pprint import pprint
import pathlib
from glob import glob
from tools import *
import itertools
from collections import defaultdict


def finger_sfb(finger: tuple, bigrams: dict[float], fingers_highest: list[tuple[str, float]], finger_nr: int):
    total = 0
    for bigram in itertools.combinations(finger, 2):
        sfb = ''.join(sorted(bigram))
        try:
            total += bigrams[sfb]
        except KeyError:
            pass
        
    if total > fingers_highest[finger_nr][1]:
        return ''.join(finger), total
    return None


def max_sfb_keyboard():
    characters = "abcdefghijklmnopqrstuvwxyz',.;"
    bigrams = get_unique_data(get_language_data("iweb_corpus")["bigrams"])

    finger_sizes = [3, 3, 3, 6, 6, 3, 3, 3]
    finger_sizes.sort(reverse=True)
    highest_template = ("", 0.0)
    fingers_highest = [highest_template for _ in range(len(finger_sizes))]

    for finger_nr, size in enumerate(finger_sizes):
        for finger in itertools.combinations(characters, size):
            finger_plus_sfb = finger_sfb(finger, bigrams, fingers_highest, finger_nr)
            if finger_plus_sfb is not None:
                fingers_highest[finger_nr] = finger_plus_sfb
        characters = ''.join([c for c in characters if c not in fingers_highest[finger_nr][0]])
        print(f"Finger {finger_nr} done, result is {''.join(fingers_highest[finger_nr][0])}")

    total = 0.0
    top_row, homerow, bot_row = "", "", ""
    for size, (finger, score) in zip(finger_sizes, fingers_highest):
        size //= 3
        top_row += finger[:size]
        homerow += finger[size: size*2]
        bot_row += finger[size*2:]
        total += score
    print(f"The highest sfb% using this method gives a % of {total}")
    return Keyboard(top_row, homerow, bot_row)


if __name__ == "__main__":
    # layout_name = "colemak qix"
    # keyboard = IsoKeyboard(*layouts[layout_name], symbols=layout_symbols[layout_name])
    # layout_name = "qwerty"
    # keyboard2 = IsoKeyboard(*layouts[layout_name], symbols=layout_symbols[layout_name])

    # with LayoutAnalyzer(language="iweb_corpus", precision=10000) as la:
    #     la.analyse(keyboard2)

    print(max_sfb_keyboard())
