# Problem 2 - Backtracking
- GRAPH COLOURING PROBLEM

## NOTES:
## How to run
From terminal:

python problem2_graph_colouring.py

The program opens a menu:
1. Enter my own graph
2. Use a built-in sample graph
3. Find the minimum number of colours (chromatic number)
4. Run the test suite
5. Exit

**Option 4** runs all six test cases automatically and prints expected vs actual
output. This is the easiest way to confirm the program works.

---

## Input format (option 1)

The program prompts for each value in turn:

| Prompt | Valid input |
| --- | --- |
| Number of vertices (V) | a whole number, at least 1 |
| Number of colours (m) | a whole number, at least 1 |
| Number of edges (E) | 0 up to V×(V−1)/2 |
| Each edge | two vertex numbers, each 0 to V−1 |

- Vertices are numbered starting from **0**.
- Colours are numbered **1 to m**.

The program rejects and re-prompts on: non-numeric input, values out of range,
self-loops (a vertex joined to itself), and duplicate edges.

### Example

| Input | Output |
| --- | --- |
| V=3, m=3, edges 0-1, 1-2, 0-2 (a triangle) | Solution found using 3 colours |
| V=3, m=2, edges 0-1, 1-2, 0-2 (same triangle) | No solution — a triangle needs 3 colours |

---

## Algorithm

**Backtracking.** The program colours one vertex at a time. For each vertex it
tries colours 1..m; before committing to a colour it calls `is_safe()` to check
that no already-coloured neighbour is using that colour. If the colour is safe
it recurses to the next vertex; if that recursion fails it un-assigns the colour
(backtracks) and tries the next one.

```
choose  →  explore  →  un-choose
```

| Measure | Result | Reasoning |
| --- | --- | --- |
| Time (worst case) | O(V · m^V) | up to m^V colour combinations, each safety check costing O(V) |
| Space | O(V) | colour array + recursion stack, plus O(V²) for the adjacency matrix |

The graph is stored as an **adjacency matrix** (a V×V list of lists of 0/1),
chosen because the graphs here are small and edge lookup is O(1).

---

## Correctness checking

`verify_colouring()` is written **independently of the search**. It walks every
edge in the graph and confirms the two endpoints have different colours, and
that no vertex was left uncoloured. It runs automatically after every solved run
and on every test case, so a wrong answer would be caught even if the search
itself were faulty.

---

## Test cases

| # | Test case | Expected |
| --- | --- | --- |
| 1 | Triangle (K3), m=3 | solvable |
| 2 | Triangle (K3), m=2 | no solution |
| 3 | Cycle of 4 (square), m=2 | solvable |
| 4 | Path of 4 vertices, m=2 | solvable |
| 5 | Disconnected graph, m=2 | solvable |
| 6 | Single vertex, no edges, m=1 | solvable |

---