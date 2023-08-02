(comment) @comment

(null) @constant.builtin
[ (true) (false) ] @boolean
(number) @number
(unit) @keyword
(string) @string
(multiline_string) @string
(string (escape_sequence) @string.escape)
(unquoted_string) @string

[ "url"
  "file"
  "classpath"
  "required"
] @keyword

(include "include" @include)

(substitution ["${" "${?" "}"] @punctuation.special)
(substitution (_) @field)

(path (_) @field)
(value [":" "=" "+=" ] @operator)

[
 "("
 ")"
 "["
 "]"
 "{"
 "}"
]  @punctuation.bracket

[ "," ] @punctuation.delimiter
(unquoted_path "." @punctuation.delimiter)
