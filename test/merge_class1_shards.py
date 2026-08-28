#!/usr/bin/env python3
"""Legacy class-1 merger. The implementation is
test/merge_class_shards.py (milestone 2); this forwards argv to it
with the class-1 defaults (which ARE its built-in defaults)."""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = ["merge_class_shards.py"] + list(sys.argv[1:])
runpy.run_path(os.path.join(HERE, "merge_class_shards.py"),
               run_name="__main__")
