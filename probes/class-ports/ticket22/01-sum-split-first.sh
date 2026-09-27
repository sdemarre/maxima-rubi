#!/bin/sh
# Ticket 22: the four witnesses on the real mr_load_all table, as loaded
# (sumfirst=false) and with 9_1 r13 (Int[u_] /; SumQ[u], the legacy 9.1 sum
# split) moved to the head of mr_rule_table (sumfirst=true).
# Run from the repo root: sh probes/class-ports/ticket22/01-sum-split-first.sh
cd "$(dirname "$0")/../../.." || exit 1
out=probes/class-ports/ticket22/01-sum-split-first.out
{
  echo "# $(date -u +%F), build: $(maxima --very-quiet --batch-string='build_info();' < /dev/null | grep -E 'version|date' | tr -s ' \n' ' ')"
  for s in false true; do
    echo "=== sumfirst=$s"
    setsid maxima --very-quiet \
      --batch-string="sumfirst:$s\$ batchload(\"probes/class-ports/ticket22/01-sum-split-first.mac\")\$" < /dev/null 2>&1
  done
} > "$out"
echo "wrote $out"
