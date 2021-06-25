from collections import defaultdict
from glob import glob
import concurrent.futures
import multiprocessing as mp
from collections import Counter
import json
from os.path import isfile, getsize
from os import cpu_count
from time import perf_counter
import pandas as pd
from functools import reduce


def time_this(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"\"{func.__name__}\" took {round(end - start, ndigits=6 if end-start < 0.1 else 3)} second(s)\n")
        return result

    return wrapper


def _utf_to_ascii_table():
    utf_stuff =  "\t\n \"+:<>?ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_{|}~«´»ÀÁÂÄÇÈÉÊËÌÍÎÏÐÑÒÓÔÖÙÚÛÜÝàáâäçèéêëìíîïðñòóôö÷øùúûüý‘“”’–ʹ͵"
    translation = "   \'=;,./abcdefghijklmnopqrstuvwxyz\\-[\\]`'''aaaaceeeeiiiidnoooouuuuyaaaaceeeeiiiidnoooo/ouuuuy''''-''"
    exceptions = utf_stuff + translation
    replace = ''.join([chr(c) for c in range(0, int("110000", 16)) if chr(c) not in exceptions])
    return str.maketrans(utf_stuff, translation, replace)


sanitization_table = _utf_to_ascii_table()


def sanitize_str2(strs: dict[str, int]):
    return {str2: val for str2, val in strs.items() if (str2[0] != str2[1] and ' ' not in str2)}


def sanitize_str3(strs: dict[str, int]):
    return {str3: val for str3, val in strs.items() if len(set(str3)) == 3 and ' ' not in str3}


def sanitize_data(bigrams: dict[str, int], skipgrams: dict[str, int], trigrams: dict[str, int]):
    with concurrent.futures.ProcessPoolExecutor(2) as executor:
        bigrams_exec = executor.submit(sanitize_str2, bigrams)
        skipgrams_exec = executor.submit(sanitize_str2, skipgrams)
        trigrams_exec = executor.submit(sanitize_str3, trigrams)

        bigrams = bigrams_exec.result()
        skipgrams = skipgrams_exec.result()
        trigrams = trigrams_exec.result()

        return bigrams, skipgrams, trigrams


@time_this
def generate_complete_data(characters, bigrams, skipgrams, trigrams):
    start = perf_counter()

    # data = reduce(
    #     lambda x, y: x.add(y, fill_value=0),
    #     (pd.DataFrame.from_dict(d) for d in corpus_iterator)
    # ).to_dict()

    end = perf_counter()
    print(f"\"adding data together\" took {round(end - start, ndigits=6 if end-start < 0.1 else 3)} second(s)\n")

    del characters[" "]
    bigrams, skipgrams, trigrams = sanitize_data(bigrams, skipgrams, trigrams)

    sum_characters = sum(characters.values())
    characters = {k: v / sum_characters for k, v in characters.items()}

    sum_bigrams = sum(bigrams.values())
    bigrams = {k: v / sum_bigrams for k, v in bigrams.items()}

    sum_skipgrams = sum(skipgrams.values())
    skipgrams = {k: v / sum_skipgrams for k, v in skipgrams.items()}

    sum_trigrams = sum(trigrams.values())
    trigrams = {k: v / sum_trigrams for k, v in trigrams.items()}

    return {
        "characters":   dict(sorted(characters.items(), key=lambda item: item[1], reverse=True)),
        "bigrams":      dict(sorted(bigrams.items(), key=lambda item: item[1], reverse=True)),
        "skipgrams":    dict(sorted(skipgrams.items(), key=lambda item: item[1], reverse=True)),
        "trigrams":     dict(sorted(trigrams.items(), key=lambda item: item[1], reverse=True))
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


def split_text(splits):
    path, split_count = splits
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read().translate(sanitization_table)
        width = len(text)
        if split_count == 1:
            return [text]
        size = width // split_count + 1
        return [text[i * size:(i+1) * size] for i in range(split_count)]


def analyse_file(text: str, characters: dict, bigrams: dict, skipgrams: dict, trigrams: dict):

    for i in range(len(text)-2):
        characters.setdefault(text[i], 0)
        characters[text[i]] += 1

        bigrams.setdefault(text[i: i+2], 0)
        bigrams[text[i: i+2]] += 1

        skipgrams.setdefault(text[i] + text[i+2], 0)
        skipgrams[text[i] + text[i+2]] += 1

        trigrams.setdefault(text[i: i+3], 0)
        trigrams[text[i: i+3]] += 1

    # return {
    #     "characters":   dict(characters),
    #     "bigrams":      dict(bigrams),
    #     "skipgrams":    dict(skipgrams),
    #     "trigrams":     dict(trigrams)
    # }


@time_this
def analyse_corpus(language="english", text_directory="text", update=False):
    if not update and isfile(f"language_data/{language.lower()}.json"):
        return

    splits = create_splits(language, text_directory)
    if len(splits) >= 1:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            texts = sum(list(executor.map(split_text, splits)), [])
    else:
        print("There are no files in that directory")
        return

    manager = mp.Manager()
    characters = manager.dict()
    bigrams = manager.dict()
    skipgrams = manager.dict()
    trigrams = manager.dict()
    processes = []
    for text in texts:
        p = mp.Process(target=analyse_file, args=(text, characters, bigrams, skipgrams, trigrams,))
        p.start()
        processes.append(p)

    for process in processes:
        process.join()

    print(characters)
    corpus_data = generate_complete_data(dict(characters), dict(bigrams), dict(skipgrams), dict(trigrams))
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     corpus_data = generate_complete_data(executor.map(analyse_file, texts))

    with open(f"language_data/{language}.json", 'w') as language_data:
        json.dump(corpus_data, language_data, indent='\t', separators=(',', ': '))
