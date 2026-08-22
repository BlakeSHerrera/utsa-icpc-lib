
import abc
import enum
from numbers import Number
from typing import Any, Self, TypeVar


T = TypeVar('T')


class GraphElement(abc.ABC):

    def __init__(self, **kwargs):
        self.properties = kwargs

    def __hash__(self):
        return hash(id(self))

    
class Node(GraphElement):

    def __init__(self, data: Any, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    def __eq__(self, other: Self):
        return self.data == other.data

    def __lt__(self, other: Self):
        return self.data < other.data


class Direction(enum.IntEnum):
    OUT = 0
    IN = 1
    BOTH = 2


class Edge(GraphElement):

    def __init__(self, from_: Node, to: Node, **kwargs):
        super().__init__(**kwargs)
        self.from_ = from_
        self.to = to

    @property
    def nodes(self) -> tuple[Node, Node]:
        return (self.from_, self.to)

    def __eq__(self, other: Self):
        return self.nodes == other.nodes


class WeightedEdge(Edge):

    def __init__(self, from_: Node, to: Node, weight: Number, **kwargs):
        super().__init__(from_, to, **kwargs)
        self.weight = weight
