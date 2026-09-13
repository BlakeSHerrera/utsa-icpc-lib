
import collections
import copy
import functools
from typing import Any, Callable
import pytest

import testutils

from prime import *


KNOWN_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
MEDIUM_PRIME = 10_007
BIG_PRIME = 1_000_000_007


@pytest.fixture(autouse = True)
def setup():
    generate_primes(102)


def test_not_enough_primes():
    e = NotEnoughPrimes(12)
    assert e.n == 12

def _test_not_enough_primes(func: Callable[[int], Any]):
    with pytest.raises(NotEnoughPrimes):
        try:
            func(BIG_PRIME)
        except NotEnoughPrimes as e:
            assert e.n == math.isqrt(BIG_PRIME)
            raise

def test_primes():
    assert PRIMES == KNOWN_PRIMES

@pytest.mark.parametrize('n', range(10))
def test_sieve(n):
    assert sieve(n) == list(filter(n.__gt__, KNOWN_PRIMES))

@pytest.mark.parametrize(
    ['n', 'expected'],
    ((i, i in KNOWN_PRIMES) for i in range(10)))
def test_is_prime(n, expected):
    generate_primes(6)
    assert is_prime(n) == expected

def test_is_prime_too_big():
    _test_not_enough_primes(is_prime)

@pytest.mark.parametrize(
    ['n', 'expected'],
    ((i, i > 1 and i not in KNOWN_PRIMES) for i in range(10))
)
def test_is_composite(n, expected):
    generate_primes(6)
    assert is_composite(n) == expected

def test_is_composite_too_big():
    _test_not_enough_primes(is_composite)

@pytest.mark.parametrize('n', range(10))
def test_generate_primes(n):
    generate_primes(n)
    assert PRIMES == list(filter(n.__gt__, KNOWN_PRIMES))


THREE_SIXTY = FactoredInt.from_primes([2, 2, 2, 3, 3, 5])

def test_factored_int_construction():
    counts = collections.Counter([2, 2, 2, 3, 3, 5])
    f = FactoredInt(counts)
    assert f.prime_factors == counts

def test_factored_int_from_primes():
    data = [2, 2, 3, 2, 5, 3]
    f = FactoredInt.from_primes(data)
    assert f.prime_factors == collections.Counter(data)

def test_factored_int_bool():
    assert not FactoredInt.from_primes(())
    assert FactoredInt.from_primes([2])
    assert THREE_SIXTY

def test_factored_int_getitem():
    for i, j in zip(KNOWN_PRIMES, range(3, -1, -1)):
        assert THREE_SIXTY[i] == j

def test_factored_int_contains():
    for i, j in zip(KNOWN_PRIMES, (True,) * 3 + (False,)):
        assert (i in THREE_SIXTY) == j

@pytest.mark.parametrize('counts', [
    {}, {2: 1}, {3: 1}, {2: 2}, {2: 1, 3: 1}, {2: 3},
    {2: 1, 3: 1, 5: 1}, {2: 2, 3: 3, 5: 4}, {2: 64},
    {MEDIUM_PRIME: 1}
])
def test_factor(counts: dict):
    n = math.prod(p ** e for p, e in counts.items())
    assert FactoredInt.factor(n).prime_factors == counts

def test_factor_not_enough_primes():
    _test_not_enough_primes(FactoredInt.factor)

def test_to_int():
    assert THREE_SIXTY.to_int() == 360
    assert FactoredInt(collections.Counter()).to_int() == 1

@pytest.mark.parametrize(
    ['a', 'b'],
    [
        (1, 1), (1, 2), (2, 1), (2 * 3, 2 * 5),
        (2 ** 3 * 3 ** 4, 3 ** 5 * 5 ** 6)
    ])
def test_mul(a: int, b: int):
    c = a * b
    fa, fb, fc = map(FactoredInt.factor, (a, b, c))
    assert fa * fb == fc

@pytest.mark.parametrize(
    ['a', 'b'],
    [(1, 1), (1, 2), (2, 1), (2 * 3, 2 * 5), (2 * 3, 3 * 5), (360, 0)])
def test_pow(a: int, b: int):
    fa, fb, fc = map(FactoredInt.factor, (a, b, a ** b))
    assert fa ** fb == fc

@pytest.mark.parametrize(
    ['a', 'b'],
    [(6, 15), (15, 6), (4, 9), (9, 4), (2, 4), (4, 2), (360, 1),  (1, 360)])
