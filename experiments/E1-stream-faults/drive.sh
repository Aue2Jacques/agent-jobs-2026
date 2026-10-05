#!/bin/bash
# drive.sh <harness>: run all cases sequentially for one harness
h=$1; E=/workspace/harness-faults; cd $E
for c in OK EMPTY LEN0 CUT FLAKY TOOLOK TRUNCTOOL TOOLCUT STALL; do
  t=300; [ $c = STALL ] && t=720
  bash run.sh $h "CASE_${c}_$h please handle this request." $t ${h}_$c
  echo "$(date +%T) $h $c $(head -1 out/${h}_$c.meta)" >> out/progress.log
done
echo "$(date +%T) $h ALLDONE" >> out/progress.log
