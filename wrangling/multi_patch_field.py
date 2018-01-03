import os
import sys
import argparse
from dcicutils import ff_utils as ff
from wranglertools.fdnDCIC import (
    patch_FDN
)


def get_args():
    parser = argparse.ArgumentParser(
        parents=[ff.input_arg_parser, ff.ff_arg_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('field',
                        help="The field to update."),
    parser.add_argument('value',
                        help="The value to update."),
    return parser.parse_args()


def main():
    args = get_args()
    try:
        connection = ff.fdn_connection(args.keyfile, keyname=args.key)
    except Exception as e:
        print("Connection failed")
        sys.exit(1)

    id_list = ff.get_item_ids_from_args(args.input, connection, args.search)

    for iid in id_list:
        print("PATCHING", iid, "to", args.field, "=", args.value)
        if (args.dbupdate):
            # do the patch
            res = patch_FDN(iid, connection, {args.field: args.value})
            if res['status'] == 'success':
                print("SUCCESS!")
            else:
                print("FAILED TO PATCH", iid, "RESPONSE STATUS", res['status'], res['description'])
                # print(res)


if __name__ == '__main__':
    main()
