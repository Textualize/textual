; Tags

; TODO apply to every symbol in list? I think it should probably only be applied to the first child of the list
(list
  (symbol) @tag)

; Includes

(list .
  ((symbol) @include
    (#eq? @include "include")))

; Keywords

; I think there's a bug in tree-sitter the anchor doesn't seem to be working, see
; https://github.com/tree-sitter/tree-sitter/pull/2107
(list .
  ((symbol) @keyword
    (#any-of? @keyword "defwindow" "defwidget" "defvar" "defpoll" "deflisten" "geometry" "children" "struts")))

; Loop

(loop_widget . "for" @repeat . (symbol) @variable . "in" @keyword.operator)

(loop_widget . "for" @repeat . (symbol) @variable . "in" @keyword.operator . (symbol) @variable)

; Builtin widgets

(list .
  ((symbol) @tag.builtin
    (#any-of? @tag.builtin
      "box"
      "button"
      "calendar"
      "centerbox"
      "checkbox"
      "circular-progress"
      "color-button"
      "color-chooser"
      "combo-box-text"
      "eventbox"
      "expander"
      "graph"
      "image"
      "input"
      "label"
      "literal"
      "overlay"
      "progress"
      "revealer"
      "scale"
      "scroll"
      "transform")))

; Variables

(ident) @variable

(array
  (symbol) @variable)

; Properties & Fields

(keyword) @property

(json_access
  (_)
  "["
  (simplexpr
    (ident) @property))

(json_safe_access
  (_)
  "?."
  "["
  (simplexpr
    (ident) @property))

(json_dot_access
  (index) @property)

(json_safe_dot_access
  (index) @property)

(json_object
  (simplexpr
    (ident) @field))

; Functions

(function_call
  name: (ident) @function.call)

; Operators

[
  "+"
  "-"
  "*"
  "/"
  "%"
  "||"
  "&&"
  "=="
  "!="
  "=~"
  ">"
  "<"
  ">="
  "<="
  "!"
  "?."
  "?:"
] @operator

; Punctuation

[":" "." ","] @punctuation.delimiter
["{" "}" "[" "]" "(" ")"] @punctuation.bracket

; Ternary expression

(ternary_expression
  ["?" ":"] @conditional.ternary)

; Literals

(number) @number

(float) @float

(boolean) @boolean

; Strings

[ (string_fragment) "\"" "'" "`" ] @string

(string_interpolation
  "${" @punctuation.special
  "}" @punctuation.special)

(escape_sequence) @string.escape

; Comments

(comment) @comment @spell

; Errors

(ERROR) @error
