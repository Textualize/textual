; Literals

(string) @string
(escape_sequence) @string.escape

(hex_blob
  "x" @character.special
  (_) @string)

(esc_blob
  "b" @character.special
  (_) @string)

(datetime
  "d" @character.special
  (_) @string.special)

(_ key: (_) @label)

(number) @number

(float) @float

(boolean) @boolean

(null) @constant.builtin

; Punctuation

[
  ","
  ":"
] @punctuation.delimiter

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[ "<" ">" ] @punctuation.bracket

(("\"" @conceal)
 (#set! conceal ""))

; Comments

(comment) @comment @spell

; Errors

(ERROR) @error
