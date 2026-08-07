import pytest

from activity_algorithms import (
    manual_sort_by_end,
    select_activities,
    verify_selection,
    brute_force_max_count,
    generate_subsets,
    is_feasible_set,
    MAX_BRUTE_FORCE_N,
)
from problem1_activity_selection import format_selection_table


def test_manual_sort_by_end_orders_ascending():
    activities = [("C", 5, 9), ("A", 1, 4), ("B", 3, 5)]
    result = manual_sort_by_end(activities)
    assert result == [("A", 1, 4), ("B", 3, 5), ("C", 5, 9)]


def test_select_activities_empty_input_returns_empty():
    assert select_activities([]) == []


def test_select_activities_no_overlaps_selects_all():
    activities = [("A", 1, 2), ("B", 3, 4), ("C", 5, 6)]
    assert select_activities(activities) == [("A", 1, 2), ("B", 3, 4), ("C", 5, 6)]


def test_select_activities_all_overlapping_selects_one():
    activities = [("A", 1, 10), ("B", 2, 9), ("C", 3, 8)]
    assert select_activities(activities) == [("C", 3, 8)]


def test_select_activities_classic_textbook_case():
    activities = [
        ("A1", 1, 4), ("A2", 3, 5), ("A3", 0, 6), ("A4", 5, 7),
        ("A5", 3, 9), ("A6", 5, 9), ("A7", 6, 10), ("A8", 8, 11),
        ("A9", 8, 12), ("A10", 2, 14), ("A11", 12, 16),
    ]
    result = select_activities(activities)
    assert result == [
        ("A1", 1, 4), ("A4", 5, 7), ("A8", 8, 11), ("A11", 12, 16),
    ]


def test_select_activities_activity_touching_at_boundary_is_compatible():
    # activity starting exactly when the previous one ends is allowed
    activities = [("A", 1, 4), ("B", 4, 8)]
    assert select_activities(activities) == [("A", 1, 4), ("B", 4, 8)]


def test_select_activities_tie_on_end_time_keeps_stable_order():
    activities = [("A", 1, 5), ("B", 0, 5)]
    result = select_activities(activities)
    assert len(result) == 1
    assert result[0][2] == 5


def test_format_selection_table_empty_selection():
    assert format_selection_table([]) == "No activities selected."


def test_format_selection_table_lists_name_start_end_and_count():
    selected = [("A1", 1, 4), ("A4", 5, 7)]
    output = format_selection_table(selected)
    assert "A1" in output
    assert "A4" in output
    assert "1" in output and "4" in output
    assert "Total selected: 2" in output


def test_verify_selection_accepts_a_valid_selection():
    source = [("A", 1, 4), ("B", 3, 5), ("C", 5, 9)]
    ok, message = verify_selection([("A", 1, 4), ("C", 5, 9)], source)
    assert ok is True
    assert "2 activities" in message


def test_verify_selection_rejects_overlapping_activities():
    source = [("A", 1, 4), ("B", 3, 5)]
    ok, message = verify_selection([("A", 1, 4), ("B", 3, 5)], source)
    assert ok is False
    assert "overlap" in message


def test_verify_selection_rejects_an_activity_not_in_the_input():
    ok, message = verify_selection([("Ghost", 1, 2)], [("A", 1, 4)])
    assert ok is False
    assert "not in the input" in message


def test_verify_selection_rejects_a_duplicate():
    source = [("A", 1, 4)]
    ok, message = verify_selection([("A", 1, 4), ("A", 1, 4)], source)
    assert ok is False
    assert "more than once" in message


def test_verify_selection_accepts_boundary_touching_activities():
    source = [("A", 1, 4), ("B", 4, 8)]
    ok, _ = verify_selection([("A", 1, 4), ("B", 4, 8)], source)
    assert ok is True


def test_verify_selection_accepts_empty_selection():
    ok, _ = verify_selection([], [])
    assert ok is True


def test_generate_subsets_yields_two_to_the_n():
    subsets = list(generate_subsets(["a", "b", "c"]))
    assert len(subsets) == 8


def test_generate_subsets_includes_empty_and_full_sets():
    subsets = list(generate_subsets(["a", "b"]))
    assert [] in subsets
    assert ["a", "b"] in subsets


def test_generate_subsets_of_empty_list_is_one_empty_subset():
    assert list(generate_subsets([])) == [[]]


def test_is_feasible_set_true_for_non_overlapping():
    assert is_feasible_set([("A", 1, 4), ("B", 5, 9)]) is True


def test_is_feasible_set_true_for_boundary_touching():
    assert is_feasible_set([("A", 1, 4), ("B", 4, 9)]) is True


def test_is_feasible_set_false_for_overlapping():
    assert is_feasible_set([("A", 1, 5), ("B", 3, 9)]) is False


def test_brute_force_finds_the_textbook_optimum():
    activities = [
        ("A1", 1, 4), ("A2", 3, 5), ("A3", 0, 6), ("A4", 5, 7),
        ("A5", 3, 9), ("A6", 5, 9), ("A7", 6, 10), ("A8", 8, 11),
        ("A9", 8, 12), ("A10", 2, 14), ("A11", 12, 16),
    ]
    count, subset = brute_force_max_count(activities)
    assert count == 4
    assert is_feasible_set(subset) is True


def test_brute_force_refuses_oversized_input():
    too_many = [("A%d" % i, i, i + 1) for i in range(MAX_BRUTE_FORCE_N + 1)]
    with pytest.raises(ValueError):
        brute_force_max_count(too_many)
