;; ----------------------------------------------------------------------------
;; Literals and comments

(integer) @number
(exp_negation) @number
(exp_literal (float)) @float
(char) @character
(string) @string

(con_unit) @symbol  ; unit, as in ()

(comment) @comment


;; ----------------------------------------------------------------------------
;; Punctuation

[
  "("
  ")"
  "{"
  "}"
  "["
  "]"
] @punctuation.bracket

[
  (comma)
  ";"
] @punctuation.delimiter


;; ----------------------------------------------------------------------------
;; Keywords, operators, includes

[
  "forall"
  "∀"
] @repeat

(pragma) @preproc

[
  "if"
  "then"
  "else"
  "case"
  "of"
] @conditional

[
  "import"
  "qualified"
  "module"
] @include

[
  (operator)
  (constructor_operator)
  (type_operator)
  (tycon_arrow)
  (qualified_module)  ; grabs the `.` (dot), ex: import System.IO
  (qualified_type)
  (qualified_variable)
  (all_names)
  (wildcard)
  "."
  ".."
  "="
  "|"
  "::"
  "=>"
  "->"
  "<-"
  "\\"
  "`"
  "@"
] @operator

(module) @namespace

[
  (where)
  "let"
  "in"
  "class"
  "instance"
  "pattern"
  "data"
  "newtype"
  "family"
  "type"
  "as"
  "hiding"
  "deriving"
  "via"
  "stock"
  "anyclass"
  "do"
  "mdo"
  "rec"
  "infix"
  "infixl"
  "infixr"
] @keyword


;; ----------------------------------------------------------------------------
;; Functions and variables

(variable) @variable
(pat_wildcard) @variable
(signature name: (variable) @variable)

(function
  name: (variable) @function
  patterns: (patterns))
(function
  name: (variable) @function
  rhs: (exp_lambda))
((signature (variable) @function (fun)) . (function (variable)))
((signature (variable) @_type (fun)) . (function (variable) @function) (#eq? @function @_type))
((signature (variable) @function (context (fun))) . (function (variable)))
((signature (variable) @_type (context (fun))) . (function (variable) @function) (#eq? @function @_type))
((signature (variable) @function (forall (context (fun)))) . (function (variable)))
((signature (variable) @_type (forall (context (fun)))) . (function (variable) @function) (#eq? @function @_type))

(exp_infix (variable) @operator)  ; consider infix functions as operators
(exp_section_right (variable) @operator) ; partially applied infix functions (sections) also get highlighted as operators
(exp_section_left (variable) @operator)

(exp_infix (exp_name) @function.call (#set! "priority" 101))
(exp_apply . (exp_name (variable) @function.call))
(exp_apply . (exp_name (qualified_variable (variable) @function.call)))


;; ----------------------------------------------------------------------------
;; Types

(type) @type
(type_star) @type
(type_variable) @type

(constructor) @constructor

; True or False
((constructor) @boolean (#any-of? @boolean "True" "False"))


;; ----------------------------------------------------------------------------
;; Quasi-quotes

(quoter) @function.call
; Highlighting of quasiquote_body is handled by injections.scm

;; ----------------------------------------------------------------------------
;; Spell checking

(string) @spell
(comment) @spell
