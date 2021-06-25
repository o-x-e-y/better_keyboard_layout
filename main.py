import concurrent.futures

from analyse_corpus import analyse_corpus
from time import perf_counter
from textwrap import wrap
from keyboards import *
import base64
import numpy as np
from random import randint
import klc.klc as klc
import json
import multiprocessing as mp
import concurrent.futures
from ctypes import windll
from analyse_corpus import time_this
from pprint import pprint
from collections import defaultdict


if __name__ == "__main__":
    layout_name = "mtgap"
    cur_layout = AnsiKeyboard(*layouts[layout_name], symbols=layout_symbols[layout_name])

    klc.from_keyboard(cur_layout, "English", "United States")

    # analyse_corpus(text_directory="text", language="new_dir", update=True)
