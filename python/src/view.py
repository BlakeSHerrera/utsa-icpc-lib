import abc
import sys
from typing import Any, Hashable, Iterable, Self


class BaseView(abc.ABC):

    def __init__(self, data: Any):
        self._data = data

    @staticmethod
    def _get_value(value: Self | Any):
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

    def __init__(self, lis: list):
        super().__init__(lis)
        self._data: list

    def copy(self) -> list:
        return self._data.copy()

    def count(self, value: Any, /) -> int:
        return self._data.count(value)

    def index(self, value: Any, start: int = 0, stop: int = sys.maxsize, /) -> int:
        return self._data.index(value, start, stop)
    

class SetView(BaseView):

    def __init__(self, set_: set):
        super().__init__(set_)
        self._data: set

    def copy(self):
        return self._data.copy()

    def difference(self, *s: Iterable[object]) -> set:
        return self._data.difference(*s)

    def intersection(self, *s: Iterable[object]) -> set:
        return self._data.intersection(*s)

    def isdisjoint(self, s: Iterable[object], /) -> bool:
        return self._data.isdisjoint(s)

    def issubset(self, s: Iterable[object], /) -> bool:
        return self._data.issubset(s)

    def issuperset(self, s: Iterable[object], /) -> bool:
        return self._data.issuperset(s)

    def symmetric_difference(self, s: Iterable, /) -> set:
        return self._data.symmetric_difference(s)

    def union(self, *s: Iterable) -> set:
        return self._data.union(*s)


class DictView(BaseView):

    def __init__(self, dict_: dict):
        super().__init__(dict_)
        self._data: dict

    def get(self, key: Hashable, default: Hashable = None, /) -> Any:
        return self._data.get(key, default)

    def items(self) -> Iterable[tuple[Hashable, Any]]:
        return self._data.items()

    def keys(self) -> Iterable[Hashable]:
        return self._data.keys()

    def values(self) -> Iterable[Any]:
        return self._data.values()