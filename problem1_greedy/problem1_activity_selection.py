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


def main():
    """Placeholder until Task 6 builds the menu."""
    print_banner()
    run_and_report(read_activities())


if __name__ == "__main__":
    main()
