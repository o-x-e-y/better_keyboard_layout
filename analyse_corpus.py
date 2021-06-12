from collections import defaultdict
from glob import glob
import concurrent.futures
from collections import Counter
import json


def _utf_to_ascii_table():
    utf_stuff =  "\t\n \"+:<>?ABCDEFGHIJKLMNOPQRSTUVWXYZ\\_{|}~«´»ÀÁÂÄÇÈÉÊËÌÍÎÏÐÑÒÓÔÖÙÚÛÜÝàáâäçèéêëìíîïðñòóôö÷øùúûüý‘“”’"
    translation = "   \'=;,./abcdefghijklmnopqrstuvwxyz\\-[\\]`'''aaaaceeeeiiiidnoooouuuuyaaaaceeeeiiiidnoooo/ouuuuy''''"
    exceptions = utf_stuff + translation
    replace = ''.join([chr(c) for c in range(0, int("110000", 16)) if chr(c) not in exceptions])
    return str.maketrans(utf_stuff, translation, replace)


sanitization_table = _utf_to_ascii_table()


def utf8_to_ascii(c: str):
    return c.translate(sanitization_table)


def bigram_to_ascii(bigram: str, consider_accents=False):
    return


def sanitise_characters(char_data: dict[str, int]):
    new_char_data = defaultdict(int)

    for char, val in char_data.items():
        new_chars = utf8_to_ascii(char)
        if len(new_chars) > 0:
            for new_char in new_chars:
                new_char_data[new_char] += val

    sum_chars = sum(new_char_data.values())
    for char, val in new_char_data.items():
        new_char_data[char] /= sum_chars
    return dict(new_char_data)


def sanitise_bigrams(bigram_data: dict[str, int]):
    new_bigram_data = defaultdict(int)

    for bigram, val in bigram_data.items():
        new_bigrams = [utf8_to_ascii(bigram[0]), utf8_to_ascii(bigram[1])]
        if len(new_bigrams) > 0:
            for new_bigram in new_bigrams:
                new_bigram_data[new_bigram] += val

    sum_bigrams = sum(new_bigram_data.values())
    for bigram, val in new_bigram_data.items():
        new_bigram_data[bigram] /= sum_bigrams
    return dict(new_bigram_data)


def sanitise_skipgrams(skipgram_data: dict[str, int], consider_accents=False):
    sum_skipgrams = sum(skipgram_data.values())


def sanitise_trigrams(trigram_data: dict[str, int], consider_accents=False):
    sum_trigrams = sum(trigram_data.values())


def sanitise_data(corpus_data: dict[str, dict[str, int]], consider_accents=False):
    with concurrent.futures.ProcessPoolExecutor(4) as executor:
        clean_chars = executor.submit(sanitise_characters, corpus_data["characters"], consider_accents)
        clean_bigrams = executor.submit(sanitise_bigrams, corpus_data["bigrams"])
        clean_skipgrams = executor.submit(sanitise_skipgrams, corpus_data["skipgrams"])
        clean_trigrams = executor.submit(sanitise_trigrams, corpus_data["trigrams"])

        return {
            clean_chars.result(),
            clean_bigrams.result(),
            clean_skipgrams.result(),
            clean_trigrams.result()
        }


def analyse_file(path: str, has_progress_bar=False):
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


def generate_data(corpus_iterator):
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


def analyse_corpus(text_directory="text", language="english"):
    paths = glob(f"{text_directory}/{language}/*.txt")
    if len(paths) == 1:
        corpus_data = dict(reversed(sorted(analyse_file(paths[0], True).items(), key=lambda item: item[1])))
    elif len(paths) > 1:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            corpus_data = generate_data(executor.map(analyse_file, paths))
    else:
        corpus_data = {}

    with open(f"{language}_data.json", 'w') as language_data:
        json.dump(corpus_data, language_data, indent='\t', separators=(',', ': '))
