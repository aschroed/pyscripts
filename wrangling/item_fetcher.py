#!/usr/bin/env python3

import os
import argparse
import json
from datetime import datetime
from wranglertools import fdnDCIC
import urllib


def getArgs():  # pragma: no cover
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

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


def main():  # pragma: no cover
    # import pdb; pdb.set_trace()
    start = datetime.now()
    args = getArgs()
    key = fdnDCIC.FDN_Key(args.keyfile, args.key)
    if key.error:
        sys.exit(1)
    connection = fdnDCIC.FDN_Connection(key)
    capc_file = '/Users/andrew/Desktop/capc_aliases.txt'
    with open(capc_file) as fn:
        for l in fn:
            res = fdnDCIC.get_FDN(l.strip(), connection)
            if res.get('uuid'):
                print(res['uuid'])

    '''
    #    nofics = [n.strip() for n in list(fn)]

    #user_file = '/Users/andrew/Documents/work/4DN_Metadata/UsersLabsAwards/4DN_Users.csv'
    #with open(user_file) as uf:
    #    for l in uf:
    #        fields = l.split(',')
    #items = 'blah'
    #for item in items:
    #    fuuid = item['uuid']
    #    falias = item['aliases'][0]

        # with open(file2) as f2:
        #    for dlacc in f2:
        #        acnt += 1
        #        if dlacc.strip() not in dacc:
        #            print(dlacc.strip())
        #            mcnt += 1

        #if args.patchall:
        #    res = fdnDCIC.patch_FDN(fuuid, connection, {'status': 'released'})
        #    print(res['status'])
        #else:
        #    print("DRY RUN")
        #res = fdnDCIC.get_FDN(item, connection)
        #print(res)
        #print("Patching %s uuid: %s to status=released" % (falias, fuuid))
        #print(len(items))

        # print('FROM DATA CNT = ', len(items))
        # print('FROM DOWNLOAD CNT = ', acnt)
        # print('MISSING = ', mcnt)

    end = datetime.now()
    print("FINISHED - START: ", str(start), "\tEND: ", str(end))
    '''


if __name__ == '__main__':
        main()
