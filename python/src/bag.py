import abc
import collections
from typing import Iterable, TypeVar, Generic


T = TypeVar('T')

class Bag(abc.ABC, Generic[T]):
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

    def push_many(self, items: Iterable[T]):
        '''Insert many items into the Bag one by one.'''
        for i in items:
            self.push(i)

    def pop(self) -> T:
        '''Remove an item from the bag.'''
        ...

    def peek(self) -> T:
        '''Equivalent to pop() without removing the item.'''
        ...

    def __len__(self) -> int:
        '''Check the size of the bag via len(my_bag).'''
        ...

    def __bool__(self) -> bool:
        '''A bag is False-y if it is empty.'''
        return bool(len(self))

    def __iter__(self) -> Iterable[T]:
        '''Iterating through the bag empties it.'''
        while self:
            yield self.pop()


class DequeBag(Bag[T], abc.ABC):

    def __init__(self, items: Iterable[T] = ()):
        self._deque = collections.deque(items)

    def __len__(self):
        return len(self._deque)
    
    def push(self, item: T):
        self._deque.append(item)


class Stack(DequeBag[T]):

    def pop(self) -> T:
        return self._deque.pop()

    def peek(self) -> T:
        return self._deque[-1]
    

class Queue(DequeBag[T]):

    def pop(self) -> T:
        return self._deque.popleft()

    def peek(self) -> T:
        return self._deque[0]
