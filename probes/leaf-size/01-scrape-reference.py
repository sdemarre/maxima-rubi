#!/usr/bin/env python3
"""Scrape the per-integral results of the 12000.org independent-test-suite
reports (summer 2022 edition, Nasser M. Abbasi), the reference whose leaf size
and A/B/C/F grade we reproduce (user request 2026-09-30).

For every integral page (reportsubsection<N>.htm) of each suite it records the
problem number, the optimal antiderivative's leaf size (Mathematica LeafCount)
and its [Out] text, and for Rubi and Maxima the grade, time and size the
report gives. Rubi and Mathematica sizes are Mathematica's LeafCount; Maxima's
is SageMath's tree_size (report section 4.2.4 / 1.9.3).

    python3 probes/leaf-size/01-scrape-reference.py [SUITE ...] > probes/leaf-size/01-scrape-reference.tsv

SUITE is a report directory name, e.g. 12_Wester_Problems (default: all 12).
Pages are cached under $MR_SCRAPE_CACHE (default /tmp/mr-leaf-scrape).

The story these measurements belong to: docs/grading-and-leaf-size.md.
"""

import html
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = ("https://www.12000.org/my_notes/CAS_integration_tests/reports/summer_2022/"
        "test_cases/0_Independent_test_suites/")
SUITES = ["1_Apostol_Problems", "2_Bondarenko_Problems", "3_Bronstein_Problems",
          "4_Charlwood_Problems", "5_Hearn_Problems", "6_Hebisch_Problems",
          "7_Jeffrey_Problems", "8_Moses_Problems", "9_Stewart_Problems",
          "10_Timofeev_Problems", "11_Welz_Problems", "12_Wester_Problems"]
CACHE = os.environ.get("MR_SCRAPE_CACHE", "/tmp/mr-leaf-scrape")


def fetch(url):
    path = os.path.join(CACHE, re.sub(r"[^\w.-]", "_", url[len(BASE):]))
    if os.path.exists(path):
        return open(path, encoding="utf-8", errors="replace").read()
    for attempt in range(3):
        try:
            # The site answers 403 to urllib's default User-Agent (measured
            # 2026-09-30); curl's is accepted.
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ""
            if attempt == 2:
                raise
            time.sleep(2)
        except Exception:
            if attempt == 2:
                return ""
            time.sleep(2)
    os.makedirs(CACHE, exist_ok=True)
    open(path, "w", encoding="utf-8").write(data)
    time.sleep(0.2)
    return data


def text(page):
    t = re.sub(r"<script.*?</script>", " ", page, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def cas_block(t, name, sizeword):
    m = re.search(name + r" \[([A-Z](?:\(-?\d\))?)\] time = ([\d.]+), " + sizeword + r" = (\d+)", t)
    if m:
        return m.group(1), m.group(2), m.group(3)
    m = re.search(name + r" \[([A-Z](?:\(-?\d\))?)\]", t)
    return (m.group(1), "-", "-") if m else ("-", "-", "-")


def main(argv):
    suites = argv or SUITES
    print("suite\tproblem\toptimal_leaf\trubi_grade\trubi_size\tmaxima_grade\tmaxima_size\toptimal_out")
    for s in suites:
        misses = 0
        n = 0
        while misses < 3:
            n += 1
            page = fetch(f"{BASE}{s}/reportsubsection{n}.htm")
            if not page or "Page Not Found" in page:
                misses += 1
                continue
            misses = 0
            t = text(page)
            m = re.search(r"\[(\d+)\] .*?Optimal[^.]*\. Leaf size=(\d+)", t)
            if not m:
                continue
            out = re.search(r"Leaf size=\d+ .*?\[Out\] (.*?) _{10,}", t)
            rubi = cas_block(t, "Rubi", "antiderivative size")
            maxima = cas_block(t, "Maxima", "size")
            print("\t".join([s, m.group(1), m.group(2), rubi[0], rubi[2], maxima[0], maxima[2],
                             out.group(1).strip() if out else "-"]))
            sys.stdout.flush()


if __name__ == "__main__":
    main(sys.argv[1:])
