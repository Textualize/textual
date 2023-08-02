[
    (block_comment)
    (comment)
    (note)
    (test)
] @comment

[
    (quantity)
    (negative_quantity)
] @number

[
    (date)
    (effective_date)
    (time)
    (interval)
] @string.special

[
    (commodity)
    (option)
    (option_value)
    (check_in)
    (check_out)
] @text.literal

((account) @field)

"include" @include

[
    "account"
    "alias"
    "assert"
    "check"
    "commodity"
    "comment"
    "def"
    "default"
    "end"
    "eval"
    "format"
    "nomarket"
    "note"
    "payee"
    "test"
    "A"
    "Y"
    "N"
    "D"
    "C"
    "P"
] @keyword
