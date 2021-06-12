from collections import defaultdict
from glob import glob
import concurrent.futures
from collections import Counter
import json
from os.path import isfile


def _utf_to_ascii_table():
    utf_stuff =  "\t\n \"+:<>?ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_{|}~«´»ÀÁÂÄÇÈÉÊËÌÍÎÏÐÑÒÓÔÖÙÚÛÜÝàáâäçèéêëìíîïðñòóôö÷øùúûüý‘“”’"
    translation = "   \'=;,./abcdefghijklmnopqrstuvwxyz\\-[\\]`'''aaaaceeeeiiiidnoooouuuuyaaaaceeeeiiiidnoooo/ouuuuy''''"
    exceptions = utf_stuff + translation
    replace = ''.join([chr(c) for c in range(0, int("110000", 16)) if chr(c) not in exceptions])
    return str.maketrans(utf_stuff, translation, replace)


sanitization_table = _utf_to_ascii_table()


def analyse_file(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read().translate(sanitization_table)

        characters = defaultdict(int)
        bigrams = defaultdict(int)
        skipgrams = defaultdict(int)
        trigrams = defaultdict(int)

        for i in range(len(text)-2):
            if text[i] != ' ':
                characters[text[i]] += 1
                if text[i+1] != ' ':
                    bigrams[text[i: i+2]] += 1
                    if text[i+2] != ' ':
                        skipgrams[text[i] + text[i+2]] += 1
                        trigrams[text[i: i+3]] += 1

        return {
            "characters":   dict(characters),
            "bigrams":      dict(bigrams),
            "skipgrams":    dict(skipgrams),
            "trigrams":     dict(trigrams)
        }


def generate_complete_data(corpus_iterator):
    characters = Counter()
    bigrams = Counter()
    skipgrams = Counter()
    trigrams = Counter()

    for data in corpus_iterator:
        characters += Counter(data["characters"])
        bigrams += Counter(data["bigrams"])
        skipgrams += Counter(data["skipgrams"])
        trigrams += Counter(data["trigrams"])

    sum_characters = sum(characters.values())
    sum_bigrams = sum(bigrams.values())
    sum_skipgrams = sum(skipgrams.values())
    sum_trigrams = sum(trigrams.values())

    for key in characters.keys():
        characters[key] /= sum_characters

    for key in bigrams.keys():
        bigrams[key] /= sum_bigrams

    for key in skipgrams.keys():
        skipgrams[key] /= sum_skipgrams

    for key in trigrams.keys():
        trigrams[key] /= sum_trigrams

    return {
        "characters":   dict(reversed(sorted(characters.items(), key=lambda item: item[1]))),
        "bigrams":      dict(reversed(sorted(bigrams.items(), key=lambda item: item[1]))),
        "skipgrams":    dict(reversed(sorted(skipgrams.items(), key=lambda item: item[1]))),
        "trigrams":     dict(reversed(sorted(trigrams.items(), key=lambda item: item[1])))
    }


def analyse_corpus(text_directory="text", language="english", update=False):
    if not update and isfile(f"language_data/{language}.json"):
        return

    paths = glob(f"{text_directory}/{language}/*.txt")
    if len(paths) > 0:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            corpus_data = generate_complete_data(executor.map(analyse_file, paths))
    else:
        corpus_data = {}

    with open(f"language_data/{language}.json", 'w') as language_data:
        json.dump(corpus_data, language_data, indent='\t', separators=(',', ': '))
