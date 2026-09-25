# translation_table.py — the closed token->Maxima seam (T4 §2 census).
# A token absent from both dicts is a generator error by design.

# Direct renames / shims / ports: token -> emitted name (1:1 arity).
RENAME = {
    # present
    "FreeQ": "freeof",            # arg order flips: FreeQ[e, x] -> freeof(x, e)
    "IntegerQ": "integerp", "OddQ": "oddp", "Not": "not",
    "Sqrt": "sqrt", "Log": "log", "D": "diff",
    "ArcTan": "atan", "ArcSin": "asin", "ArcCos": "acos",
    # class 3 (2026-08-29, branch_5_50_base_84_g4204fb669 / SBCL 2.6.7):
    # acot/acoth are bound natives with ratsimp-closing diffs
    # (diff(acot(x),x) = -1/(x^2+1), diff(acoth(x),x) = -1/(x^2-1));
    # the "rc" spellings arccot/arcoth are unbound nouns — the corpus
    # integrands and answers use the native spellings.
    "ArcCot": "acot", "ArcCoth": "acoth",
    "Denominator": "denom", "Numerator": "num", "Denom": "denom", "Numer": "num",
    "GCD": "gcd", "Mod": "mod", "Floor": "floor", "Factor": "factor",
    "Binomial": "binomial", "Cos": "cos", "Sin": "sin", "Expand": "expand",
    # shims (this binary lacks the name; %mr_ prefix, house rule 8)
    "Rt": "%mr_rt", "Sign": "%mr_sign", "Cancel": "%mr_cancel",
    "Together": "%mr_together",
    "ArcTanh": "%mr_atanh", "ArcSinh": "%mr_asinh", "ArcCosh": "%mr_acosh",
    # ports (Rubi utilities, Task 4/5/7)
    "EqQ": "%mr_eqQ", "NeQ": "%mr_neQ", "PossibleZeroQ": "%mr_possible_zeroQ",
    "Coeff": "%mr_coeff", "Coefficient": "%mr_coeff",
    # PolyQ is emitter-dispatched (Task 6 Step 0 / F2): (u,x)/(u,x,n)/(u,x^v
    # [,(n)]) -> %mr_polyQ/%mr_polyDegQ/%mr_polyPowerQ/%mr_polyDegPowerQ —
    # a 1:1 rename would silently treat the power form as a variable.
    "LinearQ": "%mr_linearQ", "QuadraticQ": "%mr_quadraticQ",
    "TrinomialQ": "%mr_trinomialQ", "BinomialQ": "%mr_binomialQ",
    "IntLinearQ": "%mr_intLinearQ", "IntBinomialQ": "%mr_intBinomialQ",
    "IntQuadraticQ": "%mr_intQuadraticQ",
    "Subst": "%mr_subst", "SubstFor": "%mr_substFor", "SubstPower": "%mr_substPower",
    "Simp": "%mr_simp", "Simplify": "%mr_simp", "SimplifyIntegrand": "%mr_simp",
    "ExpandToSum": "%mr_expandToSum", "ExpandIntegrand": "%mr_expandIntegrand",
    "ExpandLinearProduct": "%mr_expandLinearProduct",
    "FracPart": "%mr_fracPart", "IntPart": "%mr_intPart",
    "PolynomialQuotient": "%mr_polyQuotient",
    "PolynomialRemainder": "%mr_polyRemainder",
    "PolynomialDivide": "%mr_polyDivide", "Quotient": "%mr_polyQuotient",
    "PolyGCD": "%mr_polyGCD", "RationalFunctionExpand": "%mr_rationalFunctionExpand",
    "NormalizePseudoBinomial": "%mr_normalizePseudoBinomial",
    "Dist": "%mr_dist", "IntSum": "%mr_intSum", "RemoveContent": "%mr_removeContent",
    "RationalQ": "%mr_rationalQ", "IntegersQ": "%mr_integersQ", "FractionQ": "%mr_fractionQ",
    "PosQ": "%mr_posQ", "NegQ": "%mr_negQ",
    "LinearMatchQ": "%mr_linearMatchQ", "BinomialMatchQ": "%mr_binomialMatchQ",
    "QuadraticMatchQ": "%mr_quadraticMatchQ", "TrinomialMatchQ": "%mr_trinomialMatchQ",
    "GeneralizedBinomialQ": "%mr_generalizedBinomialQ",
    "GeneralizedTrinomialQ": "%mr_generalizedTrinomialQ",
    "GeneralizedBinomialMatchQ": "%mr_generalizedBinomialMatchQ",
    "GeneralizedTrinomialMatchQ": "%mr_generalizedTrinomialMatchQ",
    "GeneralizedBinomialDegree": "%mr_generalizedBinomialDegree",
    "GeneralizedTrinomialDegree": "%mr_generalizedTrinomialDegree",
    "BinomialDegree": "%mr_binomialDegree",
    "SumQ": "%mr_sumQ", "SumSimplerQ": "%mr_sumSimplerQ",
    "SimplerQ": "%mr_simplerQ", "SimplerSqrtQ": "%mr_simplerSqrtQ",
    "NiceSqrtQ": "%mr_niceSqrtQ", "RationalFunctionQ": "%mr_rationalFunctionQ",
    "MatchQ": "%mr_matchQ", "SplitProduct": "%mr_splitProduct",
    "NonfreeFactors": "%mr_nonfreeFactors",
    "FractionalPowerFactorQ": "%mr_fractionalPowerFactorQ",
    "LeafCount": "%mr_leafCount", "MonomialQ": "%mr_monomialQ",
    "PerfectSquareQ": "%mr_perfectSquareQ", "AtomQ": "%mr_atomQ",
    "LinearPairQ": "%mr_linearPairQ", "PseudoBinomialPairQ": "%mr_pseudoBinomialPairQ",
    "InverseFunctionQ": "%mr_inverseFunctionQ",
    "AlgebraicFunctionQ": "%mr_algebraicFunctionQ",
    # added by the Task 6 full-class closure check (the four heads the
    # census tier table missed in class 1):
    "PolynomialQ": "%mr_polynomialQ",   # C-tier port, Task 7
    "FractionalPart": "%mr_fracPart",   # Mathematica builtin = FracPart
    "IntegerPart": "%mr_intPart",       # Mathematica builtin = IntPart
    "SimplifyFlag": "mr_simplify_flag", # ShowStepRoutines.m :3 global (utils)
    # class 2 (exponentials) — answer-side natives (the naming trap: the
    # public names carry underscores; describe(name, exact) is the
    # arbiter — probed 2026-08-28 on 5.50.0, the identities close:
    # diff(gamma_incomplete(a,z),z) = -z^(a-1) %e^-z [UPPER, the corpus
    # GAMMA(a,z) convention], diff(expintegral_ei(z),z) = %e^z/z,
    # erf/erfi native):
    "Exp": "exp", "Erf": "erf", "Erfi": "erfi",
    "ExpIntegralEi": "expintegral_ei",
    "Gamma": "gamma_incomplete",   # arity-dispatched in the emitter (Task 2,
                                   # class 3): 1-arg -> gamma (3.5's
                                   # Log[Gamma[v_]]), 2-arg ->
                                   # gamma_incomplete (class 2: 5/5 2-arg
                                   # UPPER — unchanged), any other arity is
                                   # a loud GenError (the PolyQ dispatch
                                   # pattern; the RENAME value is the 2-arg
                                   # behavior and documents it)
    # class-2 utility ports (Tasks 4-6):
    "TrueQ": "%mr_trueQ", "PowerQ": "%mr_powerQ",
    "Exponent": "%mr_degree",      # M1 port — general polynomial degree
    "FullSimplify": "ratsimp",     # measured approximation: on the
                                   # class-2 sites (symbolic quotients of
                                   # free constants) ratsimp preserves the
                                   # quotient so num/denom read the
                                   # formal Numerator/Denominator (the
                                   # unit test pins denom() on r61's shape)
    "PowerOfLinearQ": "%mr_powerOfLinearQ",
    "PowerOfLinearMatchQ": "%mr_powerOfLinearMatchQ",
    "NormalizePowerOfLinear": "%mr_normalizePowerOfLinear",
    "FunctionExpand": "%mr_functionExpand",
    "FunctionOfExponentialQ": "%mr_functionOfExponentialQ",
    "FunctionOfExponential": "%mr_functionOfExponential",
    "FunctionOfExponentialFunction": "%mr_functionOfExponentialFunction",
    "NormalizeIntegrand": "%mr_normalizeIntegrand",
    # class 3 (logarithms) — answer-side natives (the naming trap: the
    # public names carry underscores; describe(name, exact) is the
    # arbiter). Probed 2026-08-29 on branch_5_50_base_84_g4204fb669 /
    # SBCL 2.6.7 (the 2026-08-29 rebuild): all five are bound and
    # float-evaluable, and each diff closes to 0 under ratsimp:
    #   d/dx expintegral_shi(x) = sinh(x)/x
    #   d/dx expintegral_chi(x) = cosh(x)/x
    #   d/dx expintegral_si(x)   = sin(x)/x
    #   d/dx expintegral_ci(x)   = cos(x)/x
    #   d/dx expintegral_li(x)   = 1/log(x)
    # while the SHORT names shi/chi/si/ci are UNBOUND nouns (ev(shi(0.5))
    # stays `shi(0.5)` — emitting a short name would make the answer a
    # noun). Chi/Shi/Si/Ci are answer-side ONLY: the class-3 census
    # (probes/translation/04-class3-syntax-census.out) shows no class-3
    # rule emits them — they occur only in the corpus expected texts the
    # Task-8 driver normalizes — so the four rows are inert for class 3
    # and exist to keep the closed table complete.
    "Chi": "expintegral_chi",
    "Shi": "expintegral_shi",
    "Si": "expintegral_si",
    "Ci": "expintegral_ci",
    "LogIntegral": "expintegral_li",
    # class 6 (2026-09-20): the RULE-side spellings of the same two
    # functions. Mathematica's CoshIntegral[z] IS Chi(z) and
    # SinhIntegral[z] IS Shi(z), so these map onto the same natives the
    # Chi/Shi rows above give the answer side. Unlike Chi/Shi these are
    # NOT inert: class 6 emits them from replacements (6.1.12 Sinh[d
    # x^n]/x and its Cosh sibling, 1 rule each —
    # probes/translation/05-class6-syntax-census.out). Re-measured on the
    # rule side, build branch_5_50_base_84_g4204fb669
    # (probes/answer-side/03-class6-answer-side-identities.out R1-R4):
    # d/dz expintegral_chi(z) = cosh(z)/z and d/dz expintegral_shi(z) =
    # sinh(z)/z, both residuals closing through the harness zero chain,
    # both float-evaluable.
    "CoshIntegral": "expintegral_chi",
    "SinhIntegral": "expintegral_shi",
    # 1:1 rename to the native spelling: the active class-3 corpus
    # expected texts are natively spelled (2,793 polylog( occurrences —
    # probes/corpus/03-class3-answer-heads.out). The build's
    # diff(polylog(2,x),x) and ev(polylog(2,0.5)) both stay nouns
    # (measured 2026-08-29 on branch_5_50_base_84_g4204fb669), so there
    # is no spurious self-diff closure; a form-identical expected answer
    # still closes because identical terms cancel before the diff.
    "PolyLog": "polylog",
    # class-3 utility ports (Tasks 4-5): the %mr_ names do not exist
    # yet — the table is static closure, the ports land in Tasks 4-5
    # (the class-2 port rows above are the precedent for this state).
    "InverseFunctionFreeQ": "%mr_inverseFunctionFreeQ",
    "MemberQ": "%mr_memberQ",
    "FalseQ": "%mr_falseQ",
    "ProductQ": "%mr_productQ",
    "IntegralFreeQ": "%mr_integralFreeQ",
    "RationalFunctionExponents": "%mr_rationalFunctionExponents",
    "DerivativeDivides": "%mr_derivativeDivides",
    "SubstForFractionalPowerOfLinear": "%mr_substForFractionalPowerOfLinear",
    # class-3 deferred campaign C6b (3.5.m L46 FunctionOfLog catch-all):
    "FunctionOfLog": "%mr_functionOfLog",
    "NonsumQ": "%mr_nonsumQ",
    # 9.1 as a generated source (matcher substrate spec 3.4): Identity[-1],
    # Complex[Identity[0], a] (9.1.m L14/L15). Maxima's identity(x)
    # returns x (describe("identity", exact), 2026-09-12).
    "Identity": "identity",
    # class-6 utility ports (Step 4): the %mr_ names do not exist yet —
    # the table is static closure, the ports land at Step 4 (the class-2
    # and class-3 port rows above are the precedent for this state). The
    # census's token closure
    # (.scratch/class-ports/issues/03-class6-hyperbolic-functions.md,
    # 2026-09-20) adjudicates these as the class's WHOLE porting surface:
    # 8 functions over 53 rule-uses.
    "HyperbolicQ": "%mr_hyperbolicQ",
    "IndependentQ": "%mr_independentQ",
    "QuotientOfLinearsQ": "%mr_quotientOfLinearsQ",
    "QuotientOfLinearsParts": "%mr_quotientOfLinearsParts",
    "ExpandTrigReduce": "%mr_expandTrigReduce",
    "ExpandTrigToExp": "%mr_expandTrigToExp",
    "ExpandTrigExpand": "%mr_expandTrigExpand",
    # Rubi's six INERT trig heads (inert-trig substrate design 3.1), the
    # LOWERCASE spellings. They are distinct tokens from the active
    # "Sin"/"Cos"/... rows above (this table is case-sensitive), and they
    # map to the six %mr_i* operators Task 1 measured inert
    # (probes/maxima/probe-inert-operator-inertness.out, 44/0) and Task 2
    # wired into mr-tree's +functions+ as the arity-1 tree heads
    # sin/cos/tan/cot/sec/csc. The rows serve BOTH positions:
    #   * head position — sin[v] -> %mr_isin(v);
    #   * ATOM position — Rubi passes the bare head as a value
    #     (ReduceInertTrig[sin,v], PowerOfInertTrigSumQ[w,sin,x],
    #     Switch[func, sin, ...]). The dispatcher binds a head-position
    #     capture to exactly this operator symbol (maxima_rubi_dispatch.lisp
    #     mr-binding-value / mr-head-verb), so a bare head and a bound head
    #     capture are the SAME Maxima symbol and compare with `=`.
    "sin": "%mr_isin", "cos": "%mr_icos", "tan": "%mr_itan",
    "cot": "%mr_icot", "sec": "%mr_isec", "csc": "%mr_icsc",
    # The three generated rewrite functions themselves (inert-trig
    # substrate design 3.2, Task 4): their clauses are self-recursive, so
    # a repl body calls the wrapper that re-enters the walk.
    "UnifyInertTrigFunction": "%mr_unifyInertTrigFunction",
    "FixInertTrigFunction": "%mr_fixInertTrigFunction",
    "ReduceInertTrig": "%mr_reduceInertTrig",
    # Two predicates the FixInertTrigFunction conds call, both ported in
    # maxima_rubi_utils.mac: %mr_inertReciprocalQ (Task 4; one line in Rubi
    # too) and %mr_powerOfInertTrigSumQ (commit 826e134, with the
    # 3-argument ReduceInertTrig).
    "InertReciprocalQ": "%mr_inertReciprocalQ",
    "PowerOfInertTrigSumQ": "%mr_powerOfInertTrigSumQ",
    # inert-trig substrate plan, Task 9: the tokens of the bridge's six
    # bare-u_ records (4.1.0.1 r1, 4.7.5 r21/r22/r47/r48/r58). The ACTIVE
    # circular heads Tan/Cot join Sin/Cos/Sec/Csc above (natives); the
    # substrate utilities map to their maxima_rubi_utils.mac ports.
    # %mr_tryPureTanSubst: unported at Task 9 (4.7.5 r21/r22 declined on
    # the unbound call); ported at Task 10 with %mr_calculusFreeQ, the
    # Weierstrass record's (4_7_5 r71) inner condition.
    "Tan": "tan", "Cot": "cot",
    "FunctionOfTrigOfLinearQ": "%mr_functionOfTrigOfLinearQ",
    "DeactivateTrig": "%mr_deactivateTrig",
    "ActivateTrig": "%mr_activateTrig",
    "FunctionOfTrig": "%mr_functionOfTrig",
    "FreeFactors": "%mr_freeFactors",
    "FunctionOfQ": "%mr_functionOfQ",
    "TryPureTanSubst": "%mr_tryPureTanSubst",
    "CalculusFreeQ": "%mr_calculusFreeQ",
    # Task 10 fix round 1: 4.7.5 r72's condition (the re-activating
    # CannotIntegrate catch-all). One argument in both Rubi and the port.
    "InertTrigFreeQ": "%mr_inertTrigFreeQ",
    # Rubi's undocumented $UseGamma control global (absent from Rubi.m;
    # the class-2 corpus headers assume it false) — a VARIABLE, not a
    # function (the SimplifyFlag precedent):
    "$UseGamma": "mr_use_gamma_flag",
    # section 9 (2026-09-22): 9.2's gate and 9.3's Divides
    # (maxima_rubi_utils.mac, task-2 brief).
    "PiecewiseLinearQ": "%mr_piecewiseLinearQ",
    "Divides": "%mr_divides",
    # section 9 G2a (2026-09-22, task-3 brief): EulerIntegrandQ (a
    # generated rewrite table) and its two hand-ported callers.
    "EulerIntegrandQ": "%mr_eulerIntegrandQ",
    "SimplerIntegrandQ": "%mr_simplerIntegrandQ",
    # section 9 G2b (2026-09-22, task-4 brief): SubstForFractionalPowerQ,
    # PolynomialInQ, PolynomialInSubst (the AuxQ/Aux helpers are internal,
    # not generated-rule tokens).
    "SubstForFractionalPowerQ": "%mr_substForFractionalPowerQ",
    "PolynomialInQ": "%mr_polynomialInQ",
    "PolynomialInSubst": "%mr_polynomialInSubst",
    # section 9 G3 (2026-09-22, task-5 brief): PowerVariableExpn (the
    # Degree/Subst helpers are internal, not generated-rule tokens).
    "PowerVariableExpn": "%mr_powerVariableExpn",
    # section 9 G4 (2026-09-22, task-6 brief): FunctionOfSquareRootOfQuadratic
    # (the 3-arg overload and SquareRootOfQuadraticSubst are internal,
    # not generated-rule tokens -- the census shows only the 2-arg call).
    "FunctionOfSquareRootOfQuadratic": "%mr_functionOfSquareRootOfQuadratic",
    # section 9 G5 (2026-09-22, task-7 brief): SubstForFractionalPowerOf-
    # QuotientOfLinears (FractionalPowerOfQuotientOfLinears is internal,
    # not a generated-rule token).
    "SubstForFractionalPowerOfQuotientOfLinears": "%mr_substForFractionalPowerOfQuotientOfLinears",
    # section 9 G6b (2026-09-22, task-9 brief): FunctionOfLinear (the
    # 5-arg overload and FunctionOfLinearSubst are internal, not
    # generated-rule tokens).
    "FunctionOfLinear": "%mr_functionOfLinear",
    # class 8 (2026-09-25): the special-function heads, NATIVE spellings
    # (the naming trap: the public names carry underscores). Each one
    # differentiates through the harness zero chain and float-evaluates,
    # build branch_5_50_base_84_g4204fb669
    # (probes/answer-side/04-class8-answer-side-identities.out A1-A7,
    # E1-E5): d/dz fresnel_s(z) = sin(%pi z^2/2), fresnel_c -> cos(..),
    # erfc -> -2 %e^-z^2/sqrt(%pi), expintegral_si -> sin(z)/z,
    # expintegral_ci -> cos(z)/z, expintegral_e(n,z) -> -expintegral_e(n-1,z),
    # lambert_w -> lambert_w(z)/(z (1+lambert_w(z))). mr-tree's +functions+
    # already maps all seven, so patterns need nothing new. Census counts
    # (rules): ProductLog 44, FresnelS/FresnelC 28 each, Erfc 22,
    # SinIntegral/CosIntegral 14 each, ExpIntegralE 10
    # (probes/translation/09-class8-syntax-census.out).
    "ProductLog": "lambert_w",
    "FresnelS": "fresnel_s", "FresnelC": "fresnel_c",
    "Erfc": "erfc",
    "SinIntegral": "expintegral_si", "CosIntegral": "expintegral_ci",
    "ExpIntegralE": "expintegral_e",
    # class 5 (2026-09-25): the two inverse-trig heads the earlier classes
    # never met, NATIVE spellings. Both differentiate through the harness
    # zero chain and float-evaluate on their real domain |z| >= 1, and
    # their conventions are Mathematica's -- asec(z) = acos(1/z), acsc(z) =
    # asin(1/z) -- build branch_5_50_base_84_g4204fb669
    # (probes/answer-side/05-class5-answer-side-identities.out A5/A6,
    # E5-E8, C1/C2/C4-C6). mr-tree already maps both heads. Census: 31
    # rules each (probes/translation/10-class5-syntax-census.out).
    "ArcSec": "asec", "ArcCsc": "acsc",
    # class 5: Mathematica's polynomial discriminant, 5.3.7 r27/r28 (the
    # two ShowSteps rules; the quadratic v of Int[u_*v_^n_., x]). The
    # native poly_discriminant equals Mathematica's Discriminant on a
    # symbolic quadratic (b^2-4ac) and cubic (probe 05 D1-D3).
    "Discriminant": "poly_discriminant",
    # class 5 utility rows. ExpandExpression is ported since class 1 (the
    # ExpandIntegrand catch-all) and first called by a rule here (5.1.5
    # r9/r10); the other four are the class's Step-4 ports: HalfIntegerQ
    # (8 rules, 5.1.3/5.1.4), and the 5.3.7 r27/r28 trio --
    # InverseFunctionOfLinear, SubstForInverseFunction (3-arg) and Head
    # (EqQ[Head[tmp], ArcTan]: op() of the call, compared with the bare
    # head atom, which this table renames to the same native symbol --
    # probe 05 H1-H3).
    "ExpandExpression": "%mr_expandExpression",
    "HalfIntegerQ": "%mr_halfIntegerQ",
    "InverseFunctionOfLinear": "%mr_inverseFunctionOfLinear",
    "SubstForInverseFunction": "%mr_substForInverseFunction",
    "Head": "%mr_head",
    # class 7 (2026-09-25): the two inverse-hyperbolic heads the earlier
    # classes never met, NATIVE spellings. Both differentiate through the
    # harness zero chain, float-evaluate on their real domain (asech on
    # (0, 1], acsch off 0), and follow Mathematica's conventions --
    # asech(z) = acosh(1/z), acsch(z) = asinh(1/z) -- build
    # branch_5_50_base_84_g4204fb669
    # (probes/answer-side/06-class7-answer-side-identities.out A5/A6,
    # E5/E6/E9, C1/C2/C4-C6). mr-tree already maps both heads. Census: 38
    # and 36 rules (probes/translation/11-class7-syntax-census.out).
    "ArcSech": "asech", "ArcCsch": "acsch",
}

