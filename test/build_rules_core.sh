#!/bin/sh
# test/build_rules_core.sh — build the option-D rules core.
#
# The rules core (test/mr_rules.core) is a saved Maxima image carrying the
# full loaded rule table (class 1 + class 2 + class 3, 3513 rules) +
# batch_answers_from_file, so the driver's per-integral subprocess starts
# from the image instead of re-running load("maxima_rubi.mac") +
# mr_load_all() (class-1 load alone: ~6.2 s warm / ~9.4 s cold, measured
# probes/image/probe-rule-image.out). See that probe for the
# mechanism (the installed maxima.core is itself built the same way,
# src/maxima-build.lisp:24).
#
# NOTE: the file list below (loader + utils + dispatch lisp + implicit-1
# lisp + every class-1, class-2 AND class-3 rule file) must stay in sync
# with the driver's _core_fingerprint() (test/corpus_class1_driver.py).
# The fingerprint sidecar (test/mr_rules.core.stamp) is an md5 over the rule
# files that define the image. The core BAKES the rules in: after editing a
# rule .mac, the old core still "works" but silently runs the pre-edit rules.
# The driver (corpus_class1_driver.py) refuses a core whose fingerprint does
# not match the current rule files, so a stale core can never be used.
#
# Usage (from the worktree root):  sh test/build_rules_core.sh
set -u
cd "$(dirname "$0")/.." || exit 1   # this script lives in test/ (one level)
OUT=test/mr_rules.core
STAMP=test/mr_rules.core.stamp
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Fingerprint over exactly the files the image is built from: the loader,
# the utils, the dispatch lisp, and every generated class-1, class-2 AND
# class-3 rule file. The file list is sorted (C locale) so the byte order
# matches the driver's _core_fingerprint() (test/corpus_class1_driver.py)
# exactly — a different order would make every freshly built core look
# stale.
FP=$( { printf '%s\n' maxima_rubi.mac maxima_rubi_utils.mac maxima_rubi_dispatch.lisp \
        maxima_rubi_implicit1.lisp
        ls rules/class1/*.mac rules/class2/*.mac rules/class3/*.mac
      } | LC_ALL=C sort | xargs -d '\n' cat | md5sum | cut -d' ' -f1 )

# The image is saved from a session that has ALREADY run a top-level, so
# *maxima-started* is T; unless reset, every restored launch prints a
# spurious "Maxima restarted." line (measured 2026-08-26). Reset it so the
# restored image behaves like a fresh maxima startup. The saved toplevel is
# cl-user::run, so the driver launches it with bare maxima options (no
# --eval) — see maxima_run in test/corpus_class1_driver.py.
printf 'batch_answers_from_file: true$\nload("maxima_rubi.mac")$\nmr_load_all()$\ndisp(concat("TABLE_AT_BUILD ", string(length(mr_rule_table))))$\n:lisp (setq maxima::*maxima-started* nil)$\n:lisp (sb-ext:save-lisp-and-die "%s" :toplevel (symbol-function %s))\n' \
  "$TMP/rules.core" "'cl-user::run" | maxima -X "--tls-limit 100000" > "$TMP/build.log" 2>&1 || {
    echo "rules-core build failed:"; tail -5 "$TMP/build.log"; exit 1; }
TAB=$(grep -oE 'TABLE_AT_BUILD [0-9]+' "$TMP/build.log" | head -1 | awk '{print $2}')
[ -n "$TAB" ] || { echo "rules-core build: no TABLE_AT_BUILD witness:"; tail -5 "$TMP/build.log"; exit 1; }
mv "$TMP/rules.core" "$OUT"
{ echo "fingerprint $FP"
  echo "git_rev $(git rev-parse HEAD 2>/dev/null || echo n/a)"
  # Tree-state marker: git_rev alone mislabels a build from a dirty
  # tree (the baked files can postdate HEAD). write-tree hashes the
  # CURRENT index contents — clean tree => the HEAD tree hash, so the
  # stamp is self-describing (measured incident: the 2026-08-27
  # accepted core was built from a tree carrying the then-uncommitted
  # 89054b0 fix).
  echo "git_tree $(git write-tree 2>/dev/null || echo n/a)"
  echo "git_dirty $(git status --porcelain 2>/dev/null | grep -c . || true)"
  echo "date $(date -u '+%F %T UTC')"
  echo "maxima $(maxima --version 2>&1 | head -1)"
  echo "rules $TAB"
} > "$STAMP"
echo "built $OUT ($(stat -c%s "$OUT") bytes) rules=$TAB fingerprint=$FP"
