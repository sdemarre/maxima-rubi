import sys
P = sys.argv[1]
lines = open(P).read().split("\n")
assert lines[139].startswith("%mr_dispatch(f, x, rl, depth)"), lines[139]
assert lines[346].strip() == "%mr_seen : cons(f, %mr_seen),", lines[346]
assert lines[389].strip() == ") else ans)$", lines[389]
assert lines[455].strip().startswith("ans : %mr_dispatch(f, x"), lines[455]
assert lines[750].startswith("/* ---- MatchQ structural matcher"), lines[750]
assert lines[1088].startswith("%mr_mk(m, B)"), lines[1088]
assert lines[1229].strip() == "res))$", lines[1229]
assert lines[4125].startswith("/* Manual matcher for the two-binomial-power"), lines[4125]
assert lines[4807].strip() == "res)$", lines[4807]
assert lines[5702].startswith("/* ---- class-3 head-position capture matcher"), lines[5702]
assert lines[6744].strip() == "return(false))$", lines[6744]

MR_TOP_TAIL = """  %mr_seen : cons(f, %mr_seen),
  /* One dispatch on MR-MATCH (maxima_rubi_dispatch.lisp
     %mr_dispatch_tree): Mathematica matching semantics, so the
     compensating rescans of the defmatch runner (passes 2-4) are gone
     (matcher substrate spec section 3.5). mr_model_flags (spec 3.6,
     the G-5 arm) binds radexpand:false and logexpand:false around the
     dispatch, so the intermediate integrands keep Mathematica's shape. */
  ans : if mr_model_flags
        then block([radexpand : false, logexpand : false],
                   %mr_dispatch_tree(f, x, mr_rule_table, depth_level))
        else %mr_dispatch_tree(f, x, mr_rule_table, depth_level),
  %mr_seen : rest(%mr_seen),
  depth_level : depth_level - 1,
  if ans = false then (
    if fb then integrate(f, x)
    else mr_unintegrable(f, x)
  ) else ans)$"""

HYBRID_DISPATCH = """  ans : if mr_model_flags
        then block([radexpand : false, logexpand : false],
                   %mr_dispatch_tree(f, x, mr_rule_table, depth_level))
        else %mr_dispatch_tree(f, x, mr_rule_table, depth_level),"""

GENERALIZED_HEADER = """/* ---- generalized binomial/trinomial predicates (Task 7a cluster E) --
 * The six Generalized* shapes of the 1.4.2 normalization rules:
 * GeneralizedBinomialQ/MatchQ/Degree and GeneralizedTrinomialQ/MatchQ/
 * Degree (pinned Rubi :579-593, :1016-1088, :1450-1468). The .m Parts
 * definitions are pattern rules, so the ports match their patterns with
 * %mr_matchQ_bindings (maxima_rubi_dispatch.lisp) and read the accepted
 * binding list back with %mr_mk.
 *
 * The product cases (a_*u_, x^m_*u_) keep the port's guard against the
 * no-progress binding (a := 1 / u := u itself): the recursion on the
 * unchanged u would not terminate. The cond lambda reads the caller's u
 * (Maxima's dynamic scope: the matcher calls the lambda while the
 * function that holds u is running).
 *
 * GeneralizedTrinomialParts pins the POSITIVE orientation (n - q > 0)
 * in the sum-pattern cond: the .m's EqQ[r, 2*n-q] is satisfied by
 * either endpoint as q, while the GeneralizedTrinomialDegree use at the
 * 1.4.2 call sites (EqQ against a BinomialDegree) can only see the
 * positive gap. The boolean GeneralizedTrinomialQ / MatchQ answers are
 * unchanged (a 3-term progression always has a positive orientation). */
"""

