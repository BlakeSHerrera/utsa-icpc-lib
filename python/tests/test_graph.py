import dataclasses
import itertools

import pytest

from graph import *
import testutils


def test_attributes():
    data_1 = {'a': 1}
    node_1 = Node(data_1)
    assert node_1.data is data_1

    data_2 = {'b': 2}
    node_2 = Node(data_2)
    edge = Edge(node_1, node_2)
    assert edge.from_ is node_1
    assert edge.to is node_2
    assert edge.nodes == (node_1, node_2)
    assert edge.nodes_r == (node_2, node_1)


def test_edge_in():
    edge = Edge(Node(1), Node(2))
    assert edge.to in edge
    assert edge.from_ in edge


def test_edge_neighbors():
    node_1 = Node(1)
    node_2 = Node(2)
    edge = Edge(node_1, node_2)
    for dir, result in [
        (Direction.OUT, {edge.to}),
        (Direction.IN, {edge.from_}),
        (Direction.BOTH, {edge.from_, edge.to})
    ]:
        assert set(edge.neighbors(dir)) == result

def test_direction():
    assert Direction.OUT.reverse() is Direction.IN
    assert Direction.IN.reverse() is Direction.OUT
    assert Direction.BOTH.reverse() is Direction.BOTH


def test_direction_orient():
    node_1 = Node(1)
    node_2 = Node(2)
    edge = Edge(node_1, node_2)
    for dir, result in [
        (Direction.OUT, {edge.nodes}),
        (Direction.IN, {edge.nodes_r}),
        (Direction.BOTH, {edge.nodes, edge.nodes_r})
    ]:
        assert set(dir.orient(edge)) == result


def test_simple_edge():
    e1 = SimpleEdge(n1 := Node(1), n2 := Node(2))
    e2 = SimpleEdge(n1, n2)
    e3 = SimpleEdge(n2, n1)
    assert e1 == e2
    assert e1 != e3
    assert hash(e1) == hash(e2)
    assert hash(e1) != hash(e3)


@dataclasses.dataclass
class GraphDefinition:
    nodes: list[Node]
    edges: list[Edge]

    def add_to(self, graph: MutableGraph):
        graph.add_all(self.nodes, self.edges)

    def remove_from(self, graph: MutableGraph):
        for edge in self.edges:
            graph.remove_edge(edge)
        for node in self.nodes:
            graph.remove_node(node)

    def add_and_remove(self, graph: MutableGraph):
        self.add_to(graph)
        self.remove_from(graph)


N = 1

@pytest.fixture
def elements() -> GraphDefinition:
    nodes = list(map(Node, range(N)))
    edges = list(itertools.starmap(Edge, itertools.pairwise(nodes)))
    return GraphDefinition(nodes, edges)

@pytest.fixture
def extra_elements() -> GraphDefinition:
    nodes = list(map(Node, range(N, 2 * N)))
    edges = list(itertools.starmap(Edge, itertools.pairwise(nodes)))
    return GraphDefinition(nodes, edges)

def test_lax_graph(elements: GraphDefinition):
    class G(LaxGraph): pass
    g = G()
    elements.add_to(g)
    elements.remove_from(g)


@pytest.fixture
def adjacency_set_constructor(elements: GraphDefinition) -> AdjacencySet:
    return AdjacencySet(elements.nodes, elements.edges)

@pytest.fixture
def element_set_constructor(elements: GraphDefinition) -> ElementSet:
    return ElementSet(elements.nodes, elements.edges)

@pytest.fixture
def edge_search_constructor(elements: GraphDefinition) -> EdgeSearch:
    return EdgeSearch(elements.nodes, elements.edges)

@pytest.fixture
def adjacency_set_mutated(adjacency_set_constructor: AdjacencySet, extra_elements: GraphDefinition) -> AdjacencySet:
    extra_elements.add_and_remove(adjacency_set_constructor)
    return adjacency_set_constructor

@pytest.fixture
def element_set_mutated(element_set_constructor: ElementSet, extra_elements: GraphDefinition) -> ElementSet:
    extra_elements.add_and_remove(element_set_constructor)
    return element_set_constructor

@pytest.fixture
def edge_search_mutated(edge_search_constructor: EdgeSearch, extra_elements: GraphDefinition) -> EdgeSearch:
    extra_elements.add_and_remove(edge_search_constructor)
    return edge_search_constructor

@pytest.fixture
def adjacency_set_empty() -> AdjacencySet:
    return AdjacencySet()

@pytest.fixture
def element_set_empty() -> ElementSet:
    return ElementSet()

