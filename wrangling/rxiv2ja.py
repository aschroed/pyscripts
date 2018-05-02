#!/usr/bin/env python3

import sys
import argparse
from dcicutils.ff_utils import fdn_connection
from dcicutils.submit_utils import get_FDN, patch_FDN
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
    parser.add_argument('--vals2skip',
                        nargs='+',
                        help="A list of values or IDs (uuids, accessions ...) to not transfer")

    return parser.parse_args()


def remove_skipped_vals(val, vals2skip=None, connection=None):
    if not vals2skip:
        return val
    is_string = False
    if isinstance(val, str):
        val = [val]
        is_string = True

    val = [v for v in val if v not in vals2skip]
    if connection:
        vuuids = [scu.get_item_uuid(v, connection) for v in val]
        skuids = [scu.get_item_uuid(v, connection) for v in vals2skip]
        for i, v in enumerate(vuuids):
            if v is not None:
                if v in skuids:
                    del val[i]
    if val:
        if is_string:
            return val[0]
        return val
    return None


def transfer_from_old2new(old, new, fields2move, vals2skip=None):
    # build the patch dictionary
    ja_patch_dict = {}
    skipped = {}  # has info on skipped fields
    for f in fields2move:
        val = old.get(f)
        if val:
            val = remove_skipped_vals(val, vals2skip)
            jval = new.get(f)  # see if the field already has data in new item
            if jval:
                skipped[f] = {'old': val, 'new': jval}
                continue
            ja_patch_dict[f] = val
    return ja_patch_dict, skipped


def move_old_url_to_new_aka(oldurl, patch, skip):
    aka = patch.get('aka')
    if aka:
        skip['aka'] = {'old': patch['url'], 'new': aka}
    patch['aka'] = oldurl
    return patch, skip


def patch_and_report(connection, patch_d, skipped, uuid2patch, dryrun):
    # report and patch
    if dryrun:
        print('DRY RUN - nothing will be patched to database')
    if skipped:
        print('WARNING! - SKIPPING for ', uuid2patch)
        for f, v in skipped.items():
            print('Field: %s\tHAS: %s\tNOT ADDED: %s' % (f, v['new'], v['old']))

    if not patch_d:
        print('NOTHING TO PATCH - ALL DONE!')
    else:
        print('PATCHING - ', uuid2patch)
        for f, v in patch_d.items():
            print(f, '\t', v)

        if not dryrun:
            # do the patch
            res = patch_FDN(uuid2patch, connection, patch_d)
            if res['status'] == 'success':
                print("SUCCESS!")
                return True
            else:
                print("FAILED TO PATCH", uuid2patch, "RESPONSE STATUS", res['status'], res['description'])
                return False
    return True


def main():  # pragma: no cover
    args = get_args()
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
        sys.exit(1)
    if jarticle.get('status') == 'error':
        print('Journal Article record %s cannot be found' % args.new)
        sys.exit(1)
    # make sure we can get the uuid to patch
    juuid = jarticle.get('uuid')
    # build the patch dictionary
    fields2transfer = ['categories', 'exp_sets_prod_in_pub', 'exp_sets_used_in_pub']
    patch_dict, skipped = transfer_from_old2new(biorxiv, jarticle, fields2transfer, args.vals2skip)
    if 'url' in biorxiv:
        patch_dict, skipped = move_old_url_to_new_aka(biorxiv['url'], patch_dict, skipped)

    # do the patch
    ok = patch_and_report(connection, patch_dict, skipped, juuid, dryrun)

    if not ok:
        break  # bail out if initial transfer doesn't work

    # find items with reference to old paper
    buuid = biorxiv.get('uuid')
    search = "type=Item&references.uuid=" + buuid
    itemids = scu.get_item_ids_from_args([search], connection, True)
    complete = True
    if not itemids:
        print("No references to %s found." % buuid)
    for iid in itemids:
        ok = patch_and_report(connection, {'references': [juuid]}, None, iid, dryrun)
        if not ok and complete:
            complete = False
    if not complete:
        print("ALL REFERENCES POINTING TO %s NOT UPDATED - CHECK AND FIX!" % buuid)


if __name__ == '__main__':
        main()
