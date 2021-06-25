from keyboards import *
import json


def get_data(language: str) -> dict[dict[float]]:
    with open(f"language_data/{language}.json") as language_data:
        return json.load(language_data)


def get_effort(layout, data, ) -> float:
    return 0


def get_sfbs(fingers: list[list[str]], data) -> float:
    return 0


def get_dsfbs(fingers: list[list[str]], data) -> float:
    return 0


class LayoutAnalyser:
    def __init__(self, kb: Keyboard, language="iweb_corpus"):
        self.data = get_data(language)
        self.effort = get_effort(kb.layout)
        self.sfbs = get_sfbs(kb.fingers, self.data)
        self.dsfbs = get_dsfbs(kb.fingers, self.data)
