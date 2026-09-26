#!/bin/sh
# run_probe.sh FILE.mac CAP [CORE] -- a Maxima batch on a rules image (default the
# final core, test/mr_rules.core) exactly as test/corpus_driver.py starts one
# (sbcl --core, stdin /dev/null, own session), under the driver's cpu-cap
# helper test/mr_cpu_cap.py; output to FILE.out (+ "rc N"; 200 = cap hit).
cd "$(dirname "$0")"
f=$1; cap=${2:-60}; core=${3:-../../../test/mr_rules.core}
setsid python3 ../../../test/mr_cpu_cap.py $cap "${f%.mac}.cpu" "$(command -v sbcl)" --tls-limit 100000 --core "$core" --noinform --very-quiet -b "$f" < /dev/null > "${f%.mac}.out" 2>&1
echo "rc $? cpu $(cat "${f%.mac}.cpu")" >> "${f%.mac}.out"
rm -f "${f%.mac}.cpu"
