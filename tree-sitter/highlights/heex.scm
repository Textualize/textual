; HEEx delimiters
[
  "%>"
  "--%>"
  "-->"
  "/>"
  "<!"
  "<!--"
  "<"
  "<%!--"
  "<%"
  "<%#"
  "<%%="
  "<%="
  "</"
  "</:"
  "<:"
  ">"
  "{"
  "}"
] @tag.delimiter

; HEEx operators are highlighted as such
"=" @operator

; HEEx inherits the DOCTYPE tag from HTML
(doctype) @constant

; HEEx comments are highlighted as such
(comment) @comment

; HEEx text content is treated as markup
(text) @text

; Tree-sitter parser errors
(ERROR) @error

; HEEx tags and slots are highlighted as HTML
[
 (tag_name)
 (slot_name)
] @tag

; HEEx attributes are highlighted as HTML attributes
(attribute_name) @tag.attribute
[
  (attribute_value)
  (quoted_attribute_value)
] @string

; HEEx components are highlighted as modules and function calls
(component_name [
  (module) @type
  (function) @function
  "." @punctuation.delimiter
])
