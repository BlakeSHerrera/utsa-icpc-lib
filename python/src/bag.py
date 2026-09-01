import abc
import collections
import operator
from typing import Callable, Iterable, TypeVar, Generic

import view


T = TypeVar('T')


class BagView(abc.ABC, Generic[T]):
    '''A BagView is the immutable data type of the mutable Bag (see below).'''

    def __len__(self) -> int:
        '''Check the size of the bag via len(my_bag).'''
        ...
    
    def __bool__(self) -> bool:
        '''A bag is False-y if it is empty.'''
        return bool(len(self))

    def peek(self) -> T:
        '''Equivalent to pop() without removing the item.'''
        ...

    
class Bag(BagView[T], abc.ABC):
    '''
    A Bag is a data structure in which an item can be inserted
    (pushed) and then an item can be taken out (popped) according
    to some set of logical rules.

    This protocol also includes being able to check the number of elements
    in the Bag, as well as peeking at the next element without removing it.
    The bag can be interpreted as a boolean; it is False when empty.
    It can also be iterated through, which will pop all elements.
    '''

    def push(self, item: T):
        '''Insert an item into the Bag.'''
        ...

    def push_all(self, items: Iterable[T]):
        '''Insert many items into the Bag one by one.'''
        for i in items:
            self.push(i)

    def pop(self) -> T:
        '''Remove an item from the bag.'''
        ...

    def __iter__(self) -> Iterable[T]:
        '''Iterating through the bag empties it.'''
        while self:
            yield self.pop()


class DequeBag(view.DequeView, Bag[T], abc.ABC):

    def __init__(self, items: Iterable[T] = ()):
        super().__init__(collections.deque())
        self.push_all(items)

    __iter__ = Bag.__iter__
    
    def push(self, item: T):
        self._data.append(item)


class ListBag(view.ListView, Bag[T], abc.ABC):

    def __init__(self, items: Iterable[T] = ()):
        super().__init__(list())
        self.push_all(items)

    __iter__ = Bag.__iter__

    def push(self, item: T):
        self._data.append(item)


class Stack(Bag[T], abc.ABC):
    pass


class DequeStack(DequeBag[T], Stack[T]):

    def pop(self) -> T:
        return self._data.pop()

    def peek(self) -> T:
        return self[-1]


class ListStack(ListBag[T], Stack[T]):

    def pop(self) -> T:
        return self._data.pop()

    def peek(self) -> T:
        return self[-1]

    
class Queue(Bag[T], abc.ABC):
    pass


class DequeQueue(DequeBag[T], Queue[T]):

    def pop(self) -> T:
        return self._data.popleft()

    def peek(self) -> T:
        return self[0]



class Heap(Bag[T], abc.ABC):
    pass


class ListHeap(view.ListView, Heap[T]):

    def __init__(self, items: Iterable[T] = (), comparator: Callable[[T, T], bool] = operator.lt):
        super().__init__(list(items))
        self.compare = comparator
        self._heapify()

    def __iter__(self):
        return Heap.__iter__(self)

    def push(self, item: T):
        self._data.append(item)
        self._sift_up(len(self) - 1)

    def peek(self) -> T:
        return self[0]

    def pop(self) -> T:
        self._swap(0, -1)
        r = self._data.pop()
        self._sift_down(0)
        return r

    def _swap(self, i: int, j: int):
        temp = self._data[i]
        self._data[i] = self._data[j]
        self._data[j] = temp

    @staticmethod
    def parent_i(index: int) -> int:
        return (index - 1) // 2

    @staticmethod
    def child_i(index: int) -> Iterable[T]:
        return (index * 2 + 1, index * 2 + 2)

    def _heapify(self):
        for i in range(len(self) // 2, -1, -1):
            self._sift_down(i)

    def _sift_down(self, index: int):
        while index < len(self) // 2:
            best = index
            for j in self.child_i(index):
                if j < len(self) and self.compare(self[j], self[best]):
                    best = j
            if best == index:
                break
            self._swap(best, index)
            index = best

    def _sift_up(self, index: int):
        while index > 0:
            p = ListHeap.parent_i(index)
            if not self.compare(self[index], self[p]):
                break
            self._swap(index, p)
            index = p