# Per-class overrides of RENAME, consulted first by the generator's
# translate_token (generate_rules.py) for the class being generated only.
#
# class 7 (2026-09-25): ArcTanh / ArcSinh / ArcCosh emit the NATIVE heads,
# not the %mr_atanh / %mr_asinh / %mr_acosh log-form shims the RENAME rows
# above give every other class. Section 7's rules recurse on their own
# heads -- Int[(a+b ArcSinh[c x])^n, x] reduces to Int[x (a+b ArcSinh[c
# x])^(n-1)/Sqrt[1+c^2 x^2], x], which a 7.1.2 rule matches on the
# pattern's ArcSinh (mr-tree: asinh). A shim evaluates on the spot to its
# log / product body (probes/answer-side/06 K1/K2), so the recursive
# integrand would no longer carry the head any class-7 pattern names, and
# 7.3.7's EqQ[Head[tmp], ArcTanh] would compare op() (atanh, probe 06 H1)
# with %mr_atanh. The natives are bound, differentiate through the zero
# chain and float-evaluate (probe 06 A1-A4, E1-E4); logarc is off and
# ratsimp/radcan leave them alone (S11-S13). Classes 1/2/3/5/9 keep the
# shims (byte-identity of their accepted records); their few recursive
# uses are ticket .scratch/class-ports/issues/18.
CLASS_RENAME = {
    7: {"ArcTanh": "atanh", "ArcSinh": "asinh", "ArcCosh": "acosh"},
}

