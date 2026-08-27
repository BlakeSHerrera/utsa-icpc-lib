
from __future__ import annotations
import abc
import collections, collections.abc
import enum
import functools
import itertools
import math
from numbers import Number
import operator
from typing import Any, Iterable, Mapping, Protocol, Self, TypeVar

from complexity import O, query, constant, inf
import utils


T = TypeVar('T')



    
class Node:

    def __init__(self, data: Any):
        self.data = data


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

    def orient(self, edge: Edge) -> Iterable[tuple[Node, Node]]:
        match self:
            case Direction.OUT:
                return (edge.nodes,)
            case Direction.IN:
                return (edge.nodes_r,)
            case Direction.BOTH:
                return (edge.nodes, edge.nodes_r)


class Edge:

    def __init__(self, from_: Node, to: Node):
        self.from_ = from_
        self.to = to

    def reverse(self) -> Self:
        return  Edge(self.to, self.from_, **self.properties)

    @property
    def nodes(self) -> tuple[Node, Node]:
        return (self.from_, self.to)

    @property
    def nodes_r(self) -> tuple[Node, Node]:
        return (self.to, self.from_)

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

    def __init__(self, from_: Node, to: Node, weight: Number):
        super().__init__(from_, to)
        self.weight = weight


class GraphView:

    def __init__(self, graph: Graph):
        self._graph = graph

    def neighbors(self, direction: Direction, element: Node | Edge) -> Iterable[Node | Edge]:
        if isinstance(element, Edge):
            return element.neighbors(direction)
        return self._graph.neighbors(element, direction)

    # Thin wrappers
    def degree(self, direction: Direction, node: Node) -> int: return self._graph.degree(direction, node)
    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: return self._graph.edges_between(from_, to)
    def nodes(self) -> Iterable[Node]: return self._graph.nodes()
    def edges(self) -> Iterable[Edge]: return self._graph.edges()
    def v(self) -> int: return self._graph.v()
    def e(self) -> int: return self._graph.e()
    def __bool__(self) -> bool: return bool(self._graph)

    
class Graph(GraphView, abc.ABC):

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        super().__init__(self)
        utils.apply(self.add_node, nodes)
        utils.apply(self.add_edge, edges)
        

    def add_node(self, node: Node): raise NotImplementedError
    def add_edge(self, edge: Edge): raise NotImplementedError
    def remove_node(self, node: Node): raise NotImplementedError
    def remove_edge(self, edge: Edge): raise NotImplementedError

    def neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]: raise NotImplementedError
    def degree(self, direction: Direction, node: Node) -> int: raise NotImplementedError
    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: raise NotImplementedError
    def nodes(self) -> Iterable[Node]: raise NotImplementedError
    def edges(self) -> Iterable[Edge]: raise NotImplementedError
    def v(self) -> int: raise NotImplementedError
    def e(self) -> int: raise NotImplementedError
    def __bool__(self) -> bool: raise NotImplementedError


class LaxGraph(Graph, abc.ABC):
    def add_node(self, node: Node): pass
    def add_edge(self, edge: Edge): pass
    def remove_node(self, node: Node): pass
    def remove_edge(self, edge: Edge): pass


class AdjacencySet(Graph):

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._adjacency = Mapping[Direction, dict[Node, set[Edge]]] = [dict() for _ in Direction]
        super().__init__(nodes, edges)
    
    def add_node(self, node: Node):
        for dir in Direction:
            self._adjacency[dir][node] = set()
    
    def add_edge(self, edge: Edge):
        for dir in Direction:
            for node in edge.neighbors(dir):
                self._adjacency[dir][node].add(edge)

    def remove_node(self, node: Node):
        for dir in Direction:
            del self._adjacency[dir][node]

    def remove_edge(self, edge: Edge):
        for dir in Direction:
            for node in edge.neighbors(dir):
                self._adjacency[dir][node].remove(edge)

    def neighbors(self, direction: Direction, node: Node) -> set[Edge]:
        return self._adjacency[direction][node]

    def degree(self, direction: Direction, node: Node) -> int:
        return len(self.neighbors(direction, node))
    
    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]:
        return (i for i in self._adjacency[Direction.OUT][from_] if i.to is to)
    
    def nodes(self) -> collections.abc.KeysView[Node]:
        return self._adjacency[Direction.OUT].keys()

    def edge_sets(self) -> collections.abc.ValuesView[set[Edge]]:
        return self._adjacency[Direction.OUT].values()
    
    def edges(self) -> Iterable[Edge]:
        return itertools.chain.from_iterable(self.edge_sets())

    def v(self) -> int:
        return len(self._adjacency)

    def e(self) -> int:
        return sum(map(len, self.edge_sets()))

    def __bool__(self) -> bool:
        return bool(self._adjacency)


class ElementSet(Graph):

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._nodes: set[Node] = set()
        self._edges: set[Edge] = set()
        self._elements: set[Node | Edge] = set()
        super().__init__(nodes, edges)

    def add_node(self, node: Node):
        self._nodes.add(node)
        self._elements.add(node)

    def add_edge(self, edge: Edge):
        self._edges.add(edge)
        self._elements.add(edge)

    def remove_node(self, node: Node):
        self._nodes.remove(node)
        self._elements.remove(node)
        for edge in tuple(self._edges):
            if node in edge:
                self.remove_edge(edge)

    def remove_edge(self, edge: Edge):
        self._edges.remove(edge)
        self._elements.remove(edge)

    # def neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]: raise NotImplementedError
    # def degree(self, direction: Direction, node: Node) -> int: raise NotImplementedError
    # def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: raise NotImplementedError
    
    def nodes(self) -> set[Node]:
        return self._nodes
    
    def edges(self) -> set[Edge]:
        return self._edges

    def elements(self) -> set[Node | Edge]:
        return self._elements

    def v(self) -> int:
        return len(self._nodes)

    def e(self) -> int:
        return len(self._edges)

    def __bool__(self) -> bool:
        return bool(self._elements)


class EdgeSearch(LaxGraph):

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._edges: Mapping[Direction, dict[Node, dict[Node, set[Edge]]]] \
            = [collections.defaultdict(lambda: collections.defaultdict(set)) for _ in Direction]
        super().__init__(nodes, edges)

    # def add_node(self, node: Node): pass

    def add_edge(self, edge: Edge):
        for dir in Direction:
            for node_1, node_2 in dir.orient(edge):
                self._edges[dir][node_1][node_2].add(edge)

    def remove_node(self, node: Node):
        for dir in Direction:
            for nodes in self._edges[dir].pop(node):
                utils.apply(self.remove_edge, nodes)
                nodes.pop(node, None)

    def remove_edge(self, edge: Edge):
        for dir in Direction:
            for node_1, node_2 in dir.orient(edge):
                self._edges[dir][node_1][node_2].remove(edge)

    def neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]:
        return itertools.chain.from_iterable(self._edges[direction][node].values())

    # def degree(self, direction: Direction, node: Node) -> int: raise NotImplementedError

    def edges_between(self, from_: Node, to: Node) -> set[Edge]:
        return self.edges[Direction.OUT][from_][to]

    # def nodes(self) -> set[Node]: raise NotImplementedError
    
    def edges(self) -> Iterable[Edge]:
        return itertools.chain.from_iterable(map(dict.values, self._edges.values()))

    # def v(self) -> int: raise NotImplementedError
    # def e(self) -> int: raise NotImplementedError
    # def __bool__(self) -> bool: raise NotImplementedError
