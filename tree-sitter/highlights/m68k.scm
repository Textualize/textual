(symbol) @variable

(label name: (symbol) @label)

[
  (instruction_mnemonic)
  (directive_mnemonic)
] @function.builtin

(include (directive_mnemonic) @include)
(include_bin (directive_mnemonic) @include)
(include_dir (directive_mnemonic) @include)


(size) @attribute

(macro_definition name: (symbol) @function.macro)
(macro_call name: (symbol) @function.macro)

[
  (path)
  (string_literal)
] @string

[
  (decimal_literal)
  (hexadecimal_literal)
  (octal_literal)
  (binary_literal)
] @number

[
  (reptn)
  (carg)
  (narg)
  (macro_arg)
] @variable.builtin

[
  (control_mnemonic)
  (address_register)
  (data_register)
  (float_register)
  (named_register)
] @keyword

(repeat (control_mnemonic) @repeat)
(conditional (control_mnemonic) @conditional)

(comment) @comment

[
  (operator)
  "="
  "#"
] @operator

[
  "."
  ","
  "/"
  "-"
] @punctuation.delimiter

[
  "("
  ")"
  ")+"
] @punctuation.bracket

(section) @namespace
