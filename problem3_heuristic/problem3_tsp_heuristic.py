"""
CSC2103 Data Structures and Algorithms - Group Project
Problem 3: Heuristic Algorithms - Travelling Salesman Problem (TSP)

Console program that finds a short round trip visiting every delivery point
exactly once and returning to the depot, using a hand-written Nearest Neighbour
heuristic followed by a 2-opt improvement pass.

Cities are numbered 0 .. n-1 (0-based). City 0 is the depot, so every tour
starts and ends there.

A tour is stored as an ordered list of city indices, for example [0, 3, 1, 2].
It is read as a cycle: the last city always joins back to the first.

This file handles input, output and presentation only. All algorithmic logic
lives in tsp_algorithms.py.

No external or built-in optimisation library is used. The algorithms are
implemented manually as required by the assignment brief.
"""

import random                     # only used to generate input coordinates,
                                  # never inside any algorithm
import tsp_algorithms as tsp


# Width of the console output, used by every rule and wrapped line.
LINE_WIDTH = 76


# ============================================================================
#  PART 1 - BUILT-IN SAMPLE DATASETS
# ============================================================================

# Each dataset is (description, [city names], [(x, y) coordinates]).
# Coordinates are in kilometres on a flat grid, and city index 0 is the depot.
#
# Dataset 2 is deliberately chosen: it is a case where Nearest Neighbour
# performs badly, which shows that the heuristic gives no optimality guarantee.

SAMPLE_DATASETS = {
    "1": (
        "City Courier Route - 8 drop-off points",
        ["Depot", "Northgate", "Riverside", "Hillcrest", "Eastpark",
         "Southbank", "Westfield", "Lakeview"],
        [(5, 37), (10, 12), (32, 28), (23, 20), (21, 18),
         (49, 49), (43, 18), (27, 43)],
    ),
    "2": (
        "Nearest Neighbour Trap - 7 points (heuristic performs badly here)",
        ["A", "B", "C", "D", "E", "F", "G"],
        [(45, 33), (33, 41), (26, 35), (26, 10), (50, 15), (0, 14), (60, 32)],
    ),
    "3": (
        "Regular Grid - 9 points in a 3x3 layout",
        ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"],
        [(0, 0), (20, 0), (40, 0), (0, 20), (20, 20), (40, 20),
         (0, 40), (20, 40), (40, 40)],
    ),
    "4": (
        "Regional Network - 15 stops (too large for exhaustive search)",
        ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8",
         "S9", "S10", "S11", "S12", "S13", "S14", "S15"],
        [(12, 8), (46, 15), (23, 55), (67, 42), (5, 31), (58, 60), (34, 22),
         (71, 18), (19, 44), (52, 33), (40, 68), (8, 62), (63, 5), (29, 37),
         (75, 55)],
    ),
}


# ============================================================================
#  PART 2 - INPUT / OUTPUT AND VALIDATION
# ============================================================================

# --------------------------------------------------------------- layout ----

def print_rule(character="-"):
    """Draw one horizontal line the full width of the console."""
    print(character * LINE_WIDTH)


def print_banner():
    """Print the program title block shown once at start-up."""
    print_rule("=")
    print("  CSC2103 Data Structures & Algorithms - Group Project")
    print("  Problem 3: Heuristic Algorithms")
    print("  Travelling Salesman Problem  -  Nearest Neighbour + 2-opt")
    print_rule("=")


def print_section(title):
    """Print a boxed heading so each stage of the run is easy to find."""
    print()
    print_rule("=")
    print("  " + title)
    print_rule("=")


def factorial(number):
    """
    Return number! using a plain loop.

    Written out by hand rather than importing math.factorial, to keep the
    program free of library-provided helpers.
    """
    result = 1
    for value in range(2, number + 1):
        result *= value
    return result


# ---------------------------------------------------------------- input ----

