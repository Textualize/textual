; highlights.scm

; Literals
(integer) @number

(float) @float

(complex) @number

(string) @string
(string (escape_sequence) @string.escape)

(comment) @comment @spell

((program . (comment) @preproc)
  (#lua-match? @preproc "^#!/"))

(identifier) @variable

((dollar (identifier) @variable.builtin)
 (#eq? @variable.builtin "self"))

((dollar _ (identifier) @field))

; Parameters

(formal_parameters (identifier) @parameter)

(formal_parameters
 (default_parameter name: (identifier) @parameter))

(default_argument name: (identifier) @parameter)

; Namespace

(namespace_get namespace: (identifier) @namespace)
(namespace_get_internal namespace: (identifier) @namespace)

; Operators
[
 "="
 "<-"
 "<<-"
 "->"
] @operator

(unary operator: [
  "-"
  "+"
  "!"
  "~"
  "?"
] @operator)

(binary operator: [
  "-"
  "+"
  "*"
  "/"
  "^"
  "<"
  ">"
  "<="
  ">="
  "=="
  "!="
  "||"
  "|"
  "&&"
  "&"
  ":"
  "~"
] @operator)

[
  "|>"
  (special)
] @operator

(lambda_function "\\" @operator)

[
 "("
 ")"
 "["
 "]"
 "{"
 "}"
] @punctuation.bracket

(dollar _ "$" @operator)

(subset2
  "[[" @punctuation.bracket
  "]]" @punctuation.bracket)

[
 (dots)
 (break)
 (next)
] @keyword

[
  (nan)
  (na)
  (null)
  (inf)
] @constant.builtin

[
  "if"
  "else"
  "switch"
] @conditional

[
  "while"
  "repeat"
  "for"
  "in"
] @repeat

[
  (true)
  (false)
] @boolean

"function" @keyword.function

; Functions/Methods

(call function: (identifier) @function.call)

(call
  (namespace_get function: (identifier) @function.call))

(call
  (namespace_get_internal function: (identifier) @function.call))

(call
  function: ((dollar _ (identifier) @method.call)))

; Error
(ERROR) @error
