from collections import defaultdict
import concurrent.futures
from collections import Counter
import json
from os.path import isfile
from corpus_analysis.chunk_texts import chunk_texts
from corpus_analysis.analyse_text import analyse_text

from time import perf_counter


def time_this(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"\"{func.__name__}\" took {round(end - start, ndigits=6 if end-start < 0.1 else 3)} second(s)\n")
        return result

    return wrapper


def sanitize_str2(strs: dict[bytes, int]):
    return {str2.decode('utf-8'): val for str2, val in strs.items() if (str2[0] != str2[1] and b' ' not in str2)}


def sanitize_str3(strs: dict[bytes, int]):
    return {str3.decode('utf-8'): val for str3, val in strs.items() if len(set(str3)) == 3 and b' ' not in str3}


def generate_skipgrams(trigrams: dict[bytes, int]):
    skipgrams = defaultdict(int)
    for k, v in trigrams.items():
        skipgrams[k[0] + k[2]] += v
    return skipgrams


def sanitize_data(bigrams: dict[bytes, int], trigrams: dict[bytes, int]):
    with concurrent.futures.ProcessPoolExecutor(2) as executor:
        bigrams_exec = executor.submit(sanitize_str2, bigrams)
        trigrams_exec = executor.submit(sanitize_str3, trigrams)

        bigrams = bigrams_exec.result()
        trigrams = trigrams_exec.result()
        skipgrams = generate_skipgrams(trigrams)

        return bigrams, skipgrams, trigrams


@time_this
def generate_complete_data(corpus_iterator):
    characters = Counter()
    bigrams = Counter()
    trigrams = Counter()

    for data in corpus_iterator:
        characters += Counter(data["characters"])
        bigrams += Counter(data["bigrams"])
        trigrams += Counter(data["trigrams"])

    del characters[32]
    bigrams, skipgrams, trigrams = sanitize_data(bigrams, trigrams)

    sum_characters = sum(characters.values())
    characters = {chr(k): v / sum_characters for k, v in characters.items()}

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


def analyse_file(text: str):
    characters = defaultdict(int)
    bigrams = defaultdict(int)
    skipgrams = defaultdict(int)
    trigrams = defaultdict(int)

    for i in range(len(text)-2):
        characters[text[i]] += 1
        bigrams[text[i: i+2]] += 1
        skipgrams[text[i] + text[i+2]] += 1
        trigrams[text[i: i+3]] += 1

    return {
        "characters":   dict(characters),
        "bigrams":      dict(bigrams),
        "skipgrams":    dict(skipgrams),
        "trigrams":     dict(trigrams)
    }


@time_this
def prepare_analyse_text(language, text_directory):
    texts = chunk_texts(language, text_directory)
    return [text.encode('utf-8') for text in texts], [len(text) for text in texts]


@time_this
def analyse_corpus(language="english", text_directory="text", update=False):
    if not update and isfile(f"language_data/{language.lower()}.json"):
        return

    texts, lengths = prepare_analyse_text(language, text_directory)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        corpus_iterator = executor.map(analyse_text, texts, lengths)

    corpus_data = generate_complete_data(corpus_iterator)

    with open(f"language_data/{language}.json", 'w') as language_data:
        json.dump(corpus_data, language_data, indent='\t', separators=(',', ': '))
