#!/usr/bin/env python
import shelve, sys
import db

with shelve.open(sys.argv[1]) as f:
    items = f.keys()
    #print(items[0])
    for serie in items:
        db.dump(f[serie])
        #print(serie)
