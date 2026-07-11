# Problem 1: Greedy Algorithm Implementation

## Problem Description

The Activity Selection Problem asks: given a set of activities, each with a
start time and an end time, and a single shared resource (e.g. one room, one
machine) that can only be used by one activity at a time, select the maximum
number of non-overlapping activities that can be performed using that
resource.

Formally, given activities A = {a1, a2, ..., an} where each activity ai has a
start time si and a finish time fi, the goal is to find the largest possible
subset of A such that no two selected activities overlap (i.e. for any two
selected activities, one must finish before or exactly when the other
starts).

## Greedy Strategy

The greedy choice used is: **always pick the activity that finishes earliest
among the remaining compatible activities.**

The algorithm works in two steps:

1. Sort all activities by their end (finish) time, ascending.
2. Walk through the sorted list once. Select the first activity. For every
   subsequent activity, select it only if its start time is greater than or
   equal to the end time of the most recently selected activity.

This greedy choice is suitable because finishing early leaves the most room
remaining for future activities — picking the activity that ends soonest
never does worse than any other valid choice, and can be proven optimal via
an exchange argument (any optimal solution can be rearranged to start with
the earliest-finishing activity without reducing the number of activities
selected). This also gives the problem optimal substructure: once the
earliest-finishing activity is chosen, the remaining problem is just Activity
Selection again on the activities compatible with it.

Per the assignment rules, sorting could not rely on a built-in `sort()` /
`sorted()` call since that would be using a library to solve part of the core
algorithmic task. A manual insertion sort was written instead
(`manual_sort_by_end`), keeping the sort itself within the "hand-written"
requirement.

## Input / Output Design

The program runs in the console and asks the user for:

1. How many activities there are.
2. For each activity, a single line: `name start_time end_time` (e.g.
   `A1 1 4`).

Input is validated — a non-numeric count or a malformed activity line (wrong
number of fields, non-numeric times, or a start time not before the end
time) causes a re-prompt rather than crashing the program.

The output is a simple formatted table of the selected activities (name,
start, end) followed by a total count, or `"No activities selected."` if the
input was empty.

Example interaction:

```
Activity Selection Problem (Greedy)
------------------------------------
How many activities? 4
Activity 1 - enter name, start time, end time (space separated, e.g. 'A1 1 4'): A1 1 4
Activity 2 - enter name, start time, end time (space separated, e.g. 'A1 1 4'): A2 3 5
Activity 3 - enter name, start time, end time (space separated, e.g. 'A1 1 4'): A3 0 6
Activity 4 - enter name, start time, end time (space separated, e.g. 'A1 1 4'): A4 5 7

Name      Start     End
A1        1         4
A4        5         7

Total selected: 2
```

## Key Code Snippets

Manual sort by end time (hand-written, no built-in sort used):

```python
def manual_sort_by_end(activities):
    sorted_list = list(activities)
    for i in range(1, len(sorted_list)):
        current = sorted_list[i]
        j = i - 1
        while j >= 0 and sorted_list[j][2] > current[2]:
            sorted_list[j + 1] = sorted_list[j]
            j -= 1
        sorted_list[j + 1] = current
    return sorted_list
```

Greedy selection loop:

```python
def select_activities(activities):
    if not activities:
        return []

    sorted_activities = manual_sort_by_end(activities)
    selected = [sorted_activities[0]]
    last_end = sorted_activities[0][2]

    for activity in sorted_activities[1:]:
        start = activity[1]
        if start >= last_end:
            selected.append(activity)
            last_end = activity[2]

    return selected
```

## Screenshots of Sample Runs

<!-- SCREENSHOTS GO HERE -->
<!-- Suggested: (1) the typical run above, (2) the invalid-input recovery
     case, (3) the zero-activities case. See problem1_greedy/sample_runs.txt
     for the exact inputs/outputs to reproduce for each screenshot. -->

## Strengths and Limitations

**Strengths**
- Always produces the optimal (maximum-count) solution for this specific
  problem — the greedy choice is provably correct here, unlike many greedy
  approaches which only give approximations.
- Simple and fast: after sorting, the selection pass is a single O(n) walk
  through the list.
- Handles edge cases cleanly: empty input, a single activity, fully
  overlapping activities, and activities that touch exactly at the boundary
  (one ending exactly when another starts) are all handled correctly and
  covered by automated tests.

**Limitations**
- The hand-written insertion sort is O(n^2) in the worst case, so for very
  large activity sets a faster sort (merge sort, quicksort) would scale
  better — though still hand-written to satisfy the assignment's no-built-in
  rule.
- The algorithm only handles a single shared resource. If there were
  multiple identical resources (e.g. 3 interchangeable rooms), this exact
  approach would need to be extended (e.g. run repeatedly, or track multiple
  "last end time" slots).
- Ties on end time are broken by whichever activity appears first in the
  input after sorting (a stable sort), which is a reasonable default but not
  something the user can otherwise control.
