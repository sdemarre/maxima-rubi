import re, sys
P = "generator/generate_rules.py"
src = open(P).read()

def between(src, start, end):
    i = src.index(start); j = src.index(end, i)
    return i, j

# 1. imports
old = "from translation_table import RENAME, RESTRUCTURE\n"
assert src.count(old) == 1
src = src.replace(old, old + "import mma_reader as rd  # the evaluated-FullForm reader (spec 3.4)\nfrom fractions import Fraction\n")

# 2. translate_atom: drop the MatchQ-marker pattern-side branch
i = src.index('                # A pattern-variable marker. MatchQ pattern scope first')
j = src.index('                if name == "x":', i)
new_branch = '''                # A pattern-variable marker in cond/repl text (patterns are
                # emitted by pattern_sexp / _emit_matchq, never translated):
                # the integration variable, then this rule's lhs captures.
                # FIX F11: a marker on a name in neither is a variable the
                # emitter cannot rename — fail loudly, never emit a bare
                # underscore that Maxima would read as a fresh pattern
                # variable.
'''
src = src[:i] + new_branch + src[j:]

# 3. _emit_matchq
i, j = between(src, "def _emit_matchq(arglist, ctx):", "def emit_head(head, arglist, ctx):")
src = src[:i] + open(sys.argv[1] + "/new_matchq.py").read() + "\n" + src[j:]

# 4. emit_head: headvar branch + With/Module
i = src.index('    if head == ctx.get("headvar"):')
j = src.index('    if head == "FreeQ":', i)
src = src[:i] + src[j:]
i = src.index('    if head == "With" or head == "Module":')
j = src.index('    if head == "If":', i)
src = src[:i] + open(sys.argv[1] + "/new_with.py").read() + src[j:]

# 5. emit_rule + emit_file
i, j = between(src, "def emit_rule(run, key, n, rule_vars):", "def load_class_files(rubi):")
src = src[:i] + open(sys.argv[1] + "/new_emit.py").read() + "\n" + src[j:]

# 6. configure + main
i = src.index("def configure(class_num):")
src = src[:i] + open(sys.argv[1] + "/new_main.py").read()
open(P, "w").write(src)
print("spliced", len(src.splitlines()), "lines")
