# Problem 3 - Heuristic
- TRAVELLING SALESMAN PROBLEM (TSP)

**Algorithm:** TSP with Nearest Neighbour, plus a 2-opt improvement pass

---

## How to run

    python problem3_tsp_heuristic.py

Python 3, nothing to install. Menu options: sample dataset / manual entry /
seeded random / exit.

**Dataset 2** is the quickest demo - it is a case where the heuristic lands
43.27% worse than optimal, then gets repaired by 2-opt.

Replay a recorded test case:

    python problem3_tsp_heuristic.py < sample_runs/input_02_nn_trap.txt

---

## Files

| File | Contents |
| --- | --- |
| `problem3_tsp_heuristic.py` | Main program - menus, validation, output formatting |
| `tsp_algorithms.py` | Core algorithm logic, prints nothing itself |
| `sample_runs/` | 7 test cases: keystrokes in, exact output out |
| `report_section_problem3.docx` | Our Section 5, ready to merge |
| `ai_usage_problem3.md` | Notes for the AI declaration section |

Both `.py` files must sit in the same folder or the program won't start.

---

## What the problem actually is

Find the shortest route that visits every location once and returns to the
start. We framed it as a delivery van leaving a depot and coming back.

The trouble is that `n` locations give `(n-1)!` possible routes:

| Locations | Routes |
| --- | --- |
| 7 | 720 |
| 9 | 40,320 |
| 15 | 87,178,291,200 |
| 20 | about 1.2 x 10^17 |

Checking them all is only realistic for tiny inputs. Hence a heuristic.

---

## How the heuristic works

**Nearest Neighbour** builds the route greedily: from the current city, go to
the nearest unvisited city. Repeat, then return to the start. Choices are never
reconsidered.

    pick nearest  ->  commit  ->  move on (never backtrack)

**2-opt** then improves it by removing two edges and reconnecting them the other
way round, reversing the segment between:

    Before:   ... A --> B .......... C --> D ...
    After:    ... A --> C .......... B --> D ...

Only the change in cost is computed, since untouched edges cancel out:

    delta = (dist[A][C] + dist[B][D]) - (dist[A][B] + dist[C][D])

A swap is applied only when `delta` is negative, so the route never gets worse.
Repeats until a full pass finds no improvement.

| Measure | Result | Reasoning |
| --- | --- | --- |
| Nearest Neighbour | O(n^2) | for each of n cities, scan the unvisited list |
| 2-opt | O(n^2) per pass | every pair of positions tested each pass |
| Multi-start NN | O(n^3) | runs the O(n^2) heuristic from all n starts |
| Exhaustive check | O(n!) | validation only, capped at 10 cities |

Distances are held in an n x n adjacency matrix, computed once up front.

---

## How input/output works

City 1 is always the depot. The random option takes a **seed** so datasets can
be reproduced - that is how the report screenshots were made repeatable. Bad
input is rejected and re-prompted, never crashes.

| Input method | Asks for |
| --- | --- |
| Sample dataset | pick 1-4 |
| Manual entry | 3-12 cities, then a name and x/y for each |
| Random | 3-50 cities, plus a seed |

Output runs in four labelled stages:

| Stage | Shows |
| --- | --- |
| 1 | NN route, with a leg-by-leg distance table |
| 2 | 2-opt route, cost before/after, passes, saving |
| 3 | Cost from every starting city, best and worst flagged |
| 4 | True optimum from exhaustive search, or why it was skipped |

A summary table then compares every method against the optimum.

---

## It will not always find the optimal answer

Nearest Neighbour gives **no optimality guarantee**. It never reconsiders a
choice, so it can strand a distant city and pay for it with one expensive leg at
the end.

Dataset 2 shows this deliberately: legs 6 and 7 cost 62.64 and 48.85 because
city F was left behind, making the route **43.27% worse than optimal**.

2-opt helps but is also a heuristic - it only reaches a *local* optimum.

The trade-off is speed: on 15 cities the heuristic answers instantly where
exhaustive search would face 87 billion routes.

---

## Correctness checking

1. **Hand calculation.** Square = 40.00, triangle = 5 + 5 + sqrt(50) = 17.07,
   3x3 grid = (8 x 20) + 20*sqrt(2) = 188.28. All three matched.
2. **Exhaustive cross-check.** For 10 cities or fewer the program brute-forces
   all `(n-1)!` routes and reports the error as an exact percentage.
3. **Reproducibility.** The seeded 20-city set ran twice, byte-identical.

---

## What broke, and limitations found while testing

**Column alignment.** The depot's `*` marker pushed the X/Y columns out of line
when the depot had the longest name. Only appeared on manual input. Fixed by
reserving two extra characters of column width.

**2-opt could have looped forever.** With floating-point distances, a swap that
changes nothing can compute as a tiny negative. `delta < 0` would loop endlessly;
fixed with a tolerance of `delta < -1e-9`.

**Duplicated work.** Stage 3 built a route from every start city, then the
multi-start step rebuilt them all again. Now only the winner is rebuilt - 41
route constructions down to 21 on the 20-city set.

Limitations we did not solve:

- Validation is `O(n!)`, so accuracy can only be *proven* for 10 cities or fewer.
- NN is sensitive to its start city - up to 43.27% swing on the same cities.
- 2-opt cannot escape a local optimum (20-city set gives 467.05 vs 452.09).
- Straight-line distance only; real routes follow roads and traffic.

---

## Test cases

| # | Test case | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| 1 | Courier route, 8 cities | NN above optimum, 2-opt improves | NN 176.74 (+21.94%), 2-opt 144.94 (optimal) | Pass |
| 2 | NN Trap, 7 cities | NN performs badly | NN 204.37 (+43.27%), 2-opt 142.64 (optimal) | Pass |
| 3 | 3x3 grid, 9 cities | Optimum = 188.28 | NN 216.57 (+15.02%), 2-opt 188.28 (optimal) | Pass |
| 4 | Regional, 15 cities | Exhaustive skipped | Skipped (87,178,291,200 routes); 335.26 -> 294.88 | Pass |
| 5 | Manual square, side 10 | Perimeter = 40.00 | 40.00 (optimal) | Pass |
| 6 | Random, 20 cities, seed 42 | Same output twice | 633.94 -> 452.09, byte-identical | Pass |
| 7 | Invalid input | Rejected, no crash | All rejected; triangle = 17.07 | Pass |

Keystrokes and full output for each are in `sample_runs/`.

---

## Assignment rules

**No built-in or library algorithm is used for the core task.** The full import
list for both files is `math`, `random`, and our own `tsp_algorithms`.

| Not used | Written manually instead |
| --- | --- |
| `sorted()` / `.sort()` | nothing is sorted anywhere, not even menu items |
| `min()` / `max()` | explicit comparison loops |
| `itertools.permutations()` | our own recursive `generate_permutations()` |
| `math.factorial()` | a plain loop |

`math` is only `sqrt()` in the distance formula. `random` only generates
coordinates for menu option 3 and never appears in `tsp_algorithms.py`, so every
algorithm is deterministic. Console only, no GUI.
