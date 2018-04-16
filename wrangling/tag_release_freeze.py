import sys
import argparse
from collections import Counter
from dcicutils import ff_utils as ff
from wranglertools.fdnDCIC import (
    get_FDN,
    patch_FDN
)


def get_args():
    parser = argparse.ArgumentParser(
        parents=[ff.ff_arg_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('reltag',
                        help="The release tag to query DataReleaseUpdates and add to items.")
    return parser.parse_args()


def has_released(status):
    if 'released' in status:
        return True
    return False


def get_attype(res):
    ty = res.get('@type')
    if ty:
        ty = ty[0]
    return ty


def add_tag2item(connection, item, tag, seen, cnts, itype=None, dbupdate=False):
    # turns out that we do need to do a get as tags aren't embedded
    item = get_FDN(item, connection)
    status = item.get('status')
    uid = item.get('uuid')
    if (not uid) or (uid in seen):
        print("SEEN OR IDLESS ITEM - SKIPPING")
        cnts['skipped'] += 1
        return
    seen.append(uid)
    if has_released(status):
        attype = get_attype(item)
        if not attype:
            attype = itype
        patch = make_tag_patch(item, tag)
        if patch:
            do_patch(uid, attype, patch, connection, dbupdate, cnts)
        else:
            print('NOTHING TO PATCH - skipping ', uid)
            cnts['skipped'] += 1
    else:
        print("STATUS %s doesn't get tagged - skipping %s" % (status, uid))
        cnts['skipped'] += 1
    return item


def make_tag_patch(item, tag):
    if not ff.has_field_value(item, 'tags', tag):
        # not already tagged with this tag so make a patch and add 2 dict
        if item.get('tags'):
            tags = item['tags']
            tags.append(tag)
        else:
            tags = [tag]
        return {'tags': tags}
    return None


def do_patch(uid, type, patch, connection, dbupdate, cnts):
    if not dbupdate:
        print('DRY RUN - will update %s of type %s with %s' % (uid, type, patch))
        cnts['not_patched'] += 1
        return
    # import pdb; pdb.set_trace()
    res = patch_FDN(uid, connection, patch)
    # res = {'status': 'testing'}
    print('UPDATING - %s of type %s with %s' % (uid, type, patch))
    rs = res['status']
    print(rs)
    if rs == 'success':
        cnts['patched'] += 1
    else:
        cnts['errors'] += 1
        print(res)
    return


def main():
    args = get_args()
    dbupdate = args.dbupdate
    try:
        connection = ff.fdn_connection(args.keyfile, keyname=args.key)
    except Exception as e:
        print("Connection failed")
        sys.exit(1)

    cnts = Counter()
    reltag = args.reltag
    # build the search query string
    query = 'type=DataReleaseUpdate&update_tag=' + reltag
    relupdates = ff.get_item_ids_from_args([query], connection, True)
    update_items = []
    for u in relupdates:
        res = get_FDN(u, connection)
        for ui in res.get('update_items'):
            if ui.get('primary_id'):
                update_items.append(ui['primary_id'])
    seen = []
    # update_items = ['experiment-set-replicates/4DNESOI2ALTL']
    for item in update_items:
        res = get_FDN(item, connection)
        uid = res.get('uuid')
        type = get_attype(res)
        cnts[type] += 1
        if (not uid) or (uid in seen) or ('ExperimentSet' not in type):
            # case for first freeze (no processed files included)
            print("SKIPPING ", uid)
            cnts['skipped'] += 1
            continue
        add_tag2item(connection, uid, reltag, seen, cnts, type, dbupdate)

        if 'ExperimentSet' in type:
            # get the experiments and files
            exps = res.get('experiments_in_set')
            if exps is not None:
                cnts['Experiment'] += len(exps)
                for exp in exps:
                    # import pdb; pdb.set_trace()
                    exp = add_tag2item(connection, exp, reltag, seen, cnts, 'Experiment', dbupdate)
                    files = exp.get('files')
                    if files is not None:
                        cnts['FileFastq'] += len(files)
                        for file in files:
                            file = add_tag2item(connection, file, reltag, seen, cnts, 'FileFastq', dbupdate)
                    #epfiles = exp.get('processed_files')
                    epfiles = None  # case for first freeze (no processed files included)
                    if epfiles is not None:
                        cnts['FileProcessed'] += len(epfiles)
                        for epf in epfiles:
                            epf = add_tag2item(connection, epf, reltag, seen, cnts, 'FileProcessed', dbupdate)

            # check the processed files directly associated to the eset
            # pfiles = res.get('procesed_files')
            pfiles = None  # case for first freeze (no processed files included)
            if pfiles is not None:
                cnts['FileProcessed'] += len(pfiles)
                for pf in pfiles:
                    pf = add_tag2item(connection, pf, reltag, seen, cnts, 'FileProcessed', dbupdate)
    print(cnts)


if __name__ == '__main__':
    main()
