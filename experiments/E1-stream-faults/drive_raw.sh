#!/bin/bash
h=$1; E=/workspace/harness-faults; cd $E
for c in NOFINISH INCOMPLETE BODYSTALL KEEPALIVE; do
  t=300; [ $c = BODYSTALL -o $c = KEEPALIVE ] && t=720
  PORT=4011 bash run.sh $h "RAW_${c} please handle this request ($h)." $t raw_${h}_$c
  echo "$(date +%T) $h RAW_$c $(head -1 out/raw_${h}_$c.meta)" >> out/progress_raw.log
done
echo "$(date +%T) $h ALLDONE" >> out/progress_raw.log
