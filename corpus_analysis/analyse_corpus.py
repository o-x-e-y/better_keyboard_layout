from collections import defaultdict
import concurrent.futures
from collections import Counter
import json
from os.path import isfile
from corpus_analysis.chunk_texts import chunk_texts
from corpus_analysis.analyse_text import analyse_text
from tools import *


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
    characters_list = [str] * len(text)
    bigrams_list =    [str] * len(text)
    skipgrams_list =  [str] * len(text)
    trigrams_list =   [str] * len(text)

    for i in range(len(text)-2):
        characters_list[i] = text[i]
        bigrams_list[i] =    text[i: i+2]
        skipgrams_list[i] =  text[i] + text[i+2]
        trigrams_list[i] =   text[i: i+3]

    return {
        "characters": dict(Counter(characters_list)),
        "bigrams":    dict(Counter(bigrams_list)),
        "skipgrams":  dict(Counter(skipgrams_list)),
        "trigrams":   dict(Counter(trigrams_list))
    }


def prepare_analyse_text(chunked_texts):
    return [text.encode('utf-8') for text in chunked_texts], [len(text) for text in chunked_texts]


@log_this
def analyse_corpus(language="english", text_directory="text", script='latin', update=False):
    if not update and isfile(f"language_data/{language.lower()}.json"):
        return

    chunked_texts = chunk_texts(language, text_directory)
    texts, lengths = prepare_analyse_text(chunked_texts)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        corpus_iterator = executor.map(analyse_text, texts, lengths)

    corpus_data = generate_complete_data(corpus_iterator)

    with open(f"language_data/{language}.json", 'w') as language_data:
        json.dump(corpus_data, language_data, indent='\t', separators=(',', ': '))
