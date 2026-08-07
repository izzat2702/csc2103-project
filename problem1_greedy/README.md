# Problem 1 - Greedy

Owner: Izzat
Algorithm: Activity Selection Problem

## Files
- `problem1_activity_selection.py` - main program, run with `python problem1_activity_selection.py`
- `activity_algorithms.py` - the algorithms on their own, no input/output
- `test_problem1_activity_selection.py` - pytest suite, run with `python -m pytest`
- `sample_runs/` - paired input/output files for the report

## Menu
1. Enter my own activities
2. Use a built-in sample dataset
3. Verify the greedy result against brute force (small inputs)
4. Run the test suite
5. Exit

Option 4 is the quickest way to confirm the program works.

## How it works
Sorts activities by end time using a hand-written insertion sort (no built-in
`sort()`/`sorted()`, per the assignment rules), then walks the sorted list once
and takes every activity that starts no earlier than the last selected one
finished.

## Why the greedy choice is right here
Option 3 checks this instead of just claiming it. It runs the greedy algorithm
and an exhaustive search over all 2^n subsets on the same input and reports
whether they agree. They always do, and the difference is always zero.

## Replaying the sample runs
```
python problem1_activity_selection.py < sample_runs/input_01_textbook.txt
```
Every `output_NN` file was generated this way, so they stay honest after any
change to the program.
