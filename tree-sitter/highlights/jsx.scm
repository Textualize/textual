(jsx_element
  open_tag: (jsx_opening_element ["<" ">"] @tag.delimiter))
(jsx_element
  close_tag: (jsx_closing_element ["</" ">"] @tag.delimiter))
(jsx_self_closing_element ["<" "/>"] @tag.delimiter)
(jsx_attribute (property_identifier) @tag.attribute)

(jsx_opening_element
  name: (identifier) @tag)

(jsx_closing_element
  name: (identifier) @tag)

(jsx_self_closing_element
  name: (identifier) @tag)

(jsx_opening_element ((identifier) @constructor
 (#lua-match? @constructor "^[A-Z]")))

; Handle the dot operator effectively - <My.Component>
(jsx_opening_element ((member_expression (identifier) @tag (property_identifier) @constructor)))

(jsx_closing_element ((identifier) @constructor
 (#lua-match? @constructor "^[A-Z]")))

; Handle the dot operator effectively - </My.Component>
(jsx_closing_element ((member_expression (identifier) @tag (property_identifier) @constructor)))

(jsx_self_closing_element ((identifier) @constructor
 (#lua-match? @constructor "^[A-Z]")))

; Handle the dot operator effectively - <My.Component />
(jsx_self_closing_element ((member_expression (identifier) @tag (property_identifier) @constructor)))

(jsx_text) @none
