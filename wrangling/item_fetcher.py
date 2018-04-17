#!/usr/bin/env python3

import sys
import argparse
from dcicutils import ff_utils as ff
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
    #import pdb; pdb.set_trace()
    if args.fields:
        fields = args.fields

        header = '#id\t' + '\t'.join(fields)
        if args.noid is True:
            header = header.replace('#id\t', '#')
        print(header)
    for iid in id_list:
        res = fdnDCIC.get_FDN(iid, connection)
        if args.fields:
            line = ''
            for f in fields:
                val = res.get(f)
                if isinstance(val, list):
                    val = ', '.join(val)
                    if val.endswith(', '):
                        val = val[:-2]
                line = line + str(val) + '\t'
            if args.noid is False:
                line = iid + '\t' + line
            print(line)
        else:
            if args.noid is True:
                print(res)
            else:
                print(iid, '\t', res)


if __name__ == '__main__':
        main()
