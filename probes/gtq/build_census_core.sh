#!/bin/sh
# probes/gtq/build_census_core.sh OUT.core -- the rules core
# (test/build_rules_core.sh's recipe) with the GtQ census baked in:
# gtq-readings.mac + census-wrapper.mac + the overlay make_census_overlay.py
# writes, loaded AFTER mr_load_all().  The arm is chosen per entry
# (%mr_gtq_arm, default "cur").  Used through the driver's pinned-core path
# (MR_RULES_CORE_PATH), which needs OUT.stamp next to it.  One maxima
# process, stdin /dev/null.
set -u
cd "$(dirname "$0")/../.." || exit 1
OUT=$(realpath -m "$1")
OV="${OUT%.core}.overlay.mac"
python3 probes/gtq/make_census_overlay.py "$OV" || exit 1
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
printf 'batch_answers_from_file: true$\nload("maxima_rubi.mac")$\nmr_load_all()$\nload("probes/gtq/gtq-readings.mac")$\nload("probes/gtq/census-wrapper.mac")$\nload("%s")$\ndisp(concat("TABLE_AT_BUILD ", string(length(mr_rule_table))))$\n:lisp (setq maxima::*maxima-started* nil)$\n:lisp (sb-ext:save-lisp-and-die "%s" :toplevel (symbol-function %s))\n' \
  "$OV" "$TMP/rules.core" "'cl-user::run" > "$TMP/in.mac"
maxima < "$TMP/in.mac" > "$TMP/build.log" 2>&1 || { echo "build failed"; tail -20 "$TMP/build.log"; exit 1; }
grep -q "GTQ census overlay loaded" "$TMP/build.log" || { echo "overlay did not load"; grep -i "error\|incorrect" "$TMP/build.log" | head; exit 1; }
grep "GTQ census overlay loaded\|TABLE_AT_BUILD" "$TMP/build.log"
mv "$TMP/rules.core" "$OUT"
{ echo "fingerprint gtq-census-$(md5sum "$OV" | cut -c1-32)"
  echo "git_rev $(git rev-parse HEAD)"
  echo "git_dirty $(git status --porcelain | grep -c . || true)"
  echo "date $(date -u '+%F %T UTC')"
} > "$OUT.stamp"
echo "built $OUT"