def read_int(prompt, low, high):
    """
    Keep asking until the user types a whole number within range.
    Returns the validated integer.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("  ! Please enter a whole number.")
            continue
        if value < low or value > high:
            print("  ! Please enter a value between %d and %d." % (low, high))
            continue
        return value


def read_float(prompt):
    """
    Keep asking until the user types a number, decimals allowed.
    Returns the validated float.
    """
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("  ! Please enter a number (decimals are allowed).")


def read_choice(prompt, valid_options):
    """
    Keep asking until the user picks one of the allowed menu options.
    Returns the chosen option in lower case.
    """
    while True:
        raw = input(prompt).strip().lower()
        if raw in valid_options:
            return raw
        print("  ! Please choose one of: %s" % ", ".join(valid_options))


def choose_sample_dataset():
    """
    Let the user pick one of the built-in datasets.
    Returns (description, names, coords).
    """
    print_section("BUILT-IN SAMPLE DATASETS")
    for key in sorted(SAMPLE_DATASETS.keys()):
        description = SAMPLE_DATASETS[key][0]
        print("  %s. %s" % (key, description))
    print()

    choice = read_choice("  Select a dataset: ", sorted(SAMPLE_DATASETS.keys()))
    description, names, coords = SAMPLE_DATASETS[choice]
    return description, list(names), list(coords)


def enter_cities_manually():
    """
    Collect the cities from the user, one at a time.
    Returns (description, names, coords).

    Validation performed:
      - the city count must be a whole number from 3 to 12
      - both coordinates must be numbers, decimals allowed
      - a blank name falls back to a default such as "City3"
    """
    print_section("MANUAL CITY ENTRY")
    print("  City 1 is treated as the depot (the tour starts and ends there).")
    print()

    count = read_int("  How many cities? (3-12): ", 3, 12)

    names = []
    coords = []
    for index in range(count):
        print()
        default_name = "City%d" % (index + 1)
        raw_name = input("  Name of city %d [%s]: " % (index + 1, default_name)).strip()
        name = raw_name if raw_name else default_name

        x = read_float("    x coordinate: ")
        y = read_float("    y coordinate: ")

        names.append(name)
        coords.append((x, y))

    return "User-entered dataset - %d cities" % count, names, coords


def generate_random_cities():
    """
    Build a random instance of the problem.
    Returns (description, names, coords).

    The user supplies a seed so the exact same dataset can be reproduced on a
    later run. This matters for the report, where the screenshots must be
    repeatable.
    """
    print_section("RANDOM CITY GENERATION")

    count = read_int("  How many cities? (3-50): ", 3, 50)
    seed = read_int("  Random seed (any whole number, e.g. 42): ", -10 ** 9, 10 ** 9)

    random.seed(seed)
    names = ["C%d" % (index + 1) for index in range(count)]
    coords = [(float(random.randint(0, 100)), float(random.randint(0, 100)))
              for _ in range(count)]

    description = "Random dataset - %d cities (seed %d)" % (count, seed)
    return description, names, coords


# --------------------------------------------------------------- output ----

def name_column_width(names):
    """Return the width of the longest city name, with a sensible minimum."""
    widest = 4
    for name in names:
        if len(name) > widest:
            widest = len(name)
    return widest


def print_city_table(names, coords):
    """Show the cities back to the user so the input can be confirmed."""
    # The +2 leaves room for the " *" depot marker added below, so the
    # coordinate columns stay aligned even when the depot has the longest name.
    width = name_column_width(names) + 2

    print()
    print("  %-4s %-*s %10s %10s" % ("No.", width, "City", "X", "Y"))
    print("  " + "-" * (4 + width + 23))
    for index in range(len(names)):
        label = names[index]
        if index == 0:
            label += " *"                    # mark the depot
        print("  %-4d %-*s %10.2f %10.2f"
              % (index + 1, width, label, coords[index][0], coords[index][1]))
    print("  " + "-" * (4 + width + 23))
    print("  * depot - the tour starts and ends here")


def format_tour(names, tour):
    """
    Render a tour as 'A -> B -> C -> A', wrapped to fit the console width.

    The first city is repeated at the end because a tour is a cycle.
    """
    labels = [names[city] for city in tour]
    labels.append(names[tour[0]])       # close the cycle

    lines = []
    current = "  "
    for position in range(len(labels)):
        piece = labels[position]
        if position < len(labels) - 1:
            piece += " -> "
        if len(current) + len(piece) > LINE_WIDTH:
            lines.append(current)            # start a new line
            current = "      " + piece
        else:
            current += piece
    lines.append(current)
    return "\n".join(lines)


def print_leg_table(names, tour, dist):
    """
    Print a leg-by-leg cost breakdown of a tour and return its total cost.

    The final row is the return trip to the depot, marked "(return)".
    """
    width = name_column_width(names)
    total = 0.0

    print()
    print("  %-5s %-*s     %-*s %12s" % ("Leg", width, "From", width, "To", "Distance"))
    print("  " + "-" * (width * 2 + 24))

    for position in range(len(tour)):
        from_city = tour[position]
        to_city = tour[(position + 1) % len(tour)]      # wraps to the depot
        leg_distance = dist[from_city][to_city]
        total += leg_distance

        note = "  (return)" if position == len(tour) - 1 else ""
        print("  %-5d %-*s ->  %-*s %12.2f%s"
              % (position + 1, width, names[from_city],
                 width, names[to_city], leg_distance, note))

    print("  " + "-" * (width * 2 + 24))
    print("  %-*s %12.2f" % (width * 2 + 11, "TOTAL TOUR COST", total))
    return total


# ============================================================================
#  PART 3 - THE ANALYSIS PIPELINE
# ============================================================================

def run_analysis(description, names, coords):
    """
    Run all four stages of the solution on one dataset and report the results.

    Stage 1  build a tour with the Nearest Neighbour heuristic
    Stage 2  improve that tour with 2-opt
    Stage 3  show how sensitive the heuristic is to its starting city
    Stage 4  compare against the true optimum, when the input is small enough
    """
    city_count = len(names)
    dist = tsp.build_distance_matrix(coords)

    print_section("INPUT DATA")
    print("  Dataset: %s" % description)
    print("  Cities : %d" % city_count)
    print_city_table(names, coords)

    # -- Stage 1: the heuristic itself ------------------------------------
    print_section("STAGE 1 - NEAREST NEIGHBOUR HEURISTIC (starting at %s)"
                  % names[0])
    print()
    print("  Rule: from the current city, always move to the nearest city")
    print("        that has not been visited yet. Never reconsider.")

    nn_tour = tsp.nearest_neighbour_tour(dist, 0)
    print()
    print("  Tour found:")
    print(format_tour(names, nn_tour))
    nn_cost = print_leg_table(names, nn_tour, dist)

    # -- Stage 2: the improvement pass ------------------------------------
    print_section("STAGE 2 - 2-OPT IMPROVEMENT")
    print()
    print("  Repeatedly removes two edges and reconnects them the other way")
    print("  round whenever doing so shortens the tour. Stops when no single")
    print("  swap can improve the tour any further (a local optimum).")

    improved_tour, passes = tsp.two_opt(nn_tour, dist)
    improved_cost = tsp.tour_length(improved_tour, dist)

    print()
    print("  Improved tour:")
    print(format_tour(names, improved_tour))
    print_leg_table(names, improved_tour, dist)

    saving = nn_cost - improved_cost
    saving_percent = (saving / nn_cost * 100.0) if nn_cost > 0 else 0.0
    print()
    print("  Passes over the tour : %d" % passes)
    print("  Cost before 2-opt    : %10.2f" % nn_cost)
    print("  Cost after 2-opt     : %10.2f" % improved_cost)
    print("  Saving               : %10.2f  (%.2f%%)" % (saving, saving_percent))

    # -- Stage 3: start-city sensitivity ----------------------------------
    print_section("STAGE 3 - SENSITIVITY TO THE STARTING CITY")
    print()
    print("  A known weakness of Nearest Neighbour: the same set of cities")
    print("  produces different tours depending only on where we begin.")

    start_costs = tsp.nearest_neighbour_costs_by_start(dist)
    width = name_column_width(names)

    print()
    print("  %-*s %14s" % (width + 2, "Start city", "NN tour cost"))
    print("  " + "-" * (width + 17))

    # Find the best and worst starting cities with a single scan.
    cheapest_cost = start_costs[0]
    dearest_cost = start_costs[0]
    cheapest_index = 0
    dearest_index = 0
    for index in range(city_count):
        if start_costs[index] < cheapest_cost:
            cheapest_cost = start_costs[index]
            cheapest_index = index
        if start_costs[index] > dearest_cost:
            dearest_cost = start_costs[index]
            dearest_index = index

    for index in range(city_count):
        marker = ""
        if index == cheapest_index:
            marker = "  <- best"
        elif index == dearest_index:
            marker = "  <- worst"
        print("  %-*s %14.2f%s" % (width + 2, names[index], start_costs[index], marker))

    print("  " + "-" * (width + 17))
    spread = dearest_cost - cheapest_cost
    spread_percent = (spread / cheapest_cost * 100.0) if cheapest_cost > 0 else 0.0
    print("  Best start : %s (%.2f)" % (names[cheapest_index], cheapest_cost))
    print("  Worst start: %s (%.2f)" % (names[dearest_index], dearest_cost))
    print("  Spread     : %.2f  (%.2f%% worse from the wrong start)"
          % (spread, spread_percent))

    # Best tour over every starting city, then improved again with 2-opt.
    multi_tour, multi_cost, multi_start = tsp.best_nearest_neighbour_tour(dist)
    multi_improved, _ = tsp.two_opt(multi_tour, dist)
    multi_improved_cost = tsp.tour_length(multi_improved, dist)

    # -- Stage 4: validation against the true optimum ---------------------
    print_section("STAGE 4 - VALIDATION AGAINST THE TRUE OPTIMUM")

    total_possible_tours = factorial(city_count - 1)
    optimal_cost = None                      # stays None if the input is big

    if city_count <= tsp.BRUTE_FORCE_LIMIT:
        print()
        print("  Exhaustively checking all %s possible tours..."
              % format(total_possible_tours, ","))

        optimal_tour, optimal_cost, evaluated = tsp.brute_force_optimal(dist)

        print("  Tours evaluated: %s" % format(evaluated, ","))
        print()
        print("  Optimal tour:")
        print(format_tour(names, optimal_tour))
        print()
        print("  Optimal cost: %.2f" % optimal_cost)
    else:
        # Too many tours to check, so no optimality claim can be made.
        print()
        print("  Exhaustive search skipped.")
        print("  This instance has %d cities, which means %s possible tours -"
              % (city_count, format(total_possible_tours, ",")))
        print("  far too many to check one by one.")
        print()
        print("  This is exactly why a heuristic is needed: it returns a good")
        print("  tour in a fraction of a second, where exact search cannot")
        print("  finish at all.")

    # -- Final comparison --------------------------------------------------
    print_section("RESULTS SUMMARY")
    print()
    print("  %-38s %10s %12s" % ("Method", "Cost", "vs Optimal"))
    print("  " + "-" * 62)

    results = [
        ("Nearest Neighbour (from %s)" % names[0], nn_cost),
        ("  + 2-opt improvement", improved_cost),
        ("Best NN over all starts (%s)" % names[multi_start], multi_cost),
        ("  + 2-opt improvement", multi_improved_cost),
    ]
    if optimal_cost is not None:
        results.append(("Exhaustive search (true optimum)", optimal_cost))

    for label, cost in results:
        if optimal_cost is not None:
            gap = tsp.percentage_gap(cost, optimal_cost)
            gap_text = "%+.2f%%" % gap if gap > 1e-9 else "optimal"
        else:
            gap_text = "unknown"             # nothing to compare against
        print("  %-38s %10.2f %12s" % (label, cost, gap_text))

    print("  " + "-" * 62)

    print()
    if optimal_cost is not None:
        nn_gap = tsp.percentage_gap(nn_cost, optimal_cost)
        final_gap = tsp.percentage_gap(multi_improved_cost, optimal_cost)
        print("  Plain Nearest Neighbour was %.2f%% worse than the optimum." % nn_gap)
        if final_gap <= 1e-9:
            print("  After 2-opt and multi-start, the heuristic found the")
            print("  optimal tour - while checking only a tiny fraction of")
            print("  the %s possible tours." % format(total_possible_tours, ","))
        else:
            print("  After 2-opt and multi-start, the gap closed to %.2f%%."
                  % final_gap)
        print()
        print("  Note: matching the optimum here does NOT prove the heuristic")
        print("  always will. Dataset 2 is included to show a case where")
        print("  plain Nearest Neighbour performs badly.")
    else:
        print("  No optimality guarantee is available at this size - that is")
        print("  the trade-off a heuristic makes: speed in exchange for")
        print("  certainty.")


# ============================================================================
#  PART 4 - MAIN MENU
# ============================================================================

def main():
    """Show the menu, gather one dataset, analyse it, and repeat on request."""
    print_banner()

    while True:
        print()
        print("  Select input method:")
        print("    1. Use a built-in sample dataset")
        print("    2. Enter cities manually")
        print("    3. Generate random cities (seeded, reproducible)")
        print("    4. Exit")
        print()

        choice = read_choice("  Your choice: ", ["1", "2", "3", "4"])

        if choice == "4":
            print()
            print("  Program ended.")
            break

        if choice == "1":
            description, names, coords = choose_sample_dataset()
        elif choice == "2":
            description, names, coords = enter_cities_manually()
        else:
            description, names, coords = generate_random_cities()

        run_analysis(description, names, coords)

        print()
        again = read_choice("  Run another analysis? (y/n): ", ["y", "n"])
        if again == "n":
            print()
            print("  Program ended.")
            break


if __name__ == "__main__":
    # Catch Ctrl+C and end-of-input so the program exits tidily instead of
    # printing a stack trace.
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        print("  Program interrupted.")
