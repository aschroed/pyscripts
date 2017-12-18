#!/usr/bin/env python3

import os
import sys
import argparse
import json
from datetime import datetime
from wranglertools import fdnDCIC


def getArgs():  # pragma: no cover
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('infile',
                        help="the datafile containing object data to import")
    parser.add_argument('--key',
                        default='default',
                        help="The keypair identifier from the keyfile.  \
                        Default is --key=default")
    parser.add_argument('--keyfile',
                        default=os.path.expanduser("~/keypairs.json"),
                        help="The keypair file.  Default is --keyfile=%s" %
                             (os.path.expanduser("~/keypairs.json")))
    parser.add_argument('--update',
                        default=False,
                        action='store_true',
                        help="do the updates on the database")
    args = parser.parse_args()
    return args


def get_id(term):
    id_tag = term.get('uuid')
    if not id_tag:
        term.get('term_id')
    if not id_tag:
        term.get('term_name')
    return id_tag


def main():  # pragma: no cover
    start = datetime.now()
    print(str(start))
    args = getArgs()
    key = fdnDCIC.FDN_Key(args.keyfile, args.key)
    if key.error:
        sys.exit(1)
    connection = fdnDCIC.FDN_Connection(key)

    phase2 = {}
    # assumes a single line corresponds to json for single term
    if not args.update:
        print("DRY RUN - use --update to update the database")
    with open(args.infile) as terms:
        for t in terms:
            phase2json = {}
            term = json.loads(t)
            id_tag = get_id(term)
            if id_tag is None:
                print("No Identifier for ", term)
            else:
                tid = '/ontology-terms/' + id_tag
                # look for parents and remove for phase 2 loading if they are there
                if 'parents' in term:
                    phase2json['parents'] = term['parents']
                    del term['parents']
                if 'slim_terms' in term:
                    phase2json['slim_terms'] = term['slim_terms']
                    del term['slim_terms']

                dbterm = fdnDCIC.get_FDN(tid, connection)
                op = ''
                if 'OntologyTerm' in dbterm['@type']:
                    if args.update:
                        e = fdnDCIC.patch_FDN(dbterm["uuid"], connection, term)
                    else:
                        e = {'status': 'dry run'}
                    op = 'PATCH'
                else:
                    if args.update:
                        e = fdnDCIC.new_FDN(connection, 'OntologyTerm', term)
                    else:
                        e = {'status': 'dry run'}
                    op = 'POST'
                status = e.get('status')
                if status and status == 'dry run':
                    print(op, status)
                elif status and status == 'success':
                    print(op, status, e['@graph'][0]['uuid'])
                    if phase2json:
                        phase2[e['@graph'][0]['uuid']] = phase2json
                else:
                    print('FAILED', tid, e)

    print("START LOADING PHASE2 at ", str(datetime.now()))
    for tid, data in phase2.items():
        if args.update:
            e = fdnDCIC.patch_FDN(tid, connection, data)
        else:
            e = {'status': 'dry run'}
        status = e.get('status')
        if status and status == 'dry run':
            print('PATCH', status)
        elif status and status == 'success':
            print('PATCH', status, e['@graph'][0]['uuid'])
        else:
            print('FAILED', tid, e)
    end = datetime.now()
    print("FINISHED - START: ", str(start), "\tEND: ", str(end))


if __name__ == '__main__':
        main()
