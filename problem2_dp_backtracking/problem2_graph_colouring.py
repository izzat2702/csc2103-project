"""
CSC2103 Data Structures and Algorithms - Group Project
Problem 2: Backtracking - Graph Colouring (m-Colouring Problem)

Console program that decides whether an undirected graph can be properly
coloured with at most m colours, using a hand-written backtracking search.

Vertices are numbered 0 .. V-1 (0-based).
Colours are numbered 1 .. m, with 0 meaning "not yet coloured".

The graph is stored as an adjacency matrix: a V x V list of lists where
graph[i][j] == 1 means there is an edge between vertex i and vertex j.

No external or built-in graph/colouring library is used. The algorithm is
implemented manually as required by the assignment brief.
"""

# ============================================================================
#  PART 1 - CORE BACKTRACKING ALGORITHM
# ============================================================================

def is_safe(graph, colors, vertex, colour, V):
    """
    Return True if `colour` can be given to `vertex` without breaking the
    adjacency constraint (no two adjacent vertices share a colour).

    We scan every other vertex u. If u is adjacent to `vertex` AND u has
    already been given the same colour, the assignment is illegal.
    """
    for u in range(V):
        if graph[vertex][u] == 1 and colors[u] == colour:
            return False
    return True


def solve(graph, colors, vertex, V, m):
    """
    Recursive backtracking driver.

    Tries to colour vertex `vertex`, then all vertices after it.
    Returns True if a complete valid colouring was found, False otherwise.

    Pattern: choose -> explore -> un-choose (backtrack).
    """
    # Base case: every vertex has been coloured successfully.
    if vertex == V:
        return True

    for colour in range(1, m + 1):
        if is_safe(graph, colors, vertex, colour, V):
            colors[vertex] = colour              # choose
            if solve(graph, colors, vertex + 1, V, m):
                return True                      # explore - success bubbles up
            colors[vertex] = 0                   # un-choose (BACKTRACK)

    # No colour worked for this vertex, so the caller must backtrack.
    return False


# ============================================================================
#  PART 2 - INPUT / OUTPUT AND VALIDATION
# ============================================================================

# Friendly names so the printed output reads better than bare numbers.
COLOUR_NAMES = ["Red", "Green", "Blue", "Yellow", "Orange",
                "Purple", "Cyan", "Magenta", "Brown", "Pink"]


def colour_label(colour):
    """Turn colour number 1..m into 'Colour 1 (Red)' style text."""
    if 1 <= colour <= len(COLOUR_NAMES):
        return "Colour %d (%s)" % (colour, COLOUR_NAMES[colour - 1])
    return "Colour %d" % colour


# ---------------------------------------------------------------- input ----

