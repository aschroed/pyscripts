import sys
import argparse
from dcicutils import ff_utils as ff
from wranglertools.fdnDCIC import (
    get_FDN,
)


def get_excluded(exclude_types=None, include_types=None):
    # there are some types that we almost certainly want excluded
    exclude = ['User', 'Lab', 'Award', 'OntologyTerm', 'Ontology', 'Organism']
    if exclude_types is not None:
        exclude.extend(exclude_types)
    if include_types is not None:
        exclude = [ty for ty in exclude if ty not in include_types]
    return list(set(exclude))


def get_args():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='Add a tag to provided items (and optionally their children)',
        parents=[ff.input_arg_parser, ff.ff_arg_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--types2exclude',
                        nargs='+',
                        help="List of Item Types to Explicitly Exclude getting - \
                        by default 'User', 'Lab', 'Award', 'OntologyTerm', 'Ontology', \
                        and 'Organism' are excluded - add others using this argument")
    parser.add_argument('--types2include',
                        nargs='+',
                        help="List of Item Types (that are usually excluded - see \
                        --types2exclude help) that you want to include")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    try:
        connection = ff.fdn_connection(args.keyfile, keyname=args.key)
    except Exception as e:
        print("Connection failed")
        sys.exit(1)
    itemids = ff.get_item_ids_from_args(args.input, connection, args.search)
    excluded_types = get_excluded(args.types2exclude, args.types2include)
    all_linked_ids = []
    # main loop through the top level item ids
    for itemid in itemids:
        linked = ff.get_linked_items(connection, itemid, {})
        if excluded_types is not None:
            linked = ff.filter_dict_by_value(linked, excluded_types, include=False)
        ll = [(k, linked[k]) for k in sorted(linked, key=linked.get)]
        for i, t in ll:
            if i == itemid:
                print(i, '\t', t, '\tINPUT')
            else:
                print(i, '\t', t)
            if i not in all_linked_ids:
                all_linked_ids.append(i)
    for a in all_linked_ids:
        print(a)


if __name__ == '__main__':
    main()
