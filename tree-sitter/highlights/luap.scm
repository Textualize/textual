"." @character

[
  (anchor_begin)
  (anchor_end)
] @string.escape

[
  "[" "]"
  "(" ")"
] @punctuation.bracket

[
  (zero_or_more)
  (shortest_zero_or_more)
  (one_or_more)
  (zero_or_one)
] @operator

(range
  from: (character) @constant
  "-" @punctuation.delimiter
  to: (character) @constant)

(set
  (character) @constant)

(class) @keyword

(negated_set
  "^" @operator
  (character) @constant)

(balanced_match
  (character) @parameter)
