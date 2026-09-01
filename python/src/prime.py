
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

