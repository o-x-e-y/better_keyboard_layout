from corpus_analysis.analyse_corpus import analyse_corpus
from keyboards import *

if __name__ == "__main__":
    # layout_name = "dvorak"
    # kb = AnsiKeyboard(*layouts[layout_name], symbols=layout_symbols[layout_name])

    analyse_corpus(text_directory="text", language="dutch_english", update=True)
