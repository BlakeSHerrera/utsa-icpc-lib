import abc
import collections
from typing import Iterable, TypeVar, Generic

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
