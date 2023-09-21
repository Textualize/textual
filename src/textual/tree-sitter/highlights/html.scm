(tag_name) @tag
(erroneous_end_tag_name) @html.end_tag_error
(comment) @comment
(attribute_name) @tag.attribute
(attribute
  (quoted_attribute_value) @string)
(text) @text @spell

((element (start_tag (tag_name) @_tag) (text) @text.title)
 (#eq? @_tag "title"))

((element (start_tag (tag_name) @_tag) (text) @text.title.1)
 (#eq? @_tag "h1"))

((element (start_tag (tag_name) @_tag) (text) @text.title.2)
 (#eq? @_tag "h2"))

((element (start_tag (tag_name) @_tag) (text) @text.title.3)
 (#eq? @_tag "h3"))

((element (start_tag (tag_name) @_tag) (text) @text.title.4)
 (#eq? @_tag "h4"))

((element (start_tag (tag_name) @_tag) (text) @text.title.5)
 (#eq? @_tag "h5"))

((element (start_tag (tag_name) @_tag) (text) @text.title.6)
 (#eq? @_tag "h6"))

((element (start_tag (tag_name) @_tag) (text) @text.strong)
 (#any-of? @_tag "strong" "b"))

((element (start_tag (tag_name) @_tag) (text) @text.emphasis)
 (#any-of? @_tag "em" "i"))

((element (start_tag (tag_name) @_tag) (text) @text.strike)
 (#any-of? @_tag "s" "del"))

((element (start_tag (tag_name) @_tag) (text) @text.underline)
 (#eq? @_tag "u"))

((element (start_tag (tag_name) @_tag) (text) @text.literal)
 (#any-of? @_tag "code" "kbd"))

((element (start_tag (tag_name) @_tag) (text) @text.uri)
 (#eq? @_tag "a"))

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
