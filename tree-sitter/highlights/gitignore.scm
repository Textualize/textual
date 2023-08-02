(comment) @comment @spell

[
  (directory_separator)
  (directory_separator_escaped)
] @punctuation.delimiter

[
  (wildcard_char_single)
  (wildcard_chars)
  (wildcard_chars_allow_slash)
  (bracket_negation)
] @operator

(negation) @punctuation.special

[
  (pattern_char_escaped)
  (bracket_char_escaped)
] @string.escape

;; bracket expressions
[
  "["
  "]"
] @punctuation.bracket

(bracket_char) @constant
(bracket_range
  "-" @operator)
(bracket_char_class) @constant.builtin
