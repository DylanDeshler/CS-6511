from abc import ABC, abstractmethod
from collections import defaultdict

import numpy as np

from enum import Enum

class Shape(Enum):
    FULL_BLOCK = 0
    OUTER_BOUNDARY = 1
    EL_SHAPE = 2

class Tile(ABC):
    def __init__(self, mask):
        self.mask = mask
    
    # @abstractmethod
    # def condition(self, i, j):
        ...
    
    # def can_cover(self, index, landscape, targets):
    #     row = (index * 4) % landscape.size
    #     col = (index * 4) // landscape.size
    #     covering = defaultdict(int)
    #     for i in range(4):
    #         for j in range(4):
    #             for bush, count in targets.items():
    #                 if landscape.visible_bushes[bush] - covering[bush] < count:
    #                     return False, None
    #             if self.condition(i, j):
    #                 covering[landscape.bushes[row + i][col + j]] += 1
    #     return True, covering

class FullTile(Tile):
    def __init__(self):
        super().__init__(np.asarray([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]))
        self.shape = Shape.FULL_BLOCK
    
    # def condition(self, i, j):
    #     return True

class OuterBoundaryTile(Tile):
    def __init__(self):
        super().__init__(np.asarray([[1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 1]]))
        self.shape = Shape.OUTER_BOUNDARY
    
    # def condition(self, i, j):
    #     return i == 0 or i == 3 or j == 0 or j == 3

class ELTile(Tile):
    def __init__(self, mask):
        super().__init__(mask)
        self.shape = Shape.EL_SHAPE

class LeftBottomTile(ELTile):
    def __init__(self):
        super().__init__(np.asarray([[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 1, 1]]))

    # def condition(self, i, j):
    #     return (j == 0 and (i == 0 or i == 1 or i == 2)) or (i == 3 and (j == 0 or j == 1 or j == 2 or j == 3))

class RightBottomTile(ELTile):
    def __init__(self):
        super().__init__(np.asarray([[0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1], [1, 1, 1, 1]]))
    
    # def condition(self, i, j):
    #     return (j == 3 and (i == 0 or i == 1 or i == 2)) or (i == 3 and (j == 0 or j == 1 or j == 2 or j == 3))

class LeftTopTile(ELTile):
    def __init__(self):
        super().__init__(np.asarray([[1, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]]))

    # def condition(self, i, j):
    #     return (j == 0 and (i == 0 or i == 1 or i == 2 or i == 3)) or (i == 0 and (j == 0 or j == 1 or j == 2 or j == 3))

class RightTopTile(ELTile):
    def __init__(self):
        super().__init__(np.asarray([[1, 1, 1, 1], [0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1]]))
    
    # def condition(self, i, j):
    #     return (j == 3 and (i == 0 or i == 1 or i == 2 or i == 3)) or (i == 0 and (j == 0 or j == 1 or j == 2 or j == 3))