def read_int(prompt, minimum, maximum=None):
    """
    Keep asking until the user types a whole number within range.
    Returns the validated integer.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("  -> Please enter a whole number.")
            continue
        if value < minimum:
            print("  -> Value must be at least %d." % minimum)
            continue
        if maximum is not None and value > maximum:
            print("  -> Value must be at most %d." % maximum)
            continue
        return value


def make_empty_graph(V):
    """Create a V x V adjacency matrix filled with zeros."""
    return [[0 for _ in range(V)] for _ in range(V)]


def read_input():
    """
    Collect the graph from the user.
    Returns (V, m, graph).

    Validation performed:
      - V and m must be positive whole numbers
      - vertex indices must be within 0 .. V-1
      - self-loops (u == v) are rejected - they can never be coloured
      - duplicate edges are detected and skipped, not double-counted
      - every edge is written twice (u,v and v,u) so the graph is undirected
    """
    print()
    print("--- Enter your graph ---")
    print("Vertices are numbered starting from 0.")

    V = read_int("Number of vertices (V): ", 1)
    m = read_int("Number of colours to try (m): ", 1)

    max_edges = V * (V - 1) // 2
    E = read_int("Number of edges (E), 0 to %d: " % max_edges, 0, max_edges)

    graph = make_empty_graph(V)

    edges_added = 0
    while edges_added < E:
        print("Edge %d of %d - enter two vertex numbers." % (edges_added + 1, E))
        u = read_int("  first vertex  (0 to %d): " % (V - 1), 0, V - 1)
        v = read_int("  second vertex (0 to %d): " % (V - 1), 0, V - 1)

        if u == v:
            print("  -> A vertex cannot be joined to itself. Try again.")
            continue
        if graph[u][v] == 1:
            print("  -> Edge %d-%d already exists. Try a different edge." % (u, v))
            continue

        graph[u][v] = 1
        graph[v][u] = 1          # undirected: record both directions
        edges_added += 1

    return V, m, graph


# --------------------------------------------------------------- output ----

def print_graph(graph, V):
    """Show the adjacency matrix so the user can confirm what was entered."""
    print()
    print("Adjacency matrix (1 = edge, 0 = no edge):")
    header = "     " + " ".join("%2d" % j for j in range(V))
    print(header)
    print("     " + "-" * (3 * V - 1))
    for i in range(V):
        row = " ".join("%2d" % graph[i][j] for j in range(V))
        print("%2d | %s" % (i, row))


def print_solution(colors, V, m):
    """Print a tidy Vertex -> Colour table plus how many colours were used."""
    used = len(set(colors))
    print()
    print("SOLUTION FOUND using %d of the %d available colour(s)." % (used, m))
    print()
    print("  +----------+---------------------+")
    print("  | Vertex   | Colour              |")
    print("  +----------+---------------------+")
    for v in range(V):
        print("  | %-8d | %-19s |" % (v, colour_label(colors[v])))
    print("  +----------+---------------------+")


def print_no_solution(V, m):
    print()
    print("NO SOLUTION: this graph of %d vertices cannot be properly coloured "
          "with only %d colour(s)." % (V, m))
    print("Try again with a larger m, or use option 3 to find the minimum "
          "number of colours needed.")


# --------------------------------------------------------- verification ----

def verify_colouring(graph, colors, V):
    """
    Independent correctness check, written separately from the algorithm.

    Walks every edge in the graph and confirms the two endpoints have
    different colours, and that no vertex was left uncoloured.
    Returns (ok, message).
    """
    for v in range(V):
        if colors[v] == 0:
            return False, "vertex %d was left uncoloured" % v

    for u in range(V):
        for v in range(u + 1, V):
            if graph[u][v] == 1 and colors[u] == colors[v]:
                return False, ("edge %d-%d has the same colour on both ends "
                               "(colour %d)" % (u, v, colors[u]))

    return True, "all edges connect differently-coloured vertices"


# ------------------------------------------------------ driver functions ----

def colour_graph(graph, V, m):
    """
    Run the backtracking search once for a given m.
    Returns (found, colors).
    """
    colors = [0] * V
    found = solve(graph, colors, 0, V, m)
    return found, colors


def find_chromatic_number(graph, V):
    """
    Extra feature: the m-colouring solver only answers yes/no for a fixed m.
    Trying m = 1, 2, 3, ... and stopping at the first success gives the
    chromatic number - the minimum number of colours the graph needs.
    """
    for m in range(1, V + 1):
        found, colors = colour_graph(graph, V, m)
        if found:
            return m, colors
    return V, [0] * V      # unreachable for a simple graph, kept for safety


# ============================================================================
#  PART 3 - TEST HARNESS
# ============================================================================

def build_graph(V, edges):
    """Helper for the test cases: build a matrix from a list of edge pairs."""
    graph = make_empty_graph(V)
    for u, v in edges:
        graph[u][v] = 1
        graph[v][u] = 1
    return graph


# name, V, edges, m, expected result ("solvable" / "no solution")
TEST_CASES = [
    ("Triangle (K3), m=3",
     3, [(0, 1), (1, 2), (0, 2)], 3, True),

    ("Triangle (K3), m=2  - infeasible case",
     3, [(0, 1), (1, 2), (0, 2)], 2, False),

    ("Cycle of 4 (square), m=2",
     4, [(0, 1), (1, 2), (2, 3), (3, 0)], 2, True),

    ("Path graph of 4 vertices, m=2",
     4, [(0, 1), (1, 2), (2, 3)], 2, True),

    ("Disconnected graph (two separate edges + isolated vertex), m=2",
     5, [(0, 1), (2, 3)], 2, True),

    ("Single vertex, no edges, m=1  - smallest input",
     1, [], 1, True),
]


def run_tests():
    """
    Run every test case and print expected vs actual.
    Also independently verifies each colouring that is produced.
    """
    print()
    print("=" * 68)
    print("TEST SUITE - expected vs actual")
    print("=" * 68)

    passed = 0
    for name, V, edges, m, expected in TEST_CASES:
        graph = build_graph(V, edges)
        found, colors = colour_graph(graph, V, m)

        expected_text = "solvable" if expected else "no solution"
        actual_text = "solvable" if found else "no solution"
        ok = (found == expected)

        # If a colouring was returned, it must also survive the verifier.
        detail = ""
        if found:
            valid, message = verify_colouring(graph, colors, V)
            detail = "verified: " + message
            if not valid:
                ok = False
        else:
            detail = "no colouring produced, nothing to verify"

        if ok:
            passed += 1

        print()
        print("Test: %s" % name)
        print("  Expected : %s" % expected_text)
        print("  Actual   : %s" % actual_text)
        if found:
            print("  Colouring: %s" % ", ".join(
                "v%d=%d" % (v, colors[v]) for v in range(V)))
        print("  Check    : %s" % detail)
        print("  Result   : %s" % ("PASS" if ok else "FAIL"))

    print()
    print("=" * 68)
    print("%d of %d tests passed." % (passed, len(TEST_CASES)))
    print("=" * 68)


# ============================================================================
#  PART 4 - SAMPLE GRAPHS AND MAIN MENU
# ============================================================================

SAMPLE_GRAPHS = [
    ("Triangle - 3 vertices, all joined", 3, [(0, 1), (1, 2), (0, 2)]),
    ("Square cycle - 4 vertices in a ring", 4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
    ("Path - 4 vertices in a line", 4, [(0, 1), (1, 2), (2, 3)]),
    ("Exam timetable example - 5 exams with clashes", 5,
     [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)]),
]


def choose_sample():
    """Let the user pick one of the built-in graphs. Returns (V, graph)."""
    print()
    print("--- Sample graphs ---")
    for i, (name, V, edges) in enumerate(SAMPLE_GRAPHS, start=1):
        print("  %d. %s  (%d vertices, %d edges)" % (i, name, V, len(edges)))
    choice = read_int("Choose a sample (1 to %d): " % len(SAMPLE_GRAPHS),
                      1, len(SAMPLE_GRAPHS))
    name, V, edges = SAMPLE_GRAPHS[choice - 1]
    print("Loaded: %s" % name)
    return V, build_graph(V, edges)


def run_and_report(graph, V, m):
    """Colour the graph with m colours, print the result, and verify it."""
    print_graph(graph, V)
    found, colors = colour_graph(graph, V, m)

    if not found:
        print_no_solution(V, m)
        return

    print_solution(colors, V, m)

    valid, message = verify_colouring(graph, colors, V)
    print()
    print("Verification: %s - %s" % ("PASSED" if valid else "FAILED", message))


def main():
    print("=" * 68)
    print(" CSC2103 - Problem 2: Graph Colouring using Backtracking")
    print("=" * 68)
    print("Given a graph and m colours, decide whether every vertex can be")
    print("coloured so that no two connected vertices share a colour.")

    while True:
        print()
        print("--- Main menu ---")
        print("  1. Enter my own graph")
        print("  2. Use a built-in sample graph")
        print("  3. Find the minimum number of colours (chromatic number)")
        print("  4. Run the test suite")
        print("  5. Exit")

        choice = read_int("Select an option (1 to 5): ", 1, 5)

        if choice == 1:
            V, m, graph = read_input()
            run_and_report(graph, V, m)

        elif choice == 2:
            V, graph = choose_sample()
            m = read_int("Number of colours to try (m): ", 1)
            run_and_report(graph, V, m)

        elif choice == 3:
            print()
            print("The number of colours you enter is ignored for this option -")
            print("the program searches upward from m = 1 until it succeeds.")
            V, m, graph = read_input()
            print_graph(graph, V)
            best, colors = find_chromatic_number(graph, V)
            print()
            print("Minimum colours needed (chromatic number): %d" % best)
            print_solution(colors, V, best)
            valid, message = verify_colouring(graph, colors, V)
            print()
            print("Verification: %s - %s" % ("PASSED" if valid else "FAILED", message))

        elif choice == 4:
            run_tests()

        elif choice == 5:
            print()
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()