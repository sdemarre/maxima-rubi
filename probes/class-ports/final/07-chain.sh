#!/bin/sh
cd "$(dirname "$0")"
python3 fa.py run fixRP=final+fix-eqq-radcan.mac+fix-pseudoroot.mac eqq-recovered.keys 07-fix-eqq-radcan-pseudoroot.out -j 12
python3 fa.py run fixRP=final+fix-eqq-radcan.mac+fix-pseudoroot.mac 05b-fix-check.keys 07-fix-eqq-radcan-pseudoroot.out -j 12
echo done > 07-chain.done
