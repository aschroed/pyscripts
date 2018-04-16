#!/usr/bin/env python3

import os
import sys
import argparse
from dcicutils import ff_utils as ff
from datetime import datetime
from wranglertools import fdnDCIC


def get_args():
    parser = argparse.ArgumentParser(
        parents=[ff.input_arg_parser, ff.ff_arg_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--fields',
                        nargs='+',
                        help="The item fields to retrieve/report.")
    parser.add_argument('--noid',
                        action='store_true',
                        default='False')

    return parser.parse_args()


def main():  # pragma: no cover
    args = get_args()
    try:
        connection = ff.fdn_connection(args.keyfile, keyname=args.key)
    except Exception as e:
        print("Connection failed")
        sys.exit(1)

    id_list = ff.get_item_ids_from_args(args.input, connection, args.search)
    if args.fields:
        fields = args.fields

        header = '#id\t' + '\t'.join(fields)
        if args.noid:
            header = header.replace('#id\t', '#')
        print(header)
    for iid in id_list:
        res = fdnDCIC.get_FDN(iid, connection)
        if args.fields:
            lstart = iid + '\t'
            line = lstart + '\t'.join([res.get(f) for f in fields])
            if args.noid:
                line = line.replace(lstart, '')
            print(line)
        else:
            if args.noid:
                print(res)
            else:
                print(iid, '\t', res)


if __name__ == '__main__':
        main()