@pytest.fixture
def edge_search_empty() -> EdgeSearch:
    return ElementSet()

@testutils.fixtures(adjacency_set_constructor, adjacency_set_mutated)
def adjacency_set() -> AdjacencySet:
    ...

@testutils.fixtures(element_set_constructor, element_set_mutated)
def element_set() -> ElementSet:
    ...

@testutils.fixtures(edge_search_constructor, edge_search_mutated)
def edge_search() -> EdgeSearch:
    ...

@testutils.fixtures(adjacency_set_empty, element_set_empty, edge_search_empty)
def empty_graph() -> MutableGraph:
    ...
    
@testutils.fixtures(*adjacency_set.fixtures, *element_set.fixtures, *edge_search.fixtures)
def graph() -> MutableGraph:
    ...

def test_graph_nodes(graph: MutableGraph, elements: GraphDefinition):
    try: assert set(graph.nodes()) == set(elements.nodes)
    except NotImplementedError: pass

def test_graph_edges(graph: MutableGraph, elements: GraphDefinition):
    try: assert set(graph.edges()) == set(elements.edges)
    except NotImplementedError: pass

def test_graph_v(graph: MutableGraph, elements: GraphDefinition):
    try: assert graph.v() == len(elements.nodes)
    except NotImplementedError: pass

def test_graph_e(graph: MutableGraph, elements: GraphDefinition):
    try: assert graph.e() == len(elements.edges)
    except NotImplementedError: pass

def test_graph_bool(graph: MutableGraph, elements: GraphDefinition):
    assert bool(graph) == bool(elements.nodes + elements.edges)
    elements.remove_from(graph)
    assert not bool(graph)

def test_graph_degree(graph: MutableGraph, elements: GraphDefinition):
    for node in elements.nodes:
        graph.add_edge(Edge(node, node))  # Self-edges are an edge case due to potential confusion
        graph.add_edge(Edge(node, node))  # Also test for multi-edges
        count_in = 2 + sum(edge.to is node for edge in elements.edges)
        count_out = 2 + sum(edge.from_ is node for edge in elements.edges)
        for dir, expected in [
            (Direction.IN, count_in),
            (Direction.OUT, count_out),
            (Direction.BOTH, count_in + count_out)
        ]:
            try: assert graph.degree(dir, node) == expected, f'Dir {dir} Elements are {elements.edges}'
            except NotImplementedError: pass

def test_edges_between(graph: MutableGraph, elements: GraphDefinition):
    index: dict[tuple[Node, Node], set[Edge]] = collections.defaultdict(set)
    for edge in elements.edges:
        index[edge.nodes].add(edge)
    try:
        for node_pair in itertools.pairwise(itertools.permutations(elements.nodes, r = 2)):
            assert set(graph.edges_between(*node_pair)) == index[node_pair]
    except NotImplementedError:
        pass

def test_neighbors(graph: MutableGraph, elements: GraphDefinition):
    neighbors: dict[Direction, dict[Node | Edge, list[Node | Edge]]] \
        = collections.defaultdict(lambda: collections.defaultdict(list))
    for edge, dir in itertools.product(elements.edges, Direction):
        for neighbor, neighbor_r in zip(edge.neighbors(dir), edge.neighbors(~dir)):
            neighbors[dir][edge].append(neighbor)
            neighbors[dir][neighbor_r].append(edge)
    for element, dir in itertools.product(elements.nodes + elements.edges, Direction):
        expected = collections.Counter(neighbors[dir][element])
        if isinstance(element, Node):
            try: assert collections.Counter(graph._neighbors(dir, element)) == expected
            except NotImplementedError: pass
        try: assert collections.Counter(graph.neighbors(dir, element)) == expected
        except NotImplementedError: pass


def test_composite_graph(elements: GraphDefinition):
    comp = CompositeGraph(
        adj := AdjacencySet(), 
        eset := ElementSet(), 
        nodes = (nodes := set(elements.nodes)), 
        edges = (edges := set(elements.edges)))
    assert set(adj.nodes()) == nodes
    assert set(adj.edges()) == edges
    assert adj == eset
    
    comp.add_node(n1 := Node(1))
    comp.add_node(n2 := Node(2))
    assert set(adj.nodes()) == nodes | {n1, n2}
    assert adj == eset

    comp.add_edge(e := Edge(n1, n2))
    assert set(adj.edges()) == edges | {e}
    assert adj == eset

    comp.remove_edge(e)
    assert set(adj.edges()) == edges
    assert adj == eset

    comp.remove_node(n1)
    comp.remove_node(n2)
    assert set(adj.nodes()) == nodes
    assert adj == eset
