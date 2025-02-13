

## save
save data of a few points
```
stats.py -t 'xxx' -f PBE02 -m pddd --save ./shelf:name [--unit kcal] [--rscale 100] 
```
with `--xunit deg`, the rscale is not applied.

save data of one point (ref minimum)
```
stats_spc.py -t 'xxx' -f PBE02 -m pddd -l ref --save ./shelf
```
save data of one molecule
```
stats_spc.py -t 'sio_si.out' -f PBE02 -m pddd -l none --save ./shelf
```

## fit
calculate a few curves, and fit the minimum
```
fit.py shelf -t spc.toml:dataset -m curve -u ev
```
calculate a few equations
```
fit.py shelf -t spc.toml:dataset -m label
```
draw curves of them
```
fit.py shelf -t spc.toml:dataset -m curve -p [ -u eV ] [ -l 1 ]
```

For c2h4 (use submin)
```
fit.py c2h4 -t c2h4.toml -m curve -v 4 -p --xunit deg
```

Save txt for plot
```
fit.py shelf -t spc.toml:plot -m curve -l 4 --save
```

## plot
```
plot.py txt1,txt2 -u kcal
```
option
```
--xmin 0.9 --xmax 3.5 --ymax 10.0 -o n2_big
--xmin 1.0 --xmax 1.2 --ymin -240 --ymax -200 -o n2_small
```