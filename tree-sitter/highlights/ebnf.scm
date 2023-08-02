;;;; Simple tokens ;;;;
(terminal) @string.grammar

(special_sequence) @string.special.grammar

(integer) @number

(comment) @comment

;;;; Identifiers ;;;;

; Allow different highlighting for specific casings
((identifier) @type
 (#lua-match? @type "^%u"))

((identifier) @symbol
 (#lua-match? @symbol "^%l"))

((identifier) @constant
 (#lua-match? @constant "^%u[%u%d_]+$"))

;;; Punctuation ;;;;
[
 ";"
 ","
] @punctuation.delimiter

[
 "|"
 "*"
 "-"
] @operator

"=" @keyword.operator

[
 "("
 ")"
 "["
 "]"
 "{"
 "}"
] @punctuation.bracket
