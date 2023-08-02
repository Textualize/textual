(dir_sep) @punctuation.delimiter

(quoted_pattern
  ("\"" @punctuation.special))

(range_notation) @string.special

(range_notation
  [ "[" "]" ] @punctuation.bracket)

(wildcard) @character.special

(range_negation) @operator

(character_class) @constant

(class_range ("-" @operator))

[
  (ansi_c_escape)
  (escaped_char)
] @string.escape

(attribute
  (attr_name) @parameter)

(attribute
  (builtin_attr) @variable.builtin)

[
  (attr_reset)
  (attr_unset)
  (attr_set)
] @operator

(boolean_value) @boolean

(string_value) @string

(macro_tag) @preproc

(macro_def
  macro_name: (_) @property)

[
  (pattern_negation)
  (redundant_escape)
  (trailing_slash)
] @error

(ERROR) @error

(comment) @comment @spell
