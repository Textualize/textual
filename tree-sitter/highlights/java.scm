; CREDITS @maxbrunsfeld (maxbrunsfeld@gmail.com)

; Variables

(identifier) @variable

; Methods

(method_declaration
  name: (identifier) @method)
(method_invocation
  name: (identifier) @method.call)

(super) @function.builtin

; Parameters

(formal_parameter
  name: (identifier) @parameter)

(catch_formal_parameter
  name: (identifier) @parameter)

(spread_parameter
 (variable_declarator
   name: (identifier) @parameter)) ; int... foo

;; Lambda parameter

(inferred_parameters (identifier) @parameter) ; (x,y) -> ...

(lambda_expression
    parameters: (identifier) @parameter) ; x -> ...

; Annotations

(annotation
  name: (identifier) @attribute)
(marker_annotation
  name: (identifier) @attribute)

; Operators

[
  "@"
  "+"
  ":"
  "++"
  "-"
  "--"
  "&"
  "&&"
  "|"
  "||"
  "!"
  "!="
  "=="
  "*"
  "/"
  "%"
  "<"
  "<="
  ">"
  ">="
  "="
  "-="
  "+="
  "*="
  "/="
  "%="
  "->"
  "^"
  "^="
  "&="
  "|="
  "~"
  ">>"
  ">>>"
  "<<"
  "::"
] @operator

; Types

(interface_declaration
  name: (identifier) @type)
(annotation_type_declaration
  name: (identifier) @type)
(class_declaration
  name: (identifier) @type)
(record_declaration
  name: (identifier) @type)
(enum_declaration
  name: (identifier) @type)
(constructor_declaration
  name: (identifier) @type)
(type_identifier) @type
((method_invocation
  object: (identifier) @type)
 (#lua-match? @type "^[A-Z]"))
((method_reference
  . (identifier) @type)
 (#lua-match? @type "^[A-Z]"))

((field_access
  object: (identifier) @type)
  (#lua-match? @type "^[A-Z]"))
((scoped_identifier
  scope: (identifier) @type)
  (#lua-match? @type "^[A-Z]"))

; Fields

(field_declaration
  declarator: (variable_declarator
    name: (identifier) @field))

(field_access
  field: (identifier) @field)

[
  (boolean_type)
  (integral_type)
  (floating_point_type)
  (void_type)
] @type.builtin

; Variables

((identifier) @constant
  (#lua-match? @constant "^[A-Z_][A-Z%d_]+$"))

(this) @variable.builtin

; Literals

(string_literal) @string

(escape_sequence) @string.escape

(character_literal) @character

[
  (hex_integer_literal)
  (decimal_integer_literal)
  (octal_integer_literal)
  (binary_integer_literal)
] @number

[
  (decimal_floating_point_literal)
  (hex_floating_point_literal)
] @float

[
  (true)
  (false)
] @boolean

(null_literal) @constant.builtin

; Keywords

[
  "assert"
  "class"
  "record"
  "default"
  "enum"
  "extends"
  "implements"
  "instanceof"
  "interface"
  "@interface"
  "permits"
  "to"
  "with"
] @keyword

(synchronized_statement
  "synchronized" @keyword)

[
  "abstract"
  "final"
  "native"
  "non-sealed"
  "open"
  "private"
  "protected"
  "public"
  "sealed"
  "static"
  "strictfp"
  "transitive"
] @type.qualifier

(modifiers
  "synchronized" @type.qualifier)

[
  "transient"
  "volatile"
] @storageclass

[
  "return"
  "yield"
] @keyword.return

[
  "new"
] @keyword.operator

; Conditionals

[
  "if"
  "else"
  "switch"
  "case"
] @conditional

(ternary_expression ["?" ":"] @conditional.ternary)

; Loops

[
  "for"
  "while"
  "do"
  "continue"
  "break"
] @repeat

; Includes

[
  "exports"
  "import"
  "module"
  "opens"
  "package"
  "provides"
  "requires"
  "uses"
] @include

; Punctuation

[
  ";"
  "."
  "..."
  ","
] @punctuation.delimiter

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

(type_arguments [ "<" ">" ] @punctuation.bracket)
(type_parameters [ "<" ">" ] @punctuation.bracket)

; Exceptions

[
  "throw"
  "throws"
  "finally"
  "try"
  "catch"
] @exception

; Labels

(labeled_statement
  (identifier) @label)

; Comments

[
  (line_comment)
  (block_comment)
] @comment @spell

((block_comment) @comment.documentation
  (#lua-match? @comment.documentation "^/[*][*][^*].*[*]/$"))

((line_comment) @comment.documentation
  (#lua-match? @comment.documentation "^///[^/]"))

((line_comment) @comment.documentation
  (#lua-match? @comment.documentation "^///$"))
