from typing import Iterable

import pytest

from utils import *


N = 3


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
