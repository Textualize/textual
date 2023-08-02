; CREDITS @pfoerster (adapted from https://github.com/latex-lsp/tree-sitter-bibtex)

[
  (string_type)
  (preamble_type)
  (entry_type)
] @keyword

[
  (junk)
  (comment)
] @comment

[
  "="
  "#"
] @operator

(command) @function.builtin

(number) @number

(field
  name: (identifier) @field)

(token
  (identifier) @parameter)

[
  (brace_word)
  (quote_word)
] @string

[
  (key_brace)
  (key_paren)
] @symbol

(string
  name: (identifier) @constant)

[
  "{"
  "}"
  "("
  ")"
] @punctuation.bracket

"," @punctuation.delimiter
