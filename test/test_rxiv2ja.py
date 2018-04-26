import pytest
from wrangling import rxiv2ja as rj


def test_remove_skipped_vals_string_to_skip():
    val = 'test_tag'
    vals2skip = ['test_tag']
    result = rj.remove_skipped_vals(val, vals2skip)
    assert not result


def test_remove_skipped_vals_string_to_keep_w_no_vals2skip():
    val = 'test_tag'
    vals2skip = None
    result = rj.remove_skipped_vals(val, vals2skip)
    assert result == val


def test_remove_skipped_vals_string_to_keep_w_vals2skip():
    val = 'test_tag'
    vals2skip = ['some_other_val', 'and yet another']
    result = rj.remove_skipped_vals(val, vals2skip)
    assert result == val


def test_remove_skipped_vals_list_to_skip_2_items():
    val = ['test_val1', 'test_val2']
    vals2skip = ['test_val1', 'test_val2']
    result = rj.remove_skipped_vals(val, vals2skip)
    assert not result


def test_remove_skipped_vals_list_to_skip_remove_2_of_3():
    val = ['test_val1', 'test_val2', 'test_val3']
    vals2skip = ['test_val1', 'test_val2']
    result = rj.remove_skipped_vals(val, vals2skip)
    assert len(result) == 1
    assert result[0] == 'test_val3'


def test_remove_skipped_vals_no_vals_to_skip():
    val = ['test_val1', 'test_val2', 'test_val3']
    result = rj.remove_skipped_vals(val)
    assert result == val
