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
import analyse_layout as al


if __name__ == "__main__":
    layout_name = "dvorak"
    kb = AnsiKeyboard(*layouts[layout_name], symbols=layout_symbols[layout_name])

    al.get_data("iweb_corpus")

    # analyse_corpus(text_directory="text", language="new_dir", update=True)
