; Preproc

[
  (unique_id)
  (top_level_annotation_body)
] @preproc

; Includes

[
  "import"
  "$import"
  "embed"
  "using"
] @include

(import_path) @string @text.uri

; Keywords

[
  "annotation"
  "enum"
  "group"
  "interface"
  "struct"
  "union"
  "extends"
  "namespace"
] @keyword

; Builtins

[
  "const"
] @type.qualifier

[
  (primitive_type)
  "List"
] @type.builtin

; Typedefs

(type_definition) @type.definition

; Labels (@number, @number!)

(field_version) @label

; Methods

[
  (annotation_definition_identifier)
  (method_identifier)
] @method

; Fields

(field_identifier) @field

; Properties

(property) @property

; Parameters

[
  (param_identifier)
  (return_identifier)
] @parameter

(annotation_target) @parameter.builtin

; Constants

[
  (const_identifier)
  (local_const)
  (enum_member)
] @constant

(void) @constant.builtin

; Types

[
  (enum_identifier)
  (extend_type)
  (type_identifier)
] @type

; Attributes

[
  (annotation_identifier)
  (attribute)
] @attribute

; Operators

"=" @operator

; Literals

[
  (string)
  (concatenated_string)
  (block_text)
  (namespace)
] @string

(namespace) @text.underline

(escape_sequence) @string.escape

(data_string) @string.special

(number) @number

(float) @float

(boolean) @boolean

(data_hex) @symbol

; Punctuation

[
  "*"
  "$"
  ":"
] @punctuation.special

["{" "}"] @punctuation.bracket

["(" ")"] @punctuation.bracket

["[" "]"] @punctuation.bracket

[
  "."
  ","
  ";"
  "->"
] @punctuation.delimiter

; Comments

(comment) @comment @spell

; Errors

(ERROR) @error
