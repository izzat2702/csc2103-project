"""
CSC2103 - Problem 1: Activity Selection Problem
Core algorithms module.

This module holds the pure algorithmic logic - no input(), no print(). Keeping
it separate means the tests can import the algorithms without dragging the
console program along with them.

Assignment rules observed here:
  - the sort is a hand-written insertion sort, NOT the built-in sort()/sorted()
  - the subset enumeration is a hand-written binary counter, NOT itertools

An activity is a (name, start, end) tuple throughout.
"""

# Brute force explores 2**n subsets, so it is only offered for small inputs.
MAX_BRUTE_FORCE_N = 15


# ==== PART 1 - SORTING ====

def manual_sort_by_end(activities):
    """
    Insertion sort on end time, ascending.

    Written by hand because the brief forbids using a built-in sorting routine
    as part of the core algorithm. This sort is stable: activities that share
    an end time keep the order they were given in, because the comparison is a
    strict > rather than >=.
    """
    sorted_list = list(activities)
    for i in range(1, len(sorted_list)):
        current = sorted_list[i]
        j = i - 1
        while j >= 0 and sorted_list[j][2] > current[2]:
            sorted_list[j + 1] = sorted_list[j]
            j -= 1
        sorted_list[j + 1] = current
    return sorted_list


# ==== PART 2 - THE GREEDY ALGORITHM ====

def select_activities(activities):
    """
    Select the largest set of activities that can share one resource.

    The greedy choice is: of the activities still compatible with what has
    already been chosen, always take the one that finishes earliest. Finishing
    early leaves the most room for whatever comes next, so this choice never
    does worse than any alternative.

    Sorting by end time makes that choice trivial - the next compatible
    activity in the sorted list is by definition the earliest-finishing one,
    so a single left-to-right pass is enough.
    """
    if not activities:
        return []

    sorted_activities = manual_sort_by_end(activities)

    # The first activity in the sorted list finishes earliest overall, so the
    # greedy choice always takes it.
    selected = [sorted_activities[0]]
    last_end = sorted_activities[0][2]

    for activity in sorted_activities[1:]:
        start = activity[1]
        # Starting exactly when the last one ended is fine - no overlap.
        if start >= last_end:
            selected.append(activity)
            last_end = activity[2]

    return selected


# ==== PART 3 - INDEPENDENT VERIFICATION ====

def verify_selection(selected, source):
    """
    Check a selection without trusting the algorithm that produced it.

    This deliberately does not reuse any of the greedy logic. It re-derives the
    answer to "is this actually a valid set of non-overlapping activities from
    the given input?" from scratch, so that a bug in select_activities cannot
    hide behind a check that shares the same mistake.

    Returns (ok, message) where message is safe to print either way.
    """
    if not selected:
        return True, "nothing selected, nothing to check"

    # Every selected activity must actually have come from the input.
    for activity in selected:
        if activity not in source:
            return False, "%s is not in the input" % (activity[0],)

    # No activity may be selected twice.
    seen = []
    for activity in selected:
        if activity in seen:
            return False, "%s was selected more than once" % (activity[0],)
        seen.append(activity)

    # No two selected activities may overlap. Ordering by end time means it is
    # enough to compare each activity with the one before it: if every
    # consecutive pair is clear, every pair is clear.
    ordered = manual_sort_by_end(selected)
    for i in range(1, len(ordered)):
        previous_name, _, previous_end = ordered[i - 1]
        current_name, current_start, _ = ordered[i]
        if current_start < previous_end:
            return False, "%s and %s overlap" % (previous_name, current_name)

    return True, "%d activities, no overlaps" % len(selected)
