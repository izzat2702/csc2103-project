"""
CSC2103 Data Structures and Algorithms - Group Project
Problem 3: Heuristic Algorithms - Travelling Salesman Problem (TSP)

Core algorithmic logic, imported by problem3_tsp_heuristic.py. Nothing in this
module prints anything, so the algorithms can be read and tested on their own.

Cities are numbered 0 .. n-1 (0-based).

Distances are stored as an adjacency matrix: an n x n list of lists where
dist[i][j] is the straight-line distance between city i and city j. The matrix
is symmetric, so dist[i][j] always equals dist[j][i].

A tour is an ordered list of city indices, for example [0, 3, 1, 2], read as a
cycle - the last city always joins back to the first.

No external or built-in optimisation library is used. Every algorithm is
implemented manually as required by the assignment brief:

      - distances use the Euclidean formula written out by hand
      - the nearest-neighbour step is an explicit linear scan, not min()
        or sorted()
      - the 2-opt segment reversal is a manual two-pointer swap loop
      - the exhaustive validator uses our own recursive permutation
        generator, NOT itertools.permutations()

The only import is math, used for sqrt(), which is arithmetic rather than an
algorithm.
"""

import math

# Exhaustive search runs in factorial time, so it is only offered for tiny
# instances. 10 cities => 9! = 362,880 candidate tours (a few seconds in Python).
# Anything larger is exactly why a heuristic is needed in the first place.
BRUTE_FORCE_LIMIT = 10


# ============================================================================
#  PART 1 - DISTANCE HANDLING
# ============================================================================

def euclidean_distance(point_a, point_b):
    """Return the straight-line distance between two (x, y) points."""
    dx = point_a[0] - point_b[0]
    dy = point_a[1] - point_b[1]
    return math.sqrt(dx * dx + dy * dy)


def build_distance_matrix(coords):
    """
    Pre-compute the n x n matrix of distances between every pair of cities.

    Doing this once up front means the search algorithms never repeat a
    distance calculation, they simply look the value up. Distance A->B equals
    B->A, so only the upper triangle is calculated and then mirrored, which
    halves the work.
    """
    n = len(coords)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            distance = euclidean_distance(coords[i], coords[j])
            matrix[i][j] = distance
            matrix[j][i] = distance      # symmetric: record both directions
    return matrix


def tour_length(tour, dist):
    """
    Return the total cost of a closed tour.

    A tour is a cycle, so the final leg wraps from the last city back to the
    first. The modulo below is what performs that wrap.
    """
    total = 0.0
    n = len(tour)
    for position in range(n):
        current_city = tour[position]
        next_city = tour[(position + 1) % n]     # wraps to the start
        total += dist[current_city][next_city]
    return total


# ============================================================================
#  PART 2 - THE HEURISTIC: NEAREST NEIGHBOUR
# ============================================================================

def nearest_neighbour_tour(dist, start=0):
    """
    Build a tour using the Nearest Neighbour construction heuristic.

    Greedy rule: standing at the current city, always travel to the closest
    city not yet visited. Repeat until every city is visited, then return to
    the start.

    Why this is a heuristic and not an exact method: each choice is optimal
    only at the moment it is made, and is never reconsidered afterwards. An
    early greedy choice can strand a far-away city, which must then be reached
    by one expensive leg near the end. The result is usually good, but is NOT
    guaranteed to be the shortest possible tour.

    Pattern: pick nearest -> commit -> move on (never backtrack).

    Complexity: O(n^2) - for each of the n cities we scan the unvisited list.
    """
    n = len(dist)
    visited = [False] * n

    tour = [start]
    visited[start] = True
    current_city = start

    # Each iteration commits to exactly one more city.
    for _ in range(n - 1):

        # Explicit linear scan for the nearest unvisited city. Written out
        # rather than using min(), so the greedy choice stays visible.
        nearest_city = -1
        nearest_distance = float('inf')

        for candidate in range(n):
            if not visited[candidate]:
                if dist[current_city][candidate] < nearest_distance:
                    nearest_distance = dist[current_city][candidate]
                    nearest_city = candidate

        tour.append(nearest_city)                # choose
        visited[nearest_city] = True             # mark as used
        current_city = nearest_city              # move on - never revisited

    return tour


