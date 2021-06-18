from collections import defaultdict
from glob import glob
import concurrent.futures
from collections import Counter
import json
from os.path import isfile, getsize
from os import cpu_count
from textwrap import wrap
from time import perf_counter


def time_this(func):

    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"\"{func.__name__}\" took {round(end - start, ndigits=6 if end-start < 1 else 3)} second(s)\n")
        return result

    return wrapper


def _utf_to_ascii_table():
    utf_stuff =  "\t\n \"+:<>?ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_{|}~«´»ÀÁÂÄÇÈÉÊËÌÍÎÏÐÑÒÓÔÖÙÚÛÜÝàáâäçèéêëìíîïðñòóôö÷øùúûüý‘“”’–ʹ͵"
    translation = "   \'=;,./abcdefghijklmnopqrstuvwxyz\\-[\\]`'''aaaaceeeeiiiidnoooouuuuyaaaaceeeeiiiidnoooo/ouuuuy''''-''"
    exceptions = utf_stuff + translation
    replace = ''.join([chr(c) for c in range(0, int("110000", 16)) if chr(c) not in exceptions])
    return str.maketrans(utf_stuff, translation, replace)


sanitization_table = _utf_to_ascii_table()


def sanitize_bigrams(bigrams: dict[str, int]):
    double_bigrams = {bigram for bigram in bigrams.keys() if bigram[0] != bigram[1] and ' ' not in bigram}
    for double_bigram in double_bigrams:
        bigrams.pop(double_bigram)
    return bigrams


def sanitize_skipgrams(skipgrams: dict[str, int]):
    double_skipgrams = {skipgram for skipgram in skipgrams.keys() if skipgram[0] != skipgram[1] and ' ' not in skipgram}
    for double_skipgram in double_skipgrams:
        skipgrams.pop(double_skipgram)
    return skipgrams


@time_this
def sanitize_corpus_data(corpus_data: dict[str, dict[str, int]]):
    with concurrent.futures.ProcessPoolExecutor(2) as executor:
        bigrams_exec = executor.submit(sanitize_bigrams, corpus_data["bigrams"])
        skipgrams_exec = executor.submit(sanitize_skipgrams, corpus_data["skipgrams"])

        corpus_data["bigrams"] = bigrams_exec.result()
        corpus_data["skipgrams"] = skipgrams_exec.result()

        return corpus_data


def analyse_file(text: str):
    characters = defaultdict(int)
    bigrams = defaultdict(int)
    skipgrams = defaultdict(int)

    for i in range(len(text)-2):
        characters[text[i]] += 1
        bigrams[text[i: i+2]] += 1
        skipgrams[text[i] + text[i+2]] += 1

    return {
        "characters":   dict(characters),
        "bigrams":      dict(bigrams),
        "skipgrams":    dict(skipgrams)
    }


@time_this
def generate_complete_data(corpus_iterator):
    characters = Counter()
    bigrams = Counter()
    skipgrams = Counter()

    for data in corpus_iterator:
        characters += Counter(data["characters"])
        bigrams += Counter(data["bigrams"])
        skipgrams += Counter(data["skipgrams"])

    sum_characters = sum(characters.values())
    characters = {k: v / sum_characters for k, v in characters.items()}

    sum_bigrams = sum(bigrams.values())
    bigrams = {k: v / sum_bigrams for k, v in bigrams.items()}

    sum_skipgrams = sum(skipgrams.values())
    skipgrams = {k: v / sum_skipgrams for k, v in skipgrams.items()}

    return {
        "characters":   dict(sorted(characters.items(), key=lambda item: item[1], reverse=True)),
        "bigrams":      dict(sorted(bigrams.items(), key=lambda item: item[1], reverse=True)),
        "skipgrams":    dict(sorted(skipgrams.items(), key=lambda item: item[1], reverse=True))
    }


def _split_length(piece: tuple[str, list[int, int]]):
    """
    Given a tuple containing a string and a list containing
    split count and the length, gives the length of the split
    :param piece: the tuple
    :return: the length of the path's content
    """
    return piece[1][1]


def _all_small_splits(split_info: list[list[int, int]]):
    for info in split_info:
        if info[1] > 2_000_000:
            return False
    return True


def _has_max_splits(split_info: list[list[int, int]], cpus):
    for info in split_info:
        if info[0] >= cpus:
            return True
    return False


def create_splits(language: str, text_directory: str):
    """
    Generates a more optimal distribution of work to analyse.
    Creates the framework to split big texts up into smaller parts, if applicable.
    :param language: the language to use when looking for text files.
    :param text_directory: the directory the files should be in.
    :return: a list of tuples, which contain the path to the text and the amount pieces it should be split into.
    """
    paths = glob(f"{text_directory}/{language}/*.txt")
    if len(paths) == 0:
        return None
    split_info = {path: [1, getsize(path)] for path in paths}
    cpus = cpu_count()
    values = split_info.values()

    while not _all_small_splits(values) and not _has_max_splits(values, cpus):
        split_info = sorted(split_info.items(), key=_split_length, reverse=True)

        split_info[0][1][1] *= split_info[0][1][0] / (split_info[0][1][0] + 1)
        split_info[0][1][0] += 1

        split_info = dict(split_info)
        values = split_info.values()

    return [(path, info[0]) for path, info in split_info.items()]


@time_this
def do_the_wrapping(text, width, split_count):
    return wrap(text, width=width // split_count + 1)


def split_text(splits):
    print("running")
    path, split_count = splits
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read().translate(sanitization_table)
        width = len(text)
        if split_count == 1:
            return [text]
        return do_the_wrapping(text, width, split_count)


@time_this
def do_the_splitting(splits):
    if len(splits) < 30:
        with concurrent.futures.ProcessPoolExecutor(12) as executor:
            return sum(list(executor.map(split_text, splits)), [])
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            return sum(list(executor.map(split_text, splits)), [])


@time_this
def analyse_corpus(language="english", text_directory="text", update=False):
    if not update and isfile(f"language_data/{language.lower()}.json"):
        return

    splits = create_splits(language, text_directory)
    if splits:
        texts = do_the_splitting(splits)
        print(len(texts))
    else:
        print("There are no files in that directory")
        return

    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     corpus_data = generate_complete_data(executor.map(analyse_file, texts))
    #
    # with open(f"language_data/{language}.json", 'w') as language_data:
    #     json.dump(corpus_data, language_data, indent='\t', separators=(',', ': '))
