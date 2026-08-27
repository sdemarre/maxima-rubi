;; maxima_rubi_dispatch.lisp
;;
;; Arity dispatchers for the two Rubi predicates the generated class-1
;; rules call at more than one arity: %mr_binomialQ (2 and 3 args) and
;; %mr_intBinomialQ (7, 8 and 10 args — the three DISTINCT Rubi
;; definitions, 1.1.3.2:118 / 1.1.3.3:73 / 1.1.3.4:89). Maxima has no
;; function overloading and a wrong-arity call to a := function is a
;; hard error (measured, task-7a); each defmfun below catches the args
;; and re-dispatches to the fixed-arity Maxima := body in
;; maxima_rubi_utils.mac (named <name><arity>) via the
;; (mlambda (mget sym 'mexpr) args sym t nil) call primitive (the same
;; primitive mfunction-call-aux uses to invoke a := function,
;; fcall.lisp:89-94).
;;
;; The class-1 arity census (2026-08-23, over rules/class1): binomialQ
;; 2/3 (40/1), intBinomialQ 7/8/10 (21/10/44) — the only two
;; multi-arity names. %mr_integersQ / %mr_fractionQ / %mr_rationalQ
;; are 1-arg only (scalar-or-list in that one arg) and take their calls
;; directly as committed := ports; intLinearQ (7) and intQuadraticQ (8)
;; are fixed-arity. (An earlier draft dispatched %mr_integersQ 1/2/3
;; and %mr_binomialQ 2/3/4 — the census disproves the 2/3-arg
;; integersQ and 4-arg binomialQ readings; that draft was never
;; loaded.)
;;
;; Symbol mapping (measured, task-7a): a Maxima name `foo_bar` maps to
;; the Lisp symbol `|$foo_bar|` ($-prefixed, case-preserving,
;; bar-quoted).
;;
;; Load path (measured, task-7a): maxima's load() COMPILES a .lisp, and
;; a defmfun body returning a plain (non-mlambda) value fails that
;; compile; these dispatchers return only (mlambda ...) results, which
;; compile cleanly. maxima_rubi.mac loads this file through
;; %mr_load_sibling and fails loudly (witness mr_witness_dispatch,
;; which CALLS the dispatched names — a missed load leaves them nouns)
;; if the load misses.

(defmfun |$%mr_binomialQ| (&rest args)
  (let ((f (case (length args)
             (2 '|$%mr_binomialQ2|)
             (3 '|$%mr_binomialQ3|)
             (t nil))))
    (if f (mlambda (mget f 'mexpr) args f t nil)
        (merror (intl:gettext "%mr_binomialQ: bad arity ~A") (length args)))))

(defmfun |$%mr_intBinomialQ| (&rest args)
  (let ((f (case (length args)
             (7  '|$%mr_intBinomialQ7|)
             (8  '|$%mr_intBinomialQ8|)
             (10 '|$%mr_intBinomialQ10|)
             (t nil))))
    (if f (mlambda (mget f 'mexpr) args f t nil)
        (merror (intl:gettext "%mr_intBinomialQ: bad arity ~A") (length args)))))

;; Reverse-scan rule-table rescan (2026-08-26, W1 diagnosis).
;;
;; Maxima's commutative product matcher picks, for a pattern factor with a
;; non-atomic base, the FIRST factor of the target whose head is ^ — in the
;; REVERSED stored-factor order (matrun.lisp findfun, gated on the lisp
;; global matchreverse, nil = reverse). There is no backtracking: if that
;; first ^-factor's base does not match the pattern's base, the whole
;; pattern fails even when a later factor would match (measured 2026-08-26:
;; (_c*x)^_m*_r matches (d*x)^m*(c+e*x)^3 IFF the monomial power is stored
;; LAST; the stored order is Maxima's canonical sort, data-dependent). The
;; defmatch port of a Rubi rule whose product pattern carries a monomial-
;; power factor therefore 0-fires on a data-dependent subset of its own
;; family (the 1.1.3.x / 1.2.x (c x)^m classes, ~thousands of corpus
;; entries, e.g. 1.2.1.2 e115).
;;
;; matchreverse is a defmvar but the Maxima-level value does NOT reach this
;; lisp global in the installed 5.50.0 build (measured 2026-08-26: assigning
;; matchreverse in Maxima leaves the lisp global NIL and the matcher
;; unchanged), so the toggle lives here, in the same compile environment
;; as matrun.lisp. This rescan runs the WHOLE table a second time with the
;; scan direction flipped, restoring the global in unwind-protect. It is
;; strictly additive: called only after a top-level 0-firing, so pass 1 is
;; bit-identical and nothing currently passing can change.
;; (&rest args), not a fixed lambda list: in the installed 5.50.0 build a
;; fixed-parameter defmfun does NOT become a callable Maxima function
;; (the call stays a noun — measured 2026-08-27, even the documented
;; `(defmfun $foo (a b) ...)` form); the &rest dispatch is what the two
;; arity dispatchers above use and what is callable.
;;
;; The symbol is the ALL-UPPERCASE $%MR_DISPATCH_REV: Maxima names are
;; case-insensitive and an ALL-LOWERCASE name's canonical lisp symbol is
;; uppercased, while a name containing any uppercase keeps its typed case
;; (measured 2026-08-27: defmfun |$%mr_all| is dead for the call
;; %mr_all(...), |$%MR_ALL| works; |$%mr_binomialQ| works because the Q
;; keeps the typed case). A defmfun on the wrong-case symbol loads
;; fine but every call stays a noun.
(defmfun |$%MR_DISPATCH_REV| (&rest args)
  (unless (= (length args) 4)
    (merror (intl:gettext "%mr_dispatch_rev: expected 4 args, found ~A")
            (length args)))
  (unwind-protect
      (progn
        (setf matchreverse t)
        (mlambda (mget '|$%MR_DISPATCH| 'mexpr)
                args
                '|$%MR_DISPATCH| t nil))
    (setf matchreverse nil)))
