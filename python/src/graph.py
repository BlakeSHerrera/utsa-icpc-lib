
from __future__ import annotations
import abc
import collections, collections.abc
import enum
import itertools
from numbers import Number
from typing import Any, Iterable, Mapping, Self

import utils


class Node:

    def __init__(self, data: Any):
        self.data = data


class Edge:

    def __init__(self, from_: Node, to: Node, weight: Number = 1):
        self.from_ = from_
        self.to = to
        self.weight = weight

    def reverse(self) -> Self:
        return Edge(self.to, self.from_)

    @property
    def nodes(self) -> tuple[Node, Node]:
        return (self.from_, self.to)

    @property
    def nodes_r(self) -> tuple[Node, Node]:
        return (self.to, self.from_)

    def __contains__(self, other: Node) -> bool:
        return other in self.nodes

    def neighbors(self, direction: Direction) -> Iterable[Node]:
        match direction:
            case Direction.OUT:
                return (self.to,)
            case Direction.IN:
                return (self.from_,)
            case Direction.BOTH:
                return self.nodes


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
            

class GraphView:

    def __init__(self, graph: Graph):
        self._graph = graph

    def neighbors(self, direction: Direction, element: Node | Edge) -> Iterable[Node | Edge]:
        if isinstance(element, Edge):
            return element.neighbors(direction)
        return self._graph._neighbors(direction, element)

    # Thin wrappers
    def degree(self, direction: Direction, node: Node) -> int: return self._graph.degree(direction, node)
    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: return self._graph.edges_between(from_, to)
    def nodes(self) -> Iterable[Node]: return self._graph.nodes()
    def edges(self) -> Iterable[Edge]: return self._graph.edges()
    def v(self) -> int: return self._graph.v()
    def e(self) -> int: return self._graph.e()
    def __bool__(self) -> bool: return bool(self._graph)

    def __eq__(self, other: Graph) -> bool:
        return set(self.nodes()) == set(other.nodes()) and set(self.edges()) == set(other.edges())
    
class Graph(GraphView, abc.ABC):

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        super().__init__(self)
        utils.apply(self.add_node, nodes)
        utils.apply(self.add_edge, edges)

    def add_node(self, node: Node): raise NotImplementedError
    def add_edge(self, edge: Edge): raise NotImplementedError
    def remove_node(self, node: Node): raise NotImplementedError
    def remove_edge(self, edge: Edge): raise NotImplementedError

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]: raise NotImplementedError
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
        self._adjacency: Mapping[Direction, dict[Node, set[Edge]]] = [dict() for _ in Direction]
        self._self_edges: dict[Node, set[Edge]] = dict()
        super().__init__(nodes, edges)
    
    def add_node(self, node: Node):
        for dir in Direction:
            self._adjacency[dir][node] = set()
        self._self_edges[node] = set()
    
    def add_edge(self, edge: Edge):
        for dir in Direction:
            for node in edge.neighbors(dir.reverse()):
                self._adjacency[dir][node].add(edge)
        if edge.from_ is edge.to:
            self._self_edges[edge.to].add(edge)

    def remove_node(self, node: Node):
        for dir in Direction:
            del self._adjacency[dir][node]
        del self._self_edges[node]

    def remove_edge(self, edge: Edge):
        for dir in Direction:
            for node in edge.neighbors(dir.reverse()):
                self._adjacency[dir][node].remove(edge)
        if edge.from_ is edge.to:
            self._self_edges[edge.to].remove(edge)

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]:
        if direction is Direction.BOTH:
            return itertools.chain(self._adjacency[direction][node], self._self_edges[node])
        return self._adjacency[direction][node]

    def degree(self, direction: Direction, node: Node) -> int:
        if direction is Direction.BOTH:
            return len(self._adjacency[direction][node]) + len(self._self_edges[node])
        return len(self._adjacency[direction][node])
    
    # def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: raise NotImplementedError
    
    def nodes(self) -> collections.abc.KeysView[Node]:
        return self._adjacency[Direction.OUT].keys()

    def edge_sets(self) -> collections.abc.ValuesView[set[Edge]]:
        return self._adjacency[Direction.OUT].values()
    
    def edges(self) -> Iterable[Edge]:
        return itertools.chain.from_iterable(self.edge_sets())

    def v(self) -> int:
        return len(self._adjacency[Direction.OUT])

    def e(self) -> int:
        return sum(map(len, self.edge_sets()))

    def __bool__(self) -> bool:
        return bool(self.v())


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

    # def neighbor_nodes(self, direction: Direction, node: Node) -> Iterable[Edge]: raise NotImplementedError
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


class EdgeSearch(Graph):

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._nodes = set(nodes)
        self._edges: dict[Direction, dict[Node, dict[Node, set[Edge]]]] \
            = [collections.defaultdict(lambda: collections.defaultdict(set)) for _ in Direction]
        super().__init__(nodes, edges)

    def add_node(self, node: Node):
        self._nodes.add(node)

    def add_edge(self, edge: Edge):
        for dir in Direction:
            for node_1, node_2 in dir.orient(edge):
                self._edges[dir][node_1][node_2].add(edge)

    def remove_node(self, node: Node):
        self._nodes.remove(node)
        for dir in Direction:
            second_node_mapping = self._edges[dir].pop(node, ())
            if not second_node_mapping:
                continue
            for edge_set in second_node_mapping.values():
                utils.apply(self.remove_edge, edge_set)
            second_node_mapping.pop(node, None)

    def remove_edge(self, edge: Edge):
        for dir in Direction:
            for node_1, node_2 in dir.orient(edge):
                self._edges[dir][node_1][node_2].remove(edge)

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]:
        return itertools.chain.from_iterable(self._edges[direction][node].values())

    # def degree(self, direction: Direction, node: Node) -> int: raise NotImplementedError

    def edges_between(self, from_: Node, to: Node) -> set[Edge]:
        return self.edges[Direction.OUT][from_][to]

    def nodes(self) -> set[Node]:
        return self._nodes
    
    def edges(self) -> Iterable[Edge]:
        return itertools.chain.from_iterable(
            itertools.chain.from_iterable(
                map(dict.values, self._edges[Direction.OUT].values())))

    def v(self) -> int:
        return len(self._nodes)

    # def e(self) -> int: raise NotImplementedError

    def __bool__(self) -> bool:
        return bool(self._nodes)
