import os
#import json
import sys
import argparse
#import datetime
from wranglertools.fdnDCIC import (
    FDN_Key,
    FDN_Connection,
    #get_FDN,
    patch_FDN
)

EPILOG = __doc__


def connect2server(keyfile, keyname, app=None):
    '''Sets up credentials for accessing the server.  Generates a key using info
       from the named keyname in the keyfile and checks that the server can be
       reached with that key.
       Also handles keyfiles stored in s3'''
    #if keyfile == 's3':
    #    assert app is not None
    #    s3bucket = app.registry.settings['system_bucket']
    #    #keyfile = get_key(bucket=s3bucket)

    key = FDN_Key(keyfile, keyname)
    connection = FDN_Connection(key)
    print("Running on: {server}".format(server=connection.server))
    # test connection
    if connection.check:
        return connection
    print("CONNECTION ERROR: Please check your keys.")
    return None


def get_list_from_file(fname):
    idl = []
    with open(fname) as infile:
        for l in infile:
            # print(l)
            ids = [i.strip() for i in l.split(',')]
            idl.extend(ids)
    return idl


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Given identifier Patch items status",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('field',
                        help="The field to update."),
    parser.add_argument('value',
                        help="The value to update."),
    parser.add_argument('--id_file',
                        help="File with list of IDs to update")
    parser.add_argument('--id_list',
                        nargs='+',
                        help="List of IDs to update")
    parser.add_argument('--update',
                        default=False,
                        action='store_true',
                        help="do the updates on the database")
    parser.add_argument('--key',
                        default='default',
                        help="The keypair identifier from the keyfile.  \
                        Default is --key=default")
    parser.add_argument('--keyfile',
                        default=os.path.expanduser("~/keypairs.json"),
                        help="The keypair file.  Default is --keyfile=%s" %
                             (os.path.expanduser("~/keypairs.json")))

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    connection = connect2server(args.keyfile, args.key)

    id_list = []
    if args.id_list:
        id_list = args.id_list
    elif args.id_file:
        id_list = get_list_from_file(args.id_file)
    else:
        print("NO IDs TO PROCESS - BYE NOW!")

    for iid in id_list:
        print("PATCHING", iid, "to", args.field, "=", args.value)
        if (args.update):
            # do the patch
            res = patch_FDN(iid, connection, {args.field: args.value})
            if res['status'] == 'success':
                print("SUCCESS!")
            else:
                print("FAILED TO PATCH", iid, "RESPONSE STATUS", res['status'], res['description'])
                # print(res)


if __name__ == '__main__':
    main()
