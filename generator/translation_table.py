# translation_table.py — the closed token->Maxima seam (T4 §2 census).
# A token absent from both dicts is a generator error by design.

# Direct renames / shims / ports: token -> emitted name (1:1 arity).
RENAME = {
    # present
    "FreeQ": "freeof",            # arg order flips: FreeQ[e, x] -> freeof(x, e)
    "IntegerQ": "integerp", "OddQ": "oddp", "Not": "not",
    "Sqrt": "sqrt", "Log": "log", "D": "diff",
    "ArcTan": "atan", "ArcSin": "asin", "ArcCos": "acos",
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
    "AppellF1": "mr_appellf1",
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
