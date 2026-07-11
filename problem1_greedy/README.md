# Problem 1 - Greedy

Owner: you
Algorithm: Activity Selection Problem

## Files
- `problem1_activity_selection.py` - main program (run with `python problem1_activity_selection.py`)
- `test_problem1_activity_selection.py` - test suite (run with `python -m pytest`)
- `sample_runs.txt` - sample runs for the report's testing section

## How it works
Sorts activities by end time (hand-written insertion sort, no built-in `sort()`/`sorted()` per the assignment rules), then greedily picks each activity whose start time is not before the last selected activity's end time.

## Notes for the report
- what the problem actually is
- how the greedy choice (earliest end time first) works and why it's optimal here
- how input/output works
- strengths/limitations: fast (O(n^2) due to manual sort, could be better with a smarter sort) and always optimal for this problem, but only works for single-resource scheduling
