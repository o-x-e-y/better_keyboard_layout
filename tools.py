from time import perf_counter, localtime
import datetime
import os
import sys


def time_this(func):
    def time_wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"\"{func.__name__}\" took {round(end - start, ndigits=6 if end-start < 0.1 else 3)} second(s). "
              f"It was called from {func.__module__}\n")
        return result

    return time_wrapper


def round_mem(mem: int) -> str:
    if mem < 1_000:
        return f"{mem} bytes"
    elif mem < 1_000_000:
        return f"{round(mem/1_000, 1)} kilobytes"
    elif mem < 1_000_000_000:
        return f"{round(mem/1_000_000, 1)} megabytes"
    else:
        return f"{round(mem/1_000_000_000, 1)} gigabytes"


def mem_this(func):
    def mem_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        size = sys.getsizeof(result)
        print(f"\"{func.__name__}\" returned an object that uses {round_mem(size)} of memory\n")

        return result
    return mem_wrapper


def mem_time(func):
    def mem_time_wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        size = sys.getsizeof(result)
        end = perf_counter()

        print(f"\"{func.__name__}\" took {round(end-start, ndigits=6 if end-start < 0.1 else 3)} second(s)"
              f" and returned an object that uses {round_mem(size)} of memory\n")

        return result
    return mem_time_wrapper


def log_this(func: staticmethod):
    def log_wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        size = sys.getsizeof(result)
        end = perf_counter()

        print(f"\"{func.__name__}\" took {round(end - start, ndigits=6 if end-start < 0.1 else 3)} second(s)\n")
        with open(f'logs/stuff.log', 'a', encoding='utf-8') as log_file:
            cur_time = f"[{localtime().tm_hour:0>2}:{localtime().tm_min:0>2}:{localtime().tm_sec:0>2}]"
            log_file.write(f"{cur_time}: \"{func.__name__}\" in {func.__module__.split('.')[-1]} took "
                           f"{round(end-start, ndigits=6 if end-start < 0.1 else 3)} second(s)"
                           f" and returned an object that uses {round_mem(size)} of memory\n")
        return result
    return log_wrapper


_decode = {'date': 'datetime.date.today()',
           'time': 'datetime.time'}


def params_to_line(params: list[str]):
    keys = _decode.keys()
    return [eval(_decode[param]) for param in params if param in keys]


def log_these(params=""):
    def inner(func):
        def wrapper(*args, **kwargs):
            start = perf_counter()
            result = func(*args, **kwargs)
            size = sys.getsizeof(result)
            end = perf_counter()

            print(f"\"{func.__name__}\" took {round(end-start, ndigits=6 if end-start < 0.1 else 3)} second(s)\n")
            print(f"{params=}")
            return result

        return wrapper
    return inner
