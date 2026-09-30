# mr_cpu_timed around rubi: the dispatcher swallows the timer as a matcher fault

Status: needs-triage
Type: bug (checker timer vs dispatcher fault handler)
Filed: 2026-09-29 (found tracing 7.3.6 e669, `.scratch/class-ports/issues/26`)

## What

`mr_cpu_timed(rubi(f, x), 8)` (test/mr_verify.lisp) RETURNED an answer for an integrand that
needs 58 s of CPU. Its `rubi_verbose : true` trace shows 15 lines

    rubi: rule 1_1_3_3 r64 matcher fault: Condition MAXIMA::MR-CPU-TIMEOUT was signalled.

The dispatcher's fault class (`maxima_rubi_dispatch.lisp` ~L631) is every serious-condition
except `sb-sys:interactive-interrupt` and `sb-ext:timeout`. The checker's `mr-cpu-timeout` /
`mr-heap-limit` are plain serious-conditions (since `1ffc606`; ERRORs before, also caught), so
each tick that lands inside a rule's match or condition is taken as that rule's fault: the rule
is skipped and rubi carries on, with a different (degraded) route and past the limit.

## Impact

None on corpus records: the driver never wraps rubi in `mr_cpu_timed` (rubi is capped by
test/mr_cpu_cap.py from outside; `mr_cpu_timed` bounds only the checker's stages, which do not
call rubi). It bites any probe that times rubi with it -- the result is then not rubi's answer.

## Fix (proposed, not applied)

Define the two conditions as subclasses of `sb-ext:timeout` (itself a serious-condition, not an
error): the dispatcher already lets it propagate by design, Maxima's errcatch does not catch it
(the 1ffc606 property), and mr_cpu_timed's handler-case still names the classes. Test first in
test/test_mr_verify.mac: `mr_cpu_timed(<a rubi call on a cheap loaded rule table that loops>,
0.3)` returns `timeout`.
