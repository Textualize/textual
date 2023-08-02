[
 "@media"
 "@charset"
 "@namespace"
 "@supports"
 "@keyframes"
 (at_keyword)
 (to)
 (from)
 ] @keyword

"@import" @include

(comment) @comment @spell

[
 (tag_name)
 (nesting_selector)
 (universal_selector)
 ] @type

(function_name) @function

[
 "~"
 ">"
 "+"
 "-"
 "*"
 "/"
 "="
 "^="
 "|="
 "~="
 "$="
 "*="
 "and"
 "or"
 "not"
 "only"
 ] @operator

(important) @type.qualifier

(attribute_selector (plain_value) @string)
(pseudo_element_selector "::" (tag_name) @property)
(pseudo_class_selector (class_name) @property)

[
 (class_name)
 (id_name)
 (property_name)
 (feature_name)
 (attribute_name)
 ] @property

(namespace_name) @namespace

((property_name) @type.definition
  (#lua-match? @type.definition "^[-][-]"))
((plain_value) @type
  (#lua-match? @type "^[-][-]"))

[
 (string_value)
 (color_value)
 (unit)
 ] @string

[
 (integer_value)
 (float_value)
 ] @number

[
 "#"
 ","
 "."
 ":"
 "::"
 ";"
 ] @punctuation.delimiter

[
 "{"
 ")"
 "("
 "}"
 ] @punctuation.bracket

(ERROR) @error
