from bag import Stack

import pytest


def test_stack():
    stack = Stack()
    stack.push(1)
    stack.push(2)
    assert stack.pop() == 2
    assert stack.pop() == 1


if __name__ == '__main__':
    test_stack()
