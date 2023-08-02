; Includes

(include
  "~" @include
  _ @text.uri @string.special)

; Variables

(identifier) @variable

; Macros

(macro
  "%"
  (identifier) @function.macro)

((identifier) @function.macro
  (#lua-match? @function.macro "^[a-z]?[0-9]*[A-Z-_]+$"))

(rune
  . rune_start: (rune_char ",")
  . (identifier) @function.call)

(rune
  . rune_start: (rune_char ";")
  . (identifier) @function.call)

((identifier) @function.call
  (#lua-match? @function.call "^:"))

; Keywords

(opcode) @keyword

; Labels

(label
  "@" @symbol
  (identifier) @function)

(sublabel_reference
  (identifier) @namespace
  "/" @punctuation.delimiter
  (identifier) @label)

; Repeats

((identifier) @repeat
  (#eq? @repeat "while"))

; Literals

(raw_ascii) @string

(hex_literal
  "#" @symbol
  (hex_lit_value) @string.special)

(number) @number

; Punctuation

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[
  "%"
  "|"
  "$"
  ","
  "_"
  "."
  "-"
  ";"
  "="
  "!"
  "?"
  "&"
] @punctuation.special

; Comments

(comment) @comment @spell
