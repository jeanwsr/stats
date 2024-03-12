#!/usr/bin/env python
import shelve
import db
import argparse

def argument_parse():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                               description='')
    parser.add_argument("input",type=str,#default='dump',
                        help='')
    parser.add_argument("-s","--summary", action='store_true',
                        required=False,)
    return parser

parser = argument_parse()
if __name__ == '__main__':
    args=parser.parse_args()
    short = args.summary

    with shelve.open(args.input) as f:
        items = f.keys()
        #print(items[0])
        for serie in items:
            db.dump(f[serie], short)
            #print(serie)
