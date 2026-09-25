#!/usr/bin/env python3
"""probes/class-ports/class1/mac_defs.py -- split a Maxima .mac file into
top-level statements (terminator $ or ; outside strings, comments and
brackets) and index the function definitions `name(...) := ...` by name.

  mac_defs.py diff OLD.mac NEW.mac        names whose definition differs / is new
  mac_defs.py emit OLD.mac NAME [NAME..]  the OLD definitions, as an overlay"""
import re, sys

def statements(text):
    out, buf, depth, i, n = [], [], 0, 0, len(text)
    start = 0
    while i < n:
        c = text[i]
        if text.startswith("/*", i):
            d, i = 1, i + 2
            while i < n and d:
                if text.startswith("/*", i): d += 1; i += 2
                elif text.startswith("*/", i): d -= 1; i += 2
                else: i += 1
            continue
        if c == '"':
            i += 1
            while i < n and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
            i += 1; continue
        if c == "\\": i += 2; continue
        if c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        elif c in "$;" and depth == 0:
            out.append(text[start:i + 1]); start = i + 1
        i += 1
    return out

NAME = re.compile(r"^\s*(?:/\*.*?\*/\s*)*([%A-Za-z_][%A-Za-z0-9_]*)\s*\([^=]*?\)\s*:=", re.S)

def strip_comments(s):
    return re.sub(r"/\*.*?\*/", "", s, flags=re.S)

def defs(path):
    d = {}
    for s in statements(open(path).read()):
        body = strip_comments(s).strip()
        m = re.match(r"([%A-Za-z_][%A-Za-z0-9_]*)\s*\(", body)
        if m and ":=" in body.split("\n", 1)[0] + body[:400]:
            d[m.group(1)] = body
    return d

if __name__ == "__main__":
    if sys.argv[1] == "diff":
        a, b = defs(sys.argv[2]), defs(sys.argv[3])
        for k in b:
            if k not in a: print("NEW    ", k)
            elif re.sub(r"\s+", " ", a[k]) != re.sub(r"\s+", " ", b[k]): print("CHANGED", k)
        for k in a:
            if k not in b: print("GONE   ", k)
    else:
        a = defs(sys.argv[2])
        for k in sys.argv[3:]:
            print(a[k] + "\n")
