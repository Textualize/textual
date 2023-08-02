; Keywords
[
  "as"
  "let"
  "panic"
  "todo"
  "type"
  "use"
] @keyword

; Function Keywords
[
  "fn"
] @keyword.function

; Imports
[
  "import"
] @include

; Conditionals
[
  "case"
  "if"
] @conditional

; Exceptions
[
  "assert"
] @exception

; Punctuation
[
  "("
  ")"
  "<<"
  ">>"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket

[
  ","
  "."
  ":"
  "->"
] @punctuation.delimiter

[
  "#"
] @punctuation.special

; Operators
[
  "%"
  "&&"
  "*"
  "*."
  "+"
  "+."
  "-"
  "-."
  ".."
  "/"
  "/."
  "<"
  "<."
  "<="
  "<=."
  "="
  "=="
  ">"
  ">."
  ">="
  ">=."
  "|>"
  "||"
] @operator

; Identifiers
(identifier) @variable

; Comments
[
  (comment)
] @comment @spell

[
  (module_comment)
  (statement_comment)
] @comment.documentation @spell

; Unused Identifiers
[
  (discard)
  (hole)
] @comment

; Modules & Imports
(module) @namespace
(import alias: ((identifier) @namespace)?)
(remote_type_identifier module: (identifier) @namespace)
(unqualified_import name: (identifier) @function)

; Strings
(string) @string

; Bit Strings
(bit_string_segment) @string.special

; Numbers
(integer) @number

(float) @float

; Function Parameter Labels
(function_call arguments: (arguments (argument label: (label) @label)))
(function_parameter label: (label)? @label name: (identifier) @parameter)

; Records
(record arguments: (arguments (argument label: (label) @property)?))
(record_pattern_argument  label: (label) @property)
(record_update_argument label: (label) @property)
(field_access record: (identifier) @variable field: (label) @property)
(data_constructor_argument (label) @property)

; Types
[
  (type_identifier)
  (type_parameter)
  (type_var)
] @type

((type_identifier) @type.builtin
  (#any-of? @type.builtin "Int" "Float" "String" "List"))

; Type Qualifiers
[
  "const"
  "external"
  (opacity_modifier)
  (visibility_modifier)
] @type.qualifier

; Tuples
(tuple_access index: (integer) @operator)

; Functions
(function name: (identifier) @function)
(function_call function: (identifier) @function.call)
(function_call function: (field_access field: (label) @function.call))

; External Functions
(external_function name: (identifier) @function)
(external_function_body (string) @namespace . (string) @function)

; Constructors
(constructor_name) @type @constructor

([(type_identifier) (constructor_name)] @constant.builtin
  (#any-of? @constant.builtin "Ok" "Error"))

; Booleans
((constructor_name) @boolean (#any-of? @boolean "True" "False"))

; Pipe Operator
(binary_expression operator: "|>" right: (identifier) @function)

; Parser Errors
(ERROR) @error
