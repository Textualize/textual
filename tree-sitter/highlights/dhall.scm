;; Text

;; Imports

(missing_import) @include

(local_import) @string.special.path

(http_import) @string @text.uri

[
  (env_variable)
  (import_hash)
] @string.special

[ (import_as_location) (import_as_text) ] @type

;; Types

([
  (let_binding (label) @type)
  (union_type_entry (label) @type)
] (#lua-match? @type "^%u"))

((primitive_expression
  (identifier (label) @type)
  (selector (label) @type)) @variable
  (#vim-match? @variable "^[A-Z][^.]*$"))

;; Parameters

(lambda_expression label: (label) @parameter)

;; Variables

(label) @variable

(identifier [
  (label) @variable
  (de_bruijn_index) @operator
])

(let_binding label: (label) @variable)

; Fields

(record_literal_entry (label) @field)

(record_type_entry (label) @field)

(selector
  (selector_dot)
  (_) @field)

;; Keywords

(env_import) @keyword

[
  "let"
  "in"
  "assert"
] @keyword

[
  "using"
  "as"
  "with"
] @keyword.operator

;; Operators

[
  (type_operator)
  (assign_operator)
  (lambda_operator)
  (arrow_operator)
  (infix_operator)
  (completion_operator)
  (assert_operator)
  (forall_operator)
  (empty_record_literal)
] @operator

;; Builtins

(builtin_function) @function.builtin
(builtin [
  "Natural"
  "Natural/build"
  "Natural/fold"
  "Natural/isZero"
  "Natural/even"
  "Natural/odd"
  "Natural/subtract"
  "Natural/toInteger"
  "Natural/show"
  "Integer"
  "Integer/toDouble"
  "Integer/show"
  "Integer/negate"
  "Integer/clamp"
  "Double"
  "Double/show"
  "List"
  "List/build"
  "List/fold"
  "List/length"
  "List/head"
  "List/last"
  "List/indexed"
  "List/reverse"
  "Text"
  "Text/show"
  "Text/replace"
  "Optional"
  "Date"
  "Time"
  "TimeZone"
  "Type"
  "Kind"
  "Sort"
] @type.builtin)

;; Punctuation

[ "," "|" ] @punctuation.delimiter
(selector_dot) @punctuation.delimiter

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[ "<" ">" ] @punctuation.bracket

;; Conditionals

[
  "if"
  "then"
  "else"
] @conditional

;; Literals

(text_literal) @string
(interpolation "}" @string)
[
  (double_quote_escaped)
  (single_quote_escaped)
] @string.escape

[
  (integer_literal)
  (natural_literal)
] @number

(double_literal) @float

(boolean_literal) @boolean

(builtin "None") @constant.builtin

;; Comments

[
  (line_comment)
  (block_comment)
] @comment @spell
