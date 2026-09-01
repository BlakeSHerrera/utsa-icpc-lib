

import operator
from typing import Any, Generic, Hashable, Iterable, Self, TypeVar

import utils


T = TypeVar('T')


class UfdsNode(Generic[T]):

    def __init__(self, data: T):
        self.data = data
        self.parent = self
        self.rank = 0

class UFDS(Generic[T]):

    def __init__(self, values: Iterable[T] = ()):
        self._data = dict()
        utils.apply(self.add, values)

    def add(self, value: T):
        self._data[value] = UfdsNode(value)

    def find(self, value: T) -> UfdsNode[T]:
        node = self._data[value]
        while node.parent is not node:
            node.parent = node.parent.parent
            node = node.parent
        return node

    def union(self, i: T, j: T) -> UfdsNode:
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i is root_j:
            return
        parent, child = sorted([root_i, root_j], key = operator.attrgetter('rank'))
        child.parent = parent
        parent.rank += 1
        return child
