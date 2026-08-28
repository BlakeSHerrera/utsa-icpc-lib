
import itertools
from typing import Any, Iterable, Literal, Mapping, NamedTuple, Self, Sequence

import graph


class Point(NamedTuple):
    x: int
    y: int

    @staticmethod
    def from_rc(row: int, col: int) -> Self:
        return Point(col, row)

    @property
    def r(self) -> int:
        return self.y

    @property
    def c(self) -> int:
        return self.x

    @property
    def rc(self) -> tuple[int, int]:
        return (self.r, self.c)
    
    def __neg__(self) -> Self:
        '''This operation is equivalent to a 180 degree rotation.'''
        return Point(-self.x, -self.y)

    def __add__(self, other: Self) -> Self:
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int) -> Self:
        '''This operation dialates the point about the origin.'''
        return Point(self.x * other, self.y * other)

    def __rmul__(self, other: int) -> Self:
        return self * other

    def __invert__(self) -> Self:
            '''Mirror about the line y=x.'''
            return Point(self.y, self.x)
    
    def rotate(self, degrees: Literal[0, 90, 180, 270]) -> Self:
        '''
        This is a counterclockwise in the Cartesian coordinate (x, y) view.
        In a grid (row, col) view, this is a counterclockwise rotation.

        Both are mathematically equivalent. This happens because a grid
        view is a (y, x) view.
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
        '''May contain duplicates.'''
        return map(self.rotate, ROTATIONS)

    def rotate_eightfold(self) -> Iterable[Self]:
        '''Fourfold rotation and mirroring. May contain duplicates.'''
        return itertools.chain(
            self.rotate_fourfold(),
            (~self).rotate_fourfold())


ORIGIN = Point(0, 0)

ROTATIONS = range(0, 361, 90)

TAXICAB = tuple(Point(1, 0).rotate_fourfold())
DIAGONAL_ONLY = tuple(Point(1, 1).rotate_fourfold())
DIAGONAL_PLUS = TAXICAB + DIAGONAL_ONLY
KNIGHT = tuple(Point(2, 1).rotate_eightfold())


class GridNode(graph.Node):

    def __init__(self, data: Any, point: Point):
        super().__init__(data)
        self.point = point


class Grid(graph.Graph):

    def __init__(
        self, 
        index: graph.Graph,
        grid: Sequence[Sequence[GridNode]], 
        edges: Iterable[graph.Edge]
    ):
        super().__init__(index, itertools.chain.from_iterable(grid), edges)
        self.grid = grid

    @staticmethod
    def from_adjacency(
        index: graph.Graph,
        grid: Sequence[Sequence],
        adjacency: Iterable[Point],
    ) -> Self:
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
            if Grid.in_bounds(node_grid, to := node.point + delta):
                edges.append(graph.Edge(node, node_grid[to.r][to.c]))

        super().__init__(index, node_grid, edges)

    @staticmethod
    def in_bounds(grid: Sequence[Sequence], point: Point):
        return 0 <= point.r < len(grid) \
            and 0 <= point.c < len(grid[point.r])

    @staticmethod
    def parse_str(
        s: str,
        row_delimiter: str = '\n',
        col_delimiter: str = '',
    ) -> list[list[str]]:
        return [row.split(col_delimiter) for row in s.split(row_delimiter)]
    