(tag_name) @tag
(erroneous_end_tag_name) @html.end_tag_error
(comment) @comment
(attribute_name) @tag.attribute
(attribute
  (quoted_attribute_value) @string)
(text) @text @spell

((attribute
   (attribute_name) @_attr
   (quoted_attribute_value (attribute_value) @text.uri))
 (#any-of? @_attr "href" "src"))

[
 "<"
 ">"
 "</"
 "/>"
] @tag.delimiter

"=" @operator

(doctype) @constant

"<!" @tag.delimiter