def test_divisions(a: int, b: int):
    gcf = math.gcd(a, b)
    fa, fb, fnum, fdenom, fgcf, flcm = map(
        FactoredInt.factor, 
        (a, b, a // gcf, b // gcf, gcf, math.lcm(a, b)))
    d = fa / fb
    assert d.numerator == fnum
    assert d.denominator == fdenom
    assert d.greatest_common_factor == fgcf
    assert d.least_common_multiple == flcm
    assert fa.greatest_common_factor(fb) == fgcf
    assert fa.least_common_multiple(fb) == flcm
    assert fa.is_coprime(fb) == (gcf == 1)

@pytest.mark.parametrize(
    'primes', 
    [(2, 2, 2, 3, 3, 5), ()])
def test_eq(primes: Iterable[int]):
    a = FactoredInt.from_primes(primes)
    b = FactoredInt(collections.Counter(primes))
    assert a == b

@pytest.mark.parametrize(
    ['n', 'base'],
    [(360, 5), (360, 2), (360, 10)])
def test_log(n: int, base: int):
    fn = FactoredInt.factor(n)
    assert math.isclose(fn.log(), math.log(n))
    assert math.isclose(fn.log(base), math.log(n, base))

@pytest.mark.parametrize('n', [360])
def test_log2(n: int):
    fn = FactoredInt.factor(n)
    assert math.isclose(fn.log2(), math.log2(n))

@pytest.mark.parametrize('n', [360])
def test_log10(n: int):
    fn = FactoredInt.factor(n)
    assert math.isclose(fn.log10(), math.log10(n))

@pytest.mark.parametrize(
    ['a', 'b'],
    [
        (360, 361), (361, 360), (360, 359), (359, 360),
        (math.prod(KNOWN_PRIMES) ** 2, math.prod(KNOWN_PRIMES[:-1]) ** 2),
        (math.prod(KNOWN_PRIMES[:-1]) ** 2, math.prod(KNOWN_PRIMES) ** 2),
    ])
def test_lt(a: int, b: int):
    fa, fb = map(FactoredInt.factor, (a, b))
    assert fa < fb == a < b

@pytest.mark.parametrize('nums', [(2, 3, 3, 5, 5, 5)])
def test_radical(nums: Iterable[int]):
    fn = FactoredInt.from_primes(nums)
    assert fn.radical() == FactoredInt.from_primes(set(nums))


def _divisors(n: int):
    return [n for i in range(1, n + 1) if n % i == 0]

@pytest.mark.parametrize('n', [1, 360, 359, 361, 4])
def test_divisor_count(n: int):
    fn = FactoredInt.factor(n)
    assert fn.divisor_count().to_int() == len(_divisors(n))

@pytest.mark.parametrize('n', [1, 360, 359, 361, 4])
def test_divisor_sum(n: int):
    fn = FactoredInt.factor(n)
    assert fn.divisor_sum() == sum(_divisors(n))

@pytest.mark.parametrize('n', [1, 360, 359, 361, 4])
def test_all_divisors(n: int):
    fn = FactoredInt.factor(n)
    divisors = _divisors(n)
    assert list(fn.all_divisors(Ordering.ASCENDING)) == divisors
    assert list(fn.all_divisors(Ordering.DESCENDING)) == divisors[::-1]
    assert set(fn.all_divisors(Ordering.UNORDERED)) == set(divisors)

@pytest.mark.parametrize('n', [1, 360, 359, 361, 4])
def test_divisor_pairs(n: int):
    fn = FactoredInt.factor(n)
    pairs = {(d, n // d) for d in _divisors(n) if d <= n // d}
    assert set(fn.divisor_pairs()) == pairs


@pytest.mark.parametrize(
    ['n', 'totient'],
    [
        (1, 1), (2, 1), (5, 2), (11, 10),  # base / primes
        (8, 4), (27, 18),  # Prime powers
        (10, 4), (12, 4), (36, 12),  # Composites
    ])
def test_euler_totient(n: int, totient: int):
    fn = FactoredInt.factor(n)
    assert fn.euler_totient().to_int() == totient

@pytest.mark.parametrize(
    ['n', 'mobius'],
    [
        (1, 1),  # Base 
        *zip([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 97], itertools.repeat(-1)),  # primes
        *zip([6, 10, 14, 15, 21, 22, 26, 33, 35, 210], itertools.repeat(1)),  # square-free even distinct primes
        *zip([30, 42, 70, 105, 114], itertools.repeat(-1)),  # square-free odd distinct primes
        *zip([4, 9, 16, 25, 36, 49], itertools.repeat(0)),  # squares
        *zip([12, 18, 20, 24, 28, 40, 50, 100], itertools.repeat(0)),  # square multiples
    ])
def test_mobius(n: int, mobius: int):
    fn = FactoredInt.factor(n)
    assert fn.mobius() == mobius
    