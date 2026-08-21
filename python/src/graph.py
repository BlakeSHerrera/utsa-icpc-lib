

import itertools
from numbers import Number
from typing import Any, Generic, TypeVar


T = TypeVar('T')


class GraphElement:

    def __init__(self, **kwargs):
        self.properties = kwargs

    def __hash__(self):
        return id(self)

    def __getitem__(self, item: str):
        return self.properties[item]

    def get(self, item: str, default: Any = None) -> Any:
        return self.properties.get(item, default)

    def __contains__(self, item: str):
        return item in self.properties

    
class Node(GraphElement):

    def __init__(self, data: Any, **kwargs):
        super().__init__(**kwargs)
        self.data = data


class Edge(GraphElement):

    def __init__(self, from_: Node, to: Node, **kwargs):
        super().__init__(**kwargs)
        self.from_ = from_
        self.to = to

    @property
    def nodes(self) -> tuple[Node, Node]:
        return (self.from_, self.to)


class WeightedEdge(Edge):

    def __init__(self, from_: Node, to: Node, weight: Number, **kwargs):
        super().__init__(from_, to, **kwargs)
        self.weight = weight
