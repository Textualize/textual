; highlights.scm

[
  "*"
  "/"
  "%"
  "+"
  "-"
  ">"
  ">="
  "<"
  "<="
  "="
  "=~"
  "!="
  "!~"
] @operator

[
  "{"
  "}"
  "["
  "]"
  "("
  ")"
] @punctuation.bracket

(float_literal) @float
(string_literal) @string

(metric_name) @type
(range_selection) @text.strong @type
(subquery_range_selection) @text.strong @type

(label_name) @field
(label_value) @text.underline @string.regex

(function_name) @function.call

(comment) @comment @spell
(ERROR) @error
