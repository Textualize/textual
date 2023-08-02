; inherits: ecma

"pragma" @include

;;; Annotations

(ui_annotation
  "@" @operator
  type_name: [
    (identifier) @attribute
    (nested_identifier (identifier) @attribute)
  ])

;; type
(ui_property
  type: (type_identifier) @type)

;;; Properties

(ui_object_definition_binding
  name: [
    (identifier) @property
    (nested_identifier (identifier) @property)
  ])

(ui_binding
  name: [
    (identifier) @property
    (nested_identifier (identifier) @property)
  ])

;; locals query appears not working unless id: <ref> isn't a parameter.
(ui_binding
  name: (identifier) @property
  (#eq? @property "id")
  value: (expression_statement (identifier) @variable))

(ui_property
  name: (identifier) @property)

(ui_required
  name: (identifier) @property)

(ui_list_property_type
  ["<" ">"] @punctuation.bracket)

;;; Signals

(ui_signal
  name: (identifier) @function)

(ui_signal_parameter
  (identifier) @variable)

;;; ui_object_definition
(ui_object_definition
  type_name: (identifier) @type)
(ui_object_definition
  type_name: (nested_identifier) @type)

;;; namespace
(nested_identifier
  (nested_identifier
    (identifier) @namespace)
)

; Properties
;-----------

(property_identifier) @property

;;; function
(call_expression
  function: (member_expression
    object: (identifier) @variable
    property:(property_identifier) @function
  )
)
;;; js



; Literals
;---------

[
  (true)
  (false)
] @boolean

[
  (null)
  (undefined)
] @constant.builtin

(comment) @comment

[
  (string)
  (template_string)
] @string

(regex) @string.regex
(number) @number

; Tokens
;-------

[
  "abstract"

  "private"
  "protected"
  "public"

  "default"
  "readonly"
  "required"
] @type.qualifier

; from typescript

(type_identifier) @type
(predefined_type) @type.builtin

((identifier) @type
  (#lua-match? @type "^%u"))

(type_arguments
  "<" @punctuation.bracket
  ">" @punctuation.bracket)

; Variables

(required_parameter (identifier) @variable)
(optional_parameter (identifier) @variable)

; Keywords

[
  "on"
  "property"
  "signal"
  "declare"
  "enum"
  "export"
  "implements"
  "interface"
  "keyof"
  "namespace"
  "type"
  "override"
] @keyword
