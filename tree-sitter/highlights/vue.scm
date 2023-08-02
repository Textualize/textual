; inherits: html_tags

[
  (directive_dynamic_argument)
  (directive_dynamic_argument_value)
] @tag

(interpolation) @punctuation.special
(interpolation
  (raw_text) @none)

(directive_name) @tag.attribute

(directive_attribute
  (quoted_attribute_value) @punctuation.special)

(directive_attribute
  (quoted_attribute_value (attribute_value) @none))

[
  (directive_modifier)
  (directive_argument)
] @method
