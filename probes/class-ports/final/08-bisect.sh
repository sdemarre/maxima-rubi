#!/bin/sh
# the commit-bisect cores (detached worktrees /home/serge/src/mr-bis-<sha>, each
# built with test/build_rules_core.sh at that commit) over the losses no switch
# arm explains; each core at its own commit's defaults (depth cap 16 before
# 2ee8fc4, Subst simp before e67e2eb, is() GtQ before 39eba80; symbolic EqQ on
# from d0f0237).
cd "$(dirname "$0")"
until [ -f 07-chain.done ]; do sleep 10; done
for c in d0f0237 025c589 e799ea6 3bb8c4f 1ebef70; do
  python3 fa.py run b$c=/home/serge/src/mr-bis-$c/test/mr_rules.core:mr_max_depth=16 bisect.keys 08-bisect-$c.out -j 12
done
echo done > 08-bisect.done
