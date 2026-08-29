
import collections

from grid import *

import pytest

import testutils


X = C = 2
Y = R = 3
X2 = 11
Y2 = 17

@pytest.fixture
def point_xy() -> Point:
    return Point(X, Y)

@pytest.fixture
def point_rc() -> Point:
    return Point.from_rc(R, C)

@testutils.fixtures(point_xy, point_rc)
def point() -> Point:
    ...

@pytest.fixture
def point_2() -> Point:
    return Point(X2, Y2)


def test_point_xy_rc(point: Point):
    assert point.x == X
    assert point.y == Y
    assert point.r == R
    assert point.c == C
    assert point == point
    assert point == point.rc[::-1]

def test_neg(point: Point):
    p = -point
    assert p is not point
    assert p == (-X, -Y)

def test_add(point: Point, point_2: Point):
    p = point + point_2
    assert point == (X, Y)
    assert point_2 == (X2, Y2)
    assert p == (point.x + point_2.x, point.y + point_2.y)
    
def test_sub(point: Point, point_2: Point):
    p = point - point_2
    assert point == (X, Y)
    assert point_2 == (X2, Y2)
    assert p == (point.x - point_2.x, point.y - point_2.y)

def test_mul(point: Point):
    F = 101
    for p in (point * F, F * point):
        assert point == (X, Y)
        assert p == (point.x * F, point.y * F)

def test_invert(point: Point):
    p = ~point
    assert point == (X, Y)
    assert p == (point.y, point.x)

def test_rotations(point: Point):
    point.rotate(90)
    assert point == (X, Y)

    assert list(ROTATIONS) == [0, 90, 180, 270]
    fourfold = list(map(point.rotate, ROTATIONS))
    assert fourfold[0] == (X, Y)
    assert fourfold[1] == (-Y, X)
    assert fourfold[2] == (-X, -Y)
    assert fourfold[3] == (Y, -X)
    assert collections.Counter(fourfold) == collections.Counter(point.rotate_fourfold())

    mirrored = [~p for p in fourfold]
    eightfold = collections.Counter(mirrored + fourfold)
    assert eightfold == collections.Counter(point.rotate_eightfold())


def test_constants():
    assert ROTATIONS == {0, 90, 180, 270}
    assert ORIGIN == (0, 0)
    assert TAXICAB == {(0, 1), (1, 0), (0, -1), (-1, 0)}
    assert DIAGONAL == {(1, 1), (1, -1), (-1, 1), (-1, -1)}
    assert ADJACENT == TAXICAB | DIAGONAL
    assert KNIGHT == {(2, 1), (1, 2), (2, -1), (-1, 2), (-2, 1), (1, -2), (-2, -1), (-1, -2)}
    assert SELF_VISIT == {(0, 0)}


def test_grid_in_bounds():
    # The grid is allowed to be ragged.
    grid = [
        [0],
        [1, 2],
    ]
    for expected, r, c in [
        (True, 0, 0),
        (False, 0, 1),
        (True, 1, 0),
        (True, 1, 1),
        (False, 1, 2),
        (False, 2, 0),
        (False, 0, -1),
        (False, -1, 0),
        (False, -1, -1),
    ]:
        assert Grid.in_bounds(grid, Point.from_rc(r, c)) == expected


def test_grid_from_adjacency():
    grid: Grid = Grid.from_adjacency(
        graph.AdjacencySet(),
        ['123', '456', '789'],
        KNIGHT
    )
    nodes = set(range(1, 10))
    edges = {
        (1, 6), (1, 8),
        (2, 7), (2, 9),
        (3, 4), (3, 8),
        (4, 3), (4, 9),
        (6, 1), (6, 7),
        (7, 2), (7, 6),
        (8, 1), (8, 3),
        (9, 2), (9, 4),
    }
    for edge in grid.edges():
        edges.remove((
            int(edge.from_.data), 
            int(edge.to.data)))
    assert not edges
    for node in grid.nodes():
        nodes.remove(int(node.data))
    assert not nodes
    