# Structural rewrites (not 1:1 renames): token -> handler name in the emitter.
RESTRUCTURE = {
    "GtQ": "cmp", "LtQ": "cmp", "LeQ": "cmp", "GeQ": "cmp",
    "IGtQ": "cmp", "ILtQ": "cmp", "ILeQ": "cmp",
    "Int": "mr_int",              # Int[smaller, x] -> mr_int(smaller, x)
    "Unintegrable": "noun", "CannotIntegrate": "noun",   # -> mr_unintegrable
    # class 6 (2026-09-20): Rubi's third inert-integral head, same 2-arg
    # shape (Int[Tanh[a+b x+c x^2]^n, x] := Integral[Tanh[a+b x+c x^2]^n,
    # x], 6.3.12 and siblings; 8 rules — the census's group F). It is the
    # deliberate "leave it unevaluated" answer, so it takes the same noun
    # handler and the same mr_unintegrable(f, x) emission, which also
    # makes those 8 rules give-up rules for the mr_giveup_last switch.
    # NOTE: no class-6 corpus answer spells Integral( — the discovery
    # pass finds only Unintegrable( 364 and CannotIntegrate( 47
    # (probes/corpus/12-class6-answer-heads.out) — so whether these 8
    # rules' entries close is a Step-9 A/B question, not a table one.
    "Integral": "noun",
    "IntHide": "mr_int",
    # Sum is emitter-dispatched (Task 6 E5): mr_sum(fun, var, lo, hi) is
    # 4-arg; Rubi's iterator {var, lo, hi} must be split, not renamed 1:1.
    # The package mr_sum CONCRETIZES numeric bounds per integer index, so a
    # non-identifier summand is lambda-wrapped by the emitter to survive
    # Maxima's eager argument evaluation (generate_class1.py Sum handler).
    "With": "block", "Module": "block",
    "If": "if",
    # Switch is emitter-dispatched (inert-trig substrate, Task 4):
    # Switch[e, form, value, ...] has no 1:1 Maxima name — it becomes a
    # nested if/elseif over equality with each form. Handler name only,
    # never emitted (the HANDLER_ONLY guard).
    "Switch": "switch",
    # Answer-side special functions: keep the NATIVE Maxima names. They
    # are not package-defined shims, so the anti-masking %mr_ rule does
    # not apply; emitting the native noun lets `diff` differentiate the
    # answer (measured 2026-08-24 on 5.50.0) and cancels against the
    # corpus's native expected answers.
    "EllipticF": "elliptic_f", "EllipticE": "elliptic_e",
    "EllipticPi": "elliptic_pi",
    "Hypergeometric2F1": "hypergeometric",   # list-form args
    # class 8 (2026-09-25): the generalized pFq, 16 rules. Rubi writes
    # HypergeometricPFQ[{a..}, {b..}, z] and Maxima's native takes the
    # same shape with lists, hypergeometric([a..], [b..], z) — the list
    # braces translate to brackets on their own, so the row is a 1:1
    # rename. diff closes (d/dz 3F3([1,1,1],[2,2,2],z) =
    # 3F3([2,2,2],[3,3,3],z)/8, probe 04 A13) and it float-evaluates (E9).
    "HypergeometricPFQ": "hypergeometric",
    # class 8 (2026-09-25): PolyGamma[n, z] -> psi[n](z), Maxima's
    # SUBSCRIPTED polygamma (mr-tree's +subscripted+ reads psi[n](z) back
    # as PolyGamma). An emitter case, not a rename: the order becomes the
    # subscript. diff closes for every order the rules emit, negative
    # included (psi[-2] -> psi[-1], probe 04 A8/A9). Handler name only.
    "PolyGamma": "polygamma",
    # class 8 (2026-09-25): Zeta, arity-dispatched in the emitter. 1-arg is
    # Riemann's zeta (native `zeta`); 2-arg is the HURWITZ zeta, which
    # Maxima does not have symbolically (describe("hurwitz", inexact) finds
    # nothing; `zeta` is 1-argument) — so it is emitted as the corpus's own
    # head Zeta(s, z), an inert noun (the AppellF1 precedent): identical
    # answers cancel in the zero chain, a different form cannot verify
    # (probe 04 A16/A17). Handler name only.
    "Zeta": "zeta",
    # class 8 / 9.1 (2026-09-25): Mathematica's formal derivative
    # Derivative[n][f][u] -> %mr_derivative(n, f, u), which builds Maxima's
    # own derivative noun 'diff(f(u), u, n) (order 0: f(u)). The design
    # and its measurements: .scratch/class-ports/issues/01 ("DESIGN"),
    # probes/answer-side/04 D1-D3, N1-N17. A curried-call emitter case in
    # translate_atom. Handler name only.
    "Derivative": "derivative",
    # AppellF1: emit the SAME head the corpus expected answers use
    # (the .mac files carry AppellF1[...]). Maxima has no AppellF1
    # builtin, so both sides of the zero-test carry the identical
    # noun and an identical answer closes symbolically; the noun is
    # undifferentiable, so the numeric stage cannot false-close it
    # (measured 2026-08-25: ev of its diff is an atom, is(abs(.)<eps)
    # false). The earlier mr_appellf1 alias mismatched the corpus head
    # and made every AppellF1 entry unverified/deferred.
    "AppellF1": "AppellF1",
    # LogGamma: structural rewrite, not a rename — the emitter case
    # emits log(gamma(arg)). loggamma itself is an UNBOUND noun whose
    # diff stays undifferentiated (diff(loggamma(x),x) a noun), while
    # diff(log(gamma(x)),x) = psi[0](x) closes (both measured 2026-08-29
    # on branch_5_50_base_84_g4204fb669); the value "loggamma" is the
    # handler name only, never emitted.
    "LogGamma": "loggamma",
    "Root": "%mr_root", "Hold": "%mr_hold", "Boole": "if",
    # ShowStep is emitter-dispatched (Task 6 E4): it values to its 4th arg
    # (ReleaseHold[rhs]), which the handler emits — a "drop" would leave
    # a noun. Pi/E/I are constants mapped in translate_token (%pi/%e/%i),
    # not heads.
    "Integrate": "integrate",
    "Abs": "abs",
    "Sinh": "sinh", "Tanh": "tanh", "Csc": "csc", "Sec": "sec",
    # class 6 (2026-09-20): the four hyperbolic heads Sinh/Tanh above did
    # not already cover — Cosh 172 rules, Csch 41, Sech 38, Coth 34
    # (probes/translation/05-class6-syntax-census.out), the census's
    # group A and the bulk of its unlistied token mass. All four are
    # native, and keeping the native spelling is what lets `diff`
    # differentiate the answer and cancel against the corpus's own native
    # texts (sinh( 9,101 / cosh( 7,660 / tanh( 4,556 / sech( 3,000 /
    # coth( 2,859 / csch( 2,007 occurrences —
    # probes/corpus/12-class6-answer-heads.out). Measured bound,
    # differentiable through the harness zero chain and float-evaluable
    # on branch_5_50_base_84_g4204fb669:
    # probes/answer-side/03-class6-answer-side-identities.out H1-H6/E1-E6.
    "Cosh": "cosh", "Coth": "coth", "Sech": "sech", "Csch": "csch",
    "Piecewise": "mr_piecewise", "Min": "min", "Max": "max",
    "CoefficientList": "%mr_coefficientList",
    "Power": "power", "Plus": "plus", "Times": "times",
}

def translate(token):
    if token in RENAME:
        return RENAME[token]
    if token in RESTRUCTURE:
        return RESTRUCTURE[token]
    raise KeyError(f"unlisted token {token!r} — extend the table (T4 §2) "
                   f"before generating")
