from csp_framework import Constraint, CSP
from typing import NamedTuple, Dict, List, Optional

from tiles import *

import numpy as np

class GridLocation(NamedTuple):
    row: int
    column: int

class ShapeConstraint(Constraint[GridLocation, Tile]):
    def __init__(self, variables: List[GridLocation], shape_targets: Dict[Shape, int]) -> None:
        super().__init__(variables)
        # self.variables: List[GridLocation] = variables
        self.shape_targets: Dict[Shape, int] = shape_targets
    
    def satisfied(self, assignment: Dict[GridLocation, Tile]) -> bool:
        counts = defaultdict(int)
        for tile in assignment.values():
            counts[tile.shape] += 1
        
        for k, v in self.shape_targets.items():
            if counts[k] > v:
                return False
        return True

class BushConstraint(Constraint[GridLocation, Tile]):
    def __init__(self, variables: List[GridLocation], bushes: Dict[GridLocation, List[int]], bush_targets: Dict[int, int]) -> None:
        super().__init__(variables)
        self.bushes: Dict[GridLocation, List[int]] = bushes
        self.bush_targets: Dict[int, int] = bush_targets
        self.max_bushes: Dict[int, int] = {}
        for i in range(1, 5):
            sum = 0
            for value in bushes.values():
                sum += np.count_nonzero(value == i)
            self.max_bushes[i] = sum
    
    def satisfied(self, assignment: Dict[GridLocation, Tile]) -> bool:
        counts = defaultdict(int)
        for location, tile in assignment.items():
            hidden = self.bushes[location] * tile.mask
            for bush in range(1, 5):
                counts[bush] += np.count_nonzero(hidden == bush)
        
        for k, v in self.bush_targets.items():
            if self.max_bushes[k] - counts[k] < v:
                return False
        return True

# def AC3(csp):
#     queue = list(csp.binary_constraints)

#     while queue:
#         (xi, xj) = queue.pop(0)

#         if remove_inconsistent_values(csp, xi, xj):
#             if len(csp.domains[xi]) == 0:
#                 return False
            
#             for Xk in csp.related
    
#     return True

def AC3(csp):
    queue = set(csp.variables)

    while len(queue) > 0:
        element = queue.pop()
        element_values = csp.domains[element]

        # get all related variables with set values (initially none)
        # r_all = set(csp.related_variables[element])
        r_all = set([var for var in csp.variables])

        changed = False

        for related in r_all:
            if element not in csp.variables:
                continue

            value = csp.domains[related]

            if value in element_values:
                csp.domains[element].remove(value)

                if len(csp.domains[element]) == 1:
                    pass



        # Update domains
        if changed:
            related_unfinished = [r_element for r_element in r_all if r_element in csp.variables]
            for item in related_unfinished:
                queue.add(item)

if __name__ == '__main__':
    # variable: (row, col)
    # domain: tile
    from read_csp import read
    bushes, shape_targets, size, bush_targets, solution = read(r"C:\Users\ddeshler\Desktop\ai\project2\input\tilesproblem_1327003805972500.txt")
    bushes = np.asarray(bushes)
    print(type(bushes), type(shape_targets), type(size), type(bush_targets), type(solution))
    print(bushes.shape)
    print(shape_targets)
    print(bush_targets)

    tiles = [FullTile, OuterBoundaryTile, LeftTopTile, RightTopTile, LeftBottomTile, RightBottomTile]
    locations = []
    tile_dict = {}
    bush_dict = {}
    for y in range(size // 4):
        for x in range(size // 4):
            location = GridLocation(y, x)
            locations.append(location)
            tile_dict[location] = [tile() for tile in tiles]
            bush_dict[location] = bushes[y*4:(y+1)*4, x*4:(x+1)*4]
    
    csp: CSP[GridLocation, Tile] = CSP(locations, tile_dict)
    csp.add_constraint(ShapeConstraint(locations, shape_targets))
    csp.add_constraint(BushConstraint(locations, bush_dict, bush_targets))

    solution: Optional[Dict[GridLocation, Tile]] = csp.backtracking_search(bush_dict, bush_targets, shape_targets)
    if solution is None:
        print('No solution found')
    else:
        print('Found solution: \n', solution.values())
        csp.display_assignment(size, bush_dict, solution)

