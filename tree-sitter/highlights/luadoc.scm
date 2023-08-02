; Keywords

[
  "@module"
  "@package"
] @include

[
  "@class"
  "@type"
  "@param"
  "@alias"
  "@field"
  "@generic"
  "@vararg"
  "@diagnostic"
  "@deprecated"
  "@meta"
  "@source"
  "@version"
  "@operator"
  "@nodiscard"
  "@cast"
  "@overload"
  "@enum"
  "@language"
  "@see"
  "extends"
  (diagnostic_identifier)
] @keyword

[
  "@async"
] @keyword.coroutine

(language_injection "@language" (identifier) @keyword)

(function_type ["fun" "function"] @keyword.function)

(source_annotation
  filename: (identifier) @text.uri @string.special
  extension: (identifier) @text.uri @string.special)

(version_annotation
  version: _ @constant.builtin)

[
  "@return"
] @keyword.return

; Qualifiers

[
  "public"
  "protected"
  "private"
  "@public"
  "@protected"
  "@private"
] @type.qualifier


; Variables

(identifier) @variable

[
  "..."
  "self"
] @variable.builtin

; Macros

(alias_annotation (identifier) @function.macro)

; Parameters

(param_annotation (identifier) @parameter)

(parameter (identifier) @parameter)

; Fields

(field_annotation (identifier) @field)

(table_literal_type field: (identifier) @field)

(member_type ["#" "."] . (identifier) @field)

; Types

(table_type "table" @type.builtin)

(builtin_type) @type.builtin

(class_annotation (identifier) @type)

(enum_annotation (identifier) @type)

((array_type ["[" "]"] @type)
  (#set! "priority" 105))

(type) @type

; Operators

[
  "|"
] @operator

; Literals

(string) @namespace ; only used in @module

(literal_type) @string

(number) @number

; Punctuation

[ "[" "]" ] @punctuation.bracket

[ "{" "}" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[ "<" ">" ] @punctuation.bracket

[
  ","
  "."
  "#"
  ":"
] @punctuation.delimiter

[
  "@"
  "?"
] @punctuation.special

; Comments

(comment) @comment @spell

(at_comment
  (identifier) @type
  (_) @comment @spell)

(class_at_comment
  (identifier) @type
  ("extends"? (identifier)? @type)
  (_) @comment @spell)
