"""
CSC2103 - Problem 1: Activity Selection Problem using a Greedy Algorithm

Console program. Run it interactively:
    python problem1_activity_selection.py

or replay a saved scenario:
    python problem1_activity_selection.py < sample_runs/input_01_textbook.txt

The algorithms live in activity_algorithms.py. This file only deals with the
menu, reading input, formatting output, and running the test suite.
"""

import activity_algorithms as alg

RULE_WIDTH = 68


# ==== PART 1 - SCREEN LAYOUT ====

def print_rule(character="="):
    print(character * RULE_WIDTH)


def print_banner():
    print_rule("=")
    print(" CSC2103 - Problem 1: Activity Selection using a Greedy Algorithm")
    print_rule("=")
    print("Given a set of activities that all need the same single resource,")
    print("select the largest number of them that do not overlap.")


def print_section(title):
    print()
    print("--- %s ---" % title)


# ==== PART 2 - INPUT ====

def read_line(prompt):
    """
    Read one line of input.

    When input is piped from a file it eventually runs out, which raises
    EOFError. Treating that as "the scenario is finished" lets the saved sample
    runs replay cleanly instead of ending in a traceback.
    """
    try:
        return input(prompt)
    except EOFError:
        print()
        print("End of input reached. Exiting.")
        raise SystemExit(0)


