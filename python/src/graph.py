'''
A graph is a data structure that consists of nodes and edges that connect two nodes.

This library treats graphs as directed, weighted multigraphs. That is, all edges have 
directions (directed graph), and all edges have weight (weighted graph). Edges can 
connect the same node to itself, and multiple edges between the same nodes are allowed 
(multigraph). Read on to see how to simulate an undirected or unweighted graph.

An unweighted graph is very easy to implement. Algorithms can simply ignore the edge 
weight. By default, edges all have a weight of 1, which could potentially be used to 
count the number of steps taken in a traversal.

Similarly, to create an undirected graph, the edge direction can be ignored. Traversal 
is done with the `Direction` enum, which has the values `OUT`, `IN`, and `BOTH`. Thus, 
an undirected graph can be thought of as a graph where there is no edge `(u, v)` with a 
counterpart `(v, u)`, and the algorithm can simply utilize `Direction.BOTH` to traverse.
'''


from __future__ import annotations
import abc
import collections, collections.abc
import enum
import itertools
from numbers import Real
from typing import Any, Iterable, Mapping, Self

import utils


class Node:
    '''
    A node is a type of element in a graph. Nodes are connected by edges.
    Nodes typically carry some kind of data (at least a name or label typically).
    '''

    def __init__(self, data: Any):
        self.data = data


class Edge:
    '''
    An edge connects two nodes and has a defined weight (1 by default).
    The edge has a defined `from_` and `to` direction, so edges are directed.

    Two edges with the same `from_` and `to` nodes and same weight are not equivalent.
    Multiple edges are allowed between the same pair of nodes.
    '''

    def __init__(self, from_: Node, to: Node, weight: Real = 1):
        self.from_ = from_
        self.to = to
        self.weight = weight

    def reverse(self) -> Self:
        '''Return a new edge with the `from_` and `to` nodes reversed.'''
        return Edge(self.to, self.from_)

    @property
    def nodes(self) -> tuple[Node, Node]:
        '''
        Get the two nodes that the edge connects.
        The `from_` node is first and the `to` node is last.
        '''
        return (self.from_, self.to)

    @property
    def nodes_r(self) -> tuple[Node, Node]:
        '''
        Get the two nodes that the edge connects, in reverse order.
        The `from_` node is last and the `to` node is first.
        '''
        return (self.to, self.from_)

    def __contains__(self, other: Node) -> bool:
        '''Return true if the node is one of the nodes that the edge connects.'''
        return other in self.nodes

    def neighbors(self, direction: Direction) -> Iterable[Node]:
        '''Get the nodes that this edge connects, depending on the direction.'''
        match direction:
            case Direction.OUT:
                return (self.to,)
            case Direction.IN:
                return (self.from_,)
            case Direction.BOTH:
                return self.nodes


class SimpleEdge(Edge):
    '''
    A SimpleEdge is a component of a simple graph, where multiple edges
    between the same nodes in the same direction are not allowed.
    (Note that the mathematical definition also includes that there are 
    no self-edges, but this is allowed for SimpleEdge.)
    
    Two SimpleEdges are equal if their from_ and to nodes are equal
    (including the direction of the edge). They will also hash to the
    same value.
    '''

    def __hash__(self):
        return hash(self.nodes)

    def __eq__(self, other: SimpleEdge):
        return self.nodes == other.nodes


class Direction(utils.ZeroBasedEnum):
    '''An enum for defining the edge traversal directions.'''
    
    OUT = enum.auto()
    IN = enum.auto()
    BOTH = enum.auto()

    def reverse(self) -> Self:
        '''Reverse the direction. OUT <-> IN. BOTH remains unchanged.'''
        match self:
            case Direction.OUT:
                return Direction.IN
            case Direction.IN:
                return Direction.OUT
            case BOTH:
                return BOTH

    def orient(self, edge: Edge) -> Iterable[tuple[Node, Node]]:
        '''
        Get the nodes for an edge along this direction in traversal order. That is,
        OUT: (from_, to)
        IN: (to, from_)
        BOTH: (from_, to) and (to, from_)
        '''
        match self:
            case Direction.OUT:
                return (edge.nodes,)
            case Direction.IN:
                return (edge.nodes_r,)
            case Direction.BOTH:
                return (edge.nodes, edge.nodes_r)


