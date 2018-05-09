from wrangling import get_linked_item_ids as gli


def test_get_excluded_w_nothing():
    exclude = ['User', 'Lab', 'Award', 'OntologyTerm', 'Ontology', 'Organism', 'Publication']
    types = gli.get_excluded()
    assert sorted(exclude) == sorted(types)


def test_get_excluded_w_excludes():
    to_exclude = ['Biosample', 'Vendor', 'Award']
    types = gli.get_excluded(to_exclude)
    for te in to_exclude:
        assert te in types


def test_get_excluded_w_includes():
    to_include = ['User', 'Award']
    types = gli.get_excluded(include_types=to_include)
    for ti in to_include:
        assert ti not in types


def test_get_excluded_w_both():
    to_exclude = ['Biosample', 'Vendor', 'Award']
    to_include = ['User', 'Award']  # with Award in both it should be included
    types = gli.get_excluded(to_exclude, to_include)
    for te in to_exclude:
        if te == 'Award':
            continue
        assert te in types
    for ti in to_include:
        assert ti not in types


def test_is_released_released(mocker, connection):
    with mocker.patch('wrangling.get_linked_item_ids.get_FDN',
                      return_value={'status': 'released'}):
        ans = gli.is_released('iid', connection)
        assert ans is True


def test_is_released_not_released(mocker, connection):
    with mocker.patch('wrangling.get_linked_item_ids.get_FDN',
                      return_value={'status': 'deleted'}):
        ans = gli.is_released('iid', connection)
        assert not ans
