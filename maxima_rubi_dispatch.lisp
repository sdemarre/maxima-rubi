;; maxima_rubi_dispatch.lisp
;;
;; $X: the matchfix pattern-argument slot. Every generated matcher
;; lambda that must locate the pattern argument in a product references
;; it as a FREE VARIABLE (findexpon <node> $x 'times — the matcher
;; runner sets it to the actual variable before each match attempt).
;; It is not declared anywhere visible to the compiler, so SBCL warns
;; "undefined variable: MAXIMA::$X" for EVERY compilation unit that
;; references it. That is invisible in batch (load() compiles each rule
;; file as ONE unit and SBCL dedupes the warning per unit — the full
;; class-1 load prints 16) but loud in an INTERACTIVE session, where
;; load() does not compile the matchfix matchers: each match attempt
;; compiles its matcher lambda as its OWN unit, so a top-level rubi()
;; call that scans the table prints ~1,300 of the blocks (measured
;; 2026-08-27, pty session: 1,313 on call 1, 1,273 on call 2 of the
;; same integrand). SBCL already compiles an undefined free variable
;; as a dynamic (special) reference — the warning is the only signal —
;; so declaring the slot special silences it with ZERO codegen change.
;; This file loads before every rule file (maxima_rubi.mac), and
;; special declarations are package-level, so it covers both the
;; batch load-time units and the interactive per-match units.
(declaim (special $X))

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

;; Pattern-variable slot declarations (the second per-match warning
;; class, after $X above). A pattern variable that the generated
;; matcher references as a FREE variable — the structurally
;; significant slots, i.e. a power's base inside a product (the
;; u^m*(...) families: the matcher code is
;; (findexpon <node> $SLOT 'times) — the code that locates the power
;; of the matched base reads the slot) — makes each compilation unit
;; that contains it print "undefined variable: MAXIMA::<slot>". $X
;; covers the pattern-ARGUMENT slot only; the pattern-VARIABLE slots
;; (20,847 in class 1) each need their own declaration.
;;
;; %mr_load_sibling scans each rule file's matchdeclare lines and
;; declares every slot special BEFORE the load. A runtime-evaluated
;; (declaim (special ...)) reaches SBCL's later compilations — the
;; declaim must merely be executed before the unit that references the
;; slot is compiled: in batch, load() compiles the .mac at load time
;; (so the declaim precedes it), in interactive the per-match units
;; are compiled later, at call time. Measured 2026-08-27 (pty
;; sessions, foo_u^foo_m*(...) probe rule): a verified-executed
;; runtime declaim before the rule-file load -> 0 warnings (a static
;; declaim in a loaded .lisp file works too; the runtime form was
;; kept — no 21k-line generated artifact to desync from the rules).
;; Same zero-codegen property as $X: SBCL already compiles the free
;; reference as a dynamic (special) lookup.
;;
;; Every matchdeclare line in rules/class1 (generated + the manual
;; 9_1 port) is single-variable and column-0
;; "matchdeclare(<name>, <pred>)$" with <pred> in {freeof(x), true}
;; (20,847 + 149 lines, verified 2026-08-27) — the name is the first
;; comma-delimited field, which can never contain a comma.
;;
;; Maxima -> lisp name mapping for the slots (measured against the
;; observed warning symbols): "$" + the name, uppercased when the name
;; is all lowercase (foo_u -> $FOO_U, _mr_1_2_4_2_r21_u ->
;; $_MR_1_2_4_2_R21_U), typed case kept when it contains an uppercase
;; (_mr_1_4_1_r24_Pq -> $_mr_1_4_1_r24_Pq).
;;
;; The defmfun below is |$%MR_DECLAIM_MATCHVARS| — the Maxima name
;; %mr_declaim_matchvars carries its % into the lisp symbol ($ prefix,
;; % kept, no underscore inserted); a $-only symbol is defined but
;; never found and the call silently stays a noun (measured 2026-08-27).
;;
;; The scanner's with-open-file uses the all-keyword form
;; (:direction :input ...): the positional direction arg (the usual
;; `(in path nil ...)`) compiles but throws "odd number of &KEY
;; arguments" at run time in the installed 5.50.0 build (measured
;; 2026-08-27).
(defun |$mr-scan-matchvars| (path)
  (let ((names '()))
    (when (probe-file path)
      (with-open-file (in path :direction :input :if-does-not-exist nil)
        (loop for line = (read-line in nil nil)
              while line
              when (string= (if (>= (length line) 13)
                                (subseq line 0 13)
                                "")
                            "matchdeclare(") do
              (let ((comma (position #\, (subseq line 13))))
                ;; position is relative to the subseq — add the 13 back
                ;; for the absolute end index; comma = 0 (no name) is
                ;; skipped so the bare $ symbol is never touched
                (when (and comma (plusp comma))
                  (push (subseq line 13 (+ 13 comma)) names))))))
    (nreverse names)))

(defun |$mr-declaim-matchvars| (path)
  (dolist (name (remove-duplicates (|$mr-scan-matchvars| path)
                                   :test #'string=))
    (eval `(declaim (special
                     ,(intern (concatenate 'string "$"
                                           (if (string= name
                                                        (string-downcase name))
                                               (string-upcase name)
                                               name)))))))
  nil)

(defmfun |$%MR_DECLAIM_MATCHVARS| (&rest args)
  (unless (= (length args) 1)
    (merror (intl:gettext "%mr_declaim_matchvars: expected 1 arg, found ~A")
            (length args)))
  (|$mr-declaim-matchvars| (first args)))