class GraphView:
    '''An immutable view composed of an underlying concrete implementation.'''

    def __init__(self, graph: GraphView):
        self._graph = graph

    def neighbors(self, direction: Direction, element: Node | Edge) -> Iterable[Node | Edge]:
        '''Get the next elements given an element and a traversal direction.'''
        if isinstance(element, Edge):
            return element.neighbors(direction)
        return self._neighbors(direction, element)

    # Thin wrappers
    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]:
        '''Get all the neighbors of a node in a paticular direction.'''
        return self._graph._neighbors(direction, node)

    def degree(self, direction: Direction, node: Node) -> int:
        '''
        Get the in-degree, out-degree, or total degree of the node, which is
        the number of edges connected to the node in that direction.
        '''
        return self._graph.degree(direction, node)

    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: 
        '''Get all the edges between the two nodes.'''
        return self._graph.edges_between(from_, to)
    
    def nodes(self) -> Iterable[Node]: 
        '''Get all of the nodes of the graph.'''
        return self._graph.nodes()

    def edges(self) -> Iterable[Edge]: 
        '''Get all of the edges of the graph.'''
        return self._graph.edges()
    
    def v(self) -> int:
        '''Get the number of verticies (nodes) in the graph.'''
        return self._graph.v()
    
    def e(self) -> int: 
        '''Get the number of edges in the graph.'''
        return self._graph.e()
    
    def __bool__(self) -> bool: 
        '''A graph is false-y if it contains no nodes (and therefore no edges).'''
        return bool(self._graph)

    def __eq__(self, other: GraphView) -> bool:
        '''Two graphs are equal if their sets of nodes and edges are equal.'''
        return set(self.nodes()) == set(other.nodes()) \
            and set(self.edges()) == set(other.edges())
    
class Graph(GraphView, abc.ABC):
    '''A mutable graph is a graph that can be mutated and changed.'''

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        super().__init__(self)
        self.add_all(nodes, edges)

    def add_node(self, node: Node): 
        '''Add a node into the graph.'''
        raise NotImplementedError
    
    def add_edge(self, edge: Edge): 
        '''Add an edge into the graph.'''
        raise NotImplementedError
    
    def remove_node(self, node: Node): 
        '''Remove a node from the graph.'''
        raise NotImplementedError
    
    def remove_edge(self, edge: Edge): 
        '''Remove an edge from the graph.'''
        raise NotImplementedError
    
    def add_all(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        '''Add all of the given nodes and edges from the graph.'''
        utils.apply(self.add_node, nodes)
        utils.apply(self.add_edge, edges)

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]: 
        '''Get the edges that connect a node in the given direction.'''
        raise NotImplementedError

    def degree(self, direction: Direction, node: Node) -> int: 
        '''Get the in-degree, out-degree, or total degree of the node.'''
        raise NotImplementedError

    def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: 
        '''Get all edges between the two nodes.'''
        raise NotImplementedError

    def nodes(self) -> Iterable[Node]:
        '''Get all nodes in the graph.'''
        raise NotImplementedError

    def edges(self) -> Iterable[Edge]: 
        '''Get all edges in the graph.'''
        raise NotImplementedError

    def v(self) -> int: 
        '''Get the number of nodes (vertices) in the graph.'''
        raise NotImplementedError

    def e(self) -> int: 
        '''Get the number of edges in the graph.'''
        raise NotImplementedError

    def __bool__(self) -> bool: 
        '''A graph is false-y if it contains no nodes (and therefore no edges either).'''
        raise NotImplementedError


