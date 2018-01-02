import pytest
from wrangling import tagger as t


@pytest.fixture
def connection(mocker):
    return mocker.patch.object(t, 'fdn_connection')


@pytest.fixture
def items_w_uuids():
    return [
        {'name': 'one', 'uuid': 'a'},
        {'name': 'two', 'uuid': 'b'},
        {'name': 'three', 'uuid': 'c'},
    ]


def test_get_item_ids_from_list(connection):
    ids = ['a', 'b', 'c']
    result = t.get_item_ids_from_args(ids, connection)
    for a in [i in ids for i in result]:
        assert a


def test_get_item_ids_from_search(mocker, connection, items_w_uuids):
    ids = ['a', 'b', 'c']
    with mocker.patch('wrangling.tagger.get_FDN', return_value=items_w_uuids):
        result = t.get_item_ids_from_args('search', connection, True)
        for a in [i in ids for i in result]:
            assert a


def test_make_tag_patch_no_existing_tags():
    item = {'uuid': 'a'}
    tag = 'test_tag'
    patch = t.make_tag_patch(item, tag)
    assert patch.get('tags')
    assert patch['tags'][0] == tag


def test_make_tag_patch_w_existing_tags():
    item = {'uuid': 'a', 'tags': ['my_tag']}
    tag = 'test_tag'
    import pdb; pdb.set_trace()
    patch = t.make_tag_patch(item, tag)
    assert patch.get('tags')
    tags = patch.get('tags')
    assert len(tags) == 2
    assert tag in tags
    assert 'my_tag' in tags
