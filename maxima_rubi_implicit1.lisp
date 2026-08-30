;; maxima_rubi_implicit1.lisp — implicit exponent-1 factor matching
;; (the Maxima-vs-Mathematica power-storage gap). Maxima strips a
;; power's exponent 1 at construction and never restores it: a bare
;; symbol x is stored as the atom $X, a bare sum (a+b*x) as an mplus
;; with no power wrapper. The match compiler (matcom.lisp
;; compilematch) then hard-rejects a top-level MEXPT pattern against
;; such a target (compileatom head check on (kaar e)), and the
;; product-factor path (findfun, matrun.lisp) only finds factors with
;; an explicit mexpt head — so every ported family rule with a
;; (...)^m factor 0-fires on a target whose matching factor is stored
;; bare, while the identical target integrates in Rubi (Mathematica
;; treats x as x^1 in matching). Measured 2026-08-27 (Maxima 5.50.0
;; dev build 2026-08-20, SBCL 2.6.7):
;;   - x^pm        vs x            -> false  (top-level gap)
;;   - (a+b*x)^pm  vs (a+b*x)      -> false  (top-level gap)
;;   - x^pm*(a+b*x)^pm2 vs x*(a+b*x)   -> false (factor gap)
;;   - x^pm*(a+b*x)^pm2 vs x*(a+b*x)^2 -> TRUE  (atom-base factors
;;     already get the implicit 1 via findexpon memalike; sum/product
;;     bases do not)
;; Fix: a findfun shadow (below) that, when the original factor search
;; finds no explicit power factor, wraps the first eligible non-mexpt
;; factor (or the whole leftover e) in a raw (mexpt F 1) object. The
;; generated matcher then takes kdr of it -> (F 1) and compileeach
;; binds the base pattern to F and the exponent pattern to 1 with real
;; bindings, and the emitted (mquotient e (car p)) division strips F
;; with the bound exponent (=> simp to F). No backtracking is added or
;; removed: single-candidate semantics are inherited from findfun.
;; The shadow is GATED by *mr-implicit1-active* and only ever active
;; during the top-level pass-3 rescan (mr_top, fb=false, after passes
;; 1-2 0-firing) — nested mr_int dispatches run with the gate off and
;; see the verbatim original control flow, so nothing currently
;; passing can change.
;; Pass-4 candidate index (2026-08-30, class-3 deferred campaign,
;; docs/superpowers/specs/2026-08-30-class3-deferred-campaign-design.md,
;; plan docs/superpowers/plans/2026-08-30-class3-deferred-campaign.md):
;; pass 3 offers exactly ONE wrapped candidate (the first eligible
;; non-mexpt factor in scan order); a multi-bare-factor integrand
;; 0-fires whenever that one candidate is the wrong slot (measured
;; f1/f2/f5, spec section 2.2). *mr-implicit1-which* (nil = pass-3
;; behavior, byte-identical; positive integer = 1-based index) makes
;; the shadow offer the k-th eligible factor INSTEAD. The index is
;; evaluated against the factor list CURRENT at each findfun call, so
;; a multi-slot rule's later slots see the remaining factors
;; re-indexed (a slot can bind a bare leftover factor that a one-shot
;; raw-(mexpt f 1) product materialization could not offer — strictly
;; more binding power, same single-candidate-per-slot semantics, no
;; backtracking added or removed). The e-itself branch (leftover
;; single factor) wraps for ANY which, not just nil: the which index
;; only re-orders the factor branch, and the inner matches need the
;; single-factor wrap too (the original which-nil-only guard 0-fired
;; the which=i sweep — measured 2026-08-30, 3.1.5 e186); pass 3
;; (which = nil) is byte-identical, it wrapped before too. A product
;; containing an explicit mexpt factor is outside the shadow's
;; activation entirely (the original findfun returns the explicit
;; factor before the shadow runs — why f1 0-fires pass 3); the
;; pass-4 sweep skips those (the %mr_barefactors census) and the
;; %mr_p4_diag diagnostic reports the original pick instead.
;;
;; Two dev-build quirks measured while prototyping (both fatal to the
;; naive implementation):
;; 1. SBCL 2.6.7: (catch tag form RESULT) returns RESULT even when the
;;    forms complete normally (CLHS: the last form's value); the
;;    no-result form is correct. Hence the value-returning
;;    mr-orig-findfun-v instead of a catch around the throw original.
;; 2. (return v) inside a DOLIST returns from the DOLIST, not the
;;    enclosing function — the loop value is then discarded by any
;;    following form. Use return-from for the function exit.
;; Also measured: the object metas are (MEXPT|MTIMES|MPLUS SIMP [pos])
;; lists in the MAXIMA package, so mexptp/mtimesp/mplusp (caar tests)
;; accept the hand-built (MEXPT SIMP) meta, and a defmfun-returned raw
;; power round-trips to the Maxima level unsimplified (x^1 stays x^1)
;; while a hand-built MTIMES does not — hence the top-level lift wraps
;; the whole integrand object in ONE raw power instead of rebuilding
;; the product factor by factor.

(defvar *mr-implicit1-active* nil)
(defvar *mr-implicit1-which* nil)

;; The original findfun (matrun.lisp) rewritten value-returning:
;; (values factor found-p) instead of throw matcherr.
(defun mr-orig-findfun-v (e p c)
  (prog ()
     (cond ((and (null (atom e)) (eq (caar e) p)) (return (values e t)))
	   ((or (atom e) (not (eq (caar e) c))) (return (values nil nil)))
	   ((and (null matchreverse) (member c '(mplus mtimes) :test #'eq))
	    (setq e (reverse (cdr e))) (go b)))
     a    (setq e (cdr e))
     b    (cond ((null e) (return (values nil nil)))
		((and (not (atom (car e))) (eq (caaar e) p))
		 (return (values (car e) t))))
     (go a)))

(defun mr-implicit1-w (f)
  (list (list 'MEXPT 'SIMP) f 1))

;; k-th (1-based *mr-implicit1-which*) eligible non-mexpt factor of the
;; factor list, or nil when the index is out of range. Split out of
;; findfun (not inlined) because this build's compiler fatals on the
;; inlined shape: a cond arm holding three nested lets whose innermost
;; references a middle-let binding (measured 2026-08-30, the
;; minifunB/g3/h1-h4 c2-c3/g-g3/n3a-n3b bisect set); the extracted
;; two-let helper (outer binding referenced from the inner) compiles
;; clean in the same build.
(defun mr-implicit1-which-factor (factors)
  (let ((eligible (remove-if
		   #'(lambda (g) (and (consp g)
				      (eq (caar g) 'mexpt)))
		   factors)))
    (let ((k (1- *mr-implicit1-which*)))
      (if (and (integerp k) (>= k 0)
	       (< k (length eligible)))
	  (mr-implicit1-w (nth k eligible))
	  nil))))

(defun mr-implicit1-findfun (e p c)
  (cond ((not (eq p 'mexpt)) nil)
	((or (atom e) (not (eq (caar e) c)))
	 ;; e itself is the leftover single factor (or an atom): wrap it
	 ;; for ANY which, not just nil — the which index only re-orders
	 ;; the factor branch below; the inner matches need the
	 ;; single-factor wrap too. Measured 2026-08-30: the old
	 ;; which-nil-only guard 0-fired the which=i sweep (3_5_r43 on
	 ;; 3.1.5 e186), because an inner-match single-factor findfun
	 ;; call bailed; pass 3 (which=nil) is byte-identical — it
	 ;; wrapped before too.
	 (cond ((or (eq c 'mtimes) (eq c 'mplus))
	       (mr-implicit1-w e))
	       (t nil)))
	(t (let ((factors (if (null matchreverse)
			      (reverse (cdr e))
			      (cdr e))))
	     (if (null *mr-implicit1-which*)
		 (dolist (f factors)
		   (unless (and (consp f) (eq (caar f) 'mexpt))
		     (return-from mr-implicit1-findfun (mr-implicit1-w f))))
		 (mr-implicit1-which-factor factors))))))

(defun findfun (e p c)
  (multiple-value-bind (f ok) (mr-orig-findfun-v e p c)
    (cond (ok f)
	  ((null *mr-implicit1-active*) (matcherr))
	  (t (mr-implicit1-findfun e p c)))))

;; Top-level lift: one raw (mexpt f 1) around the whole integrand
;; object (the object is reused, never rebuilt — the round-trip-safe
;; shape, see the header note).
(defmfun |$%MR_LIFT1| (f)
  (mr-implicit1-w f))

;; Pass-3 rescan dispatcher: gate on, rescan the table on f, and on a
;; 0-firing rescan again on the lifted f; gate off (unwind-protected).
;; Call with (f, x, table, depth) exactly as %mr_dispatch_rev.
(defmfun |$%MR_DISPATCH_I1| (&rest args)
  (unless (= (length args) 4)
    (merror (intl:gettext "%mr_dispatch_i1: expected 4 args, found ~A")
            (length args)))
  (unwind-protect
      (let ((ans (progn
                   (setf *mr-implicit1-active* t)
                   (mlambda (mget '|$%MR_DISPATCH| 'mexpr)
                           args
                           '|$%MR_DISPATCH| t nil))))
        (or ans
            (mlambda (mget '|$%MR_DISPATCH| 'mexpr)
                    (list (mr-implicit1-w (first args))
                          (second args) (third args) (fourth args))
                    '|$%MR_DISPATCH| t nil)))
    (setf *mr-implicit1-active* nil)))
