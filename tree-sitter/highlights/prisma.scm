(variable) @variable

[
 "datasource"
 "enum"
 "generator"
 "model"
 "type"
 "view"
] @keyword

(comment) @comment @spell

(developer_comment) @comment.documentation @spell

[
  (attribute)
  (call_expression)
] @function

(arguments) @property
(column_type) @type
(enumeral) @constant
(column_declaration (identifier) @variable)
(string) @string

[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket

[
  "="
  "@"
] @operator