class CompositeGraph(Graph):
    '''
    A composite graph distributes graph mutations to multiple different concrete
    graph objects to keep them all in sync. The programmer still selects the
    most appropriate backend representation to answer different queries.
    '''

    def __init__(self, *backends: Graph, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._backends = backends
        super().__init__(nodes, edges)

    def add_node(self, node: Node):
        '''Add a node to every graph.'''
        for g in self._backends:
            g.add_node(node)

    def add_edge(self, edge: Edge):
        '''Add an edge to every graph.'''
        for g in self._backends:
            g.add_edge(edge)

    def remove_node(self, node: Node):
        '''Remove a node from every graph.'''
        for g in self._backends:
            g.remove_node(node)

    def remove_edge(self, edge: Edge):
        '''Remove an edge from every backend'''
        for g in self._backends:
            g.remove_edge(edge)


class LaxGraph(Graph, abc.ABC):
    '''
    A LaxGraph (relaxed graph) is one which is a partial implementation of a graph.
    The underlying mutations do not need to be concretely implemented.
    For example, the subclass could merely count only the number of nodes and
    therefore ignore any operations happening with edges.
    '''

    def add_node(self, node: Node):
        '''Add a node into the graph (this operation has no effect).''' 
        pass

    def add_edge(self, edge: Edge): 
        '''Add an edge into the graph (this operation has no effect).'''
        pass

    def remove_node(self, node: Node): 
        '''Remove a node from the graph (this operation has no effect).'''
        pass

    def remove_edge(self, edge: Edge): 
        '''Remove an edge from t he graph (this operation has no effect).'''
        pass


class AdjacencySet(Graph):
    '''
    An adjacency set keeps a mapping between a node and the edges it is connected to.
    This class keeps such a mapping for each of the three traversal directions.

    This type of graph is ideal for traversal, getting nodes and neighbors, and finding 
    the degree of a node.

    This type of graph is not suited for telling whether an edge exists in the graph or
    for getting the edges between two nodes.
    '''

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._adjacency: Mapping[Direction, dict[Node, set[Edge]]] = [dict() for _ in Direction]
        self._self_edges: dict[Node, set[Edge]] = dict()
        super().__init__(nodes, edges)
    
    def add_node(self, node: Node):
        '''Add a node into the graph.'''
        for dir in Direction:
            self._adjacency[dir][node] = set()
        self._self_edges[node] = set()
    
    def add_edge(self, edge: Edge):
        '''Add an edge into the graph.'''
        for dir in Direction:
            for node in edge.neighbors(dir.reverse()):
                self._adjacency[dir][node].add(edge)
        if edge.from_ is edge.to:
            self._self_edges[edge.to].add(edge)

    def remove_node(self, node: Node):
        '''Remove a node from the graph.'''
        for dir in Direction:
            del self._adjacency[dir][node]
        del self._self_edges[node]

    def remove_edge(self, edge: Edge):
        '''Remove an edge from the graph.'''
        for dir in Direction:
            for node in edge.neighbors(dir.reverse()):
                self._adjacency[dir][node].remove(edge)
        if edge.from_ is edge.to:
            self._self_edges[edge.to].remove(edge)

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]:
        '''Get the edges that connect a node in the given direction.'''
        if direction is Direction.BOTH:
            return itertools.chain(self._adjacency[direction][node], self._self_edges[node])
        return self._adjacency[direction][node]

    def degree(self, direction: Direction, node: Node) -> int:
        '''
        Get the in-degree, out-degree, or total degree of the node, which is
        the number of edges connected to the node in that direction.
        '''
        if direction is Direction.BOTH:
            return len(self._adjacency[direction][node]) + len(self._self_edges[node])
        return len(self._adjacency[direction][node])
    
    # def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: raise NotImplementedError
    
    def nodes(self) -> collections.abc.KeysView[Node]:
        '''Get the nodes in the graph.'''
        return self._adjacency[Direction.OUT].keys()

    def edge_sets(self) -> collections.abc.ValuesView[set[Edge]]:
        '''Get the sets of edges from the adjacency set.'''
        return self._adjacency[Direction.OUT].values()
    
    def edges(self) -> Iterable[Edge]:
        '''Get the edges in the graph.'''
        return itertools.chain.from_iterable(self.edge_sets())

    def v(self) -> int:
        '''Get the number of nodes (vertices) in the graph.'''
        return len(self._adjacency[Direction.OUT])

    def e(self) -> int:
        '''Get the number of edges in the graph.'''
        return sum(map(len, self.edge_sets()))

    def __bool__(self) -> bool:
        '''A graph is false-y if it contains no nodes (and therefore no edges either).'''
        return bool(self.v())


