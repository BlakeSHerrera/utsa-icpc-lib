'''
A prime is an integer greater than 1 that cannot be divided evenly
by any integer other than 1 and itself.

This module is designed for working with primes and integers
that have been factorized.
'''

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
    '''
    This exception is raised when there are not enough primes to
    factor an integer or determine if it has been factored properly.
    '''

    def __init__(self, n: int):
        self.n = n
        super().__init__(f'Need primes up to {n}')


PRIMES: list[int] = [2]


def is_prime(n: int):
    '''
    This function performs a primality test by dividing n
    by primes up to the value of sqrt(n) and testing the remainder.
    
    However, if n is less than the value of the largest generated prime,
    it performs a binary search on the list of sorted primes instead.
    
    Note that values less than 2 are neither prime nor composite.
    '''
    if n <= PRIMES[-1]:
        return PRIMES[bisect.bisect_left(PRIMES, n)] == n
    sqrt = math.isqrt(n)
    for p in PRIMES:
        if p > sqrt:
            return True
        if n % p == 0:
            return False
    raise NotEnoughPrimes(sqrt)

def is_composite(n: int):
    '''
    The inverse of is_prime, except that integers below 2 are
    neither prime nor composite.
    '''
    return n >= 2 and not is_prime(n)


def sieve(n: int) -> list[int]:
    '''
    Perform the Sieve of Eratosthenes and return the list of sorted
    primes up to n (exclusive).
    '''
    if n <= 2:
        return []
    primes = [2]
    # Using odd indices reduces memory and runtime by half.
    index = lambda m: (m - 3) // 2
    nums = [True] * (index(n) + 1)
    is_prime = lambda m: nums[index(m)]
    
    for p in filter(is_prime, range(3, end := math.isqrt(n) + 1, 2)):
        primes.append(p)
        start, stop, skip = index(p ** 2), len(nums), p
        nums[start:stop:skip] = itertools.repeat(False, len(range(start, stop, skip)))
    primes.extend(filter(is_prime, range(end | 1, n, 2)))
    return primes

def generate_primes(n: int):
    '''Generate primes and set the global PRIMES list.'''
    global PRIMES
    PRIMES[:] = sieve(n)


class Ordering(enum.Enum):
    '''Ordering enum for ascending, descending, and unordered.'''
    UNORDERED = enum.auto()
    ASCENDING = enum.auto()
    DESCENDING = enum.auto()


