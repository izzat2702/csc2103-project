"""
tsp_algorithms.py
-----------------
Core algorithmic logic for the Travelling Salesman Problem (TSP).

CSC2103 Group Project - Problem 3: Heuristic Algorithms

Every algorithm here is implemented manually. No built-in or library-provided
algorithmic solution is used for the core task:

  * distances come from the Euclidean formula written out by hand;
  * the nearest-neighbour step is an explicit linear scan, not min() or sorted();
  * the 2-opt segment reversal is a manual two-pointer swap loop;
  * the exhaustive validator uses our own recursive permutation generator,
    NOT itertools.permutations().

The only import is math.sqrt, which is plain arithmetic rather than an algorithm.
"""

import math

# Exhaustive search runs in factorial time, so it is only offered for tiny
# instances. 10 cities => 9! = 362,880 candidate tours (a few seconds in Python).
# Anything larger is exactly why a heuristic is needed in the first place.
BRUTE_FORCE_LIMIT = 10


# ---------------------------------------------------------------------------
# Distance handling
# ---------------------------------------------------------------------------

def euclidean_distance(point_a, point_b):
    """Straight-line distance between two (x, y) points, from first principles."""
    dx = point_a[0] - point_b[0]
    dy = point_a[1] - point_b[1]
    return math.sqrt(dx * dx + dy * dy)


def build_distance_matrix(coords):
    """
    Pre-compute the n x n matrix of pairwise distances.

    Doing this once up front means the search algorithms below never repeat a
    distance calculation - they just look the value up. The matrix is symmetric
    (distance A->B equals B->A), so we only compute the upper triangle and
    mirror it, halving the work.
    """
    n = len(coords)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            distance = euclidean_distance(coords[i], coords[j])
            matrix[i][j] = distance
            matrix[j][i] = distance      # symmetric TSP
    return matrix


def tour_length(tour, dist):
    """
    Total cost of a closed tour.

    A tour is stored as an ordered list of city indices. It is a *cycle*, so
    the final leg wraps from the last city back to the first - that is what
    the modulo below does.
    """
    total = 0.0
    n = len(tour)
    for position in range(n):
        current_city = tour[position]
        next_city = tour[(position + 1) % n]
        total += dist[current_city][next_city]
    return total


# ---------------------------------------------------------------------------
# The heuristic: Nearest Neighbour
# ---------------------------------------------------------------------------

def nearest_neighbour_tour(dist, start=0):
    """
    Nearest Neighbour construction heuristic.

    Greedy rule: standing at the current city, always travel to the closest
    city that has not been visited yet. Repeat until every city is visited,
    then return to the start.

    Why this is a heuristic and not an exact method: each choice is optimal
    only at the moment it is made, and it is never reconsidered afterwards.
    Early greedy choices can strand a far-away city that must then be reached
    by one expensive leg near the end of the tour. The result is usually good,
    but is NOT guaranteed to be the shortest possible tour.

    Complexity: O(n^2). For each of the n cities we scan the unvisited list once.
    """
    n = len(dist)
    visited = [False] * n

    tour = [start]
    visited[start] = True
    current_city = start

    # Each iteration commits to exactly one more city.
    for _ in range(n - 1):

        # Explicit linear scan for the nearest unvisited city.
        # (Written out rather than using min(), so the greedy choice is visible.)
        nearest_city = -1
        nearest_distance = float('inf')

        for candidate in range(n):
            if not visited[candidate]:
                if dist[current_city][candidate] < nearest_distance:
                    nearest_distance = dist[current_city][candidate]
                    nearest_city = candidate

        # Commit to the greedy choice. This decision is never revisited.
        tour.append(nearest_city)
        visited[nearest_city] = True
        current_city = nearest_city

    return tour


def nearest_neighbour_costs_by_start(dist):
    """
    Cost of the NN tour produced from every possible starting city.

    Used to demonstrate a key limitation of the heuristic: the same set of
    cities can give noticeably different tours depending only on where we begin.
    """
    return [tour_length(nearest_neighbour_tour(dist, s), dist)
            for s in range(len(dist))]


def best_nearest_neighbour_tour(dist):
    """
    Run NN from every start city and keep the cheapest tour found.

    This is a cheap way to reduce the heuristic's start-city sensitivity:
    it multiplies the runtime by n (so O(n^3) overall) but is still far more
    practical than exhaustive search.

    Returns (tour, cost, start_city_index).
    """
    best_tour = None
    best_cost = float('inf')
    best_start = 0

    for start in range(len(dist)):
        tour = nearest_neighbour_tour(dist, start)
        cost = tour_length(tour, dist)
        if cost < best_cost:
            best_cost = cost
            best_tour = tour
            best_start = start

    return best_tour, best_cost, best_start


