#!/bin/sh
# the switch-flip arms over all 182 losses, 12 at a time, one arm after another
cd "$(dirname "$0")"
python3 fa.py run eqqF=final:mr_eqq_symbolic=false losses.tsv 02-arm-eqqF.out -j 12
python3 fa.py run substT=final:mr_subst_simp=true losses.tsv 02-arm-substT.out -j 12
python3 fa.py run depth16=final:mr_max_depth=16 losses.tsv 02-arm-depth16.out -j 12
python3 fa.py run gtqIs=final+ov-gtq-is.mac losses.tsv 02-arm-gtqIs.out -j 12
python3 fa.py run prefix=prefix:mr_max_depth=16 losses.tsv 02-arm-prefix.out -j 12
echo ALLDONE > 02-switch-arms.done