S = {
 "triQ": '"(Power (Pattern |_mr_triQ_r1mq1_w| (Blank)) 2)", []',
 "linMq": '"(Plus (Optional (Pattern |_mr_linMq_r1mq1_a| (Blank))) (Times (MRArg 1) (Optional (Pattern |_mr_linMq_r1mq1_b| (Blank)))))", [x]',
 "quadMq1": '"(Plus (Optional (Pattern |_mr_quadMq_r1mq1_a| (Blank))) (Times (MRArg 1) (Optional (Pattern |_mr_quadMq_r1mq1_b| (Blank)))) (Times (Optional (Pattern |_mr_quadMq_r1mq1_c| (Blank))) (MRArg 2)))", [x, x^2]',
 "quadMq2": '"(Plus (Optional (Pattern |_mr_quadMq_r2mq1_a| (Blank))) (Times (Optional (Pattern |_mr_quadMq_r2mq1_c| (Blank))) (MRArg 1)))", [x^2]',
 "binMq": '"(Plus (Optional (Pattern |_mr_binMq_r1mq1_a| (Blank))) (Times (Optional (Pattern |_mr_binMq_r1mq1_b| (Blank))) (Power (MRArg 1) (Optional (Pattern |_mr_binMq_r1mq1_n| (Blank))))))", [x]',
 "triMq": '"(Plus (Optional (Pattern |_mr_triMq_r1mq1_a| (Blank))) (Times (Optional (Pattern |_mr_triMq_r1mq1_b| (Blank))) (Power (MRArg 1) (Optional (Pattern |_mr_triMq_r1mq1_n| (Blank))))) (Times (Optional (Pattern |_mr_triMq_r1mq1_c| (Blank))) (Power (MRArg 2) (Optional (Pattern |_mr_triMq_r1mq1_j| (Blank))))))", [x, x]',
}
def two(key):
    return ('"(Plus (Times (Optional (Pattern |_mr_%s_r1mq1_a| (Blank))) (Power (MRArg 1) (Optional (Pattern |_mr_%s_r1mq1_q| (Blank))))) '
            '(Times (Optional (Pattern |_mr_%s_r1mq1_b| (Blank))) (Power (MRArg 2) (Optional (Pattern |_mr_%s_r1mq1_n| (Blank))))))", [x, x]') % ((key,) * 4)
def three(key):
    return ('"(Plus (Times (Optional (Pattern |_mr_%s_r1mq1_a| (Blank))) (Power (MRArg 1) (Optional (Pattern |_mr_%s_r1mq1_q| (Blank))))) '
            '(Times (Optional (Pattern |_mr_%s_r1mq1_b| (Blank))) (Power (MRArg 2) (Optional (Pattern |_mr_%s_r1mq1_n| (Blank))))) '
            '(Times (Optional (Pattern |_mr_%s_r1mq1_c| (Blank))) (Power (MRArg 3) (Optional (Pattern |_mr_%s_r1mq1_r| (Blank))))))", [x, x, x]') % ((key,) * 6)
def prod_au(key):
    return '"(Times (Pattern |_mr_%s_r1mq1_a| (Blank)) (Pattern |_mr_%s_r1mq1_u| (Blank)))", []' % (key, key)
def prod_xu(key):
    return '"(Times (Pattern |_mr_%s_r1mq1_u| (Blank)) (Power (MRArg 1) (Optional (Pattern |_mr_%s_r1mq1_m| (Blank)))))", [x]' % (key, key)

