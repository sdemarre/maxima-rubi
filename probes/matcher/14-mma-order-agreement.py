#!/usr/bin/env python3
"""probes/matcher/14-mma-order-agreement.py -- does Maxima's internal term
order (the order inpart / inflag : true read, i.e. orderlessp's canonical
order) agree with Mathematica's stored order, and where it does not, does
the disagreement change PosAux's verdict? (matcher translation fixes design
section 3.2 "Order" and 3.5.)

The oracle is the corpus: every expected answer of classes 1-3 in
reference/maxima-syntax-test-suite was printed by Mathematica, which prints
a Plus in its stored order (the raw text keeps `(-1+x)`, never `(x-1)`).
Each answer is parsed with simp:false (the printed order) and every Plus
node's raw term list is compared, term by term simplified, with the
internal argument order of the simplified sum:

  agree       the whole order agrees
  first-only  the first term agrees, a later one does not
  first-dis   the first term differs
  flip        first-dis AND %mr_posAux of Mathematica's first term differs
              from %mr_posAux of Maxima's first term (the case that changes
              PosAux's sum-branch verdict)
  noncomp     not comparable (simplification merged or changed terms, or an
              error)

Times nodes are compared on the leading numeric coefficient only (the
printed form splits the denominator off): a raw product whose first factor
is a number, against the first internal argument of the simplified product
(most losses are number merges such as 2*2^(1/4) -> 2^(5/4)). PosAux's
product branch multiplies factor signs, so factor order does not change its
verdict.

Needs the PosAux port (%mr_posAux in maxima_rubi_utils.mac): run on the
fixed tree. Maxima runs in parallel chunk processes. Usage (repo root, idle
machine):
  python3 probes/matcher/14-mma-order-agreement.py > probes/matcher/14-mma-order-agreement.out
"""

import collections
import concurrent.futures
import datetime
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "reference" / "maxima-syntax-test-suite"
SECTIONS = {1: "1 Algebraic functions", 2: "2 Exponentials", 3: "3 Logarithms"}
CHUNK = 200
WORKERS = 8
CHUNK_TIMEOUT = 900

MAC_HEAD = r'''display2d : false$
linel : 100000$
load("maxima_rubi.mac")$
mr14_args(t) := block([inflag : true], args(t))$
/* shape signature to depth d: numbers n / -n, x, other atoms s, a negated
   product -(..), otherwise op(args); e past the depth */
mr14_sig(t, d) :=
  if numberp(t) then (if is(t < 0) then "-n" else "n")
  else if atom(t) then (if t = 'x then "x" else "s")
  else if d = 0 then "e"
  else block([o : inpart(t, 0)],
    if o = "*" and numberp(inpart(t, 1)) and is(inpart(t, 1) < 0)
    then sconcat("-(", mr14_sig(-t, d), ")")
    else sconcat(string(o), "(", simplode(map(lambda([a], mr14_sig(a, d - 1)), mr14_args(t)), ","), ")"))$
mr14_walk(e) := block([simp : false, inflag : true],
  if atom(e) then true
  else (if op(e) = "+" then mr14_acc : endcons(args(e), mr14_acc),
        if op(e) = "*" then mr14_tacc : endcons(args(e), mr14_tacc),
        for a in args(e) do mr14_walk(a),
        true))$
mr14_node(id, tl) := block([st, S, sa, pm, px],
  st : map(lambda([t], expand(t, 0, 0)), tl),
  S : expand(apply("+", tl), 0, 0),
  sa : if atom(S) then [S] else block([inflag : true], if op(S) = "+" then args(S) else [S]),
  if length(sa) # length(st) or not is(sort(sa) = sort(st)) then 'nc
  else if is(sa = st) then 'ag
  else if is(first(sa) = first(st)) then 'fo
  else block([flip, ren, cf],
    pm : errcatch(%mr_posAux(first(st))),
    px : errcatch(%mr_posAux(first(sa))),
    flip : pm # [] and px # [] and pm # px,
    /* case-fold rename: each symbol v -> <lowercase v>0 (lower case) or
       <lowercase v>1 (upper case), which puts Maxima's symbol order at
       Mathematica's a < A < b < B; "case" = the renamed sum's first term is
       Mathematica's first term */
    ren : map(lambda([v], v = mr14_fold(v)), listofvars(S)),
    cf : errcatch(is(first(block([inflag : true], args(subst(ren, S)))) = subst(ren, first(st)))),
    print("D14", id, if flip then "flip" else "same", if cf = [true] then "case" else "order",
          mr14_sig(first(st), 2), mr14_sig(first(sa), 2), string(st), "|", string(sa)),
    if flip then 'fl else 'fd))$
mr14_fold(v) := if symbolp(v) then
    block([s : string(v)], concat(sdowncase(s), if s = sdowncase(s) then "0" else "1"))
  else v$
mr14_one(id, s) := block([r, nag : 0, nfo : 0, nfd : 0, nfl : 0, nnc : 0, tn : 0, td : 0],
  mr14_acc : [], mr14_tacc : [],
  r : errcatch(block([simp : false, inflag : true], mr14_walk(parse_string(s)))),
  if r = [] then (print("E14", id), return(false)),
  for tl in mr14_acc do block([k],
    k : errcatch(mr14_node(id, tl)),
    k : if k = [] then 'nc else first(k),
    if k = 'ag then nag : nag + 1
    else if k = 'fo then nfo : nfo + 1
    else if k = 'fd then nfd : nfd + 1
    else if k = 'fl then nfl : nfl + 1
    else nnc : nnc + 1),
  for tl in mr14_tacc do errcatch(block([f0, S2],
    f0 : block([simp : false], first(tl)),
    if numberp(f0) then (
      tn : tn + 1,
      S2 : errcatch(expand(apply("*", tl), 0, 0)),
      if S2 = [] or atom(first(S2))
         or not block([inflag : true], op(first(S2)) = "*" and numberp(first(first(S2))))
      then (td : td + 1, print("T14", id, string(tl), "|", if S2 = [] then "ERROR" else string(first(S2))))))),
  print("N14", id, nag, nfo, nfd, nfl, nnc, tn, td))$
'''