def read_int(prompt, minimum, maximum=None):
    """Keep asking until the answer is a whole number inside the range."""
    while True:
        raw = read_line(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if value < minimum:
            print("  Please enter a number of at least %d." % minimum)
            continue
        if maximum is not None and value > maximum:
            print("  Please enter a number no greater than %d." % maximum)
            continue
        return value


def read_activities():
    """Ask how many activities there are, then read that many of them."""
    count = read_int("Number of activities: ", 0)

    activities = []
    for i in range(count):
        while True:
            raw = read_line(
                "  Activity %d - name start end (e.g. A1 1 4): " % (i + 1))
            parts = raw.split()

            if len(parts) != 3:
                print("    Expected three values: name start end.")
                continue

            name = parts[0]
            try:
                start = int(parts[1])
                end = int(parts[2])
            except ValueError:
                print("    Start and end must be whole numbers.")
                continue

            if start >= end:
                print("    Start time must be before end time.")
                continue

            activities.append((name, start, end))
            break

    return activities


# ==== PART 3 - OUTPUT ====

def describe_activities(activities):
    """One-line summary, used by the test suite output."""
    if not activities:
        return "(none)"
    return ", ".join("%s(%d-%d)" % (n, s, e) for n, s, e in activities)


def format_selection_table(selected):
    """
    Build the results table as a string rather than printing it, so the
    automated tests can assert on the exact output.
    """
    if not selected:
        return "No activities selected."

    lines = ["%-12s %-8s %-8s" % ("Name", "Start", "End")]
    for name, start, end in selected:
        lines.append("%-12s %-8d %-8d" % (name, start, end))
    lines.append("")
    lines.append("Total selected: %d" % len(selected))
    return "\n".join(lines)


def print_activity_table(title, activities):
    print_section(title)
    if not activities:
        print("  (none)")
        return
    print("  %-12s %-8s %-8s" % ("Name", "Start", "End"))
    print("  %-12s %-8s %-8s" % ("-" * 12, "-" * 8, "-" * 8))
    for name, start, end in activities:
        print("  %-12s %-8d %-8d" % (name, start, end))


def run_and_report(activities):
    """Select, show the result, then independently verify it."""
    print_activity_table("Input activities", activities)

    selected = alg.select_activities(activities)

    print_section("Selected activities (greedy)")
    print(format_selection_table(selected))

    ok, message = alg.verify_selection(selected, activities)
    print()
    print("Verification: %s - %s" % ("PASSED" if ok else "FAILED", message))


# ==== PART 4 - SAMPLE DATASETS ====

SAMPLE_DATASETS = [
    ("Textbook example - 11 activities",
     [("A1", 1, 4), ("A2", 3, 5), ("A3", 0, 6), ("A4", 5, 7),
      ("A5", 3, 9), ("A6", 5, 9), ("A7", 6, 10), ("A8", 8, 11),
      ("A9", 8, 12), ("A10", 2, 14), ("A11", 12, 16)]),

    ("Meeting room bookings - 7 requests",
     [("Standup", 9, 10), ("Design", 9, 12), ("OneOnOne", 10, 11),
      ("Review", 11, 13), ("Lunch", 12, 13), ("Retro", 13, 15),
      ("Planning", 14, 16)]),

    ("All overlapping - only one can run",
     [("Alpha", 1, 10), ("Bravo", 2, 9), ("Charlie", 3, 8),
      ("Delta", 4, 7), ("Echo", 5, 6)]),

    ("No overlaps - every activity fits",
     [("P1", 1, 2), ("P2", 3, 4), ("P3", 5, 6), ("P4", 7, 8), ("P5", 9, 10)]),

    ("Back-to-back chain - each starts as the last ends",
     [("S1", 0, 2), ("S2", 2, 4), ("S3", 4, 6), ("S4", 6, 8), ("S5", 8, 10)]),
]


def choose_sample():
    """Let the user pick a built-in dataset. Returns the activity list."""
    print_section("Sample datasets")
    for i, (description, activities) in enumerate(SAMPLE_DATASETS, start=1):
        print("  %d. %s  (%d activities)" % (i, description, len(activities)))

    choice = read_int("Choose a dataset (1 to %d): " % len(SAMPLE_DATASETS),
                      1, len(SAMPLE_DATASETS))
    description, activities = SAMPLE_DATASETS[choice - 1]
    print("Loaded: %s" % description)
    return activities


# ==== PART 5 - TEST SUITE ====

# (name, activities, expected selection)
# Imported by test_problem1_activity_selection.py as well, so the automated
# tests and the in-program suite can never disagree about the right answer.
TEST_CASES = [
    ("Empty input", [], []),

    ("Single activity", [("A", 1, 5)], [("A", 1, 5)]),

    ("No overlaps - all selected",
     [("A", 1, 2), ("B", 3, 4), ("C", 5, 6)],
     [("A", 1, 2), ("B", 3, 4), ("C", 5, 6)]),

    ("All overlapping - one selected",
     [("A", 1, 10), ("B", 2, 9), ("C", 3, 8)],
     [("C", 3, 8)]),

    ("Textbook example - 11 activities",
     [("A1", 1, 4), ("A2", 3, 5), ("A3", 0, 6), ("A4", 5, 7),
      ("A5", 3, 9), ("A6", 5, 9), ("A7", 6, 10), ("A8", 8, 11),
      ("A9", 8, 12), ("A10", 2, 14), ("A11", 12, 16)],
     [("A1", 1, 4), ("A4", 5, 7), ("A8", 8, 11), ("A11", 12, 16)]),

    ("Touching at the boundary is compatible",
     [("A", 1, 4), ("B", 4, 8)],
     [("A", 1, 4), ("B", 4, 8)]),

    ("Unsorted input is handled",
     [("C", 5, 9), ("A", 1, 4), ("B", 3, 5)],
     [("A", 1, 4), ("C", 5, 9)]),
]


def run_tests():
    """
    Run every case and print expected against actual.

    Each selection produced is also put through verify_selection, so a case
    only passes if it both matches the expected answer and survives an
    independent check.
    """
    print()
    print_rule("=")
    print(" TEST SUITE - expected vs actual")
    print_rule("=")

    passed = 0
    for name, activities, expected in TEST_CASES:
        actual = alg.select_activities(activities)
        ok = (actual == expected)

        if actual:
            valid, message = alg.verify_selection(actual, activities)
            detail = "verified: %s" % message
            if not valid:
                ok = False
        else:
            detail = "nothing selected, nothing to verify"

        if ok:
            passed += 1

        print()
        print("Test: %s" % name)
        print("  Expected : %s" % describe_activities(expected))
        print("  Actual   : %s" % describe_activities(actual))
        print("  Check    : %s" % detail)
        print("  Result   : %s" % ("PASS" if ok else "FAIL"))

    print()
    print_rule("=")
    print("%d of %d tests passed." % (passed, len(TEST_CASES)))
    print_rule("=")


# ==== PART 6 - BRUTE FORCE COMPARISON ====

def compare_with_brute_force(activities):
    """
    Run the greedy algorithm and the exhaustive search on the same input and
    show whether they agree.

    Problem 3 prints how far its heuristic falls short of the optimum. This is
    the same comparison for Problem 1, and the difference is always zero -
    which is exactly the point about the greedy choice here. It is not a
    heuristic that usually works; it provably finds the maximum.
    """
    print_activity_table("Input activities", activities)

    selected = alg.select_activities(activities)

    try:
        best_count, best_subset = alg.brute_force_max_count(activities)
    except ValueError as error:
        print()
        print("Cannot brute force this input: %s" % error)
        print("Brute force checks 2^n subsets, so it is only practical on")
        print("small inputs. The greedy result is shown below regardless.")
        print_section("Greedy result")
        print(format_selection_table(selected))
        return

    print_section("Greedy result")
    print(format_selection_table(selected))

    print_section("Brute force result (every subset checked)")
    print(format_selection_table(alg.manual_sort_by_end(best_subset)))

    ok, message = alg.verify_selection(selected, activities)

    print()
    print_rule("-")
    print("Greedy selected  : %d activities" % len(selected))
    print("True optimum     : %d activities" % best_count)
    print("Difference       : %d" % (best_count - len(selected)))
    print("Greedy is valid  : %s (%s)" % ("yes" if ok else "no", message))
    if len(selected) == best_count:
        print("Verdict          : MATCH - the greedy choice found the optimum")
    else:
        print("Verdict          : MISMATCH - the greedy result is not optimal")
    print_rule("-")


# ==== PART 7 - MAIN MENU ====

def main():
    print_banner()

    while True:
        print_section("Main menu")
        print("  1. Enter my own activities")
        print("  2. Use a built-in sample dataset")
        print("  3. Verify the greedy result against brute force (small inputs)")
        print("  4. Run the test suite")
        print("  5. Exit")

        choice = read_int("Select an option (1 to 5): ", 1, 5)

        if choice == 1:
            run_and_report(read_activities())

        elif choice == 2:
            run_and_report(choose_sample())

        elif choice == 3:
            print()
            print("Brute force checks every possible subset, so keep this to")
            print("at most %d activities." % alg.MAX_BRUTE_FORCE_N)
            compare_with_brute_force(read_activities())

        elif choice == 4:
            run_tests()

        elif choice == 5:
            print()
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()
