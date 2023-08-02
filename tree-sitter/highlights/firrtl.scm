; Namespaces

(circuit (identifier) @namespace)

(module (identifier) @namespace)

; Types

((identifier) @type
  (#lua-match? @type "^[A-Z][A-Za-z0-9_$]*$"))

; Keywords

[
  "circuit"
  "module"
  "extmodule"

  "flip"
  "parameter"
  "reset"
  "wire"

  "cmem"
  "smem"
  "mem"

  "reg"
  "with"
  "mport"
  "inst"
  "of"
  "node"
  "is"
  "invalid"
  "skip"

  "infer"
  "read"
  "write"
  "rdwr"

  "defname"
] @keyword

; Qualifiers

(qualifier) @type.qualifier

; Storageclasses

[
  "input"
  "output"
] @storageclass

; Conditionals

[
  "when"
  "else"
] @conditional

; Annotations

(info) @attribute

; Builtins

[
  "stop"
  "printf"
  "assert"
  "assume"
  "cover"
  "attach"
  "mux"
  "validif"
] @function.builtin

[
  "UInt"
  "SInt"
  "Analog"
  "Fixed"
  "Clock"
  "AsyncReset"
  "Reset"
] @type.builtin

; Fields

[
  "data-type"
  "depth"
  "read-latency"
  "write-latency"
  "read-under-write"
  "reader"
  "writer"
  "readwriter"
] @field.builtin

((field_id) @field
  (#set! "priority" 105))

(port (identifier) @field)

(wire (identifier) @field)

(cmem (identifier) @field)

(smem (identifier) @field)

(memory (identifier) @field)

(register (identifier) @field)

; Parameters

(primitive_operation (identifier) @parameter)

(mux (identifier) @parameter)
(printf (identifier) @parameter)
(reset (identifier) @parameter)
(stop (identifier) @parameter)

; Variables

(identifier) @variable

; Operators

(primop) @keyword.operator

[
  "+"
  "-"
  "="
  "=>"
  "<="
  "<-"
] @operator

; Literals

[
  (uint)
  (number)
] @number

(number_str) @string.special

(double) @float

(string) @string

(escape_sequence) @string.escape

[
  "old"
  "new"
  "undefined"
] @constant.builtin

; Punctuation

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[ "<" ">" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[
  ","
  "."
  ":"
] @punctuation.delimiter

; Comments

(comment) @comment @spell

["=>" "<=" "="] @operator

; Error
(ERROR) @error
