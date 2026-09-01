import itertools
import random

import pytest

from bag import *
import testutils


N = 5
R = range(N)


@pytest.fixture
def deque_queue() -> DequeQueue:
    return DequeQueue()

@testutils.fixtures(deque_queue)
def queue() -> Queue:
    ...

@pytest.fixture
def deque_stack() -> DequeStack:
    return DequeStack()

@pytest.fixture
def list_stack() -> ListStack:
    return ListStack()

@testutils.fixtures(list_stack, deque_stack)
def stack() -> Stack:
    ...

@pytest.fixture
def list_heap() -> ListHeap:
    return ListHeap()

@testutils.fixtures(list_heap)
def heap() -> Heap:
    ...

@testutils.fixtures(*queue.fixtures, *stack.fixtures, *heap.fixtures)
def bag() -> Bag:
    ...

# ===== abstract base class tests =====

def test_len(bag: Bag):
    assert len(bag) == 0
    bag.push(1)
    assert len(bag) == 1

def test_bool(bag: Bag):
    assert bool(bag) == False
    bag.push(1)
    assert bool(bag) == True

def test_peek(bag: Bag):
    with pytest.raises(IndexError):
        bag.peek()
    bag.push(1)
    assert bag.peek() == 1
    assert bag.peek() == 1

def test_push(bag: Bag):
    for i in R:
        assert len(bag) == i
        bag.push(i)

def test_push_all(bag: Bag):
    bag.push_all(R)
    assert len(bag) == len(R)

def test_pop(bag: Bag):
    with pytest.raises(IndexError):
        bag.pop()
    bag.push_all(R)
    for i in R:
        assert len(bag) == N - i
        bag.pop()
    assert len(bag) == 0

def test_peek_pop(bag: Bag):
    bag.push_all(R)
    for _ in R:
        assert bag.peek() == bag.pop()

def test_iter(bag: Bag):
    bag.push_all(R)
    iter_ = iter(bag)
    for _ in R:
        value = bag.peek()
        assert value == next(iter_)
    with pytest.raises(StopIteration):
        next(iter_)


# ===== Stack / Queue =====

def test_stack(stack: Stack):
    stack.push_all(R)
    assert list(stack) == list(R)[::-1]

def test_queue(queue: Queue):
    queue.push_all(R)
    assert list(queue) == list(R)

#  ===== Heap =====

@pytest.mark.parametrize(
    argnames = ['size', 'from_constructor', 'comparator'],
    argvalues = tuple(itertools.product(
        (*range(1, 5), *range(254, 257)), 
        (True, False), 
        (operator.lt, operator.gt))))
def test_heap_sort(size: int, from_constructor: bool, comparator: Callable[[int, int], bool]):
    random.seed(42)
    nums = [random.randint(0, 100) for _ in range(size)]
    sorted_nums = sorted(nums, reverse = comparator is operator.gt)
    if from_constructor:
        heap = ListHeap(nums, comparator)
    else:
        heap = ListHeap(comparator = comparator)
        heap.push_all(nums)
    assert list(heap) == sorted_nums
