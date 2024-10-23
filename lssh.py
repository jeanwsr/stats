#!/usr/bin/env python
import shelve
import db
import argparse
from fit import get_elabel

def argument_parse():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                               description='')
    parser.add_argument("input",type=str,#default='dump',
                        help='')
    parser.add_argument("-s","--summary", action='store_true',
                        required=False,)
    parser.add_argument("-e","--energy", action='store_true',
                        required=False,)
    parser.add_argument("-n","--name",dest='name',metavar='name',type=str,
                        required=False,)
    return parser

parser = argument_parse()
if __name__ == '__main__':
    args=parser.parse_args()
    short = args.summary
    name = args.name
    

    with shelve.open(args.input) as f:
        items = f.keys()
        #print(items[0])
        for serie in items:
            if name is not None:
                if name not in serie:
                    continue
            print(serie)
            if 'spc' in serie:
                db.dump_spc(f[serie], short)
            else:
                db.dump(f[serie], short)
        if args.energy:
            get_elabel(args.input)
