#!/usr/bin/env python3
"""Class-1 entry point — the documented command keeps working:
    python3 generator/generate_class1.py [--only KEY]
The general generator is generate_rules.py (milestone 2)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_rules

if __name__ == "__main__":
    generate_rules.main(1)
