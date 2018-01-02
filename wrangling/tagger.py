import sys
import os
import argparse
from utils.dcicutils.ff_utils import (
    fdn_connection,
    get_types_that_can_have_field,
    get_linked_items,
    filter_dict_by_value,
    has_field_value,
    get_item_type
)
from wranglertools.fdnDCIC import (
    FDN_Connection,
    get_FDN,
    patch_FDN
)


def make_tag_patch(item, tag):
    if item.get('tags'):
        tags = item['tags']
        tags.append(tag)
    else:
        tags = [tag]
    return {'tags': tags}


def get_item_ids_from_args(id_input, connection, is_search=False):
    '''depending on the args passed return a list of item ids'''
    if is_search:
        urladdon = 'search/?limit=all&' + id_input
        result = get_FDN(None, connection, None, urladdon)
        return list(set([item.get('uuid') for item in result]))
    try:
        with open(id_input[0]) as inf:
            return [l.strip() for l in inf]
    except FileNotFoundError:
        return id_input


def get_args():  # pragma: no cover
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('tag',
                        help="The tag you want to add - eg. '4DN Standard'")
    parser.add_argument('input', nargs='+',
                        help="a list of ids of top level objects, \
                        a file containing said ids one per line or a search \
                        string (with --search option)")
    parser.add_argument('--search',
                        default=False,
                        action='store_true',
                        help='Include if you are passing in a search string \
                        eg. type=Biosource&biosource_type=primary cell&frame=raw')
    parser.add_argument('--taglinked',
                        default=False,
                        action='store_true',
                        help='Tag items linked to items that are input')
    parser.add_argument('--types2exclude',
                        nargs='+',
                        help="List of Item Types to Explicitly Exclude Tagging - \
                        you may have some linked items that can get tags but may \
                        not want to tag them with this tag")
    parser.add_argument('--key',
                        default='default',
                        help="The keypair identifier from the keyfile.  \
                        Default is --key=default")
    parser.add_argument('--keyfile',
                        default=os.path.expanduser("~/keypairs.json"),
                        help="The keypair file.  Default is --keyfile=%s" %
                             (os.path.expanduser("~/keypairs.json")))
    parser.add_argument('--patchall',
                        default=False,
                        action='store_true',
                        help="PATCH existing objects.  Default is False \
                        and will only PATCH with user override")
    args = parser.parse_args()
    return args


def main():
    #import pdb; pdb.set_trace()
    args = get_args()
    try:
        connection = fdn_connection(args.keyfile, keyname=args.key)
    except Exception as e:
        print("Connection failed")
        sys.exit(1)
    #import pdb; pdb.set_trace()
    itemids = get_item_ids_from_args(args.input, connection, args.search)
    taggable = get_types_that_can_have_field(connection, 'tags')
    if args.types2exclude is not None:
        # remove explicitly provide types not to tag
        taggable = [t for t in taggable if t not in args.types2exclude]

    seen = [] # only need to add tag once so this keeps track of what's been seen
    to_patch = {} # keep track of those to patch
    # main loop through the top level item ids
    for itemid in itemids:
        items2tag = {}
        if args.taglinked:
            # need to get linked items and tag them
            linked = get_linked_items(connection, itemid)
            items2tag = filter_dict_by_value(linked, taggable, include=True)
        else:
            # only want to tag provided items
            itype = get_item_type(connection, itemid)
            if itype in taggable:
                items2tag = {itemid: itype}
        for i, t in items2tag.items():
            if i not in seen:
                seen.append(i)
                item = get_FDN(i, connection)
                if not has_field_value(item, 'tags', args.tag):
                    # not already tagged so make a patch and add 2 dict
                    to_patch[i] = make_tag_patch(item, args.tag)

    # now do the patching or reporting
    for pid, patch in to_patch.items():
        if args.patchall:
            pres = patch_FDN(i, connection, patch)
            print(pres)
        else:
            print("DRY RUN: patch ", pid, " with ", patch)


if __name__ == '__main__':
    main()
