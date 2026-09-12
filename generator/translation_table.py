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
    # Rubi's undocumented $UseGamma control global (absent from Rubi.m;
    # the class-2 corpus headers assume it false) — a VARIABLE, not a
    # function (the SimplifyFlag precedent):
    "$UseGamma": "mr_use_gamma_flag",
}

# Structural rewrites (not 1:1 renames): token -> handler name in the emitter.
RESTRUCTURE = {
    "GtQ": "cmp", "LtQ": "cmp", "LeQ": "cmp", "GeQ": "cmp",
    "IGtQ": "cmp", "ILtQ": "cmp", "ILeQ": "cmp",
    "Int": "mr_int",              # Int[smaller, x] -> mr_int(smaller, x)
    "Unintegrable": "noun", "CannotIntegrate": "noun",   # -> mr_unintegrable
    "IntHide": "mr_int",
    # Sum is emitter-dispatched (Task 6 E5): mr_sum(fun, var, lo, hi) is
    # 4-arg; Rubi's iterator {var, lo, hi} must be split, not renamed 1:1.
    # The package mr_sum CONCRETIZES numeric bounds per integer index, so a
    # non-identifier summand is lambda-wrapped by the emitter to survive
    # Maxima's eager argument evaluation (generate_class1.py Sum handler).
    "With": "block", "Module": "block",
    "If": "if",
    # Answer-side special functions: keep the NATIVE Maxima names. They
    # are not package-defined shims, so the anti-masking %mr_ rule does
    # not apply; emitting the native noun lets `diff` differentiate the
    # answer (measured 2026-08-24 on 5.50.0) and cancels against the
    # corpus's native expected answers.
    "EllipticF": "elliptic_f", "EllipticE": "elliptic_e",
    "EllipticPi": "elliptic_pi",
    "Hypergeometric2F1": "hypergeometric",   # list-form args
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
