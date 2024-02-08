import math
import heapq
from functools import reduce
import numpy as np
import time
import sys
import os

def is_goal(current_state, goal):
    """
    current_state: a list of the current state values
    goal: the target state amount

    Returns True if the current state is the goal state, false otherwise.
    The goal state is when the first jug is at the desired amount
    """

    return current_state[0] == goal

def is_solvable(capacities, goal):
    """
    capacities: a list of the maximum value permitted for each element in the state (aka water jug)
    goal: the target state amount

    Returns True when the problem is solvable and false otherwise.
    Because our problem is a Diophantine equation, the gcd of our capacities deviding the goal is a nessecary and sufficient condition 
    """
    return goal % reduce(math.gcd, capacities[1:]) == 0

def heuristic(current_state, capacities, goal):
    """
    current_state: a list of the current state values
    capacities: a list of the maximum value permitted for each element in the state (aka water jug)
    goal: the target state amount

    We calculate and return the heuristic for a given state
    """
   
    # We've found the goal
    if is_goal(current_state, goal):
        return 0

    # If we're one step from the goal
    for index in range(1, len(capacities)):
        if goal == current_state[0] + current_state[index]:
            return 1 / goal

    # Helper definitions for the heuristic calculation
    current_distance = goal - current_state[0]
    next_distance = abs(goal - current_state[0] - max(current_state[1:]))
    
    # If we're two steps from the goal
    for capacity in capacities[1:]:
        if goal == current_state[0] + max(current_state[1:]) + capacity:
            return (current_distance + next_distance) / 2 / goal

    # Make a best guess of distance to the goal using the calculated next step
    # Using next_distance maintains admissable and consistent (I get non-optimal results otherwise)
    return (current_distance + next_distance) / goal

def generate_successors(current_state, capacities):
    """
    current_state: a list of the current state values
    capacities: a list of the maximum value permitted for each element in the state (aka water jug)

    Here we generate the children for the current state, enumerating every possible action
    """

    def update(current_state, i, delta_i, j, delta_j):
        """
        current_state: a list of the current state values
        i: index of 1st element to update
        delta_i: amount to add to the ith element
        j: index of 2nd element to update
        delta_j: amount to add to the jth element

        Helper function for updating states
        """
        child = list(current_state)
        child[i] += delta_i
        child[j] += delta_j
        return tuple(child)
    
    children = []
    for i, water_amount in enumerate(current_state):

        # Fill fully from the tap if not the goal jug
        if water_amount == 0 and i > 0:
            children.append(update(current_state, i, capacities[i], 0, 0))
            
        # Dump the water on the ground
        children.append(update(current_state, i, -water_amount, 0, 0))
        
        # Each jug can pour into any other
        for j, other_amount in enumerate(current_state):
            # Don't our into yourself
            if i == j:
                continue
             
            # Pour what you can from one jug into another
            delta = min(water_amount, capacities[j] - other_amount)
            children.append(update(current_state, i, -delta, j, delta))
    
    return children

def search(capacities, goal):
    """
    capacities: a list of the maximum value permitted for each element in the state (aka water jug)
    goal: the desired state (aka amount of water needed in the fist jug)

    Here we run the A* Search algorithm to find the shortest path from the intial state to our goal state
    I.e. the shortest amount of steps to fill our jug to the desired amount
    """
    if not is_solvable(capacities, goal):
        return -1

    initial_state =  [0] * len(capacities)
    frontier = [(heuristic(initial_state, capacities, goal), 0, initial_state)]
    closed = set()
    
    while frontier:
        _, current_cost, current_state = heapq.heappop(frontier)
        # print(current_state)
        # input()
        
        # problem is symmetrical to this, helps discount a lot of states and speed up
        if current_state[0] > goal:
            continue

        # don't search the same state twice
        if tuple(current_state) in closed:
            continue
        
        # woo we found the goal!
        if is_goal(current_state, goal):
            return current_cost
        
        while frontier:
            _ = heapq.heappop(frontier)

        # populate with child states
        closed.add(tuple(current_state))
        for next_state in generate_successors(current_state, capacities):
            total_cost = current_cost + 1 + heuristic(next_state, capacities, goal)
            heapq.heappush(frontier, (total_cost, current_cost + 1 , next_state))

    # no goal found
    return -1

def generate_test_cases(n_states, low=1, high=200):
    """
    n_states: integer defining the number of non-goal states for the problem to have
    low: lower bound for capacities
    high: upper bound for capacities

    Generates random test cases
    """
    capacities = [int(1e9)] + np.random.random_integers(low, high, size=n_states).tolist()
    goal = np.random.randint(low, high) * reduce(math.gcd, capacities[1:])

    return capacities, goal

if __name__ == '__main__':
    # Random test cases
    if sys.argv[1] == 'random':
        for i in range(1, 10):
            print('________________________________________________________________')
            print(f'{i} non-goal states')
            times = []
            for _ in range(10):
                capacities, goal_states = generate_test_cases(i)

                print(goal_states, ' | ', capacities)
                t0 = time.time()
                path = search(capacities, goal_states)
                t1 = time.time()
                times.append(t1 - t0)
                if path == -1:
                    print('We made an error, all generated test cases shoudl be solvable')
                else:
                    print(f'Optimal path is of length {path} in {t1 - t0} seconds')
            
            print(f'Average time taken: {np.mean(times)}')

    else:
        path = sys.argv[1]
        assert os.path.exists(path), f'path {path} must exist and point to a suitable test case (make sure there are no spaces or illegal characters in the path)'

        with open(path) as f:
            lines = f.readlines()
            capacities = [int(1e9)] + [int(i) for i in lines[0].split(',')]
            goal_states = int(lines[1])

            t0 = time.time()
            path = search(capacities, goal_states)
            t1 = time.time()

            if path == -1:
                print('No path found')
            else:
                print(f'Optimal path is of length {path} in {t1 - t0} seconds')
