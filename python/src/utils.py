import collections, collections.abc
import itertools
from typing import Callable, Iterable


def count(iterable: Iterable) -> int:
    if isinstance(iterable, collections.abc.Sized):
        return len(iterable)
    return sum(1 for _ in iterable)

def consume(iterable: Iterable):
    collections.deque(iterable, maxlen = 0)

def apply(func: Callable, *iterables: Iterable):
    consume(map(func, *iterables))

def starapply(func: Callable, iterables: Iterable[Iterable]):
    consume(itertools.starmap(func, iterables))
