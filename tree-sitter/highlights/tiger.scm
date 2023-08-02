; Built-ins {{{
((function_call
  function: (identifier) @function.builtin)
  (#any-of? @function.builtin "chr" "concat" "exit" "flush" "getchar" "not" "ord" "print" "print_err" "print_int" "size" "strcmp" "streq" "substring")
  ; FIXME: not supported by neovim
  ; (#is-not? local)
  )

((type_identifier) @type.builtin
  (#any-of? @type.builtin "int" "string" "Object")
  ; FIXME: not supported by neovim
  ; (#is-not? local)
  )

((identifier) @variable.builtin
  (#eq? @variable.builtin "self")
  ; FIXME: not supported by neovim
  ; (#is-not? local)
  )
; }}}

; Keywords {{{
[
 "function"
 "primitive"
 "method"
] @keyword.function

[
  "do"
  "for"
  "to"
  "while"
] @repeat

"new" @keyword.operator

"import" @include

[
  "array"
  (break_expression)
  "else"
  "end"
  "if"
  "in"
  "let"
  "of"
  "then"
  "type"
  "var"

  "class"
  "extends"

  "_cast"
  "_chunks"
  "_exp"
  "_lvalue"
  "_namety"
] @keyword
; }}}

; Operators {{{
(operator) @operator

[
 ","
 ";"
 ":"
 "."
] @punctuation.delimiter

[
 "("
 ")"
 "["
 "]"
 "{"
 "}"
] @punctuation.bracket
; }}}

; Functions and methods {{{
(function_call
  function: (identifier) @function)
(function_declaration
  name: (identifier) @function)
(primitive_declaration
  name: (identifier) @function)

(method_call
  method: (identifier) @method)
(method_declaration
  name: (identifier) @method)

(parameters
  name: (identifier) @parameter)
; }}}

; Declarations {{{
(import_declaration
  file: (string_literal) @string.special)
; }}}

; Literals {{{
(nil_literal) @constant.builtin
(integer_literal) @number
(string_literal) @string
(escape_sequence) @string.escape
; }}}

; Misc {{{
(comment) @comment

(type_identifier) @type
(field_identifier) @property
(identifier) @variable
; }}}

; vim: sw=2 foldmethod=marker
