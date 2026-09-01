
from __future__ import annotations
import bisect
import collections
import dataclasses
import enum
import heapq
import itertools
import math
from numbers import Number, Real
import operator
from typing import Iterable, Self, Sequence

import bag as baglib
import utils


class NotEnoughPrimes(Exception):

    def __init__(self, n: int):
        super().__init__(f'Need primes up to {n}')


PRIMES: list[int] = [2]


def is_prime(n: int):
    if n <= PRIMES[-1]:
        return PRIMES[bisect.bisect(PRIMES, n)] == n
    sqrt = math.isqrt(n)
    for p in PRIMES:
        if p > sqrt:
            return True
        if n % p == 0:
            return False
    raise NotEnoughPrimes(sqrt)

def is_composite(n: int):
    return not is_prime(n) if n >= 2 else False


def sieve(n: int) -> list[int]:
    primes = [2]
    data = [True] * (n // 2)  # Each index corresponds to n = 2 * i + 1
    end = math.isqrt(n) + 1
    for i in range(1, end):
        primes.append(2 * i + 1)
        start, stop, skip = i * 3, len(data), 2 * i
        data[start:stop:skip] = itertools.repeat(False, len(range(start, stop, skip)))
    for i in range(end, len(data)):
        if primes[i]:
            primes.append(2 * i + 1)
    return primes

def generate_primes(n: int):
    global PRIMES
    PRIMES = sieve(n)


class Ordering(enum.Enum):
    UNORDERED = enum.auto()
    ASCENDING = enum.auto()
    DESCENDING = enum.auto()
