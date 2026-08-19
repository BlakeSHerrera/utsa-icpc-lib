from bag import *

import pytest


N = 5
R = range(N)


@pytest.fixture
def deque_queue() -> DequeQueue:
    return DequeQueue()

@pytest.fixture(params = [deque_queue], ids = ['deque'])
def queue(request: pytest.FixtureRequest) -> Queue:
    return request.getfixturevalue(request.param.__name__)

@pytest.fixture
def deque_stack() -> DequeStack:
    return DequeStack()

@pytest.fixture
def list_stack() -> ListStack:
    return ListStack()

@pytest.fixture(params = [list_stack, deque_stack], ids = ['list', 'deque'])
def stack(request: pytest.FixtureRequest) -> Stack:
    return request.getfixturevalue(request.param.__name__)

@pytest.fixture(params = [deque_queue, list_stack, deque_stack], ids = ['queue', 'list_stack', 'deque_stack'])
def bag(request: pytest.FixtureRequest) -> Bag:
    return request.getfixturevalue(request.param.__name__)


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
    bag.push_all(R)
    for i in R:
        assert len(bag) == N - i
        bag.pop()
    assert len(bag) == 0

def test_peek_pop(bag: Bag):
    bag.push_all(R)
    for i in R:
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
