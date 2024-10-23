

## save
save data of a few points
```
stats.py -t 'xxx' -f PBE02 -m pddd --save ./shelf 
```
save data of one point (ref minimum)
```
stats_spc.py -t 'xxx' -f PBE02 -m pddd -l ref --save ./shelf
```
save data of one molecule
```
stats_spc.py -t 'sio_si.out' -f PBE02 -m pddd -l none --save ./shelf
```

## fit
calculate a few curves, and fit the minimumm
```
fit.py shelf -t spc.toml -m curve -u ev
```