# ---------------------------------------------------------------------------
# The improvement pass: 2-opt local search
# ---------------------------------------------------------------------------

def two_opt(tour, dist):
    """
    2-opt local search improvement.

    Nearest Neighbour tours often contain edges that visibly cross each other.
    2-opt removes a crossing by taking two edges out of the tour and
    reconnecting the ends the other way round, which requires reversing the
    segment in between:

        ... A -> B ....... C -> D ...        (before)
        ... A -> C ....... B -> D ...        (after: segment B..C reversed)

    Instead of recomputing the whole tour cost for every candidate move, we
    compute only the change in cost, since the untouched edges cancel out:

        delta = (dist[A][C] + dist[B][D]) - (dist[A][B] + dist[C][D])

    A move is applied only when delta is strictly negative, so the tour cost
    can never increase. The loop repeats until a full pass finds no improvement
    at all - a "2-optimal" tour.

    This is still a heuristic. 2-opt reaches a LOCAL optimum: no single pair
    swap can improve it, but a better tour may still exist that would require
    changing three or more edges at once.

    Returns (improved_tour, number_of_passes).
    """
    n = len(tour)
    best = list(tour)          # work on a copy, leave the caller's tour intact
    improved = True
    passes = 0

    while improved:
        improved = False
        passes += 1

        for i in range(1, n - 1):
            for j in range(i + 1, n):

                # The two edges we are considering removing.
                a = best[i - 1]
                b = best[i]
                c = best[j]
                d = best[(j + 1) % n]      # wraps back to the start city

                # Net change in tour cost if we reconnect a->c and b->d.
                delta = (dist[a][c] + dist[b][d]) - (dist[a][b] + dist[c][d])

                # Small tolerance so floating-point noise is not mistaken
                # for a genuine improvement (which would loop forever).
                if delta < -1e-9:

                    # Reverse the segment between positions i and j, manually.
                    left = i
                    right = j
                    while left < right:
                        best[left], best[right] = best[right], best[left]
                        left += 1
                        right -= 1

                    improved = True

    return best, passes


# ---------------------------------------------------------------------------
# Validation only: exhaustive search
# ---------------------------------------------------------------------------

def generate_permutations(items):
    """
    Our own recursive permutation generator.

    itertools.permutations is deliberately NOT used, since the assignment
    forbids library-provided algorithmic solutions.

    Works by choosing each item in turn as the first element, then recursively
    permuting whatever remains. Implemented as a generator so it yields one
    ordering at a time instead of building the entire list in memory.
    """
    if len(items) <= 1:
        yield list(items)
        return

    for i in range(len(items)):
        chosen = items[i]
        remaining = items[:i] + items[i + 1:]
        for sub_permutation in generate_permutations(remaining):
            yield [chosen] + sub_permutation


def brute_force_optimal(dist):
    """
    Exhaustive search for the genuinely shortest tour.

    This is used ONLY to validate the heuristic on small instances - it is
    never the main solution. Comparing the heuristic's answer against a known
    optimum is how we measure the quality of the heuristic rather than just
    assuming the output "looks about right".

    City 0 is fixed as the start. A tour is a cycle, so rotating it does not
    change its cost, which leaves (n-1)! distinct orderings to test.

    Complexity: O(n!). Unusable beyond roughly 10 cities - which is precisely
    the reason a heuristic is required for real problem sizes.

    Returns (optimal_tour, optimal_cost, number_of_tours_evaluated).
    """
    n = len(dist)
    best_tour = None
    best_cost = float('inf')
    evaluated = 0

    for permutation in generate_permutations(list(range(1, n))):
        candidate_tour = [0] + permutation
        cost = tour_length(candidate_tour, dist)
        evaluated += 1

        if cost < best_cost:
            best_cost = cost
            best_tour = candidate_tour

    return best_tour, best_cost, evaluated


def percentage_gap(heuristic_cost, optimal_cost):
    """
    How much worse a heuristic tour is than the true optimum, as a percentage.

    A gap of 0% means the heuristic happened to find the optimal tour.
    """
    if optimal_cost <= 0:
        return 0.0
    return (heuristic_cost - optimal_cost) / optimal_cost * 100.0
