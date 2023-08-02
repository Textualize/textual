; Variables

(identifier) @variable

; Types

(type) @type

(scoped_type_identifier
  (identifier) . (identifier) @type)

(struct_literal
  . (identifier) @type)

(builtin_type) @type.builtin

; Constants

((identifier) @constant
  (#lua-match? @constant "^[A-Z_]+$"))

; Includes

[
  "use"
] @include

(use_statement
  (scoped_type_identifier
    (identifier) @namespace))
(use_statement
  (identifier) @namespace  "{")
(use_statement
  . (identifier) @namespace .)

((scoped_type_identifier
  path: (_) @namespace)
  (#set! "priority" 105))

; Keywords

[
  "def"
  "enum"
  "export"
  "let"
  "struct"
  "type"
  "union"
] @keyword

[
  "fn"
] @keyword.function

[
  "defer"
  "yield"
  "return"
] @keyword.return

[
  "as"
  "is"
] @keyword.operator

; Typedefs

(type_declaration
  "type" (identifier) @type.definition . "=")

; Qualifiers

[
  "const"
  "static"
  "nullable"
] @type.qualifier

; Attributes

[
  "@fini"
  "@init"
  "@test"
  "@noreturn"
  "@packed"
  (declaration_attribute)
] @attribute

; Labels

((label) @label
  (#set! "priority" 105))

; Functions

(function_declaration
  "fn" . (identifier) @function)

(call_expression
  . (identifier) @function.call)

(call_expression
  . (scoped_type_identifier
    . (identifier) . "::" . (identifier) @method.call))

((call_expression
  . (identifier) @function.builtin)
  (#any-of? @function.builtin "align" "assert" "free" "len" "offset" "size"))

(size_expression
  "size" @function.builtin)

((function_declaration
  "fn" . (identifier) @constructor)
  (#eq? @constructor "init"))

((call_expression
  . (identifier) @constructor)
  (#eq? @constructor "init"))

; Parameters

(parameter
  (_) @parameter . ":")

; Fields

((member_expression
  "." (_) @field)
  (#set! "priority" 105))

(field
  . (identifier) @field)

(field_assignment
  . (identifier) @field)

; Repeats

[
  "for"
] @repeat

; Conditionals

[
  "if"
  "else"
  "break"
  "switch"
  "match"
  "case"
] @conditional

; Operators

[
  "+"
  "-"
  "*"
  "/"
  "%"
  "||"
  "&&"
  "^^"
  "|"
  "&"
  "^"
  "=="
  "!="
  ">"
  ">="
  "<="
  "<"
  "<<"
  ">>"
  "~"
  "!"
  "+="
  "-="
  "*="
  "/="
  "%="
  "<<="
  ">>="
  "|="
  "&="
  "^="
  "||="
  "&&="
  "^^="
  "="
  "?"
] @operator

; Punctuation

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[
  ".."
  "..."
  "_"
] @punctuation.special

(pointer_type "*" @punctuation.special)

(slice_type "*" @punctuation.special)

(error_type "!" @punctuation.special)

[
  ","
  "."
  ":"
  ";"
  "::"
  "=>"
] @punctuation.delimiter

; Literals

[
  (string)
  (raw_string)
] @string

(rune) @character

(escape_sequence) @string.escape

(number) @number

(float) @float

(boolean) @boolean

[
  (void)
  (null)
] @constant.builtin

; Comments

(comment) @comment @spell

; Errors

(ERROR) @error
