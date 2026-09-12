#!/usr/bin/env python3
"""probes/matcher/05-p0-wall-noise.py -- the per-entry wall noise band of the
class-3 corpus on one core (matcher substrate spec section 4, P0/P5
performance gate: median per-entry wall <= the P0 baseline's).

Compares two class-3 records taken on the same build and rules core:
  campaign  `git show 0579952:test/corpus_class3.out` -- the class-3 deferred
            campaign close record (merged 2026-09-04; also committed as
            test/corpus_class3.out)
  P0        test/corpus_class3.pre-matcher.out -- the matcher substrate P0 run
            (merged 2026-09-12)

Reports both records' median t= over all entries (two decimals) and, over the
entries with the same verdict class in both, the per-entry ratio P0 t /
campaign t: median and spread (quantiles).  Entries with t=0.0 in either
record are excluded from the ratio and counted.

Run:  python3 probes/matcher/05-p0-wall-noise.py > probes/matcher/05-p0-wall-noise.out
No Maxima run; stamped with the run date and git HEAD.
"""

import datetime
import importlib.util
import os
import statistics
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_spec = importlib.util.spec_from_file_location("ab_records", os.path.join(ROOT, "test", "ab_records.py"))
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)

CAMPAIGN_REV = "0579952"
CAMPAIGN_PATH = "test/corpus_class3.out"
P0_PATH = "test/corpus_class3.pre-matcher.out"


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def header(text):
    keep = ("merge date:", "maxima: Maxima-version:", "maxima: Maxima build date:", "filter:")
    return [l for l in text.splitlines()[:12] if l.startswith(keep)]


def quantile(sorted_xs, q):
    # nearest-rank on the sorted list (same convention as test/record_medians.py's p90)
    return sorted_xs[min(len(sorted_xs) - 1, int(q * len(sorted_xs)))]


def main():
    campaign_text = git("show", "%s:%s" % (CAMPAIGN_REV, CAMPAIGN_PATH))
    with open(os.path.join(ROOT, P0_PATH), encoding="utf-8") as fh:
        p0_text = fh.read()
    with tempfile.NamedTemporaryFile("w", suffix=".out", delete=False, encoding="utf-8") as tmp:
        tmp.write(campaign_text)
    try:
        campaign = ab.load_record(tmp.name)
    finally:
        os.unlink(tmp.name)
    p0 = ab.load_record(os.path.join(ROOT, P0_PATH))
    with open(os.path.join(ROOT, CAMPAIGN_PATH), encoding="utf-8") as fh:
        same_as_worktree = fh.read() == campaign_text

    print("=== probes/matcher/05-p0-wall-noise  run: %s" % datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    print("git HEAD: %s" % git("rev-parse", "HEAD").strip())
    print("campaign record: %s:%s (identical to the working-tree %s: %s)" % (CAMPAIGN_REV, CAMPAIGN_PATH, CAMPAIGN_PATH, same_as_worktree))
    for l in header(campaign_text):
        print("  " + l)
    print("P0 record: %s" % P0_PATH)
    for l in header(p0_text):
        print("  " + l)
    print()

    for name, rec in (("campaign", campaign), ("P0", p0)):
        ts = [t for _c, t in rec.values()]
        print("%-8s entries %d  median t %.2f s  mean t %.2f s" % (name, len(ts), statistics.median(ts), statistics.mean(ts)))
    print("median difference: P0 - campaign = %+.2f s (%+.1f %% of the campaign median)" % (
        statistics.median(t for _c, t in p0.values()) - statistics.median(t for _c, t in campaign.values()),
        100.0 * (statistics.median(t for _c, t in p0.values()) / statistics.median(t for _c, t in campaign.values()) - 1)))
    print("key sets equal: %s (campaign only %d, P0 only %d)" % (
        campaign.keys() == p0.keys(), len(campaign.keys() - p0.keys()), len(p0.keys() - campaign.keys())))
    print()

    common = sorted(campaign.keys() & p0.keys())
    same = [k for k in common if campaign[k][0] == p0[k][0]]
    zero = [k for k in same if campaign[k][1] == 0.0 or p0[k][1] == 0.0]
    ratios = sorted(p0[k][1] / campaign[k][1] for k in same if k not in zero)
    print("same verdict class in both: %d of %d common entries; excluded for t=0.0: %d; ratios: %d" % (
        len(same), len(common), len(zero), len(ratios)))
    print("same-class medians: campaign %.2f s  P0 %.2f s" % (
        statistics.median(campaign[k][1] for k in same), statistics.median(p0[k][1] for k in same)))
    print("per-entry ratio P0 t / campaign t: median %.2f  p10 %.2f  p25 %.2f  p75 %.2f  p90 %.2f  min %.2f  max %.2f" % (
        statistics.median(ratios), quantile(ratios, 0.10), quantile(ratios, 0.25), quantile(ratios, 0.75),
        quantile(ratios, 0.90), ratios[0], ratios[-1]))
    within = lambda lo, hi: sum(1 for r in ratios if lo <= r <= hi)
    print("share of ratios within 0.90..1.10: %.1f %%; within 0.80..1.25: %.1f %%" % (
        100.0 * within(0.90, 1.10) / len(ratios), 100.0 * within(0.80, 1.25) / len(ratios)))
    by_class = {}
    for k in same:
        if k not in zero:
            by_class.setdefault(campaign[k][0], []).append(p0[k][1] / campaign[k][1])
    print("per verdict class (entries, median ratio): %s" % ", ".join(
        "%s %d %.2f" % (c, len(v), statistics.median(v)) for c, v in sorted(by_class.items(), key=lambda kv: -len(kv[1]))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
