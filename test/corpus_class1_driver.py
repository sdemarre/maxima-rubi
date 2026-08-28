#!/usr/bin/env python3
"""Legacy class-1 driver entry point. launch_class1_shards.py,
merge_class1_shards.py, launch_timeout_rerun.py, canary.py,
test_driver_parens.py, and test_mr_sum_concrete.py exec this file
IN-PROCESS (importlib spec_from_file_location + exec_module) and call
its file_list() / extract_entries() / split_elements() / maxima_run()
/ build_text() / KNOWN_CLASSES / PASS_CLASSES — the shim therefore
RE-EXPORTS those names, not just main(). The implementation is
test/corpus_driver.py (milestone 2); class-1 behavior is unchanged —
the head rewrites are a measured no-op on the class-1 section (0
renamable-head occurrences, probes/corpus/02-class2-answer-heads
covers the class-2 counts; the class-1 no-op is the driver's
`head rewrites: {}` header line on every class-1 record)."""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "corpus_driver", os.path.join(ROOT, "test", "corpus_driver.py"))
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-exports for the in-process consumers (the launcher's cost model,
# the merger's completeness assertion, the canary, and the driver unit
# tests).
file_list = _mod.file_list
extract_entries = _mod.extract_entries
split_elements = _mod.split_elements
maxima_run = _mod.maxima_run
build_text = _mod.build_text
KNOWN_CLASSES = _mod.KNOWN_CLASSES
PASS_CLASSES = _mod.PASS_CLASSES


def __getattr__(name):
    # Transparent alias: anything not re-exported above (zero_chain,
    # rules_core_state, the argv constants, ...) resolves to the real
    # module, so a consumer touching a new driver attribute does not
    # silently break (audit: a missing re-export is an AttributeError
    # at run time, not caught by any static check).
    return getattr(_mod, name)


if __name__ == "__main__":
    _mod.main()
