; highlights.scm

; highlight comments and symbols
(comment) @comment @spell
((comment) @comment.documentation
  (#lua-match? @comment.documentation "^/[*][*][^*].*[*]/$"))
(symbol) @symbol
(member_access_expression (_) (identifier) @symbol)

; highlight constants
(
  (member_access_expression (identifier) @constant)
  (#lua-match? @constant "^[%u][%u%d_]*$")
)

(
  (member_access_expression (member_access_expression) @include (identifier) @constant)
  (#lua-match? @constant "^[%u][%u%d_]*$")
)

; highlight types and probable types
(type (symbol (_)? @namespace (identifier) @type))
(
  (member_access_expression . (identifier) @type)
  (#match? @type "^[A-Z][A-Za-z_0-9]{2,}$")
)

; highlight creation methods in object creation expressions
(
  (object_creation_expression (type (symbol (symbol (symbol)? @include (identifier) @type) (identifier) @constructor)))
  (#lua-match? @constructor "^[%l][%l%d_]*$")
)

(unqualified_type (symbol . (identifier) @type))
(unqualified_type (symbol (symbol) @namespace (identifier) @type))

(attribute) @attribute
(namespace_declaration (symbol) @namespace)
(method_declaration (symbol (symbol) @type (identifier) @function))
(method_declaration (symbol (identifier) @function))
(local_declaration (assignment (identifier) @variable))
(local_function_declaration (identifier) @function)
(destructor_declaration (identifier) @function)
(creation_method_declaration (symbol (symbol) @type (identifier) @constructor))
(creation_method_declaration (symbol (identifier) @constructor))
(constructor_declaration (_)? "construct" @keyword.function)
(enum_declaration (symbol) @type)
(enum_value (identifier) @constant)
(errordomain_declaration (symbol) @type)
(errorcode (identifier) @constant)
(constant_declaration (identifier) @constant)
(method_call_expression (member_access_expression (identifier) @function))
; highlight macros
(
 (method_call_expression (member_access_expression (identifier) @function.macro))
 (#match? @function.macro "^assert[A-Za-z_0-9]*|error|info|debug|print|warning|warning_once$")
)
(lambda_expression (identifier) @parameter)
(parameter (identifier) @parameter)
(property_declaration (symbol (identifier) @property))
(field_declaration (identifier) @field)
[
 (this_access)
 (base_access)
 (value_access)
] @constant.builtin
(boolean) @boolean
(character) @character
(escape_sequence) @string.escape
(integer) @number
(null) @constant.builtin
(real) @float
(regex) @string.regex
(string) @string
(string_formatter) @string.special
(template_string) @string
(template_string_expression) @string.special
(verbatim_string) @string
[
 "var"
 "void"
] @type.builtin

(if_directive
  expression: (_) @preproc
) @keyword
(elif_directive
  expression: (_) @preproc
) @keyword
(else_directive) @keyword
(endif_directive) @keyword

[
 "abstract"
 "class"
 "construct"
 "continue"
 "default"
 "delegate"
 "enum"
 "errordomain"
 "get"
 "inline"
 "interface"
 "namespace"
 "new"
 "out"
 "override"
 "partial"
 "ref"
 "set"
 "signal"
 "struct"
 "virtual"
 "with"
] @keyword

[
  "async"
  "yield"
] @keyword.coroutine

[
 "const"
 "dynamic"
 "owned"
 "weak"
 "unowned"
] @type.qualifier

[
 "case"
 "else"
 "if"
 "switch"
] @conditional

; specially highlight break statements in switch sections
(switch_section (break_statement "break" @conditional))

[
 "extern"
 "internal"
 "private"
 "protected"
 "public"
 "static"
] @storageclass

[
 "and"
 "as"
 "delete"
 "in"
 "is"
 "lock"
 "not"
 "or"
 "sizeof"
 "typeof"
] @keyword.operator

"using" @include
(using_directive (symbol) @namespace)

(symbol "global::" @namespace)

(array_creation_expression "new" @keyword.operator)
(object_creation_expression "new" @keyword.operator)
(argument "out" @keyword.operator)
(argument "ref" @keyword.operator)

[
  "break"
  "continue"
  "do"
  "for"
  "foreach"
  "while"
] @repeat

[
  "catch"
  "finally"
  "throw"
  "throws"
  "try"
] @exception

[
  "return"
] @keyword.return

[
 "="
 "=="
 "+"
 "+="
 "-"
 "-="
 "++"
 "--"
 "|"
 "|="
 "&"
 "&="
 "^"
 "^="
 "/"
 "/="
 "*"
 "*="
 "%"
 "%="
 "<<"
 "<<="
 ">>"
 ">>="
 "."
 "?."
 "->"
 "!"
 "!="
 "~"
 "??"
 "?"
 ":"
 "<"
 "<="
 ">"
 ">="
 "||"
 "&&"
 "=>"
] @operator

[
 ","
 ";"
] @punctuation.delimiter

[
 "$("
 "("
 ")"
 "{"
 "}"
 "["
 "]"
] @punctuation.bracket
