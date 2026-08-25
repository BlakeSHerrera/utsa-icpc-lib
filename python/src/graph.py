
from __future__ import annotations
import abc
import collections, collections.abc
import enum
import functools
import itertools
import math
from numbers import Number
import operator
from typing import Any, Iterable, Protocol, Self, TypeVar

from complexity import O, query, constant, inf
import utils


T = TypeVar('T')



    
class Node:

    def __init__(self, data: Any, **kwargs):
        self.data = data
        self.properties = kwargs


class Direction(utils.ZeroBasedEnum):
    
    OUT = enum.auto()
    IN = enum.auto()
    BOTH = enum.auto()

    def reverse(self) -> Self:
        match self:
            case Direction.OUT:
                return Direction.IN
            case Direction.IN:
                return Direction.OUT
            case BOTH:
                return BOTH


class Edge:

    def __init__(self, from_: Node, to: Node, **kwargs):
        self.from_ = from_
        self.to = to
        self.properties = kwargs

    def reverse(self) -> Self:
        return  Edge(self.to, self.from_, **self.properties)

    @property
    def nodes(self) -> tuple[Node, Node]:
        return (self.from_, self.to)

    def __contains__(self, other: Node) -> bool:
        return other in self.nodes

    def neighbors(self, direction: Direction) -> tuple[Node] | tuple[Node, Node]:
        match direction:
            case Direction.OUT:
                return (self.to,)
            case Direction.IN:
                return (self.from_,)
            case Direction.BOTH:
                return self.nodes


class WeightedEdge(Edge):

    def __init__(self, from_: Node, to: Node, weight: Number, **kwargs):
        super().__init__(from_, to, **kwargs)
        self.weight = weight

class GraphView:

    def __init__(self, index: Index):
        self._index = index

    def neighbors(self, element: Node | Edge, direction: Direction) -> Iterable[Node | Edge]:
        if isinstance(element, Edge):
            return element.neighbors(direction)
        return self._index.neighbors(element, direction)

    def degree(self, node: Node, direction: Direction) -> int:
        return self._index.degree(node, direction)

    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]:
        return self._index.edges_between(from_, to)

    @property
    def nodes(self) -> Iterable[Node]: 
        return self._index.nodes

    @property
    def edges(self) -> Iterable[Edge]:
        return self._index.edges

    @property
    def v(self) -> int:
        return self._index.v

    @property
    def e(self) -> int:
        return self._index.e
    
    def __bool__(self) -> bool:
        return bool(self._index)


class Index(abc.ABC):

    def add_node(self, node: Node):
        raise NotImplementedError

    def add_edge(self, edge: Edge):
        raise NotImplementedError

    def remove_node(self, node: Node):
        raise NotImplementedError

    def remove_edge(self, edge: Edge):
        raise NotImplementedError


class CompositeIndex(Index):

    def __init__(self, indices: Iterable[Index]):
        self.indices = tuple(indices)

    def add_node(self, node: Node):
        for i in self.indices:
            i.add_node(node)

    def add_edge(self, edge: Edge):
        for i in self.indices:
            i.add_edge(edge)

    def remove_node(self, node: Node):
        for i in self.indices:
            i.remove_node(node)

    def remove_edge(self, edge: Edge):
        for i in self.indices:
            i.remove_edge(edge)

    
class LaxIndex(Index, abc.ABC):

    def add_node(self, node: Node):
        pass

    def add_edge(self, edge: Edge):
        pass

    def remove_node(self, node: Node):
        pass

    def remove_edge(self, edge: Edge):
        pass