site_text = "\n".join(lines[2367:2826])
REPL = [
 ("    and not %mr_matchQ(u, _mr_triQ_r1mq1_w^2,", "    and not %mr_matchQ(u, " + S["triQ"] + ","),
 ("  else %mr_matchQ(u, _mr_linMq_r1mq1_a + _mr_linMq_r1mq1_b * x,", "  else %mr_matchQ(u, " + S["linMq"] + ","),
 ("  else %mr_matchQ(u,\n    _mr_quadMq_r1mq1_a + _mr_quadMq_r1mq1_b * x + _mr_quadMq_r1mq1_c * x^2,",
  "  else %mr_matchQ(u,\n    " + S["quadMq1"] + ","),
 ("  or %mr_matchQ(u, _mr_quadMq_r2mq1_a + _mr_quadMq_r2mq1_c * x^2,", "  or %mr_matchQ(u, " + S["quadMq2"] + ","),
 ("  else %mr_matchQ(u, _mr_binMq_r1mq1_a + _mr_binMq_r1mq1_b * x^_mr_binMq_r1mq1_n,", "  else %mr_matchQ(u, " + S["binMq"] + ","),
 ("  else %mr_matchQ(u,\n    _mr_triMq_r1mq1_a\n    + _mr_triMq_r1mq1_b * x^_mr_triMq_r1mq1_n\n    + _mr_triMq_r1mq1_c * x^_mr_triMq_r1mq1_j,",
  "  else %mr_matchQ(u,\n    " + S["triMq"] + ","),
 ("        _mr_gbp1_r1mq1_a * x^_mr_gbp1_r1mq1_q\n        + _mr_gbp1_r1mq1_b * x^_mr_gbp1_r1mq1_n,", "        " + two("gbp1") + ","),
 ("        _mr_gbp2_r1mq1_a * _mr_gbp2_r1mq1_u,", "        " + prod_au("gbp2") + ","),
 ("        x^_mr_gbp3_r1mq1_m * _mr_gbp3_r1mq1_u,", "        " + prod_xu("gbp3") + ","),
 ("        x^_mr_gbp4_r1mq1_m * _mr_gbp4_r1mq1_u,", "        " + prod_xu("gbp4") + ","),
 ("    _mr_gbm1_r1mq1_a * x^_mr_gbm1_r1mq1_q\n    + _mr_gbm1_r1mq1_b * x^_mr_gbm1_r1mq1_n,", "    " + two("gbm1") + ","),
 ("        _mr_gtp1_r1mq1_a * x^_mr_gtp1_r1mq1_q\n        + _mr_gtp1_r1mq1_b * x^_mr_gtp1_r1mq1_n\n        + _mr_gtp1_r1mq1_c * x^_mr_gtp1_r1mq1_r,", "        " + three("gtp1") + ","),
 ("        _mr_gtp2_r1mq1_a * _mr_gtp2_r1mq1_u,", "        " + prod_au("gtp2") + ","),
 ("        x^_mr_gtp3_r1mq1_m * _mr_gtp3_r1mq1_u,", "        " + prod_xu("gtp3") + ","),
 ("        x^_mr_gtp4_r1mq1_m * _mr_gtp4_r1mq1_u,", "        " + prod_xu("gtp4") + ","),
 ("    _mr_gtm1_r1mq1_a * x^_mr_gtm1_r1mq1_q\n    + _mr_gtm1_r1mq1_b * x^_mr_gtm1_r1mq1_n\n    + _mr_gtm1_r1mq1_c * x^_mr_gtm1_r1mq1_r,", "    " + three("gtm1") + ","),
]
for old, new in REPL:
    assert site_text.count(old) == 1, old
    site_text = site_text.replace(old, new)
assert site_text.count("      %mr_mq_capture_self : u,\n") == 6
site_text = site_text.replace("      %mr_mq_capture_self : u,\n", "")
site_text = site_text.replace("%mr_mq_capture_self", "u")
site_text = site_text.replace("%mr_mq_capture_binding(", "%mr_matchQ_bindings(")
# the section header + capture machinery (2472-2521) -> the new header
start = site_text.index("/* ---- generalized binomial/trinomial predicates")
end = site_text.index("/* Rubi :1022-1045  GeneralizedBinomialParts")
site_text = site_text[:start] + GENERALIZED_HEADER + "\n" + site_text[end:]
assert "%mr_mq_" not in site_text, [l for l in site_text.split("\n") if "%mr_mq_" in l]

out = (lines[:77]                      # through 77
       + lines[80:139]                 # 81-139 (drop 78-80: the %mr_dispatch description)
       + lines[177:251]                # 178-251 (drop 140-177: %mr_dispatch)
       + lines[316:346]                # 317-346 (drop 252-316: the pass-4 helpers)
       + MR_TOP_TAIL.split("\n")       # replaces 347-390
       + lines[390:455]                # 391-455
       + HYBRID_DISPATCH.split("\n")   # replaces 456-460
       + lines[460:750]                # 461-750 (drop 751-1085: the MatchQ matcher head)
       + lines[1085:1096]              # 1086-1096 (%mr_mk)
       + lines[1231:2367]              # 1232-2367 (drop 1097-1231: the MatchQ matcher tail)
       + site_text.split("\n")         # 2368-2826 rewritten
       + lines[2826:4125]              # 2827-4125 (drop 4126-4809: %mr_mbp_* / %mr_lpfac / %mr_binpowfactors)
       + lines[4809:5702]              # 4810-5702 (drop 5703-6746: %mr_headvar_match / %mr_logpow_* / %mr_logratio_*)
       + lines[6746:])
open(P, "w").write("\n".join(out))
print("utils:", len(lines), "->", len(out), "lines")