def nearest_neighbour_costs_by_start(dist):
    """
    Return a list holding the NN tour cost from every possible starting city.

    Serves two purposes. It shows a key limitation of the heuristic - the same
    cities give different tours depending only on where we begin - and the
    cheapest entry in the list identifies the best starting city, which is the
    "multi-start" improvement. The caller rebuilds just that one tour instead
    of searching all n starts a second time.

    Complexity: O(n^3), since it runs the O(n^2) heuristic n times. Still far
    cheaper than exhaustive search.
    """
    return [tour_length(nearest_neighbour_tour(dist, s), dist)
            for s in range(len(dist))]


# ============================================================================
#  PART 3 - THE IMPROVEMENT PASS: 2-OPT LOCAL SEARCH
# ============================================================================

def two_opt(tour, dist):
    """
    Improve an existing tour using 2-opt local search.
    Returns (improved_tour, number_of_passes).

    Nearest Neighbour tours often contain edges that visibly cross each other.
    2-opt removes a crossing by taking two edges out of the tour and
    reconnecting the ends the other way round, which requires reversing the
    segment in between:

        ... A -> B ....... C -> D ...        (before)
        ... A -> C ....... B -> D ...        (after: segment B..C reversed)

    Instead of recomputing the whole tour cost for every candidate move, only
    the change in cost is calculated, because the untouched edges cancel out:

        delta = (dist[A][C] + dist[B][D]) - (dist[A][B] + dist[C][D])

    A move is applied only when delta is strictly negative, so the tour cost
    can never increase. The loop repeats until a full pass finds no improvement
    anywhere - a "2-optimal" tour.

    This is still a heuristic. 2-opt reaches a LOCAL optimum: no single pair
    swap can improve it, but a better tour may still exist that would need
    three or more edges changed at once.
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

                # The two edges we are considering removing: a->b and c->d.
                a = best[i - 1]
                b = best[i]
                c = best[j]
                d = best[(j + 1) % n]      # wraps back to the start city

                # Net change in tour cost if we reconnect a->c and b->d.
                delta = (dist[a][c] + dist[b][d]) - (dist[a][b] + dist[c][d])

                # A small tolerance instead of plain "< 0", so floating-point
                # noise is never mistaken for a genuine improvement. Without
                # it the loop could keep swapping forever.
                if delta < -1e-9:

                    # Reverse the segment between positions i and j by hand,
                    # walking two pointers towards each other.
                    left = i
                    right = j
                    while left < right:
                        best[left], best[right] = best[right], best[left]
                        left += 1
                        right -= 1

                    improved = True        # another pass is now worthwhile

    return best, passes


# ============================================================================
#  PART 4 - VALIDATION ONLY: EXHAUSTIVE SEARCH
# ============================================================================

def generate_permutations(items):
    """
    Yield every ordering of `items`, one at a time.

    itertools.permutations is deliberately NOT used, since the brief forbids
    library-provided algorithmic solutions.

    Works by choosing each item in turn as the first element, then recursively
    permuting whatever remains. Written as a generator so orderings are
    produced one by one instead of building the whole list in memory.
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
    Find the genuinely shortest tour by testing every possibility.
    Returns (optimal_tour, optimal_cost, number_of_tours_evaluated).

    Independent correctness check, written separately from the heuristic. It
    is used ONLY to validate the heuristic on small inputs and is never the
    main solution. Comparing the heuristic against a known optimum is how the
    quality of the answer is measured, rather than assuming the output looks
    about right.

    City 0 is fixed as the start. A tour is a cycle, so rotating it does not
    change its cost, which leaves (n-1)! distinct orderings to test.

    Complexity: O(n!) - unusable beyond roughly 10 cities, which is precisely
    why a heuristic is needed for real problem sizes.
    """
    n = len(dist)
    best_tour = None
    best_cost = float('inf')
    evaluated = 0

    for permutation in generate_permutations(list(range(1, n))):
        candidate_tour = [0] + permutation       # city 0 always leads
        cost = tour_length(candidate_tour, dist)
        evaluated += 1

        if cost < best_cost:
            best_cost = cost
            best_tour = candidate_tour

    return best_tour, best_cost, evaluated


def percentage_gap(heuristic_cost, optimal_cost):
    """
    Return how much worse a heuristic tour is than the optimum, as a percentage.

    A gap of 0% means the heuristic happened to find the optimal tour.
    """
    if optimal_cost <= 0:
        return 0.0
    return (heuristic_cost - optimal_cost) / optimal_cost * 100.0
