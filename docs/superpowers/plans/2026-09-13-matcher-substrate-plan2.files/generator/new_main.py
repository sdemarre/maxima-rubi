# The legacy 9.1 integrand simplification rules (spec 3.4): absent from the
# pinned Rubi.m LoadRules (dropped 2023-12, f7fa0fd), but loaded by the 2018
# Rubi the Maxima-syntax corpus was generated with, after the 1.x files — so
# it is generated at the end of the class-1 table (the position of the
# manual port it replaces). The pinned file's first rule (L4,
# Int[u_.*(v_+w_)^p_., x_Symbol]) is commented out there, so the generated
# file carries 28 rules; the manual port carried it as a 29th, dead rule.
NINE_ONE = ("Rubi/IntegrationRules/9 Miscellaneous/"
            "9.1 Integrand simplification rules.m")
NINE_ONE_TOTAL = 28

def configure(class_num):
    """Point the generator at class <class_num> (1, 2 or 3)."""
    global CLASS, CLASS_PREFIX, OUT, EXPECTED_TOTAL
    CLASS = class_num
    CLASS_PREFIX = f"{CLASS} "
    OUT = ROOT / "rules" / f"class{CLASS}"
    # class 3: 334 — the 333 census count + the 3.5.m L46 FunctionOfLog
    # catch-all (class-3 deferred campaign C6b; the single-line
    # If[TrueQ[$LoadShowSteps], …] wrapper the census parser never
    # picked up — unwrap_showsteps_line).
    EXPECTED_TOTAL = {1: 2710 + EXTRA_TOTAL + NINE_ONE_TOTAL, 2: 125,
                      3: 334}[class_num]


def _emit_source(rel_m, key, only, total, load_lines, note=""):
    text = unwrap_showsteps_lines(strip_comments((RUBI / rel_m).read_text()))
    runs = rule_runs(text)
    out = OUT / f"{key}.mac"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(emit_file(rel_m, runs, key))
    print(f"  {key}: {len(runs)} rules{note}")
    load_lines.append(f"%mr_load_sibling(\"rules/class{CLASS}/{key}.mac\", "
                      f"'mr_witness_{key})$")
    return total + len(runs)


def main(class_num=None):
    if class_num is None:
        class_num = (int(sys.argv[sys.argv.index("--class") + 1])
                     if "--class" in sys.argv else 1)
    configure(class_num)
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].replace(".", "_")
    total = 0
    load_lines, table_terms = [], []
    for rel_m in load_class_files(RUBI):
        key = key_of(rel_m)
        if only and key != only:
            continue
        total = _emit_source(rel_m, key, only, total, load_lines)
        table_terms.append(f"mr_rules_{key}")
    if CLASS == 1:
        # The five corpus-tested dead siblings (EXTRA_CLASS1), `b`-suffixed,
        # table position immediately after their same-numbered sibling.
        for rel_m in EXTRA_CLASS1:
            if not (RUBI / rel_m).exists():
                raise GenError(f"EXTRA_CLASS1 file missing: {rel_m}")
            base = key_of(rel_m)
            key = base + "b"
            if only and key != only:
                continue
            total = _emit_source(rel_m, key, only, total, load_lines,
                                 " (extra, corpus-matched dead file)")
            sib = f"mr_rules_{base}"
            pos = table_terms.index(sib) + 1 if sib in table_terms \
                else len(table_terms)
            table_terms.insert(pos, f"mr_rules_{key}")
        if not (RUBI / NINE_ONE).exists():
            raise GenError(f"9.1 source missing: {NINE_ONE}")
        if not only or only == "9_1":
            total = _emit_source(NINE_ONE, "9_1", only, total, load_lines,
                                 " (legacy 9.1, end of the class-1 table)")
            table_terms.append("mr_rules_9_1")
    expected = EXPECTED_TOTAL
    note = (f"OK (== {expected})" if (total == expected and not only)
            else ("partial (--only)" if only
                  else f"MISMATCH (expected {expected})"))
    print(f"TOTAL: {total} rules — {note}")
    if not only and total != expected:
        raise GenError(f"rule total {total} != {expected} "
                       f"(T1 census + EXTRA_CLASS1 + 9.1 for class 1); "
                       f"aborting")
    if not only:
        print()
        print("# maxima_rubi.mac load list (Rubi LoadRules order):")
        for line in load_lines:
            print(line)
        # flatten([...]), not "a concat b": concat is an atom/STRING
        # function in this build ("concat: argument must be an atom",
        # measured 2026-08-20) and `++` parses as two unary pluses;
        # flatten of a list of flat lists is the list concatenation.
        print("mr_rule_table : flatten(["
              + ", ".join(table_terms) + "])$")

if __name__ == "__main__":
    main()
