from analyse_corpus import analyse_corpus
from time import perf_counter


if __name__ == "__main__":
    # start = perf_counter()
    analyse_corpus(text_directory="text", language="english")
    # end = perf_counter()
    # print(f"That took {round(end - start, 3)} second(s)")
