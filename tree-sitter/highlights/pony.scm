; Includes

[
  "use"
] @include

; Keywords

[
  "type"
  "actor"
  "class"
  "primitive"
  "interface"
  "trait"
  "struct"
  "embed"
  "let"
  "var"
  (compile_intrinsic)
  "as"
  "consume"
  "recover"
  "object"
  "where"
] @keyword

[
  "fun"
] @keyword.function

[
  "be"
] @keyword.coroutine

[
  "in"
  "is"
] @keyword.operator

[
  "return"
] @keyword.return

; Qualifiers

[
  "iso"
  "trn"
  "ref"
  "val"
  "box"
  "tag"
  "#read"
  "#send"
  "#share"
  "#alias"
  "#any"
] @type.qualifier

; Conditionals

[
  "if"
  "ifdef"
  "iftype"
  "then"
  "else"
  "elseif"
  "match"
] @conditional

(if_statement "end" @conditional)

(iftype_statement "end" @conditional)

(match_statement "end" @conditional)

; Repeats

[
  "repeat"
  "until"
  "while"
  "for"
  "continue"
  "do"
  "break"
] @repeat

(do_block "end" @repeat)

(repeat_statement "end" @repeat)

; Exceptions

[
  "try"
  (error)
  "compile_error"
] @exception

(try_statement "end" @exception)

(recover_statement "end" @exception)

; Attributes

(annotation) @attribute

; Variables

(identifier) @variable

(this) @variable.builtin

; Fields

(field name: (identifier) @field)

(member_expression "." (identifier) @field)

; Constructors

(constructor "new" @keyword.operator (identifier) @constructor)

; Methods

(method (identifier) @method)

(behavior (identifier) @method)

(ffi_method (identifier) @method)

((ffi_method (string) @string.special)
  (#set! "priority" 105))

(call_expression
  callee:
    [
      (identifier) @method.call
      (ffi_identifier (identifier) @method.call)
      (member_expression "." (identifier) @method.call)
    ])

; Parameters

(parameter name: (identifier) @parameter)
(lambda_parameter name: (identifier) @parameter)

; Types

(type_alias (identifier) @type.definition)

(base_type name: (identifier) @type)

(generic_parameter (identifier) @type)

(lambda_type (identifier)? @method)

((identifier) @type
  (#lua-match? @type "^_*[A-Z][a-zA-Z0-9_]*$"))

; Operators

(unary_expression
  operator: ["not" "addressof" "digestof"] @keyword.operator)

(binary_expression
  operator: ["and" "or" "xor" "is" "isnt"] @keyword.operator)

[
  "="
  "?"
  "|"
  "&"
  "-~"
  "+"
  "-"
  "*"
  "/"
  "%"
  "%%"
  "<<"
  ">>"
  "=="
  "!="
  ">"
  ">="
  "<="
  "<"
  "+~"
  "-~"
  "*~"
  "/~"
  "%~"
  "%%~"
  "<<~"
  ">>~"
  "==~"
  "!=~"
  ">~"
  ">=~"
  "<=~"
  "<~"
  "+?"
  "-?"
  "*?"
  "/?"
  "%?"
  "%%?"
  "<:"
] @operator

; Literals

(string) @string

(source_file (string) @string.documentation)
(actor_definition (string) @string.documentation)
(class_definition (string) @string.documentation)
(primitive_definition (string) @string.documentation)
(interface_definition (string) @string.documentation)
(trait_definition (string) @string.documentation)
(struct_definition (string) @string.documentation)
(type_alias (string) @string.documentation)
(field (string) @string.documentation)

(constructor
  [
   (string) @string.documentation
   (block . (string) @string.documentation)
  ])

(method
  [
   (string) @string.documentation
   (block . (string) @string.documentation)
  ])

(behavior
  [
   (string) @string.documentation
   (block . (string) @string.documentation)
  ])

(character) @character

(escape_sequence) @string.escape

(number) @number

(float) @float

(boolean) @boolean

; Punctuation

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[
  "."
  ","
  ";"
  ":"
  "~"
  ".>"
  "->"
  "=>"
] @punctuation.delimiter

[
  "@"
  "!"
  "^"
  "..."
] @punctuation.special

; Comments

[
  (line_comment)
  (block_comment)
] @comment @spell

; Errors

(ERROR) @error