def top_level_entries(text):
    """The [..] elements of the file's lst: '[ ... ] list (comments removed)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    start = text.find("'[")
    if start < 0:
        return []
    i, depth, cur, out = start + 2, 1, None, []
    while i < len(text) and depth > 0:
        ch = text[i]
        if ch == "[":
            depth += 1
            if depth == 2:
                cur = i
        elif ch == "]":
            if depth == 2 and cur is not None:
                out.append(text[cur:i + 1])
                cur = None
            depth -= 1
        i += 1
    return out


def split_elements(entry_text):
    parts, depth, cur = [], 0, ""
    for ch in entry_text:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


def answers(c):
    out = []
    files = sorted(p for p in (SUITE / SECTIONS[c]).rglob("*.mac"))
    for fi, p in enumerate(files):
        for ei, e in enumerate(top_level_entries(p.read_text(encoding="utf-8")), 1):
            parts = split_elements(e[1:-1])
            if len(parts) >= 4:
                out.append(("%d:%d:%d" % (c, fi, ei), parts[3], p.relative_to(SUITE).as_posix()))
    return out


def mstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def run_chunk(work, tag, chunk):
    mac = Path(work) / ("chunk-%s.mac" % tag)
    # one errcatch per answer: an uncaught error would end the batch file
    mac.write_text(MAC_HEAD + "".join(
        "if errcatch(mr14_one(%s, %s)) = [] then print(\"X14\", %s)$\n" % (mstr(i), mstr(a), mstr(i))
        for i, a, _ in chunk))
    try:
        r = subprocess.run(["maxima", "--very-quiet", "-b", str(mac)], stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                           timeout=CHUNK_TIMEOUT, cwd=ROOT)
        return r.stdout, False
    except subprocess.TimeoutExpired as e:
        o = e.stdout
        return (o.decode("utf-8", "replace") if isinstance(o, bytes) else (o or "")), True


def main():
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    print("=== probes/matcher/14-mma-order-agreement  git HEAD %s  %s" % (
        head, datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))
    b = subprocess.run(["maxima", "--very-quiet", "--batch-string",
                        'print("R build", build_info()@version, build_info()@timestamp)$'],
                       stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=ROOT)
    print(next((l for l in b.stdout.splitlines() if l.startswith("R build")), "R build ?"))
    work = tempfile.mkdtemp(prefix="mr-14-order-")
    for c in (1, 2, 3):
        ans = answers(c)
        files = {i: f for i, _a, f in ans}
        chunks = [ans[k:k + CHUNK] for k in range(0, len(ans), CHUNK)]
        tot = collections.Counter()
        seen, errs, parse_err, timeouts = set(), [], [], 0
        pairs, flips, dis, tdis = collections.Counter(), collections.Counter(), [], []
        fold = collections.Counter()
        with concurrent.futures.ThreadPoolExecutor(WORKERS) as ex:
            futs = [ex.submit(run_chunk, work, "%d-%d" % (c, k), ch) for k, ch in enumerate(chunks)]
            for fut in concurrent.futures.as_completed(futs):
                out, to = fut.result()
                timeouts += to
                for line in out.splitlines():
                    tag = line.split(" ", 1)[0]
                    if tag == "N14":
                        p = line.split()
                        seen.add(p[1])
                        for k, v in zip(("agree", "first-only", "first-dis-same", "flip", "noncomp",
                                         "times-num", "times-dis"), p[2:9]):
                            tot[k] += int(v)
                    elif tag == "E14":
                        parse_err.append(line.split()[1])
                        seen.add(line.split()[1])
                    elif tag == "X14":
                        errs.append(line.split()[1])
                        seen.add(line.split()[1])
                    elif tag == "D14":
                        p = line.split(" ", 6)
                        pairs[(p[4], p[5])] += 1
                        if p[2] == "flip":
                            fold[p[3]] += 1
                            if p[3] == "order":
                                flips[(p[4], p[5])] += 1
                        dis.append((p[1], p[2] if p[3] == "order" else "case", p[6]))
                    elif tag == "T14":
                        tdis.append(line)
        missing = [i for i, _a, _f in ans if i not in seen]
        fd = tot["first-dis-same"] + tot["flip"]
        plus = tot["agree"] + tot["first-only"] + fd
        print("CLASS %d answers %d done %d parse-errors %d answer-errors %d missing %d (chunk timeouts %d)" % (
            c, len(ans), len(seen), len(parse_err), len(errs), len(missing), timeouts))
        print("CLASS %d Plus comparable %d: agree %d, first-only %d, first-dis %d (PosAux flip %d); noncomp %d" % (
            c, plus, tot["agree"], tot["first-only"], fd, tot["flip"], tot["noncomp"]))
        if plus:
            print("CLASS %d first-term agreement %.4f, whole-order agreement %.4f, PosAux flip rate %.4f" % (
                c, (tot["agree"] + tot["first-only"]) / plus, tot["agree"] / plus, tot["flip"] / plus))
        print("CLASS %d Times with a leading number %d, leading number lost %d" % (
            c, tot["times-num"], tot["times-dis"]))
        print("CLASS %d PosAux flips removed by the case-fold rename %d, remaining %d" % (
            c, fold["case"], fold["order"]))
        for (sr, sm), n in flips.most_common(30):
            print("CLASS %d FLIP (after case fold) shape mma-first %s -> maxima-first %s: %d" % (c, sr, sm, n))
        for (sr, sm), n in pairs.most_common(15):
            print("CLASS %d FIRST-DIS shape mma-first %s -> maxima-first %s: %d" % (c, sr, sm, n))
        shown = set()
        for i, fl, txt in sorted((d for d in dis if d[1] == "flip"), key=lambda t: len(t[2])):
            if txt in shown:
                continue
            shown.add(txt)
            print("FLIP %s %s  %s" % (i, files.get(i, "?"), txt[:300]))
            if len(shown) >= 30:
                break
        for line in tdis[:10]:
            print(line[:300])
        for i in parse_err[:10]:
            print("PARSE-ERROR %s %s" % (i, files.get(i, "?")))
        for i in errs[:10]:
            print("ANSWER-ERROR %s %s" % (i, files.get(i, "?")))
        for i in missing[:10]:
            print("MISSING %s %s" % (i, files.get(i, "?")))
    print("=== done")


if __name__ == "__main__":
    sys.exit(main())
