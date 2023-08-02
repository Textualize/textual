(object_id) @variable

(string) @string
(escape_sequence) @string.escape

(comment) @comment

(constant) @constant.builtin

(boolean) @boolean

(using) @include

(template) @keyword

(decorator) @attribute

(property_definition (property_name) @property)

(object) @type

(signal_binding (signal_name) @function.builtin)
(signal_binding (function (identifier)) @function)
(signal_binding "swapped" @keyword)

(styles_list "styles" @function.macro)
(layout_definition "layout" @function.macro)

(gettext_string "_" @function.builtin)

(menu_definition "menu" @keyword)
(menu_section "section" @keyword)
(menu_item "item" @function.macro)

(template_definition (template_name_qualifier) @type.qualifier)

(import_statement (gobject_library) @namespace)

(import_statement (version_number) @float)

(float) @float
(number) @number

[
  ";"
  "."
  ","
] @punctuation.delimiter

[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket
