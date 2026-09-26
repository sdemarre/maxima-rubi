#!/bin/sh
# after the 47-loss fixR run: the EqQ wins + the PASS sample on fixR and on final
cd "$(dirname "$0")"
until [ "$(grep -vc '^#' 05-fix-eqq-radcan.out)" -ge 47 ]; do sleep 5; done
python3 fa.py run fixR=final+fix-eqq-radcan.mac 05b-fix-check.keys 05-fix-eqq-radcan.out -j 12
python3 fa.py run final=final 05b-fix-check.keys 05-fix-final.out -j 12
echo done > 05-chain.done
