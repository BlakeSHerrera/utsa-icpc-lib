import collections, collections.abc
import enum
import itertools
from typing import Callable, Iterable


def count(iterable: Iterable) -> int:
    if isinstance(iterable, collections.abc.Sized):
        return len(iterable)
    return sum(1 for _ in iterable)

def is_empty(iterable: Iterable) -> bool:
    if isinstance(iterable, collections.abc.Sized):
        return len(iterable) == 0
    try:
        next(iter(iterable))
        return False
    except StopIteration:
        return True

def consume(iterable: Iterable):
    collections.deque(iterable, maxlen = 0)

def apply(func: Callable, *iterables: Iterable):
    consume(map(func, *iterables))

def starapply(func: Callable, iterables: Iterable[Iterable]):
    consume(itertools.starmap(func, iterables))


class ZeroBasedEnum(enum.IntEnum):

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return count
