
from __future__ import annotations
import abc
import collections, collections.abc
import enum
import itertools
from numbers import Real
from typing import Any, Iterable, Literal, Mapping, Self, Sequence

import utils


class Node:

    def __init__(self, data: Any):
        self.data = data


class Edge:

    def __init__(self, from_: Node, to: Node, weight: Real = 1):
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

    def neighbor(self, direction: Literal[Direction.OUT, Direction.IN]) -> Node:
        match direction:
            case Direction.OUT:
                return self.to
            case Direction.IN:
                return self.from_    
        raise ValueError('Neighbor only accepts Direction.OUT and Direction.IN')


class SimpleEdge(Edge):

    def __hash__(self):
        return hash(self.nodes)

    def __eq__(self, other: SimpleEdge):
        return self.nodes == other.nodes


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

    def __init__(self, graph: GraphView):
        self._graph = graph

    def neighbors(self, direction: Direction, element: Node | Edge) -> Iterable[Node | Edge]:
        if isinstance(element, Edge):
            return element.neighbors(direction)
        return self._neighbors(direction, element)

    # Thin wrappers
    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]: return self._graph._neighbors(direction, node)
    def degree(self, direction: Direction, node: Node) -> int: return self._graph.degree(direction, node)
    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: return self._graph.edges_between(from_, to)
    def nodes(self) -> Iterable[Node]: return self._graph.nodes()
    def edges(self) -> Iterable[Edge]: return self._graph.edges()
    def v(self) -> int: return self._graph.v()
    def e(self) -> int: return self._graph.e()
    def __bool__(self) -> bool: return bool(self._graph)

    def __eq__(self, other: GraphView) -> bool:
        return set(self.nodes()) == set(other.nodes()) and set(self.edges()) == set(other.edges())

    def has_node(self, node: Node):
        return node in self.nodes()

    def has_edge(self, edge: Edge):
        return edge in self.edges()

    def has_edge_between(self, from_: Node, to: Node):
        return not utils.is_empty(self.edges_between(from_, to))
    
    
    
class MutableGraph(GraphView, abc.ABC):

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        super().__init__(self)
        self.add_all(nodes, edges)

    def add_node(self, node: Node): raise NotImplementedError
    def add_edge(self, edge: Edge): raise NotImplementedError
    def remove_node(self, node: Node): raise NotImplementedError
    def remove_edge(self, edge: Edge): raise NotImplementedError
    
    def add_all(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        utils.apply(self.add_node, nodes)
        utils.apply(self.add_edge, edges)

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]: raise NotImplementedError
    def degree(self, direction: Direction, node: Node) -> int: raise NotImplementedError
    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: raise NotImplementedError
    def nodes(self) -> Iterable[Node]: raise NotImplementedError
    def edges(self) -> Iterable[Edge]: raise NotImplementedError
    def v(self) -> int: raise NotImplementedError
    def e(self) -> int: raise NotImplementedError
    def __bool__(self) -> bool: raise NotImplementedError


class LaxGraph(MutableGraph, abc.ABC):
    def add_node(self, node: Node): pass
    def add_edge(self, edge: Edge): pass
    def remove_node(self, node: Node):
        for edge in self._neighbors(Direction.BOTH, node):
            self.remove_edge(edge)
    def remove_edge(self, edge: Edge): pass


