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
