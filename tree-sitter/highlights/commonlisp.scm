(sym_lit) @variable

;; A highlighting for functions/macros in th cl namespace is available in theHamsta/nvim-treesitter-commonlisp
;(list_lit . (sym_lit) @function.builtin (#cl-standard-function? @function.builtin))
;(list_lit . (sym_lit) @function.builtin (#cl-standard-macro? @function.macro))

(dis_expr) @comment

(defun_keyword) @function.macro
(defun_header
  function_name: (_) @function)
(defun_header
  lambda_list: (list_lit (sym_lit) @parameter))
(defun_header
  keyword: (defun_keyword "defmethod")
  lambda_list: (list_lit (list_lit . (sym_lit) . (sym_lit) @symbol)))
(defun_header
  lambda_list: (list_lit (list_lit . (sym_lit) @parameter . (_))))
(defun_header
  specifier: (sym_lit) @symbol)

[":" "::" "."] @punctuation.special

[
  (accumulation_verb)
  (for_clause_word)
  "for"
  "and"
  "finally"
  "thereis"
  "always"
  "when"
  "if"
  "unless"
  "else"
  "do"
  "loop"
  "below"
  "in"
  "from"
  "across"
  "repeat"
  "being"
  "into"
  "with"
  "as"
  "while"
  "until"
  "return"
  "initially"
] @function.macro
"=" @operator

(include_reader_macro) @symbol
["#C" "#c"] @number

[(kwd_lit) (self_referential_reader_macro)] @symbol

(package_lit
  package: (_) @namespace)
"cl" @namespace

(str_lit) @string @spell

(num_lit) @number

((sym_lit)  @boolean (#any-of? @boolean "t" "T"))

(nil_lit) @constant.builtin

(comment) @comment @spell

;; dynamic variables
((sym_lit) @variable.builtin
 (#lua-match? @variable.builtin "^[*].+[*]$"))

;; quote
"'" @string.escape
(format_specifier) @string.escape
(quoting_lit) @string.escape

;; syntax quote
"`" @string.escape
"," @string.escape
",@" @string.escape
(syn_quoting_lit) @string.escape
(unquoting_lit) @none
(unquote_splicing_lit) @none


["(" ")"] @punctuation.bracket

(block_comment) @comment @spell


(with_clause
  type: (_) @type)
(for_clause
  type: (_) @type)

;; defun-like things
(list_lit
 .
 (sym_lit) @function.macro
 .
 (sym_lit) @function
 (#eq? @function.macro "deftest"))

;;; Macros and Special Operators
(list_lit
 .
 (sym_lit) @function.macro
 ;; Generated via https://github.com/theHamsta/nvim-treesitter-commonlisp/blob/22fdc9fd6ed594176cc7299cc6f68dd21c94c63b/scripts/generate-symbols.lisp#L1-L21
 (#any-of? @function.macro
  "do*" "step" "handler-bind" "decf" "prog1" "destructuring-bind" "defconstant" "do" "lambda" "with-standard-io-syntax" "case" "restart-bind" "ignore-errors" "with-slots" "prog2" "defclass" "define-condition" "print-unreadable-object" "defvar" "when" "with-open-file" "prog" "incf" "declaim" "and" "loop-finish" "multiple-value-bind" "pop" "psetf" "defmacro" "with-open-stream" "define-modify-macro" "defsetf" "formatter" "call-method" "handler-case" "pushnew" "or" "with-hash-table-iterator" "ecase" "cond" "defun" "remf" "ccase" "define-compiler-macro" "dotimes" "multiple-value-list" "assert" "deftype" "with-accessors" "trace" "with-simple-restart" "do-symbols" "nth-value" "define-symbol-macro" "psetq" "rotatef" "dolist" "check-type" "multiple-value-setq" "push" "pprint-pop" "loop" "define-setf-expander" "pprint-exit-if-list-exhausted" "with-condition-restarts" "defstruct" "with-input-from-string" "with-compilation-unit" "defgeneric" "with-output-to-string" "untrace" "defparameter" "ctypecase" "do-external-symbols" "etypecase" "do-all-symbols" "with-package-iterator" "unless" "defmethod" "in-package" "defpackage" "return" "typecase" "shiftf" "setf" "pprint-logical-block" "time" "restart-case" "prog*" "define-method-combination" "optimize"))

;; constant
((sym_lit) @constant
 (#lua-match? @constant "^[+].+[+]$"))

(var_quoting_lit
  marker: "#'" @symbol
  value: (_) @symbol)

["#" "#p" "#P"] @symbol

(list_lit
  .
  (sym_lit) @function.builtin
  ;; Generated via https://github.com/theHamsta/nvim-treesitter-commonlisp/blob/22fdc9fd6ed594176cc7299cc6f68dd21c94c63b/scripts/generate-symbols.lisp#L1-L21
  (#any-of? @function.builtin
   "apropos-list" "subst" "substitute" "pprint-linear" "file-namestring" "write-char" "do*" "slot-exists-p" "file-author" "macro-function" "rassoc" "make-echo-stream" "arithmetic-error-operation" "position-if-not" "list" "cdadr" "lisp-implementation-type" "vector-push" "let" "length" "string-upcase" "adjoin" "digit-char" "step" "member-if" "handler-bind" "lognot" "apply" "gcd" "slot-unbound" "stringp" "values-list" "stable-sort" "decode-float" "make-list" "rplaca" "isqrt" "export" "synonym-stream-symbol" "function-keywords" "replace" "tanh" "maphash" "code-char" "decf" "array-displacement" "string-not-lessp" "slot-value" "remove-if" "cell-error-name" "vectorp" "cdddar" "two-way-stream-output-stream" "parse-integer" "get-internal-real-time" "fourth" "make-string" "slot-missing" "byte-size" "string-trim" "nstring-downcase" "cdaddr" "<" "labels" "interactive-stream-p" "fifth" "max" "logxor" "pathname-name" "function" "realp" "eql" "logand" "short-site-name" "prog1" "user-homedir-pathname" "list-all-packages" "exp" "cadar" "read-char-no-hang" "package-error-package" "stream-external-format" "bit-andc2" "nsubstitute-if" "mapcar" "complement" "load-logical-pathname-translations" "pprint-newline" "oddp" "caaar" "destructuring-bind" "copy-alist" "acos" "go" "bit-nor" "defconstant" "fceiling" "tenth" "nreverse" "=" "nunion" "slot-boundp" "string>" "count-if" "atom" "char=" "random-state-p" "row-major-aref" "bit-andc1" "translate-pathname" "simple-vector-p" "coerce" "substitute-if-not" "zerop" "invalid-method-error" "compile" "realpart" "remove-if-not" "pprint-tab" "hash-table-rehash-threshold" "invoke-restart" "if" "count" "/=" "do" "initialize-instance" "abs" "schar" "simple-condition-format-control" "delete-package" "subst-if" "lambda" "hash-table-count" "array-has-fill-pointer-p" "bit" "with-standard-io-syntax" "parse-namestring" "proclaim" "array-in-bounds-p" "multiple-value-call" "rplacd" "some" "graphic-char-p" "read-from-string" "consp" "cadaar" "acons" "every" "make-pathname" "mask-field" "case" "set-macro-character" "bit-and" "restart-bind" "echo-stream-input-stream" "compile-file" "fill-pointer" "numberp" "acosh" "array-dimensions" "documentation" "minusp" "inspect" "copy-structure" "integer-length" "ensure-generic-function" "char>=" "quote" "lognor" "make-two-way-stream" "ignore-errors" "tailp" "with-slots" "fboundp" "logical-pathname-translations" "equal" "float-sign" "shadow" "sleep" "numerator" "prog2" "getf" "ldb-test" "round" "locally" "echo-stream-output-stream" "log" "get-macro-character" "alphanumericp" "find-method" "nintersection" "defclass" "define-condition" "print-unreadable-object" "defvar" "broadcast-stream-streams" "floatp" "subst-if-not" "integerp" "translate-logical-pathname" "subsetp" "when" "write-string" "with-open-file" "clrhash" "apropos" "intern" "min" "string-greaterp" "import" "nset-difference" "prog" "incf" "both-case-p" "multiple-value-prog1" "characterp" "streamp" "digit-char-p" "random" "string-lessp" "make-string-input-stream" "copy-symbol" "read-sequence" "logcount" "bit-not" "boundp" "encode-universal-time" "third" "declaim" "map" "cons" "set-syntax-from-char" "and" "cis" "symbol-plist" "loop-finish" "standard-char-p" "multiple-value-bind" "asin" "string" "pop" "complex" "fdefinition" "psetf" "type-error-datum" "output-stream-p" "floor" "write-line" "<=" "defmacro" "rational" "hash-table-test" "with-open-stream" "read-char" "string-capitalize" "get-properties" "y-or-n-p" "use-package" "remove" "compiler-macro-function" "read" "package-nicknames" "remove-duplicates" "make-load-form-saving-slots" "dribble" "define-modify-macro" "make-dispatch-macro-character" "close" "cosh" "open" "finish-output" "string-downcase" "car" "nstring-capitalize" "software-type" "read-preserving-whitespace" "cadr" "fround" "nsublis" "defsetf" "find-all-symbols" "char>" "no-applicable-method" "compute-restarts" "pathname" "bit-orc2" "write-sequence" "pprint-tabular" "symbol-value" "char-name" "get-decoded-time" "formatter" "bit-vector-p" "intersection" "pathname-type" "clear-input" "call-method" "princ-to-string" "symbolp" "make-load-form" "nsubst" "pprint-dispatch" "handler-case" "method-combination-error" "probe-file" "atan" "string<" "type-error-expected-type" "pushnew" "unread-char" "print" "or" "with-hash-table-iterator" "make-sequence" "ecase" "unwind-protect" "require" "sixth" "get-dispatch-macro-character" "char-not-lessp" "read-byte" "tagbody" "file-error-pathname" "catch" "rationalp" "char-downcase" "char-int" "array-rank" "cond" "last" "make-string-output-stream" "array-dimension" "host-namestring" "input-stream-p" "decode-universal-time" "defun" "eval-when" "char-code" "pathname-directory" "evenp" "subseq" "pprint" "ftruncate" "make-instance" "pathname-host" "logbitp" "remf" "1+" "copy-pprint-dispatch" "char-upcase" "error" "read-line" "second" "make-package" "directory" "special-operator-p" "open-stream-p" "rassoc-if-not" "ccase" "equalp" "substitute-if" "*" "char/=" "cdr" "sqrt" "lcm" "logical-pathname" "eval" "define-compiler-macro" "nsubstitute-if-not" "mapcon" "imagpart" "set-exclusive-or" "simple-condition-format-arguments" "expt" "concatenate" "file-position" "macrolet" "keywordp" "hash-table-rehash-size" "+" "eighth" "use-value" "char-equal" "bit-xor" "format" "byte" "dotimes" "namestring" "char-not-equal" "multiple-value-list" "assert" "append" "notany" "typep" "delete-file" "makunbound" "cdaar" "file-write-date" ">" "cdddr" "write-to-string" "funcall" "member-if-not" "deftype" "readtable-case" "with-accessors" "truename" "constantp" "rassoc-if" "caaadr" "tree-equal" "nset-exclusive-or" "nsubstitute" "make-instances-obsolete" "package-use-list" "invoke-debugger" "provide" "count-if-not" "trace" "logandc1" "nthcdr" "char<=" "functionp" "with-simple-restart" "set-dispatch-macro-character" "logorc2" "unexport" "rest" "unbound-slot-instance" "make-hash-table" "hash-table-p" "reinitialize-instance" "nth" "do-symbols" "nreconc" "macroexpand" "store-value" "float-precision" "remprop" "nth-value" "define-symbol-macro" "update-instance-for-redefined-class" "identity" "progv" "progn" "return-from" "readtablep" "rem" "symbol-name" "psetq" "wild-pathname-p" "char" "list*" "char<" "plusp" "pairlis" "cddar" "pprint-indent" "union" "compiled-function-p" "rotatef" "abort" "machine-type" "concatenated-stream-streams" "string-right-trim" "enough-namestring" "arithmetic-error-operands" "ceiling" "dolist" "delete" "make-condition" "string-left-trim" "integer-decode-float" "check-type" "notevery" "function-lambda-expression" "-" "multiple-value-setq" "name-char" "push" "pprint-pop" "compile-file-pathname" "list-length" "nstring-upcase" "eq" "find-if" "method-qualifiers" "caadr" "cddr" "string=" "let*" "remove-method" "pathname-match-p" "find-package" "truncate" "caaddr" "get-setf-expansion" "loop" "define-setf-expander" "caddr" "package-shadowing-symbols" "force-output" "slot-makunbound" "string-not-greaterp" "cdadar" "cdaadr" "logandc2" "make-array" "merge-pathnames" "sin" "1-" "machine-version" "ffloor" "packagep" "set-pprint-dispatch" "flet" "gensym" "pprint-exit-if-list-exhausted" "cos" "get" "mapl" "delete-if" "with-condition-restarts" "atanh" "copy-list" "fill" "char-not-greaterp" "bit-orc1" "mod" "package-used-by-list" "warn" "add-method" "simple-string-p" "find-restart" "describe" "pathname-version" "peek-char" "yes-or-no-p" "complexp" "aref" "not" "position-if" "string>=" "defstruct" "float-radix" "ninth" "caadar" "subtypep" "set" "butlast" "allocate-instance" "with-input-from-string" "assoc" "write" "make-random-state" "bit-eqv" "float-digits" "long-site-name" "with-compilation-unit" "delete-duplicates" "make-symbol" "room" "cdar" "pprint-fill" "defgeneric" "macroexpand-1" "scale-float" "cdaaar" "update-instance-for-different-class" "array-row-major-index" "ed" "file-string-length" "ensure-directories-exist" "copy-readtable" "string<=" "seventh" "with-output-to-string" "signum" "elt" "untrace" "null" "defparameter" "block" "prin1" "revappend" "gentemp" "ctypecase" "ash" "sxhash" "listp" "do-external-symbols" "bit-ior" "etypecase" "sort" "change-class" "find-class" "alpha-char-p" "map-into" "terpri" "do-all-symbols" "ldb" "logorc1" "search" "fmakunbound" "load" "character" "string-not-equal" "pathnamep" "make-broadcast-stream" "arrayp" "mapcan" "cerror" "invoke-restart-interactively" "assoc-if-not" "with-package-iterator" "get-internal-run-time" "read-delimited-list" "unless" "lower-case-p" "restart-name" "/" "boole" "defmethod" "float" "software-version" "vector-pop" "vector-push-extend" "caar" "ldiff" "member" "find-symbol" "reduce" "svref" "describe-object" "logior" "string-equal" "type-of" "position" "cddadr" "pathname-device" "get-output-stream-string" "symbol-package" "tan" "compute-applicable-methods" "cddddr" "nsubst-if-not" "sublis" "set-difference" "two-way-stream-input-stream" "adjustable-array-p" "machine-instance" "signal" "conjugate" "caaaar" "endp" "lisp-implementation-version" "cddaar" "package-name" "adjust-array" "bit-nand" "gethash" "in-package" "symbol-function" "make-concatenated-stream" "defpackage" "class-of" "no-next-method" "logeqv" "deposit-field" "disassemble" "unuse-package" "copy-tree" "find" "asinh" "class-name" "rename-file" "values" "print-not-readable-object" "mismatch" "cadadr" "shadowing-import" "delete-if-not" "maplist" "listen" "return" "stream-element-type" "unintern" "merge" "make-synonym-stream" "prin1-to-string" "nsubst-if" "byte-position" "phase" "muffle-warning" "remhash" "continue" "load-time-value" "hash-table-size" "upgraded-complex-part-type" "char-lessp" "sbit" "upgraded-array-element-type" "file-length" "typecase" "cadddr" "first" "rationalize" "logtest" "find-if-not" "dpb" "mapc" "sinh" "char-greaterp" "shiftf" "denominator" "get-universal-time" "nconc" "setf" "lognand" "rename-package" "pprint-logical-block" "break" "symbol-macrolet" "the" "fresh-line" "clear-output" "assoc-if" "string/=" "princ" "directory-namestring" "stream-error-stream" "array-element-type" "setq" "copy-seq" "time" "restart-case" "prog*" "shared-initialize" "array-total-size" "simple-bit-vector-p" "define-method-combination" "write-byte" "constantly" "caddar" "print-object" "vector" "throw" "reverse" ">=" "upper-case-p" "nbutlast"))

(list_lit
 .
 (sym_lit) @operator
 (#match? @operator "^([+*-+=<>]|<=|>=|/=)$"))


((sym_lit) @symbol
(#lua-match? @symbol "^[&]"))

[(array_dimension) "#0A" "#0a"] @number

(char_lit) @character
