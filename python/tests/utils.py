
import operator
from typing import Callable

import pytest


def fixtures(*fixtures: pytest.FixtureDef):
    '''Parameterize multiple fixtures into one. The body and params can be omitted.'''
    
    def decorator(function: Callable):

        def wrapper(request: pytest.FixtureRequest):
            return request.getfixturevalue(request.param.__name__)

        wrapper.__name__ = function.__name__
        wrapper.__annotations__.update(function.__annotations__)
        wrapper.fixtures = fixtures
        get_name = operator.attrgetter('__name__')
        fixture_decorator = pytest.fixture(
            params = fixtures, 
            ids = map(get_name, fixtures),
            name = function.__name__)
        return fixture_decorator(wrapper)

    return decorator
