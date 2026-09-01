
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


class FactoredInt(Number):

    def __init__(self, prime_factors: collections.Counter):
        self.prime_factors = prime_factors

    def __bool__(self) -> bool:
        return bool(self.prime_factors)

    def __getitem__(self, prime: int) -> int:
        return self[prime]

    def __contains__(self, prime: int) -> bool:
        return prime in self.prime_factors

    @staticmethod
    def factor(n: int) -> Self:
        factors = collections.Counter()
        for p in PRIMES:
            if p * p > n:
                break
            while n % p == 0:
                n //= p
                factors[p] += 1
        if PRIMES[-1] ** 2 < n:
            raise NotEnoughPrimes(math.isqrt(n))
        if n != 1:
            factors[n] += 1
        return FactoredInt(factors)

    @staticmethod
    def from_primes(nums: Iterable[int]) -> Self:
        return FactoredInt(collections.Counter(nums))

    def to_int(self) -> int:
        return math.prod(itertools.starmap(pow, self.prime_factors.items()))

    def __mul__(self, other: Self):
        return FactoredInt(self.prime_factors + other.prime_factors)

    def __pow__(self, other: int):
        return FactoredInt(collections.Counter({p: e * other for p, e in self.prime_factors.items()}))

    def __truediv__(self, other: Self) -> DivisionResult:
        num = FactoredInt(self.prime_factors - other.prime_factors)
        denom = FactoredInt(other.prime_factors - self.prime_factors)
        gcf = FactoredInt(self.prime_factors - num.prime_factors)
        lcm = num * denom * gcf
        return DivisionResult(num, denom, gcf, lcm)

    def __mod__(self, other: Self) -> FactoredInt:
        # Only works if divisible, otherwise KeyError
        return FactoredInt(
            collections.Counter(
                map(
                    self.__getitem__, 
                    itertools.filterfalse(other.__contains__, self.prime_factors))))

    def __eq__(self, other: Self) -> bool:
        return self.prime_factors == other.prime_factors

    def log(self, base: Real = math.e):
        return sum(e * math.log(p, base) for p, e in self.prime_factors.items())

    def log2(self):
        return sum(e * math.log2(p) for p, e in self.prime_factors.items())

    def log10(self):
        return sum(e * math.log10(p) for p, e in self.prime_factors.items())

    def __lt__(self, other: Self) -> bool:
        result = self / other
        if not result.denominator:
            return False
        if not result.numerator:
            return True
        return result.numerator.log2() < result.denominator.log2()  # log2 is hardware-optimized
        
    def greatest_common_factor(self, other: Self) -> Self:
        return (self / other).greatest_common_factor

    def least_common_multiple(self, other: Self) -> Self:
        return (self / other).least_common_multiple

    def is_coprime(self, other: Self) -> bool:
        return not self.greatest_common_factor(other)

    def radical(self) -> FactoredInt:
        return FactoredInt(collections.Counter(zip(self.prime_factors, itertools.repeat(1))))
    
    def num_divisors(self) -> FactoredInt:
        return math.prod(FactoredInt.factor(i + 1) for i in self.prime_factors.values())

    def sum_divisors(self) -> int:
        # Return a FactoredInt instead?
        return math.prod((p ** (e + 1) - 1) // (p - 1) for p, e in self.prime_factors.items())

    def euler_totient(self) -> FactoredInt:
        return (self / self.radical()).numerator \
            * math.prod(FactoredInt.factor(p - 1) for p in self.prime_factors)

    def mobius(self) -> int:
        return 0 if max(self.prime_factors.values()) > 1 \
            else 1 if len(self.prime_factors) % 2 == 0 \
            else -1 

    def all_divisors(self, ordering: Ordering) -> Iterable[Self]:
        primes = list(self.prime_factors)
        match ordering:
            case Ordering.UNORDERED:
                bag = baglib.Stack()
                base = FactoredInt.from_primes(())
            case Ordering.ASCENDING:
                bag = baglib.Heap(comparator = operator.lt)
                base = FactoredInt.from_primes(())
            case Ordering.DESCENDING:
                bag = baglib.Heap(comparator = operator.gt)
                base = self
        bag.push((base, 0))

        while bag:
            base, prime_index = bag.pop()
            yield base
            for i in range(prime_index, len(primes)):
                p = primes[i]
                if base[p] == (0 if ordering is Ordering.DESCENDING else self[p]):
                    continue
                new = FactoredInt(collections.Counter({p: -1 if ordering is Ordering.DESCENDING else 1}))
                bag.push((base * new, i))

    def divisor_pairs(self) -> Iterable[tuple[FactoredInt, FactoredInt]]:
        # Note edge case for squares
        return ((d, (self / d).numerator) for d in self.all_divisors(Ordering.UNORDERED) if d * d <= self)


@dataclasses.dataclass
class DivisionResult:
    numerator: FactoredInt
    denominator: FactoredInt
    greatest_common_factor: FactoredInt
    least_common_multiple: FactoredInt
