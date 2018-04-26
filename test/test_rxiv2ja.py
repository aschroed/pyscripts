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


def test_remove_skipped_vals_w_good_atids(mocker):
    side_effect = ['uuid1', 'uuid2', 'uuid1', 'uuid2', 'uuid3']
    val = ['id1', 'id2']
    vals2skip = ['id1', 'id2', 'id3']
    # import pdb; pdb.set_trace()
    with mocker.patch('wrangling.script_utils.get_item_uuid',
                      side_effect=side_effect):
        result = rj.remove_skipped_vals(val, vals2skip)
        assert not result


def test_remove_skipped_vals_w_item_lookup(mocker):
    side_effect = ['uuid1', 'uuid2', 'uuid1']
    val = ['id1', 'id2']
    vals2skip = ['id1']
    # import pdb; pdb.set_trace()
    with mocker.patch('wrangling.script_utils.get_item_uuid',
                      side_effect=side_effect):
        result = rj.remove_skipped_vals(val, vals2skip)
        assert result[0] == val[1]


def test_remove_skipped_vals_w_item_lookup_and_not_found(mocker):
    side_effect = ['uuid1', None, 'uuid3', 'uuid1', None]
    val = ['id1', 'id2', 'id3']
    vals2skip = ['id3', 'id4']
    # import pdb; pdb.set_trace()
    with mocker.patch('wrangling.script_utils.get_item_uuid',
                      side_effect=side_effect):
        result = rj.remove_skipped_vals(val, vals2skip)
        assert result[0] == val[0]