class FactoredInt(Number):
    '''
    This class represents a positive integer that has been factored via a
    dict of prime factors and exponents, implemented with a
    collections.Counter object. The counter object is used since indices
    not in the object have an implicit value of 0, and modifying the count
    to be 0 also removes it from the key index.
    
    Having no prime factors represents the number 1. Zero and negative numbers
    cannot be expressed.

    This class is much more efficient for handling operations with extremely large
    integers by utilizing basic arithmetic and prime theory.
    '''

    def __init__(self, prime_factors: collections.Counter[int]):
        self.prime_factors = prime_factors

    def __bool__(self) -> bool:
        '''A factored integer is false-y if it is equal to 1.'''
        return bool(self.prime_factors)

    def __getitem__(self, prime: int) -> int:
        '''
        Get the exponent of the given prime in this number.
        The given integer is not checked for primality.
        '''
        return self.prime_factors[prime]

    def __contains__(self, prime: int) -> bool:
        '''
        Check if the given prime is in the list of prime factors.
        The given integer is not checked for primality.
        '''
        return prime in self.prime_factors

    @staticmethod
    def factor(n: int) -> FactoredInt:
        '''
        Factor an integer and return a FactoredInt object.
        If n is less than 1, raise a ValueError.
        '''
        if n < 1:
            raise ValueError('Cannot factor integers less than 1.')
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
    def from_primes(primes: Iterable[int]) -> FactoredInt:
        '''
        Return a FactoredInt by counting an iterable of prime integers.
        The primes are not validated for primality.
        '''
        return FactoredInt(collections.Counter(primes))

    def to_int(self) -> int:
        '''Convert the factored integer to a built-in int.'''
        return math.prod(itertools.starmap(pow, self.prime_factors.items()))

    def __mul__(self, other: Self) -> Self:
        '''Multiply two factored integers together and return a new one.'''
        return FactoredInt(self.prime_factors + other.prime_factors)

    def __pow__(self, other: int) -> Self:
        '''Raise a factored integer to a scalar power.'''
        return FactoredInt(collections.Counter({p: e * other for p, e in self.prime_factors.items()}))

    def __truediv__(self, other: Self) -> DivisionResult:
        '''
        Divide two factored integers (a / b) and return a new division 
        result, which contains the reduced numerator and denominator, as 
        well as the greatest common factor and least common multiple.
        '''
        num = FactoredInt(self.prime_factors - other.prime_factors)
        denom = FactoredInt(other.prime_factors - self.prime_factors)
        gcf = FactoredInt(self.prime_factors - num.prime_factors)
        lcm = num * denom * gcf
        return DivisionResult(num, denom, gcf, lcm)

    def __eq__(self, other: Self) -> bool:
        '''Compare two factored ints. They are equivalent if their prime factors are.'''
        return self.prime_factors == other.prime_factors

    def log(self, base: Real = math.e) -> float:
        '''
        Find the logarithm of the factored int and given base.

        Note that log2 and log10 have hardware-level optimizations which can
        only be utilized with the corresponding functions. Passing a base of
        2 or 10 to this function will not use those optimizations.
        '''
        return sum(e * math.log(p, base) for p, e in self.prime_factors.items())

    def log2(self):
        '''
        Find the base 2 logarithm of the factored int.

        This function utilizes hardware-level optimizations and is more
        efficient than passing a base of 2 to the standard log function.
        '''
        return sum(e * math.log2(p) for p, e in self.prime_factors.items())

    def log10(self):
        '''
        Find the base 10 logarithm of the factored int.
        
        This function utilizes hardware-level optimizations and is more
        efficient than passing a base of 10 to the standard log function.
        '''
        return sum(e * math.log10(p) for p, e in self.prime_factors.items())

    def __lt__(self, other: Self) -> bool:
        '''
        Compare the two factored ints by first removing the greatest common factors.
        If primes remain, compare via taking the log2 of each.
        '''
        result = self / other
        if not result.denominator:
            return False
        if not result.numerator:
            return True
        return result.numerator.log2() < result.denominator.log2()  # log2 is hardware-optimized
        
    def greatest_common_factor(self, other: Self) -> Self:
        '''
        Find the greatest common factor (GCF) of the two factored integers,
        returning a new factored integer.
        '''
        return (self / other).greatest_common_factor

    def least_common_multiple(self, other: Self) -> Self:
        '''
        Find the least common multiple (LCM) of the two factored integers,
        returning a new factored integer.
        '''
        return (self / other).least_common_multiple

    def is_coprime(self, other: Self) -> bool:
        '''
        Check if two factored integers are coprime. That is, they share no 
        prime factors. 1 is considered coprime with every other integer.
        '''
        return not self.greatest_common_factor(other)

    def radical(self) -> Self:
        '''
        Find the radical (or rad) of a factored integer and return a new factored integer.
        The radical is the product of all distinct prime integers that divide n.
        '''
        return FactoredInt(collections.Counter(self.prime_factors.keys()))
    
    def divisor_count(self) -> Self:
        '''
        Find the count of divisors that the factored integer has, returning the
        result as a new factored integer.
        '''
        return FactoredInt.prod(e + 1 for e in self.prime_factors.values())

    def divisor_sum(self) -> Self:
        '''Find the sum of the factored integer's divisors as a factored integer.'''
        numerator = FactoredInt.prod(p ** (e + 1) - 1 for p, e in self.prime_factors.items())
        denominator = FactoredInt.prod(p - 1 for p in self.prime_factors.keys())
        return (numerator / denominator).numerator

    def euler_totient(self) -> Self:
        '''
        The euler totient counts the number of integers that are relatively
        prime (or coprime) up to n. It it written using the Greek letter phi.
        '''
        return (self / self.radical()).numerator \
            * FactoredInt.prod(p - 1 for p in self.prime_factors.keys())

    def mobius(self) -> int:
        '''
        The mobius function is written using the Greek letter mu. The value is defined as:
        - 1 if n = 1.
        - (-1) ** k if n is a square-free number made up of k different prime factors.
            - (Meaning if it has no repeated prime factors like 2 ** 2.)
        - 0 if n is a squared prime factor.
            - (Meaning it can be divided evenly by a square number like 4, 9, or 25.)
        '''
        return 0 if self and max(self.prime_factors.values()) > 1 \
            else 1 if len(self.prime_factors) % 2 == 0 \
            else -1

    def all_divisors(self, ordering: Ordering) -> Iterable[Self]:
        '''Iterate through all divisors (as factored integers) according to an ordering.'''
        primes = list(self.prime_factors)
        match ordering:
            case Ordering.UNORDERED:
                bag = baglib.Stack()
                base = FactoredInt.from_primes(())
            case Ordering.ASCENDING:
                bag = baglib.ListHeap(comparator = operator.lt)
                base = FactoredInt.from_primes(())
            case Ordering.DESCENDING:
                bag = baglib.ListHeap(comparator = operator.gt)
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

    def divisor_pairs(self) -> Iterable[tuple[Self, Self]]:
        '''
        Iterate through all pairs of divisors that multiply to n.
        The first number will be lesser than or equal to the second.
        This function is not ordered.
        
        Note that the size of this iterable multiplied by 2 is not equivalent to
        the number of divisors since square numbers will repeat the same divisor.
        '''
        # Note edge case for squares
        return ((d, (self / d).numerator) for d in self.all_divisors(Ordering.UNORDERED) if d * d <= self)

    @staticmethod
    def prod(ints: Iterable[int]) -> FactoredInt:
        return math.prod(
            map(FactoredInt.factor, ints), 
            start = FactoredInt.from_primes(()))


@dataclasses.dataclass
class DivisionResult:
    '''A dataclass for a division result between two factored integers.'''

    numerator: FactoredInt
    denominator: FactoredInt
    greatest_common_factor: FactoredInt
    least_common_multiple: FactoredInt
