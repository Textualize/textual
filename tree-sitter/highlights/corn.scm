"let" @keyword
"in" @keyword

[
  "{"
  "}"
  "["
  "]"
] @punctuation.bracket

"." @punctuation.delimiter

(input) @constant
(comment) @comment

(string) @string
(integer) @number
(float) @float
(boolean) @boolean
(null) @keyword

(ERROR) @error
