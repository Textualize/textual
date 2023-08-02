; inherits: css

[
  "@at-root"
  "@debug"
  "@error"
  "@extend"
  "@forward"
  "@mixin"
  "@use"
  "@warn"
] @keyword

"@function" @keyword.function

"@return" @keyword.return

"@include" @include

[
  "@while"
  "@each"
  "@for"
  "from"
  "through"
  "in"
] @repeat

(single_line_comment) @comment
(function_name) @function


[
  ">="
  "<="
] @operator


(mixin_statement (name) @function)
(mixin_statement (parameters (parameter) @parameter))

(function_statement (name) @function)
(function_statement (parameters (parameter) @parameter))

(plain_value) @string
(keyword_query) @function
(identifier) @variable
(variable_name) @variable

(each_statement (key) @parameter)
(each_statement (value) @parameter)
(each_statement (variable_value) @parameter)

(for_statement (variable) @parameter)
(for_statement (_ (variable_value) @parameter))

(argument) @parameter
(arguments (variable_value) @parameter)

[
  "["
  "]"
] @punctuation.bracket

(include_statement (identifier) @function)
