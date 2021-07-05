from corpus_analysis.analyse_corpus import analyse_corpus
from keyboards import *
from analyse_layout import LayoutAnalyzer
from math import sqrt, isqrt
from math import log
from pprint import pprint
import pathlib
from glob import glob
from tools import *


if __name__ == "__main__":
    # layout_name = "colemak qix"
    # keyboard = IsoKeyboard(*layouts[layout_name], symbols=layout_symbols[layout_name])
    # print(keyboard)
    # analyzer = LayoutAnalyzer(keyboard, "iweb_corpus")

    analyse_corpus(language="iweb_corpus", update=True)
