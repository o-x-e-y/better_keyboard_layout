from collections import defaultdict
import concurrent.futures
from collections import Counter
import json
from os.path import isfile
from corpus_analysis.chunk_texts import TextChunker
from corpus_analysis.analyse_text import analyse_text
from tools import *


language_can_use_cython = {"dutch":         True,
                           "english":       True,
                           "dutch_english": True,
                           "iweb_corpus":   True,
                           "spanish":       False,
                           "russian":       False,
                           "portuguese":    False}


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


def sanitize_str2_special(strs: dict[bytes, int]):
    return {str2: val for str2, val in strs.items() if (str2[0] != str2[1] and ' ' not in str2)}


def sanitize_str3_special(strs: dict[bytes, int]):
    return {str3: val for str3, val in strs.items() if len(set(str3)) == 3 and ' ' not in str3}


def sanitize_data_special(bigrams: dict[bytes, int], trigrams: dict[bytes, int]):
    with concurrent.futures.ProcessPoolExecutor(2) as executor:
        bigrams_exec = executor.submit(sanitize_str2_special, bigrams)
        trigrams_exec = executor.submit(sanitize_str3_special, trigrams)

        bigrams = bigrams_exec.result()
        trigrams = trigrams_exec.result()
        skipgrams = generate_skipgrams(trigrams)

    return bigrams, skipgrams, trigrams


def generate_complete_data(corpus_iterator, no_special_chars):
    characters = Counter()
    bigrams = Counter()
    trigrams = Counter()

    for data in corpus_iterator:
        characters += Counter(data["characters"])
        bigrams += Counter(data["bigrams"])
        trigrams += Counter(data["trigrams"])

    if no_special_chars:
        del characters[32]
        bigrams, skipgrams, trigrams = sanitize_data(bigrams, trigrams)

        sum_characters = sum(characters.values())
        characters = {chr(k): v / sum_characters for k, v in characters.items()}
    else:
        del characters[' ']
        bigrams, skipgrams, trigrams = sanitize_data_special(bigrams, trigrams)

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


def prepare_analyse_text(chunked_texts):
    return [text.encode('utf-8') for text in chunked_texts], [len(text) for text in chunked_texts]


def generate_ngrams(n: int, text: str):
    for i in range(n, len(text)):
        yield text[i-n:i]


def count_ngrams(n: int, text: str) -> Counter:
    """Returns a frequency counter of n-grams in the given text."""
    return Counter(generate_ngrams(n, text))


def analyse_text_python(text: str):
    trigrams = dict(count_ngrams(3, text))
    return {
        "characters":   dict(count_ngrams(1, text)),
        "bigrams":      dict(count_ngrams(2, text)),
        "trigrams":     trigrams
    }


@time_this
def analyse_corpus(language="english", text_directory="text", update=False):
    if not update and isfile(f"language_data/{language.lower()}.json"):
        return

    with TextChunker(language, text_directory) as chunker:
        chunked_texts = chunker.chunked_texts

    use_cython = language_can_use_cython[language]
    if use_cython:
        texts, lengths = prepare_analyse_text(chunked_texts)

        with concurrent.futures.ProcessPoolExecutor() as executor:
            corpus_iterator = executor.map(analyse_text, texts, lengths)
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            corpus_iterator = executor.map(analyse_text_python, chunked_texts)

    corpus_data = generate_complete_data(corpus_iterator, use_cython)

    with open(f"language_data/{language}.json", 'w') as language_data:
        json.dump(corpus_data, language_data, indent='\t', separators=(',', ': '))


def get_unique_data(data: dict) -> dict:
    unique_data = defaultdict(float)
    for key, val in data.items():
        unique_data[''.join(sorted(key))] += val
    return dict(unique_data)


@time_this
def make_unique_corpus_copy(language="english"):
    with open(f"language_data/{language}.json", 'r') as language_data:
        complete_data = json.load(language_data)

    unique_bigrams = get_unique_data(complete_data["bigrams"])
    unique_skipgrams = get_unique_data(complete_data["skipgrams"])
    unique_trigrams = get_unique_data(complete_data["trigrams"])

    unique_data = {
        "characters": complete_data["characters"],
        "bigrams": dict(sorted(unique_bigrams.items(), key=lambda item: item[1], reverse=True)),
        "skipgrams": dict(sorted(unique_skipgrams.items(), key=lambda item: item[1], reverse=True)),
        "trigrams": complete_data["trigrams"]
    }

    with open(f"language_data/unique/{language}.json", 'w') as unique_language_data:
        json.dump(unique_data, unique_language_data, indent='\t', separators=(',', ': '))
