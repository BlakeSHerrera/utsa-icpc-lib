'''
A grid is a special type of graph where the nodes belong to a lattice
beginning at coordinates (0, 0). It can be indexed like a matrix.
The nodes are typically connected to adjacent nodes (in a plus or
star shape), but they can also be connected in other ways such as
knight (2, 1) movements.

This module also contains helpers such as the point class to convert
between x/y and row/col coordinates since they are inverses of each other.
'''


import itertools
from typing import Any, Iterable, Literal, Mapping, NamedTuple, Self, Sequence

import graph


class Point(NamedTuple):
    '''A point represents integer coordinates on a lattice.'''

    x: int
    y: int

    @staticmethod
    def from_rc(row: int, col: int) -> Self:
        '''Create a point from row/col coordinates rather than Cartesian (x/y) coordinates.'''
        return Point(col, row)

    @property
    def r(self) -> int:
        '''The row index, equivalent to the y value.'''
        return self.y

    @property
    def c(self) -> int:
        '''The column index, equivalent to the x value.'''
        return self.x

    @property
    def rc(self) -> tuple[int, int]:
        '''The row and column indices as a tuple of 2 integers.'''
        return (self.r, self.c)
    
    def __neg__(self) -> Self:
        '''
        Perform a vectorized negation of the point, returning a new point. 
        This operation is equivalent to a 180 degree rotation about the origin.
        '''
        return Point(-self.x, -self.y)

    def __add__(self, other: Self) -> Self:
        '''Perform a vectorized addition of the two points, returning a new point.'''
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        '''Perform a vectorized subtraction of the two points, returning a new point.'''
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int) -> Self:
        '''
        Perform a vectorized multiplication of the point with a scalar value, returning a new point.
        This operation is equivalent to dilating the point about the origin.
        '''
        return Point(self.x * other, self.y * other)

    def __rmul__(self, other: int) -> Self:
        '''
        Perform a vectorized multiplication of the point with a scalar value, returning a new point.
        This operation is equivalent to dilating the point about the origin.
        '''
        return self * other

    def __invert__(self) -> Self:
        '''Mirror the point about the line y=x (swapping the values), returning a new point.'''
        return Point(self.y, self.x)
    
    def rotate(self, degrees: Literal[0, 90, 180, 270]) -> Self:
        '''
        This is a counterclockwise in the Cartesian coordinate (x, y) view.
        In a grid (row, col) view, this is a counterclockwise rotation.

        Both are mathematically equivalent. This happens because a grid's
        (r, c) view is a (y, x) view.
        '''
        match degrees:
            case 0:
                return self
            case 90:
                return Point(-self.y, self.x)
            case 180:
                return -self
            case 270:
                return Point(self.y, -self.x)

    def rotate_fourfold(self) -> Mapping[int, Self]:
        '''
        Perform four rotations of 0, 90, 180, and 270 degrees, returning new points.
        This operation may produce duplicate values.
        '''
        return map(self.rotate, ROTATIONS)

    def rotate_eightfold(self) -> Iterable[Self]:
        '''
        Perform four rotations of 0, 90, 180, and 270 degrees, and additionally mirror
        those points, returning 8 new points. This operation may produce duplicate values.
        '''
        return itertools.chain(
            self.rotate_fourfold(),
            (~self).rotate_fourfold())


ORIGIN = Point(0, 0)

ROTATIONS = set(range(0, 360, 90))

TAXICAB = set(Point(1, 0).rotate_fourfold())
DIAGONAL = set(Point(1, 1).rotate_fourfold())
ADJACENT = TAXICAB | DIAGONAL
KNIGHT = set(Point(2, 1).rotate_eightfold())
SELF_VISIT = {ORIGIN}


class GridNode(graph.Node):
    '''A grid node is a node which also has a reference to its grid coordinates.'''

    def __init__(self, data: Any, point: Point):
        super().__init__(data)
        self.point = point


class GridView(graph.GraphView):
    '''
    The immutable view of the grid. 

    Note that there are no mutable grid implementations.
    
    Also note that a grid can be ragged and not rectangular. What matters is that
    the coordinate system is rectangular.
    '''

    def __init__(
        self, 
        backend: graph.Graph,
        grid: Sequence[Sequence[GridNode]], 
        edges: Iterable[graph.Edge]
    ):
        super().__init__(backend)
        backend.add_all(itertools.chain.from_iterable(grid), edges)
        self._grid = grid

    @staticmethod
    def from_adjacency(
        backend: graph.Graph,
        grid: Sequence[Sequence],
        adjacency: Iterable[Point],
    ) -> Self:
        '''Create a grid object from a matrix and adjacency connection rules.'''

        adjacency = tuple(adjacency)

        node_grid = list()
        for r in range(len(grid)):
            node_grid.append(list())
            for c in range(len(grid[r])):
                node = GridNode(grid[r][c], Point.from_rc(r, c))
                node_grid[-1].append(node)

        edges = list()
        for node, delta in itertools.product(itertools.chain.from_iterable(node_grid), adjacency):
            node: GridNode
            if GridView.in_bounds(node_grid, to := node.point + delta):
                edges.append(graph.Edge(node, node_grid[to.r][to.c]))

        return GridView(backend, node_grid, edges)

    @staticmethod
    def in_bounds(grid: Sequence[Sequence], point: Point) -> bool:
        '''Return whether or not the point lies within the grid's bounds.'''
        return 0 <= point.r < len(grid) \
            and 0 <= point.c < len(grid[point.r])
