; Misc keywords
[
  "my" "our" "local"
  "next" "last" "redo"
  "goto"
  "package"
;  "do"
;  "eval"
] @keyword

; Keywords for including
[ "use" "no" "require" ] @include

; Keywords that mark conditional statements
[ "if" "elsif" "unless" "else" ] @conditional
(ternary_expression
  ["?" ":"] @conditional.ternary)

; Keywords that mark repeating loops
[ "while" "until" "for" "foreach" ] @repeat

; Keyword for return expressions
[ "return" ] @keyword.return

; Keywords for phaser blocks
; TODO: Ideally these would be @keyword.phaser but vim-treesitter doesn't
;   have such a thing yet
[ "BEGIN" "CHECK" "UNITCHECK" "INIT" "END" ] @keyword.function

; Keywords to define a function
[ "sub" ] @keyword.function

; Lots of builtin functions, except tree-sitter-perl doesn't emit most of
;   these yet
;[
;  "print" "printf" "sprintf" "say"
;  "push" "pop" "shift" "unshift" "splice"
;  "exists" "delete" "keys" "values"
;  "each"
;] @function.builtin

; Keywords that are regular infix operators
[
  "and" "or" "not" "xor"
  "eq" "ne" "lt" "le" "ge" "gt" "cmp"
] @keyword.operator

; Variables
[
  (scalar_variable)
  (array_variable)
  (hash_variable)
] @variable

; Special builtin variables
[
  (special_scalar_variable)
  (special_array_variable)
  (special_hash_variable)
  (special_literal)
  (super)
] @variable.builtin

; Integer numbers
[
  (integer)
  (hexadecimal)
] @number

; Float numbers
[
  (floating_point)
  (scientific_notation)
] @float

; version sortof counts as a kind of multipart integer
(version) @constant

; Package names are types
(package_name) @type

; The special SUPER:: could be called a namespace. It isn't really but it
;   should highlight differently and we might as well do it this way
(super) @namespace

; Comments are comments
(comments) @comment
(comments) @spell

((source_file . (comments) @preproc)
  (#lua-match? @preproc "^#!/"))

; POD should be handled specially with its own embedded subtype but for now
;   we'll just have to do this.
(pod_statement) @text

(method_invocation
  function_name: (identifier) @method.call)
(call_expression
  function_name: (identifier) @function.call)

;; ----------

(use_constant_statement
  constant: (identifier) @constant)

(named_block_statement
  function_name: (identifier) @function)

(function_definition
  name: (identifier) @function)

[
(function)
(map)
(grep)
(bless)
] @function

[
"("
")"
"["
"]"
"{"
"}"
] @punctuation.bracket
(standard_input_to_variable) @punctuation.bracket

[
"=~"
"!~"
"="
"=="
"+"
"-"
"."
"//"
"||"
(arrow_operator)
(hash_arrow_operator)
(array_dereference)
(hash_dereference)
(to_reference)
(type_glob)
(hash_access_variable)
] @operator

[
(regex_option)
(regex_option_for_substitution)
(regex_option_for_transliteration)
] @parameter

(type_glob
  (identifier) @variable)

[
(word_list_qw)
(command_qx_quoted)
(string_single_quoted)
(string_double_quoted)
(string_qq_quoted)
(bareword)
(transliteration_tr_or_y)
] @string

[
(pattern_matcher)
(regex_pattern_qr)
(patter_matcher_m)
(substitution_pattern_s)
] @string.regex

(escape_sequence) @string.escape

[
","
(semi_colon)
(start_delimiter)
(end_delimiter)
(ellipsis_statement)
] @punctuation.delimiter

(function_attribute) @field

(function_signature) @type
