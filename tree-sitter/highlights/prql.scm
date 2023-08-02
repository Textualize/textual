[
  (keyword_from)
  (keyword_filter)
  (keyword_derive)
  (keyword_group)
  (keyword_aggregate)
  (keyword_sort)
  (keyword_take)
  (keyword_window)
  (keyword_join)
  (keyword_select)
  (keyword_append)
  (keyword_remove)
  (keyword_intersect)
  (keyword_rolling)
  (keyword_rows)
  (keyword_expanding)
  (keyword_let)
  (keyword_prql)
  (keyword_from_text)
] @keyword

(keyword_loop) @repeat

(keyword_case) @conditional

[
 (literal_string)
 (f_string)
 (s_string)
] @string

(assignment
  alias: (field) @field)

alias: (identifier) @field

(comment) @comment @spell

(function_call
  (identifier) @function.call)

[
  "+"
  "-"
  "*"
  "/"
  "="
  "=="
  "<"
  "<="
  "!="
  ">="
  ">"
  "&&"
  "||"
  "//"
  "~="
  (bang)
] @operator

[
  "("
  ")"
  "{"
  "}"
] @punctuation.bracket

[
  ","
  "."
  (pipe)
  "->"
] @punctuation.delimiter

(integer) @number

(decimal_number) @float

[
  (keyword_min)
  (keyword_max)
  (keyword_count)
  (keyword_count_distinct)
  (keyword_average)
  (keyword_avg)
  (keyword_sum)
  (keyword_stddev)
  (keyword_count)
  (keyword_lag)
  (keyword_lead)
  (keyword_first)
  (keyword_last)
  (keyword_rank)
  (keyword_row_number)
  (keyword_round)
  (keyword_all)
  (keyword_map)
] @function

[
 (keyword_side)
 (keyword_format)
] @attribute

[
 (keyword_version)
 (keyword_target)
] @type.qualifier

(target) @function.builtin

 [
  (date)
  (time)
  (timestamp)
] @string.special

[
  (keyword_left)
  (keyword_inner)
  (keyword_right)
  (keyword_full)
  (keyword_csv)
  (keyword_json)
] @method.call

[
  (keyword_true)
  (keyword_false)
] @boolean

[
 (keyword_in)
] @keyword.operator

(function_definition
  (keyword_let)
  name: (identifier) @function)

(parameter
  (identifier) @parameter)

(variable
  (keyword_let)
  name: (identifier) @constant)


 (keyword_null) @constant.builtin
