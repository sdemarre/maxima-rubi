#!/bin/sh
# test/ms_measure.sh -- both arms (maxima-rubi, then native integrate+risch),
# every section 0-8, re-measured with millisecond t= (`timing: printf-free+ms`,
# 2026-10-04): the records before had 0.1 s resolution, and nearly every native
# pass recorded 0.0 s. Runs test/graded_measure.sh (one section at a time,
# the two arms alternating, 24 workers), then A/Bs every record and grade
# census against the 0.1 s records read from git (BASE_REV, default 3d6c2a0)
# into BASE_DIR, and regenerates test/grade_report.out:
#   test/ms_ab_class<N>[.baseline].out       ab_records.py, old -> new
#   test/ms_abgrade_class<N>[.baseline].out  ab_grades.py,  old -> new
# Verdicts should not move except at the 30 s cap.
#   setsid sh test/ms_measure.sh > test/ms_measure.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/.." || exit 1
BASE_REV=${BASE_REV:-3d6c2a0}
BASE_DIR=.scratch/corpus-harness/records-pre-ms
mkdir -p "$BASE_DIR"
for n in 0 1 2 3 4 5 6 7 8; do
  for f in "corpus_class$n.out" "corpus_class$n.grade.out" \
           "corpus_class$n.baseline.out" "corpus_class$n.baseline.grade.out"; do
    [ -s "$BASE_DIR/$f" ] || git show "$BASE_REV:test/$f" > "$BASE_DIR/$f" \
      || { echo "REFUSING: no $f at $BASE_REV"; exit 5; }
  done
done
sh test/graded_measure.sh "0 Independent test suites" "1 Algebraic functions" "2 Exponentials" \
  "3 Logarithms" "4 Trig functions" "5 Inverse trig functions" "6 Hyperbolic functions" \
  "7 Inverse hyperbolic functions" "8 Special functions"
rc=$?
for n in 0 1 2 3 4 5 6 7 8; do
  for arm in "" ".baseline"; do
    python3 test/ab_records.py "$BASE_DIR/corpus_class$n$arm.out" "test/corpus_class$n$arm.out" \
      > "test/ms_ab_class$n$arm.out" 2>&1
    python3 test/ab_grades.py "$BASE_DIR/corpus_class$n$arm.grade.out" "test/corpus_class$n$arm.grade.out" \
      > "test/ms_abgrade_class$n$arm.out" 2>&1
    echo "$(date '+%F %T %Z') A/B class$n$arm: $(awk '/PASS\/FAIL table/{f=1;next} f&&NF==2{printf "%s=%s ",$1,$2} f&&NF==0{exit}' "test/ms_ab_class$n$arm.out")$(tail -1 "test/ms_abgrade_class$n$arm.out")"
  done
done
python3 test/grade_report.py > test/grade_report.out
echo "$(date '+%F %T %Z') ALL DONE rc=$rc"
exit $rc
