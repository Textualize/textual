; Variables

(variable_name) @variable

; Constants

((name) @constant
 (#lua-match? @constant "^_?[A-Z][A-Z%d_]*$"))
((name) @constant.builtin
 (#lua-match? @constant.builtin "^__[A-Z][A-Z%d_]+__$"))

(const_declaration (const_element (name) @constant))

; Types

[
 (primitive_type)
 (cast_type)
 ] @type.builtin
(named_type
  [(name) @type
   (qualified_name (name) @type)])
(class_declaration
  name: (name) @type)
(base_clause
  [(name) @type
   (qualified_name (name) @type)])
(enum_declaration
  name: (name) @type)
(interface_declaration
  name: (name) @type)
(namespace_use_clause
  [(name) @type
   (qualified_name (name) @type)])
(namespace_aliasing_clause (name) @type.definition)
(class_interface_clause
  [(name) @type
   (qualified_name (name) @type)])
(scoped_call_expression
  scope: [(name) @type
          (qualified_name (name) @type)])
(class_constant_access_expression
  . [(name) @type
     (qualified_name (name) @type)]
  (name) @constant)
(trait_declaration
  name: (name) @type)
(use_declaration
    (name) @type)
(binary_expression
  operator: "instanceof"
  right: [(name) @type
          (qualified_name (name) @type)])

; Functions, methods, constructors

(array_creation_expression "array" @function.builtin)
(list_literal "list" @function.builtin)

(method_declaration
  name: (name) @method)

(function_call_expression
  function: (qualified_name (name) @function.call))

(function_call_expression
  (name) @function.call)

(scoped_call_expression
  name: (name) @function.call)

(member_call_expression
  name: (name) @method.call)

(function_definition
  name: (name) @function)

(nullsafe_member_call_expression
    name: (name) @method)

(method_declaration
    name: (name) @constructor
    (#eq? @constructor "__construct"))
(object_creation_expression
  [(name) @constructor
   (qualified_name (name) @constructor)])

; Parameters
[
  (simple_parameter)
  (variadic_parameter)
] @parameter

(argument
    (name) @parameter)

; Member

(property_element
  (variable_name) @property)

(member_access_expression
  name: (variable_name (name)) @property)

(member_access_expression
  name: (name) @property)

; Variables

(relative_scope) @variable.builtin

((variable_name) @variable.builtin
 (#eq? @variable.builtin "$this"))

; Namespace
(namespace_definition
  name: (namespace_name (name) @namespace))
(namespace_name_as_prefix
  (namespace_name (name) @namespace))

; Attributes
(attribute_list) @attribute

; Conditions ( ? : )
(conditional_expression) @conditional

; Directives
(declare_directive ["strict_types" "ticks" "encoding"] @parameter)

; Basic tokens

[
 (string)
 (encapsed_string)
 (heredoc_body)
 (nowdoc_body)
 (shell_command_expression) ; backtick operator: `ls -la`
 ] @string @spell
(escape_sequence) @string.escape

(boolean) @boolean
(null) @constant.builtin
(integer) @number
(float) @float
(comment) @comment @spell

(named_label_statement) @label
; Keywords

[
 "and"
 "as"
 "instanceof"
 "or"
 "xor"
] @keyword.operator

[
 "fn"
 "function"
] @keyword.function

[
 "break"
 "class"
 "clone"
 "declare"
 "default"
 "echo"
 "enddeclare"
 "enum"
 "extends"
 "global"
 "goto"
 "implements"
 "insteadof"
 "interface"
 "namespace"
 "new"
 "trait"
 "unset"
 ] @keyword

[
 "abstract"
 "const"
 "final"
 "private"
 "protected"
 "public"
 "readonly"
 "static"
] @type.qualifier

[
  "return"
  "yield"
] @keyword.return

[
 "case"
 "else"
 "elseif"
 "endif"
 "endswitch"
 "if"
 "switch"
 "match"
  "??"
 ] @conditional

[
 "continue"
 "do"
 "endfor"
 "endforeach"
 "endwhile"
 "for"
 "foreach"
 "while"
 ] @repeat

[
 "catch"
 "finally"
 "throw"
 "try"
 ] @exception

[
 "include_once"
 "include"
 "require_once"
 "require"
 "use"
 ] @include

[
 ","
 ";"
 ":"
 "\\"
 ] @punctuation.delimiter

[
 (php_tag)
 "?>"
 "("
 ")"
 "["
 "]"
 "{"
 "}"
 "#["
 ] @punctuation.bracket

[
  "="

  "."
  "-"
  "*"
  "/"
  "+"
  "%"
  "**"

  "~"
  "|"
  "^"
  "&"
  "<<"
  ">>"

  "->"
  "?->"

  "=>"

  "<"
  "<="
  ">="
  ">"
  "<>"
  "=="
  "!="
  "==="
  "!=="

  "!"
  "&&"
  "||"

  ".="
  "-="
  "+="
  "*="
  "/="
  "%="
  "**="
  "&="
  "|="
  "^="
  "<<="
  ">>="
  "??="
  "--"
  "++"

  "@"
  "::"
] @operator

(ERROR) @error
