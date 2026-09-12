'''
This module contains immutable views of underlying base classes without
immutable types. That is, the methods are read-only and do not modify the
data structure.

Note that it is still possible to modify the items in the data structure since
the programmer still has access to references of that data.
'''


import abc
import collections
import sys
from typing import Any, Hashable, Iterable, Self


class BaseView(abc.ABC):
    '''Abstract base class for all view types with common methods.'''

    def __init__(self, data: Any):
        self._data = data

    @staticmethod
    def _get_value(value: Self | Any):
        '''
        Return the underlying object if the parameter is a view, 
        otherwise return the parameter itself.
        '''
        if isinstance(value, BaseView):
            return value._data
        return value

    def __len__(self):
        return len(self._data)
    
    def __bool__(self):
        return bool(self._data)

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return 'View of ' + repr(self._data)
    
    def __contains__(self, item: Any):
        return item in self._data

    def __iter__(self):
        return iter(self._data)

    def __add__(self, value: Self | Any, /):
        return self._data + BaseView._get_value(value)

    def __sub__(self, value: Self | Any, /):
        return self._data - BaseView._get_value(value)

    def __or__(self, value: Self | Any, /):
        return self._data | BaseView._get_value(value)

    def __and__(self, value: Self | Any, /):
        return self._data & BaseView._get_value(value)

    def __eq__(self, value: Self | Any, /):
        return self._data == BaseView._get_value(value)

    def __lt__(self, value: Self | Any, /):
        return self._data < BaseView._get_value(value)

    def __getitem__(self, index: int):
        return self._data[index]
    
        
class ListView(BaseView):
    '''An immutable view of the built-in list type.'''

    def __init__(self, lis: list):
        super().__init__(lis)
        self._data: list

    def copy(self) -> list:
        '''See list.copy'''
        return self._data.copy()

    def count(self, value: Any, /) -> int:
        '''See list.count'''
        return self._data.count(value)

    def index(self, value: Any, start: int = 0, stop: int = sys.maxsize, /) -> int:
        '''See list.index'''
        return self._data.index(value, start, stop)
    

class SetView(BaseView):
    '''An immutable view of the built-in set type.'''

    def __init__(self, set_: set):
        super().__init__(set_)
        self._data: set

    def copy(self):
        '''See set.copy'''
        return self._data.copy()

    def difference(self, *s: Iterable[object]) -> set:
        '''See set.difference'''
        return self._data.difference(*s)

    def intersection(self, *s: Iterable[object]) -> set:
        '''See set.intersection'''
        return self._data.intersection(*s)

    def isdisjoint(self, s: Iterable[object], /) -> bool:
        '''See set.isdisjoint'''
        return self._data.isdisjoint(s)

    def issubset(self, s: Iterable[object], /) -> bool:
        '''See set.issubset'''
        return self._data.issubset(s)

    def issuperset(self, s: Iterable[object], /) -> bool:
        '''See set.issuperset'''
        return self._data.issuperset(s)

    def symmetric_difference(self, s: Iterable, /) -> set:
        '''See set.symmetric_difference'''
        return self._data.symmetric_difference(s)

    def union(self, *s: Iterable) -> set:
        '''See set.union'''
        return self._data.union(*s)


class DictView(BaseView):
    '''An immutable view of the underlying dict type.'''

    def __init__(self, dict_: dict):
        super().__init__(dict_)
        self._data: dict

    def get(self, key: Hashable, default: Hashable = None, /) -> Any:
        '''See dict.get'''
        return self._data.get(key, default)

    def items(self) -> Iterable[tuple[Hashable, Any]]:
        '''See dict.items'''
        return self._data.items()

    def keys(self) -> Iterable[Hashable]:
        '''See dict.keys'''
        return self._data.keys()

    def values(self) -> Iterable[Any]:
        '''See dict.values'''
        return self._data.values()


class DequeView(BaseView):
    '''An immutable view of the built-in collections.deque type.'''

    def __init__(self, deque: collections.deque):
        super().__init__(deque)
        self._data: collections.deque

    def copy(self) -> collections.deque:
        '''See collections.deque.copy'''
        return self._data.copy()

    def count(self, x: Any):
        '''See collections.deque.count'''
        return self._data.count(x)

    def index(self, x: Any, start: int = 0, stop: int = sys.maxsize) -> int:
        '''See collections.deque.index'''
        return self._data.index(x, start, stop)
