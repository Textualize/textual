; Preprocs

[
  (calling_convention)
  (tag)
] @preproc

; Includes

[
  "import"
  "package"
] @include

; Keywords

[
  "foreign"
  "using"
  "struct"
  "enum"
  "union"
  "defer"
  "cast"
  "transmute"
  "auto_cast"
  "map"
  "bit_set"
  "matrix"
] @keyword

[
  "proc"
] @keyword.function

[
  "return"
  "or_return"
] @keyword.return

[
  "distinct"
  "dynamic"
] @storageclass

; Conditionals

[
  "if"
  "else"
  "when"
  "switch"
  "case"
  "where"
  "break"
  (fallthrough_statement)
] @conditional

((ternary_expression
  [
    "?"
    ":"
    "if"
    "else"
    "when"
  ] @conditional.ternary)
  (#set! "priority" 105))

; Repeats

[
  "for"
  "do"
  "continue"
] @repeat

; Variables

(identifier) @variable

; Namespaces

(package_declaration (identifier) @namespace)

(import_declaration alias: (identifier) @namespace)

(foreign_block (identifier) @namespace)

(using_statement (identifier) @namespace)

; Parameters

(parameter (identifier) @parameter ":" "="? (identifier)? @constant)

(default_parameter (identifier) @parameter ":=")

(named_type (identifier) @parameter)

(call_expression argument: (identifier) @parameter "=")

; Functions

(procedure_declaration (identifier) @type)

(procedure_declaration (identifier) @function (procedure (block)))

(procedure_declaration (identifier) @function (procedure (uninitialized)))

(overloaded_procedure_declaration (identifier) @function)

(call_expression function: (identifier) @function.call)

; Types

(type (identifier) @type)

((type (identifier) @type.builtin)
  (#any-of? @type.builtin
    "bool" "byte" "b8" "b16" "b32" "b64"
    "int" "i8" "i16" "i32" "i64" "i128"
    "uint" "u8" "u16" "u32" "u64" "u128" "uintptr"
    "i16le" "i32le" "i64le" "i128le" "u16le" "u32le" "u64le" "u128le"
    "i16be" "i32be" "i64be" "i128be" "u16be" "u32be" "u64be" "u128be"
    "float" "double" "f16" "f32" "f64" "f16le" "f32le" "f64le" "f16be" "f32be" "f64be"
    "complex32" "complex64" "complex128" "complex_float" "complex_double"
    "quaternion64" "quaternion128" "quaternion256"
    "rune" "string" "cstring" "rawptr" "typeid" "any"))

"..." @type.builtin

(struct_declaration (identifier) @type "::")

(enum_declaration (identifier) @type "::")

(union_declaration (identifier) @type "::")

(const_declaration (identifier) @type "::" [(array_type) (distinct_type) (bit_set_type) (pointer_type)])

(struct . (identifier) @type)

(field_type . (identifier) @namespace "." (identifier) @type)

(bit_set_type (identifier) @type ";")

(procedure_type (parameters (parameter (identifier) @type)))

(polymorphic_parameters (identifier) @type)

((identifier) @type
  (#lua-match? @type "^[A-Z][a-zA-Z0-9]*$")
  (#not-has-parent? @type parameter procedure_declaration))

; Fields

(member_expression "." (identifier) @field)

(struct_type "{" (identifier) @field)

(struct_field (identifier) @field "="?)

(field (identifier) @field)

; Constants

((identifier) @constant
  (#lua-match? @constant "^_*[A-Z][A-Z0-9_]*$")
  (#not-has-parent? @constant type parameter))

(member_expression . "." (identifier) @constant)

(enum_declaration "{" (identifier) @constant)

; Macros

((call_expression function: (identifier) @function.macro)
  (#lua-match? @function.macro "^_*[A-Z][A-Z0-9_]*$"))

; Attributes

(attribute (identifier) @attribute "="?)

; Labels

(label_statement (identifier) @label ":")

; Literals

(number) @number

(float) @float

(string) @string

(character) @character

(escape_sequence) @string.escape

(boolean) @boolean

[
  (uninitialized)
  (nil)
] @constant.builtin

((identifier) @variable.builtin
  (#any-of? @variable.builtin "context" "self"))

; Operators

[
  ":="
  "="
  "+"
  "-"
  "*"
  "/"
  "%"
  "%%"
  ">"
  ">="
  "<"
  "<="
  "=="
  "!="
  "~="
  "|"
  "~"
  "&"
  "&~"
  "<<"
  ">>"
  "||"
  "&&"
  "!"
  "^"
  ".."
  "+="
  "-="
  "*="
  "/="
  "%="
  "&="
  "|="
  "^="
  "<<="
  ">>="
  "||="
  "&&="
  "&~="
  "..="
  "..<"
  "?"
] @operator

[
  "or_else"
  "in"
  "not_in"
] @keyword.operator

; Punctuation

[ "{" "}" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[
  "::"
  "->"
  "."
  ","
  ":"
  (separator)
] @punctuation.delimiter


[
  "@"
  "$"
] @punctuation.special

; Comments

[
  (comment)
  (block_comment)
] @comment @spell

; Errors

(ERROR) @error
