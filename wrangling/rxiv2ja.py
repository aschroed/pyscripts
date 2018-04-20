#!/usr/bin/env python3

import sys
import argparse
from dcicutils.ff_utils import fdn_connection
from dcicutils.submit_utils import get_FDN  # , patch_FDN
from pyscripts.wrangling import script_utils as scu


def get_args():
    parser = argparse.ArgumentParser(
        parents=[scu.create_ff_arg_parser()],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('old',
                        help="The uuid or ID of the Biorxiv publication")
    parser.add_argument('new',
                        help="The uuid or ID of the Published Journal Article")

    return parser.parse_args()


def main():  # pragma: no cover
    args = get_args(sys.argv[1:])
    try:
        connection = fdn_connection(args.keyfile, keyname=args.key)
    except Exception as e:
        print("Connection failed")
        sys.exit(1)

    dryrun = not args.dbupdate

    biorxiv = get_FDN(args.old, connection)
    jarticle = get_FDN(args.new, connection)

    if biorxiv.get('status') == 'error':
        print('Biorxiv record %s cannot be found' % args.old)
    if jarticle.get('status') == 'error':
        print('Journal Article record %s cannot be found' % args.new)

    # build the patch dictionary
    uuid2patch = jarticle.get('uuid')
    fields2transfer = ['categories', 'exp_sets_prod_in_pub', 'exp_sets_used_in_pub', 'url']
    ja_patch_dict = {}
    skipped = {}  # has info on skipped fields
    for f in fields2transfer:
        val = biorxiv.get(f)
        if val:
            if f == 'url':
                f = 'aka'
            jval = jarticle.get(f)  # see if the field already has data in new item
            if jval:
                skipped[f] = {'old': val, 'new': jval}
                continue
            ja_patch_dict[f] = val

    # report and patch
    if dryrun:
        print('DRY RUN - nothing will be patched to database')
    if skipped:
        print('WARNING! - SKIPPING for ', args.new)
        for f, v in skipped.items():
            print('Field: %s\tHAS: %s\tNOT ADDED: %s' % (f, v['new'], v['old']))

    if not ja_patch_dict:
        print('NOTHING TO PATCH - ALL DONE!')
    else:
        print('PATCHING - ', args.new)
        for f, v in ja_patch_dict.items():
            print(f, '\t', v)

        if not dryrun:
            # do the patch
            res = {'status': 'success'}
            #res = patch_FDN(uuid2patch, connection, ja_patch_dict)
            if res['status'] == 'success':
                print("SUCCESS!")
            else:
                print("FAILED TO PATCH", uuid2patch, "RESPONSE STATUS", res['status'], res['description'])


if __name__ == '__main__':
        main()
