import itertools

import pytest

from graph import *


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

    w_edge = WeightedEdge(node_1, node_2, 3)
    assert w_edge.weight == 3


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
