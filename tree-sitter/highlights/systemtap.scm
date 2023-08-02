(identifier) @variable

(preprocessor_macro_definition
  name: (identifier) @function.macro)

(preprocessor_macro_expansion) @function.macro

(preprocessor_constant) @constant.macro

(number) @number
(string) @string
(escape_sequence) @string.escape

[
  (script_argument_string)
  (script_argument_number)
] @constant

(probe_point_component) @function

(function_definition
  name: (identifier) @function)

(parameter
  name: (identifier) @parameter)

(type) @type.builtin

(aggregation_operator) @attribute

(member_expression
  member: (identifier) @field)

(call_expression
  function: (identifier) @function.call)

((call_expression
    function: (identifier) @function.builtin)
  (#any-of? @function.builtin
    "print" "printd" "printdln" "printf" "println"
    "sprint" "sprintd" "sprintdln" "sprintf" "sprintln"))

((identifier) @variable.builtin
  (#lua-match? @variable.builtin "^\$+[0-9A-Z_a-z]+\$*$"))

(shebang_line) @preproc

(comment) @comment @spell

[
  "!"
  "!="
  "!~"
  "$"
  "$$"
  "%"
  "%="
  "&"
  "&&"
  "&="
  "*"
  "*="
  "+"
  "++"
  "+="
  "-"
  "--"
  "-="
  "->"
  "."
  ".="
  "/"
  "/="
  ":"
  "<"
  "<<"
  "<<<"
  "<<="
  "<="
  "="
  "=="
  "=~"
  ">"
  ">="
  ">>"
  ">>="
  "?"
  "^"
  "^="
  "|"
  "|="
  "||"
  "~"
] @operator

[
  ","
  (null_statement)
] @punctuation.delimiter

[
  "%{"
  "%}"
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket

[
  "delete"
  "limit"
  "next"
  "probe"
] @keyword

"function" @keyword.function
"in" @keyword.operator
"return" @keyword.return

[
  "if"
  "else"
] @conditional

[
  "break"
  "continue"
  "for"
  "foreach"
  "while"
] @repeat

[
  "try"
  "catch"
] @exception

[
  "%("
  "%)"
  "%:"
  "%?"
  (preprocessor_tokens)
  (embedded_code)
] @preproc

"@define" @define

"private" @type.qualifier
"global" @storageclass
