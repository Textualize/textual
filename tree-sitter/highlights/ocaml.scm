; Modules
;--------

[(module_name) (module_type_name)] @namespace

; Types
;------

(
  (type_constructor) @type.builtin
  (#any-of? @type.builtin
    "int" "char" "bytes" "string" "float"
    "bool" "unit" "exn" "array" "list" "option"
    "int32" "int64" "nativeint" "format6" "lazy_t")
)

[(class_name) (class_type_name) (type_constructor)] @type

[(constructor_name) (tag)] @constructor

; Variables
;----------

[(value_name) (type_variable)] @variable

(value_pattern) @parameter

; Functions
;----------

(let_binding
  pattern: (value_name) @function
  (parameter))

(let_binding
  pattern: (value_name) @function
  body: [(fun_expression) (function_expression)])

(value_specification (value_name) @function)

(external (value_name) @function)

(method_name) @method

; Application
;------------

(infix_expression
  left: (value_path (value_name) @function)
  operator: (concat_operator) @_operator
  (#eq? @_operator "@@"))

(infix_expression
  operator: (rel_operator) @_operator
  right: (value_path (value_name) @function)
  (#eq? @_operator "|>"))

(application_expression
  function: (value_path (value_name) @function))

((value_name) @function.builtin
  (#any-of? @function.builtin "raise" "raise_notrace" "failwith" "invalid_arg"))

; Properties
;-----------

[(label_name) (field_name) (instance_variable_name)] @property

; Constants
;----------

; Don't let normal parens take priority over this
((unit) @constant.builtin (#set! "priority" 105))

(boolean) @boolean

[(number) (signed_number)] @number

(character) @character

(string) @string

(quoted_string "{" @string "}" @string) @string

(escape_sequence) @string.escape

[
  (conversion_specification)
  (pretty_printing_indication)
] @string.special

; Keywords
;---------

[
  "and" "as" "assert" "begin" "class"
  "constraint" "end" "external" "in"
  "inherit" "initializer" "let" "match"
  "method" "module" "new" "object" "of"
  "sig" "struct" "type" "val" "when" "with"
] @keyword

[
  "lazy" "mutable" "nonrec"
  "rec" "private" "virtual"
] @type.qualifier

["fun" "function" "functor"] @keyword.function

["if" "then" "else"] @conditional

["exception" "try"] @exception

["include" "open"] @include

["for" "to" "downto" "while" "do" "done"] @repeat

; Punctuation
;------------

(attribute ["[@" "]"] @punctuation.special)
(item_attribute ["[@@" "]"] @punctuation.special)
(floating_attribute ["[@@@" "]"] @punctuation.special)
(extension ["[%" "]"] @punctuation.special)
(item_extension ["[%%" "]"] @punctuation.special)
(quoted_extension ["{%" "}"] @punctuation.special)
(quoted_item_extension ["{%%" "}"] @punctuation.special)

"%" @punctuation.special

["(" ")" "[" "]" "{" "}" "[|" "|]" "[<" "[>"] @punctuation.bracket

(object_type ["<" ">"] @punctuation.bracket)

[
  "," "." ";" ":" "=" "|" "~" "?" "+" "-" "!" ">" "&"
  "->" ";;" ":>" "+=" ":=" ".."
] @punctuation.delimiter

; Operators
;----------

[
  (prefix_operator)
  (sign_operator)
  (pow_operator)
  (mult_operator)
  (add_operator)
  (concat_operator)
  (rel_operator)
  (and_operator)
  (or_operator)
  (assign_operator)
  (hash_operator)
  (indexing_operator)
  (let_operator)
  (and_operator)
  (match_operator)
] @operator

(match_expression (match_operator) @keyword)

(value_definition [(let_operator) (let_and_operator)] @keyword)

["*" "#" "::" "<-"] @operator

; Attributes
;-----------

(attribute_id) @property

; Comments
;---------

[(comment) (line_number_directive) (directive) (shebang)] @comment

(ERROR) @error
