["Show" "Hide" "Minimal"] @namespace

(condition (name) @conditional)
(action (name) @keyword)
(continue) @label

(operator) @operator

(string) @string @spell

(file) @string

[
  (quality)
  (rarity)
  (influence)
  (colour)
  (shape)
] @constant.builtin

(sockets) @variable.builtin

(number) @number

(boolean) @boolean

[
  (disable)
  "Temp"
] @constant

(comment) @comment @spell

"\"" @punctuation.delimiter

("\"" @conceal
  (#not-has-parent? @conceal string file)
  (#set! conceal ""))
