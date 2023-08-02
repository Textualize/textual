; Preproc

[
  "%builtins"
  "%lang"
] @preproc

; Includes

(import_statement [ "from" "import" ] @include module_name: (dotted_name (identifier) @namespace . ))

[
  "as"
  "use"
  "mod"
] @include

; Variables

(identifier) @variable

; Namespaces

(namespace_definition (identifier) @namespace)

(mod_item
  name: (identifier) @namespace)

(use_list (self) @namespace)

(scoped_use_list (self) @namespace)

(scoped_identifier
  path: (identifier) @namespace)

(scoped_identifier
 (scoped_identifier
  name: (identifier) @namespace))

(scoped_type_identifier
  path: (identifier) @namespace)

((scoped_identifier
  path: (identifier) @type)
 (#lua-match? @type "^[A-Z]"))

((scoped_identifier
    name: (identifier) @type)
 (#lua-match? @type "^[A-Z]"))

((scoped_identifier
    name: (identifier) @constant)
 (#lua-match? @constant "^[A-Z][A-Z%d_]*$"))

((scoped_identifier
  path: (identifier) @type
  name: (identifier) @constant)
  (#lua-match? @type "^[A-Z]")
  (#lua-match? @constant "^[A-Z]"))

((scoped_type_identifier
  path: (identifier) @type
  name: (type_identifier) @constant)
  (#lua-match? @type "^[A-Z]")
  (#lua-match? @constant "^[A-Z]"))

(scoped_use_list
  path: (identifier) @namespace)

(scoped_use_list
  path: (scoped_identifier
          (identifier) @namespace))

(use_list (scoped_identifier (identifier) @namespace . (_)))

(use_list (identifier) @type (#lua-match? @type "^[A-Z]"))

(use_as_clause alias: (identifier) @type (#lua-match? @type "^[A-Z]"))

; Keywords

[
  ; 0.x
  "using"
  "namespace"
  "struct"
  "let"
  "const"
  "local"
  "rel"
  "abs"
  "dw"
  "alloc_locals"
  (inst_ret)
  "with_attr"
  "with"
  "call"
  "nondet"

  ; 1.0
  "type"
  "impl"
  "implicits"
  "of"
  "ref"
  "mut"
  "trait"
  "enum"
] @keyword

[
  "func"
  "fn"
  "end"
] @keyword.function

"return" @keyword.return

[
  "cast"
  "new"
  "and"
] @keyword.operator

[
  "tempvar"
  "extern"
] @storageclass

[
  "if"
  "else"
  "match"
] @conditional

[
  "loop"
] @repeat

[
  "assert"
  "static_assert"
  "nopanic"
] @exception

; Fields

(implicit_arguments (typed_identifier (identifier) @field))

(member_expression "." (identifier) @field)

(call_expression (assignment_expression left: (identifier) @field))

(tuple_expression (assignment_expression left: (identifier) @field))

(field_identifier) @field

(shorthand_field_initializer (identifier) @field)

; Parameters

(arguments (typed_identifier (identifier) @parameter))

(call_expression (tuple_expression (assignment_expression left: (identifier) @parameter)))

(return_type (tuple_type (named_type . (identifier) @parameter)))

(parameter (identifier) @parameter)

; Builtins

(builtin_directive (identifier) @variable.builtin)
(lang_directive (identifier) @variable.builtin)

[
  "ap"
  "fp"
  (self)
] @variable.builtin

; Functions

(function_definition "func" (identifier) @function)
(function_definition "fn" (identifier) @function)
(function_signature "fn" (identifier) @function)
(extern_function_statement (identifier) @function)

(call_expression
  function: (identifier) @function.call)

(call_expression
  function: (scoped_identifier
              (identifier) @function.call .))

(call_expression
  function: (field_expression
    field: (field_identifier) @function.call))

[
  "jmp"
] @function.builtin

; Types

(struct_definition . (identifier) @type (typed_identifier (identifier) @field)?)

(named_type (identifier) @type .)

[
  (builtin_type)
  (primitive_type)
] @type.builtin

((identifier) @type
  (#lua-match? @type "^[A-Z][a-zA-Z0-9_]*$"))

(type_identifier) @type

; Constants

((identifier) @constant
  (#lua-match? @constant "^[A-Z_][A-Z0-9_]*$"))

(enum_variant
  name: (identifier) @constant)

(call_expression
  function: (scoped_identifier
    "::"
    name: (identifier) @constant)
  (#lua-match? @constant "^[A-Z]"))

((match_arm
   pattern: (match_pattern (identifier) @constant))
 (#lua-match? @constant "^[A-Z]"))

((match_arm
   pattern: (match_pattern
     (scoped_identifier
       name: (identifier) @constant)))
 (#lua-match? @constant "^[A-Z]"))

((identifier) @constant.builtin
 (#any-of? @constant.builtin "Some" "None" "Ok" "Err"))

; Constructors

(unary_expression "new" (call_expression . (identifier) @constructor))

((call_expression . (identifier) @constructor)
  (#lua-match? @constructor "^%u"))

; Attributes

(decorator "@" @attribute (identifier) @attribute)

(attribute_item (identifier) @function.macro)

(attribute_item (scoped_identifier (identifier) @function.macro .))

; Labels

(label . (identifier) @label)

(inst_jmp_to_label "jmp" . (identifier) @label)

(inst_jnz_to_label "jmp" . (identifier) @label)

; Operators

[
  "+"
  "-"
  "*"
  "/"
  "**"
  "=="
  "!="
  "&"
  "="
  "++"
  "+="
  "@"
  "!"
  "~"
  ".."
  "&&"
  "||"
  "^"
  "<"
  "<="
  ">"
  ">="
  "<<"
  ">>"
  "%"
  "-="
  "*="
  "/="
  "%="
  "&="
  "|="
  "^="
  "<<="
  ">>="
  "?"
] @operator

; Literals

(number) @number

(boolean) @boolean

[
  (string)
  (short_string)
] @string

; Punctuation

(attribute_item "#" @punctuation.special)

[ "." "," ":" ";" "->" "=>" "::" ] @punctuation.delimiter

[ "{" "}" "(" ")" "[" "]" "%{" "%}" ] @punctuation.bracket

(type_parameters [ "<" ">" ] @punctuation.bracket)

(type_arguments [ "<" ">" ] @punctuation.bracket)

; Comment

(comment) @comment @spell

; Errors

(ERROR) @error
