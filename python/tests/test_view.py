import itertools

import pytest

from view import *

N = 3

@pytest.fixture
def list_view() -> ListView:
    return ListView(list(range(N)))

@pytest.fixture
def deque_view() -> DequeView:
    return DequeView(collections.deque(range(N)))

@pytest.fixture(params = [list_view, deque_view], ids = ['list', 'deque'])
def list_or_deque_view(request: pytest.FixtureRequest) -> ListView |  DequeView:
    return request.getfixturevalue(request.param.__name__)

@pytest.fixture
def set_view() -> SetView:
    return SetView({1, 2})

@pytest.fixture
def set_2() -> set:
    return {2, 3}

@pytest.fixture
def dict_view() -> DictView:
    return DictView({1: -1, 2: -2})


# ===== base tests =====

def test_constructor():
    lis = [1, 2, 3]
    bv = BaseView(lis)
    assert bv._data is lis

def test_get_value_helper(list_view: BaseView):
    assert BaseView._get_value(list_view) is list_view._data
    assert BaseView._get_value(list_view._data) is list_view._data

def test_len(list_view: BaseView):
    assert len(list_view) == len(list_view._data)

def test_bool(list_view: BaseView):
    assert bool(list_view) == bool(list_view._data)

def test_str(list_view: BaseView):
    assert str(list_view) == str(list_view._data)

def test_repr(list_view: BaseView):
    repr_original  = repr(list_view._data)
    repr_view = repr(list_view)
    # E.g., "View of X"
    assert repr_original in repr_view
    assert repr_original != repr_view

def test_contains(list_view: BaseView):
    for i in range(-1, 1):
        assert (i in list_view) == (i in list_view._data)

def test_iter(list_view: BaseView):
    iter_original = iter(list_view._data)
    iter_view = iter(list_view)
    for i in iter_original:
        assert next(iter_view) == i
    with pytest.raises(StopIteration):
        next(iter_view)

def test_add(list_view: BaseView):
    assert list_view + [1] == list_view._data + [1]

def test_sub(set_view: BaseView, set_2: set):
    assert set_view - set_2 == set_view._data - set_2

def test_and(set_view: BaseView, set_2: set):
    assert set_view & set_2 == set_view._data & set_2

def test_or(set_view: BaseView, set_2: set):
    assert (set_view | set_2) == (set_view._data | set_2)

def test_eq(list_view: BaseView):
    assert list_view == list(list_view._data)

def test_lt(list_view: BaseView):
    assert list_view < [1e9]

def test_getitem(list_view: BaseView):
    assert list_view[0] == list_view._data[0]
    assert list_view[:2] == list_view._data[:2]


# ===== list / deque tests =====

def test_copy_list_deque(list_or_deque_view: ListView):
    assert list_or_deque_view.copy() == list_or_deque_view._data.copy()

def test_count(list_or_deque_view: ListView):
    for i in (-1, 1):
        assert list_or_deque_view.count(i) == list_or_deque_view._data.count(i)

def test_index(list_or_deque_view: ListView):
    for params in itertools.product(range(len(list_or_deque_view)), repeat = 3):
        try:
            r = list_or_deque_view._data.index(*params)
        except ValueError:
            with pytest.raises(ValueError):
                list_or_deque_view.index(*params)
        else:
            assert list_or_deque_view.index(*params) == r


# ===== set tests =====

def test_copy_set(set_view: SetView):
    assert set_view.copy() == set_view._data.copy()

def test_difference(set_view: SetView, set_2: set):
    assert set_view.difference(set_2) == set_view._data.difference(set_2)

def test_intersection(set_view: SetView, set_2: set):
    assert set_view.intersection(set_2) == set_view._data.intersection(set_2)

def test_isdisjoint(set_view: SetView, set_2: set):
    assert set_view.isdisjoint(set_2) == set_view._data.isdisjoint(set_2)

def test_issubset(set_view: SetView, set_2: set):
    assert set_view.isdisjoint(set_2) == set_view._data.isdisjoint(set_2)

def test_issuperset(set_view: SetView, set_2: set):
    assert set_view.issuperset(set_2) == set_view._data.issuperset(set_2)

def test_symmetric_difference(set_view: SetView, set_2: set):
    assert set_view.symmetric_difference(set_2) == set_view._data.symmetric_difference(set_2)

def test_union(set_view: SetView, set_2: set):
    assert set_view.union(set_2) == set_view._data.union(set_2)


# ===== dict tests =====

def test_get(dict_view: DictView):
    for params in [(1, None), (0, 'zero')]:
        assert dict_view.get(*params) == dict_view._data.get(*params)

def test_items(dict_view: DictView):
    assert sorted(dict_view.items()) == sorted(dict_view._data.items())

def test_keys(dict_view: DictView):
    assert sorted(dict_view.keys()) == sorted(dict_view._data.keys())

def test_values(dict_view: DictView):
    assert sorted(dict_view.values()) == sorted(dict_view._data.values())
