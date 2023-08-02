; Types

(node (identifier) @type)

(type) @type

(annotation_type) @type.builtin

; Properties

(prop (identifier) @property)

; Variables

(identifier) @variable

; Operators
[
 "="
 "+"
 "-"
] @operator

; Literals

(string) @string

(escape) @string.escape

(number) @number

(number (decimal) @float)
(number (exponent) @float)

(boolean) @boolean

"null" @constant.builtin

; Punctuation

["{" "}"] @punctuation.bracket

["(" ")"] @punctuation.bracket

[
  ";"
] @punctuation.delimiter

; Comments

[
  (single_line_comment)
  (multi_line_comment)
] @comment @spell

(node (node_comment) (#set! "priority" 105)) @comment
(node (node_field (node_field_comment) (#set! "priority" 105)) @comment)
(node_children (node_children_comment) (#set! "priority" 105)) @comment
