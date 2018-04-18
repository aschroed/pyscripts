import sys
import argparse
from dcicutils.ff_utils import fdn_connection
from dcicutils.submit_utils import get_FDN
from pyscripts.wrangling import script_utils as scu


def get_excluded(exclude_types=None, include_types=None):
    # there are some types that we almost certainly want excluded
    exclude = ['User', 'Lab', 'Award', 'OntologyTerm', 'Ontology', 'Organism', 'Publication']
    if exclude_types is not None:
        exclude.extend(exclude_types)
    if include_types is not None:
        exclude = [ty for ty in exclude if ty not in include_types]
    return list(set(exclude))


def is_released(itemid, connection):
    item = get_FDN(itemid, connection)
    if item.get('status'):
        if item['status'] == 'released':
            return True
    return False


def get_args():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='Add a tag to provided items (and optionally their children)',
        parents=[scu.create_input_arg_parser(), scu.create_ff_arg_parser()],
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
    parser.add_argument('--no_children',
                        nargs='+',
                        help="List of Item types not to get children of")
    parser.add_argument('--include_released',
                        default=False,
                        action='store_true',
                        help='Normally released items are skipped \
                        - this flag includes them in the final list'),
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    try:
        connection = fdn_connection(args.keyfile, keyname=args.key)
    except Exception as e:
        print("Connection failed")
        sys.exit(1)
    itemids = scu.get_item_ids_from_args(args.input, connection, args.search)
    excluded_types = get_excluded(args.types2exclude, args.types2include)
    no_child = ['Publication', 'Lab', 'User', 'Award']  # default no_childs
    if args.no_children:
        no_child = list(set(no_child.extend(args.no_children)))

    all_linked_ids = []
    # main loop through the top level item ids
    for itemid in itemids:
        linked = scu.get_linked_items(connection, itemid, {})
        if excluded_types is not None:
            linked = scu.filter_dict_by_value(linked, excluded_types, include=False)
        ll = [(k, linked[k]) for k in sorted(linked, key=linked.get)]
        for i, t in ll:
            suff = ''
            if i == itemid:
                suff = '\tINPUT'
            if is_released(i, connection):
                suff = '\tRELEASED' + suff
                if not args.include_released:
                    print(i, '\t', t, '\tSKIPPING', suff)
                    continue
            if i not in all_linked_ids:
                all_linked_ids.append(i)
            else:
                suff = suff + '\tSEEN'
            print(i, '\t', t, suff)
    for a in all_linked_ids:
        print(a)


if __name__ == '__main__':
    main()