class ElementSet(Graph):
    '''
    An element set simply keeps track of the nodes and edges that have been added
    via sets for each, and a set for both.

    This type of graph is best suited to answer whether a particular element is
    in the graph, getting the nodes and edges, and counting them.

    This graph is not suited for traversal, getting the degree of nodes, or finding
    the edges between two nodes.
    '''

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._nodes: set[Node] = set()
        self._edges: set[Edge] = set()
        self._elements: set[Node | Edge] = set()
        super().__init__(nodes, edges)

    def add_node(self, node: Node):
        '''Add a node to the graph.'''
        self._nodes.add(node)
        self._elements.add(node)

    def add_edge(self, edge: Edge):
        '''Add an edge to the graph.'''
        self._edges.add(edge)
        self._elements.add(edge)

    def remove_node(self, node: Node):
        '''Remove a node from the graph.'''
        self._nodes.remove(node)
        self._elements.remove(node)
        for edge in tuple(self._edges):
            if node in edge:
                self.remove_edge(edge)

    def remove_edge(self, edge: Edge):
        '''Remove an edge from the graph.'''
        self._edges.remove(edge)
        self._elements.remove(edge)

    # def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]: raise NotImplementedError
    # def degree(self, direction: Direction, node: Node) -> int: raise NotImplementedError
    # def edges_between(self, from_: Node, to: Node) -> Iterable[Edge]: raise NotImplementedError
    
    def nodes(self) -> set[Node]:
        '''Get the nodes of the graph.'''
        return self._nodes
    
    def edges(self) -> set[Edge]:
        '''Get the edges of the graph'''
        return self._edges

    def elements(self) -> set[Node | Edge]:
        '''Get a set containing both the nodes and edges of the graph.'''
        return self._elements

    def v(self) -> int:
        '''Get the number of nodes of the graph.'''
        return len(self._nodes)

    def e(self) -> int:
        '''Get the number of edges of the graph.'''
        return len(self._edges)

    def __bool__(self) -> bool:
        '''A graph is false-y if it contains no nodes (and therefore no edges either).'''
        return bool(self._elements)


class EdgeSearch(Graph):
    '''
    This is a specialized type of graph designed to answer which edges
    exist between two nodes. It is not suited for most other tasks.
    '''

    def __init__(self, nodes: Iterable[Node] = (), edges: Iterable[Edge] = ()):
        self._nodes = set(nodes)
        self._edges: dict[Direction, dict[Node, dict[Node, set[Edge]]]] \
            = [collections.defaultdict(lambda: collections.defaultdict(set)) for _ in Direction]
        super().__init__(nodes, edges)

    def add_node(self, node: Node):
        '''Add a node into the graph.'''
        self._nodes.add(node)

    def add_edge(self, edge: Edge):
        '''Add an edge into the graph.'''
        for dir in Direction:
            for node_1, node_2 in dir.orient(edge):
                self._edges[dir][node_1][node_2].add(edge)

    def remove_node(self, node: Node):
        '''Remove a node from the graph.'''
        self._nodes.remove(node)
        for dir in Direction:
            second_node_mapping = self._edges[dir].pop(node, ())
            if not second_node_mapping:
                continue
            for edge_set in second_node_mapping.values():
                utils.apply(self.remove_edge, edge_set)
            second_node_mapping.pop(node, None)

    def remove_edge(self, edge: Edge):
        '''Remove an edge from the graph.'''
        for dir in Direction:
            for node_1, node_2 in dir.orient(edge):
                self._edges[dir][node_1][node_2].remove(edge)

    def _neighbors(self, direction: Direction, node: Node) -> Iterable[Edge]:
        '''Get the edges that connect a node in the given direction.'''
        return itertools.chain.from_iterable(self._edges[direction][node].values())

    # def degree(self, direction: Direction, node: Node) -> int: raise NotImplementedError

    def edges_between(self, from_: Node, to: Node) -> set[Edge]:
        '''Get the edges that connect a node in the given direction.'''
        return self.edges[Direction.OUT][from_][to]

    def nodes(self) -> set[Node]:
        '''Get the nodes in the graph.'''
        return self._nodes
    
    def edges(self) -> Iterable[Edge]:
        '''Get the edges in the graph.'''
        return itertools.chain.from_iterable(
            itertools.chain.from_iterable(
                map(dict.values, self._edges[Direction.OUT].values())))

    def v(self) -> int:
        '''Get the number of nodes (vertices) of the graph.'''
        return len(self._nodes)

    # def e(self) -> int: raise NotImplementedError

    def __bool__(self) -> bool:
        '''A graph is false-y if it contains no nodes (and therefore no edges).'''
        return bool(self._nodes)
