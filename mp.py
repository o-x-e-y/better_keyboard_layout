import multiprocessing as mp
import concurrent.futures
from collections import defaultdict
import os
from random import randint


texts = [''.join([chr(randint(33, 126)) for _ in range(1000000)]),
         ''.join([chr(randint(33, 126)) for _ in range(1000000)]),
         ''.join([chr(randint(33, 126)) for _ in range(1000000)])]


def get_user_object(text, characters: dict):
    for c in text:
        characters.setdefault(c, 0)
        characters[c] += 1


def main():
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     executor.map(get_user_object, texts)
    # manager = mp.Manager()
    # characters = manager.dict()
    #
    # processes = []
    # for text in texts:
    #     p = mp.Process(target=get_user_object, args=(text, characters))
    #     p.start()
    #     processes.append(p)
    #
    # for process in processes:
    #     process.join()

    # print(characters)

    arr = [[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9]]
    print(arr)
    print(np.cumsum(arr, axis=1))


if __name__ == '__main__':
    import numpy as np
    import cProfile
    from pstats import Stats, SortKey
    with cProfile.Profile() as pr:
        main()
        a = 0
        for i in range(10000000):
            a += 10 + i

    stats = Stats(pr)
    stats.strip_dirs()
    stats.sort_stats('cumtime')
    stats.print_stats()
