(line_comment) @comment @spell

[
  (container_doc_comment)
  (doc_comment)
] @comment.documentation @spell

[
  variable: (IDENTIFIER)
  variable_type_function: (IDENTIFIER)
] @variable

parameter: (IDENTIFIER) @parameter

[
  field_member: (IDENTIFIER)
  field_access: (IDENTIFIER)
] @field

;; assume TitleCase is a type
(
  [
    variable_type_function: (IDENTIFIER)
    field_access: (IDENTIFIER)
    parameter: (IDENTIFIER)
  ] @type
  (#lua-match? @type "^%u([%l]+[%u%l%d]*)*$")
)
;; assume camelCase is a function
(
  [
    variable_type_function: (IDENTIFIER)
    field_access: (IDENTIFIER)
    parameter: (IDENTIFIER)
  ] @function
  (#lua-match? @function "^%l+([%u][%l%d]*)+$")
)

;; assume all CAPS_1 is a constant
(
  [
    variable_type_function: (IDENTIFIER)
    field_access: (IDENTIFIER)
  ] @constant
  (#lua-match? @constant "^%u[%u%d_]+$")
)

function: (IDENTIFIER) @function
function_call: (IDENTIFIER) @function.call

exception: "!" @exception

(
  (IDENTIFIER) @variable.builtin
  (#eq? @variable.builtin "_")
)

(PtrTypeStart "c" @variable.builtin)

(
  (ContainerDeclType
    [
      (ErrorUnionExpr)
      "enum"
    ]
  )
  (ContainerField (IDENTIFIER) @constant)
)

field_constant: (IDENTIFIER) @constant

(BUILTINIDENTIFIER) @function.builtin

((BUILTINIDENTIFIER) @include
  (#any-of? @include "@import" "@cImport"))

(INTEGER) @number

(FLOAT) @float

[
  "true"
  "false"
] @boolean

[
  (LINESTRING)
  (STRINGLITERALSINGLE)
] @string @spell

(CHAR_LITERAL) @character
(EscapeSequence) @string.escape
(FormatSequence) @string.special

(BreakLabel (IDENTIFIER) @label)
(BlockLabel (IDENTIFIER) @label)

[
  "asm"
  "defer"
  "errdefer"
  "test"
  "struct"
  "union"
  "enum"
  "opaque"
  "error"
] @keyword

[
  "async"
  "await"
  "suspend"
  "nosuspend"
  "resume"
] @keyword.coroutine

[
  "fn"
] @keyword.function

[
  "and"
  "or"
  "orelse"
] @keyword.operator

[
  "return"
] @keyword.return

[
  "if"
  "else"
  "switch"
] @conditional

[
  "for"
  "while"
  "break"
  "continue"
] @repeat

[
  "usingnamespace"
] @include

[
  "try"
  "catch"
] @exception

[
  "anytype"
  (BuildinTypeExpr)
] @type.builtin

[
  "const"
  "var"
  "volatile"
  "allowzero"
  "noalias"
] @type.qualifier

[
  "addrspace"
  "align"
  "callconv"
  "linksection"
] @storageclass

[
  "comptime"
  "export"
  "extern"
  "inline"
  "noinline"
  "packed"
  "pub"
  "threadlocal"
] @attribute

[
  "null"
  "unreachable"
  "undefined"
] @constant.builtin

[
  (CompareOp)
  (BitwiseOp)
  (BitShiftOp)
  (AdditionOp)
  (AssignOp)
  (MultiplyOp)
  (PrefixOp)
  "*"
  "**"
  "->"
  ".?"
  ".*"
  "?"
] @operator

[
  ";"
  "."
  ","
  ":"
] @punctuation.delimiter

[
  ".."
  "..."
] @punctuation.special

[
  "["
  "]"
  "("
  ")"
  "{"
  "}"
  (Payload "|")
  (PtrPayload "|")
  (PtrIndexPayload "|")
] @punctuation.bracket

; Error
(ERROR) @error
