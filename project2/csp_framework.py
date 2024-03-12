from typing import Generic, TypeVar, Dict, List, Optional
from abc import ABC, abstractmethod
from collections import defaultdict

from tiles import Shape
import numpy as np

V = TypeVar('V')
D = TypeVar('D')

class Constraint(Generic[V, D], ABC):
    def __init__(self, variables: List[V]) -> None:
        self.variables = variables
    
    @abstractmethod
    def satisfied(self, assignment: Dict[V, D]) -> bool:
        ...

class CSP(Generic[V, D]):
    def __init__(self, variables: List[V], domains: Dict[V, List[D]]) -> None:
        self.variables: List[V] = variables
        self.domains: Dict[V, List[D]] = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}

        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it")
    
    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)
    
    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True
    
    def most_constrained_variable(self, assignment: Dict[V, D]) -> V:
        """
        Calculate the most constrained variable as the one with the smallest domain

        assignmet: Dict[V, D] - the current local assignment of V -> D
        """
        unassigned: List[V] = []

        for variable in self.variables:
            if variable not in assignment:
                unassigned.append(variable)
        
        # Attempting to use inverse constraint as a proxy for degree (makes things worse)
        # criterion = lambda variable: (len(self.domains[variable]), sum([self.constraining(bushes[variable], domain) for domain in self.domains[variable]]))
        criterion = lambda variable: len(self.domains[variable])
        return min(unassigned, key=criterion)
    
    def constraining(self, bushes: List[int], domain: D,) -> int:
        """
        Calculate a proxy for how constraining a V -> D assignment is

        bushes: List[int] - the bushes in the corresponding grid location
        domain: D - a possible tile

        returns: int - proxy for how constraining a domain assignment is
        """

        # We calculate which bushes will be visible after the tile is palced
        visible = bushes * (1 - domain.mask)
        # Then calculate the total
        return np.count_nonzero(visible)
  
    def least_constraining_value(self, variable: V, bushes: Dict[V, List[int]]) -> List[D]:
        """
        Calculate the least constraining value for a given variable

        variable: V - the variable to find the least constraining value for
        bushes: Dict[V, List[int]] - the initial bushes for all grid locations

        returns: List[D] - domains sorted by least constraining value
        """

        # No sorting is needed
        if len(self.domains[variable]) == 1:
            return self.domains[variable]

        criterion = lambda value: self.constraining(bushes[variable], value)
        return sorted(self.domains[variable], key=criterion)

    def matches_target(self, assignment: Dict[V, D], bushes: Dict[V, List[int]], bush_targets: Dict[int, int], shape_targets: Dict[Shape, int]) -> bool:
        """
        Determine if an assignment is a valid solution

        assignmet: Dict[V, D] - the current local assignment of V -> D
        bushes: Dict[V, List[int]] - the initial bushes for all grid locations
        bush_targets: Dict[int, int] - for a given bush type, how many need to be visible
        shape_targets: Dict[Shape, int] - for a given tile shape, how many must be placed

        returns: bool - True if solution is valid, False otherwise
        """
        bush_counts = defaultdict(int)
        shape_counts = defaultdict(int)

        for k, v in assignment.items():
            shape_counts[v.shape] += 1
            
            visible = bushes[k] * (1 - v.mask)
            for i in range(1, 5):
                bush_counts[i] += np.count_nonzero(visible == i)

        return bush_counts == bush_targets and shape_counts == shape_targets
    
    def display_assignment(self, size: int, bushes: Dict[V, List[int]], assignment: Dict[V, D]):
        """
        Display an assignment with its bush count

        size: int - the size of the landsacpe
        bushes: Dict[V, List[int]] - the initial bushes for all grid locations
        assignmet: Dict[V, D] - the current local assignment of V -> D
        """
        final = np.zeros((size, size), dtype=int)
        for k, v in assignment.items():
            final[k.row*4:(k.row+1)*4, k.column*4:(k.column+1)*4] = bushes[k] * (1 - v.mask)
        print([np.count_nonzero(final == i) for i in range(1, 5)])
        print(final)
    
    def backtracking_search(self, bushes: Dict[V, List[int]], bush_targets: Dict[int, int], shape_targets: Dict[Shape, int], assignment: Dict[V, D] = {}) -> Optional[Dict[V, D]]:
        """
        Determine if an assignment is a valid solution

        bushes: Dict[V, List[int]] - the initial bushes for all grid locations
        bush_targets: Dict[int, int] - for a given bush type, how many need to be visible
        shape_targets: Dict[Shape, int] - for a given tile shape, how many must be placed
        assignmet: Dict[V, D] - the current local assignment of V -> D

        returns: Optional[Dict[V, D]] - the solution if one exists, otherwise None
        """
        if len(assignment) == len(self.variables):
            if self.matches_target(assignment, bushes, bush_targets, shape_targets):
                return assignment
            return None

        # MCV
        first: V = self.most_constrained_variable(assignment)

        # LCV
        for value in self.least_constraining_value(first, bushes):
            local_assignment = assignment.copy()
            local_assignment[first] = value
            
            # If the value is consistent add it to the local assignment and continue searching
            if self.consistent(first, local_assignment):
                result: Optional[Dict[V, D]] = self.backtracking_search(bushes, bush_targets, shape_targets, local_assignment)

                # If we found a solution return it
                if result is not None:
                    return result
            
            # There was an issue with the value
            # local assignment loses scope (and so reverts to previous state) and we continue searching
        
        # No solution found
        return None