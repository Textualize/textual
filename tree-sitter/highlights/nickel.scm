(comment) @comment @spell

[
  "forall"
  "in"
  "let"
  "default"
  "doc"
  "rec"
] @keyword

"fun" @keyword.function

"import" @include

[ "if" "then" "else" ] @conditional
"match" @conditional

(types) @type
"Array" @type.builtin

; BUILTIN Constants
(bool) @boolean
"null" @constant.builtin

(num_literal) @number

(infix_op) @operator

(type_atom) @type
(enum_tag) @variable

(chunk_literal_single) @string
(chunk_literal_multi) @string

(str_esc_char) @string.escape

[
 "{" "}"
 "(" ")"
 "[|" "|]"
] @punctuation.bracket

(multstr_start) @punctuation.bracket
(multstr_end) @punctuation.bracket
(interpolation_start) @punctuation.bracket
(interpolation_end) @punctuation.bracket

(record_field) @field

(builtin) @function.builtin

(fun_expr pats:
  (pattern id:
    (ident) @parameter
  )
)

(applicative t1:
  (applicative (record_operand) @function)
)
