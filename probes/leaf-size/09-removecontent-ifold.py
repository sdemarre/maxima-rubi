#!/usr/bin/env python3
""".scratch/answer-quality/issues/02: does folding %i out of RemoveContent's
argument clear the log(%i*u) answers?

Mathematica evaluates RemoveContent's argument before RemoveContent sees it:
4_3_1_1 r3's Log[RemoveContent[Cos[I a + I b x + Pi/2], x]] reaches it as
-I Sinh[a + b x], whose content -I is stripped. The port's argument stays
sin(%i*b*x+%i*a), and the depth-0 %i fold later turns it into
log(%i*sinh(b*x+a)) (6.1.1 e30, traced with rubi_verbose : 'matches).

Candidates: probe 07's entries whose answer has a log(%i*..)/log(-%i*..)
factor. Each runs rubi twice in a fresh process at the current defaults:
  old  as shipped
  new  %mr_removeContent redefined to fold its argument first with
       %mr_ifold, under radexpand:false, logexpand:false, errcatch'd
       (%mr_top_final's wrapper)
and prints `fixed` (old has a log(+-%i*..), new has none), `same` (identical
answers) or `changed-still`, with the new answer when not fixed. No
verification: this measures the answer's shape only.

    python3 probes/leaf-size/09-removecontent-ifold.py \\
        > probes/leaf-size/09-removecontent-ifold.out < /dev/null
"""

import concurrent.futures as cf
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.argv = [sys.argv[0]]
sys.path.insert(0, os.path.join(ROOT, "test"))
os.chdir(ROOT)
import corpus_driver as d  # noqa: E402

REDEF = '''%mr_removeContent(u, x) := block([v, w],
  u : block([MR_e : errcatch(block([radexpand : false, logexpand : false], %mr_ifold(u)))],
            if MR_e = [] then u else first(MR_e)),
  v : %mr_nonfreeFactors(u, x),
  w : %mr_together(v),
  if %mr_eqQ(%mr_freeFactors(w, x), 1) then %mr_removeContentAux(v, x)
  else %mr_removeContentAux(%mr_nonfreeFactors(w, x), x))$
'''
LOGI = re.compile(r'log\(-?%i\*')
_cache = {}


def elements(label):
    rel, e, _l = label.rsplit(" ", 2)
    if rel not in _cache:
        _cache[rel] = d.extract_entries(os.path.join(d.SUITE, rel))[0]
    return d.split_elements(_cache[rel][int(e[1:]) - 1][1:-1])


def candidates():
    ans, cur = {}, None
    for l in open("probes/leaf-size/07-remaining-i-answers.out"):
        if l.startswith("## "):
            cur = l[3:].strip()
        elif l.startswith("ANSWER "):
            ans[cur] = l[7:].strip()
    return [k for k, a in ans.items() if LOGI.search(a)]


def one(label):
    els = elements(label)
    f, x = d.normalize_heads(els[0]), els[1]
    res = []
    for pre in ("", REDEF):
        out, _hit = d.maxima_run(
            pre + f'mr_r : rubi({f}, {x})$\nprintf(true, "ANS ~a~%", string(mr_r))$\n',
            d.TIMEOUT + 10, [])
        a = [l[4:] for l in out.splitlines() if l.startswith("ANS ")]
        res.append(a[0] if a else "NONE")
    return label, res


def main():
    cands = candidates()
    print(f"# {len(cands)} candidates (probe 07 answers with a log(+-%i*..)); "
          "old = shipped, new = RemoveContent folds its argument")
    tally = {}
    with cf.ThreadPoolExecutor(12) as ex:
        for label, (old, new) in ex.map(one, cands):
            st = ("fixed" if LOGI.search(old) and not LOGI.search(new)
                  else "same" if old == new else "changed-still")
            tally[st] = tally.get(st, 0) + 1
            print(f"{st:13s} {label}" + ("" if st == "fixed" else f"\n    new: {new}"),
                  flush=True)
    print("# census: " + " ".join(f"{k}={v}" for k, v in sorted(tally.items())))


if __name__ == "__main__":
    main()
