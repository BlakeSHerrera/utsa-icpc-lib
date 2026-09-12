import collections, collections.abc
import enum
import itertools
from typing import Callable, Iterable


def count(iterable: Iterable) -> int:
    '''
    Count the number of items in an iterable. If the iterable 
    defines a __len__ function, count uses the len() function instead.
    If the iterable is an iterator, it will be exhausted.
    '''
    if isinstance(iterable, collections.abc.Sized):
        return len(iterable)
    return sum(1 for _ in iterable)

def is_empty(iterable: Iterable) -> bool:
    '''
    Returns whether or not iterable is empty.
    If the iterable does not define a __len__ method and is a 
    non-empty an iterator, it will be advanced by one step.'''
    if isinstance(iterable, collections.abc.Sized):
        return len(iterable) == 0
    try:
        next(iter(iterable))
        return False
    except StopIteration:
        return True

def consume(iterable: Iterable):
    '''Exhaust an iterator.'''
    collections.deque(iterable, maxlen = 0)

def apply(func: Callable, *iterables: Iterable):
    '''
    Call the function using arguments from each of the iterables.
    Stops when the shortest iterable is exhausted.
    '''
    consume(map(func, *iterables))

def starapply(func: Callable, iterables: Iterable[Iterable]):
    '''
    Call the function evaluated with an argument tuple taken from
    the given sequence of iterables.
    '''
    consume(itertools.starmap(func, iterables))


class ZeroBasedEnum(enum.IntEnum):
    '''Equivalent to enum.IntEnum, but starting at zero.'''

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return count
