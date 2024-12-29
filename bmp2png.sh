#!/bin/bash
suf=$1
xscale=$2
yscale=$3
for i in `ls $suf*.bmp`
do 
p=${i/bmp/png}
p1=${i/.bmp/c.png}
magick $i $p
magick $p -gravity Center -crop ${xscale}%x${yscale}% ${p1}
done
