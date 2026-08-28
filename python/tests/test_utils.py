from typing import Iterable

import pytest

from utils import *


N = 3
BIG_N = int(1e15)


@pytest.fixture
def generator() -> Iterable[int]:
    return iter(range(N))


def test_count_sized():

    class Sized:
        def __len__(self):
            return N
        
    sized = Sized()
    assert count(sized) == N

def test_count_unsized(generator: Iterable[int]):
    assert count(generator) == N

def test_consume(generator: Iterable[int]):
    consume(generator)
    with pytest.raises(StopIteration):
        next(generator)

def test_apply(generator: Iterable[int]):
    lis = list()
    def mutator(a, b):
        lis.append((a, b))
    apply(mutator, generator, [-1, -2])
    assert lis == [(0, -1), (1, -2)]

def test_starapply(generator: Iterable[int]):
    lis = list()
    def mutator(a, b):
        lis.append((a, b))
    starapply(mutator, zip(generator, [-1, -2]))
    assert lis == [(0, -1), (1, -2)]

def test_is_empty_sized():
    assert not is_empty(range(BIG_N))
    assert is_empty([])

def test_is_empty_unsized():
    assert not is_empty(iter(range(BIG_N)))
    assert is_empty(iter([]))

def test_zero_based_enum():

    class MyEnum(ZeroBasedEnum):
        ZERO = enum.auto()
        ONE = enum.auto()

    assert MyEnum.ZERO == 0
    assert MyEnum.ONE == 1