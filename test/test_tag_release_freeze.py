# import pytest
from wrangling import tag_release_freeze as trf


def test_has_released_released():
    relstatus = ['released', 'released to project']
    for s in relstatus:
        res = trf.has_released(s)
        assert res is True


def test_has_released_not_released():
    relstatus = ['in review by lab', 'archived', 'deleted', 'current',
                 'submission in progress', 'obsolete']
    for s in relstatus:
        res = trf.has_released(s)
        assert not res


def test_get_attype_w_attype():
    res = {'@type': ['FileFastq', 'File', 'Item']}
    ty = trf.get_attype(res)
    assert ty == 'FileFastq'


def test_get_attype_w_no_attype():
    res = {'uuif': 'test_uuid'}
    ty = trf.get_attype(res)
    assert ty is None


def test_add_tag2item_no_uid(capsys, mocker, connection):
    with mocker.patch('wrangling.tag_release_freeze.get_FDN', return_value={'status': 'released'}):
        trf.add_tag2item(connection, 'iid', 'test_tag', [], {})
        out = capsys.readouterr()[0]
        assert "SEEN OR IDLESS ITEM - SKIPPING" in out
