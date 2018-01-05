from wrangling import get_linked_item_ids as gli


def test_get_excluded_w_nothing():
    exclude = ['User', 'Lab', 'Award', 'OntologyTerm', 'Ontology', 'Organism']
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
