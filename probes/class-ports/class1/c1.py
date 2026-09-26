#!/usr/bin/env python3
"""probes/class-ports/class1/c1.py -- class-1 runner over the class-6
template's trace_entry.py (the corpus driver's own text transform, cap
helper, stdin /dev/null, process-group kill). ONE Maxima process at a time.

  c1.py ab ENTRIES CAP ARM [ARM ..]
      For each entry (record-format line), for each ARM in order (so the arms
      ALTERNATE per entry): the harness verdict (driver build_text +
      classify_output) plus the rubi call's own cpu. ARM is
      name=CORE[+OVERLAY.mac[+OVERLAY2.mac]]. Prints
      `<name> <class> t= <entry cpu>s rubi= <rubi cpu>s <key>`.
  c1.py trace ENTRIES CAP ARM [ARM ..]
      rubi_verbose firings per arm (trace_entry.trace), blank-line separated.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import trace_entry as te
te.SECTION = "1 Algebraic functions"
ROOT = te.ROOT
RESULT = re.compile(r"^(?:\S+\s+)?(\S+)\s+t=\s*([\d.]+)s\s+(?:rubi=\s*\S+\s+)?(1 Algebraic functions/.*\.mac) e(\d+)")


def arms(specs):
    out = []
    for s in specs:
        name, rest = s.split("=", 1)
        parts = rest.split("+")
        core = os.path.abspath(parts[0])
        pre = "".join(open(p).read() + "\n" for p in parts[1:])
        out.append((name, core, pre))
    return out


def entries(path):
    for l in open(path):
        m = RESULT.match(l)
        if m:
            yield m.group(3), int(m.group(4))


def classify(d, rel, idx, cap, core, pre_text):
    d.RULES_CORE = core
    sec = te.SECTION
    rel = rel[len(sec) + 1:] if rel.startswith(sec + "/") else rel
    ents, lnos = d.extract_entries(os.path.join(te.SUITE, sec, rel))
    els = d.split_elements(ents[idx - 1][1:-1])
    f_text = d.normalize_heads(els[0]); var = els[1]
    e_text = d.normalize_heads(els[3])
    e_text2 = d.normalize_heads(els[4]) if len(els) == 5 else None
    text = d.build_text(f_text, var, e_text, e_text2)
    call = f"mr_r: rubi(mr_f, {var})$\n"
    assert call in text
    text = text.replace(call, "mr_t0: elapsed_run_time()$\n" + call
                        + 'print("RUBI-CPU", elapsed_run_time() - mr_t0)$\n', 1)
    cpu = []
    out, hit = d.maxima_run(pre_text + text, cap, cpu)
    cls, _ = d.classify_output(out, hit)
    t = cpu[0] if cpu and cpu[0] is not None else -1
    m = re.search(r"RUBI-CPU\s+([\d.]+)", out)
    r = f"{float(m.group(1)):6.1f}" if m else "   n/a"
    return f"{cls:14s} t={t:6.1f}s rubi={r}s {sec}/{rel} e{idx} L{lnos[idx - 1]}"


def main():
    mode, path, cap = sys.argv[1], sys.argv[2], int(sys.argv[3])
    A = arms(sys.argv[4:])
    d = te.load_driver(cap)
    for rel, idx in entries(path):
        for name, core, pre in A:
            if mode == "ab":
                print(f"{name:6s} " + classify(d, rel, idx, cap, core, pre), flush=True)
            else:
                print(f"## arm {name}", flush=True)
                print(te.trace(d, rel, idx, cap, core, pre_text=pre), flush=True)
                print(flush=True)


if __name__ == "__main__":
    main()
