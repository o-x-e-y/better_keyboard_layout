import concurrent.futures

from analyse_corpus import analyse_corpus
from time import perf_counter
from textwrap import wrap
from keyboards import *
import base64
import numpy as np
from random import randint
from klc.klc import from_keyboard_ansi
import json


if __name__ == "__main__":
    # from_keyboard_ansi(colemak, "English", "United States")
    # with open("layouts/colemak.klc", 'r', encoding='utf-16') as layout_file:
    #     print(repr(layout_file.read()[300:]))

    analyse_corpus(text_directory="text", language="iweb_corpus", update=True)