class MutableGraphWrapper(GraphView, MutableGraph):

    def __init__(self, backend: MutableGraph, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        super().__init__(backend)
        self._backend = backend
        self.add_all(nodes, edges)

    def add_node(self, node: Node): return self._backend.add_node(node)
    def add_edge(self, edge: Edge): return self._backend.add_edge(edge)
    def remove_node(self, node: Node): return self._backend.remove_node(node)
    def remove_edge(self, edge: Edge): return self._backend.remove_edge(edge)


class AdjacencySet(MutableGraph):

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


class ElementSet(MutableGraph):

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

    # def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]: raise NotImplementedError
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


class EdgeSearch(MutableGraph):

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



class SimpleGraphView(GraphView):

    def neighbors(self, direction: Direction, element: Node | SimpleEdge) -> Iterable[Node | SimpleEdge]:
        if isinstance(element, Edge):
            return element.neighbors(direction)
        return self._neighbors(direction, element)

class MutableSimpleGraph(SimpleGraphView, MutableGraphWrapper):

    def __init__(self, backend: MutableGraph, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        SimpleGraphView.__init__(self, backend)
        MutableGraphWrapper.__init__(self, backend, nodes, edges)

    def add_edge(self, edge: Edge):
        if edge.from_ is edge.to:
            raise ValueError('Simple graphs cannot contain self-edges.')
        if self._backend.has_edge_between(*edge.nodes):
            raise ValueError('Simple graphs cannot contain multi edges.')
        self._backend.add_edge(edge)


class RingGraphView(SimpleGraphView):

    def __init__(self, semi_dense_graph: RingGraphView):
        super().__init__(semi_dense_graph)
        self._semi_dense_graph = semi_dense_graph

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[SimpleEdge]:
        nodes = self.nodes()
        n = len(nodes)
        product = itertools.product(range(n), self.connections())
        match direction:
            case Direction.OUT:
                return (SimpleEdge(nodes[i], nodes[j % n]) for i, j in product)
            case Direction.IN:
                return (SimpleEdge(nodes[-j % n], nodes[i]) for i, j in product)
            case Direction.BOTH:
                return itertools.chain(
                    self._neighbors(direction.OUT, node), 
                    self._neighbors(direction.IN, node))
    
    def edges_between(self, from_: Node, to: Node) -> tuple[SimpleEdge]:
        i, j = map(self.index_of, (from_, to))
        return (SimpleEdge(from_, to),) if (j - i) in self.connections() else ()

    def nodes(self) -> Sequence[Node]:
        raise NotImplementedError
    
    def edges(self) -> Iterable[SimpleEdge]: 
        return itertools.chain.from_iterable(self._neighbors(Direction.OUT, i) for i in self.nodes())

    def v(self) -> int: 
        return len(self.nodes())

    def e(self) -> int:
        return self.v() * len(self.connections)
    
    def __bool__(self) -> bool: 
        return bool(self.v())

    def __eq__(self, other: RingGraphView) -> bool:
        return set(self.nodes()) == set(other.nodes()) and set(self.connections) == set(other.connections)

    def has_node(self, node: Node) -> bool:
        return node in self.nodes()

    def has_edge(self, edge: Edge) -> bool:
        return bool(self.edges_between(*edge.nodes))

    def has_edge_between(self, from_: Node, to: Node):
        return not utils.is_empty(self.edges_between(from_, to))

    def connections(self) -> set[int]:
        raise NotImplementedError

    def index_of(self, node: Node) -> int:
        raise NotImplementedError


class MutableRingGraph(RingGraphView):
    # TODO not really mutable

    def __init__(self, nodes: Iterable[Node], connections: Iterable[int]):
        super().__init__(self)
        self._nodes = tuple(nodes)
        self._index = {v: i for i, v in self._nodes}
        self._connections = {i % len(self._nodes) for i in connections}
        if 0 in self._connections:
            raise ValueError('Self-edges violate simple graph invariant.')

    def nodes(self) -> tuple[Node]:
        return self._nodes

    def connections(self) -> set[int]:
        return self._connections

    def index_of(self, node: Node):
        return self._index[node]


class CompleteGraphView(SimpleGraphView):

    def __init__(self, dense_graph: MutableCompleteGraph):
        super().__init__(dense_graph)
        self._dense_graph = dense_graph

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[SimpleEdge]:
        nodes = filter(node.__eq__, self.nodes())
        match direction:
            case Direction.OUT:
                return (SimpleEdge(node, i) for i in nodes)
            case Direction.IN:
                return (SimpleEdge(i, node) for i in nodes)
            case Direction.BOTH:
                return itertools.chain(
                    self._neighbors(Direction.OUT, node), 
                    self._neighbors(Direction.IN, node))

    def degree(self, direction: Direction, node: Node) -> int:
        return (1 + direction is Direction.BOTH) * (self.v() - 1)

    def edges_between(self, from_: Node, to: Node) -> Iterable[SimpleEdge]:
        return SimpleEdge(from_, to)

    def nodes(self) -> set[Node]:
        return self._dense_graph.nodes()

    def edges(self) -> Iterable[SimpleEdge]:
        return itertools.starmap(SimpleEdge, itertools.permutations(self.nodes(), r = 2))

    def v(self) -> int:
        return len(self.nodes())

    def e(self) -> int:
        v = self.v()
        return v * (v - 1)

    def __bool__(self):
        return bool(self.nodes())

    def __eq__(self, other: CompleteGraphView):
        return self.nodes() == other.nodes()

    def has_edge(self, edge: SimpleEdge):
        return self.has_edge_between(*edge.nodes)

    def has_edge_between(self, from_: Node, to: Node):
        return all(map(self.has_edge, (from_, to)))
    

class MutableCompleteGraph(CompleteGraphView):

    def __init__(self, nodes: Iterable[Node] = ()):
        self._nodes = set(nodes)

    def add_node(self, node: Node):
        self._nodes.add(node)

    def remove_node(self, node: Node):
        self._nodes.remove(node)


class BipartiteGraphView(GraphView):
    pass

class MutableBipartiteGraph(BipartiteGraphView, MutableGraphWrapper):

    def __init__(self, backend: MutableGraph, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._parity: dict[Node, bool] = dict()
        BipartiteGraphView.__init__(self)
        MutableGraphWrapper.__init__(self, backend, nodes, edges)

    def remove_node(self, node: Node):
        MutableGraphWrapper.remove_node(self, node)
        self._parity.pop(node, None)

    def add_edge(self, edge: Edge):
        a = self._parity.get(edge.from_)
        b = self._parity.get(edge.to)
        if a is not None and b is not None:
            if a == b:
                raise ValueError('Violation of parity in bipartite graph.')
        elif a is None and b is None:
            # TODO What to do? How to efficiently check invariant violation if two disjoint sets are combined?
            raise NotImplementedError
        elif a is None:
            self._parity[a] = not b
        elif b is None:
            self._parity[b] = not a


class HypercubeGraphView(SimpleGraphView):

    def __init__(self, hypercube_graph_view: HypercubeGraphView):
        super().__init__(hypercube_graph_view)
        self._hypercube_graph_view = hypercube_graph_view

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[SimpleEdge]:
        i = self.index_of(node)
        match direction:
            case Direction.OUT:
                return (SimpleEdge(node, self.nodes()[2 << j ^  i]) for j in range(self.n()))
            case Direction.IN:
                return (SimpleEdge(self.nodes()[2 << j ^  i], node) for j in range(self.n()))
            case Direction.BOTH:
                return itertools.chain(
                    self._neighbors(Direction.OUT, node),
                    self._neighbors(Direction.IN, node))

    def degree(self, direction: Direction, node: Node) -> int:
        return (1 + direction is Direction.BOTH) * self.n()
    
    def edges_between(self, from_: Node, to: Node) -> tuple[SimpleEdge]: 
        from_i, to_i = map(self.index_of, (from_, to))
        return ((from_i ^ to_i).bit_count() == 1) * (SimpleEdge(from_, to),)
    
    def nodes(self) -> Iterable[Node]: return self._graph.nodes()
    def edges(self) -> Iterable[Edge]: return self._graph.edges()

    def v(self) -> int:
        return 2 ** self.n()
    
    def e(self) -> int:
        self.v() * 2 * self.n()

    def __eq__(self, other: Self) -> bool:
        return self.n() == other.n() and set(self.nodes()) == set(other.nodes())

    def has_node(self, node: Node):
        return node in self.nodes()

    def has_edge(self, edge: Edge):
        return edge in self.edges()

    def has_edge_between(self, from_: Node, to: Node):
        return bool(self.edges_between(from_, to))

    def n(self) -> int:
        raise NotImplementedError

    def f(self):
        return self.e() - self.v() // 2 + 2

    def index_of(self, node: Node) -> int:
        raise NotImplementedError


class MutableHypercubeGraph(HypercubeGraphView):

    def __init__(self, n: int, data: Iterable):
        super().__init__(self)
        self._n = n
        self._nodes = list(map(Node, data))
        self._index = {v: i for i, v in enumerate(self._nodes)}
        if len(self.nodes) != 2 ** n:
            raise ValueError('Data does not match number of nodes in hypercube graph.')

    def nodes(self) -> list[Node]:
        return self._nodes

    def n(self):
        return self._n

    def index_of(self, node: Node):
        return self._index[node]
    