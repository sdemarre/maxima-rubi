#!/usr/bin/env python3
"""Legacy class-1 launcher (documented interface, AGENTS.md). The
implementation is test/launch_class_shards.py (milestone 2)."""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.argv = ["launch_class_shards.py",
            "1 Algebraic functions",
            os.path.join(ROOT, "test", "corpus_class1.out"),
            os.path.join("test", "corpus_class1_driver.py")] \
    + list(sys.argv[1:])
runpy.run_path(os.path.join(HERE, "launch_class_shards.py"),
              run_name="__main__")
