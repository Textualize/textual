[
  (true)
  (false)
] @boolean

(comment) @comment
(id) @variable
(import) @include
(null) @constant.builtin
(number) @number
(string) @string

(fieldname (id) @label)

[
  "["
  "]"
  "{"
  "}"
  "("
  ")"
] @punctuation.bracket

[
  "."
  ","
  ";"
  ":"
  "::"
  ":::"
] @punctuation.delimiter

(unaryop) @operator
[
  "+"
  "-"
  "*"
  "/"
  "%"
  "^"
  "=="
  "!="
  "<="
  ">="
  "<"
  ">"
  "="
  "&"
  "|"
  "<<"
  ">>"
  "&&"
  "||"
] @operator

"for" @repeat

"function" @keyword.function

"in" @keyword.operator

[
 (local)
 "assert"
] @keyword

[
  "else"
  "if"
  "then"
] @conditional

[
  (dollar)
  (self)
] @variable.builtin
((id) @variable.builtin
 (#eq? @variable.builtin "std"))

; Function declaration
(bind
  function: (id) @function
  params: (params
            (param
              identifier: (id) @parameter)))

; Function call
(expr
  (expr (id) @function.call)
  "("
  (args
    (named_argument
      (id) @parameter))?
  ")")

(ERROR) @error
