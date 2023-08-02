; Includes

((command_name) @include
  (#eq? @include "import"))

; Keywords

[
  "arguments"
  "classdef"
  "end"
  "enumeration"
  "events"
  "global"
  "methods"
  "persistent"
  "properties"
] @keyword

; Conditionals

(if_statement [ "if" "end" ] @conditional)
(elseif_clause "elseif" @conditional)
(else_clause "else" @conditional)
(switch_statement [ "switch" "end" ] @conditional)
(case_clause "case" @conditional)
(otherwise_clause "otherwise" @conditional)
(break_statement) @conditional

; Repeats

(for_statement [ "for" "parfor" "end" ] @repeat)
(while_statement [ "while" "end" ] @repeat)
(continue_statement) @repeat

; Exceptions

(try_statement [ "try" "end" ] @exception)
(catch_clause "catch" @exception)

; Variables

(identifier) @variable

; Constants

(events (identifier) @constant)
(attribute (identifier) @constant)

"~" @constant.builtin

; Fields/Properties

(field_expression field: (identifier) @field)

(superclass "." (identifier) @property)

(property_name "." (identifier) @property)

(property name: (identifier) @property)

; Types

(class_definition name: (identifier) @type)

(attributes (identifier) @constant)

(enum . (identifier) @type)

((identifier) @type
  (#lua-match? @type "^_*[A-Z][a-zA-Z0-9_]+$"))

; Functions

(function_definition
  "function" @keyword.function
  name: (identifier) @function
  [ "end" "endfunction" ]? @keyword.function)

(function_signature name: (identifier) @function)

(function_call
  name: (identifier) @function.call)

(handle_operator (identifier) @function)

(validation_functions (identifier) @function)

(command (command_name) @function.call)
(command_argument) @parameter

(return_statement) @keyword.return

; Parameters

(function_arguments (identifier) @parameter)

; Punctuation

[ ";" "," "." ] @punctuation.delimiter

[ "(" ")" "[" "]" "{" "}" ] @punctuation.bracket

; Operators

[
  "+"
  ".+"
  "-"
  ".*"
  "*"
  ".*"
  "/"
  "./"
  "\\"
  ".\\"
  "^"
  ".^"
  "'"
  ".'"
  "|"
  "&"
  "?"
  "@"
  "<"
  "<="
  ">"
  ">="
  "=="
  "~="
  "="
  "&&"
  "||"
  ":"
] @operator

; Literals

(string) @string

(escape_sequence) @string.escape
(formatting_sequence) @string.special

(number) @number

(boolean) @boolean

; Comments

[ (comment) (line_continuation) ] @comment @spell

; Errors

(ERROR) @error
