(identifier) @variable
(reference_identifier) @variable
(member_identifier) @property

; Classes

(custom_type) @type
(class_field
  name: (identifier) @field)
(class_definition
  name: (identifier) @type)
(method_definition
  name: (identifier) @method)
(inflight_method_definition
  name: (identifier) @method)

; Functions

(keyword_argument_key) @parameter
(call
  caller: (reference
  	(nested_identifier
    	property: (member_identifier) @method.call)))
(call
  caller: (reference
  	(reference_identifier) @method.call))

; Primitives

(number) @number
(duration) @constant
(string) @string
(bool) @boolean
(builtin_type) @type.builtin
(json_container_type) @type.builtin

; Special

(comment) @comment

[
  "("
  ")"
  "{"
  "}"
]  @punctuation.bracket

[
  "-"
  "+"
  "*"
  "/"
  "%"
  "<"
  "<="
  "="
  "=="
  "!"
  "!="
  ">"
  ">="
  "&&"
  "??"
  "||"
] @operator

[
  ";"
  "."
  ","
] @punctuation.delimiter

[
  "as"
  "bring"
  "class"
  "else"
  "for"
  "if"
  "in"
  "init"
  "let"
  "new"
  "return"
  (inflight_specifier)
] @keyword
