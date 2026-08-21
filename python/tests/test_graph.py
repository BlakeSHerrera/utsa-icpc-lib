
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

def test_getitem(elem: GraphElement):
    assert elem['a'] == 1
    with pytest.raises(KeyError):
        elem['b']

def test_get(elem: GraphElement):
    assert elem.get('a') == 1
    assert elem.get('b') == None
    assert elem.get('b', 2) == 2

def test_contains(elem: GraphElement):
    assert 'a' in elem
    assert 'b' not in elem


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
