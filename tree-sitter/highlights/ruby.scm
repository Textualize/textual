; Variables

(identifier) @variable
(global_variable) @variable.global

; Keywords

[
 "alias"
 "begin"
 "class"
 "do"
 "end"
 "ensure"
 "module"
 "rescue"
 "then"
 ] @keyword

[
 "return"
 "yield"
] @keyword.return

[
 "and"
 "or"
 "in"
 "not"
] @keyword.operator

[
  "def"
  "undef"
] @keyword.function

(method
  "end" @keyword.function)

[
 "case"
 "else"
 "elsif"
 "if"
 "unless"
 "when"
 "then"
 ] @conditional

(if
  "end" @conditional)

[
 "for"
 "until"
 "while"
 "break"
 "redo"
 "retry"
 "next"
 ] @repeat

(constant) @type

((identifier) @type.qualifier
 (#any-of? @type.qualifier "private" "protected" "public"))

[
 "rescue"
 "ensure"
 ] @exception

((identifier) @exception
 (#any-of? @exception "fail" "raise"))

; Function calls

"defined?" @function

(call
   receiver: (constant)? @type
   method: [
            (identifier)
            (constant)
            ] @function.call
   )

(program
 (call
  (identifier) @include)
 (#any-of? @include "require" "require_relative" "load"))

; Function definitions

(alias (identifier) @function)
(setter (identifier) @function)

(method name: [
               (identifier) @function
               (constant) @type
               ])

(singleton_method name: [
                         (identifier) @function
                         (constant) @type
                         ])

(class name: (constant) @type)
(module name: (constant) @type)
(superclass (constant) @type)

; Identifiers
[
 (class_variable)
 (instance_variable)
 ] @label

((identifier) @constant.builtin
 (#vim-match? @constant.builtin "^__(callee|dir|id|method|send|ENCODING|FILE|LINE)__$"))

((constant) @type
 (#vim-match? @type "^[A-Z\\d_]+$"))

[
 (self)
 (super)
 ] @variable.builtin

(method_parameters (identifier) @parameter)
(lambda_parameters (identifier) @parameter)
(block_parameters (identifier) @parameter)
(splat_parameter (identifier) @parameter)
(hash_splat_parameter (identifier) @parameter)
(optional_parameter (identifier) @parameter)
(destructured_parameter (identifier) @parameter)
(block_parameter (identifier) @parameter)
(keyword_parameter (identifier) @parameter)

; TODO: Re-enable this once it is supported
; ((identifier) @function
;  (#is-not? local))

; Literals

[
 (string)
 (bare_string)
 (subshell)
 (heredoc_body)
 ] @string

[
 (heredoc_beginning)
 (heredoc_end)
 ] @constant

[
 (bare_symbol)
 (simple_symbol)
 (delimited_symbol)
 (hash_key_symbol)
 ] @symbol

(pair key: (hash_key_symbol) ":" @constant)
(regex) @string.regex
(escape_sequence) @string.escape
(integer) @number
(float) @float

[
 (true)
 (false)
 ] @boolean

(nil) @constant.builtin

(comment) @comment @spell

(program
  (comment)+ @comment.documentation
  (class))

(module
  (comment)+ @comment.documentation
  (body_statement (class)))

(class
  (comment)+ @comment.documentation
  (body_statement (method)))

(body_statement
  (comment)+ @comment.documentation
  (method))

(string_content) @spell

; Operators

[
 "!"
 "="
 "=="
 "==="
 "<=>"
 "=>"
 "->"
 ">>"
 "<<"
 ">"
 "<"
 ">="
 "<="
 "**"
 "*"
 "/"
 "%"
 "+"
 "-"
 "&"
 "|"
 "^"
 "&&"
 "||"
 "||="
 "&&="
 "!="
 "%="
 "+="
 "-="
 "*="
 "/="
 "=~"
 "!~"
 "?"
 ":"
 ".."
 "..."
 ] @operator

[
 ","
 ";"
 "."
 ] @punctuation.delimiter

[
 "("
 ")"
 "["
 "]"
 "{"
 "}"
 "%w("
 "%i("
 ] @punctuation.bracket

(interpolation
  "#{" @punctuation.special
  "}" @punctuation.special) @none

(ERROR) @error
