from keyboards import *
import json


def get_data(language: str) -> (dict, dict, dict, dict):
    with open(f"language_data/{language}.json") as language_data:
        data = json.load(language_data)
        print(data["characters"]["e"])


def get_sfbs(fingers: list[list[str]]) -> int:
    return 0


class LayoutAnalyser:
    def __init__(self, kb: Keyboard):

        self.sfb = get_sfbs(kb.fingers)
