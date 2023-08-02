; adapted from https://github.com/interdependence/tree-sitter-htmldjango

[
  (unpaired_comment)
  (paired_comment)
] @comment @spell

[
  "{{" "}}"
  "{%" "%}"
  (end_paired_statement)
] @punctuation.bracket

[
 "end"
 (tag_name)
] @function

(variable_name) @variable

(filter_name) @method
(filter_argument) @parameter

(keyword) @keyword

(operator) @operator
(variable "|" @operator)
(paired_statement "=" @operator)
(keyword_operator) @keyword.operator

(number) @number

(boolean) @boolean

(string) @string
