import itertools

import pytest

from graph import *


@pytest.fixture
def elem() -> GraphElement:
    data = {'a': 1}
    return GraphElement(**data)

def test_properties(elem: GraphElement):
    assert elem.properties == {'a': 1}

def test_hash(elem: GraphElement):
    assert hash(elem) == hash(elem)


def test_subclass_attributes():
    data_1 = {'a': 1}
    node_1 = Node(data_1)
    assert node_1.data is data_1

    data_2 = {'b': 2}
    node_2 = Node(data_2)
    edge = Edge(node_1, node_2)
    assert edge.from_ is node_1
    assert edge.to is node_2
    assert edge.nodes == (node_1, node_2)

    w_edge = WeightedEdge(node_1, node_2, 3)
    assert w_edge.weight == 3


def test_eq():
    nodes = [Node([1, 2, 3]) for _ in range(3)]
    assert nodes[0] == nodes[1]
    edges = [Edge(*pair) for pair in itertools.pairwise(nodes)]
    assert edges[0] == edges[1]

def test_lt():
    assert Node(0) < Node(1)
